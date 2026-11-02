"""Offline-only UR01 JSON-envelope adapter. Never edits raw evidence or values."""
from hashlib import sha256
import readout_split_01_scoring as json_contract

PROTOCOL = 'UR01-ENVELOPE-REFERENCE-v0.1'
PREFIX = b'```json\n'
SUFFIX = b'\n```'
MAX_BYTES = 16384


def normalize(raw, finish_reason='EOS'):
    """Return a byte-preserving candidate and an audit trace; schema checks follow separately."""
    if not isinstance(raw, bytes):
        raise TypeError('RAW_BYTES_REQUIRED')
    result = {'protocol': PROTOCOL, 'status': 'REJECT', 'reason': None,
        'raw_sha256': sha256(raw).hexdigest(), 'raw_bytes': len(raw),
        'normalized_sha256': None, 'normalized_bytes_length': None, 'normalized_bytes': None,
        'removed_prefix_bytes': 0, 'removed_suffix_bytes': 0, 'value_repair': False}
    if finish_reason != 'EOS':
        result.update(status='UNRESOLVED', reason='NON_EOS'); return result
    if len(raw) > MAX_BYTES:
        result['reason'] = 'RAW_BYTES_LIMIT'; return result
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError:
        result['reason'] = 'INVALID_UTF8'; return result
    candidate = raw; status = 'UNCHANGED'
    try:
        json_contract.parse(candidate)
    except (ValueError, UnicodeError, RecursionError):
        if not (raw.startswith(PREFIX) and raw.endswith(SUFFIX)):
            result['reason'] = 'NOT_BARE_JSON_OR_EXACT_ENVELOPE'; return result
        candidate = raw[len(PREFIX):-len(SUFFIX)]
        # Validate the complete interior. No searching for one parseable substring.
        try:
            json_contract.parse(candidate)
        except (ValueError, UnicodeError, RecursionError):
            result['reason'] = 'INVALID_ENVELOPE_INTERIOR'; return result
        status = 'UNWRAPPED'
    result.update(status=status, reason='EXACT_ENVELOPE_ONLY' if status == 'UNWRAPPED' else 'BARE_JSON',
        normalized_bytes=candidate, normalized_sha256=sha256(candidate).hexdigest(), normalized_bytes_length=len(candidate),
        removed_prefix_bytes=len(PREFIX) if status == 'UNWRAPPED' else 0,
        removed_suffix_bytes=len(SUFFIX) if status == 'UNWRAPPED' else 0)
    return result
