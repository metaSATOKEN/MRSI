"""CU01 immutable evidence controller. Stdlib at import; model loading only in worker."""
from collections import Counter
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
import customer_update_01_design as sc

PROTOCOL = 'CUSTOMER-UPDATE-01-RUN-v0.1'
DESIGN_SHA = 'ee42c13b0f49f3c0696de5715330b80c37b47b790ab100f657064d8959f57f3f'
REQUESTS_SHA = '92ae04521e8dfd9557e8ec5cb7f0058cd70f4ca22a3e454a72cb8cd7c2e0d758'


def contract_for(packed):
    return {'protocol': PROTOCOL, 'design_sha256': DESIGN_SHA, 'requests_sha256': REQUESTS_SHA,
        'source_hashes': {n: sha256(s.encode()).hexdigest() for n,s in packed['code'].items()},
        'frozen_hashes': {n: sha256(t.encode()).hexdigest() for n,t in packed['frozen'].items()},
        'max_generations': 96, 'max_updates': 64, 'max_reads': 32, 'seconds_including_setup': 2700, 'reserved_final_seconds': 90,
        'automatic_regenerations': 0, 'resume_generation': False, 'checkpoint_every_closed_pairs': 2,
        'cloud_drive': 'not_used', 'retention': 'private_no_deletion_deadline', 'delivery': 'zip_download',
        'sharing': 'No response sharing across roles or repeats.',
        'normalization': 'Strict bare JSON first; exact json LF fence only; no value repair.',
        'eos_policy': 'Remove one final im_end only, preserving output tokens.'}


def validate_payload(packed):
    core.require(sha256(packed['design_text'].encode()).hexdigest() == DESIGN_SHA, 'DESIGN_CHANGED')
    core.require(sha256(packed['requests_text'].encode()).hexdigest() == REQUESTS_SHA, 'REQUESTS_CHANGED')
    design = json.loads(packed['design_text']); requests = json.loads(packed['requests_text'])
    core.require(len(design['runs']) == 16 and len(design['allocation']) == 96, 'SCOPE')
    core.require(requests == sc.initial_requests(design), 'REQUESTS_CHANGED')
    core.require(packed['contract'] == contract_for(packed), 'CONTRACT_CHANGED')
    frozen = packed['frozen']; manifest = json.loads(frozen['MANIFEST.json'])
    core.require(len(manifest) == 30 and set(frozen) == set(manifest) | {'MANIFEST.json'}, 'FROZEN_FILE_SET')
    for name, expected in manifest.items():
        p = PurePosixPath(name)
        core.require(not p.is_absolute() and '..' not in p.parts and p.as_posix() == name
                     and '\\' not in name and ':' not in name, 'FROZEN_PATH')
        core.require(sha256(frozen[name].encode()).hexdigest() == expected, 'FROZEN_HASH')
    core.require(frozen['design.json'] == packed['design_text'] and frozen['initial-requests.json'] == packed['requests_text'], 'FROZEN_DESIGN')
    for name in ('customer_update_01_design.py', *sc.DEPENDENCIES):
        core.require(packed['code'][name] == frozen[name], 'FROZEN_SCORING_CHANGED')
    for source in design['sources']:
        for kind in ('memory',):
            raw = frozen['sources/' + source['id'] + '/' + kind + '.json'].encode()
            core.require(sha256(raw).hexdigest() == source['source_' + kind + '_sha256'], 'SOURCE_BYTES')
            if kind == 'memory': core.require(json.loads(raw) == source['memory'], 'SOURCE_CONTENT')
    core.require(design['model'] == {'model': live.MODEL_ID, 'revision': live.MODEL_REVISION,
        'pins': live.PINS, 'generation': live.GENERATION, 'max_input_tokens': live.MAX_INPUT_TOKENS,
        'enable_thinking': False, 'dtype': 'bfloat16', 'attention': 'sdpa'}, 'MODEL_CHANGED')
    return design, requests


def initialize(root, packed):
    validate_payload(packed); root = Path(root); root.mkdir(parents=True, exist_ok=True)
    live.write_new(root / 'design.json', packed['design_text'].encode())
    live.write_new(root / 'requests.json', packed['requests_text'].encode())
    live.write_json(root / 'contract.json', packed['contract'])
    for directory, key in [('code', 'code'), ('frozen', 'frozen')]:
        for name, src in packed[key].items(): live.write_new(root / directory / name, src.encode())


