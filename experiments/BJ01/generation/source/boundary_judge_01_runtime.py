"""BJ01 immutable request/answer controller. Real inference is Colab-only."""
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
import boundary_judge_01_scoring as sc

PROTOCOL = 'BOUNDARY-JUDGE-01-RUN-v0.1'
CODE_NAMES = ('cross_model_e1_01_offline_runtime.py', 'cross_model_e1_01_generation_runtime.py',
              'boundary_judge_01_scoring.py', 'boundary_judge_01_runtime.py', 'boundary_judge_01_bootstrap.py')
MATERIAL_NAMES = ('judge-output-schema.json', 'design-summary.json', 'labels-and-provenance.json',
                  'packets.json', 'judge-requests.json', 'MANIFEST.json')


def contract_for(packed):
    return {'protocol': PROTOCOL, 'source_hashes': {n: sha256(s.encode()).hexdigest() for n, s in packed['code'].items()},
            'frozen_hashes': {n: sha256(s.encode()).hexdigest() for n, s in packed['frozen'].items()},
            'max_generations': 64, 'seconds_including_setup': 3600, 'reserved_final_seconds': 90,
            'max_input_tokens': 8192, 'max_output_tokens': 1024, 'max_raw_bytes': 16384,
            'model_id': live.MODEL_ID, 'model_revision': live.MODEL_REVISION, 'package_pins': live.PINS,
            'generation': dict(live.GENERATION, max_new_tokens=1024), 'dtype': 'bfloat16', 'attention': 'sdpa',
            'enable_thinking': False, 'batch_size': 1, 'grammar_constraint': False,
            'automatic_regenerations': 0, 'resume_generation': False, 'checkpoint_every': 8,
            'cloud_drive': 'not_used', 'retention': 'private_no_deletion_deadline', 'delivery': 'zip_download',
            'answer_repairs': False, 'judge_mode': 'observe', 'normalization': 'strict bare JSON only',
            'eos_policy': 'Remove one final im_end only; preserve output token IDs and full decoded text.'}


def safe_name(name):
    p = PurePosixPath(name)
    core.require(not p.is_absolute() and '..' not in p.parts and p.as_posix() == name and '\\' not in name and ':' not in name, 'UNSAFE_PATH')


def validate_payload(packed):
    core.require(set(packed) == {'code', 'frozen', 'contract'}, 'PAYLOAD_KEYS')
    core.require(set(packed['code']) == set(CODE_NAMES) and set(packed['frozen']) == set(MATERIAL_NAMES), 'PAYLOAD_FILE_SET')
    core.require(packed['contract'] == contract_for(packed), 'CONTRACT_CHANGED')
    frozen = packed['frozen']; manifest = sc.strict_loads(frozen['MANIFEST.json'].encode())
    core.require(set(manifest) == set(MATERIAL_NAMES) - {'MANIFEST.json'}, 'MATERIAL_FILE_SET')
    for name, expected in manifest.items():
        core.require(sha256(frozen[name].encode()).hexdigest() == expected, 'FROZEN_HASH:' + name)
    data = {name: sc.strict_loads(value.encode()) for name, value in frozen.items()}
    packets, requests, labels = (data[n] for n in ('packets.json', 'judge-requests.json', 'labels-and-provenance.json'))
    ids = [p['judgment_id'] for p in packets]
    core.require(len(ids) == len(set(ids)) == 64 and ids == [r['id'] for r in requests] == [r['judgment_id'] for r in labels], 'ID_ORDER')
    for request, packet, label in zip(requests, packets, labels):
        core.require(set(request) == {'id', 'seed', 'messages'} and type(request['seed']) is int, 'REQUEST_KEYS')
        core.require(set(packet) == {'judgment_id', 'stage', 'payload', 'answer', 'contract', 'facts'}, 'PACKET_KEYS')
        safe_name(request['id'])
        core.require(set(label['expected']) == set(sc.AXES) and set(label['expected'].values()) <= {'OK', 'VIOLATION'}, 'REFERENCE_LABEL')
        core.require(label['all_axes_ok'] == all(v == 'OK' for v in label['expected'].values()), 'REFERENCE_CLEAN')
    core.require(data['design-summary.json']['model_calls'] == 0, 'DESIGN_NOT_RESULT')
    return data


def initialize(root, packed):
    validate_payload(packed)
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    live.write_json(root / 'contract.json', packed['contract'])
    for directory in ('code', 'frozen'):
        for name, source in packed[directory].items():
            live.write_new(root / directory / name, source.encode())


