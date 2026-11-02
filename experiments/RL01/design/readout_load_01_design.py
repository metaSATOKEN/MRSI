"""READOUT-LOAD-01 design and offline scoring. Standard library; no model backend."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path

from aggregate_cross_model_e1_01 import load_payload
import cross_model_e1_01_offline_runtime as core

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'READOUT-LOAD-01/v1'
METHODS = ('FULL', 'DUAL', 'CHANNEL')
CHANNELS = ('PAPER', 'DIGITAL', 'UNKNOWN')
ANIMALS = ('DOG', 'CAT', 'UNKNOWN')
CELL = ROOT / 'study2/colab/cross_model_e1_01_main_onecell.py'
OUT = ROOT / 'study2/designs/readout-load-01-20260925'


def enc(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(obj):
    return sha256(enc(obj)).hexdigest()


def rank(text):
    return sha256((PROTOCOL + '|' + text).encode()).hexdigest()


def truth_from_coverage(coverage):
    choices = [m.upper() for m in ('paper', 'digital')
               if all(coverage[r][m] == 'ALL' for r in ('A', 'B'))]
    return choices[0] if len(choices) == 1 else 'UNKNOWN'


def opposite_blockers(material):
    alternative = 'digital' if material['final_channel'] == 'PAPER' else 'paper'
    return ''.join(r for r in ('A', 'B') if material['notices'][r][alternative] == 'NOT_ALL')


def selection(materials):
    cells = []
    for channel in ('PAPER', 'DIGITAL'):
        for role in ('A', 'B'):
            for blockers in ('A', 'B', 'AB'):
                label = '|'.join((channel, role, blockers))
                options = [g for g, m in materials.items()
                           if m['final_channel'] == channel and opposite_blockers(m) == blockers]
                options.sort(key=lambda g: rank('select|' + label + '|' + g))
                if not options:
                    raise ValueError('EMPTY_SELECTION_CELL:' + label)
                cells.append({'channel': channel, 'role': role, 'blockers': blockers,
                              'stratum': label, 'options': options})

    def solve(i, used, choices, balances):
        if i == len(cells):
            return choices
        for group in cells[i]['options']:
            if group not in used:
                c = cells[i]
                animal = materials[group]['baseline_by_role'][c['role']]['private_note']['customer']['animal']
                keys = [('role', c['role'], animal), ('channel', c['channel'], animal),
                        ('blockers', c['blockers'], animal), ('role_channel', c['role'] + '|' + c['channel'], animal)]
                if any(balances[k] >= (2 if k[0] in ('blockers', 'role_channel') else 3) for k in keys):
                    continue
                updated = balances.copy()
                updated.update(keys)
                result = solve(i + 1, used | {group}, choices + [group], updated)
                if result is not None:
                    return result
        return None

    groups = solve(0, set(), [], Counter())
    if groups is None:
        raise ValueError('NO_DISTINCT_BALANCED_SELECTION')
    return [dict(cell, source_group=g) for cell, g in zip(cells, groups)]


def notes_payload(material, role, pair):
    memory = pair.rc.expected_memory(material, role, 'MERGE')
    return {'scene': material['scene'], 'item': material['item'], 'holder': role,
            'records': [{'record_id': 'PRIVATE', 'body': deepcopy(memory['private_note'])},
                        {'record_id': 'GROUP', 'body': deepcopy(memory['shared_note'])}]}


def case_gold(payload):
    bodies = {r['record_id']: r['body'] for r in payload['records']}
    coverage = bodies['GROUP']['coverage']
    return {'channel': truth_from_coverage(coverage), 'mascot': bodies['PRIVATE']['customer']['animal'],
            'channel_origins': [coverage[r]['origin_id'] for r in ('A', 'B')],
            'mascot_origins': [bodies['PRIVATE']['customer']['origin_id']]}


def make_prompts(bundle, pair):
    full = bundle['prompts']['PROBE']
    schema = deepcopy(pair.rc.memory_schemas()['PROBE'])
    full_schema = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
    assert full.count(full_schema) == 1
    prose = full.split(full_schema)[0]
    evidence_start = '根拠の現在記録名と元観測IDを分けて記録してください。'
    evidence_tail = ('read_receiptは今回の各欄の根拠記録名で、ノート本文へ混ぜません。'
                     '同じ値を支える記録が複数なら一件でも複数件でもよいですが、無関係な記録を加えず、'
                     '元観測IDや昔の資料名を現在記録名の代わりにしないでください。'
                     '確定した欄には現在参照を一件以上記録し、不明で根拠を挙げられない欄は空配列にしてください。')
    assert prose.count(evidence_start) == prose.count(evidence_tail) == 1
    dual_prose = prose.replace(evidence_start, '').replace(evidence_tail, '')
    mascot = '自分の担当客が希望した犬猫にmascotを合わせてください。'
    assert dual_prose.count(mascot) == 1
    schemas = {'FULL': schema}
    for method in ('DUAL', 'CHANNEL'):
        decision = deepcopy(schema['properties']['decision'])
        if method == 'CHANNEL':
            decision['properties'].pop('mascot')
            decision['required'] = ['channel']
        schemas[method] = {'type': 'object', 'properties': {'decision': decision},
                           'required': ['decision'], 'additionalProperties': False}
    prompts = {'FULL': full}
    for method in ('DUAL', 'CHANNEL'):
        text = dual_prose if method == 'DUAL' else dual_prose.replace(mascot, '')
        prompts[method] = text + json.dumps(schemas[method], ensure_ascii=False, separators=(',', ':')) + '\n\n'
    return prompts, schemas


def build_design():
    source = load_payload(CELL)
    bundle = source['bundle']
    pair = core.load_fixed_code(bundle)
    chosen = selection(bundle['materials'])
    cases = []
    for i, spec in enumerate(chosen, 1):
        payload = notes_payload(bundle['materials'][spec['source_group']], spec['role'], pair)
        cases.append({'id': f'RL01-M{i:02}', 'set': 'MAIN',
                      'source_group': spec['source_group'], 'stratum': spec['stratum'],
                      'role': spec['role'], 'blockers': spec['blockers'],
                      'payload': payload, 'gold': case_gold(payload)})
    used = {x['source_group'] for x in cases}
    remaining = sorted(set(bundle['materials']) - used, key=lambda g: rank('boundary|' + g))
    for i, (kind, role) in enumerate((('ZERO', 'A'), ('ZERO', 'B'), ('TWO', 'A'), ('TWO', 'B')), 1):
        animal = ('DOG', 'CAT', 'CAT', 'DOG')[i - 1]
        group = next(g for g in remaining
                     if bundle['materials'][g]['baseline_by_role'][role]['private_note']['customer']['animal'] == animal)
        remaining.remove(group)
        material = deepcopy(bundle['materials'][group])
        for owner in ('A', 'B'):
            row = material['notices'][owner]
            row['paper'] = 'ALL' if kind == 'TWO' or owner == 'A' else 'NOT_ALL'
            row['digital'] = 'ALL' if kind == 'TWO' or owner == 'B' else 'NOT_ALL'
            row['origin_id'] = 'RL' + rank(f'boundary-origin|{i}|{owner}')[:14].upper()
        payload = notes_payload(material, role, pair)
        cases.append({'id': f'RL01-B{i:02}', 'set': 'BOUNDARY', 'boundary_kind': kind,
                      'source_group': group, 'role': role, 'payload': payload, 'gold': case_gold(payload),
                      'derivation': 'New synthetic coverage and observation IDs; baseline scene/customer preserved.'})
    for case in cases:
        assert not pair.validate_input('E1', 'PROBE', case['payload'])
        case['payload_sha256'] = digest(case['payload'])
    prompts, schemas = make_prompts(bundle, pair)
    orders = list(permutations(METHODS))
    mains = sorted(cases[:12], key=lambda c: rank('case-order|' + c['id']))
    blocks = []
    for i, case in enumerate(mains):
        blocks.append((case, orders[i % 6]))
        if (i + 1) % 3 == 0:
            bi = (i + 1) // 3 - 1
            blocks.append((cases[12 + bi], orders[bi]))
    allocation = []
    for rep in (1, 2):
        for case, order in blocks:
            order = order if rep == 1 else tuple(reversed(order))
            seed = int(rank(f'seed|{case["id"]}|{rep}')[:8], 16) % (2 ** 31)
            for position, method in enumerate(order, 1):
                allocation.append({'id': f'{case["id"]}-R{rep}-{method}', 'case': case['id'],
                                   'set': case['set'], 'condition': method, 'replicate': rep,
                                   'seed': seed, 'condition_position': position, 'dependencies': []})
    return {'protocol': PROTOCOL, 'status': 'DESIGN_FROZEN_NO_LIVE_GENERATION',
            'source_cell_sha256': sha256(CELL.read_bytes()).hexdigest(), 'source_bundle_sha256': digest(bundle),
            'source_code_hashes': bundle['source_hashes'], 'selection_cells': chosen,
            'cases': cases, 'prompts': prompts, 'schemas': schemas, 'allocation': allocation,
            'model': {k: source['contracts']['PART1'][k] for k in
                      ('model', 'revision', 'pins', 'generation', 'max_input_tokens', 'enable_thinking', 'dtype', 'attention')},
            'limits': {'max_generations': 96, 'seconds_including_setup': 5400, 'automatic_regenerations': 0,
                       'max_output_utf8_bytes_for_scoring': 4096, 'storage': 'colab_ephemeral_no_drive',
                       'delivery': 'zip_download', 'retention_proposal': 'private_no_deletion_deadline'},
            'decision_rules': {'signal_min_net_correct_per_24': 4, 'signal_each_replicate_lower_bound_positive': True,
                               'signal_each_truth_lower_bound_nonnegative': True, 'readout_min_correct_per_24': 20,
                               'readout_min_each_truth_per_12': 10, 'readout_min_each_rep_per_12': 9,
                               'boundary_min_each_kind_per_4': 3, 'p_value': None, 'confidence_interval': None}}


def requests(design):
    cases = {c['id']: c for c in design['cases']}
    return [{'id': s['id'], 'seed': s['seed'],
             'messages': [{'role': 'system', 'content': design['prompts'][s['condition']]},
                          {'role': 'user', 'content': '\n資料JSON:\n' + enc(cases[s['case']]['payload']).decode()}]}
            for s in design['allocation']]


def ideal(case, method):
    gold = case['gold']
    answer = {'decision': {'channel': gold['channel']}}
    if method != 'CHANNEL':
        answer['decision']['mascot'] = gold['mascot']
    if method == 'FULL':
        answer['read_receipt'] = {'mascot_record_refs': ['PRIVATE'], 'channel_record_refs': ['GROUP']}
        answer['origin_ids'] = {'mascot': list(gold['mascot_origins']), 'channel': list(gold['channel_origins'])}
    return answer


def score(raw, case, method, schema, pair, finish_reason='EOS'):
    """Component scores are independent of other fields' schema/provenance success."""
    result = {'channel': None, 'mascot': None, 'mascot_applicable': method != 'CHANNEL',
              'attribution_applicable': method == 'FULL', 'attribution': None,
              'format_valid': None, 'parse_valid': None, 'channel_output': None, 'errors': []}
    if raw is None or finish_reason != 'EOS':
        result['errors'] = ['MISSING_OR_NON_EOS']
        return result
    if isinstance(raw, str):
        raw = raw.encode()
    if len(raw) > 4096:
        result.update(format_valid=False, parse_valid=False, errors=['OUTPUT_BYTES'])
        return result
    try:
        value = pair.rc.parse(raw)
    except (ValueError, UnicodeError, RecursionError):
        result.update(format_valid=False, parse_valid=False, errors=['JSON'])
        return result
    result['parse_valid'] = True
    result['errors'] = pair.rc.shape(value, schema)
    result['format_valid'] = not result['errors']
    decision = value.get('decision') if type(value) is dict else None
    if type(decision) is dict:
        channel = decision.get('channel')
        if type(channel) is str and channel in CHANNELS:
            result['channel_output'] = channel
            result['channel'] = channel == case['gold']['channel']
        if method != 'CHANNEL':
            animal = decision.get('mascot')
            if type(animal) is str and animal in ANIMALS:
                result['mascot'] = animal == case['gold']['mascot']
    if method == 'FULL':
        receipt = value.get('read_receipt') if type(value) is dict else None
        origins = value.get('origin_ids') if type(value) is dict else None
        diagnostics = {}
        for field in ('mascot', 'channel'):
            refs = receipt.get(field + '_record_refs') if type(receipt) is dict else None
            ids = origins.get(field) if type(origins) is dict else None
            ids_ok = (type(ids) is list and all(type(x) is str for x in ids)
                      and len(ids) == len(set(ids)) and set(ids) == set(case['gold'][field + '_origins']))
            diagnostics[field] = {'refs_exact': refs == (['PRIVATE'] if field == 'mascot' else ['GROUP']),
                                  'origins_exact': ids_ok}
        result['attribution'] = diagnostics
    return result


