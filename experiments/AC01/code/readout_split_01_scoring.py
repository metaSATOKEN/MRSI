"""Approved READOUT-SPLIT-01 scoring, extracted verbatim. Standard library only."""

from collections import Counter

from copy import deepcopy

import json

METHODS = ('DIRECT', 'EXTRACT', 'RULE')

CHANNELS = ('PAPER', 'DIGITAL', 'UNKNOWN')

VALUES = ('ALL', 'NOT_ALL')

FIELDS = ('A.paper', 'A.digital', 'B.paper', 'B.digital')

def enc(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

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