def verify_root(root, packed):
    data = validate_payload(packed); root = Path(root)
    core.require(not root.is_symlink(), 'ROOT_SYMLINK')
    core.require(live.read_json(root / 'contract.json') == packed['contract'], 'SAVED_CONTRACT')
    if (root / 'payload.json').exists():
        core.require(live.read_json(root / 'payload.json') == packed, 'SAVED_PAYLOAD')
    for directory in ('code', 'frozen'):
        for name, source in packed[directory].items():
            core.require((root / directory / name).read_bytes() == source.encode(), 'SAVED_SOURCE:' + name)
    for module in (core, live, sc, sys.modules[__name__]):
        p = Path(module.__file__)
        core.require(sha256(p.read_bytes()).hexdigest() == packed['contract']['source_hashes'][p.name], 'ACTIVE_CODE_CHANGED')
    allowed = {r['id'] for r in data['judge-requests.json']}
    if (root / 'responses').exists():
        core.require(all(p.is_dir() and not p.is_symlink() and p.name in allowed for p in (root / 'responses').iterdir()), 'UNEXPECTED_RESPONSE_ID')
        core.require(all(not p.is_symlink() and (p.is_file() or p.name in allowed) for p in (root / 'responses').rglob('*')), 'RESPONSE_FILE_TYPE')
    return data


def match_bytes(path, raw, create):
    if create and not path.exists():
        live.write_new(path, raw)
    core.require(path.read_bytes() == raw, 'ARTIFACT_MISMATCH:' + path.name)


def read_response(folder, request):
    response = live.read_json(folder / 'response.json')
    core.require(response['payload_sha256'] == live.digest({k: v for k, v in response.items() if k != 'payload_sha256'}), 'RESPONSE_HASH')
    core.require(response['seed'] == request['seed'], 'RESPONSE_SEED')
    ids = response['output_token_ids']
    core.require(type(ids) is list and all(type(n) is int for n in ids) and len(ids) <= 1024, 'OUTPUT_TOKEN_LIMIT')
    eos = bool(ids and ids[-1] == live.SPECIAL_TOKEN_IDS['<|im_end|>'])
    core.require(response['finish_reason'] in ('EOS', 'LENGTH', 'TIME_LIMIT'), 'FINISH_REASON')
    core.require((response['finish_reason'] == 'EOS') == eos, 'EOS_MISMATCH')
    core.require(type(response['answer_text']) is str and type(response['decoded_with_special_tokens']) is str, 'TEXT_TYPE')
    return response


def evaluate(folder, request, packet, label, schema, create):
    response = read_response(folder, request)
    raw = response['answer_text'].encode()
    result = sc.score(raw, response['finish_reason'], packet, label['expected'], schema)
    match_bytes(folder / 'answer.txt', raw, create)
    match_bytes(folder / 'decoded-with-special-tokens.txt', response['decoded_with_special_tokens'].encode(), create)
    if result['format_valid']:
        match_bytes(folder / 'validated-judgment.json', core.encoded(result['answer']), create)
    else:
        core.require(not (folder / 'validated-judgment.json').exists(), 'INVALID_HAS_JUDGMENT')
    status = response['finish_reason'] if response['finish_reason'] != 'EOS' else 'EOS' if result['format_valid'] else 'FORMAT_REJECT'
    return status, result


