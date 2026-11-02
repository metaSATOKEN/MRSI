"""TVR01 runtime copied from completed TB01 v0.1.1; fixed-input vote repeats."""
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
import three_role_vote_repeat_01_design as d
import three_role_vote_repeat_01_scoring as sc

PROTOCOL = 'THREE-ROLE-VOTE-REPEAT-01-RUN-v0.1'
IMPLEMENTATION = 'v0.1-fixed-prior-votes'
CHAT_TEMPLATE_SHA256 = 'a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
CODE_NAMES = ('cross_model_e1_01_offline_runtime.py', 'cross_model_e1_01_generation_runtime.py',
 'readout_split_01_scoring.py', 'update_readout_01_envelope.py',
 'three_role_boundary_01_design.py', 'three_role_boundary_01_scoring.py',
 'three_role_boundary_01_fixtures.py',
 'three_role_vote_repeat_01_design.py', 'three_role_vote_repeat_01_scoring.py',
 'three_role_vote_repeat_01_fixtures.py', 'three_role_vote_repeat_01_runtime.py',
 'three_role_vote_repeat_01_bootstrap.py')


def model_contract():
    return {'id': live.MODEL_ID, 'revision': live.MODEL_REVISION, 'pins': live.PINS,
            'generation': dict(live.GENERATION, max_new_tokens=1024), 'max_input_tokens': live.MAX_INPUT_TOKENS,
            'dtype': 'bfloat16', 'attention': 'sdpa', 'enable_thinking': False}


def contract_for(packed):
    return {'protocol': PROTOCOL, 'implementation': IMPLEMENTATION,
            'chat_template_sha256': CHAT_TEMPLATE_SHA256,
            'design_sha256': sha256(packed['design_text'].encode()).hexdigest(),
            'source_hashes': {n: sha256(s.encode()).hexdigest() for n, s in packed['code'].items()},
            'frozen_hashes': {n: sha256(s.encode()).hexdigest() for n, s in packed['frozen'].items()},
            'max_generations': 54, 'seconds_including_setup': 1800, 'automatic_regenerations': 0,
            'resume_generation': False, 'cloud_drive': 'not_used', 'retention': 'private_no_deletion_deadline'}


def validate_payload(packed):
    core.require(set(packed['code']) == set(CODE_NAMES), 'CODE_FILE_SET')
    core.require(packed['contract'] == contract_for(packed), 'CONTRACT_CHANGED')
    design = json.loads(packed['design_text'])
    core.require(design == d.build_design(model_contract(), json.loads(packed['frozen']['source-inputs.json'])), 'DESIGN_CHANGED')
    core.require(packed['frozen']['design.json'] == packed['design_text'], 'FROZEN_DESIGN_CHANGED')
    for name in list(packed['code']) + list(packed['frozen']):
        core.require(Path(name).name == name and ':' not in name and '\\' not in name, 'PAYLOAD_PATH')
    seen = set()
    for s in design['allocation']:
        core.require(s['id'] not in seen and set(s['parents']) <= seen, 'ALLOCATION_DEPENDENCIES')
        seen.add(s['id'])
    core.require(len(seen) == 54, 'SLOT_SET')
    return design


def initialize(root, packed):
    validate_payload(packed)
    live.write_new(root / 'design.json', packed['design_text'].encode())
    live.write_json(root / 'contract.json', packed['contract'])
    for directory in ('code', 'frozen'):
        for name, src in packed[directory].items():
            live.write_new(root / directory / name, src.encode())


def verify_root(root, packed):
    design = validate_payload(packed); root = Path(root)
    core.require((root / 'design.json').read_text() == packed['design_text'], 'SAVED_DESIGN')
    core.require(live.read_json(root / 'contract.json') == packed['contract'], 'SAVED_CONTRACT')
    if (root / 'payload.json').exists():
        core.require(live.read_json(root / 'payload.json') == packed, 'SAVED_PAYLOAD')
    for directory in ('code', 'frozen'):
        for name, src in packed[directory].items():
            core.require((root / directory / name).read_bytes() == src.encode(), 'SAVED_' + name)
    for module in (core, live, d, sc, sc.base, sc.base.d, sc.strict_json, sc.envelope, sys.modules[__name__]):
        p = Path(module.__file__)
        core.require(sha256(p.read_bytes()).hexdigest() == packed['contract']['source_hashes'][p.name], 'ACTIVE_CODE_CHANGED')
    allowed = {s['id'] for s in design['allocation']}
    if (root / 'responses').exists():
        core.require(all(p.is_dir() and not p.is_symlink() and p.name in allowed for p in (root / 'responses').iterdir()), 'UNEXPECTED_RESPONSE_ID')
        core.require(all(not p.is_symlink() for p in (root / 'responses').rglob('*')), 'RESPONSE_SYMLINK')
    return design


