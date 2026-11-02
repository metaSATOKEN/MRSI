"""TVR01: repeat all 18 actual TB01 vote inputs, without rebuilding messages."""
from copy import deepcopy
from hashlib import sha256
import json
import random
import three_role_boundary_01_design as base

enc, digest = base.enc, base.digest
SOURCE_SHA256 = '81b8d080cf0b75d65e4ce3757bbf105a575a7fd34763efc60678d3b354716c46'
PROTOCOL = 'THREE-ROLE-VOTE-REPEAT-01-v0.1'
REPEATS = (1, 2, 3)
STAGES = ('VOTE',)


def build_design(model, source):
    if digest(source) != SOURCE_SHA256:
        raise ValueError('FIXED_SOURCE_CHANGED')
    assert model == source['model']
    assert len(source['items']) == 18
    slots = []
    for rep in REPEATS:
        order = deepcopy(source['items'])
        random.Random(2026101310 + rep).shuffle(order)
        for item in order:
            sid = f"TVR01-{item['key']}-R{rep}"
            seed = int(sha256(('TVR01-20261013|' + sid).encode()).hexdigest()[:8],16) % 2**31
            slots.append({'id':sid,'input_key':item['key'],'stage':'VOTE', 'case':item['case'],
                          'role':item['role'],'branch':item['branch'],'repeat':rep,'snapshot':None,
                          'parents':[],'seed':seed})
    seeds = [s['seed'] for s in slots]
    assert len(set(seeds)) == 54 and not set(seeds).intersection(source['old_seeds'])
    return {'protocol':PROTOCOL,'date':'2026-10-13','source':deepcopy(source),
            'cases':deepcopy(source['cases']),'schemas':deepcopy(source['schemas']),
            'prompts':deepcopy(source['prompts']),'allocation':slots,'repeats':list(REPEATS),'model':model,
            'budget':{'max_generations':54,'total_seconds':1800,'reserve_seconds':90,'max_raw_bytes':16384,'retries':0},
            'retention':'private_no_deletion_deadline',
            'stop_rule':'One fixed pass. New 3 repeats only; no replacement or adaptive extension.',
            'unit':'18 fixed inputs from 3 numeric triads; 3 new technical replicates; no FORM/READ rerun.'}


def source_for(design, slot):
    return next(x for x in design['source']['items'] if x['key']==slot['input_key'])


def case_for(design, slot):
    return next(c for c in design['cases'] if c['id']==slot['case'])


def request_for(design, slot, states=None):
    return {'id':slot['id'],'seed':slot['seed'],'messages':deepcopy(source_for(design,slot)['messages'])}


def payload_for(design, slot, states=None):
    return json.loads(source_for(design,slot)['messages'][1]['content'])
