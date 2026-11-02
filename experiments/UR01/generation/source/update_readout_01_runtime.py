"""UPDATE-READOUT-01 execution/evidence. Import is standard-library-only."""
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
import update_readout_01_scoring as scoring

PROTOCOL = 'UPDATE-READOUT-01-RUN-v0.1'
DESIGN_SHA = 'c896e08550dcdc0f2b338437456044957858f7d9d92746e34330844692ddb8aa'
REQUESTS_SHA = '2f19596f163b2e50c3f27258c285bfad907053ecc5fd0a4d610bb9559cc37792'


def validate_payload(packed):
    core.require(sha256(packed['design_text'].encode()).hexdigest() == DESIGN_SHA, 'DESIGN_CHANGED')
    core.require(sha256(packed['requests_text'].encode()).hexdigest() == REQUESTS_SHA, 'REQUESTS_CHANGED')
    design, requests = json.loads(packed['design_text']), json.loads(packed['requests_text'])
    core.require(len(design['allocation']) == 144 and len(requests) == 72, 'SCOPE')
    core.require(requests == scoring.requests(design), 'REQUEST_ORDER_OR_CONTENT')
    for name, src in packed['code'].items():
        core.require(sha256(src.encode()).hexdigest() == packed['contract']['source_hashes'][name], 'CODE_HASH')
    core.require(packed['contract'] == contract_for(packed), 'CONTRACT_CHANGED')
    core.require(design['model'] == {'model': live.MODEL_ID, 'revision': live.MODEL_REVISION,
        'pins': live.PINS, 'generation': live.GENERATION, 'max_input_tokens': live.MAX_INPUT_TOKENS,
        'enable_thinking': False, 'dtype': 'bfloat16', 'attention': 'sdpa'}, 'MODEL_SETTINGS_CHANGED')
    return design, requests


def contract_for(packed):
    return {'protocol': PROTOCOL, 'design_sha256': DESIGN_SHA, 'requests_sha256': REQUESTS_SHA,
            'source_hashes': {n: sha256(s.encode()).hexdigest() for n, s in packed['code'].items()},
            'max_generations': 144, 'max_updates': 72, 'max_reads': 72,
            'seconds_including_setup': 5400, 'automatic_regenerations': 0,
            'resume_generation': False, 'checkpoint_every_closed_slots': 24, 'cloud_drive': 'not_used',
            'retention': 'private_no_deletion_deadline', 'delivery': 'zip_download',
            'dependency_policy': 'Actual saved memory only; structurally invalid UPDATE blocks its READ only.',
            'eos_policy': 'Remove one final im_end only, retaining raw token IDs; no text repair.'}


def initialize(root, packed):
    validate_payload(packed)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    live.write_new(root / 'design.json', packed['design_text'].encode())
    live.write_new(root / 'requests.json', packed['requests_text'].encode())
    live.write_json(root / 'contract.json', packed['contract'])
    for name, src in packed['code'].items():
        live.write_new(root / 'code' / name, src.encode())


def preflight(packed):
    """Synthetic checks only; no research responses, tokenizer, network or model."""
    design, requests = validate_payload(packed)
    cases = {c['id']: c for c in design['cases']}; memories = {}
    for slot in design['allocation']:
        case = cases[slot['case']]
        if slot['stage'] == 'UPDATE':
            value = scoring.score_update(scoring.enc(scoring.ideal_update(case, slot['condition'])),
                case, slot['condition'], design['schemas'][slot['condition']])
            core.require(value['gate'] == 'PASS' and value['joint_state_exact'], 'SYNTHETIC_UPDATE')
            memories[slot['pipeline']] = value['memory']
        else:
            memory = memories[slot['pipeline']]
            request = scoring.read_request(design, slot, case, memory)
            payload = json.loads(request['messages'][1]['content'].split('\n資料JSON:\n', 1)[1])
            core.require(set(payload) == set(case['original_notes_payload']), 'READ_INPUT_KEYS')
            raw = scoring.enc({'coverage': {r: {m: memory['shared_note']['coverage'][r][m]
                for m in ('paper', 'digital')} for r in ('A', 'B')}})
            value = scoring.score_read(raw, memory, case, design['read_schema'])
            core.require(value['format_valid'] and value['four_exact'] and value['channel_latest'], 'SYNTHETIC_READ')
    return {'kind': 'SYNTHETIC_PREFLIGHT_NOT_MODEL_RESULTS', 'fixture_responses': 144,
            'model_generations': 0, 'status': 'PASS'}


