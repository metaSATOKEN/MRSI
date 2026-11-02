"""OR01 evidence controller: one update, four saved branches, deduplicated reads.

Standard library at import time. Actual model loading is guarded inside worker().
"""
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
import owner_recency_01_scoring as sc

PROTOCOL = 'OWNER-RECENCY-01-RUN-v0.1'
DESIGN_SHA = 'd4d72a6cbbb950d2cbddb63d91912d2b716dab3880cc91414205f4750ae40291'
REQUESTS_SHA = 'b430d4534f70c8fa8840f5e1a8d893c723238d59866a3ba3cd64deb727fc321e'


def contract_for(packed):
    return {'protocol': PROTOCOL, 'design_sha256': DESIGN_SHA, 'requests_sha256': REQUESTS_SHA,
        'source_hashes': {n: sha256(s.encode()).hexdigest() for n,s in packed['code'].items()},
        'max_generations': 180, 'max_updates': 36, 'max_logical_reads': 144,
        'seconds_including_setup': 5400, 'automatic_regenerations': 0, 'resume_generation': False,
        'checkpoint_every_closed_parents': 6, 'cloud_drive': 'not_used',
        'retention': 'private_no_deletion_deadline', 'delivery': 'zip_download',
        'deduplication': 'Within common parent only; identical messages/schema/model/seed before generation.',
        'normalization': 'Strict bare JSON first; exact json LF fence only; no value repair.',
        'eos_policy': 'Remove one final im_end only, preserving output tokens.'}


def validate_payload(packed):
    core.require(sha256(packed['design_text'].encode()).hexdigest() == DESIGN_SHA, 'DESIGN_CHANGED')
    core.require(sha256(packed['requests_text'].encode()).hexdigest() == REQUESTS_SHA, 'REQUESTS_CHANGED')
    design = json.loads(packed['design_text']); requests = json.loads(packed['requests_text'])
    core.require(len(design['parents']) == 36 and len(design['pipelines']) == 144, 'SCOPE')
    core.require(requests == sc.requests(design), 'REQUESTS_CHANGED')
    core.require(packed['contract'] == contract_for(packed), 'CONTRACT_CHANGED')
    core.require(design['model'] == {'model':live.MODEL_ID,'revision':live.MODEL_REVISION,
        'pins':live.PINS,'generation':live.GENERATION,'max_input_tokens':live.MAX_INPUT_TOKENS,
        'enable_thinking':False,'dtype':'bfloat16','attention':'sdpa'}, 'MODEL_CHANGED')
    return design, requests


def initialize(root, packed):
    validate_payload(packed); root = Path(root); root.mkdir(parents=True, exist_ok=True)
    live.write_new(root/'design.json', packed['design_text'].encode())
    live.write_new(root/'requests.json', packed['requests_text'].encode())
    live.write_json(root/'contract.json', packed['contract'])
    for name,src in packed['code'].items(): live.write_new(root/'code'/name,src.encode())


def verify_root(root, packed):
    design, requests = validate_payload(packed); root = Path(root)
    for name,key in [('design.json','design_text'),('requests.json','requests_text')]:
        core.require((root/name).read_bytes() == packed[key].encode(), 'SAVED_' + name)
    core.require(live.read_json(root/'contract.json') == packed['contract'], 'SAVED_CONTRACT')
    for name,src in packed['code'].items():
        core.require((root/'code'/name).read_bytes() == src.encode(), 'SAVED_CODE')
    for module in (core,live,sc.ur.base,sc.ur.readout,sc.ur,sc.envelope,sc,sys.modules[__name__]):
        p = Path(module.__file__)
        core.require(sha256(p.read_bytes()).hexdigest() == packed['contract']['source_hashes'][p.name], 'ACTIVE_CODE_CHANGED')
    allowed = {p['id']+'-UPDATE' for p in design['parents']}
    allowed |= {p['id']+'-READ-U'+str(i) for p in design['parents'] for i in range(1,5)}
    for directory, ids in [('responses',allowed),('parents',{p['id'] for p in design['parents']}),
                           ('branches',{p['id'] for p in design['pipelines']})]:
        if (root/directory).exists():
            core.require(all(p.is_dir() and not p.is_symlink() and p.name in ids for p in (root/directory).iterdir()), 'UNEXPECTED_ID:'+directory)
    return design, requests


def match_bytes(path, raw, create):
    if create and not path.exists(): live.write_new(path,raw)
    core.require(path.read_bytes() == raw, 'ARTIFACT_BYTES_MISMATCH:'+path.name)


