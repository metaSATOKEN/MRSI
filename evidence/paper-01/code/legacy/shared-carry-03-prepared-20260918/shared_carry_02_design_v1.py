"""SC02 offline design, deterministic projection and scoring. No transport/auth."""
from copy import deepcopy
import json
import random
import shared_update_design_v1 as su
from record_decision_design_v1 import REMOVE

ROLES = ('A', 'B')
ARMS = ('BOTH', 'PRIVATE')
SEED = 2026091807
LIMITS = dict(logical_requests=48, physical_requests=52, active_seconds=2700,
              attempt_seconds=180, reserve_seconds=200, concurrency=1,
              overload_retries_total=4, overload_retries_per_slot=1,
              input_bytes=32768, output_bytes=4096)
PROMPTS = {k: su.PROMPTS[k] for k in ('ENCODE', 'DRAFT', 'EDIT', 'PROBE')}
assert PROMPTS['ENCODE'].count(REMOVE) == 1
PROMPTS['ENCODE'] = PROMPTS['ENCODE'].replace(REMOVE, '', 1)
PROMPTS['PROBE'] = PROMPTS['PROBE'].replace('保存されたPRIVATEとGROUPだけから、', '今回提示された保存ノートだけから、', 1).replace(
    '今直接読めるのはPRIVATE/GROUPだけです。',
    '今直接読める参照名は、今回資料のrecordsに存在するrecord_idだけです。見えていない記録は引用しません。', 1)
canon = su.canon
parse = su.parse
sid = su.sid

def materials():
    groups = []
    for source in su.materials():
        g = {k: deepcopy(source[k]) for k in ('group', 'scene', 'item', 'writer', 'editor', 'originals')}
        g['group'] = g['group'].replace('SU01', 'SC02')
        g['best_channel'] = source['initial_channel']
        groups.append(g)
    return groups

def allocation(groups):
    rng = random.Random(SEED); slots = []
    for stage in ('ENCODE', 'DRAFT', 'EDIT'):
        batch = []
        for g in groups:
            roles = ROLES if stage == 'ENCODE' else (g['writer' if stage == 'DRAFT' else 'editor'],)
            for role in roles:
                parents = [] if stage == 'ENCODE' else [sid(g, 'ENCODE', r) for r in ROLES]
                if stage == 'EDIT': parents.append(sid(g, 'DRAFT', g['writer']))
                batch.append(dict(id=sid(g, stage, role), group=g['group'], stage=stage, role=role,
                                  arm=None, repetition=None, parents=parents))
        rng.shuffle(batch); slots.extend(batch)
    pairs = [(g, r) for g in groups for r in ROLES]; rng.shuffle(pairs); wave = []
    for i, (g, role) in enumerate(pairs):
        for arm in ARMS if i % 2 == 0 else ARMS[::-1]:
            wave.append(dict(group=g['group'], stage='PROBE', role=role, arm=arm,
                             parents=[sid(g, 'ENCODE', r) for r in ROLES] + [sid(g, 'EDIT', g['editor'])]))
    for rep, batch in ((1, wave), (2, wave[::-1])):
        for original in batch:
            s = deepcopy(original); g = next(g for g in groups if g['group'] == s['group'])
            s.update(id=sid(g, 'PROBE', s['role'], s['arm'], rep), repetition=rep); slots.append(s)
    for i, s in enumerate(slots): s['position'] = i + 1
    return slots

def payload(g, s, parsed):
    if any(not su.continuable(parsed.get(p, {'missing': None})) for p in s['parents']): return None
    t, r = s['stage'], s['role']; rec = su.record
    if t == 'ENCODE':
        records = [rec('CUSTOMER', r, g['originals'][r]['customer']), rec('OBSERVATION', r, g['originals'][r]['coverage'])]
    elif t in ('DRAFT', 'EDIT'):
        records = [rec('OBS_' + role, role, parsed[sid(g, 'ENCODE', role)]['private_note']['coverage']) for role in ROLES]
        if t == 'EDIT': records.append(rec('DRAFT', g['writer'], parsed[sid(g, 'DRAFT', g['writer'])]['shared_note']))
    else:
        records = [rec('PRIVATE', r, parsed[sid(g, 'ENCODE', r)]['private_note'])]
        if s['arm'] == 'BOTH': records.append(rec('GROUP', g['editor'], parsed[sid(g, 'EDIT', g['editor'])]['shared_note']))
    return dict(scene=g['scene'], item=g['item'], holder=r, records=records)

def input_text(g, s, parsed):
    packet = payload(g, s, parsed)
    return None if packet is None else PROMPTS[s['stage']] + '\n資料JSON:\n' + canon(packet)

def ideal(g, s):
    t, r = s['stage'], s['role']; own = deepcopy(g['originals'][r])
    if t == 'ENCODE': return dict(private_note=own)
    cov = {role: deepcopy(g['originals'][role]['coverage']) for role in ROLES}
    origins = [cov[role]['origin_id'] for role in ROLES]
    if t in ('DRAFT', 'EDIT'):
        return dict(shared_note=dict(coverage=cov, channel=g['best_channel'], channel_read_refs=['OBS_A', 'OBS_B'], channel_origin_ids=origins))
    both = s['arm'] == 'BOTH'
    return dict(mascot=own['customer']['animal'], mascot_read_refs=['PRIVATE'], mascot_origin_ids=[own['customer']['origin_id']],
                channel=g['best_channel'] if both else 'UNKNOWN', channel_read_refs=['GROUP'] if both else [], channel_origin_ids=origins if both else [])

