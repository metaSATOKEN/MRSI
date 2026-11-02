"""RU01 fixed independent readouts; immutable evidence, no ML imports at import time."""
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
import role_shared_use_01_design as sc

PROTOCOL = 'ROLE-SHARED-USE-01-RUN-v0.1'
DESIGN_SHA = '74188ddeabadad000b3cf03b5710ccb1845e15ecdb8c1166579e8552b4ede923'
REQUESTS_SHA = 'f747b48a288f31e9f96536923b66b7759037b928a3790a84aba01bffb3614544'


def contract_for(packed):
    return {'protocol': PROTOCOL, 'design_sha256': DESIGN_SHA, 'requests_sha256': REQUESTS_SHA,
        'source_hashes': {n: sha256(s.encode()).hexdigest() for n, s in packed['code'].items()},
        'frozen_hashes': {n: sha256(s.encode()).hexdigest() for n, s in packed['frozen'].items()},
        'max_generations': 128, 'seconds_including_setup': 2700, 'reserved_final_seconds': 90,
        'automatic_regenerations': 0, 'resume_generation': False, 'checkpoint_every': 32,
        'cloud_drive': 'not_used', 'retention': 'private_no_deletion_deadline', 'delivery': 'zip_download',
        'sharing': 'No response sharing across conditions, roles or repeats.',
        'normalization': 'Strict bare JSON first; exact json LF fence only; no value repair.',
        'eos_policy': 'Remove one final im_end only, preserving output tokens.'}


def validate_payload(packed):
    core.require(sha256(packed['design_text'].encode()).hexdigest() == DESIGN_SHA, 'DESIGN_CHANGED')
    core.require(sha256(packed['requests_text'].encode()).hexdigest() == REQUESTS_SHA, 'REQUESTS_CHANGED')
    design = json.loads(packed['design_text']); requests = json.loads(packed['requests_text'])
    core.require(len(design['runs']) == 16 and len(design['allocation']) == 128, 'SCOPE')
    core.require(requests == sc.requests(design), 'REQUESTS_CHANGED')
    core.require(packed['contract'] == contract_for(packed), 'CONTRACT_CHANGED')
    frozen = packed['frozen']; manifest = json.loads(frozen['MANIFEST.json'])
    core.require(len(manifest) == 75 and set(frozen) == set(manifest) | {'MANIFEST.json'}, 'FROZEN_FILE_SET')
    for name, expected in manifest.items():
        p = PurePosixPath(name)
        core.require(not p.is_absolute() and '..' not in p.parts and p.as_posix() == name
                     and '\\' not in name and ':' not in name, 'FROZEN_PATH')
        core.require(sha256(frozen[name].encode()).hexdigest() == expected, 'FROZEN_HASH')
    core.require(frozen['design.json'] == packed['design_text'] and frozen['requests.json'] == packed['requests_text'], 'FROZEN_DESIGN')
    for name in ('role_shared_use_01_design.py', *sc.DEPENDENCIES):
        core.require(packed['code'][name] == frozen[name], 'FROZEN_SCORING_CHANGED')
    for source in design['sources']:
        for kind in ('memory', 'result'):
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
    for module in (core, live, sc.base.base, sc.base.readout, sc.base, sc.receiver.envelope,
                   sc.receiver, sc, sys.modules[__name__]):
        path = Path(module.__file__)
        core.require(sha256(path.read_bytes()).hexdigest() == packed['contract']['source_hashes'][path.name], 'ACTIVE_CODE_CHANGED')
    allowed = {s['id'] for s in design['allocation']}
    if (root / 'responses').exists():
        core.require(all(p.is_dir() and not p.is_symlink() and p.name in allowed for p in (root / 'responses').iterdir()), 'UNEXPECTED_RESPONSE_ID')
        core.require(all(not p.is_symlink() and (p.is_file() or p.name in allowed) for p in (root / 'responses').rglob('*')), 'RESPONSE_FILE_TYPE')
    return design, requests


def input_binding(source, branch):
    return {'source_id': source['id'], 'source_archive_sha256': sc.SOURCE_SHA,
        'source_memory_path': source['source_memory_path'], 'source_memory_sha256': source['source_memory_sha256'],
        'source_result_path': source['source_result_path'], 'source_result_sha256': source['source_result_sha256'],
        'payload_sha256': branch['payload_sha256'], 'intervention_trace': branch['trace']}


def unknown(payload, design):
    return sc.score_response(None, payload, design['schema'])


def evaluate(response, payload, design):
    return sc.score_response(response['answer_text'].encode(), payload, design['schema'], response['finish_reason'])


