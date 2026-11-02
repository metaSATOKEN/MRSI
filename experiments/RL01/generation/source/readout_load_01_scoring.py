"""Frozen scoring functions extracted verbatim from the approved READOUT-LOAD-01 design. No model imports."""
import json
METHODS = ("FULL", "DUAL", "CHANNEL")
CHANNELS = ("PAPER", "DIGITAL", "UNKNOWN")
ANIMALS = ("DOG", "CAT", "UNKNOWN")

def enc(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def truth_from_coverage(coverage):
    choices = [m.upper() for m in ('paper', 'digital')
               if all(coverage[r][m] == 'ALL' for r in ('A', 'B'))]
    return choices[0] if len(choices) == 1 else 'UNKNOWN'


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
