"""SX02 continuation design and pure scoring. Offline standard library only."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import zipfile

import role_shared_use_01_design as ru
import self_update_exchange_01_scoring as sx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study2/designs/self-update-exchange-02-20260925'
PROTOCOL = 'SELF-UPDATE-EXCHANGE-02/v1'
STAGES = ('SELF', 'EXCHANGE', 'DELAY', 'READ')
RU_DESIGN = 'study2/designs/role-shared-use-01-20260925/design.json'
RU_DESIGN_SHA = '74188ddeabadad000b3cf03b5710ccb1845e15ecdb8c1166579e8552b4ede923'
RU_RESULT = 'throughline/audits/role-shared-use-01-result-20260925/npp-ru01-result-20260925-131522-816fc642.zip'
RU_RESULT_SHA = '6333e83dfe41d717b27183aad33d4bf2df8f9082001253cc0af4011e7ede6121'
DEPENDENCIES = ('role_shared_use_01_design.py', 'self_update_exchange_01_scoring.py', *ru.DEPENDENCIES)
base = sx.base
enc = base.enc
digest = sx.digest
other = sx.other


def expected_memory(case, role, stage):
    """Scoring oracle only. Actual later inputs are supplied by saved parent notes."""
    if stage not in STAGES: raise ValueError('STAGE')
    want = deepcopy(case['baseline_memories'][role])
    want['private_note']['coverage'] = deepcopy(case['next_rows'][role])
    want['shared_note']['coverage'][role] = deepcopy(case['next_rows'][role])
    if stage != 'SELF': want['shared_note']['coverage'][other(role)] = deepcopy(case['next_rows'][other(role)])
    return want


def update_payload(case, role, stage, previous, peer=None):
    """Every stage requires actual saved memory, including the frozen original for SELF."""
    partner = other(role)
    if previous is None: raise ValueError('DEPENDENCY_MISSING:OWN')
    if stage == 'SELF':
        if peer is not None: raise ValueError('SELF_HAS_NO_PEER')
        notice = deepcopy(case['next_rows'][role])
    elif stage == 'EXCHANGE':
        if peer is None: raise ValueError('DEPENDENCY_MISSING:PEER')
        notice = deepcopy(peer['private_note']['coverage'])
        if notice['observer'] != partner: raise ValueError('EXCHANGE_OWNER_CONTRACT')
    elif stage == 'DELAY':
        if peer is not None: raise ValueError('DELAY_HAS_NO_PEER')
        target = role if case['delay_relation'] == 'SELF' else partner
        notice = deepcopy(case['baseline_rows'][target])
    else: raise ValueError('NOT_UPDATE_STAGE')
    memory = deepcopy(previous)
    entries = [('PRIVATE.coverage', memory['private_note']['coverage']),
               ('GROUP.coverage.A', memory['shared_note']['coverage']['A']),
               ('GROUP.coverage.B', memory['shared_note']['coverage']['B']), ('NOTICE', notice)]
    entries.sort(key=lambda pair: digest([PROTOCOL, case['id'], role, stage, pair[0]]))
    payload = {'holder': role, 'scene': case['scene'], 'item': case['item'],
        'records': [{'record_id':'PRIVATE','body':memory['private_note']},
                    {'record_id':'GROUP','body':memory['shared_note']}],
        'incoming_notice': notice,
        'row_catalog':[{'row_id':'C'+str(i+1),'location':location,'row':deepcopy(row)} for i,(location,row) in enumerate(entries)]}
    return payload


def slot_payload(design, slot, states):
    """The only input path: frozen actual source, then actual outputs. No oracle fallback."""
    case = next(c for c in design['cases'] if c['id'] == slot['case'])
    role, stage = slot['role'], slot['stage']
    if stage == 'SELF':
        source = next(s for s in design['sources'] if s['id'] == slot['source_id'])
        return update_payload(case, role, stage, source['memory'])
    parents = [states.get(pid) for pid in slot['parents']]
    if not parents or any(value is None for value in parents): raise ValueError('DEPENDENCY_MISSING')
    if stage == 'READ': return ru.input_payload({'role':role,'scene':case['scene'],'item':case['item']}, parents[0])
    return update_payload(case, role, stage, parents[0], parents[1] if stage == 'EXCHANGE' else None)


def request_for(design, slot, states):
    payload = slot_payload(design, slot, states)
    return {'id':slot['id'],'seed':slot['seed'],'messages':[
        {'role':'system','content':design['read_prompt'] if slot['stage']=='READ' else design['update_prompt']},
        {'role':'user','content':'\n資料JSON:\n'+enc(payload).decode()}]}


def score_memory(memory, case, role, stage):
    if memory is None:
        return {'format_valid':None,'customer':None,'self_row':None,'partner_row':None,'shared':None,'joint':None}
    want = expected_memory(case, role, stage)
    return {'format_valid':True,
        'customer':memory['private_note']['customer']==want['private_note']['customer'],
        'self_row':memory['private_note']['coverage']==want['private_note']['coverage'],
        'partner_row':memory['shared_note']['coverage'][other(role)]==want['shared_note']['coverage'][other(role)],
        'shared':memory['shared_note']==want['shared_note'],'joint':memory==want}


def evaluate_update(raw, payload, design, case, role, stage, finish_reason='EOS'):
    """Unmodified frozen G1P1; preserve model-written customer even when wrong."""
    derived = sx.derive_update(raw, payload, design['update_schema'], finish_reason)
    score = score_memory(derived['memory'], case, role, stage)
    score.update(proposal_score=score_memory(derived['proposal'],case,role,stage) if derived['proposal'] is not None else None,
                 normalization=derived['receipt'], error=derived['error'])
    if derived['memory'] is None: score['format_valid'] = False
    return derived, score


def score_read(raw, memory, case, role, schema, finish_reason='EOS'):
    keys = ('subject_note','animal_note','four_note_exact','channel_note','customer_latest','four_latest','channel_latest','joint')
    if memory is None:
        return {'format_valid':None, **{k:None for k in keys},'answer':None,'actions':None,'normalization':{'status':'UNRESOLVED','reason':'DEPENDENCY_MISSING'}}
    payload = ru.input_payload({'role':role,'scene':case['scene'],'item':case['item']}, memory)
    score = ru.score_response(raw,payload,schema,finish_reason)
    result = {'format_valid':score['format_valid'], **{k:None for k in keys},
              'answer':score['answer'],'actions':score['actions'],'normalization':score['normalization'],'errors':score['errors']}
    if not score['format_valid']: return result
    wanted = case['baseline_memories'][role]['private_note']['customer']
    expected_four = {o:{k:case['next_rows'][o][k] for k in ('paper','digital')} for o in ('A','B')}
    result.update(subject_note=score['subject'],animal_note=score['animal'],four_note_exact=score['four_exact'],channel_note=score['channel'],
        customer_latest=score['answer']['customer']=={k:wanted[k] for k in ('subject','animal')},
        four_latest=score['answer']['coverage']==expected_four,
        channel_latest=score['actions']['channel']==base.compute_channel(expected_four))
    result['joint'] = all(result[k] for k in keys if k != 'joint')
    return result


def summarize(design, outcomes):
    if set(outcomes)-{s['id'] for s in design['allocation']}: raise ValueError('UNEXPECTED_RESPONSE')
    paths=[];pairs=[]
    for run in design['runs']:
        values=[outcomes.get(run['id']+'-'+stage+'-'+role,{}) for stage in STAGES for role in ('A','B')]
        success=all(v.get('joint') is True for v in values) if all(v.get('format_valid') is True for v in values) else None
        paths.append({**run,'success':success})
        reads=[outcomes.get(run['id']+'-READ-'+role,{}) for role in ('A','B')]
        entry={**run,'different_animals':None,'same_channel':None,'both_correct':None,'channel_changed_from_baseline':None}
        if all(v.get('format_valid') is True for v in reads):
            case=next(c for c in design['cases'] if c['id']==run['case'])
            a,b=[v['actions'] for v in reads]
            entry.update(different_animals=a['card_animal']!=b['card_animal'],same_channel=a['channel']==b['channel'],
                both_correct=all(v['joint'] for v in reads),
                channel_changed_from_baseline=all(v['actions']['channel']!=case['baseline_channel'] for v in reads))
        pairs.append(entry)
    total=base.counts(p['success'] for p in paths)
    reps={str(i):base.counts(p['success'] for p in paths if p['replicate']==i) for i in (1,2)}
    tests=[(total,design['decision_rules']['complete_pair_paths'])]+[(c,design['decision_rules']['each_repeat']) for c in reps.values()]
    status='MET' if all(c['correct']>=n for c,n in tests) else 'NOT_MET' if any(c['correct']+c['unresolved']<n for c,n in tests) else 'INCONCLUSIVE'
    components={}
    for stage in STAGES:
        selected=[outcomes.get(s['id'],{}) for s in design['allocation'] if s['stage']==stage]
        names=('joint','subject_note','animal_note','four_note_exact','channel_note','customer_latest','four_latest','channel_latest') if stage=='READ' else ('joint','customer','self_row','partner_row','shared')
        components[stage]={k:base.counts(v.get(k) for v in selected) for k in names}
        if stage!='READ': components[stage]['proposal']={k:base.counts((v.get('proposal_score') or {}).get(k) for v in selected) for k in names}
    return {'protocol':PROTOCOL,'materials':8,'pair_runs':16,'response_slots':128,'path':total,'by_repeat':reps,
        'criterion_status':status,'path_fraction_missing_bounds':[total['correct']/16,(total['correct']+total['unresolved'])/16],
        'paths':paths,'components':components,'read_pairs':pairs,
        'read_pair_metrics':{k:base.counts(v[k] for v in pairs) for k in ('different_animals','same_channel','both_correct','channel_changed_from_baseline')},
        'p_value':None,'confidence_interval':None}


def build_design():
    for name,expected in [(RU_DESIGN,RU_DESIGN_SHA),(RU_RESULT,RU_RESULT_SHA)]:
        if sha256((ROOT/name).read_bytes()).hexdigest()!=expected: raise ValueError('SOURCE_CHANGED:'+name)
    read_design=json.loads((ROOT/RU_DESIGN).read_bytes())
    old,sources=ru.read_sources()
    for source in sources:
        for k in ('id','case','run'):source[k]=source[k].replace('RU01-','SX02-')
    source_by={(s['case'],s['replicate'],s['role']):s for s in sources}
    old_cases={c['id'].replace('SX01-','SX02-'):c for c in old['cases']}
    cases=[]
    for cid in sorted(old_cases):
        oc=old_cases[cid];memories={o:deepcopy(source_by[cid,1,o]['memory']) for o in ('A','B')}
        for o in ('A','B'):
            if memories[o]!=source_by[cid,2,o]['memory']:raise ValueError('BASELINE_REPEATS_DIFFER')
        rows=deepcopy(memories['A']['shared_note']['coverage'])
        if rows!=memories['B']['shared_note']['coverage']:raise ValueError('BASELINE_GROUP_DIFFER')
        baseline=base.compute_channel(rows)
        available=[o for o in ('A','B') if rows[o]['paper']==rows[o]['digital']=='ALL']
        if len(available)!=1 or baseline not in ('PAPER','DIGITAL'):raise ValueError('BASELINE_VALUE_PATTERN')
        next_rows={}
        for o in ('A','B'):
            row=deepcopy(rows[o]);row.update(paper='ALL',digital='ALL',revision=rows[o]['revision']+1,
                origin_id='Y'+digest([PROTOCOL,cid,o,'NEXT_OBSERVATION'])[:16].upper())
            if o==available[0]:row[baseline.lower()]='NOT_ALL'
            next_rows[o]=row
        cases.append({'id':cid,'scene':oc['scene'],'item':oc['item'],'baseline_memories':memories,'baseline_rows':rows,
            'next_rows':next_rows,'baseline_channel':baseline,'latest_channel':base.compute_channel(next_rows),
            'direction':baseline+'_TO_'+base.compute_channel(next_rows),'delay_relation':oc['delay_relation'],
            'higher_revision_owner':oc['higher_revision_owner']})
    ordered=sorted(cases,key=lambda c:digest([PROTOCOL,'order',c['id']]))
    runs=[];allocation=[]
    for rep in (1,2):
        for i,case in enumerate(ordered if rep==1 else ordered[::-1]):
            rid=case['id']+f'-R{rep}';runs.append({'id':rid,'case':case['id'],'replicate':rep})
            for j,stage in enumerate(STAGES):
                roles=('A','B') if (i+j+rep)%2==0 else ('B','A')
                for role in roles:
                    sid=rid+'-'+stage+'-'+role
                    parents=[] if stage=='SELF' else [rid+'-'+STAGES[j-1]+'-'+role]
                    if stage=='EXCHANGE':parents.append(rid+'-SELF-'+other(role))
                    allocation.append({'id':sid,'run':rid,'case':case['id'],'replicate':rep,'role':role,'stage':stage,
                        'source_id':source_by[case['id'],rep,role]['id'] if stage=='SELF' else None,
                        'parents':parents,'seed':int(digest([PROTOCOL,sid,'generation'])[:8],16)%2**31})
    pins={RU_DESIGN:RU_DESIGN_SHA,RU_RESULT:RU_RESULT_SHA,ru.SOURCE:ru.SOURCE_SHA}
    for name in DEPENDENCIES:pins['scripts/'+name]=sha256((ROOT/'scripts'/name).read_bytes()).hexdigest()
    return {'protocol':PROTOCOL,'status':'DESIGN_FROZEN_NO_MODEL_GENERATION','condition':'G1P1_FIXED',
        'source_archive':ru.SOURCE,'source_archive_sha256':ru.SOURCE_SHA,'source_design_sha256':ru.SOURCE_DESIGN_SHA,
        'readout_result_reference':RU_RESULT,'readout_result_sha256':RU_RESULT_SHA,'sources':sources,
        'cases':cases,'runs':runs,'allocation':allocation,'source_pins':pins,
        'update_prompt':old['update_prompt'],'update_schema':old['update_schema'],
        'read_prompt':read_design['prompt'],'read_schema':read_design['schema'],'model':old['model'],
        'limits':{'updates':96,'reads':32,'max_generations':128,'seconds_including_setup':3600,
            'reserved_final_seconds':90,'automatic_regenerations':0,'cloud_drive':'not_used','retention':'private_no_deletion_deadline'},
        'decision_rules':{'complete_pair_paths':14,'each_repeat':7,'p_value':None,'confidence_interval':None}}


def initial_requests(design):
    return [request_for(design,slot,{}) for slot in design['allocation'] if slot['stage']=='SELF']


def freeze():
    design=build_design();OUT.mkdir(parents=True,exist_ok=False)
    def write(n,v):(OUT/n).write_bytes(enc(v)+b'\n')
    write('design.json',design);write('initial-requests.json',initial_requests(design))
    write('schemas.json',{'UPDATE':design['update_schema'],'READ':design['read_schema']})
    (OUT/'prompt-update.txt').write_text(design['update_prompt']);(OUT/'prompt-read.txt').write_text(design['read_prompt'])
    with zipfile.ZipFile(ROOT/ru.SOURCE) as z:
        for s in design['sources']:
            folder=OUT/'sources'/s['id'];folder.mkdir(parents=True)
            for kind in ('memory','result'):
                raw=z.read(s['source_'+kind+'_path']);assert sha256(raw).hexdigest()==s['source_'+kind+'_sha256']
                (folder/(kind+'.json')).write_bytes(raw)
    for name in ('self_update_exchange_02_design.py',*DEPENDENCIES):(OUT/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    (OUT/'README.md').write_text('# SELF-UPDATE-EXCHANGE-02 固定設計\n\nSX01の実保存32冊から本人更新→実保存行交換→旧版通知→本人/共同の同時利用。\n8既知材料×二反復×二役×4工程、最大128生成・60分案。\n初回32入力を固定し、後続96入力は今回の実保存物から組む。\nUPDATE指示と保存構成はSX01、READ指示/schemaはRU01から継承。\n新通知は人物別revision+1と新しい元IDを持ち、共同案内を前回から反転。\nColab接続・実モデル生成は未実施。\n')
    write('MANIFEST.json',{str(p.relative_to(OUT)):sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file()})
    print(json.dumps({'design_sha256':sha256((OUT/'design.json').read_bytes()).hexdigest(),
        'requests_sha256':sha256((OUT/'initial-requests.json').read_bytes()).hexdigest(),'source_notes':32,'initial_requests':32,'max_generations':128}))


if __name__=='__main__':freeze()
