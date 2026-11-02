"""Frozen SAVED-READOUT-01 scoring; standard library only, no source-data access."""
from collections import Counter
import readout_split_01_scoring as base

METHODS = ('DIRECT', 'EXTRACT')
enc = base.enc
counts = base.counts
FIELDS = base.FIELDS
parse = base.parse
four_values_valid = base.four_values_valid
compute_channel = base.compute_channel

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
