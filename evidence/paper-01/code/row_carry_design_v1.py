"""ROW-CARRY-01 offline design: rewrite vs selecting whole shared rows. No transport."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import random
import shared_merge_02_design_v1 as prior

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'study2/designs/row-carry-01-20260919'
SOURCE = ROOT / 'study2/runs/shared-merge-02-prepared-20260919'
CONDITIONS = ('REWRITE', 'SELECT')
ROLES = ('A', 'B')
SEED = 2026091905
bytes_json = prior.json_bytes
tri = prior.tri_and


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def schemas():
    rw = prior.schemas()['MERGE']
    select = deepcopy(rw)
    pointer = prior.obj({'record_id': prior.ID, 'observer': prior.enum('A','B')})
    select['properties']['memory']['properties']['shared_note']['properties']['coverage'] = prior.obj({'A': pointer, 'B': pointer})
    return {'REWRITE': rw, 'SELECT': select, 'PROBE': prior.schemas()['PROBE']}


def prompt(stage, condition):
    if stage == 'PROBE':
        return prior.PROMPTS['PROBE']+'\n'+prior.COMMON+'\n'+json.dumps(schemas()['PROBE'], ensure_ascii=False, separators=(',',':'))
    common = prior.PROMPTS['MERGE']+'\n'+prior.COMMON
    common += '\nPRIVATEのcoverageは本人の一行、LOCAL_GROUPとPARTNER_GROUPのcoverageはA/Bの各行です。'
    if condition == 'REWRITE':
        treatment = 'shared_note.coverageのA/Bそれぞれに、採用する観測のobserver・paper・digital・origin_id・revisionを記述してください。private_noteとread_receiptもschemaどおり出力してください。'
    else:
        treatment = 'shared_note.coverageのA/Bそれぞれには、採用する入力行の場所だけをrecord_idとobserverで指定してください。保存係はその場所の観測行全体を変更せず複製します。PRIVATEを指定する場合は実在する本人のobserverを指定します。観測の値・版・元IDをこの指定欄に書き足さないでください。private_noteとread_receiptは自分でschemaどおり出力してください。read_receiptの参照は選択後に保存される観測内容を根拠づける記録名です。'
    return common+'\n'+treatment+'\n'+json.dumps(schemas()[condition],ensure_ascii=False,separators=(',',':'))


def candidates(payload):
    """Only available records; no expected answer, revision ranking or owner filtering."""
    result = {}
    for record in payload['records']:
        alias, body = record['record_id'], record['body']
        if alias == 'PRIVATE':
            row = body['coverage'];result[(alias,row['observer'])] = row
        elif alias in ('LOCAL_GROUP','PARTNER_GROUP'):
            for owner,row in body['coverage'].items():result[(alias,owner)] = row
    return result


def resolve(value, payload):
    """Pure literal selection. Wrong/stale existing rows are copied, never repaired."""
    output = deepcopy(value);bindings=[];errors=[];available=candidates(payload)
    for destination in ROLES:
        pointer = prior.leaf(value,'memory','shared_note','coverage',destination)
        key = (pointer.get('record_id'),pointer.get('observer')) if type(pointer) is dict else (None,None)
        # Type validation precedes this lookup; no eval, filesystem paths or searches.
        key_ok = all(type(x) is str for x in key)
        selected = available.get(key) if key_ok else None
        if selected is None:
            errors.append('SELECTION_NOT_CURRENT:'+destination)
        output['memory']['shared_note']['coverage'][destination] = deepcopy(selected)
        bindings.append({'destination':destination,'selected':pointer,'body_sha256':sha256(bytes_json(selected)).hexdigest() if selected is not None else None})
    return output,bindings,errors


def evaluate(material, slot, raw, payload):
    stage,condition = slot['stage'],slot['condition']
    if stage == 'PROBE' or condition == 'REWRITE':
        score=prior.score(material,slot,raw,payload);checked=prior.inspect(raw,payload,stage)
        return {'score':score,'gate':checked['gate'],'value':checked['value'],'normalized':checked['value'],'bindings':[], 'selection_errors':[],'selection_shape_errors':[]}
    value=None;shape_errors=[];errors=[];bindings=[];normalized=None
    if raw is not None:
        if len(raw)>4096:shape_errors=['OUTPUT_BYTES']
        else:
            try:value=prior.parse(raw)
            except (ValueError,UnicodeError,RecursionError):shape_errors=['JSON']
        if value is not None:
            shape_errors += prior.shape(value,schemas()['SELECT'])
            # Preserve independently readable components when a selector is malformed.
            normalized=deepcopy(value)
            for owner in ROLES:
                selection=prior.leaf(value,'memory','shared_note','coverage',owner)
                pointer_rule=schemas()['SELECT']['properties']['memory']['properties']['shared_note']['properties']['coverage']['properties'][owner]
                if prior.shape(selection,pointer_rule):
                    try:normalized['memory']['shared_note']['coverage'][owner]=None
                    except (KeyError,TypeError):pass
            # Resolve each well-shaped selector independently, even if another field
            # is malformed. This preserves known failures under partial missingness.
            available=candidates(payload)
            for owner in ROLES:
                pointer=prior.leaf(value,'memory','shared_note','coverage',owner)
                rule=schemas()['SELECT']['properties']['memory']['properties']['shared_note']['properties']['coverage']['properties'][owner]
                if not prior.shape(pointer,rule):
                    selected=available.get((pointer['record_id'],pointer['observer']))
                    normalized['memory']['shared_note']['coverage'][owner]=deepcopy(selected)
                    if selected is None:errors.append('SELECTION_NOT_CURRENT:'+owner)
                    bindings.append({'destination':owner,'selected':pointer,'body_sha256':sha256(bytes_json(selected)).hexdigest() if selected is not None else None})
    norm_raw=bytes_json(normalized) if normalized is not None else None
    score=prior.score(material,slot,norm_raw,payload)
    score['strict']=tri([score['strict'],False if errors else None if shape_errors or raw is None else True])
    normalized_gate=prior.inspect(norm_raw,payload,stage)['gate']
    gate='PASS' if not shape_errors and not errors and normalized_gate=='PASS' else 'REJECT'
    return {'score':score,'gate':gate,'value':value,'normalized':normalized,'bindings':bindings,'selection_errors':errors,'selection_shape_errors':shape_errors}


def slot_id(group,condition,role,stage):return f'{group}-{condition}-{stage}-{role}'


def input_for(slot, roots, states):
    if slot['stage']=='MERGE':return deepcopy(roots[slot['group']][slot['role']])
    memory=states[slot['dependencies'][0]]
    source=roots[slot['group']][slot['role']]
    return {'scene':source['scene'],'item':source['item'],'holder':slot['role'],
            'records':[{'record_id':'PRIVATE','body':deepcopy(memory['private_note'])},
                       {'record_id':'GROUP','body':deepcopy(memory['shared_note'])}]}


def ideal(material,slot):
    value=prior.ideal(material,slot)
    if slot['stage']=='MERGE' and slot['condition']=='SELECT':
        role=slot['role']
        value['memory']['shared_note']['coverage']={r:{'record_id':'LOCAL_GROUP' if r==role else 'PARTNER_GROUP','observer':r} for r in ROLES}
    return value


def aggregate(slots, scores):
    groups=sorted({s['group'] for s in slots});result={}
    for mode in ('strict','content'):
        arms={}
        for cond in CONDITIONS:
            by_group={g:tri(scores.get(s['id'],{}).get(mode) for s in slots if s['group']==g and s['condition']==cond) for g in groups}
            values=list(by_group.values());arms[cond]={'groups':by_group,'bounds':[values.count(True)/4,(values.count(True)+values.count(None))/4]}
        r,s=arms['REWRITE']['bounds'],arms['SELECT']['bounds'];delta=[s[0]-r[1],s[1]-r[0]]
        result[mode]={'conditions':arms,'delta':delta,'paired_groups':{g:{cond:arms[cond]['groups'][g] for cond in CONDITIONS} for g in groups}}
    lo,hi=result['strict']['delta']
    result['prediction_status']='MET_IN_FIXED_SAMPLE' if lo>=.25 else 'NOT_MET_IN_FIXED_SAMPLE' if hi<.25 else 'INCONCLUSIVE'
    return result


def build():
    source_seals=[('study2/checks/shared-merge-02-live-20260919/live-completion.json',ROOT,'5a033080956b459c462498c4cc90538b3f6b3d350dd23e462c2f290b29ddf150'),
                  ('study2/runs/shared-merge-02-prepared-20260919/completion.json',SOURCE,'8d9fc3ac88ae6ac37113623f0147bc65c4ca1a285dfa5655776bd9e1fca503d5')]
    anchors=[]
    for name,base,expected in source_seals:
        path=ROOT/name;assert digest(path)==expected
        sealed=json.loads(path.read_text())['files_sha256']
        for n,v in sealed.items():assert digest(base/n)==v,n
        anchors.append({'file':name,'sha256':expected,'verified_files':len(sealed)})
    old=json.loads((SOURCE/'configuration.json').read_text());materials={};roots={};bindings=[]
    for idx,(old_group,material) in enumerate(sorted(old['materials'].items()),1):
        group=f'RC01-G{idx:02}';materials[group]=deepcopy(material);materials[group]['group']=group;materials[group]['source_group']=old_group;roots[group]={}
        for role in ROLES:
            path=SOURCE/'states'/f'{old_group}-MERGE-{role}-incoming.json';raw=path.read_bytes();payload=json.loads(raw)
            archived=D/'source-inputs'/path.name;archived.parent.mkdir(parents=True,exist_ok=True)
            with archived.open('xb') as f:f.write(raw)
            assert len(candidates(payload))==5
            roots[group][role]=payload
            bindings.append({'group':group,'role':role,'source':str(path.relative_to(ROOT)),'archived':str(archived.relative_to(ROOT)),'sha256':digest(path)})
    rng=random.Random(SEED);slots=[]
    for stage in ('MERGE','PROBE'):
        cases=[(g,r) for g in materials for r in ROLES];rng.shuffle(cases)
        for group,role in cases:
            idx=int(group[-2:]);order=CONDITIONS if (idx+(role=='B'))%2==0 else CONDITIONS[::-1]
            # Flip ordering in the later stage; both roles have 2/2 in each stage.
            if stage=='PROBE':order=order[::-1]
            for cond in order:
                slots.append({'id':slot_id(group,cond,role,stage),'group':group,'role':role,'condition':cond,'stage':stage,
                              'dependencies':[] if stage=='MERGE' else [slot_id(group,cond,role,'MERGE')]})
    write(D/'materials.json',materials);write(D/'root-payloads.json',roots);write(D/'source-bindings.json',bindings);write(D/'source-seals.json',anchors)
    write(D/'allocation.json',slots);write(D/'response-schemas.json',schemas())
    for name,stage,cond in [('merge-rewrite','MERGE','REWRITE'),('merge-select','MERGE','SELECT'),('probe','PROBE','REWRITE')]:
        with (D/f'prompt-{name}.txt').open('x') as f:f.write(prompt(stage,cond)+'\n')
    lengths=[]
    for slot in slots:
        if slot['stage']=='MERGE':
            payload=input_for(slot,roots,{});write(D/'initial-inputs'/(slot['id']+'.json'),payload)
            text=prompt('MERGE',slot['condition'])+'\n資料JSON:\n'+bytes_json(payload).decode();lengths.append(len(text.encode()))
    write(D/'config.json',{'protocol':'ROW-CARRY-01','seed':SEED,'groups':4,'case_holders':8,'conditions':list(CONDITIONS),'initial_inputs':16,'dependent_slots':16,'planned_slots':32,'max_requests_candidate':36,'max_seconds_candidate':1800,'model_candidate':'gpt-5.6-luna','reasoning_candidate':'medium','primary':'Delta of end-to-end all-four-slot group success, SELECT minus REWRITE','prediction_delta_at_least':.25,'new_model_calls':0,'new_auth_calls':0,'transport_connected':False,'execution_authorized':False,'retention_until':'2026-10-12T17:41:23+09:00','initial_input_text_bytes':{'sum':sum(lengths),'max':max(lengths)}})
    print(json.dumps({'groups':4,'roots':16,'dependent':16,'initial_text_bytes':sum(lengths),'largest':max(lengths),'model_calls':0}))


if __name__=='__main__':build()