def physical(store, request, packet, label, schema, backend, deadline, close_pending):
    folder = store.directory(request)
    inp = folder / 'input.json'; start = folder / 'started.json'; response = folder / 'response.json'
    if inp.exists():
        saved = live.read_json(inp)
        core.require(set(saved) == {'request', 'prepared'} and saved['request'] == request, 'INPUT_CHANGED')
        core.require(type(saved['prepared']['input_ids']) is list and all(type(n) is int for n in saved['prepared']['input_ids']), 'INPUT_TOKEN_TYPE')
    if start.exists():
        mark = live.read_json(start)
        core.require(inp.exists() and mark['input_sha256'] == sha256(inp.read_bytes()).hexdigest() and mark['seed'] == request['seed'], 'START_BINDING')
    def finish():
        core.require(start.exists(), 'RESPONSE_WITHOUT_START')
        status, result = evaluate(folder, request, packet, label, schema, True)
        return store.finish(request, status, result, 'FIXED_FOUR_AXES')
    if store.completed(request):
        saved_result = store.load(request)
        if response.exists():
            core.require(start.exists(), 'RESPONSE_WITHOUT_START')
            status, result = evaluate(folder, request, packet, label, schema, False)
            core.require(saved_result['score'] == result and saved_result['status'] == status, 'SCORE_REPLAY_MISMATCH')
        else:
            status = saved_result['status']
            core.require(status in ('NOT_RUN', 'INPUT_TOO_LONG', 'PREPARATION_ERROR', 'GENERATION_ERROR', 'INTERRUPTED_UNCERTAIN'), 'UNANSWERED_STATUS')
            core.require(saved_result['score'] == sc.unknown(status), 'UNANSWERED_SCORE')
            core.require(not any((folder / n).exists() for n in ('answer.txt', 'decoded-with-special-tokens.txt', 'validated-judgment.json')), 'UNANSWERED_ARTIFACT')
        return saved_result
    if start.exists():
        return finish() if response.exists() else store.finish(request, 'INTERRUPTED_UNCERTAIN', sc.unknown('INTERRUPTED_UNCERTAIN'))
    core.require(not response.exists(), 'ORPHAN_RESPONSE')
    if inp.exists():
        return store.finish(request, 'NOT_RUN', sc.unknown('NOT_RUN'))
    if backend is None or live.STOP_REQUESTED or time.monotonic() >= deadline:
        return store.finish(request, 'NOT_RUN', sc.unknown('NOT_RUN')) if close_pending else None
    core.require(not folder.exists() or not any(folder.iterdir()), 'PARTIAL_PREPARATION')
    try:
        prepared = backend.prepare(request['messages'])
    except BaseException as error:
        live.write_json(folder / 'preparation-error.json', {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()})
        store.finish(request, 'PREPARATION_ERROR', sc.unknown('PREPARATION_ERROR'))
        raise
    live.write_json(inp, {'request': request, 'prepared': prepared})
    if len(prepared['input_ids']) > 8192:
        return store.finish(request, 'INPUT_TOO_LONG', sc.unknown('INPUT_TOO_LONG'))
    if live.STOP_REQUESTED or time.monotonic() >= deadline:
        return store.finish(request, 'NOT_RUN', sc.unknown('NOT_RUN'))
    core.require(len(list((store.root / 'responses').glob('*/started.json'))) < 64, 'GENERATION_BUDGET')
    live.write_json(start, {'started_at': live.now(), 'seed': request['seed'], 'input_sha256': sha256(inp.read_bytes()).hexdigest()})
    try:
        answer = backend.generate(prepared, request['seed'], deadline)
        answer['payload_sha256'] = live.digest(answer)
        live.write_json(response, answer)
    except BaseException as error:
        live.write_json(folder / 'generation-error.json', {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()})
        store.finish(request, 'GENERATION_ERROR', sc.unknown('GENERATION_ERROR'))
        raise
    return finish()


def run_routes(root, packed, backend=None, deadline=float('inf'), close_pending=False, checkpoint=None):
    data = verify_root(root, packed); root = Path(root)
    store = live.EvidenceStore(root, packed['contract']); results = {}
    for i, (request, packet, label) in enumerate(zip(data['judge-requests.json'], data['packets.json'], data['labels-and-provenance.json']), 1):
        result = physical(store, request, packet, label, data['judge-output-schema.json'], backend, deadline, close_pending)
        if result is not None:
            results[request['id']] = result
        if backend is not None:
            print(f'BJ01 {i}/64; stored {len(results)}; calls {len(list((root / "responses").glob("*/started.json")))}/64', flush=True)
            if checkpoint and i % 8 == 0:
                checkpoint(i)
    return results


def make_report(root, packed, rows):
    data = verify_root(root, packed); root = Path(root)
    report = sc.summarize(data['labels-and-provenance.json'], {sid: row['score'] for sid, row in rows.items()})
    report.update(protocol=PROTOCOL, attempted_generations=len(list((root / 'responses').glob('*/started.json'))),
                  status_counts=dict(Counter(row['status'] for row in rows.values())), by_id=rows)
    core.require(report['attempted_generations'] <= 64, 'GENERATION_BUDGET')
    responses = []; inputs = []
    for request in data['judge-requests.json']:
        folder = root / 'responses' / request['id']
        if (folder / 'response.json').exists():
            responses.append(read_response(folder, request))
            inputs.append(live.read_json(folder / 'input.json'))
    report['performance'] = {'responses': len(responses), 'input_tokens': [len(x['prepared']['input_ids']) for x in inputs],
                             'output_tokens': [len(x['output_token_ids']) for x in responses],
                             'raw_bytes': [len(x['answer_text'].encode()) for x in responses],
                             'generation_seconds': [x['generation_seconds'] for x in responses]}
    report['evidence_kind'] = ('SYNTHETIC_TEST_NOT_MODEL_RESULTS' if any(x.get('synthetic_fixture') for x in responses) else
                               'MODEL_RUN_EVIDENCE' if responses else 'NO_MODEL_RESPONSES')
    return report


