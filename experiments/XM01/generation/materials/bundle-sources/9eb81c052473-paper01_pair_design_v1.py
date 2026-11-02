"""Offline protocol material and scoring for E1/E2. No transport or auth code.

Truth helpers are used only in fixture construction/scoring. Input projection and
SELECT copying never use them. Existing studies remain immutable.
"""
from copy import deepcopy
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import random
import row_carry_02_design_v1 as rc
from note_provenance_split_v1 import obj, enum, ID, parse, shape, json_bytes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study2/designs/paper-01-pair-20260921'
SEED = 2026092101
ROLES = ('A', 'B')
MODES = ('REWRITE', 'SELECT')
ORIGINS = ('CORRECT', 'OLD', 'ABSENT')
NOTICES = ('ID_ONLY', 'DETAILS')
DOMAINS = ('科学工作展', '地域園芸講座', '図書交換会', '防災学習会',
           '天体観察会', '料理体験会', '歴史散策会', '音楽鑑賞会')
AREAS = ('東会場', '西会場', '南会場', '北会場', '中央会場', '川辺会場', '丘の会場', '駅前会場')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def opaque(tag):
    return 'R' + sha256(('P01-20260921/' + tag).encode()).hexdigest()[:15].upper()


def canonical(material):
    """Ignore scene/ID strings and collapse A/B, paper/digital, DOG/CAT mirrors."""
    world = {'old': material['baseline_by_role']['A']['shared_note']['coverage'],
             'new': material['notices'],
             'customers': {r: material['baseline_by_role'][r]['private_note']['customer'] for r in ROLES}}
    def transform(x, mapping):
        if isinstance(x, dict):
            return {mapping.get(k, k): transform(v, mapping) for k, v in x.items() if k != 'origin_id'}
        return mapping.get(x, x) if isinstance(x, str) else x
    variants = []
    for a, p, d in product((False, True), repeat=3):
        mp = {}
        if a: mp.update(A='B', B='A')
        if p: mp.update(paper='digital', digital='paper')
        if d: mp.update(DOG='CAT', CAT='DOG')
        variants.append(json_bytes(transform(world, mp)))
    return sha256(min(variants)).hexdigest()


