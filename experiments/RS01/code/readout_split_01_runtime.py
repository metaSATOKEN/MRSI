"""READOUT-SPLIT-01 execution/evidence. Import is standard-library-only."""
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
import readout_split_01_scoring as scoring

PROTOCOL = 'READOUT-SPLIT-01-RUN-v0.1'
DESIGN_SHA = '1ec12f121c464b19c6df258d9069480bedb94c1013a90a4000ca1e74c56e06df'
REQUESTS_SHA = 'd01b038ea3503cbf984c94f860bad1c22bb32a631b595a82d7e0a4dc3e63960c'


def validate_payload(packed):
    core.require(sha256(packed['design_text'].encode()).hexdigest() == DESIGN_SHA, 'DESIGN_CHANGED')
    core.require(sha256(packed['requests_text'].encode()).hexdigest() == REQUESTS_SHA, 'REQUESTS_CHANGED')
    design, requests = json.loads(packed['design_text']), json.loads(packed['requests_text'])
    core.require(len(design['allocation']) == len(requests) == 96, 'SCOPE')
    core.require([s['id'] for s in design['allocation']] == [q['id'] for q in requests], 'REQUEST_ORDER')
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
            'max_generations': 96, 'seconds_including_setup': 5400, 'automatic_regenerations': 0,
            'resume_generation': False, 'checkpoint_every': 24, 'cloud_drive': 'not_used',
            'retention': 'private_no_deletion_deadline', 'delivery': 'zip_download',
            'eos_policy': 'Remove one final im_end only, retaining raw token IDs; no text repair.'}


def initialize(root, packed):
    validate_payload(packed)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for name, raw in [('design.json', packed['design_text'].encode()),
                      ('requests.json', packed['requests_text'].encode())]:
        live.write_new(root / name, raw)
    live.write_json(root / 'contract.json', packed['contract'])
    for name, src in packed['code'].items():
        live.write_new(root / 'code' / name, src.encode())


def preflight(packed):
    """Synthetic transport/scoring check only; never writes research responses."""
    design, requests = validate_payload(packed)
    cases = {c['id']: c for c in design['cases']}
    for slot, request in zip(design['allocation'], requests):
        case = cases[slot['case']]
        payload = case['rule_payload'] if slot['condition'] == 'RULE' else case['notes_payload']
        core.require(scoring.compute_channel(case['gold']['four_values']) == case['gold']['channel'], 'GOLD_RULE')
        core.require(request['messages'][1]['content'] == '\n資料JSON:\n' + scoring.enc(payload).decode(), 'MESSAGE_PAYLOAD')
        core.require(request['messages'][0]['content'] == design['prompts'][slot['condition']], 'MESSAGE_PROMPT')
        value = scoring.score(scoring.enc(scoring.ideal(case, slot['condition'])), case, slot['condition'], design['schemas'][slot['condition']])
        core.require(value['channel'] and value['format_valid'], 'SYNTHETIC_SCORE')
    return {'kind': 'SYNTHETIC_PREFLIGHT_NOT_MODEL_RESULTS', 'fixture_responses': 96, 'model_generations': 0, 'status': 'PASS'}


def verify_root(root, packed):
    design, requests = validate_payload(packed)
    root = Path(root)
    core.require((root / 'design.json').read_bytes() == packed['design_text'].encode(), 'SAVED_DESIGN_CHANGED')
    core.require((root / 'requests.json').read_bytes() == packed['requests_text'].encode(), 'SAVED_REQUESTS_CHANGED')
    core.require(live.read_json(root / 'contract.json') == packed['contract'], 'SAVED_CONTRACT_CHANGED')
    for name, src in packed['code'].items():
        core.require((root / 'code' / name).read_bytes() == src.encode(), 'SAVED_CODE_CHANGED')
    for module in (core, live, scoring, sys.modules[__name__]):
        p = Path(module.__file__)
        core.require(sha256(p.read_bytes()).hexdigest() == packed['contract']['source_hashes'][p.name], 'ACTIVE_CODE_CHANGED')
    allowed = {s['id'] for s in design['allocation']}
    if (root / 'responses').exists():
        core.require(all(p.is_dir() and p.name in allowed for p in (root / 'responses').iterdir()), 'UNEXPECTED_ID')
    return design, requests


