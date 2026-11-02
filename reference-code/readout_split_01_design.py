"""READOUT-SPLIT-01 fixed design and component scoring; standard library only."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'study2/designs/readout-load-01-20260925/design.json'
SOURCE_SHA = 'd875ffba03fc3f97ef7226df67000b270d009362f5dc76a7123f80c7c08f1d37'
OUT = ROOT / 'study2/designs/readout-split-01-20260925'
PROTOCOL = 'READOUT-SPLIT-01/v1'
METHODS = ('DIRECT', 'EXTRACT', 'RULE')
CHANNELS = ('PAPER', 'DIGITAL', 'UNKNOWN')
VALUES = ('ALL', 'NOT_ALL')
FIELDS = ('A.paper', 'A.digital', 'B.paper', 'B.digital')
RULE_SENTENCE = '案内方法はA/Bの両方でALLと確認できる方法がちょうど一つならPAPERまたはDIGITAL、0個または2個ならUNKNOWNとしてください。'


def enc(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(obj):
    return sha256(enc(obj)).hexdigest()


def rank(text):
    return sha256((PROTOCOL + '|' + text).encode()).hexdigest()


def read_field(coverage, field):
    role, medium = field.split('.')
    row = coverage.get(role) if type(coverage) is dict else None
    return row.get(medium) if type(row) is dict else None


def four_values_valid(coverage):
    return all(type(read_field(coverage, f)) is str and read_field(coverage, f) in VALUES for f in FIELDS)


def compute_channel(coverage):
    """Derive only from all four valid supplied values; never consult gold."""
    if not four_values_valid(coverage):
        return None
    paper = coverage['A']['paper'] == 'ALL' and coverage['B']['paper'] == 'ALL'
    digital = coverage['A']['digital'] == 'ALL' and coverage['B']['digital'] == 'ALL'
    if paper == digital:
        return 'UNKNOWN'
    return 'PAPER' if paper else 'DIGITAL'


def object_schema(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def build_design():
    raw = SOURCE.read_bytes()
    if sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('SOURCE_DESIGN_CHANGED')
    old = json.loads(raw)
    cases = []
    for c in old['cases']:
        group = next(r['body'] for r in c['payload']['records'] if r['record_id'] == 'GROUP')
        four = {r: {m: group['coverage'][r][m] for m in ('paper', 'digital')} for r in ('A', 'B')}
        if compute_channel(four) != c['gold']['channel']:
            raise ValueError('GOLD_COVERAGE_MISMATCH')
        cases.append({'id': c['id'].replace('RL01-', 'RS01-'), 'source_case': c['id'],
                      'source_group': c['source_group'], 'set': c['set'], 'role': c['role'],
                      'boundary_kind': c.get('boundary_kind'), 'blockers': c.get('blockers'),
                      'notes_payload': deepcopy(c['payload']), 'rule_payload': {'coverage': four},
                      'notes_payload_sha256': c['payload_sha256'], 'rule_payload_sha256': digest({'coverage': four}),
                      'pattern': '|'.join(read_field(four, f) for f in FIELDS),
                      'gold': {'four_values': deepcopy(four), 'channel': c['gold']['channel']}})
    row = object_schema({m: {'enum': list(VALUES)} for m in ('paper', 'digital')})
    extract_schema = object_schema({'coverage': object_schema({r: deepcopy(row) for r in ('A', 'B')})})
    schemas = {'DIRECT': deepcopy(old['schemas']['CHANNEL']), 'EXTRACT': extract_schema,
               'RULE': deepcopy(old['schemas']['CHANNEL'])}
    extract = ('あなたは架空の作業担当者です。今回の資料JSONのrecordsから、record_idがGROUPの記録を読み、'
               'body.coverage.Aとbody.coverage.Bのpaperとdigitalの値をそのまま転記してください。'
               'ALLとNOT_ALLは入力にある文字列を保ってください。'
               '担当役にかかわらずA/Bの両方、計四値を書いてください。'
               '犬猫の判断、案内方法の選択、理由、参照名、元ID、版番号は出力しません。'
               'JSON以外を出力せず、schemaの全必須欄・A/B固定キーを守ってください。\n')
    rule = ('あなたは架空の作業担当者です。今回の資料JSONのcoverageに、'
            'A/Bのpaperとdigitalの観測値が与えられています。今回の四値だけを根拠に仕事を決めてください。'
            + RULE_SENTENCE + '過去に出した結論を推測しないでください。'
            'JSON以外を出力せず、schemaの全必須欄を守ってください。\n')
    prompts = {'DIRECT': old['prompts']['CHANNEL'],
               'EXTRACT': extract + json.dumps(extract_schema, ensure_ascii=False, separators=(',', ':')) + '\n\n',
               'RULE': rule + json.dumps(schemas['RULE'], ensure_ascii=False, separators=(',', ':')) + '\n\n'}
    main = sorted([c for c in cases if c['set'] == 'MAIN'], key=lambda c: rank('order|' + c['id']))
    boundary = [c for c in cases if c['set'] == 'BOUNDARY']
    orders = list(permutations(METHODS)); blocks = []
    for i, c in enumerate(main):
        blocks.append((c, orders[i % 6]))
        if (i + 1) % 3 == 0:
            j = (i + 1) // 3 - 1
            blocks.append((boundary[j], orders[j]))
    allocation = []
    for rep in (1, 2):
        for c, order in blocks:
            seed = int(rank(f'seed|{c["id"]}|{rep}')[:8], 16) % (2 ** 31)
            for pos, method in enumerate(order if rep == 1 else tuple(reversed(order)), 1):
                allocation.append({'id': f'{c["id"]}-R{rep}-{method}', 'case': c['id'], 'set': c['set'],
                                   'condition': method, 'replicate': rep, 'condition_position': pos,
                                   'seed': seed, 'dependencies': []})
    return {'protocol': PROTOCOL, 'status': 'DESIGN_FROZEN_NO_GENERATION', 'source_design_sha256': SOURCE_SHA,
            'selection': 'All 16 RL01 cases unchanged; no selection using individual outcomes.',
            'cases': cases, 'schemas': schemas, 'prompts': prompts, 'allocation': allocation,
            'model': deepcopy(old['model']),
            'limits': {'max_generations': 96, 'seconds_including_setup': 5400, 'automatic_regenerations': 0,
                       'max_output_utf8_bytes_for_scoring': 4096, 'storage': 'colab_ephemeral_no_drive',
                       'delivery': 'zip_download', 'retention': 'private_no_deletion_deadline'},
            'decision_rules': {'signal_min_net_correct_per_24': 4, 'each_repeat_lower_positive': True,
                               'each_truth_lower_nonnegative': True, 'adequate_main': 20,
                               'adequate_each_truth': 10, 'adequate_each_repeat': 9,
                               'adequate_each_boundary': 3, 'p_value': None, 'confidence_interval': None}}


def requests(design):
    cases = {c['id']: c for c in design['cases']}
    rows = []
    for s in design['allocation']:
        c = cases[s['case']]
        payload = c['rule_payload'] if s['condition'] == 'RULE' else c['notes_payload']
        rows.append({'id': s['id'], 'seed': s['seed'], 'messages': [
            {'role': 'system', 'content': design['prompts'][s['condition']]},
            {'role': 'user', 'content': '\n資料JSON:\n' + enc(payload).decode()}]})
    return rows


def parse(raw):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('DUPLICATE_JSON_KEY')
            obj[key] = value
        return obj
    def nonstandard(value):
        raise ValueError('NONSTANDARD_NUMBER')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=nonstandard)


def shape(value, schema, path='$'):
    if 'enum' in schema:
        return [] if type(value) is str and value in schema['enum'] else [path + ':ENUM']
    if type(value) is not dict:
        return [path + ':OBJECT']
    errors = [path + '.' + key + ':MISSING' for key in schema['required'] if key not in value]
    errors += [path + '.' + key + ':EXTRA' for key in value if key not in schema['properties']]
    for key, spec in schema['properties'].items():
        if key in value:
            errors.extend(shape(value[key], spec, path + '.' + key))
    return errors


def tri_all(values):
    values = list(values)
    return False if False in values else None if None in values else True


def ideal(case, method):
    return {'coverage': deepcopy(case['gold']['four_values'])} if method == 'EXTRACT' else {'decision': {'channel': case['gold']['channel']}}


def score(raw, case, method, schema, finish_reason='EOS'):
    if method not in METHODS:
        raise ValueError('UNKNOWN_CONDITION')
    result = {'parse_valid': None, 'format_valid': None, 'channel': None, 'channel_output': None,
              'channel_kind': 'DETERMINISTIC_FROM_EXTRACTED_VALUES' if method == 'EXTRACT' else 'LLM',
              'extraction_applicable': method == 'EXTRACT', 'four_valid': None, 'four_exact': None,
              'fields': {f: None for f in FIELDS} if method == 'EXTRACT' else None,
              'extracted_values': None, 'errors': []}
    if raw is None or finish_reason != 'EOS':
        result['errors'] = ['MISSING_OR_NON_EOS']; return result
    raw = raw.encode() if isinstance(raw, str) else raw
    if len(raw) > 4096:
        result.update(parse_valid=False, format_valid=False, errors=['OUTPUT_BYTES']); return result
    try:
        value = parse(raw)
    except (ValueError, UnicodeError, RecursionError):
        result.update(parse_valid=False, format_valid=False, errors=['JSON']); return result
    result['parse_valid'] = True
    result['errors'] = shape(value, schema)
    result['format_valid'] = not result['errors']
    if method == 'EXTRACT':
        coverage = value.get('coverage') if type(value) is dict else None
        result['extracted_values'] = deepcopy(coverage)
        result['four_valid'] = four_values_valid(coverage)
        for f in FIELDS:
            v = read_field(coverage, f)
            if type(v) is str and v in VALUES:
                result['fields'][f] = v == read_field(case['gold']['four_values'], f)
        result['four_exact'] = tri_all(result['fields'].values())
        predicted = compute_channel(coverage)
    else:
        decision = value.get('decision') if type(value) is dict else None
        predicted = decision.get('channel') if type(decision) is dict else None
    if type(predicted) is str and predicted in CHANNELS:
        result['channel_output'] = predicted
        result['channel'] = predicted == case['gold']['channel']
    return result


def counts(values):
    values = list(values)
    if any(v is not None and type(v) is not bool for v in values):
        raise ValueError('NON_TRIVALUED_SCORE')
    return {'correct': values.count(True), 'incorrect': values.count(False), 'unresolved': values.count(None), 'n': len(values)}


def bounds(values):
    c = counts(values)
    return [c['correct'] / c['n'], (c['correct'] + c['unresolved']) / c['n']]


def difference(later, earlier):
    lo, hi = bounds(later); a, b = bounds(earlier)
    return [lo - b, hi - a]


def summarize(design, scores):
    expected = {s['id'] for s in design['allocation']}
    if set(scores) - expected:
        raise ValueError('UNEXPECTED_RESPONSE_ID')
    cases = {c['id']: c for c in design['cases']}
    def values(method, metric='channel', subset='MAIN', rep=None, truth=None, kind=None, pattern=None):
        return [scores.get(s['id'], {}).get(metric) for s in design['allocation']
                if s['condition'] == method and s['set'] == subset
                and (rep is None or s['replicate'] == rep)
                and (truth is None or cases[s['case']]['gold']['channel'] == truth)
                and (kind is None or cases[s['case']]['boundary_kind'] == kind)
                and (pattern is None or cases[s['case']]['pattern'] == pattern)]
    def metric_summary(method, metric):
        main = counts(values(method, metric))
        reps = {str(r): counts(values(method, metric, rep=r)) for r in (1, 2)}
        truths = {t: counts(values(method, metric, truth=t)) for t in ('PAPER', 'DIGITAL')}
        boundary = {k: counts(values(method, metric, subset='BOUNDARY', kind=k)) for k in ('ZERO', 'TWO')}
        adequate = (main['correct'] >= 20 and all(c['correct'] >= 9 for c in reps.values())
                    and all(c['correct'] >= 10 for c in truths.values())
                    and all(c['correct'] >= 3 for c in boundary.values()))
        thresholds = [(main, 20)] + [(c, 9) for c in reps.values()] + [(c, 10) for c in truths.values()] + [(c, 3) for c in boundary.values()]
        status = 'MET' if adequate else 'NOT_MET' if any(c['correct'] + c['unresolved'] < n for c, n in thresholds) else 'INCONCLUSIVE'
        return {'main': main, 'bounds': bounds(values(method, metric)), 'by_replicate': reps,
                'by_truth': truths, 'boundary': boundary, 'adequate': adequate, 'criterion_status': status,
                'by_pattern': {p: counts(values(method, metric, subset=subset, pattern=p))
                    for subset in ('MAIN', 'BOUNDARY') for p in sorted({c['pattern'] for c in design['cases'] if c['set'] == subset})}}
    methods = {m: metric_summary(m, 'channel') for m in METHODS}
    extraction = metric_summary('EXTRACT', 'four_exact')
    contrasts = {}
    for later in ('RULE', 'EXTRACT'):
        def signal(a, b):
            return (difference(values(a), values(b))[0] >= 4/24 - 1e-12
                    and all(difference(values(a, rep=r), values(b, rep=r))[0] > 1e-12 for r in (1, 2))
                    and all(difference(values(a, truth=t), values(b, truth=t))[0] >= -1e-12 for t in ('PAPER', 'DIGITAL')))
        contrasts[later + '-DIRECT'] = {'bounds': difference(values(later), values('DIRECT')),
                                        'positive_signal': signal(later, 'DIRECT'), 'negative_signal': signal('DIRECT', later)}
    accidental = {}; all_rows = [s for s in design['allocation'] if s['condition'] == 'EXTRACT']
    for subset in ('MAIN', 'BOUNDARY'):
        rows = [scores.get(s['id'], {}) for s in all_rows if s['set'] == subset]
        accidental[subset] = dict(Counter('four_exact=' + str(r.get('four_exact')) + '|channel=' + str(r.get('channel')) for r in rows))
    return {'kind': 'DESCRIPTIVE_STAGE_DIAGNOSTIC', 'planned_responses': 96, 'main_materials': 12,
            'boundary_inputs': 4, 'distinct_rule_inputs': 8, 'distinct_main_rule_inputs': 6,
            'supplied_scores': len(scores), 'methods': methods, 'extraction_exact': extraction,
            'contrasts': contrasts, 'extraction_vs_derived_decision': accidental,
            'p_value': None, 'confidence_interval': None}


def freeze():
    design = build_design()
    OUT.mkdir(parents=True, exist_ok=True)
    items = {'design.json': json.dumps(design, ensure_ascii=False, sort_keys=True, indent=2).encode() + b'\n',
             'requests.json': json.dumps(requests(design), ensure_ascii=False, sort_keys=True, indent=2).encode() + b'\n',
             'readout_split_01_design.py': Path(__file__).read_bytes()}
    items.update({'prompt-' + m.lower() + '.txt': t.encode() for m, t in design['prompts'].items()})
    for name, raw in items.items():
        p = OUT / name
        if p.exists() and p.read_bytes() != raw:
            raise ValueError('WOULD_CHANGE_FROZEN_DESIGN:' + name)
        if not p.exists(): p.write_bytes(raw)
    return design


if __name__ == '__main__':
    x = freeze()
    print(json.dumps({'status': x['status'], 'cases': len(x['cases']), 'responses': len(x['allocation']), 'output': str(OUT)}, ensure_ascii=False))