def generate_materials():
    """Fixed grammar, outcome-free rejection of structural duplicates only."""
    rng = random.Random(SEED)
    seen = set()
    for old in ('row-carry-01-20260919', 'row-carry-02-20260920'):
        for m in json.loads((ROOT/'study2/designs'/old/'materials.json').read_text()).values():
            seen.add(canonical(m))
    excluded = len(seen)
    rejected = 0
    materials = {}
    patterns = list(product(('ALL', 'NOT_ALL'), repeat=2))
    for index in range(72):
        g = f'E1-G{index+1:02}' if index < 64 else f'E2-G{index-63:02}'
        while True:
            channel = rng.choice(('PAPER', 'DIGITAL'))
            restricted = rng.choice((('A',), ('B',), ROLES))
            latest, oldrows, customers = {}, {}, {}
            first_animal = rng.choice(('DOG', 'CAT'))
            for r in ROLES:
                revision = rng.choice((2, 3, 4))
                p, d = ('ALL', 'ALL')
                if r in restricted:
                    p, d = ('ALL', 'NOT_ALL') if channel == 'PAPER' else ('NOT_ALL', 'ALL')
                op, od = rng.choice([x for x in patterns if x != (p, d)])
                latest[r] = dict(observer=r, paper=p, digital=d, revision=revision,
                                 origin_id=opaque(g+'/'+r+'/new'))
                oldrows[r] = dict(observer=r, paper=op, digital=od, revision=rng.randrange(1, revision),
                                  origin_id=opaque(g+'/'+r+'/old'))
                customers[r] = dict(subject=r, animal=first_animal if r == 'A' else ('CAT' if first_animal == 'DOG' else 'DOG'),
                                    origin_id=opaque(g+'/'+r+'/customer'))
            m = {'group': g, 'scene': DOMAINS[index % 8] + '・' + AREAS[(index // 8) % 8],
                 'item': '個別の案内カード', 'notices': latest, 'final_channel': channel,
                 'baseline_by_role': {r: {'private_note': {'customer': customers[r], 'coverage': deepcopy(oldrows[r])},
                                         'shared_note': {'coverage': deepcopy(oldrows)}} for r in ROLES}}
            key = canonical(m)
            if key not in seen:
                seen.add(key)
                break
            rejected += 1
        if index >= 64:
            m['scene'] = DOMAINS[index % 8] + '・撤回診断用の別開催'
            m['target'] = ROLES[(index-64) % 2]
            m['notice_id'] = opaque(g+'/notice')
            m['absent_id'] = opaque(g+'/absent')
        materials[g] = m
    return materials, {'legacy_canonical_classes_excluded': excluded,
                       'structural_duplicates_rejected_before_model_use': rejected,
                       'new_canonical_classes': 72, 'model_selection_calls': 0}


def allocation(materials):
    rng = random.Random(SEED+1)
    result = []
    e1 = [g for g in materials if g.startswith('E1')]
    rng.shuffle(e1)
    for window in range(1, 5):
        batch = e1[(window-1)*16:window*16]
        for i, g in enumerate(batch):
            method_order = MODES if i % 2 == 0 else MODES[::-1]
            for stage in ('MERGE', 'PROBE'):
                for method in method_order if stage == 'MERGE' else method_order[::-1]:
                    for r in ROLES if i % 2 == 0 else ROLES[::-1]:
                        ident = f'{g}-{method}-{stage}-{r}'
                        result.append(dict(id=ident, experiment='E1', group=g, window=window, condition=method,
                                           stage=stage, role=r,
                                           group_order='LOCAL_FIRST' if (i+(r == 'B')) % 2 == 0 else 'PARTNER_FIRST',
                                           dependencies=[] if stage == 'MERGE' else [f'{g}-{method}-MERGE-{r}']))
    e2 = [g for g in materials if g.startswith('E2')]
    rng.shuffle(e2)
    cells = list(product(ORIGINS, NOTICES))
    for i, g in enumerate(e2):
        order = cells[i % 6:] + cells[:i % 6]
        if i % 2: order = order[::-1]
        for origin, notice in order:
            for stage in ('REVOKE', 'PROBE'):
                for r in ROLES if i % 2 == 0 else ROLES[::-1]:
                    result.append(dict(id=f'{g}-{origin}-{notice}-{stage}-{r}', experiment='E2', group=g, window=5,
                                       origin=origin, notice=notice, stage=stage, role=r,
                                       dependencies=[] if stage == 'REVOKE' else [f'{g}-{origin}-{notice}-REVOKE-{r}']))
    return result


def e1_input(m, slot, states):
    r = slot['role']
    record = lambda alias, body: {'record_id': alias, 'body': deepcopy(body)}
    if slot['stage'] == 'MERGE':
        old = m['baseline_by_role']['A']['shared_note']['coverage']
        local = {q: deepcopy(m['notices'][q] if q == r else old[q]) for q in ROLES}
        partner = {q: deepcopy(old[q] if q == r else m['notices'][q]) for q in ROLES}
        private = {'customer': m['baseline_by_role'][r]['private_note']['customer'], 'coverage': m['notices'][r]}
        groups = [record('LOCAL_GROUP', {'coverage': local}), record('PARTNER_GROUP', {'coverage': partner})]
        if slot['group_order'] == 'PARTNER_FIRST': groups.reverse()
        records = [record('PRIVATE', private)] + groups
    else:
        # Only actual normalized memory; missing parent -> KeyError, no truth substitution.
        memory = states[slot['dependencies'][0]]
        records = [record('PRIVATE', memory['private_note']), record('GROUP', memory['shared_note'])]
    return {'scene': m['scene'], 'item': m['item'], 'holder': r, 'records': records}


def e1_prompt(stage, method):
    if stage == 'PROBE' or method == 'SELECT':
        return rc.prompt(stage)
    return rc.PROMPTS[stage]+'\n'+rc.COMMON+'\nPRIVATEは本人の一行、LOCAL_GROUPとPARTNER_GROUPはA/B各行です。shared_note.coverageのA/B各欄に採用する観測のobserver・paper・digital・origin_id・revisionを記述してください。private_noteとread_receiptも出力してください。\n'+json.dumps(rc.memory_schemas()[stage], ensure_ascii=False)


def e1_ideal(m, slot):
    return rc.ideal(m, slot) if slot['condition'] == 'SELECT' else rc.ideal_normal(m, slot)


def e1_evaluate(m, slot, raw, payload):
    if slot['condition'] == 'SELECT': return rc.evaluate(m, slot, raw, payload)
    inspected = rc.inspect_normal(raw, payload, slot['stage'])
    return dict(score=rc.score_normal(m, slot, raw, payload), gate=inspected['gate'],
                normalized=inspected['value'], bindings=[], selection_errors=[])


def e2_schemas():
    base = rc.memory_schemas()['MERGE']['properties']['memory']
    memory = deepcopy(base)
    row = memory['properties']['private_note']['properties']['coverage']
    row['properties']['status'] = enum('ACTIVE', 'REVOKED'); row['required'].append('status')
    for r in ROLES: memory['properties']['shared_note']['properties']['coverage']['properties'][r] = deepcopy(row)
    processing = obj({'notice_id': ID, 'target_origin_id': ID,
                      'resolution': enum('MATCHED', 'UNRESOLVED'), 'basis': enum('ID', 'DETAILS', 'NONE'),
                      'matched_observer': enum('A', 'B', 'UNKNOWN')})
    save = obj({'memory': memory, 'processing': processing})
    probe = obj({'mascot': enum('DOG', 'CAT', 'UNKNOWN'), 'customer_origin_id': ID,
                 'channel': enum('PAPER', 'DIGITAL', 'UNKNOWN'),
                 'channel_status': enum('READY', 'WITHDRAWN', 'PENDING'),
                 'active_coverage': {'type': 'array', 'items': deepcopy(row), 'maxItems': 2, 'uniqueItems': True},
                 'revoked_observers': {'type': 'array', 'items': enum('A', 'B'), 'maxItems': 2, 'uniqueItems': True},
                 'pending_notice_ids': {'type': 'array', 'items': ID, 'maxItems': 1, 'uniqueItems': True}})
    return {'REVOKE': save, 'PROBE': probe}


E2_COMMON = '''資料だけを使い、指定schemaのJSONを一つ返す。A/Bは役が担当する対象の区別で、人物を統合しない。origin_idは観測原票の出典である。版は観測者ごとに比較し、出典IDの字面から人物・版を推測しない。全必須欄を出力する。説明文、操作、外部参照は禁止。'''
E2_REVOKE = '''PRIVATE相当のprivate_noteと共同のshared_noteに、現在の記録を保存している。noticeは信頼できる発行元からの観測撤回であり、対象はcoverageだけ。顧客customerの情報は撤回対象ではない。
まずtarget_origin_idが現在の観測のorigin_idと完全一致すれば、その観測者をIDで特定する。一致がなくdetailsがある場合、observer・revision・paper・digitalがすべて一致する一種類の観測を特定できればDETAILSで照合する。同じ観測のprivate/sharedコピーは同一種類と数える。この照合は異なる出典IDを同一内容の撤回対象へ結び付けるために許可される。
特定できたら、対象観測の全コピーをREVOKEDにする。観測内容・版・元の出典IDは履歴として保持し、正しいIDへの書換えや代替観測の創作はしない。対象外の観測とcustomerは全欄保持する。processingはMATCHED、該当するbasis、matched_observerを記録する。
特定できなければ記録の全内容とACTIVE状態を維持し、processingをUNRESOLVED/NONE/UNKNOWNにする。通知IDと対象出典IDを保存し、後続の共同判断を保留できるようにする。手当たり次第の削除や推測での対象決定をしない。'''
E2_PROBE = '''保存されたmemoryとprocessingだけを読む。mascotは本人customerのanimal、customer_origin_idはその出典。shared_note.coverageのACTIVE行をactive_coverageへ全欄で列挙し、REVOKEDの観測者をrevoked_observersへ列挙する。配列の順序は任意。
processingがUNRESOLVEDなら、pending_notice_idsにそのnotice_idを入れ、channel=UNKNOWN、channel_status=PENDING。対象不明の撤回が共同判断の根拠へ影響し得るためである。MATCHEDならpending_notice_idsは空で、A/Bどちらかの共同観測がREVOKEDならchannel=UNKNOWN、channel_status=WITHDRAWN。
未解決も失効もなく、両観測者でALLの媒体が一つだけならそれをchannelへ、channel_status=READY。媒体が一意でない場合もchannel=UNKNOWNとする。保留の場合も、本人の好みや有効な観測行は読み取って答える。'''


def e2_prompt(stage):
    return E2_COMMON+'\n'+(E2_REVOKE if stage == 'REVOKE' else E2_PROBE)+'\n'+json.dumps(e2_schemas()[stage], ensure_ascii=False)


def validate_input(experiment, stage, payload):
    """Structural ingress gate, no truth matching or semantic content correction."""
    if type(payload) is not dict: return ['INPUT_OBJECT']
    errors = []
    for k in ('scene', 'item'):
        if type(payload.get(k)) is not str or not 1 <= len(payload[k]) <= 128: errors.append('CONTEXT:'+k)
    if payload.get('holder') not in ROLES: errors.append('HOLDER')
    if experiment == 'E1':
        if set(payload) != {'scene','item','holder','records'}: errors.append('INPUT_KEYS')
        records = payload.get('records')
        if type(records) is not list: return errors+['RECORDS_ARRAY']
        aliases = [x.get('record_id') if type(x) is dict else None for x in records]
        expected = ['PRIVATE','LOCAL_GROUP','PARTNER_GROUP'] if stage == 'MERGE' else ['PRIVATE','GROUP']
        if len(aliases) != len(expected) or any(a not in expected for a in aliases) or len(set(aliases)) != len(aliases):
            errors.append('RECORD_ALIAS_SET')
        rules = rc.memory_schemas()['MERGE']['properties']['memory']['properties']
        for x in records:
            if type(x) is not dict or set(x) != {'record_id','body'}: errors.append('RECORD_KEYS'); continue
            errors += shape(x['body'], rules['private_note' if x['record_id'] == 'PRIVATE' else 'shared_note'])
    elif experiment == 'E2':
        expected = {'scene','item','holder','memory', 'notice' if stage == 'REVOKE' else 'processing'}
        if set(payload) != expected: errors.append('INPUT_KEYS')
        rules = e2_schemas()['REVOKE']['properties']
        errors += shape(payload.get('memory'), rules['memory'])
        if stage == 'REVOKE':
            n = payload.get('notice')
            props = {'notice_id':ID,'target_origin_id':ID}
            if type(n) is dict and 'details' in n:
                base = deepcopy(rc.memory_schemas()['MERGE']['properties']['memory']['properties']['private_note']['properties']['coverage'])
                del base['properties']['origin_id']; base['required'].remove('origin_id')
                props['details'] = base
            errors += shape(n, obj(props))
        else: errors += shape(payload.get('processing'), rules['processing'])
    else: errors.append('EXPERIMENT')
    return errors


def e2_input(m, slot, states):
    if slot['stage'] == 'PROBE':
        saved = states[slot['dependencies'][0]]
        return {'scene': m['scene'], 'item': m['item'], 'holder': slot['role'],
                'memory': deepcopy(saved['memory']), 'processing': deepcopy(saved['processing'])}
    memory = rc.expected_memory(m, slot['role'], 'MERGE')
    bad = m['baseline_by_role']['A']['shared_note']['coverage'][m['target']]['origin_id'] if slot['origin'] == 'OLD' else m['absent_id']
    rows = [memory['private_note']['coverage'], *memory['shared_note']['coverage'].values()]
    for row in rows:
        row['status'] = 'ACTIVE'
        if row['observer'] == m['target'] and slot['origin'] != 'CORRECT': row['origin_id'] = bad
    notice = {'notice_id': m['notice_id'], 'target_origin_id': m['notices'][m['target']]['origin_id']}
    if slot['notice'] == 'DETAILS':
        notice['details'] = {k: v for k, v in m['notices'][m['target']].items() if k != 'origin_id'}
    return {'scene': m['scene'], 'item': m['item'], 'holder': slot['role'], 'memory': memory, 'notice': notice}


def e2_ideal_revoke(m, slot, payload):
    """Fixture/scoring oracle only; never called in input projection or storage."""
    matched = slot['origin'] == 'CORRECT' or slot['notice'] == 'DETAILS'
    memory = deepcopy(payload['memory'])
    if matched:
        for row in [memory['private_note']['coverage'], *memory['shared_note']['coverage'].values()]:
            if row['observer'] == m['target']: row['status'] = 'REVOKED'
    return {'memory': memory, 'processing': {'notice_id': m['notice_id'],
            'target_origin_id': m['notices'][m['target']]['origin_id'],
            'resolution': 'MATCHED' if matched else 'UNRESOLVED',
            'basis': 'ID' if slot['origin'] == 'CORRECT' else ('DETAILS' if matched else 'NONE'),
            'matched_observer': m['target'] if matched else 'UNKNOWN'}}


def e2_read(memory, processing):
    """Deterministic scoring of the explicit readout contract, not a model worker."""
    customer = memory['private_note']['customer']
    active = [deepcopy(memory['shared_note']['coverage'][r]) for r in ROLES if memory['shared_note']['coverage'][r]['status'] == 'ACTIVE']
    revoked = [r for r in ROLES if memory['shared_note']['coverage'][r]['status'] == 'REVOKED']
    pending = [processing['notice_id']] if processing['resolution'] == 'UNRESOLVED' else []
    media = [k for k in ('paper', 'digital') if len(active) == 2 and all(v[k] == 'ALL' for v in active)]
    return dict(mascot=customer['animal'], customer_origin_id=customer['origin_id'],
                channel=media[0].upper() if not pending and not revoked and len(media) == 1 else 'UNKNOWN',
                channel_status='PENDING' if pending else ('WITHDRAWN' if revoked else 'READY'),
                active_coverage=active, revoked_observers=revoked, pending_notice_ids=pending)


def unpack(raw, rule, max_bytes):
    if raw is None: return None, ['MISSING']
    if len(raw) > max_bytes: return None, ['OUTPUT_BYTES']
    try: value = parse(raw)
    except (ValueError, UnicodeError, RecursionError): return None, ['JSON']
    return value, shape(value, rule)


def component(actual, expected, rule, unordered=False):
    if shape(actual, rule): return None
    if unordered: return sorted(map(json_bytes, actual)) == sorted(map(json_bytes, expected))
    return actual == expected


def e2_evaluate(m, slot, raw, payload):
    rule = e2_schemas()[slot['stage']]
    value, errors = unpack(raw, rule, 8192)
    parts = {}
    if slot['stage'] == 'REVOKE':
        expected = e2_ideal_revoke(m, slot, payload)
        paths = [('memory','private_note','customer'), ('memory','private_note','coverage'),
                 ('memory','shared_note','coverage','A'), ('memory','shared_note','coverage','B')]
        paths += [('processing', k) for k in expected['processing']]
        for path in paths:
            field_rule = rule
            for k in path: field_rule = field_rule['properties'][k]
            parts['.'.join(path)] = component(rc.leaf(value, *path), rc.leaf(expected, *path), field_rule)
        completion_known = slot['origin'] == 'CORRECT' or slot['notice'] == 'DETAILS'
        local_read = None
    else:
        initial = e2_input(m, {**slot, 'stage': 'REVOKE'}, {})
        ideal_state = e2_ideal_revoke(m, slot, initial)
        expected = e2_read(ideal_state['memory'], ideal_state['processing'])
        actual_read = e2_read(payload['memory'], payload['processing'])
        for k, target in expected.items():
            parts[k] = component(rc.leaf(value, k), target, rule['properties'][k], isinstance(target, list))
        local_read = rc.tri_and(component(rc.leaf(value, k), v, rule['properties'][k], isinstance(v, list)) for k, v in actual_read.items())
        completion_known = slot['origin'] == 'CORRECT' or slot['notice'] == 'DETAILS'
    safe = rc.tri_and([*parts.values(), None if errors else True])
    # Resolution is impossible under the information contract in the bad-ID-only cells.
    completed = None if safe is None else rc.tri_and([safe, completion_known])
    return {'gate': 'REJECT' if errors else 'PASS', 'value': value, 'errors': errors,
            'score': {'evidence_appropriate': safe, 'completion': completed,
                      'parts': parts, 'local_readout': local_read}}


def paired_counts_possible(pairs):
    """All compatible (SELECT-only, REWRITE-only) counts; None is unknown."""
    possible = {(0, 0)}
    for rewrite, select in pairs:
        assert all(v is None or type(v) is bool for v in (rewrite, select))
        rv = (False, True) if rewrite is None else (rewrite,)
        sv = (False, True) if select is None else (select,)
        changes = {(int(s and not r), int(r and not s)) for r, s in product(rv, sv)}
        possible = {(a+c, b+d) for a, b in possible for c, d in changes}
    return sorted(possible)


def paired_statistics(pairs):
    from scipy.stats import beta, binomtest
    n = len(pairs)
    if not n: raise ValueError('EMPTY_FIXED_DENOMINATOR')
    possible = paired_counts_possible(pairs)
    # Two marginal 97.5% exact binomial intervals; union bound >=95% jointly.
    intervals = []
    for k in range(n+1):
        intervals.append((0.0 if k == 0 else float(beta.ppf(.0125, k, n-k+1)),
                          1.0 if k == n else float(beta.ppf(.9875, k+1, n-k))))
    bounds = [(a-b)/n for a, b in possible]
    ci = [(intervals[a][0]-intervals[b][1], intervals[a][1]-intervals[b][0]) for a, b in possible]
    missing = any(None in p for p in pairs)
    a, b = possible[0]
    pvalue = None if missing else (float(binomtest(a, a+b, .5).pvalue) if a+b else 1.0)
    return dict(n=n, missing_pairs=sum(None in p for p in pairs), delta_bounds=[min(bounds), max(bounds)],
                conservative_ci95=[min(v[0] for v in ci), max(v[1] for v in ci)],
                exact_mcnemar_two_sided_p=pvalue, compatible_discordance_counts=len(possible))


def aggregate(materials, slots, scores):
    e1 = {}
    for mode in ('strict', 'content'):
        groups = {}
        for g in materials:
            if not g.startswith('E1'): continue
            groups[g] = {c: rc.tri_and(scores.get(s['id'], {}).get(mode) for s in slots if s['group'] == g and s['condition'] == c)
                         for c in MODES}
        stats = paired_statistics([(v['REWRITE'], v['SELECT']) for v in groups.values()])
        if mode != 'strict':
            stats['exact_mcnemar_two_sided_p'] = None
            stats['test_policy'] = 'DESCRIPTIVE_SENSITIVITY_NO_SECOND_TEST'
        e1[mode] = {'groups': groups, 'statistics': stats}
    e2 = {}
    for origin, notice in product(ORIGINS, NOTICES):
        cell = {}
        for mode in ('evidence_appropriate', 'completion'):
            groups = {g: rc.tri_and(scores.get(s['id'], {}).get(mode) for s in slots if s['group'] == g and s['origin'] == origin and s['notice'] == notice)
                      for g in materials if g.startswith('E2')}
            values = list(groups.values())
            cell[mode] = {'groups': groups, 'fixed_n': 8, 'bounds': [values.count(True)/8, (values.count(True)+values.count(None))/8]}
        e2[origin+'/'+notice] = cell
    return {'E1': e1, 'E2': e2,
            'E2_control_gate': {t: 'ESTABLISHED' if e2['CORRECT/'+t]['completion']['bounds'][0] == 1 else 'BASELINE_NOT_ESTABLISHED' for t in NOTICES}}


def build():
    materials, audit = generate_materials()
    slots = allocation(materials)
    write(OUT/'materials.json', materials); write(OUT/'material-audit.json', audit)
    write(OUT/'allocation.json', slots)
    write(OUT/'schemas-e1.json', {'REWRITE': rc.memory_schemas()['MERGE'], 'SELECT': rc.schemas()['MERGE'], 'PROBE': rc.memory_schemas()['PROBE']})
    write(OUT/'schemas-e2.json', e2_schemas())
    for stage, method in [('MERGE','REWRITE'), ('MERGE','SELECT'), ('PROBE','COMMON')]:
        with (OUT/f'prompt-e1-{stage.lower()}-{method.lower()}.txt').open('x') as f: f.write(e1_prompt(stage, method)+'\n')
    for stage in ('REVOKE', 'PROBE'):
        with (OUT/f'prompt-e2-{stage.lower()}.txt').open('x') as f: f.write(e2_prompt(stage)+'\n')
    states, scores, examples, lengths = {}, {}, [], {'E1': [], 'E2': []}
    for s in slots:
        m = materials[s['group']]
        if s['experiment'] == 'E1':
            payload = e1_input(m, s, states); answer = e1_ideal(m, s)
            ev = e1_evaluate(m, s, json_bytes(answer), payload)
            if s['stage'] != 'PROBE': states[s['id']] = deepcopy(ev['normalized']['memory'])
            prompt = e1_prompt(s['stage'], s['condition'])
            assert ev['score']['strict'] is True
        else:
            payload = e2_input(m, s, states)
            answer = e2_ideal_revoke(m, s, payload) if s['stage'] == 'REVOKE' else e2_read(payload['memory'], payload['processing'])
            ev = e2_evaluate(m, s, json_bytes(answer), payload)
            if s['stage'] != 'PROBE': states[s['id']] = deepcopy(ev['value'])
            prompt = e2_prompt(s['stage'])
            assert ev['score']['evidence_appropriate'] is True
        assert ev['gate'] == 'PASS'
        assert not validate_input(s['experiment'], s['stage'], payload)
        scores[s['id']] = ev['score']
        lengths[s['experiment']].append(len((prompt+'\n資料JSON:\n'+json_bytes(payload).decode()).encode()))
        if not s['dependencies']: write(OUT/'initial-inputs'/(s['id']+'.json'), payload)
        examples.append({'kind': 'SYNTHETIC_NOT_MODEL_DATA', 'slot': s, 'input': payload, 'output': answer, 'evaluation': ev})
    write(OUT/'synthetic-perfect.json', examples)
    write(OUT/'synthetic-perfect-summary.json', aggregate(materials, slots, scores))
    write(OUT/'config.json', dict(protocol='PAPER-01-PAIR-V1', seed=SEED, planned_slots=704,
          E1=dict(groups=64, regular_requests=512, max_requests=528, windows=4, seconds_per_window=3600,
                  retry_reserve_per_window=4, primary='strict', alpha=.05),
          E2=dict(groups=8, regular_requests=192, max_requests=200, windows=1, seconds_per_window=5400,
                  retry_reserve_per_window=8, primary_axes=['completion','evidence_appropriate']),
          model_candidate='gpt-5.6-luna', reasoning_candidate='medium', concurrency=1, tools=[],
          usage_soft_stop=dict(E1=1367718, E2=487025, total=1854743), max_attempts_per_slot=2,
          input_prompt_bytes_max=16384, output_bytes_max={'E1':4096,'E2':8192},
          extra_payment_budget=0, execution_authorized=False, transport_connected=False,
          new_model_calls=0, new_auth_calls=0, retention_until=None,
          projected_perfect_input_bytes={k: {'sum': sum(v), 'max': max(v), 'count': len(v)} for k,v in lengths.items()}))
    print(json.dumps({'slots':len(slots),'material_audit':audit,'initial_inputs':sum(not s['dependencies'] for s in slots),'model_calls':0}))


if __name__ == '__main__': build()