def response_score(folder, case, slot, design):
    response = live.read_json(folder / 'response.json')
    core.require(response['payload_sha256'] == live.digest({k: v for k, v in response.items() if k != 'payload_sha256'}), 'RESPONSE_HASH')
    core.require(response['seed'] == slot['seed'], 'RESPONSE_SEED')
    core.require(response['finish_reason'] in ('EOS', 'LENGTH', 'TIME_LIMIT'), 'FINISH_REASON')
    ids = response['output_token_ids']
    core.require(type(ids) is list and all(type(x) is int for x in ids) and len(ids) <= 2048, 'OUTPUT_TOKENS')
    eos = bool(ids and ids[-1] == live.SPECIAL_TOKEN_IDS['<|im_end|>'])
    core.require((response['finish_reason'] == 'EOS') == eos, 'EOS_INCONSISTENT')
    return scoring.score(response['answer_text'], case, slot['condition'],
                         design['schemas'][slot['condition']], response['finish_reason'])


def derived_decision(response):
    """Derive from raw EXTRACT response only. No original note or gold is available here."""
    raw = response['answer_text'].encode()
    coverage = None
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


def check_derived(folder, response, score, create=False):
    expected = derived_decision(response)
    core.require(expected['channel'] == score['channel_output'], 'DERIVED_SCORE_MISMATCH')
    core.require(score['four_exact'] is not True or score['channel'] is True, 'EXACT_EXTRACTION_WRONG_CHANNEL')
    path = folder / 'derived-decision.json'
    if create and not path.exists():
        live.write_json(path, expected)
    core.require(live.read_json(path) == expected, 'DERIVED_REPLAY_MISMATCH')


def complete_response(store, design, case, slot):
    folder = store.directory(slot)
    value = live.read_json(folder / 'response.json')
    score = response_score(folder, case, slot, design)
    for name, raw in [('answer.txt', value['answer_text'].encode()),
                      ('decoded-with-special-tokens.txt', value['decoded_with_special_tokens'].encode())]:
        if (folder / name).exists():
            core.require((folder / name).read_bytes() == raw, 'ANSWER_CHANGED')
        else:
            live.write_new(folder / name, raw)
    if slot['condition'] == 'EXTRACT':
        check_derived(folder, value, score, create=True)
    status = value['finish_reason']
    if status == 'EOS' and not score['format_valid']:
        status = 'FORMAT_REJECT'
    return store.finish(slot, status, score, 'COMPONENT_SCORING')


def run_routes(root, packed, backend=None, deadline=float('inf'), close_pending=False, checkpoint=None):
    design, requests = verify_root(root, packed)
    cases = {c['id']: c for c in design['cases']}
    store = live.EvidenceStore(root, packed['contract'])
    rows = {}
    for slot, request in zip(design['allocation'], requests):
        folder = store.directory(slot); case = cases[slot['case']]
        unknown = scoring.score(None, case, slot['condition'], design['schemas'][slot['condition']])
        if (folder / 'input.json').exists():
            saved = live.read_json(folder / 'input.json')
            core.require(all(saved[k] == request[k] for k in request), 'INPUT_CHANGED')
        if (folder / 'started.json').exists():
            marker = live.read_json(folder / 'started.json')
            core.require(marker['input_sha256'] == sha256((folder / 'input.json').read_bytes()).hexdigest(), 'START_INPUT_HASH')
        if store.completed(slot):
            result = store.load(slot)
            if (folder / 'response.json').exists():
                core.require((folder / 'started.json').exists(), 'RESPONSE_WITHOUT_START')
                score = response_score(folder, case, slot, design)
                value = live.read_json(folder / 'response.json')
                core.require(score == result['score'], 'SCORE_REPLAY_MISMATCH')
                if slot['condition'] == 'EXTRACT':
                    check_derived(folder, value, score)
                core.require((folder / 'answer.txt').read_bytes() == value['answer_text'].encode(), 'ANSWER_MISMATCH')
                expected_status = 'FORMAT_REJECT' if value['finish_reason'] == 'EOS' and not score['format_valid'] else value['finish_reason']
                core.require(result['status'] == expected_status, 'STATUS_MISMATCH')
            else:
                core.require(result['score'] == unknown and result['status'] in ('NOT_RUN', 'INTERRUPTED_UNCERTAIN', 'GENERATION_ERROR', 'INPUT_TOO_LONG'), 'UNANSWERED_SCORE')
        elif (folder / 'started.json').exists():
            result = (complete_response(store, design, case, slot) if (folder / 'response.json').exists()
                      else store.finish(slot, 'INTERRUPTED_UNCERTAIN', unknown))
        elif backend is None or live.STOP_REQUESTED or time.monotonic() >= deadline:
            if not close_pending:
                continue
            result = store.finish(slot, 'NOT_RUN', unknown)
        else:
            core.require(not folder.exists() or not any(folder.iterdir()), 'PARTIAL_PREPARATION')
            prepared = backend.prepare(request['messages'])
            live.write_json(folder / 'input.json', dict(request, prepared=prepared))
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
                result = complete_response(store, design, case, slot)
        rows[slot['id']] = result
        if backend is not None:
            print(f"{len(rows)}/96 {slot['id']} {result['status']} channel={result['score']['channel']}", flush=True)
            if checkpoint and len(rows) % 24 == 0:
                checkpoint(len(rows))
    return rows