def verify_prepared(prepared, template):
    core.require(type(prepared['input_ids']) is list and all(type(x) is int for x in prepared['input_ids']), 'INPUT_TOKEN_TYPES')
    messages = template['messages']
    core.require(type(messages) is list and len(messages) == 2 and
                 [m.get('role') for m in messages] == ['system', 'user'] and
                 all(type(m.get('content')) is str for m in messages), 'INPUT_MESSAGE_SHAPE')
    # The pinned Qwen text-only chat template trims each message at its boundaries.
    # Compare the COMPLETE role-delimited serialization; do not strip internal text,
    # skip the guard, or merely check that a substring occurs somewhere in the prompt.
    expected = ''.join('<|im_start|>' + m['role'] + '\n' + m['content'].strip() + '<|im_end|>\n'
                       for m in messages) + '<|im_start|>assistant\n<think>\n\n</think>\n\n'
    core.require(prepared['rendered_prompt'] == expected, 'RENDERED_INPUT_CHANGED')
    core.require(prepared['rendered_prompt'].endswith('<|im_start|>assistant\n<think>\n\n</think>\n\n'), 'NONTHINKING_TEMPLATE')
    if 'expected_prepared' in template:
        core.require(prepared == template['expected_prepared'], 'FIXED_PRIOR_TOKENIZATION_CHANGED')