def derive_update(response, payload, schema):
    """Materialize ONLY from visible data. No case, expected_memory, or score input."""
    receipt = sc.receive(response['answer_text'].encode(), 'UPDATE', response['finish_reason'])
    normalized = receipt['normalized_bytes']; branches = dict.fromkeys(sc.ARMS); error = None
    if normalized is None:
        error = 'UNACCEPTED_PARENT'
    else:
        value = sc.ur.parse(normalized)
        if sc.ur.shape(value,schema): error = 'PARENT_SCHEMA'
        else:
            try:
                sc.latest_rows(payload,schema['properties']['private_note']['properties']['coverage'])
            except (ValueError,KeyError,TypeError) as exc:
                error = 'POLICY_INPUT_ERROR:'+str(exc)
            if error is None:
                for arm in sc.ARMS:
                    memory,trace = sc.transform(value,payload,arm,schema)
                    branches[arm] = {'memory':memory,'trace':trace}
    return receipt,branches,error


def evaluate(response, case, stage, design, memory=None):
    if stage == 'READ':
        return sc.score_read(response['answer_text'].encode(),memory,case,design['read_schema'],response['finish_reason'])
    prep = sc.prepare(design,case,response['answer_text'].encode(),response['finish_reason'])
    return {'gate':'PASS' if prep['error'] is None else 'UNRESOLVED' if prep['receipt']['status']=='UNRESOLVED' else 'REJECT',
            'proposal_score':prep['proposal_score'],'normalization':prep['receipt'],'error':prep['error']}


def unknown(case, stage, design, memory=None):
    if stage == 'UPDATE':
        return {'gate':'UNRESOLVED','proposal_score':None,'normalization':{'status':'UNRESOLVED','reason':'NO_RESPONSE'},'error':'NO_RESPONSE'}
    return sc.score_read(None,memory,case,design['read_schema'])


def artifacts(folder, response, score, case, stage, design, create):
    raw = response['answer_text'].encode()
    match_bytes(folder/'answer.txt',raw,create)
    match_bytes(folder/'decoded-with-special-tokens.txt',response['decoded_with_special_tokens'].encode(),create)
    receipt = sc.receive(raw,stage,response['finish_reason'])
    norm = receipt.pop('normalized_bytes')
    match_artifact(folder/'normalization.json',receipt,create)
    if norm is not None: match_bytes(folder/'normalized-answer.txt',norm,create)
    else: core.require(not (folder/'normalized-answer.txt').exists(), 'REJECTED_NORMALIZED_TEXT')
    if stage == 'UPDATE':
        _,branches,error = derive_update(response,case['update_payload'],design['update_schema'])
        core.require((error is None) == (score['gate']=='PASS'), 'DERIVE_SCORE_GATE')
    else:
        obj = sc.ur.parse(norm) if norm is not None else None
        coverage = obj.get('coverage') if isinstance(obj,dict) else None
        decision = {'kind':'FROM_ACTUAL_EXTRACTED_VALUES','raw_sha256':sha256(raw).hexdigest(),
            'normalized_sha256':receipt.get('normalized_sha256'),'coverage':coverage,
            'channel':sc.ur.compute_channel(coverage),'additional_model_calls':0}
        core.require(decision['channel'] == score['channel_output'], 'DECISION_SCORE_MISMATCH')
        match_artifact(folder/'derived-decision.json',decision,create)


def status_for(response, score, stage):
    if response['finish_reason'] != 'EOS': return response['finish_reason']
    if stage == 'UPDATE':
        if (score.get('error') or '').startswith('POLICY_INPUT_ERROR'): return 'POLICY_INPUT_ERROR'
        return 'EOS' if score['gate']=='PASS' else 'FORMAT_REJECT'
    return 'EOS' if score['format_valid'] else 'FORMAT_REJECT'