def verify_root(root, packed):
    design, requests = validate_payload(packed); root = Path(root)
    for name, key in [('design.json', 'design_text'), ('requests.json', 'requests_text')]:
        core.require((root / name).read_bytes() == packed[key].encode(), 'SAVED_' + name)
    core.require(live.read_json(root / 'contract.json') == packed['contract'], 'SAVED_CONTRACT')
    if (root / 'payload.json').exists(): core.require(live.read_json(root / 'payload.json') == packed, 'SAVED_PAYLOAD')
    for directory, key in [('code', 'code'), ('frozen', 'frozen')]:
        for name, src in packed[key].items():
            core.require((root / directory / name).read_bytes() == src.encode(), 'SAVED_' + key.upper())
    for module in (core, live, sc.base.base, sc.base.readout, sc.base, sc.sx.policy.envelope,
                   sc.sx.policy, sc.sx, sc.ru, sc, sys.modules[__name__]):
        path = Path(module.__file__)
        core.require(sha256(path.read_bytes()).hexdigest() == packed['contract']['source_hashes'][path.name], 'ACTIVE_CODE_CHANGED')
    allowed = {s['id'] for s in design['allocation']}
    if (root / 'responses').exists():
        core.require(all(p.is_dir() and not p.is_symlink() and p.name in allowed for p in (root / 'responses').iterdir()), 'UNEXPECTED_RESPONSE_ID')
        core.require(all(not p.is_symlink() and (p.is_file() or p.name in allowed) for p in (root / 'responses').rglob('*')), 'RESPONSE_FILE_TYPE')
    return design, requests


def match_bytes(path, raw, create):
    if create and not path.exists():live.write_new(path,raw)
    core.require(path.read_bytes()==raw,'ARTIFACT_BYTES_MISMATCH:'+path.name)


def unknown(context, stage, design, memory=None):
    if stage=='READ':
        return sc.score_read(None,memory,context['case'],context['role'],design['read_schema'])
    return dict(sc.score_memory(None,context['case'],context['role'],stage),
        proposal_score=None,normalized_schema_accepted=None,error='NO_RESPONSE',
        normalization={'status':'UNRESOLVED','reason':'NO_RESPONSE'})


def evaluate(response, context, stage, design, memory=None):
    raw=response['answer_text'].encode(); finish=response['finish_reason']
    if stage=='READ':
        return sc.score_read(raw,memory,context['case'],context['role'],design['read_schema'],finish)
    derived,score=sc.evaluate_update(raw,context['payload'],design,context['case'],context['role'],stage,finish)
    score['normalized_schema_accepted']=derived['proposal'] is not None
    return score


def artifacts(folder, response, score, context, stage, design, create):
    raw=response['answer_text'].encode()
    match_bytes(folder/'answer.txt',raw,create)
    match_bytes(folder/'decoded-with-special-tokens.txt',response['decoded_with_special_tokens'].encode(),create)
    receipt=sc.receive(raw,'READ' if stage=='READ' else 'UPDATE',response['finish_reason'])
    normalized=receipt.pop('normalized_bytes')
    match_artifact(folder/'normalization.json',receipt,create)
    if normalized is not None:match_bytes(folder/'normalized-answer.txt',normalized,create)
    else:core.require(not (folder/'normalized-answer.txt').exists(),'REJECTED_NORMALIZED_TEXT')
    if stage!='READ':
        derived=sc.derive_update(raw,context['payload'],design['update_schema'],response['finish_reason'])
        for name,value in [('proposal.json',derived['proposal']),('saved-memory.json',derived['memory']),('policy-trace.json',derived['trace'])]:
            if value is not None:match_artifact(folder/name,value,create)
            else:core.require(not (folder/name).exists(),'REJECTED_SAVED_ARTIFACT:'+name)
        if derived['memory'] is not None:
            actual=live.read_json(folder/'saved-memory.json')
            reread=sc.score_memory(actual,context['case'],context['role'],stage)
            core.require(all(score[k]==v for k,v in reread.items()),'SAVED_SCORE_MISMATCH')
    else:
        answer=sc.base.parse(normalized) if normalized is not None else None
        accepted=answer is not None and not sc.base.shape(answer,design['read_schema'])
        decision={'kind':'FROM_ACTUAL_EXTRACTED_VALUES','raw_sha256':sha256(raw).hexdigest(),
            'normalized_sha256':receipt.get('normalized_sha256'),'schema_accepted':accepted,
            'extracted_answer':answer if accepted else None,
            'actions':sc.ru.actions(answer) if accepted else None,'additional_model_calls':0}
        core.require(decision['actions']==score['actions'] and decision['extracted_answer']==score['answer'],'DECISION_SCORE_MISMATCH')
        match_artifact(folder/'derived-decision.json',decision,create)