def make_report(root, packed, rows):
    design, requests = verify_root(root, packed)
    cases = {c['id']: c for c in design['cases']}
    scores = {sid: r['score'] for sid, r in rows.items()}
    report = scoring.summarize(design, scores)
    report.update(protocol=PROTOCOL, status_counts=dict(Counter(r['status'] for r in rows.values())), closed_responses=len(rows))
    report['attempted_generations'] = len(list((Path(root) / 'responses').glob('*/started.json')))
    core.require(report['attempted_generations'] <= 96, 'GENERATION_BUDGET')
    report['components'] = {}; detail = []
    for slot in design['allocation']:
        c = cases[slot['case']]; s = scores.get(slot['id'], {})
        detail.append(dict(slot, role=c['role'], gold=c['gold'], score=s, status=rows.get(slot['id'], {}).get('status', 'NOT_RUN')))
    report['by_response'] = detail
    for method in scoring.METHODS:
        records = [r for r in detail if r['condition'] == method]
        main = [r for r in records if r['set'] == 'MAIN']
        report['components'][method] = {
            'all_format': scoring.counts(r['score'].get('format_valid') for r in records),
            'all_parse': scoring.counts(r['score'].get('parse_valid') for r in records),
            'main_confusion': dict(Counter(r['gold']['channel'] + '->' + str(r['score'].get('channel_output')) for r in main)),
            'main_by_role': {role: scoring.counts(r['score'].get('channel') for r in main if r['role'] == role) for role in ('A', 'B')},
            'main_repeats_by_case': {c['id']: [r['score'].get('channel_output') for r in main if r['case'] == c['id']] for c in design['cases'] if c['set'] == 'MAIN'}}
        if method == 'EXTRACT':
            report['components'][method]['four_valid'] = scoring.counts(r['score'].get('four_valid') for r in records)
            report['components'][method]['main_fields'] = {f: scoring.counts((r['score'].get('fields') or {}).get(f) for r in main) for f in scoring.FIELDS}
    report['rule_input_patterns'] = {p: {'case_ids': [c['id'] for c in design['cases'] if c['pattern'] == p],
        'four_values': next(c['rule_payload']['coverage'] for c in design['cases'] if c['pattern'] == p)}
        for p in sorted({c['pattern'] for c in design['cases']})}
    performance = {}
    for method in scoring.METHODS:
        values = []; inputs = []
        for slot in design['allocation']:
            folder = Path(root) / 'responses' / slot['id']
            if slot['condition'] == method and (folder / 'response.json').exists():
                values.append(live.read_json(folder / 'response.json'))
                inputs.append(len(live.read_json(folder / 'input.json')['prepared']['input_ids']))
        performance[method] = {'responses': len(values), 'input_tokens': inputs,
            'output_tokens': [len(v['output_token_ids']) for v in values],
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
    with tempfile.TemporaryDirectory(prefix='rs01-audit-') as temp:
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
                export_zip(root, root.parent / f'npp-rs01-checkpoint-{root.name}-{n:03d}.zip', 'CHECKPOINT')
            run_routes(root, packed, backend, deadline, checkpoint=checkpoint)
    finally:
        rows = run_routes(root, packed, close_pending=True)
        report = make_report(root, packed, rows)
        live.write_json(root / ('report-' + uuid.uuid4().hex + '.json'), report)
        print(json.dumps({'closed': report['closed_responses'], 'generations': report['attempted_generations'], 'status': report['status_counts']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    worker(sys.argv[1], float(sys.argv[2]), len(sys.argv) > 3 and sys.argv[3] == 'AUDIT_ONLY')