def physical(store, request, binding, case, stage, design, memory, backend, deadline, close_pending):
    """Execute/replay one immutable physical request. No retry or fixture fallback."""
    slot = {'id':request['id'],'seed':request['seed']}; folder = store.directory(slot)
    unk = unknown(case,stage,design,memory)
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
        score = evaluate(response,case,stage,design,memory)
        artifacts(folder,response,score,case,stage,design,True)
        return store.finish(slot,status_for(response,score,stage),score,'COMPONENT_SCORING')
    if store.completed(slot):
        result = store.load(slot)
        if (folder/'response.json').exists():
            core.require((folder/'started.json').exists(), 'RESPONSE_WITHOUT_START')
            response = read_response(folder,slot); score = evaluate(response,case,stage,design,memory)
            core.require(score==result['score'], 'SCORE_REPLAY_MISMATCH')
            core.require(result['status']==status_for(response,score,stage), 'STATUS_MISMATCH')
            artifacts(folder,response,score,case,stage,design,False)
        else:
            core.require(result['score']==unk and result['status'] in ('NOT_RUN','INTERRUPTED_UNCERTAIN','GENERATION_ERROR','INPUT_TOO_LONG','PREPARATION_ERROR'), 'UNANSWERED_SCORE')
            core.require(not any((folder/n).exists() for n in ('answer.txt','normalization.json','normalized-answer.txt','derived-decision.json')), 'UNANSWERED_ARTIFACT')
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
    core.require(len(list((store.root/'responses').glob('*/started.json'))) < 180,'GENERATION_BUDGET')
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


def make_branches(root, parent, update, case, design):
    folder = root/'responses'/(parent['id']+'-UPDATE')
    if (folder/'response.json').exists():
        _, derived, error = derive_update(read_response(folder,{'seed':parent['update_seed']}),case['update_payload'],design['update_schema'])
    else:
        derived = dict.fromkeys(sc.ARMS); error = 'NO_RESPONSE'
    result = {}; memories = {}; bindings = {}
    for arm in parent['arm_order']:
        pid = parent['id']+'-'+arm; dest = root/'branches'/pid; item = derived[arm]
        info = {'id':pid,'arm':arm,'update_id':parent['id']+'-UPDATE',
            'update_result_sha256':sha256((folder/'result.json').read_bytes()).hexdigest(),
            'status':'SAVED' if item is not None else 'DEPENDENCY_MISSING','error':error,
            'saved_memory_sha256':None,'policy_trace_sha256':None}
        if item is not None:
            match_artifact(dest/'saved-memory.json',item['memory'],True)
            match_artifact(dest/'policy-trace.json',item['trace'],True)
            for k,n in [('saved_memory_sha256','saved-memory.json'),('policy_trace_sha256','policy-trace.json')]:
                info[k]=sha256((dest/n).read_bytes()).hexdigest()
            # Score the serialized actual saved artifact, after materialization.
            memory = live.read_json(dest/'saved-memory.json')
            score = sc.score_memory(memory,case,design['update_schema'])
        else:
            core.require(not (dest/'saved-memory.json').exists() and not (dest/'policy-trace.json').exists(), 'BLOCKED_BRANCH_SAVED')
            memory = None; score = sc.ur.score_update(None,case,'REWRITE',design['update_schema'])
        info['score']=score
        match_artifact(dest/'branch.json',info,True)
        result[arm]=info;memories[arm]=memory
        bindings[arm]={'branch_json_sha256':sha256((dest/'branch.json').read_bytes()).hexdigest(),
                       'saved_memory_sha256':info['saved_memory_sha256']}
    return result,memories,bindings


def run_routes(root, packed, backend=None, deadline=float('inf'), close_pending=False, checkpoint=None):
    design, requests = verify_root(root,packed);root=Path(root)
    cases={c['id']:c for c in design['cases']};requests={q['id']:q for q in requests}
    store=live.EvidenceStore(root,packed['contract']);physical_rows={};logical={};visited=set();closed=0
    for parent in design['parents']:
        case=cases[parent['case']]; uid=parent['id']+'-UPDATE';visited.add(uid)
        update=physical(store,requests[uid],None,case,'UPDATE',design,None,backend,deadline,close_pending)
        if update is None:continue
        physical_rows[uid]=update
        branches,memories,bindings=make_branches(root,parent,update,case,design)
        groups=sc.read_groups(design,parent,case,memories)
        match_artifact(root/'parents'/parent['id']/'read-plan.json',groups,True)
        reads={}
        for group in groups:
            rid=group['id'];visited.add(rid)
            bind={'update_id':uid,'update_result_sha256':sha256((root/'responses'/uid/'result.json').read_bytes()).hexdigest(),
                  'input_identity_sha256':group['input_sha256'], 'branches':{arm:bindings[arm] for arm in group['arms']}}
            request={'id':rid,'seed':group['seed'],'messages':group['messages']}
            first=group['arms'][0]
            read=physical(store,request,bind,case,'READ',design,memories[first],backend,deadline,close_pending)
            if read is None:continue
            physical_rows[rid]=read
            for arm in group['arms']:reads[arm]=(rid,read)
        for arm in parent['arm_order']:
            pid=parent['id']+'-'+arm
            if memories[arm] is None:
                info={'id':pid,'status':'DEPENDENCY_MISSING','physical_read_id':None,
                    'physical_result_sha256':None,'update':branches[arm]['score'],
                    'read':sc.score_read(None,None,case,design['read_schema'])}
            elif arm not in reads:continue
            else:
                rid,read=reads[arm]
                info={'id':pid,'status':read['status'],'physical_read_id':rid,
                    'physical_result_sha256':sha256((root/'responses'/rid/'result.json').read_bytes()).hexdigest(),
                    'update':branches[arm]['score'],'read':read['score']}
            info['branch_json_sha256']=bindings[arm]['branch_json_sha256']
            match_artifact(root/'branches'/pid/'logical-result.json',info,True);logical[pid]=info
        if all(parent['id']+'-'+arm in logical for arm in sc.ARMS):
            closed+=1
            if backend is not None:
                attempted=len(list((root/'responses').glob('*/started.json')))
                print(f'{closed}/36 parents; {len(logical)}/144 branches; model calls {attempted}/180',flush=True)
                if checkpoint and closed%6==0:checkpoint(closed)
    present={p.name for p in (root/'responses').iterdir()} if (root/'responses').exists() else set()
    core.require(present <= visited,'ORPHAN_PHYSICAL_READ')
    for p in (root/'branches').iterdir() if (root/'branches').exists() else []:
        allowed={'branch.json','logical-result.json','saved-memory.json','policy-trace.json'}
        core.require(all(q.is_file() and not q.is_symlink() and (q.name in allowed or '.tmp-' in q.name) for q in p.iterdir()),'BRANCH_FILE_SET')
    return {'physical':physical_rows,'logical':logical,'closed_parents':closed}


