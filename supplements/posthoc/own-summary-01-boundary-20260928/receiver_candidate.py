"""Offline candidate: quarantine one known input-only field; never repair meaning."""
from copy import deepcopy
from hashlib import sha256
import own_summary_01_design as sc

PROTOCOL = 'OS01-OUTPUT-BOUNDARY-OFFLINE/v0.1'
POINTER = '/local/own_experience_summary'


def receive(raw, stage, finish='EOS'):
    """No condition label, expected answer, or experience data is accepted here."""
    result = {'protocol': PROTOCOL, 'status': 'REJECT', 'reason': None,
              'raw_sha256': sha256(raw).hexdigest(), 'candidate_bytes': None,
              'quarantine': [], 'semantic_repair': False}
    norm = sc.envelope.normalize(raw, finish)
    candidate = norm.pop('normalized_bytes')
    result['envelope'] = norm
    if candidate is None:
        result['reason'] = norm['reason']
        return result
    if stage not in sc.SCHEMAS:
        result['reason'] = 'UNKNOWN_STAGE'
        return result
    original = sc.strict_json.parse(candidate)
    errors = sc.shape(original, sc.SCHEMAS[stage])
    result['original_schema_errors'] = errors
    if not errors:
        result.update(status='UNCHANGED', reason='OLD_SCHEMA_VALID', candidate_bytes=candidate)
        return result
    if (stage != 'USE' or type(original) is not dict
            or type(original.get('local')) is not dict
            or 'own_experience_summary' not in original['local']):
        result['reason'] = 'OUTSIDE_SINGLE_FIELD_RULE'
        return result
    projected = deepcopy(original)
    excluded = projected['local'].pop('own_experience_summary')
    remaining = sc.shape(projected, sc.SCHEMAS['USE'])
    if remaining:
        result.update(reason='OTHER_SCHEMA_ERRORS_REMAIN', remaining_schema_errors=remaining)
        return result
    result.update(status='QUARANTINED', reason='KNOWN_INPUT_ONLY_FIELD',
                  candidate_bytes=sc.enc(projected),
                  quarantine=[{'pointer': POINTER, 'value': excluded,
                               'value_sha256': sha256(sc.enc(excluded)).hexdigest(),
                               'trusted': False, 'for_downstream': False}])
    return result