def status_for(response, score, stage):
    if response['finish_reason']!='EOS':return response['finish_reason']
    if stage!='READ' and (score.get('error') or '').startswith('INPUT_CONTRACT:'):return 'INPUT_CONTRACT_ERROR'
    return 'EOS' if score.get('format_valid') is True else 'FORMAT_REJECT'


def parent_state(root, slot, rows):
    """Read actual serialized parents, binding content and result identity."""
    states={}; binding={}
    for pid in slot['parents']:
        if pid not in rows:return None,None
        folder=root/'responses'/pid;path=folder/'saved-memory.json'
        states[pid]=live.read_json(path) if path.exists() else None
        binding[pid]={'result_sha256':sha256((folder/'result.json').read_bytes()).hexdigest(),
                      'saved_memory_sha256':sha256(path.read_bytes()).hexdigest() if path.exists() else None}
    return states,binding


def blocked(store, slot, score, status, binding, detail):
    folder=store.directory(slot)
    expected={'status':status,'parents':binding,'detail':detail}
    match_artifact(folder/'blocked.json',expected,True)
    forbidden=('input.json','started.json','response.json','answer.txt','saved-memory.json','proposal.json','policy-trace.json','normalization.json','normalized-answer.txt','derived-decision.json')
    core.require(not any((folder/n).exists() for n in forbidden),'BLOCKED_HAS_RESPONSE')
    if store.completed(slot):
        result=store.load(slot)
        core.require(result['score']==score and result['status']==status,'BLOCKED_REPLAY_MISMATCH')
        return result
    return store.finish(slot,status,score,'DEPENDENCY_OR_INPUT_CONTRACT')


def source_state(root, source):
    path=Path(root)/'frozen'/'sources'/source['id']/'memory.json'
    core.require(sha256(path.read_bytes()).hexdigest()==source['source_memory_sha256'],'SOURCE_BYTES')
    memory=live.read_json(path)
    core.require(memory==source['memory'],'SOURCE_CONTENT')
    return memory, {k:source[k] for k in ('id','kind','case','role','source_memory_sha256')}


def run_routes(root, packed, backend=None, deadline=float('inf'), close_pending=False, checkpoint=None):
    design,initial=verify_root(root,packed);root=Path(root)
    initial={q['id']:q for q in initial};cases={c['id']:c for c in design['cases']}
    sources={s['id']:s for s in design['sources']}
    store=live.EvidenceStore(root,packed['contract']);rows={};closed=0
    for run in design['runs']:
        slots=[s for s in design['allocation'] if s['run']==run['id']]
        for slot in slots:
            case=cases[slot['case']];stage=slot['stage'];role=slot['role']
            context={'case':case,'role':role,'payload':None}
            states,bindings=parent_state(root,slot,rows)
            if states is None:continue
            memory=states.get(slot['parents'][0]) if slot['parents'] else None
            source_binding=None
            if stage=='CHANGE':memory,source_binding=source_state(root,sources[slot['source_id']])
            if any(v is None for v in states.values()):
                rows[slot['id']]=blocked(store,slot,unknown(context,stage,design,memory),
                    'DEPENDENCY_MISSING',bindings,{'missing_parents':[k for k,v in states.items() if v is None]})
                continue
            try:
                if stage=='READ':
                    context['payload']=sc.ru.input_payload({'role':role,'scene':case['scene'],'item':case['item']},memory)
                    request=sc.request_for(design,slot,states)
                else:
                    payload=sc.update_payload(case,role,stage,memory)
                    sc.validate_input(payload,design['update_schema'])
                    context['payload']=payload
                    request={'id':slot['id'],'seed':slot['seed'],'messages':[
                        {'role':'system','content':design['update_prompt']},
                        {'role':'user','content':'\n資料JSON:\n'+sc.enc(payload).decode()}]}
                    if stage=='CHANGE':core.require(request==initial[slot['id']],'INITIAL_REQUEST_CHANGED')
            except (ValueError,KeyError,TypeError) as error:
                rows[slot['id']]=blocked(store,slot,unknown(context,stage,design,memory),
                    'INPUT_CONTRACT_ERROR',bindings,{'type':type(error).__name__,'message':str(error)})
                continue
            binding={'stage':stage,'role':role,'parents':bindings}
            if source_binding is not None:binding['source']=source_binding
            result=physical(store,request,binding,context,stage,design,memory,backend,deadline,close_pending)
            if result is not None:rows[slot['id']]=result
        if all(s['id'] in rows for s in slots):
            closed+=1
            if backend is not None:
                attempted=len(list((root/'responses').glob('*/started.json')))
                print(f'{closed}/16 pair runs; {len(rows)}/96 slots; model calls {attempted}/96',flush=True)
                if checkpoint and closed%2==0:checkpoint(closed)
    return {'responses':rows,'closed_pairs':closed}