def match_bytes(path, raw, create):
    if create and not path.exists(): live.write_new(path, raw)
    core.require(path.read_bytes() == raw, 'ARTIFACT_BYTES_MISMATCH:' + path.name)


def artifacts(folder, response, score, design, create):
    raw = response['answer_text'].encode()
    match_bytes(folder / 'answer.txt', raw, create)
    match_bytes(folder / 'decoded-with-special-tokens.txt', response['decoded_with_special_tokens'].encode(), create)
    receipt = sc.receiver.receive(raw, 'READ', response['finish_reason'])
    normalized = receipt.pop('normalized_bytes')
    match_artifact(folder / 'normalization.json', receipt, create)
    if normalized is not None: match_bytes(folder / 'normalized-answer.txt', normalized, create)
    else: core.require(not (folder / 'normalized-answer.txt').exists(), 'REJECTED_NORMALIZED_TEXT')
    answer = sc.base.parse(normalized) if normalized is not None else None
    accepted = answer is not None and not sc.base.shape(answer, design['schema'])
    decision = {'kind': 'FROM_ACTUAL_EXTRACTED_VALUES', 'raw_sha256': sha256(raw).hexdigest(),
        'normalized_sha256': receipt.get('normalized_sha256'), 'schema_accepted': accepted,
        'extracted_answer': answer if accepted else None,
        'actions': sc.actions(answer) if accepted else None, 'additional_model_calls': 0}
    core.require(decision['actions'] == score['actions'] and decision['extracted_answer'] == score['answer'], 'DECISION_SCORE_MISMATCH')
    match_artifact(folder / 'derived-decision.json', decision, create)


def status_for(response, score):
    if response['finish_reason'] != 'EOS': return response['finish_reason']
    return 'EOS' if score['format_valid'] else 'FORMAT_REJECT'


def run_routes(root, packed, backend=None, deadline=float('inf'), close_pending=False, checkpoint=None):
    design, requests = verify_root(root, packed); root = Path(root)
    branches = {b['id']: b for b in design['branches']}; sources = {s['id']: s for s in design['sources']}
    store = live.EvidenceStore(root, packed['contract']); rows = {}
    for slot, request in zip(design['allocation'], requests):
        branch = branches[slot['id']]; source = sources[slot['source_id']]
        result = physical(store, request, input_binding(source, branch), branch['payload'], design,
                          backend, deadline, close_pending)
        if result is not None:
            rows[slot['id']] = result
            if backend is not None and len(rows) % 8 == 0:
                attempted = len(list((root / 'responses').glob('*/started.json')))
                print(f'{len(rows)}/128 readouts closed; model calls {attempted}/128', flush=True)
                if checkpoint and len(rows) % 32 == 0: checkpoint(len(rows))
    return {'responses': rows}


def make_report(root, packed, rows):
    design, _ = verify_root(root, packed); root = Path(root); results = rows['responses']
    core.require(set(results) == {s['id'] for s in design['allocation']}, 'REPORT_INCOMPLETE')
    report = sc.summarize(design, {sid: r['score'] for sid, r in results.items()})
    report.update(protocol=PROTOCOL, closed_logical_responses=128,
        status_counts=dict(Counter(r['status'] for r in results.values())),
        attempted_generations=len(list((root / 'responses').glob('*/started.json'))))
    core.require(report['attempted_generations'] <= 128, 'GENERATION_BUDGET')
    report['by_slot'] = [dict(s, status=results[s['id']]['status'], score=results[s['id']]['score']) for s in design['allocation']]
    report['by_role'] = {role: {k: sc.base.counts(x['score'].get(k) for x in report['by_slot'] if x['role'] == role)
        for k in ('subject', 'animal', 'four_exact', 'channel', 'joint')} for role in ('A', 'B')}
    answered = [s['id'] for s in design['allocation'] if (root / 'responses' / s['id'] / 'response.json').exists()]
    values = [live.read_json(root / 'responses' / sid / 'response.json') for sid in answered]
    norms = [live.read_json(root / 'responses' / sid / 'normalization.json') for sid in answered]
    accepted = [results[sid]['score']['format_valid'] is True for sid in answered]
    report['normalization'] = {'answered': len(answered), 'status': dict(Counter(n['status'] for n in norms)),
        'raw_schema_accepted': sum(ok and n['status'] == 'UNCHANGED' for ok, n in zip(accepted, norms)),
        'normalized_schema_accepted': sum(accepted),
        'removed_bytes': sum(n.get('removed_prefix_bytes', 0) + n.get('removed_suffix_bytes', 0) for n in norms)}
    report['performance'] = {'planned_slots': 128, 'responses': len(values),
        'input_tokens': [len(live.read_json(root / 'responses' / sid / 'input.json')['prepared']['input_ids']) for sid in answered],
        'output_tokens': [len(v['output_token_ids']) for v in values],
        'raw_bytes': [len(v['answer_text'].encode()) for v in values],
        'generation_seconds': [v['generation_seconds'] for v in values]}
    return report