def verify_root(root, packed):
    design, requests = validate_payload(packed)
    root = Path(root)
    core.require((root / 'design.json').read_bytes() == packed['design_text'].encode(), 'SAVED_DESIGN_CHANGED')
    core.require((root / 'requests.json').read_bytes() == packed['requests_text'].encode(), 'SAVED_REQUESTS_CHANGED')
    core.require(live.read_json(root / 'contract.json') == packed['contract'], 'SAVED_CONTRACT_CHANGED')
    for name, src in packed['code'].items():
        core.require((root / 'code' / name).read_bytes() == src.encode(), 'SAVED_CODE_CHANGED')
    for module in (core, live, scoring.base, scoring.readout, scoring, sys.modules[__name__]):
        p = Path(module.__file__)
        core.require(sha256(p.read_bytes()).hexdigest() == packed['contract']['source_hashes'][p.name], 'ACTIVE_CODE_CHANGED')
    allowed = {s['id'] for s in design['allocation']}
    if (root / 'responses').exists():
        core.require(all(p.is_dir() and not p.is_symlink() and p.name in allowed for p in (root / 'responses').iterdir()), 'UNEXPECTED_ID')
    return design, requests


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


def score_response(response, case, slot, design, memory):
    if slot['stage'] == 'UPDATE':
        return scoring.score_update(response['answer_text'], case, slot['condition'],
                                    design['schemas'][slot['condition']], response['finish_reason'])
    return scoring.score_read(response['answer_text'], memory, case, design['read_schema'], response['finish_reason'])


def derived_memory(response, payload, method, schema):
    """Build transport artifact from actual raw response and visible catalog; no gold."""
    raw = response['answer_text'].encode()
    if response['finish_reason'] != 'EOS' or len(raw) > 16384:
        return None, []
    try:
        value = scoring.parse(raw)
    except (ValueError, UnicodeError, RecursionError):
        return None, []
    memory, trace, errors = scoring.materialize(value, payload, method, schema)
    return memory, trace


def derived_decision(response):
    """Compute from actual extracted values; neither saved note nor gold is consulted."""
    raw = response['answer_text'].encode(); coverage = None
    if response['finish_reason'] == 'EOS' and len(raw) <= 4096:
        try:
            obj = scoring.parse(raw)
            coverage = obj.get('coverage') if type(obj) is dict else None
        except (ValueError, UnicodeError, RecursionError):
            pass
    return {'kind': 'DETERMINISTIC_FROM_EXTRACTED_VALUES',
            'answer_sha256': sha256(raw).hexdigest(), 'finish_reason': response['finish_reason'],
            'extracted_values': coverage, 'four_valid': scoring.four_values_valid(coverage),
            'channel': scoring.compute_channel(coverage), 'additional_model_requests': 0}


def match_artifact(path, value, create):
    if create and not path.exists():
        live.write_json(path, value)
    core.require(live.read_json(path) == value, 'ARTIFACT_REPLAY_MISMATCH:' + path.name)


def check_artifacts(folder, response, score, case, slot, design, create=False):
    if slot['stage'] == 'UPDATE':
        memory, trace = derived_memory(response, case['update_payload'], slot['condition'], design['schemas'][slot['condition']])
        core.require(memory == score['memory'] and trace == score['choice_trace'], 'MEMORY_SCORE_MISMATCH')
        if memory is None:
            core.require(not (folder / 'saved-memory.json').exists() and not (folder / 'selection-trace.json').exists(), 'REJECTED_MEMORY_SAVED')
        else:
            match_artifact(folder / 'saved-memory.json', memory, create)
            match_artifact(folder / 'selection-trace.json', {'method': slot['condition'],
                'answer_sha256': sha256(response['answer_text'].encode()).hexdigest(), 'rows': trace}, create)
    else:
        expected = derived_decision(response)
        core.require(expected['channel'] == score['channel_output'], 'DERIVED_SCORE_MISMATCH')
        core.require(score['four_exact'] is not True or score['channel_note'] is True, 'EXACT_EXTRACTION_WRONG_CHANNEL')
        match_artifact(folder / 'derived-decision.json', expected, create)


def status_for(response, score):
    return 'FORMAT_REJECT' if response['finish_reason'] == 'EOS' and not score['format_valid'] else response['finish_reason']


