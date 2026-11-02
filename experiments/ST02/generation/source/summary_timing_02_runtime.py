"""ST02 immutable evidence controller; stdlib imports, Colab-only model loading."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import platform
import signal
import stat
import sys
import tempfile
import time
import traceback
import uuid
import zipfile
import cross_model_e1_01_offline_runtime as core
import cross_model_e1_01_generation_runtime as live
import summary_timing_02_scoring as sc

PROTOCOL='SUMMARY-TIMING-02-RUN-v0.1'
CODE_NAMES=('cross_model_e1_01_offline_runtime.py','cross_model_e1_01_generation_runtime.py',
            'readout_split_01_scoring.py','update_readout_01_envelope.py',
            'experience_update_01_design.py','summary_timing_02_scoring.py','summary_timing_02_fixtures.py',
            'summary_timing_02_runtime.py','summary_timing_02_bootstrap.py')

def initialize(root,packed):
    validate_payload(packed);root=Path(root);root.mkdir(parents=True,exist_ok=True)
    live.write_new(root/'design.json',packed['design_text'].encode())
    live.write_new(root/'requests.json',packed['requests_text'].encode())
    live.write_json(root/'contract.json',packed['contract'])
    for directory,key in [('code','code'),('frozen','frozen')]:
        for name,src in packed[key].items():live.write_new(root/directory/name,src.encode())

def verify_root(root,packed):
    design,requests=validate_payload(packed);root=Path(root)
    for name,key in [('design.json','design_text'),('requests.json','requests_text')]:
        core.require((root/name).read_bytes()==packed[key].encode(),'SAVED_'+name)
    core.require(live.read_json(root/'contract.json')==packed['contract'],'SAVED_CONTRACT')
    if (root/'payload.json').exists():core.require(live.read_json(root/'payload.json')==packed,'SAVED_PAYLOAD')
    for directory,key in [('code','code'),('frozen','frozen')]:
        for name,src in packed[key].items():core.require((root/directory/name).read_bytes()==src.encode(),'SAVED_'+key.upper())
    for module in (core,live,sc.strict_json,sc.envelope,sc.base,sc,sys.modules[__name__]):
        path=Path(module.__file__)
        core.require(sha256(path.read_bytes()).hexdigest()==packed['contract']['source_hashes'][path.name],'ACTIVE_CODE_CHANGED')
    allowed={s['id'] for s in design['allocation']}
    if (root/'responses').exists():
        core.require(all(p.is_dir() and not p.is_symlink() and p.name in allowed for p in (root/'responses').iterdir()),'UNEXPECTED_RESPONSE_ID')
        core.require(all(not p.is_symlink() and (p.is_file() or p.name in allowed) for p in (root/'responses').rglob('*')),'RESPONSE_FILE_TYPE')
    return design,requests

def match_bytes(path,raw,create):
    if create and not path.exists():live.write_new(path,raw)
    core.require(path.read_bytes()==raw,'ARTIFACT_BYTES_MISMATCH:'+path.name)

def unknown(context,stage,design,memory=None):
    return sc.score(None,context['slot'],context['payload'],context['case_rows'])

def evaluate(response,context,stage,design,memory=None):
    return sc.score(response['answer_text'].encode(),context['slot'],context['payload'],context['case_rows'],response['finish_reason'])

def artifacts(folder,response,score,context,stage,design,create):
    raw=response['answer_text'].encode()
    match_bytes(folder/'answer.txt',raw,create)
    match_bytes(folder/'decoded-with-special-tokens.txt',response['decoded_with_special_tokens'].encode(),create)
    receipt=sc.receive(raw,stage,response['finish_reason']);normalized=receipt.pop('normalized_bytes')
    match_artifact(folder/'normalization.json',receipt['normalization'],create)
    if normalized is not None:match_bytes(folder/'normalized-answer.txt',normalized,create)
    else:core.require(not (folder/'normalized-answer.txt').exists(),'REJECTED_NORMALIZED_TEXT')
    for name in ('saved-answer.json','carry-answer.json'):
        if score['answer'] is not None:match_artifact(folder/name,score['answer'],create)
        else:core.require(not (folder/name).exists(),'REJECTED_SAVED_ANSWER')
    match_artifact(folder/'carry-trace.json',context['trace'],create)
    match_artifact(folder/'calculation-receipt.json',context['trace']['calculation_receipt'],create)


def status_for(response,score,stage):
    if response['finish_reason']!='EOS':return response['finish_reason']
    return 'EOS' if score['format_valid'] is True else 'FORMAT_REJECT'


def parent_state(root,slot,rows):
    states={};binding={}
    for pid in slot['parents']:
        core.require(pid.startswith('ST02-'+slot['condition_not_for_model']+'-'),'CROSS_CONDITION_PARENT')
        if pid not in rows:return None,None
        folder=root/'responses'/pid;path=folder/'carry-answer.json'
        states[pid]=live.read_json(path) if path.exists() else None
        binding[pid]={'result_sha256':sha256((folder/'result.json').read_bytes()).hexdigest(),
                     'carry_answer_sha256':sha256(path.read_bytes()).hexdigest() if path.exists() else None,
                     'raw_answer_sha256':sha256((folder/'saved-answer.json').read_bytes()).hexdigest() if (folder/'saved-answer.json').exists() else None,
                     'candidate_binding_sha256':sha256((folder/'candidate-binding.json').read_bytes()).hexdigest() if (folder/'candidate-binding.json').exists() else None}
    return states,binding

def blocked(store,slot,score,binding,missing):
    folder=store.directory(slot);status='DEPENDENCY_MISSING'
    match_artifact(folder/'blocked.json',{'status':status,'parents':binding,'missing_parents':missing},True)
    core.require(not any((folder/n).exists() for n in ('input.json','started.json','response.json','answer.txt','saved-answer.json','carry-answer.json','candidate-binding.json','normalization.json','normalized-answer.txt','carry-trace.json','calculation-receipt.json')),'BLOCKED_HAS_RESPONSE')
    if store.completed(slot):
        result=store.load(slot)
        core.require(result['score']==score and result['status']==status,'BLOCKED_REPLAY_MISMATCH')
        return result
    return store.finish(slot,status,score,'DEPENDENCY_ONLY')

def physical(store, request, binding, context, stage, design, memory, backend, deadline, close_pending):
    """Execute/replay one immutable physical request. No retry or fixture fallback."""
    slot = {'id':request['id'],'seed':request['seed']}; folder = store.directory(slot)
    unk = unknown(context,stage,design,memory)
    if (folder/'input.json').exists():
        saved = live.read_json(folder/'input.json')
        core.require(all(saved[k]==request[k] for k in request), 'INPUT_CHANGED')
        core.require(saved.get('binding')==binding, 'INPUT_BINDING_CHANGED')
    if (folder/'started.json').exists():
        mark = live.read_json(folder/'started.json')
        core.require(mark['input_sha256']==sha256((folder/'input.json').read_bytes()).hexdigest(), 'START_INPUT_HASH')
        core.require(mark['seed']==request['seed'], 'START_SEED')
    def finish():
        response = read_response(folder,slot)
        score = evaluate(response,context,stage,design,memory)
        artifacts(folder,response,score,context,stage,design,True)
        return store.finish(slot,status_for(response,score,stage),score,'COMPONENT_SCORING')
    if store.completed(slot):
        result = store.load(slot)
        if (folder/'response.json').exists():
            core.require((folder/'started.json').exists(), 'RESPONSE_WITHOUT_START')
            response = read_response(folder,slot); score = evaluate(response,context,stage,design,memory)
            core.require(score==result['score'], 'SCORE_REPLAY_MISMATCH')
            core.require(result['status']==status_for(response,score,stage), 'STATUS_MISMATCH')
            artifacts(folder,response,score,context,stage,design,False)
        else:
            core.require(result['score']==unk and result['status'] in ('NOT_RUN','INTERRUPTED_UNCERTAIN','GENERATION_ERROR','INPUT_TOO_LONG','PREPARATION_ERROR'), 'UNANSWERED_SCORE')
            core.require(not any((folder/n).exists() for n in ('answer.txt','normalization.json','normalized-answer.txt','saved-answer.json','carry-answer.json','candidate-binding.json','carry-trace.json','calculation-receipt.json')), 'UNANSWERED_ARTIFACT')
        return result
    if (folder/'started.json').exists():
        return finish() if (folder/'response.json').exists() else store.finish(slot,'INTERRUPTED_UNCERTAIN',unk)
    core.require(not (folder/'response.json').exists(), 'ORPHAN_RESPONSE')
    if (folder/'input.json').exists():
        return store.finish(slot,'NOT_RUN',unk,'PREPARATION_INTERRUPTED')
    if backend is None or live.STOP_REQUESTED or time.monotonic() >= deadline:
        return store.finish(slot,'NOT_RUN',unk) if close_pending else None
    core.require(not folder.exists() or not any(folder.iterdir()), 'PARTIAL_PREPARATION')
    try:
        prepared = backend.prepare(request['messages'])
    except BaseException as error:
        live.write_json(folder/'preparation-error.json',{'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()})
        store.finish(slot,'PREPARATION_ERROR',unk); raise
    live.write_json(folder/'input.json',dict(request,binding=binding,prepared=prepared))
    if len(prepared['input_ids']) > live.MAX_INPUT_TOKENS:
        return store.finish(slot,'INPUT_TOO_LONG',unk)
    if live.STOP_REQUESTED or time.monotonic() >= deadline:
        return store.finish(slot,'NOT_RUN',unk)
    core.require(len(list((store.root/'responses').glob('*/started.json'))) < 248,'GENERATION_BUDGET')
    live.write_json(folder/'started.json',{'started_at':live.now(),'seed':request['seed'],
        'input_sha256':sha256((folder/'input.json').read_bytes()).hexdigest()})
    try:
        response = backend.generate(prepared,request['seed'],deadline)
        response['payload_sha256'] = live.digest(response)
        live.write_json(folder/'response.json',response)
    except BaseException as error:
        live.write_json(folder/'generation-error.json',{'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()})
        store.finish(slot,'GENERATION_ERROR',unk); raise
    return finish()

def read_response(folder, slot):
    response = live.read_json(folder / 'response.json')
    core.require(response['payload_sha256'] == live.digest({k: v for k, v in response.items() if k != 'payload_sha256'}), 'RESPONSE_HASH')
    core.require(response['seed'] == slot['seed'], 'RESPONSE_SEED')
    core.require(response['finish_reason'] in ('EOS', 'LENGTH', 'TIME_LIMIT'), 'FINISH_REASON')
    ids = response['output_token_ids']
    core.require(type(ids) is list and all(type(x) is int for x in ids) and len(ids) <= 1024, 'OUTPUT_TOKENS')
    eos = bool(ids and ids[-1] == live.SPECIAL_TOKEN_IDS['<|im_end|>'])
    core.require((response['finish_reason'] == 'EOS') == eos, 'EOS_INCONSISTENT')
    return response

def match_artifact(path, value, create):
    if create and not path.exists():
        live.write_json(path, value)
    core.require(live.read_json(path) == value, 'ARTIFACT_REPLAY_MISMATCH:' + path.name)

def export_zip(root, destination, kind='FINAL'):
    root, destination = Path(root), Path(destination)
    core.require(not destination.resolve().is_relative_to(root.resolve()), 'ZIP_INSIDE_EVIDENCE')
    files = {}
    for p in sorted(root.rglob('*')):
        core.require(not p.is_symlink(), 'EVIDENCE_SYMLINK')
        if p.is_file() and '__pycache__' not in p.parts and '.tmp-' not in p.name and p.name != 'RUNNING.lock':
            files[str(p.relative_to(root))] = p.read_bytes()
    manifest = {'protocol': PROTOCOL, 'kind': kind, 'resume_generation': False,
                'files_sha256': {n: sha256(b).hexdigest() for n, b in files.items()}}
    temporary = destination.with_name(destination.name + '.tmp-' + uuid.uuid4().hex)
    with zipfile.ZipFile(temporary, 'x', zipfile.ZIP_DEFLATED) as z:
        for n, raw in files.items(): z.writestr(n, raw)
        z.writestr('FEEDBACK_MANIFEST.json', core.encoded(manifest))
    core.require(not destination.exists(), 'ZIP_EXISTS')
    temporary.rename(destination)
    return destination

def read_archive(path):
    with zipfile.ZipFile(path) as z:
        members = z.infolist(); names = [m.filename for m in members]
        core.require(len(names) == len(set(names)) and len(names) <= 7500 and sum(m.file_size for m in members) <= 250_000_000, 'ARCHIVE_LIMIT')
        for m in members:
            p = PurePosixPath(m.filename)
            core.require(not p.is_absolute() and '..' not in p.parts and p.as_posix() == m.filename and '\\' not in m.filename and ':' not in m.filename and not m.is_dir() and not stat.S_ISLNK(m.external_attr >> 16), 'ARCHIVE_PATH')
        files = {n: z.read(n) for n in names}
    manifest = json.loads(files.pop('FEEDBACK_MANIFEST.json'))
    core.require(manifest['protocol'] == PROTOCOL and set(files) == set(manifest['files_sha256']), 'ARCHIVE_MANIFEST')
    core.require(all(sha256(raw).hexdigest() == manifest['files_sha256'][n] for n, raw in files.items()), 'ARCHIVE_HASH')
    return manifest, files

def contract_for(packed):
    return {'protocol':PROTOCOL,'proposal_sha256':sc.PROPOSAL_SHA,
        'design_sha256':sha256(packed['design_text'].encode()).hexdigest(),
        'requests_sha256':sha256(packed['requests_text'].encode()).hexdigest(),
        'source_hashes':{n:sha256(s.encode()).hexdigest() for n,s in packed['code'].items()},
        'frozen_hashes':{n:sha256(t.encode()).hexdigest() for n,t in packed['frozen'].items()},
        'max_generations':248,'nominal_generations':232,'max_form':32,'max_confirm':48,'max_recheck':48,'max_use':96,'diagnostic_recheck':24,
        'seconds_including_setup':2700,'reserved_final_seconds':90,'automatic_regenerations':0,'resume_generation':False,
        'checkpoint_every_closed_paths':4,'cloud_drive':'not_used','retention':'private_no_deletion_deadline',
        'delivery':'zip_download','normalization':'Strict bare JSON or exact inherited json fence; no key deletion or value repair.',
        'sharing':'Per condition: 16 new FORM responses shared across 24 paths; 12 diagnoses separate. Actual carry never crosses conditions; model-visible CR01 IDs retained.',
        'eos_policy':'Remove one final im_end only, preserving output tokens.'}



def initial_requests(design):
    # Frozen messages are authoritative: do not reserialize the original user payload.
    raise RuntimeError('Use the sealed initial-requests.json directly')



def validate_payload(packed):
    core.require(set(packed['code'])==set(CODE_NAMES),'CODE_FILE_SET')
    core.require(packed['contract']==contract_for(packed),'CONTRACT_CHANGED')
    frozen=packed['frozen'];manifest=json.loads(frozen['MANIFEST.json'])
    core.require(set(frozen)==set(manifest)|{'MANIFEST.json'},'FROZEN_FILE_SET')
    for name,h in manifest.items():
        p=PurePosixPath(name)
        core.require(not p.is_absolute() and '..' not in p.parts and p.as_posix()==name and chr(92) not in name and ':' not in name,'FROZEN_PATH')
        core.require(sha256(frozen[name].encode()).hexdigest()==h,'FROZEN_HASH')
    core.require(sha256(frozen['materials-proposal.json'].encode()).hexdigest()==sc.PROPOSAL_SHA,'PROPOSAL_CHANGED')
    core.require(packed['design_text']==frozen['materials-proposal.json'] and packed['requests_text']==frozen['initial-requests.json'],'DESIGN_REQUEST_BYTES')
    design=json.loads(packed['design_text']);requests=json.loads(packed['requests_text'])
    core.require(design['protocol']==sc.PROTOCOL,'PROTOCOL')
    for stage in ('FORM','CONFIRM','RECHECK','USE'):
        core.require(design['schemas'][stage]==sc.SCHEMAS[stage] and json.loads(frozen['schemas/'+stage+'.json'])==design['schemas'][stage],'SCHEMA_CHANGED')
        core.require(design['prompts'][stage]==frozen['prompts/'+stage+'.txt'],'PROMPT_CHANGED')
    expected={'id':live.MODEL_ID,'revision':live.MODEL_REVISION,'pins':live.PINS,
        'generation':dict(live.GENERATION,max_new_tokens=1024),'max_input_tokens':live.MAX_INPUT_TOKENS,
        'dtype':'bfloat16','attention':'sdpa','enable_thinking':False}
    core.require(design['model']==expected and design['max_generations']==248 and design['seconds_including_setup']==2700,'MODEL_BUDGET_CHANGED')
    slots={s['id']:s for s in design['allocation']}
    core.require(len(slots)==248 and len(requests)==32 and len(design['paths'])==48 and len(design['diagnostics'])==24 and len(design['cases'])==8,'SCOPE')
    for slot in slots.values():
        for pid in slot['parents']:
            core.require(pid in slots and slots[pid]['condition_not_for_model']==slot['condition_not_for_model'],'CROSS_CONDITION_PARENT')
    core.require({q['id'] for q in requests}=={s['id'] for s in slots.values() if s['stage']=='FORM'},'INITIAL_REQUEST_SET')
    for q in requests:
        slot=slots[q['id']];p=sc.payload_for(design,slot,{})
        core.require(q['seed']==slot['seed'] and len(q['messages'])==2 and q['messages'][0]=={'role':'system','content':design['prompts']['FORM']},'INITIAL_REQUEST_CHANGED')
        core.require(q['messages'][1]['role']=='user' and q['messages'][1]['content'].startswith('資料JSON:\n'),'INITIAL_USER')
        core.require(json.loads(q['messages'][1]['content'].split('\n',1)[1])==p,'INITIAL_PAYLOAD_CHANGED')
    return design,requests



def carry_trace(design,slot,states,payload,binding,source):
    case=sc.case_for(design,slot);stage=slot['stage'];carried=[];receipt={'joint_totals':None,'own_summary':None}
    expected_rows=[r for r in case['experiences'] if r['observer']==slot['role']] if stage=='FORM' else case['experiences']
    core.require(payload['experiences']==expected_rows,'EXPERIENCE_CARRY_CHANGED')
    core.require(payload==sc.payload_for(design,slot,states),'PAYLOAD_FIELD_CARRY_CHANGED')
    def actual(sid,field,target):
        rec=sc.record(sc.slot_for(design,sid),states[sid],field)
        carried.append({'parent_id':sid,'parent_artifact':'carry-answer.json','extraction':'/'+field,'target':target,'record':rec})
        return rec
    if stage!='FORM':
        if stage in ('CONFIRM','RECHECK','RECHECK_DIAGNOSTIC'):
            actual(sc.form_id(case['id'],slot['role'],slot['condition_not_for_model']),'local','/own_judgment')
            carried.append({'origin':'researcher_constructed_initial_proposal','target':'/initial_proposal','record':source['initial_proposal']})
            if stage=='RECHECK':actual(source['confirm_id'],'reply','/counter_record')
            elif stage=='RECHECK_DIAGNOSTIC':carried.append({'origin':'researcher_constructed_counter','target':'/counter_record','record':source['counter_record']})
            receipt['joint_totals']=sc.joint_receipt(case,payload)

        else:
            required=states[source['confirm_id']]['reply']['action']=='COUNTER'
            carried.append({'origin':'researcher_constructed_initial_proposal','target':'/joint_records/0','record':source['initial_proposal']})
            actual(source['confirm_id'],'reply','/joint_records/1')
            if required:actual(source['recheck_id'],'reply','/joint_records/2')
            sid=source['confirm_id'] if slot['role']==case['peer'] else source['recheck_id'] if required else sc.form_id(case['id'],slot['role'],slot['condition_not_for_model'])
            actual(sid,'local','/own_judgment')
            core.require(set(payload)=={'holder','experiences','own_judgment','joint_records','own_experience_summary'},'USE_SUPPORT_LEAK')
    summary,calc=sc.own_summary(payload,case['medium_order'])
    supplied=sc.supplies_summary(design,slot)
    core.require(('own_experience_summary' in payload)==supplied,'SUMMARY_SUPPLY_TIMING')
    if supplied:
        core.require(payload['own_experience_summary']==summary,'OWN_SUMMARY_CHANGED')
        core.require(list(payload)[-1]=='own_experience_summary','SUMMARY_NOT_LAST')
    receipt['own_summary']=dict(calc,supplied_to_model=supplied)
    return {'kind':'ACTUAL_PARENT_FIELD_CARRY','condition':slot['condition_not_for_model'],'parents':binding,'payload_sha256':sc.digest(payload),
        'case_sha256':sc.digest(case),'source_sha256':sc.digest(source),'calculation_receipt':receipt,
        'carried_fields':carried,'semantic_repair':False,'diagnostic':stage=='RECHECK_DIAGNOSTIC'}



def skipped(store,slot,score,binding):
    folder=store.directory(slot)
    match_artifact(folder/'skipped.json',{'status':'SKIPPED_BY_PROTOCOL','parents':binding,'reason':'CONFIRM_ACTION_NOT_COUNTER'},True)
    core.require(not any((folder/n).exists() for n in ('started.json','input.json','response.json','carry-answer.json')),'SKIPPED_HAS_GENERATION')
    if store.completed(slot):
        result=store.load(slot)
        core.require(result['status']=='SKIPPED_BY_PROTOCOL' and result['score']==score,'SKIP_REPLAY_MISMATCH')
        return result
    return store.finish(slot,'SKIPPED_BY_PROTOCOL',score,'NONAPPLICABLE')


def run_routes(root,packed,backend=None,deadline=float('inf'),close_pending=False,checkpoint=None):
    design,initial=verify_root(root,packed);root=Path(root);initial={q['id']:q for q in initial}
    store=live.EvidenceStore(root,packed['contract']);rows={};closed=0
    route=lambda s:s.get('route') or s.get('diagnostic')
    ends={route(s):i for i,s in enumerate(design['allocation']) if route(s)}
    for idx,slot in enumerate(design['allocation']):
        stage=slot['stage'];source=sc.source_for(design,slot);case=sc.case_for(design,slot)
        context={'slot':slot,'case_rows':case['experiences'],'payload':None}
        states,bindings=parent_state(root,slot,rows)
        if states is None:continue
        conf=states.get(source.get('confirm_id')) if stage in ('RECHECK','USE') else None
        bypass=conf is not None and conf['reply']['action']!='COUNTER'
        if stage=='RECHECK' and bypass:
            rows[slot['id']]=skipped(store,slot,sc.skipped_score(slot,case['experiences']),bindings)
        else:
            required=[pid for pid in slot['parents'] if not(stage=='USE' and bypass and pid==slot['conditional_parent'])]
            missing=[pid for pid in required if states[pid] is None]
            if missing:rows[slot['id']]=blocked(store,slot,unknown(context,stage,design),bindings,missing)
            else:
                request=initial[slot['id']] if stage=='FORM' else sc.request_for(design,slot,states)
                payload=json.loads(request['messages'][1]['content'].split('\n',1)[1]);context['payload']=payload
                core.require(payload==sc.payload_for(design,slot,states),'ACTUAL_PAYLOAD_CHANGED')
                binding={'condition':slot['condition_not_for_model'],'stage':stage,'role':slot['role'],'parents':bindings,'required_parent_ids':required,
                         'source':{'sha256':sc.digest(source)},'recheck_bypassed':bypass}
                context['trace']=carry_trace(design,slot,states,payload,bindings,source)
                result=physical(store,request,binding,context,stage,design,None,backend,deadline,close_pending)
                if result is not None:rows[slot['id']]=result
        rid=route(slot)
        if rid and idx==ends[rid] and all(s['id'] in rows for s in design['allocation'] if route(s)==rid):
            closed+=1
            if backend is not None:
                attempted=len(list((root/'responses').glob('*/started.json')))
                print(f'{closed}/72 paths/diagnoses; {len(rows)}/248 slots closed; generations {attempted}/248',flush=True)
                if checkpoint and closed%4==0:checkpoint(closed)
    return {'responses':rows,'closed_paths':closed}



def make_report(root,packed,rows):
    design,_=verify_root(root,packed);root=Path(root);results=rows['responses']
    core.require(set(results)=={s['id'] for s in design['allocation']} and rows['closed_paths']==72,'REPORT_INCOMPLETE')
    report=sc.summarize(design,{sid:r['score'] for sid,r in results.items()})
    report.update(protocol=PROTOCOL,closed_logical_responses=248,closed_paths=72,
        status_counts=dict(Counter(r['status'] for r in results.values())),
        attempted_generations=len(list((root/'responses').glob('*/started.json'))))
    core.require(report['attempted_generations']<=248,'GENERATION_BUDGET')
    report['by_slot']=[dict(s,status=results[s['id']]['status'],score=results[s['id']]['score']) for s in design['allocation']]
    report['performance']={};report['normalization']={};synthetic=False
    for stage in sc.STAGES:
        ids=[s['id'] for s in design['allocation'] if s['stage']==stage]
        answered=[sid for sid in ids if (root/'responses'/sid/'response.json').exists()]
        values=[live.read_json(root/'responses'/sid/'response.json') for sid in answered]
        synthetic=synthetic or any(v.get('synthetic_fixture') for v in values)
        norms=[live.read_json(root/'responses'/sid/'normalization.json') for sid in answered]
        accepted=[results[sid]['score']['format_valid'] is True for sid in answered]
        report['normalization'][stage]={'answered':len(answered),'status':dict(Counter(n['status'] for n in norms)),
            'raw_schema_accepted':sum(ok and n['status']=='UNCHANGED' for ok,n in zip(accepted,norms)),
            'normalized_schema_accepted':sum(accepted),'removed_bytes':sum(n.get('removed_prefix_bytes',0)+n.get('removed_suffix_bytes',0) for n in norms)}
        inputs=[live.read_json(root/'responses'/sid/'input.json') for sid in answered]
        report['performance'][stage]={'planned_responses':len(ids),'responses':len(values),
            'input_tokens':[len(v['prepared']['input_ids']) for v in inputs],
            'prompt_bytes':[len(sc.displayed(v['messages']).encode()) for v in inputs],
            'output_tokens':[len(v['output_token_ids']) for v in values],
            'raw_bytes':[len(v['answer_text'].encode()) for v in values],
            'generation_seconds':[v['generation_seconds'] for v in values]}
    report['prompt_lengths']={'by_stage':{stage:len(p.encode()) for stage,p in design['prompts'].items()},'unit':'utf8_bytes'}
    report['evidence_kind']='SYNTHETIC_TEST_NOT_MODEL_RESULTS' if synthetic else 'MODEL_RUN_EVIDENCE'
    return report


def preflight(packed):
    import summary_timing_02_fixtures as fixtures
    design,_=validate_payload(packed);states={};outcomes={};calls=0
    for slot in design['allocation']:
        case=sc.case_for(design,slot);source=sc.source_for(design,slot)
        if slot['stage']=='RECHECK' and states[source['confirm_id']]['reply']['action']!='COUNTER':
            states[slot['id']]=None;outcomes[slot['id']]=sc.skipped_score(slot,case['experiences']);continue
        payload=sc.payload_for(design,slot,states);answer=fixtures.correct_answer(payload,slot['stage'])
        outcome=sc.score(sc.enc(answer),slot,payload,case['experiences']);calls+=1
        states[slot['id']]=outcome['carried_answer'];outcomes[slot['id']]=outcome
    report=sc.summarize(design,outcomes)
    core.require(report['progression']['status']=='MET_IN_FIXED_SAMPLE' and all(report['by_condition'][arm]['metrics']['J']['correct']==24 for arm in ('LATE','EARLY')) and calls==232,'SYNTHETIC_PATH')
    return {'kind':'SYNTHETIC_PREFLIGHT_NOT_MODEL_RESULTS','materials':8,'paths':48,'diagnoses':24,
            'stage_counts':dict(Counter(s['stage'] for s in design['allocation'])),
            'synthetic_calls':calls,'skipped_rechecks':16,'model_generations':0,'status':'PASS'}



def aggregate_archive(path,packed):
    manifest,files=read_archive(path)
    with tempfile.TemporaryDirectory(prefix='st02-audit-') as temp:
        root=Path(temp)
        for name,raw in files.items():
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        verify_root(root,packed)
        rows=run_routes(root,packed,close_pending=True);report=make_report(root,packed,rows)
        for p in root.glob('report-*.json'):core.require(live.read_json(p)==report,'ARCHIVED_REPORT_MISMATCH')
        return {'archive_sha256':sha256(Path(path).read_bytes()).hexdigest(),'manifest_files':len(files),'kind':manifest['kind'],'report':report}


def worker(root,seconds,audit_only=False):
    root=Path(root);packed=live.read_json(root/'payload.json')
    def stop(signum,frame):live.STOP_REQUESTED=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    deadline=time.monotonic()+seconds
    try:
        if not audit_only:
            core.require(platform.system()=='Linux' and Path('/content').is_dir(),'COLAB_ONLY_NO_MODEL_LOAD')
            verify_root(root,packed)
            core.require(live.read_json(root/'preflight.json')==preflight(packed),'PREFLIGHT_CHANGED')
            core.require(not list((root/'responses').glob('*/*')),'NO_GENERATION_RESTART')
            live.GENERATION=dict(live.GENERATION,max_new_tokens=1024)
            core.require(live.GENERATION==json.loads(packed['design_text'])['model']['generation'],'EFFECTIVE_GENERATION_CHANGED')
            backend=live.HuggingFaceBackend(root,deadline)
            def checkpoint(n):export_zip(root,root.parent/f'npp-st02-checkpoint-{root.name}-{n:02d}.zip','CHECKPOINT')
            run_routes(root,packed,backend,deadline,checkpoint=checkpoint)
    finally:
        rows=run_routes(root,packed,close_pending=True);report=make_report(root,packed,rows)
        live.write_json(root/('report-'+uuid.uuid4().hex+'.json'),report)
        print(json.dumps({'closed_paths':72,'planned_responses':248,'model_calls':report['attempted_generations'],
            'progression':report['progression']['status'],'status':report['status_counts']},ensure_ascii=False),flush=True)


if __name__=='__main__':worker(sys.argv[1],float(sys.argv[2]),len(sys.argv)>3 and sys.argv[3]=='AUDIT_ONLY')