def preflight(packed):
    """Synthetic scoring only; never insert fixtures in model responses."""
    design, _ = validate_payload(packed)
    sources = {s['id']: s for s in design['sources']}; outcomes = {}
    for branch in design['branches']:
        source = sources[branch['source_id']]
        memory, trace = sc.intervene(source['memory'], branch['arm'])
        core.require(sc.input_payload(source, memory) == branch['payload'] and trace == branch['trace'], 'INTERVENTION_CHANGED')
        core.require(sc.digest(branch['payload']) == branch['payload_sha256'], 'PAYLOAD_HASH')
        core.require(sc.expected_answer(branch['payload']) == branch['gold'], 'EXPECTED_ANSWER_CHANGED')
        score = sc.score_response(sc.enc(branch['gold']), branch['payload'], design['schema'])
        core.require(score['joint'] is True, 'SYNTHETIC_SCORE')
        outcomes[branch['id']] = score
    report = sc.summarize(design, outcomes)
    core.require(report['path']['correct'] == 16 and report['criterion_status'] == 'MET', 'SYNTHETIC_SUMMARY')
    return {'kind': 'SYNTHETIC_PREFLIGHT_NOT_MODEL_RESULTS', 'fixture_responses': 128,
            'source_notes': 32, 'model_generations': 0, 'status': 'PASS'}


def aggregate_archive(path, packed):
    manifest, files = read_archive(path)
    with tempfile.TemporaryDirectory(prefix='ru01-audit-') as temp:
        root = Path(temp)
        for name, raw in files.items():
            p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        verify_root(root, packed)
        rows = run_routes(root, packed, close_pending=True); report = make_report(root, packed, rows)
        for p in root.glob('report-*.json'): core.require(live.read_json(p) == report, 'ARCHIVED_REPORT_MISMATCH')
        return {'archive_sha256': sha256(Path(path).read_bytes()).hexdigest(), 'manifest_files': len(files), 'kind': manifest['kind'], 'report': report}


def worker(root, seconds, audit_only=False):
    root = Path(root); packed = live.read_json(root / 'payload.json')
    def stop(signum, frame): live.STOP_REQUESTED = True
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    deadline = time.monotonic() + seconds
    try:
        if not audit_only:
            core.require(platform.system() == 'Linux' and Path('/content').is_dir(), 'COLAB_ONLY_NO_MODEL_LOAD')
            verify_root(root, packed)
            core.require(live.read_json(root / 'preflight.json') == preflight(packed), 'PREFLIGHT_CHANGED')
            core.require(not list((root / 'responses').glob('*/*')), 'NO_GENERATION_RESTART')
            backend = live.HuggingFaceBackend(root, deadline)
            def checkpoint(n): export_zip(root, root.parent / f'npp-ru01-checkpoint-{root.name}-{n:03d}.zip', 'CHECKPOINT')
            run_routes(root, packed, backend, deadline, checkpoint=checkpoint)
    finally:
        rows = run_routes(root, packed, close_pending=True); report = make_report(root, packed, rows)
        live.write_json(root / ('report-' + uuid.uuid4().hex + '.json'), report)
        print(json.dumps({'planned_responses': 128, 'model_calls': report['attempted_generations'],
                          'path': report['path'], 'status': report['status_counts']}, ensure_ascii=False), flush=True)


# Immutable physical response and archive helpers adapted from SX01.

def physical(store, request, binding, payload, design, backend, deadline, close_pending):
    """Execute/replay one immutable physical request. No retry or fixture fallback."""
    slot = {'id':request['id'],'seed':request['seed']}; folder = store.directory(slot)
    unk = unknown(payload,design)
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
        score = evaluate(response,payload,design)
        artifacts(folder,response,score,design,True)
        return store.finish(slot,status_for(response,score),score,'COMPONENT_SCORING')
    if store.completed(slot):
        result = store.load(slot)
        if (folder/'response.json').exists():
            core.require((folder/'started.json').exists(), 'RESPONSE_WITHOUT_START')
            response = read_response(folder,slot); score = evaluate(response,payload,design)
            core.require(score==result['score'], 'SCORE_REPLAY_MISMATCH')
            core.require(result['status']==status_for(response,score), 'STATUS_MISMATCH')
            artifacts(folder,response,score,design,False)
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
    core.require(len(list((store.root/'responses').glob('*/started.json'))) < 128,'GENERATION_BUDGET')
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