def complete_response(store, design, case, slot, memory):
    folder = store.directory(slot)
    response = read_response(folder, slot)
    score = score_response(response, case, slot, design, memory)
    for name, raw in [('answer.txt', response['answer_text'].encode()),
                      ('decoded-with-special-tokens.txt', response['decoded_with_special_tokens'].encode())]:
        if (folder / name).exists():
            core.require((folder / name).read_bytes() == raw, 'ANSWER_CHANGED')
        else:
            live.write_new(folder / name, raw)
    check_artifacts(folder, response, score, case, slot, design, create=True)
    return store.finish(slot, status_for(response, score), score, 'COMPONENT_SCORING')


def read_context(root, rows, slot):
    parent_id = slot['dependencies'][0]
    if parent_id not in rows:
        return None, None
    parent = rows[parent_id]; folder = Path(root) / 'responses' / parent_id
    binding = {'id': parent_id, 'status': parent['status'], 'gate': parent['score']['gate'],
        'result_sha256': sha256((folder / 'result.json').read_bytes()).hexdigest(), 'saved_memory_sha256': None}
    if parent['score']['gate'] != 'PASS':
        return None, binding
    # Parent response/artifacts were already replayed in allocation order.
    memory = live.read_json(folder / 'saved-memory.json')
    binding['saved_memory_sha256'] = sha256((folder / 'saved-memory.json').read_bytes()).hexdigest()
    return memory, binding


def run_routes(root, packed, backend=None, deadline=float('inf'), close_pending=False, checkpoint=None):
    design, requests = verify_root(root, packed)
    cases = {c['id']: c for c in design['cases']}; requests = {q['id']: q for q in requests}
    store = live.EvidenceStore(root, packed['contract']); rows = {}
    for slot in design['allocation']:
        folder = store.directory(slot); case = cases[slot['case']]
        memory = None; binding = None
        if slot['stage'] == 'UPDATE':
            request = requests[slot['id']]
            unknown = scoring.score_update(None, case, slot['condition'], design['schemas'][slot['condition']])
        else:
            memory, binding = read_context(root, rows, slot)
            if binding is None:
                core.require(not folder.exists(), 'READ_WITHOUT_CLOSED_PARENT')
                continue  # Only possible in a still-open partial run; final audit closes parents first.
            request = scoring.read_request(design, slot, case, memory) if memory is not None else None
            unknown = scoring.score_read(None, memory, case, design['read_schema'])
        if (folder / 'input.json').exists():
            saved = live.read_json(folder / 'input.json')
            core.require(request is not None and all(saved[k] == request[k] for k in request), 'INPUT_CHANGED')
            core.require(saved.get('parent') == binding, 'INPUT_PARENT_CHANGED')
        if (folder / 'started.json').exists():
            marker = live.read_json(folder / 'started.json')
            core.require(marker['input_sha256'] == sha256((folder / 'input.json').read_bytes()).hexdigest(), 'START_INPUT_HASH')
        if store.completed(slot):
            result = store.load(slot)
            if (folder / 'response.json').exists():
                core.require(request is not None and (folder / 'started.json').exists(), 'RESPONSE_WITHOUT_VALID_START')
                response = read_response(folder, slot)
                score = score_response(response, case, slot, design, memory)
                core.require(score == result['score'], 'SCORE_REPLAY_MISMATCH')
                check_artifacts(folder, response, score, case, slot, design)
                core.require((folder / 'answer.txt').read_bytes() == response['answer_text'].encode(), 'ANSWER_MISMATCH')
                core.require((folder / 'decoded-with-special-tokens.txt').read_bytes() == response['decoded_with_special_tokens'].encode(), 'DECODED_MISMATCH')
                core.require(result['status'] == status_for(response, score), 'STATUS_MISMATCH')
            else:
                allowed = ('DEPENDENCY_MISSING',) if request is None else ('NOT_RUN', 'INTERRUPTED_UNCERTAIN', 'GENERATION_ERROR', 'INPUT_TOO_LONG')
                core.require(result['score'] == unknown and result['status'] in allowed, 'UNANSWERED_SCORE')
                core.require(not (folder / 'saved-memory.json').exists() and not (folder / 'derived-decision.json').exists(), 'UNANSWERED_ARTIFACT')
                if request is None:
                    core.require(not (folder / 'input.json').exists() and not (folder / 'started.json').exists(), 'BLOCKED_READ_STARTED')
                    match_artifact(folder / 'dependency.json', binding, False)
        elif request is None:
            core.require(not (folder / 'started.json').exists() and not (folder / 'input.json').exists(), 'BLOCKED_READ_STARTED')
            match_artifact(folder / 'dependency.json', binding, True)
            result = store.finish(slot, 'DEPENDENCY_MISSING', unknown)
        elif (folder / 'started.json').exists():
            result = (complete_response(store, design, case, slot, memory) if (folder / 'response.json').exists()
                      else store.finish(slot, 'INTERRUPTED_UNCERTAIN', unknown))
        elif backend is None or live.STOP_REQUESTED or time.monotonic() >= deadline:
            if not close_pending:
                continue
            result = store.finish(slot, 'NOT_RUN', unknown)
        else:
            core.require(not folder.exists() or not any(folder.iterdir()), 'PARTIAL_PREPARATION')
            prepared = backend.prepare(request['messages'])
            live.write_json(folder / 'input.json', dict(request, parent=binding, prepared=prepared))
            if len(prepared['input_ids']) > live.MAX_INPUT_TOKENS:
                result = store.finish(slot, 'INPUT_TOO_LONG', unknown)
            elif time.monotonic() >= deadline or live.STOP_REQUESTED:
                result = store.finish(slot, 'NOT_RUN', unknown)
            else:
                live.write_json(folder / 'started.json', {'started_at': live.now(), 'seed': slot['seed'],
                    'input_sha256': sha256((folder / 'input.json').read_bytes()).hexdigest()})
                try:
                    response = backend.generate(prepared, slot['seed'], deadline)
                    response['payload_sha256'] = live.digest(response)
                    live.write_json(folder / 'response.json', response)
                except BaseException as error:
                    live.write_json(folder / 'generation-error.json', {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()})
                    store.finish(slot, 'GENERATION_ERROR', unknown)
                    raise
                result = complete_response(store, design, case, slot, memory)
        rows[slot['id']] = result
        if backend is not None:
            print(f"{len(rows)}/144 {slot['id']} {result['status']}", flush=True)
            if checkpoint and len(rows) % 24 == 0:
                checkpoint(len(rows))
    return rows


