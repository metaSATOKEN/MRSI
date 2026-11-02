"""JR01 immutable exact-input replay; all real model loading is Colab-only."""
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
import judgment_repeat_01_scoring as sc

PROTOCOL = 'JUDGMENT-REPEAT-01-RUN-v0.1'
CODE_NAMES = ('cross_model_e1_01_offline_runtime.py', 'cross_model_e1_01_generation_runtime.py',
 'readout_split_01_scoring.py', 'update_readout_01_envelope.py', 'experience_update_01_design.py',
 'summary_timing_02_scoring.py', 'summary_timing_02_fixtures.py',
 'judgment_repeat_01_scoring.py', 'judgment_repeat_01_fixtures.py',
 'judgment_repeat_01_runtime.py', 'judgment_repeat_01_bootstrap.py')


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
    for module in (core,live,sc.prior.strict_json,sc.prior.envelope,sc.prior.base,sc.prior,sc,sys.modules[__name__]):
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

def physical(store, request, binding, context, stage, design, memory, backend, deadline, close_pending):
    """Execute/replay one immutable physical request. No retry or fixture fallback."""
    slot = {'id':request['id'],'seed':request['seed']}; folder = store.directory(slot)
    unk = unknown(context,stage,design,memory)
    if (folder/'input.json').exists():
        saved = live.read_json(folder/'input.json')
        core.require(all(saved[k]==request[k] for k in request), 'INPUT_CHANGED')
        core.require(saved.get('binding')==binding, 'INPUT_BINDING_CHANGED')
        verify_prepared(saved['prepared'], context['template'])
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
        verify_prepared(prepared, context['template'])
    except BaseException as error:
        if 'prepared' in locals():live.write_json(folder/'preparation-observed.json', prepared)
        live.write_json(folder/'preparation-error.json',{'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()})
        store.finish(slot,'PREPARATION_ERROR',unk); raise
    live.write_json(folder/'input.json',dict(request,binding=binding,prepared=prepared))
    if len(prepared['input_ids']) > live.MAX_INPUT_TOKENS:
        return store.finish(slot,'INPUT_TOO_LONG',unk)
    if live.STOP_REQUESTED or time.monotonic() >= deadline:
        return store.finish(slot,'NOT_RUN',unk)
    core.require(len(list((store.root/'responses').glob('*/started.json'))) < 240,'GENERATION_BUDGET')
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


def verify_prepared(prepared, template):
    ids = prepared['input_ids']
    core.require(type(ids) is list and all(type(x) is int for x in ids), 'INPUT_TOKEN_TYPES')
    core.require(len(ids)==template['source_input_tokens'] and sc.digest(ids)==template['source_token_ids_sha256'], 'SOURCE_TOKEN_IDS_CHANGED')
    core.require(sha256(prepared['rendered_prompt'].encode()).hexdigest()==template['source_rendered_prompt_sha256'], 'SOURCE_RENDERED_PROMPT_CHANGED')


def contract_for(packed):
    return {'protocol':PROTOCOL,'proposal_sha256':sc.PROPOSAL_SHA,'requests_sha256':sc.REQUESTS_SHA,
            'source_hashes':{n:sha256(s.encode()).hexdigest() for n,s in packed['code'].items()},
            'frozen_hashes':{n:sha256(s.encode()).hexdigest() for n,s in packed['frozen'].items()},
            'max_generations':240,'nominal_generations':240,'FORM':96,'CONFIRM':144,
            'seconds_including_setup':2700,'reserved_final_seconds':90,'automatic_regenerations':0,
            'resume_generation':False,'checkpoint_every_responses':40,'cloud_drive':'not_used',
            'retention':'private_no_deletion_deadline','delivery':'zip_download',
            'carry':'Only old ST02 FORM records frozen inside CONFIRM. New FORM responses are never carried.',
            'input_guard':'Exact source message bytes, token IDs, rendered prompt; fail before generation on mismatch.',
            'normalization':'Inherited exact JSON envelope only; no key removal or semantic repair.'}


def validate_payload(packed):
    core.require(set(packed['code'])==set(CODE_NAMES),'CODE_FILE_SET')
    core.require(packed['contract']==contract_for(packed),'CONTRACT_CHANGED')
    frozen=packed['frozen'];manifest=json.loads(frozen['MANIFEST.json'])
    core.require(set(frozen)==set(manifest)|{'MANIFEST.json'},'FROZEN_FILE_SET')
    for name,h in manifest.items():
        p=PurePosixPath(name)
        core.require(not p.is_absolute() and '..' not in p.parts and p.as_posix()==name and chr(92) not in name and ':' not in name,'FROZEN_PATH')
        core.require(sha256(frozen[name].encode()).hexdigest()==h,'FROZEN_HASH')
    core.require(sha256(packed['design_text'].encode()).hexdigest()==sc.PROPOSAL_SHA,'PROPOSAL_CHANGED')
    core.require(sha256(packed['requests_text'].encode()).hexdigest()==sc.REQUESTS_SHA,'REQUESTS_CHANGED')
    core.require(packed['design_text']==frozen['materials-proposal.json'] and packed['requests_text']==frozen['requests.json'],'FROZEN_BYTES_CHANGED')
    design=json.loads(packed['design_text']);requests=json.loads(packed['requests_text'])
    templates=json.loads(frozen['source-inputs.json']);parents=json.loads(frozen['source-parent-evidence.json'])
    core.require(design['protocol']==sc.PROTOCOL and len(design['cases'])==8 and design['repeats']==[1,2,3],'SCOPE')
    expected={'id':live.MODEL_ID,'revision':live.MODEL_REVISION,'pins':live.PINS,
        'generation':dict(live.GENERATION,max_new_tokens=1024),'max_input_tokens':live.MAX_INPUT_TOKENS,
        'dtype':'bfloat16','attention':'sdpa','enable_thinking':False}
    core.require(design['model']==expected and design['budget']=={'max_generations':240,'total_seconds':2700,'reserve_seconds':90,'max_raw_bytes':16384,'retries':0},'MODEL_BUDGET_CHANGED')
    for stage in sc.STAGES:
        core.require(design['schemas'][stage]==sc.SCHEMAS[stage] and json.loads(frozen['schemas/'+stage.lower()+'.json'])==design['schemas'][stage],'SCHEMA_CHANGED')
        core.require(design['prompts'][stage]==frozen['prompts/'+stage.lower()+'.txt'],'PROMPT_CHANGED')
    slots=design['allocation'];core.require(len(slots)==240 and len(requests)==240 and len(templates)==80 and len(parents)==32,'COUNTS')
    core.require(len({s['id'] for s in slots})==240 and Counter(s['stage'] for s in slots)=={'FORM':96,'CONFIRM':144},'ALLOCATION')
    for slot,req in zip(slots,requests):
        template=templates[slot['source_id']]
        core.require(req=={'id':slot['id'],'seed':slot['seed'],'messages':template['messages']},'REQUEST_REPLAY_CHANGED')
        core.require(not slot['parents'] and slot['source_parent_ids']==list(template['source_binding']['parents']),'NEW_PARENT_LEAK')
        core.require(sc.digest(req['messages'])==template['messages_sha256'],'SOURCE_MESSAGE_HASH')
        payload=sc.payload_of(req)
        core.require(req['messages'][0]=={'role':'system','content':design['prompts'][slot['stage']]} and payload['holder']==slot['role'],'INPUT_CONTRACT')
        if slot['stage']=='CONFIRM':
            core.require(len(slot['source_parent_ids'])==2,'SOURCE_PARENT_COUNT')
            own_id=sc.prior.form_id(slot['case'],slot['role'],slot['condition_not_for_model'])
            core.require(own_id in slot['source_parent_ids'],'SOURCE_OWN_PARENT')
            core.require(payload['own_judgment']==sc.prior.record(templates[own_id]['source_slot'],parents[own_id]['carry_answer'],'local'),'FROZEN_PARENT_CONTENT')
            for pid in slot['source_parent_ids']:
                parent=parents[pid]
                core.require(pid.startswith('ST02-'+slot['condition_not_for_model']+'-'),'SOURCE_PARENT_ARM')
                oldbinding=template['source_binding']['parents'][pid]
                core.require(oldbinding['carry_answer_sha256']==parent['hashes']['carry-answer.json'] and oldbinding['result_sha256']==parent['hashes']['result.json'],'SOURCE_PARENT_HASH')
                core.require(oldbinding['raw_answer_sha256']==parent['result']['files_sha256']['saved-answer.json'],'LEGACY_SAVED_ANSWER_HASH')
                core.require(sha256(parent['raw_answer'].encode()).hexdigest()==parent['hashes']['answer.txt'],'SOURCE_RAW_TEXT_HASH')
    return design,requests


def context_for(design, packed, slot, request, templates=None, parents=None):
    templates=templates if templates is not None else json.loads(packed['frozen']['source-inputs.json'])
    parents=parents if parents is not None else json.loads(packed['frozen']['source-parent-evidence.json'])
    template=templates[slot['source_id']];payload=sc.payload_of(request)
    case=next(c for c in design['cases'] if c['id']==slot['case'])
    binding={'kind':'FIXED_ST02_INPUT_REPLAY','source_id':slot['source_id'],'source_archive_sha256':design['source']['sha256'],
             'source_input_sha256':template['source_input_sha256'],'source_messages_sha256':template['messages_sha256'],
             'condition':slot['condition_not_for_model'],'repeat':slot['repeat'],'new_parent_ids':[],
             'source_parents':{pid:{'source_saved_answer_sha256':parents[pid]['result']['files_sha256']['saved-answer.json'],
                                   'source_raw_text_sha256':parents[pid]['hashes']['answer.txt'],
                                   'source_carry_answer_sha256':parents[pid]['hashes']['carry-answer.json'],
                                   'source_result_sha256':parents[pid]['hashes']['result.json']}
                               for pid in slot['source_parent_ids']}}
    summary,calc=sc.prior.own_summary(payload,case['medium_order'])
    supplied='own_experience_summary' in payload
    core.require(supplied==(slot['condition_not_for_model']=='EARLY'),'SUMMARY_SUPPLY')
    if supplied:core.require(payload['own_experience_summary']==summary,'OWN_SUMMARY_CHANGED')
    receipt={'own_summary':dict(calc,supplied_to_model=supplied),
             'joint_totals':sc.prior.joint_receipt(case,payload) if slot['stage']=='CONFIRM' else None}
    trace={'kind':'FIXED_SOURCE_REPLAY_NO_NEW_CARRY','binding':binding,'payload_sha256':sc.digest(payload),
           'fixed_own_judgment':payload.get('own_judgment'),'calculation_receipt':receipt,'semantic_repair':False}
    return {'slot':slot,'case_rows':case['experiences'],'payload':payload,'template':template,'trace':trace},binding


def run_routes(root,packed,backend=None,deadline=float('inf'),close_pending=False,checkpoint=None):
    design,requests=verify_root(root,packed);root=Path(root)
    templates=json.loads(packed['frozen']['source-inputs.json']);parents=json.loads(packed['frozen']['source-parent-evidence.json'])
    store=live.EvidenceStore(root,packed['contract']);rows={}
    for index,(slot,req) in enumerate(zip(design['allocation'],requests),1):
        context,binding=context_for(design,packed,slot,req,templates,parents)
        result=physical(store,req,binding,context,slot['stage'],design,None,backend,deadline,close_pending)
        if result is not None:rows[slot['id']]=result
        if backend is not None and index%20==0:
            print(f'{len(rows)}/240 responses closed; repeat {slot["repeat"]} {slot["stage"]}',flush=True)
        if backend is not None and checkpoint and index%40==0:checkpoint(index)
    return {'responses':rows}


def make_report(root,packed,rows):
    design,_=verify_root(root,packed);root=Path(root);results=rows['responses']
    core.require(set(results)=={s['id'] for s in design['allocation']},'REPORT_INCOMPLETE')
    report=sc.summarize(design,{sid:r['score'] for sid,r in results.items()})
    report.update(protocol=PROTOCOL,closed_logical_responses=240,
                  status_counts=dict(Counter(r['status'] for r in results.values())),
                  attempted_generations=len(list((root/'responses').glob('*/started.json'))))
    core.require(report['attempted_generations']<=240,'GENERATION_BUDGET')
    report['by_slot']=[dict(s,status=results[s['id']]['status'],score=results[s['id']]['score']) for s in design['allocation']]
    report['performance']={};report['normalization']={};synthetic=False;any_answers=False
    for stage in sc.STAGES:
        ids=[s['id'] for s in design['allocation'] if s['stage']==stage]
        answered=[sid for sid in ids if (root/'responses'/sid/'response.json').exists()]
        values=[live.read_json(root/'responses'/sid/'response.json') for sid in answered]
        any_answers=any_answers or bool(values);synthetic=synthetic or any(v.get('synthetic_fixture') for v in values)
        norms=[live.read_json(root/'responses'/sid/'normalization.json') for sid in answered]
        accepted=[results[sid]['score']['format_valid'] is True for sid in answered]
        report['normalization'][stage]={'answered':len(answered),'status':dict(Counter(n['status'] for n in norms)),
            'raw_schema_accepted':sum(ok and n['status']=='UNCHANGED' for ok,n in zip(accepted,norms)),
            'normalized_schema_accepted':sum(accepted),'removed_bytes':sum(n.get('removed_prefix_bytes',0)+n.get('removed_suffix_bytes',0) for n in norms)}
        inputs=[live.read_json(root/'responses'/sid/'input.json') for sid in answered]
        report['performance'][stage]={'planned_responses':len(ids),'responses':len(values),
            'input_tokens':[len(v['prepared']['input_ids']) for v in inputs],
            'output_tokens':[len(v['output_token_ids']) for v in values],
            'raw_bytes':[len(v['answer_text'].encode()) for v in values],
            'generation_seconds':[v['generation_seconds'] for v in values]}
    report['evidence_kind']='SYNTHETIC_TEST_NOT_MODEL_RESULTS' if synthetic else 'MODEL_RUN_EVIDENCE' if any_answers else 'NO_MODEL_ANSWERS'
    return report


def preflight(packed):
    import judgment_repeat_01_fixtures as fx
    design,requests=validate_payload(packed);outcomes={}
    for slot,req in zip(design['allocation'],requests):
        context,_=context_for(design,packed,slot,req)
        answer=fx.correct_answer(context['payload'],slot['stage'])
        outcomes[slot['id']]=sc.score(sc.enc(answer),slot,context['payload'],context['case_rows'])
    report=sc.summarize(design,outcomes)
    core.require(all(s['V'] is True for s in outcomes.values()),'SYNTHETIC_RESPONSE')
    core.require(report['formation_prediction']['status']=='NOT_IN_ALL_THREE_REPEATS','SYNTHETIC_TIE')
    return {'kind':'SYNTHETIC_PREFLIGHT_NOT_MODEL_RESULTS','status':'PASS','synthetic_answers':240,'model_generations':0,
            'fixed_source_inputs':80,'fixed_source_parents':32,'new_carry_edges':0}


def aggregate_archive(path,packed):
    manifest,files=read_archive(path)
    with tempfile.TemporaryDirectory(prefix='jr01-audit-') as temp:
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
            core.require(live.read_json(root/'tokenizer-binding.json')==json.loads(packed['design_text'])['source_tokenizer_binding'],'SOURCE_TOKENIZER_CHANGED')
            def checkpoint(n):export_zip(root,root.parent/f'npp-jr01-checkpoint-{root.name}-{n:03d}.zip','CHECKPOINT')
            run_routes(root,packed,backend,deadline,checkpoint=checkpoint)
    finally:
        rows=run_routes(root,packed,close_pending=True);report=make_report(root,packed,rows)
        live.write_json(root/('report-'+uuid.uuid4().hex+'.json'),report)
        print(json.dumps({'planned_responses':240,'model_calls':report['attempted_generations'],
                          'formation_prediction':report['formation_prediction']['status'],'status':report['status_counts']},ensure_ascii=False),flush=True)


if __name__=='__main__':worker(sys.argv[1],float(sys.argv[2]),len(sys.argv)>3 and sys.argv[3]=='AUDIT_ONLY')