def check_tokenizer_inputs(root, packed, tokenizer):
    """Check exact old prompt AND token IDs before any model weights are loaded."""
    design = validate_payload(packed)
    core.require(sha256(tokenizer.get_chat_template().encode()).hexdigest() == CHAT_TEMPLATE_SHA256,
                 'CHAT_TEMPLATE_HASH_CHANGED')
    states = {}; checked = []
    for slot in design['allocation']:
        request = d.request_for(design, slot, states)
        rendered = tokenizer.apply_chat_template(request['messages'], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        ids = tokenizer(rendered, add_special_tokens=False, truncation=False)['input_ids']
        prepared = {'rendered_prompt': rendered, 'input_ids': ids}
        try:
            verify_prepared(prepared, dict(request, expected_prepared=d.source_for(design,slot)['prepared']))
            core.require(len(ids) <= live.MAX_INPUT_TOKENS, 'PREFLIGHT_INPUT_TOO_LONG')
        except BaseException:
            live.write_json(root / 'tokenizer-preflight-error.json', {'slot': slot, 'request': request, 'prepared': prepared})
            raise
        checked.append({'id': slot['id'], 'stage': slot['stage'], 'input_tokens': len(ids),
                        'rendered_sha256': sha256(rendered.encode()).hexdigest()})
    report = {'kind': 'TOKENIZER_PREFLIGHT_FIXED_PRIOR_INPUTS_NOT_NEW_RESULTS',
              'status': 'PASS', 'model_generations': 0, 'template_sha256': CHAT_TEMPLATE_SHA256, 'checked': checked}
    live.write_json(root / 'tokenizer-preflight.json', report)
    print('実tokenizerの入力検査: 全54予定入力が旧prompt・token列と完全一致。続いてモデルをロードします。', flush=True)
    return report


def unknown(context, stage, design, memory=None):
    return sc.score(None, context['slot'], context['payload'], context['case'])


def evaluate(response, context, stage, design, memory=None):
    return sc.score(response['answer_text'].encode(), context['slot'], context['payload'], context['case'], response['finish_reason'])


def artifacts(folder, response, score, context, stage, design, create):
    raw = response['answer_text'].encode()
    match_bytes(folder / 'answer.txt', raw, create)
    match_bytes(folder / 'decoded-with-special-tokens.txt', response['decoded_with_special_tokens'].encode(), create)
    norm = sc.envelope.normalize(raw, response['finish_reason']); normalized = norm.pop('normalized_bytes')
    match_artifact(folder / 'normalization.json', norm, create)
    if normalized is not None:
        match_bytes(folder / 'normalized-answer.txt', normalized, create)
    else:
        core.require(not (folder / 'normalized-answer.txt').exists(), 'UNEXPECTED_NORMALIZED')
    for name in ('saved-answer.json', 'carry-answer.json'):
        if score['answer'] is not None:
            match_artifact(folder / name, score['answer'], create)
        else:
            core.require(not (folder / name).exists(), 'REJECTED_SAVED_ANSWER')
    match_artifact(folder / 'carry-trace.json', context['trace'], create)
    match_artifact(folder / 'calculation-receipt.json', context['payload']['own_experience_summary'], create)


def parent_state(root, slot, rows):
    states = {}; binding = {}
    for pid in slot['parents']:
        core.require(pid in rows, 'PARENT_NOT_CLOSED')
        folder = root / 'responses' / pid; path = folder / 'carry-answer.json'
        states[pid] = live.read_json(path) if path.exists() else None
        binding[pid] = {'result_sha256': sha256((folder / 'result.json').read_bytes()).hexdigest(),
                        'carry_answer_sha256': sha256(path.read_bytes()).hexdigest() if path.exists() else None,
                        'answer_sha256': sha256((folder / 'answer.txt').read_bytes()).hexdigest() if (folder / 'answer.txt').exists() else None}
    return states, binding


def blocked(store, slot, score, binding, missing):
    folder = store.directory(slot)
    match_artifact(folder / 'blocked.json', {'parents': binding, 'missing_parents': missing}, True)
    core.require(not any((folder / n).exists() for n in ('input.json', 'started.json', 'response.json', 'carry-answer.json')), 'BLOCKED_HAS_RESPONSE')
    if store.completed(slot):
        result = store.load(slot)
        core.require(result['score'] == score and result['status'] == 'DEPENDENCY_MISSING', 'BLOCKED_REPLAY_MISMATCH')
        return result
    return store.finish(slot, 'DEPENDENCY_MISSING', score, 'DEPENDENCY_ONLY')


def run_routes(root, packed, backend=None, deadline=float('inf'), close_pending=False, checkpoint=None):
    root = Path(root); design = verify_root(root, packed)
    store = live.EvidenceStore(root, packed['contract']); rows = {}
    for index, slot in enumerate(design['allocation']):
        states, binding = parent_state(root, slot, rows)
        context = {'slot': slot, 'case': d.case_for(design, slot), 'payload': None}
        missing = [p for p in slot['parents'] if states[p] is None]
        if missing:
            result = blocked(store, slot, unknown(context, slot['stage'], design), binding, missing)
        else:
            request = d.request_for(design, slot, states)
            context['payload'] = d.payload_for(design, slot, states)
            core.require(json.loads(request['messages'][1]['content']) == context['payload'], 'ACTUAL_PAYLOAD_CHANGED')
            context['template'] = dict(request, expected_prepared=d.source_for(design,slot)['prepared'])
            context['trace'] = {'parents': binding, 'payload_sha256': d.digest(context['payload']),
                                'own_parent': slot.get('own_parent', slot['parents'][0] if slot['parents'] else None),
                                'receipt_parents': slot.get('vote_parents', []), 'semantic_repair': False,
                                'host_agreement_supplied': False,
                                'fixed_source_slot_id':d.source_for(design,slot)['source_slot_id'],
                                'fixed_source_input_sha256':d.source_for(design,slot)['source_input_sha256']}
            result = physical(store, request, binding, context, slot['stage'], design, None, backend, deadline, close_pending)
        if result is None:
            return rows
        rows[slot['id']] = result
        if backend is not None:
            print(f"{index+1}/54 {slot['stage']} {slot['id']}: {result['status']} strict={result['score']['strict']}", flush=True)
            if checkpoint and (index + 1) % 18 == 0:
                checkpoint(index + 1)
    return rows


def make_report(root, packed, rows):
    design = verify_root(root, packed)
    report = sc.summarize(design, {k: v['score'] for k, v in rows.items()})
    responses = [live.read_json(p) for p in (Path(root) / 'responses').glob('*/response.json')]
    report.update(protocol=PROTOCOL, planned_responses=54, attempted_generations=len(list((Path(root) / 'responses').glob('*/started.json'))),
                  status_counts=dict(Counter(v['status'] for v in rows.values())),
                  evidence_kind=('SYNTHETIC_TEST_NOT_MODEL_RESULTS' if any(v.get('synthetic_fixture') for v in responses)
                                 else 'MODEL_RUN_EVIDENCE' if responses else 'NO_MODEL_RESPONSES'),
                  output_tokens=sum(len(v['output_token_ids']) for v in responses),
                  generation_seconds=sum(v['generation_seconds'] for v in responses),
                  by_slot=[dict(s, status=rows[s['id']]['status'], score=rows[s['id']]['score']) for s in design['allocation']])
    core.require(report['attempted_generations'] <= 54, 'GENERATION_BUDGET')
    return report


def preflight(packed):
    from three_role_boundary_01_fixtures import ideal
    design = validate_payload(packed); states = {}; scores = {}
    for slot in design['allocation']:
        p = d.payload_for(design, slot, states); case = d.case_for(design, slot)
        answer = ideal(p, slot['stage'])
        result = sc.score(d.enc(answer), slot, p, case)
        core.require(result['strict'] is True, 'SYNTHETIC_PREFLIGHT')
        states[slot['id']] = result['answer']; scores[slot['id']] = result
    report = sc.summarize(design, scores)
    core.require(report['gate'] == 'PASS_IN_FIXED_REPEAT', 'SYNTHETIC_GATE')
    return {'kind': 'SYNTHETIC_PREFLIGHT_NOT_MODEL_RESULTS', 'status': 'PASS', 'slots': 54,
            'stage_counts': dict(Counter(s['stage'] for s in design['allocation'])), 'model_generations': 0}


def aggregate_archive(path, packed):
    manifest, files = read_archive(path)
    with tempfile.TemporaryDirectory(prefix='tvr01-audit-') as temp:
        root = Path(temp)
        for name, raw in files.items():
            p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        verify_root(root, packed)
        report = make_report(root, packed, run_routes(root, packed, close_pending=True))
        for p in root.glob('report-*.json'):
            core.require(live.read_json(p) == report, 'ARCHIVED_REPORT_MISMATCH')
        return {'archive_sha256': sha256(Path(path).read_bytes()).hexdigest(), 'files': len(files), 'report': report}


def worker(root, seconds, audit_only=False):
    root = Path(root); packed = live.read_json(root / 'payload.json')
    def stop(signum, frame):
        live.STOP_REQUESTED = True
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    deadline = time.monotonic() + seconds
    try:
        if not audit_only:
            core.require(platform.system() == 'Linux' and Path('/content').is_dir(), 'COLAB_ONLY_NO_MODEL_LOAD')
            verify_root(root, packed)
            core.require(live.read_json(root / 'preflight.json') == preflight(packed), 'PREFLIGHT_CHANGED')
            core.require(not list((root / 'responses').glob('*/*')), 'NO_GENERATION_RESTART')
            live.GENERATION = dict(live.GENERATION, max_new_tokens=1024)
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(live.MODEL_ID, revision=live.MODEL_REVISION,
                                                       token=False, trust_remote_code=False)
            check_tokenizer_inputs(root, packed, tokenizer)
            del tokenizer
            backend = live.HuggingFaceBackend(root, deadline)
            def checkpoint(n):
                export_zip(root, root.parent / f'npp-tvr01-checkpoint-{root.name}-{n:03d}.zip', 'CHECKPOINT')
            run_routes(root, packed, backend, deadline, close_pending=True, checkpoint=checkpoint)
    finally:
        report = make_report(root, packed, run_routes(root, packed, close_pending=True))
        live.write_json(root / ('report-' + uuid.uuid4().hex + '.json'), report)
        print(json.dumps({k: report[k] for k in ('gate', 'status_counts', 'attempted_generations', 'totals')}, ensure_ascii=False), flush=True)



def match_bytes(path,raw,create):
    if create and not path.exists():live.write_new(path,raw)
    core.require(path.read_bytes()==raw,'ARTIFACT_BYTES_MISMATCH:'+path.name)

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
    core.require(len(list((store.root/'responses').glob('*/started.json'))) < 54,'GENERATION_BUDGET')
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


if __name__ == '__main__':
    worker(Path(sys.argv[1]), float(sys.argv[2]), len(sys.argv) > 3 and sys.argv[3] == 'AUDIT_ONLY')
