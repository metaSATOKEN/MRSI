"""TCV01: paired direct voting versus an explicit, separately recorded comparison."""
from copy import deepcopy
from hashlib import sha256
import json
import random
import three_role_boundary_01_design as base

enc, digest = base.enc, base.digest
SOURCE_SHA256 = '81b8d080cf0b75d65e4ce3757bbf105a575a7fd34763efc60678d3b354716c46'
PROTOCOL = 'THREE-ROLE-COMPARISON-VOTE-01-v0.1'
ARMS = ('DIRECT', 'COMPARE')
REPEATS = (1, 2, 3)
STAGES = ('VOTE',)
COMPARISON_SCHEMA = {'type':'object', 'additionalProperties':False,
    'required':['candidate_id','other_candidate_id','relation'], 'properties':{
        'candidate_id':{'type':'string','enum':['C1','C2']},
        'other_candidate_id':{'type':'string','enum':['C1','C2']},
        'relation':{'type':'string','enum':['HIGHER','LOWER']}}}
COMPARE_INSTRUCTION = (
    '今回のJSONはown、comparison、voteの順で記述する。'
    'comparisonには提示proposalのcandidate_id、もう一つの候補のother_candidate_id、'
    '三人分の予測成功人数の合計を比較したrelationを記録する。'
    '提示候補の合計が他候補より高ければHIGHER、低ければLOWERとする。'
    'この比較には本人だけの成功人数や本人推奨を使わない。'
    '本人推奨はownに保持したまま、共同候補の比較をcomparisonへ分けて記録する。'
    'voteはこの共同候補の比較に従い、HIGHERならACCEPT、LOWERならHOLDとする。'
    '説明文や追加キーは出さない。\n')


def schema_for(arm):
    schema = deepcopy(base.SCHEMAS['VOTE'])
    if arm == 'COMPARE':
        schema['required'] = ['own','comparison','vote']
        schema['properties']['comparison'] = deepcopy(COMPARISON_SCHEMA)
    elif arm != 'DIRECT':
        raise ValueError('UNKNOWN_ARM')
    return schema


def old_repeat_seeds(source):
    return {int(sha256(('TVR01-20261013|TVR01-'+item['key']+'-R'+str(rep)).encode()).hexdigest()[:8],16) % 2**31
            for item in source['items'] for rep in REPEATS}


def build_design(model, source):
    if digest(source) != SOURCE_SHA256: raise ValueError('FIXED_SOURCE_CHANGED')
    assert model == source['model'] and len(source['items']) == 18
    slots = []
    for rep in REPEATS:
        rng = random.Random(2026101330 + rep)
        order = deepcopy(source['items']); rng.shuffle(order)
        direct_first = [True]*9 + [False]*9; rng.shuffle(direct_first)
        for item, first in zip(order,direct_first):
            pair = f"TCV01-{item['key']}-R{rep}"
            seed = int(sha256(('TCV01-20261013|'+pair).encode()).hexdigest()[:8],16) % 2**31
            for pos,arm in enumerate(ARMS if first else ARMS[::-1]):
                slots.append({'id':pair+'-'+arm,'pair_id':pair,'input_key':item['key'],
                    'arm':arm,'arm_position':pos+1,'stage':'VOTE','case':item['case'],
                    'role':item['role'],'branch':item['branch'],'repeat':rep,'snapshot':None,
                    'parents':[],'seed':seed})
    seeds = {s['seed'] for s in slots}
    assert len(seeds) == 54 and not seeds.intersection(set(source['old_seeds']) | old_repeat_seeds(source))
    return {'protocol':PROTOCOL,'date':'2026-10-13','source':deepcopy(source),
        'cases':deepcopy(source['cases']),'schemas':{a:schema_for(a) for a in ARMS},
        'compare_instruction':COMPARE_INSTRUCTION,'allocation':slots,'repeats':list(REPEATS),
        'arms':list(ARMS),'model':model,
        'budget':{'max_generations':108,'total_seconds':1800,'reserve_seconds':90,'max_raw_bytes':16384,'retries':0},
        'unit':'18 fixed inputs from 3 materials; 2 arms; 3 new technical replicates; 54 matched pairs.',
        'retention':'private_no_deletion_deadline',
        'stop_rule':'One fixed pass; no adaptive extension, replacement, or old-outcome pooling.'}


def source_for(design, slot):
    return next(x for x in design['source']['items'] if x['key']==slot['input_key'])


def case_for(design, slot):
    return next(x for x in design['cases'] if x['id']==slot['case'])


def request_for(design, slot, states=None):
    messages = deepcopy(source_for(design,slot)['messages'])
    if slot['arm'] == 'COMPARE':
        messages[0]['content'] += design['compare_instruction']
        payload = json.loads(messages[1]['content'])
        payload['schema'] = deepcopy(design['schemas']['COMPARE'])
        messages[1]['content'] = enc(payload).decode()
    return {'id':slot['id'],'seed':slot['seed'],'messages':messages}


def payload_for(design, slot, states=None):
    return json.loads(request_for(design,slot)['messages'][1]['content'])


def verification_template(design, slot, request):
    template = dict(request)
    if slot['arm'] == 'DIRECT': template['expected_prepared'] = source_for(design,slot)['prepared']
    return template
