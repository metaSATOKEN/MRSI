"""CU01 fixed synthetic materials and deterministic evaluation; stdlib only."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import role_shared_use_01_design as ru
import self_update_exchange_01_scoring as sx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study2/designs/customer-update-01-20260926'
PROTOCOL = 'CUSTOMER-UPDATE-01/v1'
STAGES = ('CHANGE', 'DELAY', 'READ')
BASE_DESIGN = 'study2/designs/self-update-exchange-02-20260925/design.json'
BASE_SHA = '20131af8d637f7982e930580efe662eec84ef0aa980539d1ee812e5b94ca04c6'
DEPENDENCIES = ('role_shared_use_01_design.py', 'self_update_exchange_01_scoring.py', *ru.DEPENDENCIES)
base = sx.base
enc = base.enc
digest = sx.digest
other = sx.other
receive = sx.policy.receive


def latest_observations(payload, row_schema):
    """G1P1 selection with three observed rows; customer notice is never a candidate."""
    if payload.get('holder') not in ('A', 'B'): raise ValueError('HOLDER')
    records = payload['records']
    if len(records) != 2 or {r['record_id'] for r in records} != {'PRIVATE', 'GROUP'}:
        raise ValueError('RECORDS')
    bodies = {r['record_id']: r['body'] for r in records}
    sources = {'PRIVATE.coverage': bodies['PRIVATE']['coverage'],
               'GROUP.coverage.A': bodies['GROUP']['coverage']['A'],
               'GROUP.coverage.B': bodies['GROUP']['coverage']['B']}
    catalog = payload['row_catalog']
    if len(catalog) != 3 or {c['row_id'] for c in catalog} != {'C1', 'C2', 'C3'}:
        raise ValueError('CATALOG_IDS')
    if {c['location'] for c in catalog} != set(sources): raise ValueError('CATALOG_LOCATIONS')
    for c in catalog:
        if set(c) != {'row_id', 'location', 'row'} or base.shape(c['row'], row_schema):
            raise ValueError('CATALOG_SCHEMA')
        if c['row'] != sources[c['location']]: raise ValueError('CATALOG_SOURCE_MISMATCH')
    selected = {}; witnesses = {}
    for owner in ('A', 'B'):
        candidates = [c for c in catalog if c['row']['observer'] == owner]
        if not candidates: raise ValueError('MISSING_OWNER:' + owner)
        by_version = {}
        for c in candidates:
            version = c['row']['revision']
            if version in by_version and by_version[version] != c['row']:
                raise ValueError('CONFLICTING_EQUAL_REVISION:' + owner)
            by_version[version] = c['row']
        revision = max(by_version)
        winners = sorted((c for c in candidates if c['row']['revision'] == revision), key=lambda c: c['row_id'])
        selected[owner] = deepcopy(winners[0]['row'])
        witnesses[owner] = {'owner': owner, 'revision': revision,
            'candidate_ids': sorted(c['row_id'] for c in candidates),
            'equal_latest_ids': [c['row_id'] for c in winners],
            'selected_id': winners[0]['row_id'], 'location': winners[0]['location'],
            'row_sha256': digest(winners[0]['row'])}
    return selected, witnesses


def validate_input(payload, schema):
    bodies = {r['record_id']: r['body'] for r in payload['records']}
    memory = {'private_note': bodies['PRIVATE'], 'shared_note': bodies['GROUP']}
    if base.shape(memory, schema): raise ValueError('INPUT_MEMORY_SCHEMA')
    customer_schema = schema['properties']['private_note']['properties']['customer']
    if base.shape(payload['customer_notice'], customer_schema): raise ValueError('CUSTOMER_NOTICE_SCHEMA')
    return latest_observations(payload, schema['properties']['private_note']['properties']['coverage'])


def derive_update(raw, payload, schema, finish_reason='EOS'):
    receipt = receive(raw, 'UPDATE', finish_reason)
    metadata = {k: v for k, v in receipt.items() if k != 'normalized_bytes'}
    result = {'receipt': metadata, 'normalized_bytes': receipt['normalized_bytes'],
              'proposal': None, 'memory': None, 'trace': None, 'error': None}
    if receipt['normalized_bytes'] is None:
        result['error'] = 'RECEIVE'; return result
    proposal = base.parse(receipt['normalized_bytes'])
    if base.shape(proposal, schema):
        result['error'] = 'SCHEMA'; return result
    result['proposal'] = proposal
    try: latest, witnesses = validate_input(payload, schema)
    except (ValueError, TypeError, KeyError) as exc:
        result['error'] = 'INPUT_CONTRACT:' + str(exc); return result
    memory = deepcopy(proposal); changes = []
    for owner, target, destination, key in [
        ('A', 'shared_note.coverage.A', memory['shared_note']['coverage'], 'A'),
        ('B', 'shared_note.coverage.B', memory['shared_note']['coverage'], 'B'),
        (payload['holder'], 'private_note.coverage', memory['private_note'], 'coverage')]:
        before = deepcopy(destination[key]); destination[key] = deepcopy(latest[owner])
        changes.append({'target': target, 'before_sha256': digest(before),
            'after_sha256': digest(destination[key]), 'changed': before != destination[key],
            'source': deepcopy(witnesses[owner])})
    assert memory['private_note']['customer'] == proposal['private_note']['customer']
    result.update(memory=memory, trace=changes)
    return result


def expected_memory(case, role, stage):
    """Evaluation-only oracle: no calls from the input path or saving policy."""
    if stage not in STAGES: raise ValueError('STAGE')
    wanted = deepcopy(case['initial_memories'][role])
    if role == case['target']: wanted['private_note']['customer'] = deepcopy(case['new_customer'])
    return wanted


def update_payload(case, role, stage, previous):
    other(role)
    if previous is None: raise ValueError('DEPENDENCY_MISSING:OWN')
    if stage not in ('CHANGE', 'DELAY'): raise ValueError('NOT_UPDATE_STAGE')
    notice = case['new_customer'] if stage == 'CHANGE' else case['initial_memories'][case['target']]['private_note']['customer']
    memory = deepcopy(previous)
    entries = [('PRIVATE.coverage', memory['private_note']['coverage']),
               ('GROUP.coverage.A', memory['shared_note']['coverage']['A']),
               ('GROUP.coverage.B', memory['shared_note']['coverage']['B'])]
    entries.sort(key=lambda pair: digest([PROTOCOL, case['id'], role, stage, pair[0]]))
    return {'holder': role, 'scene': case['scene'], 'item': case['item'],
        'records': [{'record_id': 'PRIVATE', 'body': memory['private_note']},
                    {'record_id': 'GROUP', 'body': memory['shared_note']}],
        'customer_notice': deepcopy(notice),
        'row_catalog': [{'row_id': 'C'+str(i+1), 'location': location, 'row': deepcopy(row)}
                        for i, (location, row) in enumerate(entries)]}


def slot_payload(design, slot, states):
    case = next(c for c in design['cases'] if c['id'] == slot['case'])
    role, stage = slot['role'], slot['stage']
    if stage == 'CHANGE':
        source = next(s for s in design['sources'] if s['id'] == slot['source_id'])
        return update_payload(case, role, stage, source['memory'])
    parents = [states.get(pid) for pid in slot['parents']]
    if len(parents) != 1 or parents[0] is None: raise ValueError('DEPENDENCY_MISSING')
    if stage == 'READ': return ru.input_payload({'role': role, 'scene': case['scene'], 'item': case['item']}, parents[0])
    return update_payload(case, role, stage, parents[0])


def request_for(design, slot, states):
    payload = slot_payload(design, slot, states)
    return {'id': slot['id'], 'seed': slot['seed'], 'messages': [
        {'role': 'system', 'content': design['read_prompt'] if slot['stage'] == 'READ' else design['update_prompt']},
        {'role': 'user', 'content': '\n資料JSON:\n'+enc(payload).decode()}]}


def score_memory(memory, case, role, stage):
    names = ('customer', 'customer_subject', 'customer_animal', 'customer_origin', 'customer_revision',
             'customer_matches_initial', 'self_row', 'partner_row', 'shared', 'joint')
    if memory is None: return {'format_valid': None, **{k: None for k in names}}
    want = expected_memory(case, role, stage)
    actual = memory['private_note']['customer']; expected = want['private_note']['customer']
    return {'format_valid': True, 'customer': actual == expected,
        **{'customer_'+label: actual[key] == expected[key] for label, key in
           [('subject','subject'), ('animal','animal'), ('origin','origin_id'), ('revision','revision')]},
        'customer_matches_initial': actual == case['initial_memories'][role]['private_note']['customer'],
        'self_row': memory['private_note']['coverage'] == want['private_note']['coverage'],
        'partner_row': memory['shared_note']['coverage'][other(role)] == want['shared_note']['coverage'][other(role)],
        'shared': memory['shared_note'] == want['shared_note'], 'joint': memory == want}


def evaluate_update(raw, payload, design, case, role, stage, finish_reason='EOS'):
    derived = derive_update(raw, payload, design['update_schema'], finish_reason)
    score = score_memory(derived['memory'], case, role, stage)
    score.update(proposal_score=score_memory(derived['proposal'], case, role, stage) if derived['proposal'] is not None else None,
                 normalization=derived['receipt'], error=derived['error'])
    if derived['memory'] is None: score['format_valid'] = False
    return derived, score


def score_read(raw, memory, case, role, schema, finish_reason='EOS'):
    keys = ('subject_note', 'animal_note', 'four_note_exact', 'channel_note', 'customer_latest', 'four_latest', 'channel_latest', 'joint')
    if memory is None:
        return {'format_valid': None, **{k: None for k in keys}, 'answer': None, 'actions': None,
                'normalization': {'status': 'UNRESOLVED', 'reason': 'DEPENDENCY_MISSING'}}
    payload = ru.input_payload({'role': role, 'scene': case['scene'], 'item': case['item']}, memory)
    score = ru.score_response(raw, payload, schema, finish_reason)
    result = {'format_valid': score['format_valid'], **{k: None for k in keys},
              'answer': score['answer'], 'actions': score['actions'], 'normalization': score['normalization'], 'errors': score['errors']}
    if not score['format_valid']: return result
    wanted = expected_memory(case, role, 'READ')['private_note']['customer']
    expected_four = {o: {k: case['observations'][o][k] for k in ('paper', 'digital')} for o in ('A', 'B')}
    result.update(subject_note=score['subject'], animal_note=score['animal'], four_note_exact=score['four_exact'], channel_note=score['channel'],
        customer_latest=score['answer']['customer'] == {k: wanted[k] for k in ('subject', 'animal')},
        four_latest=score['answer']['coverage'] == expected_four,
        channel_latest=score['actions']['channel'] == base.compute_channel(expected_four))
    result['joint'] = all(result[k] for k in keys if k != 'joint')
    return result


def summarize(design, outcomes):
    if set(outcomes) - {s['id'] for s in design['allocation']}: raise ValueError('UNEXPECTED_RESPONSE')
    cases = {c['id']: c for c in design['cases']}; paths = []; pairs = []; rollback = []
    for run in design['runs']:
        case = cases[run['case']]
        values = [outcomes.get(run['id']+'-'+stage+'-'+role, {}) for stage in STAGES for role in ('A', 'B')]
        success = all(v.get('joint') is True for v in values) if all(v.get('format_valid') is True for v in values) else None
        paths.append({**run, 'success': success})
        reads = [outcomes.get(run['id']+'-READ-'+role, {}) for role in ('A', 'B')]
        pair = {**run, 'expected_relation': 'DIFFERENT' if case['initial_relation'] == 'SAME' else 'SAME',
                'relation_correct': None, 'same_channel': None, 'both_correct': None}
        if all(v.get('format_valid') is True for v in reads):
            a, b = [v['actions'] for v in reads]
            pair.update(relation_correct=(a['card_animal'] == b['card_animal']) == (pair['expected_relation'] == 'SAME'),
                        same_channel=a['channel'] == b['channel'], both_correct=all(v['joint'] for v in reads))
        pairs.append(pair)
        change = outcomes.get(run['id']+'-CHANGE-'+case['target'], {})
        delay = outcomes.get(run['id']+'-DELAY-'+case['target'], {})
        if change.get('format_valid') is not True: state = 'CHANGE_UNRESOLVED'
        elif change.get('customer') is not True: state = 'CHANGE_ALREADY_WRONG'
        elif delay.get('format_valid') is not True: state = 'DELAY_UNRESOLVED'
        elif delay['customer']: state = 'KEPT_LATEST'
        elif delay['customer_matches_initial']: state = 'ROLLED_BACK_TO_INITIAL'
        else: state = 'OTHER_CUSTOMER_ERROR'
        rollback.append({**run, 'state': state})
    total = base.counts(p['success'] for p in paths)
    reps = {str(i): base.counts(p['success'] for p in paths if p['replicate'] == i) for i in (1, 2)}
    tests = [(total, design['decision_rules']['complete_pair_paths'])] + [(c, design['decision_rules']['each_repeat']) for c in reps.values()]
    status = 'MET' if all(c['correct'] >= n for c, n in tests) else 'NOT_MET' if any(c['correct']+c['unresolved'] < n for c, n in tests) else 'INCONCLUSIVE'
    components = {}
    for stage in STAGES:
        selected = [outcomes.get(s['id'], {}) for s in design['allocation'] if s['stage'] == stage]
        names = ('joint','subject_note','animal_note','four_note_exact','channel_note','customer_latest','four_latest','channel_latest') if stage == 'READ' else ('joint','customer','customer_subject','customer_animal','customer_origin','customer_revision','self_row','partner_row','shared')
        components[stage] = {k: base.counts(v.get(k) for v in selected) for k in names}
        if stage != 'READ': components[stage]['proposal'] = {k: base.counts((v.get('proposal_score') or {}).get(k) for v in selected) for k in names}
    subsets = {}
    for label, selector, key in [
        ('target_change', lambda s: s['stage']=='CHANGE' and s['role']==cases[s['case']]['target'], 'customer'),
        ('non_target_preserved', lambda s: s['stage']!='READ' and s['role']!=cases[s['case']]['target'], 'customer'),
        ('target_after_delay', lambda s: s['stage']=='DELAY' and s['role']==cases[s['case']]['target'], 'customer')]:
        subsets[label] = base.counts(outcomes.get(s['id'], {}).get(key) for s in design['allocation'] if selector(s))
    return {'protocol': PROTOCOL, 'materials': 8, 'pair_runs': 16, 'response_slots': 96, 'path': total, 'by_repeat': reps,
        'criterion_status': status, 'path_fraction_missing_bounds': [total['correct']/16, (total['correct']+total['unresolved'])/16],
        'paths': paths, 'components': components, 'customer_subsets': subsets, 'read_pairs': pairs,
        'read_pair_metrics': {k: base.counts(p[k] for p in pairs) for k in ('relation_correct','same_channel','both_correct')},
        'rollback': {'rows': rollback, 'counts': dict(Counter(x['state'] for x in rollback)),
                     'eligible_correct_change': sum(x['state'] not in ('CHANGE_UNRESOLVED','CHANGE_ALREADY_WRONG') for x in rollback)},
        'strata': {key: {v: base.counts(p['success'] for p in paths if cases[p['case']][key] == v)
                        for v in sorted({c[key] for c in design['cases']})} for key in ('initial_relation','target','direction','channel')},
        'p_value': None, 'confidence_interval': None}


def build_design():
    raw = (ROOT/BASE_DESIGN).read_bytes()
    if sha256(raw).hexdigest() != BASE_SHA: raise ValueError('BASE_DESIGN_CHANGED')
    old = json.loads(raw); schema = deepcopy(old['update_schema'])
    customer = schema['properties']['private_note']['properties']['customer']
    customer['properties']['revision'] = {'type':'integer','minimum':1,'maximum':1000000}
    customer['required'].append('revision')
    prompt = ('あなたは架空の作業担当者です。holderが自分の担当役です。保存済みの個別・共同ノートと、担当客の希望に関する正規の通知customer_noticeから、次へ渡すノートを作ってください。'
        'customer.subjectはその客を担当する役を示します。PRIVATE.customerとcustomer_noticeのrevisionは担当客の希望の版であり、coverageの観測版とは別です。'
        '通知のsubjectがholderと一致し、その同じ担当客について保存済みの版より通知のrevisionが大きいときだけ、通知のsubject・animal・origin_id・revisionを一行として採用してください。'
        '別の役の担当客の通知では、自分のPRIVATE.customerを全欄そのまま保持してください。人物間でrevisionを比較しません。'
        '同じ担当客の古い通知では、保存済みの新しい希望と元ID・版を保持してください。到着順で上書きしないでください。同版の矛盾は今回の通知にはありません。'
        '担当客の希望が二人で同じか違うかは、変更する理由になりません。担当客の情報を観測欄へ入れないでください。'
        '観測はPRIVATE.coverageとGROUP.coverage.A/Bにあります。row_catalogはこの三行だけの一覧です。C1〜C3は今回だけの候補位置IDで、origin_idとは異なります。'
        '同じobserverのrevisionを比較してその人の最新行を選び、PRIVATE.coverageはholder本人、GROUP.coverageはA/Bそれぞれを記述してください。'
        'observer・paper・digital・origin_id・revisionは一行単位で扱い、候補どうしの項目を混ぜないでください。担当客通知は観測の候補ではありません。'
        'private_noteとshared_noteの本文をschemaどおりに記述してください。A/Bは固定キーのobjectです。案内方法、説明、受領票、余分な欄を出さず、全必須欄を含むJSONのみを返してください。\n'+enc(schema).decode()+'\n')
    scenes = ('陶芸体験受付','野鳥観察受付','製本体験受付','星空観察受付','染色体験受付','水族観察受付','木版画体験受付','鉱物観察受付')
    cases = []; sources = []
    for i, (relation, target, animal) in enumerate(product(('SAME','DIFFERENT'), ('A','B'), ('DOG','CAT')), 1):
        cid = f'CU01-C{i:02d}'; r, t, d = int(relation=='DIFFERENT'), int(target=='B'), int(animal=='CAT')
        channel = 'PAPER' if (r+t+d)%2==0 else 'DIGITAL'
        higher = 'A' if (r+d)%2==0 else 'B'
        high_observer = other(higher); observations = {}
        for o in ('A','B'):
            observations[o] = {'observer':o,'paper':'ALL','digital':'ALL',
                'origin_id':'V'+digest([PROTOCOL,cid,o,'OBS'])[:16].upper(), 'revision': 300+i+(50 if o==high_observer else 0)}
        observations[other(target)]['digital' if channel=='PAPER' else 'paper'] = 'NOT_ALL'
        memories = {}
        for o in ('A','B'):
            value = animal if o==target or relation=='SAME' else {'DOG':'CAT','CAT':'DOG'}[animal]
            customer = {'subject':o,'animal':value,'origin_id':'K'+digest([PROTOCOL,cid,o,'CUSTOMER_OLD'])[:16].upper(),
                        'revision': 10+i+(60 if o==higher else 0)}
            memory = {'private_note':{'customer':customer,'coverage':deepcopy(observations[o])},
                      'shared_note':{'coverage':deepcopy(observations)}}
            memories[o] = memory
            sources.append({'id':cid+'-'+o,'case':cid,'role':o,'kind':'SYNTHETIC_INITIAL_STATE',
                'memory':deepcopy(memory),'source_memory_sha256':sha256(enc(memory)+b'\n').hexdigest()})
        new = deepcopy(memories[target]['private_note']['customer'])
        new.update(animal={'DOG':'CAT','CAT':'DOG'}[animal], revision=new['revision']+1,
                   origin_id='K'+digest([PROTOCOL,cid,target,'CUSTOMER_NEW'])[:16].upper())
        cases.append({'id':cid,'scene':scenes[i-1],'item':f'試設会場CU{i}', 'initial_relation':relation,'target':target,
            'direction':animal+'_TO_'+new['animal'],'channel':channel,'higher_customer_revision_owner':higher,
            'initial_memories':memories,'observations':observations,'new_customer':new})
    ordered = sorted(cases, key=lambda c: digest([PROTOCOL, 'order', c['id']]))
    runs = []; allocation = []
    for rep in (1,2):
        for i, case in enumerate(ordered if rep==1 else ordered[::-1]):
            rid = case['id']+f'-R{rep}'; runs.append({'id':rid,'case':case['id'],'replicate':rep})
            for j, stage in enumerate(STAGES):
                for role in (('A','B') if (i+j+rep)%2==0 else ('B','A')):
                    sid = rid+'-'+stage+'-'+role
                    allocation.append({'id':sid,'run':rid,'case':case['id'],'replicate':rep,'role':role,'stage':stage,
                        'source_id':case['id']+'-'+role if stage=='CHANGE' else None,
                        'parents':[] if stage=='CHANGE' else [rid+'-'+STAGES[j-1]+'-'+role],
                        'seed':int(digest([PROTOCOL,sid,'generation'])[:8],16)%2**31})
    pins = {BASE_DESIGN:BASE_SHA, **{'scripts/'+n:sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in DEPENDENCIES}}
    return {'protocol':PROTOCOL,'status':'DESIGN_FROZEN_NO_MODEL_GENERATION','condition':'LLM_CUSTOMER_G1P1_OBSERVATIONS',
        'cases':cases,'sources':sources,'runs':runs,'allocation':allocation,'source_pins':pins,
        'update_prompt':prompt,'update_schema':schema,'read_prompt':old['read_prompt'],'read_schema':old['read_schema'],'model':old['model'],
        'limits':{'updates':64,'reads':32,'max_generations':96,'seconds_including_setup':2700,'reserved_final_seconds':90,
                  'automatic_regenerations':0,'cloud_drive':'not_used','retention':'private_no_deletion_deadline'},
        'decision_rules':{'complete_pair_paths':14,'each_repeat':7,'p_value':None,'confidence_interval':None}}


def initial_requests(design):
    return [request_for(design, slot, {}) for slot in design['allocation'] if slot['stage']=='CHANGE']


def freeze():
    design = build_design(); OUT.mkdir(parents=True, exist_ok=False)
    def write(name, value): (OUT/name).write_bytes(enc(value)+b'\n')
    write('design.json', design); write('initial-requests.json', initial_requests(design))
    write('schemas.json', {'UPDATE':design['update_schema'],'READ':design['read_schema']})
    (OUT/'prompt-update.txt').write_text(design['update_prompt']); (OUT/'prompt-read.txt').write_text(design['read_prompt'])
    for s in design['sources']:
        folder = OUT/'sources'/s['id']; folder.mkdir(parents=True)
        raw = enc(s['memory'])+b'\n'; assert sha256(raw).hexdigest()==s['source_memory_sha256']
        (folder/'memory.json').write_bytes(raw)
    for name in ('customer_update_01_design.py', *DEPENDENCIES): (OUT/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    (OUT/'README.md').write_text('# CUSTOMER-UPDATE-01 固定設計\n\n合成初期ノート16冊。新通知→旧通知→本人/共同利用。\n8ケース×2反復×2役×3工程、最大96生成・準備込み45分。\n初回32入力、後続64は実保存物から作る。担当客四欄はモデル出力のまま保存。\n観測は実入力の三候補からG1P1選択・複製。実モデル生成は未実施。\n')
    write('MANIFEST.json', {str(p.relative_to(OUT)):sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file()})
    print(json.dumps({'design_sha256':sha256((OUT/'design.json').read_bytes()).hexdigest(),
        'requests_sha256':sha256((OUT/'initial-requests.json').read_bytes()).hexdigest(), 'initial_notes':16,'initial_requests':32,'max_generations':96}))


if __name__ == '__main__': freeze()
