"""RD01 frozen offline materials, parser and finite-sample analysis. No transport."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json
import random
import re

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'study2/designs/record-decision-01-20260918'
SOURCE = ROOT / 'study2/runs/shared-update-01-prepared-20260918'
ARMS = ('WITH_RULE', 'RECORD_ONLY')
SEED = 2026091806
REMOVE = '全体案内は、A/B両範囲でALLと確認できる唯一の方法をPAPER/DIGITALから選びます。片方が不明、二方法ともALL、どちらも成立しない場合はUNKNOWNです。必ず正解が一つあるとは仮定しません。'
LIMITS = dict(logical_requests=32, physical_requests=36, active_seconds=1800,
              attempt_seconds=180, reserve_seconds=200, concurrency=1,
              overload_retries_total=4, overload_retries_per_slot=1,
              input_bytes=32768, output_bytes=4096)
METRICS = ('H', 'V', 'BOTH_UNKNOWN', 'ANY_UNKNOWN', 'I', 'O', 'J')
FIELDS = ('customer.subject', 'customer.animal', 'customer.origin_id',
          'coverage.observer', 'coverage.paper', 'coverage.digital', 'coverage.origin_id')

def canon(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')

def materials():
    out = []
    for i in range(1, 5):
        for role in ('A', 'B'):
            old_id = f'SU01-G{i:02}-ENCODE-{role}'
            path = SOURCE / 'requests' / (old_id + '-packet.json')
            packet = json.loads(path.read_text())
            assert set(packet) == {'instructions', 'input'}
            assert packet['instructions'].count(REMOVE) == 1
            data = json.loads(packet['input'].split('\n資料JSON:\n', 1)[1])
            assert data['holder'] == role
            c, o = data['records']
            assert c['record_id'] == 'CUSTOMER' and o['record_id'] == 'OBSERVATION'
            assert c['author'] == o['author'] == role
            truth = dict(customer=c['body'], coverage=o['body'])
            stratum = 'ALL_ALL' if o['body']['paper'] == o['body']['digital'] == 'ALL' else 'MIXED'
            out.append(dict(id=f'RD01-G{i:02}-{role}', group=f'RD01-G{i:02}', role=role,
                            stratum=stratum, source_id=old_id,
                            source_packet=str(path.relative_to(ROOT)), packet=packet, truth=truth))
    return out

def allocation(cases):
    rng = random.Random(SEED)
    groups = sorted({c['group'] for c in cases}); rng.shuffle(groups)
    first = []
    for index, group in enumerate(groups):
        batch = [c for c in cases if c['group'] == group]; rng.shuffle(batch)
        for case in batch:
            # Each stratum has two orders in wave 1; every case reverses in wave 2.
            arms = ARMS if index % 2 == 0 else ARMS[::-1]
            for arm in arms:
                first.append(dict(case=case['id'], group=group, stratum=case['stratum'], arm=arm))
    slots = []
    for rep, wave in ((1, first), (2, first[::-1])):
        for row in wave:
            slots.append(dict(row, id=f"{row['case']}-{row['arm']}-R{rep}", repetition=rep,
                              position=len(slots) + 1, parents=[]))
    return slots

def packet(case, arm):
    assert arm in ARMS
    value = deepcopy(case['packet'])
    if arm == 'RECORD_ONLY':
        value['instructions'] = value['instructions'].replace(REMOVE, '', 1)
    return value

def parse(raw):
    def unique(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError('duplicate key')
        return result
    def invalid(_):
        raise ValueError('non-JSON constant')
    def keys(v, expected):
        return type(v) is dict and set(v) == set(expected)
    def label(v, allowed):
        return type(v) is str and v in allowed
    def ref(v):
        return type(v) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,31}', v) is not None
    try:
        if type(raw) is not str or len(raw.encode('utf-8')) > LIMITS['output_bytes']:
            return None
        obj = json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)
        if not keys(obj, ('private_note',)) or not keys(obj['private_note'], ('customer', 'coverage')):
            return None
        note = obj['private_note']; c, o = note['customer'], note['coverage']
        if not keys(c, ('subject', 'animal', 'origin_id')) or not keys(o, ('observer', 'paper', 'digital', 'origin_id')):
            return None
        if not label(c['subject'], ('A', 'B', 'UNKNOWN')) or not label(o['observer'], ('A', 'B', 'UNKNOWN')):
            return None
        if not label(c['animal'], ('DOG', 'CAT', 'UNKNOWN')):
            return None
        if not all(label(o[k], ('ALL', 'NOT_ALL', 'UNKNOWN')) for k in ('paper', 'digital')):
            return None
        if not ref(c['origin_id']) or not ref(o['origin_id']):
            return None
        return note
    except (ValueError, TypeError, RecursionError):
        return None

def score(raw, truth):
    note = parse(raw)
    state = 'UNOBSERVED' if raw is None else 'STRUCTURAL_MISSING' if note is None else 'VALID'
    if note is None:
        return dict(status=state, metrics={k: None for k in METRICS},
                    fields={k: None for k in FIELDS}, parsed=None)
    o, t = note['coverage'], truth['coverage']
    metrics = dict(H=o == t, V=all(o[k] == t[k] for k in ('paper', 'digital')),
                   BOTH_UNKNOWN=o['paper'] == o['digital'] == 'UNKNOWN',
                   ANY_UNKNOWN='UNKNOWN' in (o['paper'], o['digital']),
                   I=note['customer'] == truth['customer'],
                   O=all(o[k] == t[k] for k in ('observer', 'origin_id')), J=note == truth)
    fields = {f: note[f.split('.')[0]][f.split('.')[1]] == truth[f.split('.')[0]][f.split('.')[1]] for f in FIELDS}
    return dict(status=state, metrics=metrics, fields=fields, parsed=note)

def bounds(values):
    assert values and all(x is None or type(x) is bool for x in values)
    good = sum(x is True for x in values); missing = sum(x is None for x in values)
    return [good / len(values), (good + missing) / len(values)]

def analyze(cases, slots, raw_by_id):
    expected = {s['id'] for s in slots}
    if len(slots) != 32 or len(expected) != 32 or set(raw_by_id) != expected:
        raise ValueError('Expected exactly the planned 32 IDs; missing slots must be explicit null.')
    lookup = {c['id']: c for c in cases}; rows = []
    for slot in slots:
        rows.append(dict(slot, **score(raw_by_id[slot['id']], lookup[slot['case']]['truth'])))
    summaries = {}
    for stratum in ('ALL_ALL', 'MIXED', 'ALL'):
        summaries[stratum] = {}
        for arm in ARMS:
            part = [r for r in rows if r['arm'] == arm and (stratum == 'ALL' or r['stratum'] == stratum)]
            summaries[stratum][arm] = dict(planned=len(part), statuses=dict(Counter(r['status'] for r in part)),
                metrics={k: bounds([r['metrics'][k] for r in part]) for k in METRICS},
                fields={k: bounds([r['fields'][k] for r in part]) for k in FIELDS})
    w = summaries['ALL_ALL']['WITH_RULE']['metrics']['H']
    r = summaries['ALL_ALL']['RECORD_ONLY']['metrics']['H']
    delta = [r[0] - w[1], r[1] - w[0]]
    status = 'LOCAL_POSITIVE' if delta[0] > 0 else 'NOT_MET_IN_FIXED_SAMPLE' if delta[1] <= 0 else 'UNRESOLVED_MISSINGNESS'
    sign = ('POSITIVE' if delta[0] > 0 else 'NEGATIVE' if delta[1] < 0 else 'ZERO' if delta == [0, 0] else 'UNRESOLVED')
    all_perfect = all(summaries['ALL'][a]['metrics']['J'] == [1, 1] for a in ARMS)
    adopt = status == 'LOCAL_POSITIVE' and summaries['ALL']['RECORD_ONLY']['metrics']['J'] == [1, 1]
    gate = 'CANDIDATE_FOR_SHARED_DESIGN' if adopt else 'CURRENT_CEILING' if all_perfect else 'RETURN_TO_CHECKPOINT'
    paired = []; repeats = []
    for case in cases:
        cs = [x for x in rows if x['case'] == case['id']]
        differences = []
        for rep in (1, 2):
            by_arm = {x['arm']: x for x in cs if x['repetition'] == rep}
            values = {a: by_arm[a]['metrics']['H'] for a in ARMS}
            differences.append(None if None in values.values() else int(values['RECORD_ONLY']) - int(values['WITH_RULE']))
        paired.append(dict(case=case['id'], stratum=case['stratum'], repetition_H_differences=differences,
                           H_by_arm={a: bounds([x['metrics']['H'] for x in cs if x['arm'] == a]) for a in ARMS}))
        for arm in ARMS:
            two = [x for x in cs if x['arm'] == arm]
            observed = all(x['status'] == 'VALID' for x in two)
            repeats.append(dict(case=case['id'], arm=arm, both_observed=observed,
                                same_note=(two[0]['parsed'] == two[1]['parsed']) if observed else None))
    return dict(protocol='RECORD-DECISION-01', kind='FIXED_SAMPLE_DESCRIPTIVE',
                summaries=summaries, primary_delta_H=delta, prediction_status=status,
                sign=sign, next_design_gate=gate, case_pairs=paired, repeats=repeats, rows=rows)
