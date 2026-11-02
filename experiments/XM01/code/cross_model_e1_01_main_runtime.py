"""Two-part research runner and ZIP verifier. Imports only standard-library code.

Real generation is reachable only through the Colab worker. Synthetic fixtures are
used solely in tests and are never fallback answers for missing observations.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import signal
import stat
import sys
import tempfile
import time
import uuid
import zipfile

import cross_model_e1_01_offline_runtime as core
import cross_model_e1_01_generation_runtime as live

PROTOCOL = 'CROSS-MODEL-E1-01-MAIN-v0.1'
PARTITION_SHA256 = '8ed748b7c5f86f02edf0a1140124954e8ad104c90360894ba96a9add06a1afd2'
TOTAL_SECONDS = 8 * 3600
MAX_ZIP_BYTES = 1_000_000_000


def contract_for(bundle, partition, part, source_hashes):
    core.require(part in ('PART1', 'PART2'), 'PART_MUST_BE_1_OR_2')
    slots = partition['parts'][part]['allocation']
    return {'protocol': PROTOCOL, 'part': part, 'bundle_sha256': live.digest(bundle),
            'partition_sha256': sha256(core.encoded(partition) + b'\n').hexdigest(),
            'allocation_sha256': live.digest(slots), 'source_hashes': source_hashes,
            'model': live.MODEL_ID, 'revision': live.MODEL_REVISION,
            'special_token_ids': live.SPECIAL_TOKEN_IDS, 'pins': live.PINS,
            'generation': live.GENERATION, 'max_input_tokens': live.MAX_INPUT_TOKENS,
            'enable_thinking': False, 'dtype': 'bfloat16', 'attention': 'sdpa',
            'max_generations': 768, 'total_seconds': TOTAL_SECONDS, 'automatic_retries': 0,
            'checkpoint_every_closed_responses': 64, 'checkpoint_seconds': 1800,
            'storage': 'colab_ephemeral_no_drive', 'delivery': 'zip_download_at_part_end',
            'resume': 'latest_final_zip_only; unfinished_window_charged_in_full',
            'retention_proposal': 'private_no_deletion_deadline',
            'eos_policy': 'Remove one final im_end only; preserve raw token IDs.',
            'non_eos_policy': 'Unresolved; no downstream memory; no automatic regeneration.'}


def verify_scope(root, bundle, partition, contract):
    core.require(sha256(core.encoded(partition) + b'\n').hexdigest() == PARTITION_SHA256, 'PARTITION_CHANGED')
    core.require(contract == contract_for(bundle, partition, contract['part'], contract['source_hashes']), 'CONTRACT_CHANGED')
    for name, source in bundle['sources'].items():
        core.require(sha256(source.encode()).hexdigest() == bundle['source_hashes'][name], 'FROZEN_CODE_CHANGED')
    for name, prompt in bundle['prompts'].items():
        core.require(sha256(prompt.encode()).hexdigest() == bundle['prompt_hashes'][name], 'PROMPT_CHANGED')
    for name, expected in contract['source_hashes'].items():
        core.require(sha256((Path(root) / 'code' / name).read_bytes()).hexdigest() == expected, 'RUNNER_CODE_CHANGED:' + name)
    # Offline aggregation must also use the distributed execution/aggregation
    # modules, not silently substitute a later local revision.
    for module in (core, live, sys.modules[__name__]):
        path = Path(module.__file__)
        core.require(sha256(path.read_bytes()).hexdigest() == contract['source_hashes'][path.name],
                     'ACTIVE_CODE_CHANGED:' + path.name)
    full = core.repeated_slots(bundle['base_slots'])
    chosen = partition['parts'][contract['part']]
    slots = chosen['allocation']
    core.require(slots == [s for s in full if s['group'] in chosen['groups']], 'ALLOCATION_CHANGED')
    core.require(len(slots) == 768 and len(set(chosen['groups'])) == 32, 'PART_SIZE')
    core.validate_slots(slots)
    core.require(live.read_json(Path(root) / 'allocation.json') == slots, 'SAVED_ALLOCATION_CHANGED')
    allowed = {s['id'] for s in slots}
    response_root = Path(root) / 'responses'
    if response_root.exists():
        core.require(all(p.is_dir() and p.name in allowed for p in response_root.iterdir()), 'UNEXPECTED_RESPONSE_ID')
    return slots


def budget_used(root):
    total = 0.0
    for path in (Path(root) / 'windows').glob('*-start.json'):
        start = live.read_json(path)
        end = path.with_name(path.name.replace('-start.json', '-end.json'))
        seconds = live.read_json(end)['elapsed_seconds'] if end.exists() else start['reserved_seconds']
        core.require(isinstance(seconds, (float, int)) and math.isfinite(seconds) and seconds >= 0, 'INVALID_TIME_ACCOUNT')
        total += seconds
    return total


def archive_files(root):
    result = {}
    for path in sorted(Path(root).rglob('*')):
        core.require(not path.is_symlink(), 'SYMLINK_IN_EVIDENCE')
        if not path.is_file() or path.name == 'RUNNING.lock' or '__pycache__' in path.parts or '.tmp-' in path.name:
            continue
        result[str(path.relative_to(root))] = path.read_bytes()
    return result


def export_zip(root, destination, *, kind):
    core.require(kind in ('CHECKPOINT', 'FINAL'), 'ARCHIVE_KIND')
    root, destination = Path(root), Path(destination)
    core.require(not destination.resolve().is_relative_to(root.resolve()), 'ZIP_INSIDE_EVIDENCE')
    files = archive_files(root)
    contract = json.loads(files['contract.json']) if 'contract.json' in files else {}
    manifest = {'protocol': PROTOCOL, 'kind': kind, 'part': contract.get('part'),
                'files_sha256': {name: sha256(raw).hexdigest() for name, raw in files.items()},
                'automatic_resume_eligible': kind == 'FINAL' and 'contract.json' in files
                    and not any(not p.with_name(p.name.replace('-start.json', '-end.json')).exists()
                                for p in (root / 'windows').glob('*-start.json')),
                'note': 'CHECKPOINT is a snapshot, not proof that later generation did not occur.'}
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.tmp-' + uuid.uuid4().hex)
    with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, raw in files.items():
            archive.writestr(name, raw)
        archive.writestr('FEEDBACK_MANIFEST.json', core.encoded(manifest) + b'\n')
    core.require(not destination.exists(), 'ZIP_WOULD_OVERWRITE')
    os.rename(temporary, destination)
    return destination


def read_archive(path):
    """Validate every member before writing anything; never execute archived code."""
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = [m.filename for m in members]
        core.require(len(names) == len(set(names)), 'DUPLICATE_ZIP_PATH')
        core.require(len(names) <= 40000 and sum(m.file_size for m in members) <= MAX_ZIP_BYTES, 'ZIP_SIZE_LIMIT')
        for member in members:
            name = member.filename
            pure = PurePosixPath(name)
            core.require(name == pure.as_posix() and not pure.is_absolute() and '..' not in pure.parts
                         and '\\' not in name and ':' not in name and not member.is_dir(), 'UNSAFE_ZIP_PATH')
            core.require(not stat.S_ISLNK(member.external_attr >> 16), 'ZIP_SYMLINK')
        files = {name: archive.read(name) for name in names}
    core.require('FEEDBACK_MANIFEST.json' in files, 'MISSING_MANIFEST')
    manifest = json.loads(files.pop('FEEDBACK_MANIFEST.json'))
    core.require(manifest['protocol'] == PROTOCOL, 'ZIP_PROTOCOL')
    core.require(set(files) == set(manifest['files_sha256']), 'ZIP_FILE_SET')
    for name, raw in files.items():
        core.require(sha256(raw).hexdigest() == manifest['files_sha256'][name], 'ZIP_HASH:' + name)
    return manifest, files


def verify_archive_payload(files, expected):
    for name, value in [('bundle.json', expected['bundle']), ('partition.json', expected['partition']),
                        ('contract.json', expected['contract']), ('allocation.json', expected['allocation'])]:
        core.require(name in files and json.loads(files[name]) == value, 'ZIP_BINDING:' + name)
    for name, source in expected['code'].items():
        core.require(files.get('code/' + name) == source.encode(), 'ZIP_CODE_BINDING:' + name)


def restore_zip(path, destination, expected):
    manifest, files = read_archive(path)
    core.require(manifest['kind'] == 'FINAL' and manifest['automatic_resume_eligible'], 'FINAL_STOPPED_ZIP_REQUIRED')
    verify_archive_payload(files, expected)
    destination = Path(destination)
    core.require(not destination.exists(), 'RESTORE_REQUIRES_NEW_DESTINATION')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.xm01-restore-', dir=destination.parent) as temp:
        stage = Path(temp) / 'run'
        stage.mkdir()
        for name, raw in files.items():
            live.write_new(stage / name, raw)
        slots = verify_scope(stage, expected['bundle'], expected['partition'], expected['contract'])
        pair = core.load_fixed_code(expected['bundle'])
        # Reconstruct started-but-unanswered entries without retrying them.
        live.run_routes(live.EvidenceStore(stage, expected['contract']), expected['bundle'], pair,
                        expected['bundle']['materials'], slots)
        live.write_json(stage / ('restored-' + uuid.uuid4().hex + '.json'),
                        {'archive_sha256': sha256(Path(path).read_bytes()).hexdigest(), 'restored_at': live.now(),
                         'budget_used_seconds': budget_used(stage), 'previous_process_must_be_stopped': True})
        os.rename(stage, destination)


def summarize(pair, slots, rows):
    """Same tri-valued aggregation as frozen core; denominator follows this part."""
    core.require(set(rows) == {s['id'] for s in slots}, 'SUMMARY_ID_SET_MISMATCH')
    groups = sorted({s['group'] for s in slots})
    reps = sorted({s['replicate'] for s in slots})
    core.require(reps == [1, 2, 3] and len(groups) in (32, 64), 'SUMMARY_DESIGN_COUNT')
    indexed = {}
    for slot in slots:
        indexed.setdefault((slot['group'], slot['condition'], slot['replicate']), []).append(slot['id'])
    denominator = len(groups) * 3
    core.require(len(indexed) == denominator * 2 and all(len(ids) == 4 for ids in indexed.values()), 'GROUP_REP_COUNT')
    result = {'kind': 'FIXED_MATERIAL_DESCRIPTIVE_REPLICATION', 'material_count': len(groups),
              'replicates_per_material': 3, 'planned_responses': len(slots),
              'independent_material_count': len(groups), 'response_status': dict(Counter(r['status'] for r in rows.values())),
              'metrics': {}, 'stage_parts': {}}
    for metric in ('strict', 'content'):
        grouped = {key: pair.rc.tri_and(rows[sid]['score'].get(metric) for sid in ids) for key, ids in indexed.items()}
        methods = {}
        for method in ('REWRITE', 'SELECT'):
            c = core.counts(grouped[g, method, rep] for g in groups for rep in reps)
            patterns, by_group = Counter(), {}
            disagreement = evaluable = unresolved = 0
            for g in groups:
                values = [grouped[g, method, rep] for rep in reps]
                by_group[g] = values
                pattern = ('has_unresolved' if None in values else 'all_success' if all(values)
                           else 'all_failure' if not any(values) else 'mixed_success_failure')
                patterns[pattern] += 1
                for left, right in combinations(values, 2):
                    if left is None or right is None:
                        unresolved += 1
                    else:
                        evaluable += 1
                        disagreement += int(left != right)
            methods[method] = {'group_replicate_counts': c,
                               'success_bounds': [c['success'] / denominator, (c['success'] + c['unresolved']) / denominator],
                               'by_replicate': {str(rep): core.counts(grouped[g, method, rep] for g in groups) for rep in reps},
                               'by_group': by_group, 'repeat_patterns': dict(patterns),
                               'repeat_disagreement': {'different': disagreement, 'evaluable_pairs': evaluable,
                                                       'unresolved_pairs': unresolved, 'rate': disagreement / evaluable if evaluable else None}}
        s_lo, s_hi = methods['SELECT']['success_bounds']
        r_lo, r_hi = methods['REWRITE']['success_bounds']
        result['metrics'][metric] = {'methods': methods, 'select_minus_rewrite_missingness_bounds': [s_lo - r_hi, s_hi - r_lo],
                                    'paired_by_replicate': {str(rep): dict(Counter(f"R={grouped[g, 'REWRITE', rep]}|S={grouped[g, 'SELECT', rep]}" for g in groups)) for rep in reps},
                                    'p_value': None, 'confidence_interval': None,
                                    'reason': 'Descriptive fixed-material replication; no independent-N=192 test.'}
    values = {}
    for slot in slots:
        parts = (('private_note.customer', 'private_note.coverage', 'shared_note.coverage.A', 'shared_note.coverage.B')
                 if slot['stage'] == 'MERGE' else ('mascot', 'channel'))
        for part in parts:
            scores = rows[slot['id']]['score'].get('parts', {}).get(part, {})
            for metric in ('strict', 'content'):
                values.setdefault('|'.join((slot['condition'], slot['stage'], part, metric)), []).append(scores.get(metric))
    result['stage_parts'] = {key: core.counts(items) for key, items in sorted(values.items())}
    return result


def make_report(store, bundle, slots, rows):
    all_rows = {s['id']: rows.get(s['id'], {'status': 'NOT_ISSUED', 'score': live.unknown_score(), 'gate': 'NOT_RUN'}) for s in slots}
    summary = summarize(core.load_fixed_code(bundle), slots, all_rows)
    timings = []
    for slot in slots:
        path = store.directory(slot) / 'response.json'
        if path.exists():
            response = live.read_json(path)
            timings.append({'id': slot['id'], 'seconds': response['generation_seconds'],
                            'tokens': len(response['output_token_ids']), 'peak_vram_bytes': response['peak_vram_bytes']})
    return {'protocol': PROTOCOL, 'part': live.read_json(store.root / 'contract.json')['part'],
            'generated_at': live.now(), 'planned_responses': len(slots), 'closed_responses': len(rows),
            'collection_status': 'ALL_SLOTS_CLOSED' if len(rows) == len(slots) else 'PARTIAL',
            'attempted_generations': sum((store.directory(s) / 'started.json').exists() for s in slots),
            'received_responses': len(timings), 'semantic_accuracy_is_not_a_continuation_gate': True,
            'summary': summary, 'rows': all_rows, 'generation_timings': timings}


class ProgressStore(live.EvidenceStore):
    def __init__(self, root, contract, checkpoint_dir=None):
        super().__init__(root, contract)
        self.contract, self.checkpoint_dir = contract, checkpoint_dir
        self.closed = len(list((self.root / 'responses').glob('*/result.json')))
        self.last_checkpoint = self.closed
        self.checkpoint_time = time.monotonic()
        self.run_started = self.checkpoint_time
        self.initial_closed = self.closed

    def finish(self, slot, status, score=None, gate='NOT_RUN'):
        result = super().finish(slot, status, score, gate)
        self.closed += 1
        elapsed = time.monotonic() - self.run_started
        newly_closed = self.closed - self.initial_closed
        eta = elapsed / newly_closed * (768 - self.closed) if newly_closed else 0
        print(f"{self.contract['part']} 進捗 {self.closed}/768 / この処理区間 {elapsed/60:.1f}分 / 残り目安 {eta/3600:.2f}時間", flush=True)
        if self.checkpoint_dir and (self.closed - self.last_checkpoint >= 64 or time.monotonic() - self.checkpoint_time >= 1800):
            tag = str(self.closed).zfill(4) + '-' + uuid.uuid4().hex[:8]
            path = Path(self.checkpoint_dir) / f"npp-xm01-{self.contract['part'].lower()}-checkpoint-{tag}.zip"
            export_zip(self.root, path, kind='CHECKPOINT')
            self.last_checkpoint, self.checkpoint_time = self.closed, time.monotonic()
            print('定期ZIP保存（自動継続）:', path, flush=True)
        return result


def audit_root(root, bundle, partition, contract):
    slots = verify_scope(root, bundle, partition, contract)
    store = live.EvidenceStore(root, contract)
    rows = live.run_routes(store, bundle, core.load_fixed_code(bundle), bundle['materials'], slots)
    return make_report(store, bundle, slots, rows)


def worker_main(root, seconds, audit_only=False):
    root = Path(root)
    if not audit_only:
        core.require(platform.system() == 'Linux' and Path('/content').is_dir(), 'COLAB_ONLY_NO_MODEL_LOAD')
    def stop(signum, frame):
        live.STOP_REQUESTED = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    bundle, partition, contract = (live.read_json(root / name) for name in ('bundle.json', 'partition.json', 'contract.json'))
    slots = verify_scope(root, bundle, partition, contract)
    pair = core.load_fixed_code(bundle)
    checkpoint_dir = root.parent.parent / 'npp_xm01_checkpoints' / root.name
    store = ProgressStore(root, contract, None if audit_only else checkpoint_dir)
    deadline = time.monotonic() + max(0, seconds)
    try:
        rows = live.run_routes(store, bundle, pair, bundle['materials'], slots)
        if len(rows) < len(slots) and not audit_only and seconds > 0 and not live.STOP_REQUESTED:
            backend = live.HuggingFaceBackend(root, deadline)
            live.run_routes(store, bundle, pair, bundle['materials'], slots, backend, deadline)
    finally:
        rows = live.run_routes(store, bundle, pair, bundle['materials'], slots)
        report = make_report(store, bundle, slots, rows)
        path = root / ('report-' + uuid.uuid4().hex + '.json')
        live.write_json(path, report)
        print(json.dumps({k: report[k] for k in ('part', 'collection_status', 'closed_responses', 'attempted_generations', 'received_responses')}, ensure_ascii=False), flush=True)
        print('報告:', path, flush=True)


def aggregate_archives(paths, payload, output):
    core.require(len(paths) == 2, 'TWO_ARCHIVES_REQUIRED')
    combined, reports, environments, seen = {}, {}, {}, set()
    for path in paths:
        manifest, files = read_archive(path)
        core.require(manifest['kind'] == 'FINAL', 'FINAL_ARCHIVE_REQUIRED')
        part = manifest['part']
        core.require(part in ('PART1', 'PART2') and part not in seen, 'DUPLICATE_OR_INVALID_PART')
        seen.add(part)
        expected = {'bundle': payload['bundle'], 'partition': payload['partition'],
                    'contract': payload['contracts'][part], 'allocation': payload['partition']['parts'][part]['allocation'],
                    'code': payload['code']}
        verify_archive_payload(files, expected)
        with tempfile.TemporaryDirectory(prefix='xm01-offline-audit-') as temp:
            root = Path(temp)
            for name, raw in files.items():
                live.write_new(root / name, raw)
            report = audit_root(root, payload['bundle'], payload['partition'], expected['contract'])
            core.require(not set(combined) & set(report['rows']), 'DUPLICATE_RESULT_ID')
            combined.update(report['rows'])
            reports[part] = {k: v for k, v in report.items() if k != 'rows'}
            environments[part] = json.loads(files['environment.json']) if 'environment.json' in files else None
    slots = core.repeated_slots(payload['bundle']['base_slots'])
    result = summarize(core.load_fixed_code(payload['bundle']), slots, combined)
    result.update({'parts': reports, 'environments': environments, 'environment_equal_between_parts': environments['PART1'] == environments['PART2'],
                   'source_archives': [{'name': Path(p).name, 'sha256': sha256(Path(p).read_bytes()).hexdigest()} for p in paths],
                   'all_slots_closed': all(r['closed_responses'] == 768 for r in reports.values()), 'rows': combined})
    live.write_json(Path(output), result)
    return result


if __name__ == '__main__':
    worker_main(sys.argv[1], float(sys.argv[2]), audit_only=len(sys.argv) > 3 and sys.argv[3] == 'AUDIT_ONLY')
