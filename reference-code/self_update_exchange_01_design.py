"""SX01 material/contract design. Offline stdlib only; no model or network calls."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

import owner_recency_01_scoring as policy
import update_readout_01_scoring as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study2/designs/self-update-exchange-01-20260925'
PROTOCOL = 'SELF-UPDATE-EXCHANGE-01/v1'
STAGES = ('SELF', 'EXCHANGE', 'DELAY', 'READ')
SOURCE = 'study2/designs/owner-recency-01-20260925/design.json'
SOURCE_SHA = 'd4d72a6cbbb950d2cbddb63d91912d2b716dab3880cc91414205f4750ae40291'
enc = base.enc


def digest(value):
    return sha256(enc(value)).hexdigest()


def other(role):
    if role not in ('A', 'B'):
        raise ValueError('ROLE')
    return 'B' if role == 'A' else 'A'


def initial_memory(case, role):
    other(role)
    return {'private_note': {'customer': deepcopy(case['customers'][role]),
                             'coverage': deepcopy(case['old_rows'][role])},
            'shared_note': {'coverage': deepcopy(case['old_rows'])}}


def expected_memory(case, role, stage):
    """Scoring oracle; never call from payload/materialization of later stages."""
    if stage not in STAGES:
        raise ValueError('STAGE')
    shared = deepcopy(case['new_rows'])
    if stage == 'SELF':
        shared[other(role)] = deepcopy(case['old_rows'][other(role)])
    return {'private_note': {'customer': deepcopy(case['customers'][role]),
                             'coverage': deepcopy(case['new_rows'][role])},
            'shared_note': {'coverage': shared}}


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
    records = [{'record_id': 'PRIVATE', 'body': memory['private_note']},
               {'record_id': 'GROUP', 'body': memory['shared_note']}]
    entries = [('PRIVATE.coverage', memory['private_note']['coverage']),
               ('GROUP.coverage.A', memory['shared_note']['coverage']['A']),
               ('GROUP.coverage.B', memory['shared_note']['coverage']['B']), ('NOTICE', notice)]
    entries.sort(key=lambda pair: digest([case['id'], role, stage, pair[0]]))
    return {'holder': role, 'scene': case['scene'], 'item': case['item'], 'records': records,
            'incoming_notice': notice,
            'row_catalog': [{'row_id': 'C' + str(i + 1), 'location': location, 'row': deepcopy(row)}
                            for i, (location, row) in enumerate(entries)]}


def derive_update(raw, payload, schema, finish_reason='EOS'):
    """Accept shape, then apply frozen G1P1. No case, stage or expected-state argument."""
    receipt = policy.receive(raw, 'UPDATE', finish_reason)
    metadata = {k: v for k, v in receipt.items() if k != 'normalized_bytes'}
    result = {'receipt': metadata, 'normalized_bytes': receipt['normalized_bytes'],
              'proposal': None, 'memory': None, 'trace': None, 'error': None}
    if receipt['normalized_bytes'] is None:
        result['error'] = 'RECEIVE'; return result
    proposal = base.parse(receipt['normalized_bytes'])
    if base.shape(proposal, schema):
        result['error'] = 'SCHEMA'; return result
    result['proposal'] = proposal
    try:
        result['memory'], result['trace'] = policy.transform(proposal, payload, 'G1P1', schema)
    except (ValueError, TypeError, KeyError) as exc:
        result['error'] = 'INPUT_CONTRACT:' + str(exc)
    return result


def score_memory(memory, case, role, stage):
    if memory is None:
        return {'format_valid': None, 'customer': None, 'self_row': None,
                'partner_row': None, 'shared': None, 'joint': None}
    want = expected_memory(case, role, stage)
    return {'format_valid': True,
            'customer': memory['private_note']['customer'] == want['private_note']['customer'],
            'self_row': memory['private_note']['coverage'] == want['private_note']['coverage'],
            'partner_row': memory['shared_note']['coverage'][other(role)] == want['shared_note']['coverage'][other(role)],
            'shared': memory['shared_note'] == want['shared_note'], 'joint': memory == want}


def read_messages(design, case, role, memory):
    if memory is None:
        raise ValueError('DEPENDENCY_MISSING:READ')
    payload = {'holder': role, 'scene': case['scene'], 'item': case['item'],
               'records': [{'record_id': 'PRIVATE', 'body': deepcopy(memory['private_note'])},
                           {'record_id': 'GROUP', 'body': deepcopy(memory['shared_note'])}]}
    return [{'role': 'system', 'content': design['read_prompt']},
            {'role': 'user', 'content': '\n資料JSON:\n' + enc(payload).decode()}]


def score_read(raw, memory, case, role, schema, finish_reason='EOS'):
    c = {'expected_memory': expected_memory(case, role, 'READ'),
         'latest_channel': base.compute_channel(case['new_rows'])}
    score = policy.score_read(raw, memory, c, schema, finish_reason)
    score['joint'] = (score['four_exact'] is True and score['channel_latest'] is True
                      if score.get('format_valid') is True else None)
    return score


def summarize(design, outcomes):
    """Whole-pair trajectories; missing structure stays unresolved, bad components retained."""
    valid_ids = {s['id'] for s in design['allocation']}
    if set(outcomes) - valid_ids:
        raise ValueError('UNEXPECTED_RESPONSE')
    paths = []
    for run in design['runs']:
        values = [outcomes.get(run['id'] + '-' + stage + '-' + role, {})
                  for stage in STAGES for role in ('A', 'B')]
        complete = all(v.get('format_valid') is True for v in values)
        success = all(v.get('joint') is True for v in values) if complete else None
        paths.append({'id': run['id'], 'case': run['case'], 'replicate': run['replicate'], 'success': success})
    def counts(rows):
        return base.counts([p['success'] for p in rows])
    total = counts(paths)
    reps = {str(r): counts([p for p in paths if p['replicate'] == r]) for r in (1, 2)}
    tests = [(total, 14)] + [(c, 7) for c in reps.values()]
    status = 'MET' if all(c['correct'] >= n for c, n in tests) else 'NOT_MET' if any(
        c['correct'] + c['unresolved'] < n for c, n in tests) else 'INCONCLUSIVE'
    cases = {c['id']: c for c in design['cases']}
    strata = {key: {value: counts([p for p in paths if cases[p['case']][key] == value])
                   for value in sorted({c[key] for c in design['cases']})}
              for key in ('direction', 'delay_relation', 'higher_revision_owner')}
    return {'materials': 8, 'pair_runs': 16, 'response_slots': 128, 'path': total,
            'by_repeat': reps, 'strata': strata, 'criterion_status': status, 'paths': paths}


def build_design():
    source = ROOT / SOURCE
    if sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('SOURCE_CHANGED')
    old = json.loads(source.read_bytes())
    names = ['夜空観察会', '折り紙相談会', '水辺学習会', '昆虫標本会',
             '演劇体験会', '地図制作会', '木工相談会', '防災ラジオ講座']
    cases = []
    for i in range(8):
        cid = f'SX01-C{i+1:02d}'
        direction = 'PAPER_TO_DIGITAL' if i // 4 == 0 else 'DIGITAL_TO_PAPER'
        delay = 'SELF' if (i // 2) % 2 == 0 else 'PARTNER'
        high = 'A' if i % 2 == 0 else 'B'
        # Two distinct roles: restrictive -> unrestricted; unrestricted -> restrictive.
        first, second = ('A', 'B') if i % 2 == 0 else ('B', 'A')
        old_values = {first: ('ALL', 'NOT_ALL'), second: ('ALL', 'ALL')}
        new_values = {first: ('ALL', 'ALL'), second: ('NOT_ALL', 'ALL')}
        if direction == 'DIGITAL_TO_PAPER':
            old_values = {o: (v[1], v[0]) for o, v in old_values.items()}
            new_values = {o: (v[1], v[0]) for o, v in new_values.items()}
        old_rows, new_rows, customers = {}, {}, {}
        for role in ('A', 'B'):
            revision = 10 * (i + 1) + (7 if role == high else 2)
            def row(values, age, rev):
                return {'observer': role, 'paper': values[0], 'digital': values[1], 'revision': rev,
                        'origin_id': 'X' + digest([PROTOCOL, cid, role, age])[:16].upper()}
            old_rows[role] = row(old_values[role], 'OLD', revision)
            new_rows[role] = row(new_values[role], 'NEW', revision + 1)
            customers[role] = {'subject': role, 'animal': 'DOG' if role == high else 'CAT',
                               'origin_id': 'X' + digest([PROTOCOL, cid, role, 'CUSTOMER'])[:16].upper()}
        cases.append({'id': cid, 'scene': names[i] + '・試設会場' + str(i+1), 'item': '個別の案内カード',
                      'direction': direction, 'delay_relation': delay, 'higher_revision_owner': high,
                      'old_rows': old_rows, 'new_rows': new_rows, 'customers': customers})
    runs, allocation = [], []
    ordered = sorted(cases, key=lambda c: digest([PROTOCOL, 'order', c['id']]))
    for rep in (1, 2):
        for index, case in enumerate(ordered if rep == 1 else ordered[::-1]):
            rid = case['id'] + f'-R{rep}'
            runs.append({'id': rid, 'case': case['id'], 'replicate': rep})
            for stage_index, stage in enumerate(STAGES):
                roles = ('A', 'B') if (index + rep + stage_index) % 2 == 0 else ('B', 'A')
                for role in roles:
                    sid = rid + '-' + stage + '-' + role
                    parents = [] if stage == 'SELF' else [rid + '-' + STAGES[stage_index-1] + '-' + role]
                    if stage == 'EXCHANGE':
                        parents.append(rid + '-SELF-' + other(role))
                    allocation.append({'id': sid, 'run': rid, 'case': case['id'], 'replicate': rep,
                                       'role': role, 'stage': stage, 'parents': parents,
                                       'seed': int(digest([sid, 'generation'])[:8], 16) % 2**31})
    pins = {SOURCE: SOURCE_SHA}
    for name in ('owner_recency_01_scoring.py', 'update_readout_01_scoring.py', 'update_readout_01_envelope.py',
                 'saved_readout_01_scoring.py', 'readout_split_01_scoring.py'):
        pins['scripts/' + name] = sha256((ROOT / 'scripts' / name).read_bytes()).hexdigest()
    return {'protocol': PROTOCOL, 'status': 'DESIGN_FROZEN_NO_MODEL_GENERATION', 'cases': cases,
            'runs': runs, 'allocation': allocation, 'source_pins': pins, 'condition': 'G1P1_FIXED',
            'update_prompt': old['update_prompt'], 'update_schema': old['update_schema'],
            'read_prompt': old['read_prompt'], 'read_schema': old['read_schema'], 'model': old['model'],
            'normalization': deepcopy(old['normalization']),
            'limits': {'updates': 96, 'reads': 32, 'max_generations': 128, 'seconds_including_setup': 5400,
                       'automatic_regenerations': 0, 'cloud_drive': 'not_used', 'retention': 'private_no_deletion_deadline'},
            'decision_rules': {'complete_pair_paths': 14, 'each_repeat': 7,
                               'p_value': None, 'confidence_interval': None}}


def initial_requests(design):
    cases = {c['id']: c for c in design['cases']}
    return [{'id': s['id'], 'seed': s['seed'], 'messages': [
        {'role': 'system', 'content': design['update_prompt']},
        {'role': 'user', 'content': '\n資料JSON:\n' + enc(update_payload(cases[s['case']], s['role'], 'SELF')).decode()}]}
        for s in design['allocation'] if s['stage'] == 'SELF']


def freeze():
    design = build_design()
    OUT.mkdir(parents=True, exist_ok=False)
    def write(name, value):
        (OUT / name).write_bytes(enc(value) + b'\n')
    write('design.json', design)
    write('initial-requests.json', initial_requests(design))
    write('schemas.json', {'UPDATE': design['update_schema'], 'READ': design['read_schema']})
    (OUT / 'prompt-update.txt').write_text(design['update_prompt'])
    (OUT / 'prompt-read.txt').write_text(design['read_prompt'])
    for name in ('self_update_exchange_01_design.py', 'owner_recency_01_scoring.py', 'update_readout_01_scoring.py',
                 'update_readout_01_envelope.py', 'saved_readout_01_scoring.py', 'readout_split_01_scoring.py'):
        (OUT / name).write_bytes((ROOT / 'scripts' / name).read_bytes())
    (OUT / 'README.md').write_text('# SELF-UPDATE-EXCHANGE-01 固定設計\n\n'
        '未使用の合成8ペア×2反復、2役のSELF→EXCHANGE→DELAY→READ。最大128生成。\n'
        '初回32入力だけが固定済み。後続96入力は実保存物から構築し、正解による補完なし。\n'
        '人物別最新版複製はG1P1固定。案内は実READ四値から計算する。実モデル未実行。\n')
    write('MANIFEST.json', {p.name: sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()})
    print(json.dumps({'path': str(OUT), 'design_sha256': sha256((OUT/'design.json').read_bytes()).hexdigest(),
                      'cases': len(design['cases']), 'slots': len(design['allocation'])}))


if __name__ == '__main__':
    freeze()