def make_report(root, packed, rows):
    design,_=verify_root(root,packed);root=Path(root)
    core.require(set(rows['logical'])=={p['id'] for p in design['pipelines']} and rows['closed_parents']==36,'REPORT_INCOMPLETE')
    logical=rows['logical'];physical_rows=rows['physical']
    report=sc.summarize(design,{pid:{'update':r['update'],'read':r['read']} for pid,r in logical.items()})
    report.update(protocol=PROTOCOL,closed_logical_responses=180,closed_physical_slots=len(physical_rows),
        closed_parents=36,logical_status_counts=dict(Counter(r['status'] for r in logical.values())),
        physical_status_counts=dict(Counter(r['status'] for r in physical_rows.values())))
    report['attempted_generations']=len(list((root/'responses').glob('*/started.json')))
    core.require(report['attempted_generations']<=180,'GENERATION_BUDGET')
    cases={c['id']:c for c in design['cases']}; detail=[]
    for p in design['pipelines']:
        c=cases[p['case']];item=logical[p['id']]
        detail.append(dict(p,role=c['role'],notice_relation=c['notice_relation'],notice_target=c['notice_target'],
            source_group=c['source_group'],source_condition=c['source_condition'],latest_channel=c['latest_channel'],
            **{k:item[k] for k in ('update','read','status','physical_read_id')},
            end_to_end_exact=sc.ur.end_to_end(item['update'],item['read'])))
    report['by_pipeline']=detail
    report['common_updates']={p['id']:physical_rows[p['id']+'-UPDATE'] for p in design['parents']}
    report['components']={};report['strata']={}
    ukeys=('private_customer_exact','private_owner_exact','private_owner_revision_exact','private_observation_exact','shared_latest_exact','joint_state_exact')
    rkeys=('format_valid','four_exact','channel_note','channel_latest')
    for arm in sc.ARMS:
        report['components'][arm]={};report['strata'][arm]={}
        for subset in ('REPAIR','GUARD'):
            selected=[x for x in detail if x['condition']==arm and x['set']==subset]
            report['components'][arm][subset]={
                'update':{k:sc.ur.counts(x['update'].get(k) for x in selected) for k in ukeys},
                'read':{k:sc.ur.counts(x['read'].get(k) for x in selected) for k in rkeys},
                'shared_rows':{r:sc.ur.counts(x['update']['shared_rows_exact'][r] for x in selected) for r in ('A','B')},
                'end_to_end_exact':sc.ur.counts(x['end_to_end_exact'] for x in selected)}
            report['strata'][arm][subset]={dim:{str(v):{
                'ids':[x['id'] for x in selected if x[dim]==v],
                'joint_state_exact':sc.ur.counts(x['update']['joint_state_exact'] for x in selected if x[dim]==v),
                'end_to_end_exact':sc.ur.counts(x['end_to_end_exact'] for x in selected if x[dim]==v)}
                for v in sorted({x[dim] for x in selected})} for dim in ('role','notice_relation','replicate','case','source_condition')}
    performance={}; normalization={}
    for stage in ('UPDATE','READ'):
        ids=[rid for rid in physical_rows if ('-UPDATE' in rid)==(stage=='UPDATE')]
        answered=[rid for rid in ids if (root/'responses'/rid/'response.json').exists()]
        values=[live.read_json(root/'responses'/rid/'response.json') for rid in answered]
        norms=[live.read_json(root/'responses'/rid/'normalization.json') for rid in answered]
        performance[stage]={'planned_physical_slots':len(ids),'responses':len(answered),
            'input_tokens':[len(live.read_json(root/'responses'/rid/'input.json')['prepared']['input_ids']) for rid in answered],
            'output_tokens':[len(r['output_token_ids']) for r in values],
            'raw_bytes':[len(r['answer_text'].encode()) for r in values],
            'generation_seconds':[r['generation_seconds'] for r in values]}
        after=[physical_rows[rid]['score']['gate']=='PASS' if stage=='UPDATE' else physical_rows[rid]['score']['format_valid'] is True for rid in answered]
        normalization[stage]={'answered':len(answered),'status':dict(Counter(n['status'] for n in norms)),
            'raw_format_accepted':sum(ok and n['status']=='UNCHANGED' for ok,n in zip(after,norms)),
            'normalized_format_accepted':sum(after),'removed_bytes':sum(n.get('removed_prefix_bytes',0)+n.get('removed_suffix_bytes',0) for n in norms)}
    report['performance']=performance;report['normalization']=normalization
    physical_read_ids={x['physical_read_id'] for x in detail if x['physical_read_id'] is not None}
    report['read_sharing']={'logical_reads':144,'logical_reads_with_input':sum(x['physical_read_id'] is not None for x in detail),
        'unique_physical_read_slots':len(physical_read_ids),'recovered_physical_read_responses':performance['READ']['responses'],
        'mapping':{rid:[x['id'] for x in detail if x['physical_read_id']==rid] for rid in sorted(physical_read_ids)}}
    return report