def make_report(root, packed, rows):
    design,_=verify_root(root,packed);root=Path(root);results=rows['responses']
    core.require(set(results)=={s['id'] for s in design['allocation']} and rows['closed_pairs']==16,'REPORT_INCOMPLETE')
    report=sc.summarize(design,{sid:r['score'] for sid,r in results.items()})
    report.update(protocol=PROTOCOL,closed_logical_responses=96,closed_pairs=16,
        status_counts=dict(Counter(r['status'] for r in results.values())),
        attempted_generations=len(list((root/'responses').glob('*/started.json'))))
    core.require(report['attempted_generations']<=96,'GENERATION_BUDGET')
    count=report['path'];report['path_fraction_missing_bounds']=[count['correct']/16,(count['correct']+count['unresolved'])/16]
    report['by_slot']=[dict(s,status=results[s['id']]['status'],score=results[s['id']]['score']) for s in design['allocation']]
    for stage in sc.STAGES:
        report['components'][stage]['format_valid']=sc.base.counts(x['score'].get('format_valid') for x in report['by_slot'] if x['stage']==stage)
    report['performance']={};report['normalization']={}
    for stage in ('UPDATE','READ'):
        ids=[s['id'] for s in design['allocation'] if (s['stage']=='READ')==(stage=='READ')]
        answered=[sid for sid in ids if (root/'responses'/sid/'response.json').exists()]
        values=[live.read_json(root/'responses'/sid/'response.json') for sid in answered]
        norms=[live.read_json(root/'responses'/sid/'normalization.json') for sid in answered]
        accepted=[results[sid]['score'].get('format_valid') is True if stage=='READ' else results[sid]['score']['normalized_schema_accepted'] for sid in answered]
        report['normalization'][stage]={'answered':len(answered),'status':dict(Counter(n['status'] for n in norms)),
            'raw_schema_accepted':sum(ok and n['status']=='UNCHANGED' for ok,n in zip(accepted,norms)),
            'normalized_schema_accepted':sum(accepted),'removed_bytes':sum(n.get('removed_prefix_bytes',0)+n.get('removed_suffix_bytes',0) for n in norms)}
        report['performance'][stage]={'planned_slots':len(ids),'responses':len(values),
            'input_tokens':[len(live.read_json(root/'responses'/sid/'input.json')['prepared']['input_ids']) for sid in answered],
            'output_tokens':[len(v['output_token_ids']) for v in values],
            'raw_bytes':[len(v['answer_text'].encode()) for v in values],
            'generation_seconds':[v['generation_seconds'] for v in values]}
    return report


