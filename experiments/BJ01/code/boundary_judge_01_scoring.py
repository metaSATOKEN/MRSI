"""BJ01 fixed judge-output validation and diagnostic aggregation. Stdlib only."""
from collections import Counter
from hashlib import sha256
import json
import re

AXES = ('output_contract', 'attribution', 'local_choice', 'joint_action')
MAX_RAW_BYTES = 16384


def require(ok, why):
    if not ok:
        raise ValueError(why)


def strict_loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'DUPLICATE_KEY:' + key)
            result[key] = value
        return result
    def reject(value):
        raise ValueError('NONFINITE:' + value)
    return json.loads(raw.decode('utf-8', errors='strict'), object_pairs_hook=pairs, parse_constant=reject)


def validate_schema(value, schema, path=''):
    if 'enum' in schema:
        require(any(type(value) is type(item) and value == item for item in schema['enum']), 'ENUM:' + path)
    kind = schema.get('type')
    if kind == 'object':
        require(type(value) is dict, 'OBJECT:' + path)
        require(set(schema.get('required', ())) <= set(value), 'REQUIRED:' + path)
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            require(set(value) <= set(props), 'EXTRA_KEY:' + path)
        for key, item in value.items():
            if key in props:
                validate_schema(item, props[key], path + '/' + key)
    elif kind == 'array':
        require(type(value) is list, 'ARRAY:' + path)
        require(schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', float('inf')), 'ITEM_COUNT:' + path)
        for i, item in enumerate(value):
            validate_schema(item, schema['items'], path + '/' + str(i))
    elif kind == 'string':
        require(type(value) is str, 'STRING:' + path)
        require(schema.get('minLength', 0) <= len(value) <= schema.get('maxLength', float('inf')), 'STRING_LENGTH:' + path)
        value.encode('utf-8', errors='strict')
    elif kind is not None:
        raise ValueError('UNSUPPORTED_SCHEMA_TYPE:' + str(kind))


def resolve_pointer(packet, pointer, allowed_roots):
    require(isinstance(pointer, str) and pointer.startswith('/'), 'POINTER_SYNTAX')
    require(not re.search(r'~(?![01])', pointer), 'POINTER_ESCAPE')
    parts = [part.replace('~1', '/').replace('~0', '~') for part in pointer[1:].split('/')]
    require(parts[0] in allowed_roots, 'POINTER_ROOT:' + pointer)
    current = packet
    for part in parts:
        if type(current) is dict:
            require(part in current, 'POINTER_MISSING:' + pointer)
            current = current[part]
        elif type(current) is list:
            require(re.fullmatch(r'0|[1-9][0-9]*', part) is not None, 'POINTER_INDEX:' + pointer)
            require(int(part) < len(current), 'POINTER_RANGE:' + pointer)
            current = current[int(part)]
        else:
            raise ValueError('POINTER_SCALAR:' + pointer)
    return current


def unknown(reason):
    return {'format_valid': False, 'errors': [reason], 'answer': None,
            'axis_match': {axis: None for axis in AXES}, 'case_match': None,
            'case_state': 'UNKNOWN', 'reason_semantics': 'NOT_REVIEWED'}


def score(raw, finish_reason, packet, expected, schema):
    """No fence removal, repairs, rejudging, or use of judge output as gold."""
    try:
        require(type(raw) is bytes and len(raw) <= MAX_RAW_BYTES, 'RAW_BYTE_LIMIT')
        require(finish_reason == 'EOS', 'INCOMPLETE_OUTPUT:' + str(finish_reason))
        answer = strict_loads(raw)
        validate_schema(answer, schema)
        require(answer['judgment_id'] == packet['judgment_id'], 'JUDGMENT_ID')
        for axis in AXES:
            item = answer['checks'][axis]
            for pointer in item['answer_pointers']:
                resolve_pointer(packet, pointer, ('answer',))
            for pointer in item['evidence_pointers']:
                resolve_pointer(packet, pointer, ('payload', 'contract', 'facts'))
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        return unknown(str(error))
    matches = {axis: None if answer['checks'][axis]['verdict'] == 'UNRESOLVED'
               else answer['checks'][axis]['verdict'] == expected[axis] for axis in AXES}
    case = False if False in matches.values() else None if None in matches.values() else True
    return {'format_valid': True, 'errors': [], 'answer': answer, 'axis_match': matches,
            'case_match': case, 'case_state': {True: 'MATCH', False: 'MISMATCH', None: 'UNKNOWN'}[case],
            'reason_semantics': 'NOT_REVIEWED'}


def counts(values):
    values = list(values)
    return {'planned': len(values), 'match': sum(v is True for v in values),
            'mismatch': sum(v is False for v in values), 'unknown': sum(v is None for v in values)}


def summarize(labels, scores):
    require(len(labels) == 64 and len({x['judgment_id'] for x in labels}) == 64, '64_UNIQUE_CASES')
    require(set(scores) == {x['judgment_id'] for x in labels}, 'SCORE_ID_SET')
    def selected(predicate):
        return [row for row in labels if predicate(row)]
    def count_rows(rows):
        return counts(scores[row['judgment_id']]['case_match'] for row in rows)
    report = {'cases': count_rows(labels), 'axes': {}, 'by_kind': {}, 'by_variant': {},
              'by_synthetic_base': {}, 'by_real_source_root': {}, 'by_stage': {}, 'by_role': {},
              'scope': 'Fixed diagnostic panel; no population inference or independent-axis N.'}
    for field, key, pred in [('kind', 'by_kind', lambda r: True), ('variant', 'by_variant', lambda r: r['kind'] == 'SYNTHETIC'),
                             ('base_id', 'by_synthetic_base', lambda r: r['kind'] == 'SYNTHETIC'),
                             ('source_root', 'by_real_source_root', lambda r: r['kind'] == 'REAL'),
                             ('stage', 'by_stage', lambda r: True), ('source_role', 'by_role', lambda r: True)]:
        for value in sorted({r[field] for r in labels if pred(r)}):
            report[key][value] = count_rows(selected(lambda r: pred(r) and r[field] == value))
    for axis in AXES:
        tally = counts(scores[r['judgment_id']]['axis_match'][axis] for r in labels)
        tally.update(false_positive=0, false_negative=0, unresolved=0, error_or_missing=0,
                     reference_ok=sum(r['expected'][axis] == 'OK' for r in labels),
                     reference_violation=sum(r['expected'][axis] == 'VIOLATION' for r in labels))
        for row in labels:
            s = scores[row['judgment_id']]
            if not s['format_valid']:
                tally['error_or_missing'] += 1
            else:
                verdict = s['answer']['checks'][axis]['verdict']
                tally['unresolved'] += verdict == 'UNRESOLVED'
                tally['false_positive'] += verdict == 'VIOLATION' and row['expected'][axis] == 'OK'
                tally['false_negative'] += verdict == 'OK' and row['expected'][axis] == 'VIOLATION'
        report['axes'][axis] = tally
    clean = selected(lambda r: r['all_axes_ok'])
    require(len(clean) == 29, '29_CLEAN_CONTROLS')
    report['clean_controls'] = count_rows(clean)
    conditions = [('all_cases', report['cases'], 60), ('real', report['by_kind']['REAL'], 30),
                  ('synthetic', report['by_kind']['SYNTHETIC'], 30), ('clean_controls', report['clean_controls'], 29)]
    for variant, tally in report['by_variant'].items():
        if not variant.startswith(('V0_', 'V6_')):
            conditions.append((variant, tally, 3))
    bounds = [{'condition': name, 'lower': tally['match'], 'upper': tally['match'] + tally['unknown'],
               'required': target, 'planned': tally['planned']} for name, tally, target in conditions]
    status = ('NOT_MET' if any(b['upper'] < b['required'] for b in bounds) else
              'MET_IN_FIXED_PANEL' if all(b['lower'] >= b['required'] for b in bounds) else 'INCONCLUSIVE')
    report['calibration'] = {'status': status, 'bounds': bounds, 'authorizes_automatic_intervention': False}
    review = [r['judgment_id'] for r in labels if scores[r['judgment_id']]['case_match'] is not True]
    normal = sorted((r['judgment_id'] for r in clean if scores[r['judgment_id']]['case_match'] is True),
                    key=lambda sid: sha256(('2026092808|reason-review|' + sid).encode()).hexdigest())[:8]
    report['reason_review'] = {'status': 'PENDING_OFFLINE_REVIEW', 'mismatch_or_unknown': review,
                               'normal_match_sample': normal, 'changes_primary_labels': False}
    return report