def make_report(root, packed, rows):
    design, requests = verify_root(root, packed)
    core.require(set(rows) == {s['id'] for s in design['allocation']}, 'REPORT_INCOMPLETE_IDS')
    cases = {c['id']: c for c in design['cases']}
    outcomes = {p['id']: {'update': rows[p['id'] + '-UPDATE']['score'], 'read': rows[p['id'] + '-READ']['score']}
                for p in design['pipelines']}
    report = scoring.summarize(design, outcomes)
    report.update(protocol=PROTOCOL, status_counts=dict(Counter(r['status'] for r in rows.values())), closed_responses=len(rows))
    report['attempted_generations'] = len(list((Path(root) / 'responses').glob('*/started.json')))
    core.require(report['attempted_generations'] <= 144, 'GENERATION_BUDGET')
    detail = []
    for p in design['pipelines']:
        c = cases[p['case']]; item = outcomes[p['id']]
        detail.append(dict(p, role=c['role'], notice_relation=c['notice_relation'], notice_target=c['notice_target'],
            notice_catalog_position=c['notice_catalog_position'], latest_channel=c['latest_channel'],
            source={k: v for k, v in c.items() if k.startswith('source_')}, original_note_state=c['original_note_state'],
            original_payload_sha256=c['original_payload_sha256'], update_payload_sha256=c['update_payload_sha256'],
            update=item['update'], read=item['read'], end_to_end_exact=scoring.end_to_end(item['update'], item['read']),
            status={stage: rows[p['id'] + '-' + stage]['status'] for stage in ('UPDATE', 'READ')}))
    report['by_pipeline'] = detail
    report['by_response'] = [dict(s, status=rows[s['id']]['status'], score=rows[s['id']]['score']) for s in design['allocation']]
    report['components'] = {}; report['strata'] = {}; performance = {}
    update_keys = ('parse_valid', 'format_valid', 'private_customer_exact', 'private_observation_exact',
                   'shared_values_exact', 'shared_provenance_exact', 'shared_latest_exact', 'joint_state_exact')
    read_keys = ('format_valid', 'four_valid', 'four_exact', 'channel_note', 'channel_latest')
    for method in scoring.METHODS:
        records = [r for r in detail if r['condition'] == method]
        components = {}
        for subset in ('REPAIR', 'GUARD'):
            selected = [r for r in records if r['set'] == subset]
            accepted = [r for r in selected if r['update']['gate'] == 'PASS']
            components[subset] = {
                'update': {k: scoring.counts(r['update'].get(k) for r in selected) for k in update_keys},
                'read_planned_denominator': {k: scoring.counts(r['read'].get(k) for r in selected) for k in read_keys},
                'read_accepted_memory_only_descriptive': {k: scoring.counts(r['read'].get(k) for r in accepted) for k in read_keys},
                'read_input_count': len(accepted),
                'shared_rows': {role: scoring.counts(r['update']['shared_rows_exact'][role] for r in selected) for role in ('A', 'B')},
                'shared_row_matches_input': {role: scoring.counts(r['update']['shared_row_matches_input'][role] for r in selected) for role in ('A', 'B')},
                'end_to_end_exact': scoring.counts(r['end_to_end_exact'] for r in selected)}
        report['components'][method] = components
        # Stratify within each set: do not pool repair and guard as a superiority test.
        report['strata'][method] = {}
        for subset in ('REPAIR', 'GUARD'):
            selected = [r for r in records if r['set'] == subset]
            report['strata'][method][subset] = {}
            for dimension in ('role', 'notice_relation', 'notice_catalog_position', 'replicate', 'case', 'source_condition'):
                def get(r): return r['source']['source_condition'] if dimension == 'source_condition' else r[dimension]
                report['strata'][method][subset][dimension] = {str(v): {
                    'pipeline_ids': [r['id'] for r in selected if get(r) == v],
                    'joint_state_exact': scoring.counts(r['update']['joint_state_exact'] for r in selected if get(r) == v),
                    'end_to_end_exact': scoring.counts(r['end_to_end_exact'] for r in selected if get(r) == v)}
                    for v in sorted({get(r) for r in selected})}
        performance[method] = {}
        for stage in ('UPDATE', 'READ'):
            values = []; inputs = []
            for slot in design['allocation']:
                folder = Path(root) / 'responses' / slot['id']
                if slot['condition'] == method and slot['stage'] == stage and (folder / 'response.json').exists():
                    values.append(live.read_json(folder / 'response.json'))
                    inputs.append(len(live.read_json(folder / 'input.json')['prepared']['input_ids']))
            performance[method][stage] = {'responses': len(values), 'input_tokens': inputs,
                'output_tokens': [len(v['output_token_ids']) for v in values],
                'output_utf8_bytes': [len(v['answer_text'].encode()) for v in values],
                'generation_seconds': [v['generation_seconds'] for v in values]}
    report['performance'] = performance
    return report

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