def preflight(packed):
    design,_=validate_payload(packed);states={};outcomes={};updates=reads=0
    cases={c['id']:c for c in design['cases']}
    for slot in design['allocation']:
        case=cases[slot['case']];role=slot['role'];stage=slot['stage']
        payload=sc.slot_payload(design,slot,states)
        if stage=='READ':
            raw=sc.enc(sc.ru.expected_answer(payload))
            score=sc.score_read(raw,states[slot['parents'][0]],case,role,design['read_schema'])
            reads+=1
        else:
            bodies={r['record_id']:r['body'] for r in payload['records']}
            proposal={'private_note':json.loads(json.dumps(bodies['PRIVATE'])),'shared_note':bodies['GROUP']}
            customer=proposal['private_note']['customer'];notice=payload['customer_notice']
            if notice['subject']==payload['holder'] and notice['revision']>customer['revision']:
                proposal['private_note']['customer']=notice
            raw=sc.enc(proposal)
            result,score=sc.evaluate_update(raw,payload,design,case,role,stage)
            core.require(result['memory']==sc.expected_memory(case,role,stage),'SYNTHETIC_POLICY_CHAIN')
            states[slot['id']]=result['memory'];updates+=1
        outcomes[slot['id']]=score
    report=sc.summarize(design,outcomes)
    core.require(report['path']['correct']==16,'SYNTHETIC_PATH')
    return {'kind':'SYNTHETIC_PREFLIGHT_NOT_MODEL_RESULTS','materials':8,'updates_checked':updates,
        'reads_checked':reads,'model_generations':0,'status':'PASS'}


def aggregate_archive(path, packed):
    manifest,files=read_archive(path)
    with tempfile.TemporaryDirectory(prefix='cu01-audit-') as temp:
        root=Path(temp)
        for name,raw in files.items():
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        verify_root(root,packed)
        rows=run_routes(root,packed,close_pending=True);report=make_report(root,packed,rows)
        for p in root.glob('report-*.json'):core.require(live.read_json(p)==report,'ARCHIVED_REPORT_MISMATCH')
        return {'archive_sha256':sha256(Path(path).read_bytes()).hexdigest(),'manifest_files':len(files),'kind':manifest['kind'],'report':report}


def worker(root, seconds, audit_only=False):
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
            backend=live.HuggingFaceBackend(root,deadline)
            def checkpoint(n):export_zip(root,root.parent/f'npp-cu01-checkpoint-{root.name}-{n:02d}.zip','CHECKPOINT')
            run_routes(root,packed,backend,deadline,checkpoint=checkpoint)
    finally:
        rows=run_routes(root,packed,close_pending=True);report=make_report(root,packed,rows)
        live.write_json(root/('report-'+uuid.uuid4().hex+'.json'),report)
        print(json.dumps({'closed_pairs':16,'planned_responses':96,'model_calls':report['attempted_generations'],
                          'path':report['path'],'status':report['status_counts']},ensure_ascii=False),flush=True)


# The immutable physical response/ZIP helpers are copied from the tested OR01 runner below.


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
            core.require(not any((folder/n).exists() for n in ('answer.txt','normalization.json','normalized-answer.txt','derived-decision.json','saved-memory.json','policy-trace.json','proposal.json')), 'UNANSWERED_ARTIFACT')
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
    core.require(len(list((store.root/'responses').glob('*/started.json'))) < 96,'GENERATION_BUDGET')
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
    core.require(type(ids) is list and all(type(x) is int for x in ids) and len(ids) <= 2048, 'OUTPUT_TOKENS')
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
        core.require(len(names) == len(set(names)) and len(names) <= 5000 and sum(m.file_size for m in members) <= 250_000_000, 'ARCHIVE_LIMIT')
        for m in members:
            p = PurePosixPath(m.filename)
            core.require(not p.is_absolute() and '..' not in p.parts and p.as_posix() == m.filename and '\\' not in m.filename and ':' not in m.filename and not m.is_dir() and not stat.S_ISLNK(m.external_attr >> 16), 'ARCHIVE_PATH')
        files = {n: z.read(n) for n in names}
    manifest = json.loads(files.pop('FEEDBACK_MANIFEST.json'))
    core.require(manifest['protocol'] == PROTOCOL and set(files) == set(manifest['files_sha256']), 'ARCHIVE_MANIFEST')
    core.require(all(sha256(raw).hexdigest() == manifest['files_sha256'][n] for n, raw in files.items()), 'ARCHIVE_HASH')
    return manifest, files

if __name__=='__main__':
    worker(sys.argv[1],float(sys.argv[2]),len(sys.argv)>3 and sys.argv[3]=='AUDIT_ONLY')
