"""TCV02: new triads, one shared formation per role, unchanged voting conditions."""
from copy import deepcopy
from hashlib import sha256
import json
import random
import three_role_boundary_01_design as base
import three_role_comparison_vote_01_design as previous

enc, digest = base.enc, base.digest
PROTOCOL = 'THREE-ROLE-COMPARISON-VOTE-02-v0.1'
SOURCE_SHA256 = '37decbb06f18db7d776b0aa56f8d36b0e65885a3713280fa8014bb9e85b100ff'
ARMS, REPEATS = previous.ARMS, previous.REPEATS
STAGES = ('FORM', 'VOTE')
COMPARE_INSTRUCTION = previous.COMPARE_INSTRUCTION
schema_for = previous.schema_for


def materials():
    specs = [
        ('N01', ('B','A','C'), 'DIGITAL', [(35,24),(29,24),(16,32)], '地域の修理相談会'),
        ('N02', ('C','B','A'), 'PAPER', [(31,20),(28,23),(18,33)], '公園の体験受付'),
        ('N03', ('A','C','B'), 'DIGITAL', [(33,20),(30,24),(17,28)], '夜間の学習案内所'),
    ]
    cases=[]
    for idx,(cid,order,scarce,totals,scene) in enumerate(specs):
        other=next(m for m in base.MEDIA if m!=scarce);rows=[]
        for role,(scarce_n,other_n) in zip(order,totals):
            for session in (1,2):
                values={}
                for medium,total in [(scarce,scarce_n),(other,other_n)]:
                    first=max(total-20,min(20,total//2+(2 if medium==scarce else -2)))
                    values[medium]={'success':first if session==1 else total-first,'trials':20}
                rows.append({'id':'E'+sha256(f'TCV02|{cid}|{role}|{session}'.encode()).hexdigest()[:10],
                             'owner':role,'session':session,'observed':values})
        candidates=[]
        for number,recipient in enumerate(order[:2]):
            candidates.append({'candidate_id':['C1','C2'][(number+idx+1)%2],
                'assignment':{r:scarce if r==recipient else other for r in base.ROLES}})
        random.Random(2026101340+idx).shuffle(candidates)
        cases.append({'id':cid,'scene':scene,'role_order':list(order),
            'resource_count':{scarce:1,other:2},'experiences':rows,'candidates':candidates})
    return cases


def form_id(cid,role):return f'TCV02-{cid}-FORM-{role}'


def build_design(model,source):
    if digest(source)!=SOURCE_SHA256:raise ValueError('FIXED_SOURCE_CHANGED')
    assert model==source['model'] and source['cases']==materials()
    slots=[]
    for case in source['cases']:
        for role in case['role_order']:
            sid=form_id(case['id'],role)
            slots.append({'id':sid,'stage':'FORM','case':case['id'],'role':role,'arm':'FORM',
                'repeat':0,'branch':None,'snapshot':None,'parents':[],
                'seed':int(sha256(('TCV02-20261013|'+sid).encode()).hexdigest()[:8],16)%2**31})
    for rep in REPEATS:
        rng=random.Random(2026101350+rep);order=deepcopy(source['items']);rng.shuffle(order)
        firsts=[True]*9+[False]*9;rng.shuffle(firsts)
        for item,first in zip(order,firsts):
            pair=f"TCV02-{item['key']}-R{rep}"
            seed=int(sha256(('TCV02-20261013|'+pair).encode()).hexdigest()[:8],16)%2**31
            for pos,arm in enumerate(ARMS if first else ARMS[::-1]):
                slots.append({'id':pair+'-'+arm,'pair_id':pair,'input_key':item['key'],'stage':'VOTE',
                    'arm':arm,'arm_position':pos+1,'case':item['case'],'role':item['role'],
                    'branch':item['branch'],'repeat':rep,'snapshot':None,
                    'parents':[form_id(item['case'],item['role'])],'seed':seed})
    seeds={s['seed'] for s in slots}
    assert len(slots)==117 and len(seeds)==63 and not seeds.intersection(source['old_seeds'])
    return {'protocol':PROTOCOL,'date':'2026-10-13','source':deepcopy(source),'cases':deepcopy(source['cases']),
        'schemas':{**{a:schema_for(a) for a in ARMS},'FORM':deepcopy(base.SCHEMAS['FORM'])},
        'prompts':{'FORM':base.PROMPTS['FORM'],'VOTE':base.PROMPTS['VOTE']},
        'compare_instruction':COMPARE_INSTRUCTION,'allocation':slots,'repeats':list(REPEATS),
        'arms':list(ARMS),'model':model,'budget':{'max_generations':117,'total_seconds':1800,
            'reserve_seconds':90,'max_raw_bytes':16384,'retries':0},
        'unit':'3 new triads; 9 single FORM outputs shared across 108 VOTE slots; 54 matched pairs.',
        'retention':'private_no_deletion_deadline','stop_rule':'One fixed pass; no retry, repair, or old-outcome pooling.'}


def case_for(design,slot):return next(c for c in design['cases'] if c['id']==slot['case'])


def payload_for(design,slot,states=None):
    case=case_for(design,slot);role=slot['role'];stage=slot['stage']
    payload={'holder':role,'scene':case['scene'],'schema':deepcopy(design['schemas'][slot['arm']]),
        'experiences':deepcopy([r for r in case['experiences'] if stage!='FORM' or r['owner']==role]),
        'own_experience_summary':base.own_summary(case,role)}
    if stage=='FORM':return payload
    table=base.candidate_table(case);ranked=sorted(table,key=lambda c:c['expected_total'],reverse=True)
    candidate=ranked[0 if slot['branch']=='HIGHER' else 1]
    proposal='P'+sha256(f"TCV02|{case['id']}|{candidate['candidate_id']}".encode()).hexdigest()[:8]
    parent=slot['parents'][0]
    if states is None or states.get(parent) is None:raise ValueError('OWN_PARENT_MISSING')
    payload.update(resource_count=deepcopy(case['resource_count']),candidates=table,
        proposal={'proposal_id':proposal,'candidate_id':candidate['candidate_id']},
        own_saved_note=deepcopy(states[parent]['own']))
    return payload


def request_for(design,slot,states=None):
    instruction=design['prompts'][slot['stage']]
    if slot['arm']=='COMPARE':instruction+=design['compare_instruction']
    return {'id':slot['id'],'seed':slot['seed'],'messages':[
        {'role':'system','content':instruction},
        {'role':'user','content':enc(payload_for(design,slot,states)).decode()}]}


def verification_template(design,slot,request):return dict(request)
