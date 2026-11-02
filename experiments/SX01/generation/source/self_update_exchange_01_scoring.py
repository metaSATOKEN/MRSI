"""SX01 approved pure functions; AST-verbatim from frozen design, no build entry point."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import owner_recency_01_scoring as policy
import update_readout_01_scoring as base
PROTOCOL="SELF-UPDATE-EXCHANGE-01/v1"
STAGES=("SELF","EXCHANGE","DELAY","READ")
enc=base.enc

def digest(value):
    return sha256(enc(value)).hexdigest()

def other(role):
    if role not in ('A', 'B'):
        raise ValueError('ROLE')
    return 'B' if role == 'A' else 'A'

def initial_memory(case, role):
    other(role)
    return {'private_note': {'customer': deepcopy(case['customers'][role]), 'coverage': deepcopy(case['old_rows'][role])}, 'shared_note': {'coverage': deepcopy(case['old_rows'])}}

def expected_memory(case, role, stage):
    """Scoring oracle; never call from payload/materialization of later stages."""
    if stage not in STAGES:
        raise ValueError('STAGE')
    shared = deepcopy(case['new_rows'])
    if stage == 'SELF':
        shared[other(role)] = deepcopy(case['old_rows'][other(role)])
    return {'private_note': {'customer': deepcopy(case['customers'][role]), 'coverage': deepcopy(case['new_rows'][role])}, 'shared_note': {'coverage': shared}}

def update_payload(case, role, stage, previous=None, peer=None):
    """Only actual saved notes supply later state. No gold/initial reset fallback."""
    partner = other(role)
    if stage == 'SELF':
        if previous is not None or peer is not None:
            raise ValueError('SELF_HAS_NO_PARENT')
        memory = initial_memory(case, role)
        notice = deepcopy(case['new_rows'][role])
    elif stage in ('EXCHANGE', 'DELAY'):
        if previous is None:
            raise ValueError('DEPENDENCY_MISSING:OWN')
        memory = deepcopy(previous)
        if stage == 'EXCHANGE':
            if peer is None:
                raise ValueError('DEPENDENCY_MISSING:PEER')
            notice = deepcopy(peer['private_note']['coverage'])
            if notice['observer'] != partner:
                raise ValueError('EXCHANGE_OWNER_CONTRACT')
        else:
            if peer is not None:
                raise ValueError('DELAY_HAS_NO_PEER_PARENT')
            target = role if case['delay_relation'] == 'SELF' else partner
            notice = deepcopy(case['old_rows'][target])
    else:
        raise ValueError('NOT_UPDATE_STAGE')
    records = [{'record_id': 'PRIVATE', 'body': memory['private_note']}, {'record_id': 'GROUP', 'body': memory['shared_note']}]
    entries = [('PRIVATE.coverage', memory['private_note']['coverage']), ('GROUP.coverage.A', memory['shared_note']['coverage']['A']), ('GROUP.coverage.B', memory['shared_note']['coverage']['B']), ('NOTICE', notice)]
    entries.sort(key=lambda pair: digest([case['id'], role, stage, pair[0]]))
    return {'holder': role, 'scene': case['scene'], 'item': case['item'], 'records': records, 'incoming_notice': notice, 'row_catalog': [{'row_id': 'C' + str(i + 1), 'location': location, 'row': deepcopy(row)} for i, (location, row) in enumerate(entries)]}

def derive_update(raw, payload, schema, finish_reason='EOS'):
    """Accept shape, then apply frozen G1P1. No case, stage or expected-state argument."""
    receipt = policy.receive(raw, 'UPDATE', finish_reason)
    metadata = {k: v for k, v in receipt.items() if k != 'normalized_bytes'}
    result = {'receipt': metadata, 'normalized_bytes': receipt['normalized_bytes'], 'proposal': None, 'memory': None, 'trace': None, 'error': None}
    if receipt['normalized_bytes'] is None:
        result['error'] = 'RECEIVE'
        return result
    proposal = base.parse(receipt['normalized_bytes'])
    if base.shape(proposal, schema):
        result['error'] = 'SCHEMA'
        return result
    result['proposal'] = proposal
    try:
        result['memory'], result['trace'] = policy.transform(proposal, payload, 'G1P1', schema)
    except (ValueError, TypeError, KeyError) as exc:
        result['error'] = 'INPUT_CONTRACT:' + str(exc)
    return result

def score_memory(memory, case, role, stage):
    if memory is None:
        return {'format_valid': None, 'customer': None, 'self_row': None, 'partner_row': None, 'shared': None, 'joint': None}
    want = expected_memory(case, role, stage)
    return {'format_valid': True, 'customer': memory['private_note']['customer'] == want['private_note']['customer'], 'self_row': memory['private_note']['coverage'] == want['private_note']['coverage'], 'partner_row': memory['shared_note']['coverage'][other(role)] == want['shared_note']['coverage'][other(role)], 'shared': memory['shared_note'] == want['shared_note'], 'joint': memory == want}

def read_messages(design, case, role, memory):
    if memory is None:
        raise ValueError('DEPENDENCY_MISSING:READ')
    payload = {'holder': role, 'scene': case['scene'], 'item': case['item'], 'records': [{'record_id': 'PRIVATE', 'body': deepcopy(memory['private_note'])}, {'record_id': 'GROUP', 'body': deepcopy(memory['shared_note'])}]}
    return [{'role': 'system', 'content': design['read_prompt']}, {'role': 'user', 'content': '\n資料JSON:\n' + enc(payload).decode()}]

def score_read(raw, memory, case, role, schema, finish_reason='EOS'):
    c = {'expected_memory': expected_memory(case, role, 'READ'), 'latest_channel': base.compute_channel(case['new_rows'])}
    score = policy.score_read(raw, memory, c, schema, finish_reason)
    score['joint'] = score['four_exact'] is True and score['channel_latest'] is True if score.get('format_valid') is True else None
    return score

def summarize(design, outcomes):
    """Whole-pair trajectories; missing structure stays unresolved, bad components retained."""
    valid_ids = {s['id'] for s in design['allocation']}
    if set(outcomes) - valid_ids:
        raise ValueError('UNEXPECTED_RESPONSE')
    paths = []
    for run in design['runs']:
        values = [outcomes.get(run['id'] + '-' + stage + '-' + role, {}) for stage in STAGES for role in ('A', 'B')]
        complete = all((v.get('format_valid') is True for v in values))
        success = all((v.get('joint') is True for v in values)) if complete else None
        paths.append({'id': run['id'], 'case': run['case'], 'replicate': run['replicate'], 'success': success})

    def counts(rows):
        return base.counts([p['success'] for p in rows])
    total = counts(paths)
    reps = {str(r): counts([p for p in paths if p['replicate'] == r]) for r in (1, 2)}
    tests = [(total, 14)] + [(c, 7) for c in reps.values()]
    status = 'MET' if all((c['correct'] >= n for c, n in tests)) else 'NOT_MET' if any((c['correct'] + c['unresolved'] < n for c, n in tests)) else 'INCONCLUSIVE'
    cases = {c['id']: c for c in design['cases']}
    strata = {key: {value: counts([p for p in paths if cases[p['case']][key] == value]) for value in sorted({c[key] for c in design['cases']})} for key in ('direction', 'delay_relation', 'higher_revision_owner')}
    return {'materials': 8, 'pair_runs': 16, 'response_slots': 128, 'path': total, 'by_repeat': reps, 'strata': strata, 'criterion_status': status, 'paths': paths}

def initial_requests(design):
    cases = {c['id']: c for c in design['cases']}
    return [{'id': s['id'], 'seed': s['seed'], 'messages': [{'role': 'system', 'content': design['update_prompt']}, {'role': 'user', 'content': '\n資料JSON:\n' + enc(update_payload(cases[s['case']], s['role'], 'SELF')).decode()}]} for s in design['allocation'] if s['stage'] == 'SELF']