def all3(values): return False if False in values else None if None in values else True
def bounds(values): return [values.count(True) / len(values), (len(values) - values.count(False)) / len(values)]
def equivalent(a, b):
    if type(a) is not type(b): return False
    if isinstance(a, dict): return set(a) == set(b) and all(equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list): return len(a) == len(b) and len(set(a)) == len(a) and set(a) == set(b)
    return a == b
def no_ref(value):
    return {k: v for k, v in value.items() if k not in ('channel_read_refs', 'channel_origin_ids')}
def matches(value, target): return None if value is None else equivalent(value, target)

def supported(p, packet, field):
    value, direct, origins = [p[field + suffix] for suffix in ('', '_read_refs', '_origin_ids')]
    if value is None or direct is None or origins is None or packet is None: return None
    if value == 'UNKNOWN': return direct == origins == []
    records = {r['record_id']: r['body'] for r in packet['records']}
    name = 'PRIVATE' if field == 'mascot' else 'GROUP'
    if name not in records: return False
    if direct != [name]: return False
    if field == 'mascot':
        c = records[name]['customer']
        return c['subject'] == packet['holder'] and c['animal'] == value and equivalent(origins, [c['origin_id']])
    cov = records[name]['coverage']
    return all(cov[r]['observer'] == r for r in ROLES) and su.best(cov) == value and equivalent(origins, [cov[r]['origin_id'] for r in ROLES])

def analyse(groups, slots, outputs):
    assert set(outputs) == {s['id'] for s in slots}
    parsed = {s['id']: parse(outputs[s['id']], s['stage']) for s in slots}
    gm = {g['group']: g for g in groups}; rows = []; formation = {}; score = {}
    for s in slots:
        g = gm[s['group']]; p = parsed[s['id']]; expected = ideal(g, s); packet = payload(g, s, parsed)
        full = all3([matches(p[k], expected[k]) for k in expected])
        row = dict(id=s['id'], full=full, dependency_unissued=packet is None)
        if s['stage'] == 'PROBE':
            support = all3([supported(p, packet, f) for f in ('mascot', 'channel')])
            row.update(full=all3([full, support]), input_support=support,
                       I=matches(p['mascot'], g['originals'][s['role']]['customer']['animal']),
                       G=matches(p['channel'], g['best_channel']), unknown_channel=matches(p['channel'], 'UNKNOWN'))
        elif s['stage'] in ('DRAFT', 'EDIT'):
            row['no_ref'] = None if p['shared_note'] is None else equivalent(no_ref(p['shared_note']), no_ref(expected['shared_note']))
        rows.append(row); score[s['id']] = row
    E = []; E_no = []; group_rows = []
    for g in groups:
        notes = [score[sid(g, 'ENCODE', r)]['full'] for r in ROLES]; edit = score[sid(g, 'EDIT', g['editor'])]
        F = all3(notes + [edit['full']]); F_no = all3(notes + [edit['no_ref']]); formation[g['group']] = F
        es = []; ens = []
        for rep in (1, 2):
            ps = [score[sid(g, 'PROBE', r, 'BOTH', rep)] for r in ROLES]
            es.append(all3([F] + [p['full'] for p in ps]))
            ens.append(all3([F_no] + [all3([p['I'], p['G']]) for p in ps]))
        E.extend(es); E_no.extend(ens)
        group_rows.append(dict(group=g['group'], F=F, F_NOREF=F_no, E=es, E_NOREF=ens, both_repetitions=all3(es)))
    arms = {}
    for arm in ARMS:
        selected = [score[s['id']] for s in slots if s['arm'] == arm]
        arms[arm] = {k: bounds([r[k] for r in selected]) for k in ('I', 'G', 'full', 'input_support', 'unknown_channel')}
    def difference(key):
        a, b = arms['BOTH'][key], arms['PRIVATE'][key]
        return [a[0] - b[1], a[1] - b[0]]
    e = bounds(E); fs = list(formation.values())
    return dict(rows=rows, groups=group_rows, E_BOTH=e, E_NOREF=bounds(E_no), F=bounds(fs), arms=arms,
                L=difference('I'), A=difference('G'),
                formation_status='OBSERVED_JOINT_FORMATION' if True in fs else 'NO_JOINT_FORMATION' if all(v is False for v in fs) else 'INCONCLUSIVE',
                prediction_status='MET_IN_FIXED_SAMPLE' if e[0] == 1 else 'NOT_MET_IN_FIXED_SAMPLE' if e[1] < 1 else 'INCONCLUSIVE')

def simulate(groups, slots, mutation=None):
    gm = {g['group']: g for g in groups}; parsed = {}; outputs = {}; inputs = {}; blocked = []
    for s in slots:
        g = gm[s['group']]; text = input_text(g, s, parsed)
        if text is None: raw = None; blocked.append(s['id'])
        else:
            inputs[s['id']] = text; obj = ideal(g, s)
            if mutation: obj = mutation(s, obj)
            raw = obj if isinstance(obj, str) or obj is None else canon(obj)
        outputs[s['id']] = raw; parsed[s['id']] = parse(raw, s['stage'])
    return dict(outputs=outputs, parsed=parsed, inputs=inputs, dependency_unissued=blocked, analysis=analyse(groups, slots, outputs))
