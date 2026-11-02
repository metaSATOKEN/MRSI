"""OR01 frozen design and offline contracts. Standard library; no model/network calls."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

import update_readout_01_scoring as ur
import update_readout_01_envelope as envelope

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study2/designs/owner-recency-01-20260925'
PROTOCOL = 'OWNER-RECENCY-01/v1'
ARMS = {'G0P0': (False, False), 'G1P0': (True, False),
        'G0P1': (False, True), 'G1P1': (True, True)}
SOURCE = 'study2/designs/update-readout-01-20260925/design.json'
PINS = {SOURCE: 'c896e08550dcdc0f2b338437456044957858f7d9d92746e34330844692ddb8aa',
        'scripts/update_readout_01_envelope.py': '165b083ca6244238dec43f87e14884a30ac9854b666a9d339410d0f9cfa4bdb8'}
enc = ur.enc


def digest(value):
    return sha256(enc(value)).hexdigest()


def latest_rows(payload, row_schema):
    """Validate public input; filter by observer BEFORE comparing revisions. No gold argument."""
    if payload.get('holder') not in ('A', 'B'):
        raise ValueError('HOLDER')
    records = payload['records']
    if len(records) != 2 or {r['record_id'] for r in records} != {'PRIVATE', 'GROUP'}:
        raise ValueError('RECORDS')
    bodies = {r['record_id']: r['body'] for r in records}
    sources = {'PRIVATE.coverage': bodies['PRIVATE']['coverage'],
               'GROUP.coverage.A': bodies['GROUP']['coverage']['A'],
               'GROUP.coverage.B': bodies['GROUP']['coverage']['B'],
               'NOTICE': payload['incoming_notice']}
    catalog = payload['row_catalog']
    if len(catalog) != 4 or {c['row_id'] for c in catalog} != {'C1', 'C2', 'C3', 'C4'}:
        raise ValueError('CATALOG_IDS')
    if {c['location'] for c in catalog} != set(sources):
        raise ValueError('CATALOG_LOCATIONS')
    for c in catalog:
        if set(c) != {'row_id', 'location', 'row'} or ur.shape(c['row'], row_schema):
            raise ValueError('CATALOG_SCHEMA')
        if c['row'] != sources[c['location']]:
            raise ValueError('CATALOG_SOURCE_MISMATCH')
    selected = {}; witnesses = {}
    for owner in ('A', 'B'):
        candidates = [c for c in catalog if c['row']['observer'] == owner]
        if not candidates:
            raise ValueError('MISSING_OWNER:' + owner)
        by_version = {}
        for c in candidates:
            version = c['row']['revision']
            if version in by_version and by_version[version] != c['row']:
                raise ValueError('CONFLICTING_EQUAL_REVISION:' + owner)
            by_version[version] = c['row']
        revision = max(by_version)
        winners = sorted((c for c in candidates if c['row']['revision'] == revision), key=lambda c: c['row_id'])
        selected[owner] = deepcopy(winners[0]['row'])
        witnesses[owner] = {'owner': owner, 'revision': revision,
            'candidate_ids': sorted(c['row_id'] for c in candidates),
            'equal_latest_ids': [c['row_id'] for c in winners],
            'selected_id': winners[0]['row_id'], 'location': winners[0]['location'],
            'row_sha256': digest(winners[0]['row'])}
    return selected, witnesses


def transform(proposal, payload, arm, schema):
    """The sole intervention. Customer remains model-written in EVERY arm."""
    if arm not in ARMS:
        raise ValueError('UNKNOWN_ARM')
    if ur.shape(proposal, schema):
        raise ValueError('UNACCEPTED_PROPOSAL')
    latest, witnesses = latest_rows(payload, schema['properties']['private_note']['properties']['coverage'])
    group_on, private_on = ARMS[arm]
    memory = deepcopy(proposal); changes = []
    def copy_to(target, owner, destination, key):
        before = deepcopy(destination[key]); destination[key] = deepcopy(latest[owner])
        changes.append({'target': target, 'before_sha256': digest(before),
                        'after_sha256': digest(destination[key]), 'changed': before != destination[key],
                        'source': deepcopy(witnesses[owner])})
    if group_on:
        for owner in ('A', 'B'):
            copy_to('shared_note.coverage.' + owner, owner, memory['shared_note']['coverage'], owner)
    if private_on:
        copy_to('private_note.coverage', payload['holder'], memory['private_note'], 'coverage')
    assert memory['private_note']['customer'] == proposal['private_note']['customer']
    return memory, changes


def receive(raw, stage, finish_reason='EOS'):
    """Same exact-envelope repair in both stages; enforce limits on RAW bytes."""
    if stage not in ('UPDATE', 'READ'):
        raise ValueError('UNKNOWN_STAGE')
    if raw is None:
        return {'status': 'UNRESOLVED', 'reason': 'MISSING', 'normalized_bytes': None}
    if not isinstance(raw, bytes):
        raise TypeError('RAW_BYTES_REQUIRED')
    if finish_reason != 'EOS':
        return envelope.normalize(raw, finish_reason)
    if len(raw) > (16384 if stage == 'UPDATE' else 4096):
        return {'status': 'REJECT', 'reason': 'STAGE_RAW_BYTES_LIMIT', 'normalized_bytes': None,
                'raw_sha256': sha256(raw).hexdigest(), 'raw_bytes': len(raw)}
    return envelope.normalize(raw, finish_reason)


def score_memory(memory, case, schema):
    score = ur.score_update(enc(memory), case, 'REWRITE', schema)
    want = case['expected_memory']; private = memory['private_note']['coverage']
    score['private_owner_exact'] = private['observer'] == case['role']
    score['private_owner_revision_exact'] = (private['observer'], private['revision']) == (
        case['role'], want['private_note']['coverage']['revision'])
    score['shared_owner_exact'] = {r: memory['shared_note']['coverage'][r]['observer'] == r for r in ('A', 'B')}
    score['shared_owner_revision_exact'] = {r: (memory['shared_note']['coverage'][r]['observer'],
        memory['shared_note']['coverage'][r]['revision']) == (r, want['shared_note']['coverage'][r]['revision']) for r in ('A', 'B')}
    return score


def prepare(design, case, raw, finish_reason='EOS'):
    """Offline preparation; none of the four branches bypasses a rejected common parent."""
    receipt = receive(raw, 'UPDATE', finish_reason)
    result = {'receipt': {k: v for k, v in receipt.items() if k != 'normalized_bytes'},
              'normalized_bytes': receipt['normalized_bytes'], 'proposal_score': None,
              'branches': {arm: None for arm in ARMS}, 'error': None}
    if receipt['normalized_bytes'] is None:
        result['error'] = 'UNACCEPTED_PARENT'; return result
    proposal = ur.parse(receipt['normalized_bytes'])
    score = ur.score_update(receipt['normalized_bytes'], case, 'REWRITE', design['update_schema'])
    result['proposal_score'] = score
    if score['gate'] != 'PASS':
        result['error'] = 'PARENT_SCHEMA'; return result
    try:
        # Validate once before any branch, including the OFF/OFF control.
        latest_rows(case['update_payload'], design['update_schema']['properties']['private_note']['properties']['coverage'])
    except (ValueError, KeyError, TypeError) as exc:
        result['error'] = 'POLICY_INPUT_ERROR:' + str(exc); return result
    for arm in ARMS:
        memory, trace = transform(proposal, case['update_payload'], arm, design['update_schema'])
        result['branches'][arm] = {'memory': memory, 'trace': trace,
            'score': score_memory(memory, case, design['update_schema'])}
    return result


def score_read(raw, memory, case, schema, finish_reason='EOS'):
    receipt = receive(raw, 'READ', finish_reason)
    data = receipt['normalized_bytes']
    score = ur.score_read(data, memory, case, schema, 'EOS' if data is not None else 'UNRESOLVED')
    score['normalization'] = {k: v for k, v in receipt.items() if k != 'normalized_bytes'}
    return score


def requests(design):
    cases = {c['id']: c for c in design['cases']}
    return [{'id': p['id'] + '-UPDATE', 'seed': p['update_seed'], 'messages': [
        {'role': 'system', 'content': design['update_prompt']},
        {'role': 'user', 'content': '\n資料JSON:\n' + enc(cases[p['case']]['update_payload']).decode()}]}
        for p in design['parents']]


def read_groups(design, parent, case, memories):
    """Deduplicate only identical inputs BEFORE generation, within one common parent."""
    if set(memories) != set(ARMS):
        raise ValueError('ARM_SET')
    groups = {}; order = []
    for arm in parent['arm_order']:
        memory = memories[arm]
        if memory is None:
            continue
        messages = [{'role': 'system', 'content': design['read_prompt']},
                    {'role': 'user', 'content': '\n資料JSON:\n' + enc(ur.read_payload(case, memory)).decode()}]
        identity = {'messages': messages, 'schema': design['read_schema'],
                    'model': design['model'], 'seed': parent['read_seed']}
        key = digest(identity)
        if key not in groups:
            groups[key] = {'id': parent['id'] + '-READ-U' + str(len(order) + 1),
                'parent_id': parent['id'], 'input_sha256': key, **identity, 'logical_ids': [], 'arms': []}
            order.append(key)
        # Verify bytes too, rather than trusting a hash alone.
        assert enc(identity) == enc({k: groups[key][k] for k in identity})
        groups[key]['logical_ids'].append(parent['id'] + '-' + arm + '-READ')
        groups[key]['arms'].append(arm)
    return [groups[k] for k in order]


def build_design():
    for path, expected in PINS.items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('SOURCE_CHANGED:' + path)
    old = json.loads((ROOT / SOURCE).read_bytes())
    source_pins = dict(PINS)
    cases = deepcopy(old['cases'])
    for c in cases:
        source_pins.update(c['source_files_sha256'])
        latest, _ = latest_rows(c['update_payload'], old['schemas']['REWRITE']['properties']['private_note']['properties']['coverage'])
        assert latest == c['expected_memory']['shared_note']['coverage']
        assert latest[c['role']] == c['expected_memory']['private_note']['coverage']
    for path, expected in source_pins.items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('SOURCE_CHANGED:' + path)
    parents = []; pipelines = []
    ordered = sorted(cases, key=lambda c: digest([PROTOCOL, 'order', c['id']]))
    for rep in (1, 2):
        for case in (ordered if rep == 1 else ordered[::-1]):
            i = len(parents); arm_order = list(ARMS); shift = i % 4
            arm_order = arm_order[shift:] + arm_order[:shift]
            pid = case['id'].replace('UR01-', 'OR01-') + f'-R{rep}'
            parent = {'id': pid, 'case': case['id'], 'set': case['set'], 'replicate': rep,
                'arm_order': arm_order, 'update_seed': int(digest([pid, 'UPDATE'])[:8], 16) % 2**31,
                'read_seed': int(digest([pid, 'READ'])[:8], 16) % 2**31}
            parents.append(parent)
            pipelines.extend({'id': pid + '-' + arm, 'parent': pid, 'case': case['id'],
                'set': case['set'], 'condition': arm, 'replicate': rep} for arm in arm_order)
    return {'protocol': PROTOCOL, 'status': 'DESIGN_FROZEN_NO_MODEL_GENERATION',
        'source_pins': source_pins, 'cases': cases, 'parents': parents, 'pipelines': pipelines,
        'arms': {k: {'shared_owner_latest': g, 'private_owner_latest': p} for k, (g, p) in ARMS.items()},
        'update_prompt': old['prompts']['REWRITE'].replace('private_noteは両方式とも本文を記述します。',
                                                          'private_noteは本文を記述します。'),
        'update_schema': old['schemas']['REWRITE'],
        'read_prompt': old['read_prompt'], 'read_schema': old['read_schema'], 'model': old['model'],
        'normalization': {'rule': envelope.PROTOCOL, 'update_raw_bytes': 16384, 'read_raw_bytes': 4096,
                          'value_repair': False, 'applied_before_schema': True},
        'limits': {'max_updates': 36, 'max_logical_reads': 144, 'max_generations': 180,
            'seconds_including_setup': 5400, 'automatic_regenerations': 0, 'cloud_drive': 'not_used',
            'retention': 'private_no_deletion_deadline'},
        'decision_rules': {'repair': 18, 'repair_each_repeat': 9, 'guard': 14,
            'guard_each_repeat': 7, 'private_customer': 36, 'p_value': None, 'confidence_interval': None}}


def summarize(design, outcomes):
    expected = {p['id'] for p in design['pipelines']}
    if set(outcomes) - expected:
        raise ValueError('UNEXPECTED_PIPELINE')
    def value(p, metric):
        o = outcomes.get(p['id'], {}); u = o.get('update', {}); r = o.get('read', {})
        return ur.end_to_end(u, r) if metric == 'end_to_end_exact' else u.get(metric)
    def vals(arm, metric, subset=None, rep=None):
        return [value(p, metric) for p in design['pipelines'] if p['condition'] == arm
                and (subset is None or p['set'] == subset) and (rep is None or p['replicate'] == rep)]
    metrics = ('joint_state_exact', 'end_to_end_exact')
    arms = {}
    for arm in ARMS:
        arms[arm] = {}
        for metric in metrics:
            sets = {s: ur.counts(vals(arm, metric, s)) for s in ('REPAIR', 'GUARD')}
            reps = {s: {str(r): ur.counts(vals(arm, metric, s, r)) for r in (1, 2)} for s in sets}
            customer = ur.counts(vals(arm, 'private_customer_exact'))
            tests = [(sets['REPAIR'], 18), (sets['GUARD'], 14), (customer, 36)]
            tests += [(v, 9 if s == 'REPAIR' else 7) for s in reps for v in reps[s].values()]
            status = 'MET' if all(c['correct'] >= n for c, n in tests) else 'NOT_MET' if any(
                c['correct'] + c['unresolved'] < n for c, n in tests) else 'INCONCLUSIVE'
            arms[arm][metric] = {'by_set': sets, 'by_repeat': reps, 'private_customer': customer, 'criterion_status': status}
    comparisons = [('G1P0', 'G0P0', 'shared_latest_exact'), ('G1P1', 'G0P1', 'shared_latest_exact'),
                   ('G0P1', 'G0P0', 'private_observation_exact'), ('G1P1', 'G1P0', 'private_observation_exact')]
    contrasts = {}
    for high, low, component in comparisons:
        entry = {}
        for subset in ('REPAIR', 'GUARD'):
            entry[subset] = {}
            for rep in (None, 1, 2):
                parents = [p for p in design['parents'] if p['set'] == subset and (rep is None or p['replicate'] == rep)]
                lookup = {p['id']: p for p in design['pipelines']}
                data = {}
                for metric in (component,) + metrics:
                    pairs = [(value(lookup[p['id'] + '-' + high], metric), value(lookup[p['id'] + '-' + low], metric)) for p in parents]
                    counts = Counter('unresolved' if a is None or b is None else 'improved' if a and not b
                        else 'worsened' if b and not a else 'same_correct' if a else 'same_incorrect' for a, b in pairs)
                    lower = sum((int(a) if a is not None else 0) - (int(b) if b is not None else 1) for a, b in pairs)
                    upper = sum((int(a) if a is not None else 1) - (int(b) if b is not None else 0) for a, b in pairs)
                    data[metric] = {'counts': dict(counts), 'n': len(pairs), 'difference_bounds_count': [lower, upper]}
                baseline = [value(lookup[p['id'] + '-' + low], component) for p in parents]
                data['opportunity'] = {'observed_component_failures': baseline.count(False),
                    'unresolved': baseline.count(None), 'status': 'OBSERVED_OPPORTUNITY' if False in baseline else 'NO_OBSERVED_OPPORTUNITY'}
                entry[subset]['all' if rep is None else str(rep)] = data
        contrasts[high + '-' + low] = entry
    return {'kind': 'PAIRED_BRANCH_DIAGNOSTIC_NOT_INDEPENDENT_ARMS', 'materials': 18,
            'common_parents': 36, 'logical_reads': 144, 'arms': arms, 'contrasts': contrasts}


def freeze():
    design = build_design()
    OUT.mkdir(parents=True, exist_ok=False)
    def write(name, value):
        (OUT / name).write_bytes(enc(value) + b'\n')
    write('design.json', design); write('update-requests.json', requests(design))
    (OUT / 'prompt-update.txt').write_text(design['update_prompt'])
    (OUT / 'prompt-read.txt').write_text(design['read_prompt'])
    write('schemas.json', {'UPDATE': design['update_schema'], 'READ': design['read_schema']})
    for name in ('owner_recency_01_design.py', 'update_readout_01_scoring.py', 'update_readout_01_envelope.py',
                 'saved_readout_01_scoring.py', 'readout_split_01_scoring.py'):
        (OUT / name).write_bytes((ROOT / 'scripts' / name).read_bytes())
    (OUT / 'README.md').write_text('# OWNER-RECENCY-01 固定物\n\n18既知材料、36共通更新、144論理READ。実モデル未実行。\n'
        'design.jsonのexpected_memoryは採点専用。生成器・保存介入・READへ渡さない。\n'
        '同じ親内の完全一致READ入力は共用。旧試験の成績を変更しない。\n')
    write('MANIFEST.json', {p.name: sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()})
    print(json.dumps({'design': str(OUT), 'sha256': sha256((OUT / 'design.json').read_bytes()).hexdigest(),
                      'parents': len(design['parents']), 'branches': len(design['pipelines'])}))


if __name__ == '__main__':
    freeze()