def preflight(packed):
    data = validate_payload(packed)
    # Test validation and bounds without fabricating a model response.
    missing = {r['id']: sc.unknown('NOT_RUN') for r in data['judge-requests.json']}
    report = sc.summarize(data['labels-and-provenance.json'], missing)
    core.require(report['cases']['unknown'] == 64 and report['calibration']['status'] == 'INCONCLUSIVE', 'MISSING_PREFLIGHT')
    return {'kind': 'OFFLINE_PREFLIGHT_NOT_MODEL_RESULTS', 'cases': 64, 'model_calls': 0, 'status': 'PASS',
            'material_manifest_sha256': sha256(packed['frozen']['MANIFEST.json'].encode()).hexdigest()}


def export_zip(root, destination, kind='FINAL'):
    root, destination = Path(root), Path(destination)
    core.require(not destination.resolve().is_relative_to(root.resolve()), 'ZIP_INSIDE_EVIDENCE')
    files = {}
    for p in sorted(root.rglob('*')):
        core.require(not p.is_symlink(), 'EVIDENCE_SYMLINK')
        if p.is_file() and '__pycache__' not in p.parts and '.tmp-' not in p.name and p.name != 'RUNNING.lock':
            files[str(p.relative_to(root))] = p.read_bytes()
    manifest = {'protocol': PROTOCOL, 'kind': kind, 'resume_generation': False,
                'files_sha256': {name: sha256(raw).hexdigest() for name, raw in files.items()}}
    temporary = destination.with_name(destination.name + '.tmp-' + uuid.uuid4().hex)
    with zipfile.ZipFile(temporary, 'x', zipfile.ZIP_DEFLATED) as z:
        for name, raw in files.items():
            z.writestr(name, raw)
        z.writestr('FEEDBACK_MANIFEST.json', core.encoded(manifest))
    core.require(not destination.exists(), 'ZIP_EXISTS')
    temporary.rename(destination)
    return destination


def read_archive(path):
    with zipfile.ZipFile(path) as z:
        members = z.infolist(); names = [m.filename for m in members]
        core.require(len(names) == len(set(names)) and len(names) <= 2500 and sum(m.file_size for m in members) <= 100_000_000, 'ARCHIVE_LIMIT')
        for m in members:
            safe_name(m.filename)
            core.require(not m.is_dir() and not stat.S_ISLNK(m.external_attr >> 16), 'ARCHIVE_TYPE')
        files = {name: z.read(name) for name in names}
    manifest = sc.strict_loads(files.pop('FEEDBACK_MANIFEST.json'))
    core.require(manifest['protocol'] == PROTOCOL and set(files) == set(manifest['files_sha256']), 'ARCHIVE_MANIFEST')
    core.require(all(sha256(raw).hexdigest() == manifest['files_sha256'][name] for name, raw in files.items()), 'ARCHIVE_HASH')
    return manifest, files


def aggregate_archive(path, packed):
    manifest, files = read_archive(path)
    with tempfile.TemporaryDirectory(prefix='bj01-audit-') as temp:
        root = Path(temp)
        for name, raw in files.items():
            p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        rows = run_routes(root, packed, close_pending=True)
        report = make_report(root, packed, rows)
        for p in root.glob('report-*.json'):
            core.require(live.read_json(p) == report, 'ARCHIVED_REPORT_MISMATCH')
        return {'archive_sha256': sha256(Path(path).read_bytes()).hexdigest(), 'manifest_files': len(files), 'kind': manifest['kind'], 'report': report}


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
            core.require(live.GENERATION == packed['contract']['generation'], 'EFFECTIVE_GENERATION_CHANGED')
            backend = live.HuggingFaceBackend(root, deadline)
            run_routes(root, packed, backend, deadline,
                       checkpoint=lambda n: export_zip(root, root.parent / f'npp-bj01-checkpoint-{n:02d}.zip', 'CHECKPOINT'))
    finally:
        rows = run_routes(root, packed, close_pending=True)
        report = make_report(root, packed, rows)
        live.write_json(root / ('report-' + uuid.uuid4().hex + '.json'), report)
        print(json.dumps({'planned': 64, 'calls': report['attempted_generations'], 'cases': report['cases'],
                          'calibration': report['calibration']['status'], 'status': report['status_counts']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    worker(sys.argv[1], float(sys.argv[2]), len(sys.argv) > 3 and sys.argv[3] == 'AUDIT_ONLY')