def counts(values):
    values = list(values)
    return {'correct': values.count(True), 'incorrect': values.count(False), 'unresolved': values.count(None), 'n': len(values)}


def bounds(values):
    c = counts(values)
    return (c['correct'] / c['n'], (c['correct'] + c['unresolved']) / c['n'])


def difference(later, earlier):
    lo, hi = bounds(later); before_lo, before_hi = bounds(earlier)
    return [lo - before_hi, hi - before_lo]


def summarize(design, scores):
    expected = {s['id'] for s in design['allocation']}
    if set(scores) - expected:
        raise ValueError('UNEXPECTED_RESPONSE_ID')
    cases = {c['id']: c for c in design['cases']}
    def values(method, rep=None, truth=None, subset='MAIN', kind=None):
        return [scores.get(s['id'], {}).get('channel') for s in design['allocation']
                if s['condition'] == method and s['set'] == subset
                and (rep is None or s['replicate'] == rep)
                and (truth is None or cases[s['case']]['gold']['channel'] == truth)
                and (kind is None or cases[s['case']].get('boundary_kind') == kind)]
    methods = {}
    for method in METHODS:
        per_rep = {str(rep): counts(values(method, rep=rep)) for rep in (1, 2)}
        per_truth = {truth: counts(values(method, truth=truth)) for truth in ('PAPER', 'DIGITAL')}
        boundary = {kind: counts(values(method, subset='BOUNDARY', kind=kind)) for kind in ('ZERO', 'TWO')}
        n = counts(values(method))
        adequate = (n['correct'] >= 20 and all(x['correct'] >= 9 for x in per_rep.values())
                    and all(x['correct'] >= 10 for x in per_truth.values())
                    and all(x['correct'] >= 3 for x in boundary.values()))
        methods[method] = {'main': n, 'bounds': bounds(values(method)), 'by_replicate': per_rep,
                           'by_truth': per_truth, 'boundary': boundary, 'readout_foothold': adequate}
    contrasts = {}
    for later, earlier in (('DUAL', 'FULL'), ('CHANNEL', 'DUAL')):
        def signal(a, b):
            return (difference(values(a), values(b))[0] >= 4 / 24 - 1e-12
                    and all(difference(values(a, rep=rep), values(b, rep=rep))[0] > 1e-12 for rep in (1, 2))
                    and all(difference(values(a, truth=t), values(b, truth=t))[0] >= -1e-12 for t in ('PAPER', 'DIGITAL')))
        contrasts[later + '-' + earlier] = {'bounds': difference(values(later), values(earlier)),
                                            'positive_signal': signal(later, earlier), 'negative_signal': signal(earlier, later)}
    return {'kind': 'DESCRIPTIVE_READOUT_COMPONENT_COMPARISON', 'main_materials': 12,
            'boundary_inputs': 4, 'planned_responses': 96, 'supplied_results': len(scores),
            'methods': methods, 'contrasts': contrasts, 'p_value': None, 'confidence_interval': None}


def save_new(path, raw):
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError('WOULD_CHANGE_FROZEN_DESIGN:' + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def freeze():
    design = build_design()
    for name, obj in [('design.json', design), ('requests.json', requests(design))]:
        save_new(OUT / name, json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2).encode() + b'\n')
    for method, text in design['prompts'].items():
        save_new(OUT / ('prompt-' + method.lower() + '.txt'), text.encode())
    save_new(OUT / 'readout_load_01_design.py', Path(__file__).read_bytes())
    return design


if __name__ == '__main__':
    design = freeze()
    print(json.dumps({'status': 'DESIGN_ONLY_NO_MODEL_EXECUTION', 'cases': len(design['cases']),
                      'responses': len(design['allocation']), 'output': str(OUT)}, ensure_ascii=False))
