"""Frozen UPDATE-READOUT-01 pure functions, copied verbatim from approved design."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import re
import readout_split_01_scoring as base
import saved_readout_01_scoring as readout
METHODS = ('REWRITE', 'SELECT')
enc = base.enc
parse = base.parse
counts = base.counts
four_values_valid = base.four_values_valid
compute_channel = base.compute_channel


def requests(design):
    cases = {c['id']: c for c in design['cases']}
    return [{'id': s['id'], 'seed': s['seed'], 'messages': [
        {'role': 'system', 'content': design['prompts'][s['condition']]},
        {'role': 'user', 'content': '\n資料JSON:\n' + enc(cases[s['case']]['update_payload']).decode()}]}
        for s in design['allocation'] if s['stage'] == 'UPDATE']


def shape(value, schema, path='$'):
    if 'enum' in schema:
        return [] if type(value) is str and value in schema['enum'] else [path + ':ENUM']
    if schema['type'] == 'string':
        return [] if type(value) is str and re.fullmatch(schema['pattern'], value) else [path + ':STRING']
    if schema['type'] == 'integer':
        return [] if type(value) is int and schema['minimum'] <= value <= schema['maximum'] else [path + ':INTEGER']
    if type(value) is not dict:
        return [path + ':OBJECT']
    errors = [path + '.' + k + ':MISSING' for k in schema['required'] if k not in value]
    errors += [path + '.' + k + ':EXTRA' for k in value if k not in schema['properties']]
    for k, spec in schema['properties'].items():
        if k in value:
            errors += shape(value[k], spec, path + '.' + k)
    return errors


def materialize(value, payload, method, schema):
    """Structural/selector validation only; no expected memory or hidden latest truth."""
    if method not in METHODS:
        raise ValueError('UNKNOWN_METHOD')
    errors = shape(value, schema)
    if errors:
        return None, [], errors
    if method == 'REWRITE':
        return deepcopy(value), [], []
    catalog = {r['row_id']: r for r in payload['row_catalog']}
    if any(value['shared_choice'][r] not in catalog for r in ('A', 'B')):
        return None, [], ['UNRESOLVED_SELECTOR']
    chosen = {r: catalog[value['shared_choice'][r]] for r in ('A', 'B')}
    memory = {'private_note': deepcopy(value['private_note']),
              'shared_note': {'coverage': {r: deepcopy(chosen[r]['row']) for r in ('A', 'B')}}}
    trace = [{'target': r, 'row_id': chosen[r]['row_id'], 'location': chosen[r]['location'],
              'source_row_sha256': sha256(enc(chosen[r]['row'])).hexdigest()} for r in ('A', 'B')]
    return memory, trace, []


def ideal_update(case, method):
    memory = deepcopy(case['expected_memory'])
    if method == 'REWRITE':
        return memory
    if method != 'SELECT':
        raise ValueError('UNKNOWN_METHOD')
    return {'private_note': memory['private_note'], 'shared_choice': {r:
        next(v['row_id'] for v in case['update_payload']['row_catalog'] if v['row'] == memory['shared_note']['coverage'][r])
        for r in ('A', 'B')}}


def score_update(raw, case, method, schema, finish_reason='EOS'):
    result = {'gate': 'UNRESOLVED', 'parse_valid': None, 'format_valid': None, 'memory': None, 'choice_trace': [],
        'private_customer_exact': None, 'private_observation_exact': None, 'shared_rows_exact': {'A': None, 'B': None},
        'shared_values_exact': None, 'shared_provenance_exact': None, 'shared_latest_exact': None,
        'shared_row_matches_input': {'A': None, 'B': None}, 'joint_state_exact': None, 'errors': []}
    if method not in METHODS:
        raise ValueError('UNKNOWN_METHOD')
    if raw is None or finish_reason != 'EOS':
        result['errors'] = ['MISSING_OR_NON_EOS']; return result
    raw = raw.encode() if isinstance(raw, str) else raw
    if len(raw) > 16384:
        result.update(parse_valid=False, format_valid=False, gate='REJECT', errors=['OUTPUT_BYTES']); return result
    try:
        value = base.parse(raw)
    except (ValueError, UnicodeError, RecursionError):
        result.update(parse_valid=False, format_valid=False, gate='REJECT', errors=['JSON']); return result
    result['parse_valid'] = True
    memory, trace, errors = materialize(value, case['update_payload'], method, schema)
    result.update(format_valid=not errors, memory=memory, choice_trace=trace, errors=errors, gate='REJECT' if errors else 'PASS')
    if memory is None:
        return result
    expected = case['expected_memory']; group = memory['shared_note']['coverage']; latest = expected['shared_note']['coverage']
    result['private_customer_exact'] = memory['private_note']['customer'] == expected['private_note']['customer']
    result['private_observation_exact'] = memory['private_note']['coverage'] == expected['private_note']['coverage']
    result['shared_rows_exact'] = {r: group[r] == latest[r] for r in ('A', 'B')}
    result['shared_values_exact'] = all(group[r][m] == latest[r][m] for r in ('A', 'B') for m in ('paper', 'digital'))
    result['shared_provenance_exact'] = all(group[r][m] == latest[r][m] for r in ('A', 'B') for m in ('observer', 'origin_id', 'revision'))
    result['shared_latest_exact'] = all(result['shared_rows_exact'].values())
    result['shared_row_matches_input'] = {r: any(group[r] == v['row'] for v in case['update_payload']['row_catalog']) for r in ('A', 'B')}
    result['joint_state_exact'] = all(result[k] for k in ('private_customer_exact', 'private_observation_exact', 'shared_latest_exact'))
    return result


def read_payload(case, memory):
    if memory is None:
        raise ValueError('NO_ACCEPTED_MEMORY')
    payload = deepcopy(case['original_notes_payload'])
    payload['records'] = [{'record_id': 'PRIVATE', 'body': deepcopy(memory['private_note'])},
                          {'record_id': 'GROUP', 'body': deepcopy(memory['shared_note'])}]
    return payload


def read_request(design, slot, case, memory):
    if slot['stage'] != 'READ':
        raise ValueError('NOT_READ_SLOT')
    return {'id': slot['id'], 'seed': slot['seed'], 'messages': [
        {'role': 'system', 'content': design['read_prompt']},
        {'role': 'user', 'content': '\n資料JSON:\n' + enc(read_payload(case, memory)).decode()}]}


def score_read(raw, memory, case, schema, finish_reason='EOS'):
    if memory is None:
        return {'dependency_missing': True, 'format_valid': None, 'four_exact': None, 'channel_note': None, 'channel_latest': None}
    group = memory['shared_note']['coverage']; latest = case['expected_memory']['shared_note']['coverage']
    pseudo_case = {'gold': {'four_values': group, 'channel': base.compute_channel(group),
        'latest_four_values': latest, 'latest_channel': case['latest_channel']}}
    result = readout.score(raw, pseudo_case, 'EXTRACT', schema, finish_reason)
    result['dependency_missing'] = False
    return result


def end_to_end(update, read):
    if update.get('gate') != 'PASS' or read.get('format_valid') is not True:
        return None
    return base.tri_all([update['joint_state_exact'], read.get('four_exact'), read.get('channel_latest')])


def summarize(design, outcomes):
    expected_ids = {p['id'] for p in design['pipelines']}
    if set(outcomes) - expected_ids:
        raise ValueError('UNEXPECTED_PIPELINE')
    def values(method, metric, subset=None, rep=None):
        out = []
        for p in design['pipelines']:
            if p['condition'] != method or (subset is not None and p['set'] != subset) or (rep is not None and p['replicate'] != rep):
                continue
            item = outcomes.get(p['id'], {}); update = item.get('update', {}); read = item.get('read', {})
            out.append(end_to_end(update, read) if metric == 'end_to_end_exact' else update.get(metric))
        return out
    def metric_summary(method, metric):
        groups = {s: base.counts(values(method, metric, s)) for s in ('REPAIR', 'GUARD')}
        reps = {s: {str(r): base.counts(values(method, metric, s, r)) for r in (1, 2)} for s in groups}
        person = base.counts(values(method, 'private_customer_exact'))
        tests = [(groups['REPAIR'], 18), (groups['GUARD'], 14), (person, 36)]
        tests += [(v, 9 if s == 'REPAIR' else 7) for s in reps for v in reps[s].values()]
        status = 'MET' if all(c['correct'] >= n for c, n in tests) else 'NOT_MET' if any(c['correct'] + c['unresolved'] < n for c, n in tests) else 'INCONCLUSIVE'
        return {'by_set': groups, 'by_repeat': reps, 'private_customer': person, 'criterion_status': status}
    def signal(a, b, metric):
        return (base.difference(values(a, metric, 'REPAIR'), values(b, metric, 'REPAIR'))[0] >= 4/20 - 1e-12
            and all(base.difference(values(a, metric, 'REPAIR', r), values(b, metric, 'REPAIR', r))[0] > 1e-12 for r in (1, 2))
            and base.difference(values(a, metric, 'GUARD'), values(b, metric, 'GUARD'))[0] >= -1e-12)
    metrics = ('joint_state_exact', 'end_to_end_exact')
    return {'kind': 'DESCRIPTIVE_UPDATE_AND_READOUT', 'planned_pipelines': 72, 'planned_responses': 144,
        'materials': {'REPAIR': 10, 'GUARD': 8},
        'methods': {m: {metric: metric_summary(m, metric) for metric in metrics} for m in METHODS},
        'contrasts': {metric: {'repair_bounds': base.difference(values('SELECT', metric, 'REPAIR'), values('REWRITE', metric, 'REPAIR')),
            'guard_bounds': base.difference(values('SELECT', metric, 'GUARD'), values('REWRITE', metric, 'GUARD')),
            'positive_signal': signal('SELECT', 'REWRITE', metric), 'negative_signal': signal('REWRITE', 'SELECT', metric)} for metric in metrics},
        'p_value': None, 'confidence_interval': None}
