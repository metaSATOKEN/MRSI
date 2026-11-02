"""SAVED-READOUT-01: freeze real saved-note inputs and dual-reference scoring. No model calls."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from aggregate_cross_model_e1_01 import load_payload
import readout_split_01_scoring as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study2/designs/saved-readout-01-20260925'
PROTOCOL = 'SAVED-READOUT-01/v1'
METHODS = ('DIRECT', 'EXTRACT')
DIRECT_OLD_SCOPE = '今回のPRIVATEとGROUPだけを根拠に仕事を決めてください。'
DIRECT_GROUP_SCOPE = ('案内方法は今回の資料JSONのrecordsのうち、record_idがGROUPのbody.coverageにあるA/Bの四値だけから決めてください。'
                      'PRIVATEの観測値でGROUPを補完・更新せず、GROUPに書かれた値をそのまま使ってください。')
CELL = 'study2/colab/cross_model_e1_01_main_onecell.py'
PREVIOUS = 'study2/designs/readout-split-01-20260925/design.json'
PINS = {
    CELL: 'fd735084f6da4755cab05fad08a0ddedac4cab147668159dfb90b795729862cd',
    PREVIOUS: '1ec12f121c464b19c6df258d9069480bedb94c1013a90a4000ca1e74c56e06df',
    'scripts/readout_split_01_scoring.py': 'fc4bc5aa181a46745c6f29875d650a63c3e1908735331eda85ff653eb99b1e45',
    'throughline/audits/cross-model-e1-01-part1-result-20260924/MANIFEST.json': '787127b5d67d7c88a5d8bfd4f0c29764404998aae31209d5480c8f0d50765b97',
    'throughline/audits/cross-model-e1-01-part2-result-20260925/MANIFEST.json': '33b4cf99bdbf7783d30c47c0342b7e3a4baeb7be25eedb508267e2efa596f0b7',
}
enc = base.enc


def digest(obj):
    return sha256(enc(obj)).hexdigest()


def rank(text):
    return sha256((PROTOCOL + '|' + text).encode()).hexdigest()


def four(coverage):
    return {r: {m: coverage[r][m] for m in ('paper', 'digital')} for r in ('A', 'B')}


def scan_sources():
    for name, expected in PINS.items():
        if sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('SOURCE_CHANGED:' + name)
    previous = json.loads((ROOT / PREVIOUS).read_bytes())
    original = load_payload(ROOT / CELL)
    snapshots = []
    for part, date in (('PART1', '20260924'), ('PART2', '20260925')):
        directory = ROOT / f'throughline/audits/cross-model-e1-01-{part.lower()}-result-{date}'
        manifest = json.loads((directory / 'MANIFEST.json').read_bytes())['files_sha256']
        def read(name):
            raw = (directory / name).read_bytes()
            if sha256(raw).hexdigest() != manifest[name]:
                raise ValueError('EVIDENCE_CHANGED:' + name)
            return json.loads(raw), {str((directory / name).relative_to(ROOT)): manifest[name]}
        for slot in original['partition']['parts'][part]['allocation']:
            if slot['stage'] != 'PROBE':
                continue
            name = 'received/responses/' + slot['id'] + '/input.json'
            # Enumerate membership from the frozen manifest, so a missing file is not silently dropped.
            if name not in manifest:
                continue
            actual_input, evidence = read(name)
            parent = slot['dependencies'][0]
            memory, hashes = read('received/responses/' + parent + '/saved-memory.json'); evidence.update(hashes)
            result, hashes = read('received/responses/' + parent + '/result.json'); evidence.update(hashes)
            if result['gate'] != 'PASS':
                raise ValueError('NON_ACCEPTED_PARENT')
            payload = actual_input['payload']
            bodies = {r['record_id']: r['body'] for r in payload['records']}
            if bodies != {'PRIVATE': memory['private_note'], 'GROUP': memory['shared_note']}:
                raise ValueError('SAVED_TO_INPUT_MISMATCH')
            material = original['bundle']['materials'][slot['group']]
            coverage = bodies['GROUP']['coverage']
            latest = material['notices']
            observed, current = four(coverage), four(latest)
            if not base.four_values_valid(observed) or not base.four_values_valid(current):
                raise ValueError('INVALID_SOURCE_VALUES')
            note_channel = base.compute_channel(observed)
            world_channel = base.compute_channel(current)
            if world_channel != material['final_channel']:
                raise ValueError('LATEST_TRUTH_MISMATCH')
            row_exact = {r: coverage[r] == latest[r] for r in ('A', 'B')}
            latest_memory = material['baseline_by_role'][slot['role']]['private_note']
            private_customer_exact = bodies['PRIVATE']['customer'] == latest_memory['customer']
            private_coverage_exact = bodies['PRIVATE']['coverage'] == latest[slot['role']]
            if not private_customer_exact or not private_coverage_exact:
                raise ValueError('UNEXPECTED_PRIVATE_NOTE_FAILURE')
            stale = [r for r in ('A', 'B') if not row_exact[r]]
            kinds = sum(all(observed[r][m] == 'ALL' for r in ('A', 'B')) for m in ('paper', 'digital'))
            snapshots.append({
                'source_response_id': slot['id'], 'source_parent_id': parent, 'source_group': slot['group'],
                'source_condition': slot['condition'], 'source_replicate': slot['replicate'], 'source_part': part,
                'role': slot['role'], 'notes_payload': payload, 'payload_sha256': digest(payload),
                'source_files_sha256': evidence,
                'note_state': {'shared_latest_exact': all(row_exact.values()), 'shared_rows_latest_exact': row_exact,
                    'private_customer_latest_exact': private_customer_exact, 'private_observation_latest_exact': private_coverage_exact,
                    'private_group_observation_conflict': bodies['PRIVATE']['coverage'] != coverage[slot['role']],
                    'stale_rows': stale, 'saved_coverage': deepcopy(coverage), 'latest_coverage': deepcopy(latest),
                    'note_world_channel_agree': note_channel == world_channel},
                'note_kind': {0: 'ZERO', 1: 'ONE', 2: 'TWO'}[kinds],
                'pattern': '|'.join(base.read_field(observed, f) for f in base.FIELDS),
                'gold': {'four_values': observed, 'channel': note_channel,
                         'latest_four_values': current, 'latest_channel': world_channel}})
    if len(snapshots) != 240 or sum(not c['note_state']['shared_latest_exact'] for c in snapshots) != 10:
        raise ValueError('SOURCE_POPULATION_CHANGED')
    return snapshots, previous


def select_main(snapshots, previous):
    exclude = {c['source_group'] for c in previous['cases']}
    exclude |= {c['source_group'] for c in snapshots if not c['note_state']['shared_latest_exact']}
    candidates = [c for c in snapshots if c['note_state']['shared_latest_exact'] and c['source_group'] not in exclude]
    strata = [(m, r, t) for m in ('REWRITE', 'SELECT') for r in ('A', 'B') for t in ('PAPER', 'DIGITAL')]
    cells = [stratum for stratum in strata for _ in range(2)]
    def solve(i, used, selected):
        if i == len(cells):
            return selected
        key = cells[i]
        options = [c for c in candidates if (c['source_condition'], c['role'], c['gold']['channel']) == key]
        options.sort(key=lambda c: rank('main|' + '|'.join(key) + '|' + c['source_response_id']))
        for c in options:
            if c['source_group'] not in used:
                found = solve(i + 1, used | {c['source_group']}, selected + [c])
                if found is not None:
                    return found
        return None
    chosen = solve(0, set(), [])
    if chosen is None:
        raise ValueError('NO_DISTINCT_BALANCED_SELECTION')
    return deepcopy(chosen)


def build_design():
    snapshots, previous = scan_sources()
    main = select_main(snapshots, previous)
    stress = sorted([deepcopy(c) for c in snapshots if not c['note_state']['shared_latest_exact']],
                    key=lambda c: rank('stress|' + c['source_response_id']))
    cases = []
    for subset, selected, prefix in (('MAIN', main, 'M'), ('STALE', stress, 'S')):
        for i, case in enumerate(selected, 1):
            case.update(id=f'SVR01-{prefix}{i:02}', set=subset)
            cases.append(case)
    # Interleave 16 main and 10 stale inputs; balance first method separately in each set.
    main = sorted(cases[:16], key=lambda c: rank('order|' + c['id']))
    stress = cases[16:]; blocks = []
    for i, c in enumerate(main):
        blocks.append((c, METHODS if i % 2 == 0 else METHODS[::-1]))
        if i < len(stress):
            blocks.append((stress[i], METHODS if i % 2 == 0 else METHODS[::-1]))
    allocation = []
    for rep in (1, 2):
        for case, order in blocks:
            seed = int(rank(f'seed|{case["id"]}|{rep}')[:8], 16) % (2 ** 31)
            for pos, method in enumerate(order if rep == 1 else order[::-1], 1):
                allocation.append({'id': f'{case["id"]}-R{rep}-{method}', 'case': case['id'], 'set': case['set'],
                                   'condition': method, 'replicate': rep, 'condition_position': pos, 'seed': seed, 'dependencies': []})
    catalog = [{k: c[k] for k in ('source_response_id', 'source_group', 'source_condition', 'role', 'payload_sha256')}
               | {'shared_latest_exact': c['note_state']['shared_latest_exact'],
                  'note_channel': c['gold']['channel'], 'latest_channel': c['gold']['latest_channel']}
               for c in snapshots]
    prompts = {m: previous['prompts'][m] for m in METHODS}
    if prompts['DIRECT'].count(DIRECT_OLD_SCOPE) != 1:
        raise ValueError('SOURCE_PROMPT_SCOPE_CHANGED')
    prompts['DIRECT'] = prompts['DIRECT'].replace(DIRECT_OLD_SCOPE, DIRECT_GROUP_SCOPE)
    return {'protocol': PROTOCOL, 'status': 'DESIGN_FROZEN_NO_GENERATION', 'source_pins': PINS,
            'permitted_evidence': 'GROUP_COVERAGE_ONLY_BOTH_METHODS',
            'prompt_change': 'DIRECT scope restricted to GROUP to match EXTRACT; all other DIRECT text and both schemas unchanged.',
            'source_inventory': catalog, 'population': {'accepted_saved_inputs': 240, 'latest_exact': 230, 'stale': 10},
            'selection': '16 distinct new readout groups, two per source-method/holder/channel cell; all 10 stale snapshots. No original PROBE answers read.',
            'cases': cases, 'allocation': allocation, 'model': deepcopy(previous['model']),
            'prompts': prompts, 'schemas': {m: previous['schemas'][m] for m in METHODS},
            'limits': {'max_generations': 104, 'seconds_including_setup': 5400, 'automatic_regenerations': 0,
                'max_output_utf8_bytes_for_scoring': 4096, 'storage': 'colab_ephemeral_no_drive',
                'delivery': 'zip_download', 'retention': 'private_no_deletion_deadline'},
            'decision_rules': {'main': 28, 'main_each_truth': 14, 'main_each_repeat': 14,
                'stale': 18, 'stale_zero': 6, 'stale_two': 3, 'contrast_lower_correct_per_32': 4,
                'each_repeat_positive': True, 'each_truth_nonnegative': True, 'p_value': None, 'confidence_interval': None}}


def requests(design):
    cases = {c['id']: c for c in design['cases']}
    return [{'id': s['id'], 'seed': s['seed'], 'messages': [
        {'role': 'system', 'content': design['prompts'][s['condition']]},
        {'role': 'user', 'content': '\n資料JSON:\n' + enc(cases[s['case']]['notes_payload']).decode()}]}
        for s in design['allocation']]


def ideal(case, method):
    return base.ideal(case, method)


def score(raw, case, method, schema, finish_reason='EOS'):
    """Base channel/four_exact mean faithful to the saved note, never to hidden latest truth."""
    if method not in METHODS:
        raise ValueError('UNKNOWN_CONDITION')
    result = base.score(raw, case, method, schema, finish_reason)
    out = result['channel_output']
    result['channel_note'] = result['channel']
    result['channel_latest'] = None if out is None else out == case['gold']['latest_channel']
    result['four_latest_exact'] = None
    if method == 'EXTRACT' and result['parse_valid']:
        latest_fields = []
        for field in base.FIELDS:
            value = base.read_field(result['extracted_values'], field)
            latest_fields.append(value == base.read_field(case['gold']['latest_four_values'], field)
                                 if type(value) is str and value in base.VALUES else None)
        result['four_latest_exact'] = base.tri_all(latest_fields)
    return result


def summarize(design, scores):
    expected = {s['id'] for s in design['allocation']}
    if set(scores) - expected:
        raise ValueError('UNEXPECTED_RESPONSE_ID')
    cases = {c['id']: c for c in design['cases']}
    def values(method, metric='channel_note', subset='MAIN', **filters):
        return [scores.get(s['id'], {}).get(metric) for s in design['allocation']
                if s['condition'] == method and s['set'] == subset
                and all((s['replicate'] if k == 'replicate' else cases[s['case']]['gold']['channel'] if k == 'truth'
                         else cases[s['case']][k]) == v for k, v in filters.items())]
    def summary(method, metric):
        main = base.counts(values(method, metric)); stale = base.counts(values(method, metric, 'STALE'))
        reps = {str(r): base.counts(values(method, metric, replicate=r)) for r in (1, 2)}
        truths = {t: base.counts(values(method, metric, truth=t)) for t in ('PAPER', 'DIGITAL')}
        kinds = {k: base.counts(values(method, metric, 'STALE', note_kind=k)) for k in ('ZERO', 'ONE', 'TWO')}
        thresholds = [(main, 28), (stale, 18), (kinds['ZERO'], 6), (kinds['TWO'], 3)]
        thresholds += [(v, 14) for v in reps.values()] + [(v, 14) for v in truths.values()]
        status = ('MET' if all(c['correct'] >= n for c, n in thresholds) else 'NOT_MET'
                  if any(c['correct'] + c['unresolved'] < n for c, n in thresholds) else 'INCONCLUSIVE')
        return {'main': main, 'main_bounds': base.bounds(values(method, metric)), 'stale': stale,
                'by_replicate': reps, 'by_note_truth': truths, 'stale_by_kind': kinds, 'criterion_status': status,
                'main_by_source_method': {v: base.counts(values(method, metric, source_condition=v)) for v in ('REWRITE', 'SELECT')},
                'main_by_role': {v: base.counts(values(method, metric, role=v)) for v in ('A', 'B')}}
    def signal(a, b):
        return (base.difference(values(a), values(b))[0] >= 4 / 32 - 1e-12
                and all(base.difference(values(a, replicate=r), values(b, replicate=r))[0] > 1e-12 for r in (1, 2))
                and all(base.difference(values(a, truth=t), values(b, truth=t))[0] >= -1e-12 for t in ('PAPER', 'DIGITAL')))
    patterns, cross = {}, {}
    for method in METHODS:
        patterns[method] = {}
        cross[method] = {}
        for subset in ('MAIN', 'STALE'):
            selected = [s for s in design['allocation'] if s['condition'] == method and s['set'] == subset]
            cross[method][subset] = dict(Counter('note=' + str(scores.get(s['id'], {}).get('channel_note'))
                + '|latest=' + str(scores.get(s['id'], {}).get('channel_latest')) for s in selected))
            patterns[method][subset] = {p: base.counts(values(method, pattern=p, subset=subset))
                                        for p in sorted({cases[s['case']]['pattern'] for s in selected})}
    extraction_cross = {}
    for subset in ('MAIN', 'STALE'):
        selected = [s for s in design['allocation'] if s['condition'] == 'EXTRACT' and s['set'] == subset]
        extraction_cross[subset] = dict(Counter('|'.join(k + '=' + str(scores.get(s['id'], {}).get(k))
            for k in ('four_exact', 'channel_note', 'channel_latest')) for s in selected))
    return {'kind': 'DESCRIPTIVE_SAVED_NOTE_READOUT', 'planned_responses': 104, 'supplied_scores': len(scores),
            'main_materials': 16, 'stale_materials': 10, 'methods': {m: summary(m, 'channel_note') for m in METHODS},
            'extraction_exact': summary('EXTRACT', 'four_exact'),
            'latest_channel': {m: {subset: base.counts(values(m, 'channel_latest', subset)) for subset in ('MAIN', 'STALE')} for m in METHODS},
            'extraction_latest': {subset: base.counts(values('EXTRACT', 'four_latest_exact', subset)) for subset in ('MAIN', 'STALE')},
            'note_latest_cross': cross, 'by_pattern': patterns,
            'extraction_note_latest_cross': extraction_cross,
            'contrast': {'bounds': base.difference(values('EXTRACT'), values('DIRECT')),
                         'positive_signal': signal('EXTRACT', 'DIRECT'), 'negative_signal': signal('DIRECT', 'EXTRACT')},
            'p_value': None, 'confidence_interval': None}


def freeze():
    design = build_design()
    OUT.mkdir(parents=True, exist_ok=True)
    items = {'design.json': json.dumps(design, ensure_ascii=False, sort_keys=True, indent=2).encode() + b'\n',
             'requests.json': json.dumps(requests(design), ensure_ascii=False, sort_keys=True, indent=2).encode() + b'\n',
             'saved_readout_01_design.py': Path(__file__).read_bytes(),
             'readout_split_01_scoring.py': (ROOT / 'scripts/readout_split_01_scoring.py').read_bytes()}
    items.update({'prompt-' + m.lower() + '.txt': text.encode() for m, text in design['prompts'].items()})
    for name, raw in items.items():
        p = OUT / name
        if p.exists() and p.read_bytes() != raw:
            raise ValueError('WOULD_CHANGE_FROZEN_DESIGN:' + name)
        if not p.exists():
            p.write_bytes(raw)
    return design


if __name__ == '__main__':
    design = freeze()
    print(json.dumps({'status': design['status'], 'cases': len(design['cases']), 'responses': len(design['allocation'])}))
