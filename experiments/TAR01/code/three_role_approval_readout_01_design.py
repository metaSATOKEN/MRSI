"""TAR01: fixed real parents, paired readout under three receipt states."""
from copy import deepcopy
from hashlib import sha256
from itertools import permutations
import json
import random
import three_role_boundary_01_design as base

enc,digest=base.enc,base.digest
PROTOCOL='THREE-ROLE-APPROVAL-READOUT-01-v0.1'
SOURCE_SHA256='070409f87930bddd3e30976c4faaf791c87dfcc4d9a2432a12f601c59df0c1ee'
ARMS=('MISSING','HOLD','ACCEPT')
REPEATS=(1,2)
STAGES=('READ',)

def build_design(model,source):
    if digest(source)!=SOURCE_SHA256:raise ValueError('FIXED_SOURCE_CHANGED')
    assert source['model']==model and len(source['records'])==18
    for record in source['records'].values():
        for f in record['files'].values():assert sha256(f['text'].encode()).hexdigest()==f['sha256']
    units=[]
    for i,case in enumerate(source['cases']):
        orders=list(permutations(ARMS));random.Random(2026101360+i).shuffle(orders)
        for (rep,role),order in zip(((rep,r) for rep in REPEATS for r in base.ROLES),orders):
            triplet=f"TAR01-{case['id']}-{role}-R{rep}"
            seed=int(sha256(('TAR01-20261013|'+triplet).encode()).hexdigest()[:8],16)%2**31
            units.append((case['id'],role,rep,triplet,seed,order))
    random.Random(2026101369).shuffle(units)
    slots=[]
    for cid,role,rep,triplet,seed,order in units:
        for pos,arm in enumerate(order,1):
            slots.append({'id':triplet+'-'+arm,'triplet_id':triplet,'input_key':cid+'-'+role+'-'+arm,
                'stage':'READ','case':cid,'role':role,'arm':arm,'repeat':rep,'arm_position':pos,
                'parents':[],'seed':seed})
    seeds={s['seed'] for s in slots}
    assert len(slots)==54 and len(seeds)==18 and not seeds.intersection(source['old_seeds'])
    return {'protocol':PROTOCOL,'date':'2026-10-13','source':deepcopy(source),
        'cases':deepcopy(source['cases']),'prompts':{'READ':base.PROMPTS['READ']},
        'schemas':{'READ':deepcopy(base.SCHEMAS['READ'])},'allocation':slots,
        'repeats':list(REPEATS),'arms':list(ARMS),'model':model,
        'budget':{'max_generations':54,'total_seconds':1800,'reserve_seconds':90,'max_raw_bytes':16384,'retries':0},
        'unit':'3 reused triads; 27 distinct inputs x 2 technical replicates; 18 matched condition triplets.',
        'retention':'private_no_deletion_deadline','stop_rule':'One fixed pass; no retry or adaptive extension. Then paper draft regardless of outcome.'}

def source_for(design,slot):
    return next(x for x in design['source']['parent_map'] if x['case']==slot['case'])

def case_for(design,slot):
    return next(x for x in design['cases'] if x['id']==slot['case'])

def record_json(design,sid,name):
    return json.loads(design['source']['records'][sid]['files'][name]['text'])

def receipts_for(design,slot):
    src=source_for(design,slot);receipts=[]
    for role in base.ROLES:
        if slot['arm']=='MISSING' and role==src['focal_role']:continue
        vote=record_json(design,src['votes'][role],'carry-answer.json')['vote']
        receipt={'sender':role,**vote}
        if slot['arm']=='HOLD' and role==src['focal_role']:receipt['decision']='HOLD'
        receipts.append(receipt)
    return receipts

def payload_for(design,slot,states=None):
    src=source_for(design,slot);role=slot['role']
    # Reuse the actual prior vote payload; replace only stage schema, own note
    # source (always FORM), and append the controlled receipt projection.
    old=record_json(design,src['votes'][role],'input.json')
    p=json.loads(old['messages'][1]['content'])
    assert set(p)=={'holder','scene','schema','experiences','own_experience_summary','resource_count','candidates','proposal','own_saved_note'}
    p['schema']=deepcopy(design['schemas']['READ'])
    p['own_saved_note']=record_json(design,src['forms'][role],'carry-answer.json')['own']
    p['receipts']=receipts_for(design,slot)
    return p

def request_for(design,slot,states=None):
    return {'id':slot['id'],'seed':slot['seed'],'messages':[
        {'role':'system','content':design['prompts']['READ']},
        {'role':'user','content':enc(payload_for(design,slot)).decode()}]}

def binding_for(design,slot):
    src=source_for(design,slot);sid=src['forms'][slot['role']]
    chosen=[sid,*src['votes'].values()]
    return {'archive_sha256':design['source']['archives']['TCV02']['sha256'],
        'own_form_id':sid,'parent_files':{p:{n:f['sha256'] for n,f in design['source']['records'][p]['files'].items()} for p in chosen},
        'focal_role':src['focal_role'],'condition':slot['arm'],
        'transformation':{'MISSING':'omit_focal_receipt','HOLD':'replace_focal_decision_ACCEPT_with_HOLD','ACCEPT':'unchanged_receipt_projection'}[slot['arm']],
        'constructed_HOLD':slot['arm']=='HOLD','receipt_order':list(base.ROLES),
        'receipts_sha256':digest(receipts_for(design,slot)),'payload_sha256':digest(payload_for(design,slot))}

def verification_template(design,slot,request):return dict(request)