def preflight(packed):
    design,_=validate_payload(packed)
    cases={c['id']:c for c in design['cases']}
    for parent in design['parents']:
        c=cases[parent['case']];value=c['expected_memory'];response={'answer_text':sc.ur.enc(value).decode(),'finish_reason':'EOS'}
        receipt,branches,error=derive_update(response,c['update_payload'],design['update_schema'])
        core.require(error is None and all(x['memory']==value for x in branches.values()),'SYNTHETIC_BRANCH')
        groups=sc.read_groups(design,parent,c,{a:b['memory'] for a,b in branches.items()})
        core.require(len(groups)==1 and len(groups[0]['arms'])==4,'SYNTHETIC_SHARED_READ')
    return {'kind':'SYNTHETIC_PREFLIGHT_NOT_MODEL_RESULTS','parents':36,'branches':144,'model_generations':0,'status':'PASS'}


def aggregate_archive(path, packed):
    manifest,files=read_archive(path)
    with tempfile.TemporaryDirectory(prefix='or01-audit-') as temp:
        root=Path(temp)
        for name,raw in files.items():
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        verify_root(root,packed)  # Archive code is compared, never executed.
        rows=run_routes(root,packed,close_pending=True);report=make_report(root,packed,rows)
        for p in root.glob('report-*.json'):
            core.require(live.read_json(p)==report,'ARCHIVED_REPORT_MISMATCH')
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
            core.require(not list((root/'responses').glob('*/started.json')),'NO_GENERATION_RESTART')
            backend=live.HuggingFaceBackend(root,deadline)
            def checkpoint(n):export_zip(root,root.parent/f'npp-or01-checkpoint-{root.name}-{n:02d}.zip','CHECKPOINT')
            run_routes(root,packed,backend,deadline,checkpoint=checkpoint)
    finally:
        rows=run_routes(root,packed,close_pending=True);report=make_report(root,packed,rows)
        live.write_json(root/('report-'+uuid.uuid4().hex+'.json'),report)
        print(json.dumps({'parents':36,'logical_reads':144,'model_calls':report['attempted_generations'],
                          'unique_reads':report['read_sharing']['unique_physical_read_slots'],
                          'status':report['physical_status_counts']},ensure_ascii=False),flush=True)


# Shared response and ZIP helpers are appended verbatim from UR01 by the build preparation.


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


if __name__ == '__main__':
    worker(sys.argv[1],float(sys.argv[2]),len(sys.argv)>3 and sys.argv[3]=='AUDIT_ONLY')