def aggregate_archive(path, packed):
    manifest, files = read_archive(path)
    with tempfile.TemporaryDirectory(prefix='ur01-audit-') as temp:
        root = Path(temp)
        for name, raw in files.items():
            p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        verify_root(root, packed)  # Archived code is compared, never imported or executed.
        rows = run_routes(root, packed, close_pending=True)
        report = make_report(root, packed, rows)
        for p in root.glob('report-*.json'):
            old = live.read_json(p)
            if len(rows) == old.get('closed_responses'):
                core.require(core.encoded(old) == core.encoded(report), 'ARCHIVED_REPORT_MISMATCH')
        return {'archive_sha256': sha256(Path(path).read_bytes()).hexdigest(), 'manifest_files': len(files),
                'kind': manifest['kind'], 'report': report}


def worker(root, seconds, audit_only=False):
    root = Path(root)
    packed = live.read_json(root / 'payload.json')
    def stop(signum, frame): live.STOP_REQUESTED = True
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    deadline = time.monotonic() + seconds
    try:
        if not audit_only:
            core.require(platform.system() == 'Linux' and Path('/content').is_dir(), 'COLAB_ONLY_NO_MODEL_LOAD')
            verify_root(root, packed)
            core.require(live.read_json(root / 'preflight.json') == preflight(packed), 'PREFLIGHT_CHANGED')
            core.require(not list((root / 'responses').glob('*/started.json')), 'NO_GENERATION_RESTART')
            backend = live.HuggingFaceBackend(root, deadline)
            def checkpoint(n):
                export_zip(root, root.parent / f'npp-ur01-checkpoint-{root.name}-{n:03d}.zip', 'CHECKPOINT')
            run_routes(root, packed, backend, deadline, checkpoint=checkpoint)
    finally:
        rows = run_routes(root, packed, close_pending=True)
        report = make_report(root, packed, rows)
        live.write_json(root / ('report-' + uuid.uuid4().hex + '.json'), report)
        print(json.dumps({'closed': report['closed_responses'], 'generations': report['attempted_generations'], 'status': report['status_counts']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    worker(sys.argv[1], float(sys.argv[2]), len(sys.argv) > 3 and sys.argv[3] == 'AUDIT_ONLY')
