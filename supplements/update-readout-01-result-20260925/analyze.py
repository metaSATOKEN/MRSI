"""Offline audit from original sources and raw answers. No execution of returned code."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

A = Path(__file__).resolve().parent
ROOT = A.parents[2]
S = A / 'received'
sys.path.insert(0, str(ROOT / 'scripts'))
from aggregate_cross_model_e1_01 import load_payload


def load(path): return json.loads(path.read_bytes())

def canonical(obj): return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()

def four(c): return {r: {m: c[r][m] for m in ('paper', 'digital')} for r in ('A', 'B')}

def choose(c):
    options = [m.upper() for m in ('paper', 'digital') if all(c[r][m] == 'ALL' for r in ('A', 'B'))]
    return options[0] if len(options) == 1 else 'UNKNOWN'

def write(name, value): (A / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def unique_pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result: raise ValueError('DUPLICATE_KEY')
        result[k] = v
    return result

def invalid_constant(value): raise ValueError('NON_FINITE')

def parse(raw): return json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=invalid_constant)


def valid_row(v):
    return (type(v) is dict and set(v) == {'observer','paper','digital','origin_id','revision'} and
        v['observer'] in ('A','B') and all(v[k] in ('ALL','NOT_ALL') for k in ('paper','digital')) and
        type(v['origin_id']) is str and re.fullmatch(r'[A-Z][A-Z0-9_]{0,31}',v['origin_id']) is not None and
        type(v['revision']) is int and 1 <= v['revision'] <= 1000000)


def valid_update(v, method):
    if type(v) is not dict or set(v) != {'private_note', 'shared_note' if method == 'REWRITE' else 'shared_choice'}: return False
    private = v['private_note']
    if type(private) is not dict or set(private) != {'customer','coverage'}: return False
    customer = private['customer']
    if not (type(customer) is dict and set(customer) == {'subject','animal','origin_id'} and customer['subject'] in ('A','B') and
        customer['animal'] in ('DOG','CAT') and type(customer['origin_id']) is str and
        re.fullmatch(r'[A-Z][A-Z0-9_]{0,31}',customer['origin_id']) and valid_row(private['coverage'])): return False
    if method == 'REWRITE':
        group = v['shared_note']
        return (type(group) is dict and set(group) == {'coverage'} and type(group['coverage']) is dict and
                set(group['coverage']) == {'A','B'} and all(valid_row(row) for row in group['coverage'].values()))
    choices = v['shared_choice']
    return type(choices) is dict and set(choices) == {'A','B'} and all(x in ('C1','C2','C3','C4') for x in choices.values())


def stats(values):
    values = list(values)
    return {'correct':sum(v is True for v in values), 'incorrect':sum(v is False for v in values),
            'unresolved':sum(v is None for v in values), 'n':len(values)}


design = load(S/'design.json'); report = load(A/'recomputed.json')['report']
cases = {c['id']:c for c in design['cases']}; slots = {s['id']:s for s in design['allocation']}
by_pipeline = {p['id']:p for p in report['by_pipeline']}
fixed_requests = {q['id']:q for q in load(S/'requests.json')}
for path, h in design['source_pins'].items(): assert sha256((ROOT/path).read_bytes()).hexdigest() == h,path
original = load_payload(ROOT/'study2/colab/cross_model_e1_01_main_onecell.py')
source_hashes = {}; expected = {}; case_states = {}
for case in design['cases']:
    evidence = {}
    for path,h in case['source_files_sha256'].items():
        raw=(ROOT/path).read_bytes();assert sha256(raw).hexdigest()==h,path
        source_hashes[path]=h;evidence[Path(path).name]=parse(raw)
    payload=evidence['input.json']['payload']; old_memory=evidence['saved-memory.json']
    assert evidence['result.json']['gate']=='PASS'
    assert payload==case['original_notes_payload']
    assert sha256(canonical(payload)).hexdigest()==case['original_payload_sha256']
    bodies={r['record_id']:r['body'] for r in payload['records']}
    assert bodies=={'PRIVATE':old_memory['private_note'],'GROUP':old_memory['shared_note']}
    material=original['bundle']['materials'][case['source_group']];latest=material['notices']
    expected[case['id']]={'private_note':{'customer':material['baseline_by_role'][case['role']]['private_note']['customer'],
        'coverage':latest[case['role']]}, 'shared_note':{'coverage':latest}}
    assert expected[case['id']]==case['expected_memory']
    assert expected[case['id']]['private_note']==old_memory['private_note']
    assert choose(latest)==case['latest_channel']==material['final_channel']
    notice=(latest[case['notice_target']] if case['set']=='REPAIR' else
        material['baseline_by_role'][case['notice_target']]['private_note']['coverage'])
    up=case['update_payload'];assert up==dict(payload,incoming_notice=notice,row_catalog=up['row_catalog'])
    assert sha256(canonical(up)).hexdigest()==case['update_payload_sha256']
    assert [v['row_id'] for v in up['row_catalog']]==['C1','C2','C3','C4']
    catalog={v['location']:v['row'] for v in up['row_catalog']}
    assert catalog=={'PRIVATE.coverage':old_memory['private_note']['coverage'],
        'GROUP.coverage.A':old_memory['shared_note']['coverage']['A'],
        'GROUP.coverage.B':old_memory['shared_note']['coverage']['B'],'NOTICE':notice}
    assert up['row_catalog'][case['notice_catalog_position']-1]['location']=='NOTICE'
    case_states[case['id']]={'old':old_memory,'latest':expected[case['id']], 'notice':notice}

responses=[]; outcomes=[]; problems=[]; fences=[]; accepted_memories={}
for s in design['allocation']:
    c=cases[s['case']];f=S/'responses'/s['id'];result=load(f/'result.json');sc=result['score']
    if result['status']=='DEPENDENCY_MISSING':
        assert s['stage']=='READ' and s['pipeline'] not in accepted_memories
        assert not any((f/name).exists() for name in ('input.json','response.json','started.json','saved-memory.json'))
        parent=S/'responses'/s['dependencies'][0];binding=load(f/'dependency.json')
        assert binding['result_sha256']==sha256((parent/'result.json').read_bytes()).hexdigest()
        assert binding['id']==s['dependencies'][0] and binding['gate']=='REJECT' and binding['saved_memory_sha256'] is None
        assert result['score']['dependency_missing'] is True
        continue
    inp=load(f/'input.json');response=load(f/'response.json');raw=(f/'answer.txt').read_text()
    assert response['answer_text']==raw and response['decoded_with_special_tokens']==raw+'<|im_end|>'
    assert response['finish_reason']=='EOS' and response['output_token_ids'][-1]==248046
    assert response['seed']==inp['seed']==s['seed']
    assert len(inp['prepared']['input_ids'])<=8192 and len(response['output_token_ids'])<=2048
    assert inp['id']==s['id']
    if s['stage']=='UPDATE':
        assert inp['parent'] is None
        wanted={'id':s['id'],'seed':s['seed'],'messages':[{'role':'system','content':design['prompts'][s['condition']]},
            {'role':'user','content':'\n資料JSON:\n'+canonical(c['update_payload']).decode()}]}
        assert wanted==fixed_requests[s['id']]
        assert all(inp[k]==wanted[k] for k in wanted)
    else:
        memory=accepted_memories[s['pipeline']]
        parent=S/'responses'/s['dependencies'][0]
        binding=inp['parent']
        assert binding=={'id':s['dependencies'][0],'status':'EOS','gate':'PASS',
            'result_sha256':sha256((parent/'result.json').read_bytes()).hexdigest(),
            'saved_memory_sha256':sha256((parent/'saved-memory.json').read_bytes()).hexdigest()}
        payload=dict(c['original_notes_payload'],records=[{'record_id':'PRIVATE','body':memory['private_note']},
            {'record_id':'GROUP','body':memory['shared_note']}])
        assert inp['messages']==[{'role':'system','content':design['read_prompt']},
            {'role':'user','content':'\n資料JSON:\n'+canonical(payload).decode()}]
    rendered=''.join('<|im_start|>'+m['role']+'\n'+m['content'].strip()+'<|im_end|>\n' for m in inp['messages'])+'<|im_start|>assistant\n<think>\n\n</think>\n\n'
    assert inp['prepared']['rendered_prompt']==rendered
    responses.append(dict(s,input_tokens=len(inp['prepared']['input_ids']),output_tokens=len(response['output_token_ids']),
        output_bytes=len(raw.encode()),generation_seconds=response['generation_seconds'],status=result['status']))
    if s['stage']=='UPDATE':
        try:
            value=parse(raw);parse_valid=True
        except (ValueError,UnicodeError):
            parse_valid=False
        assert sc['parse_valid']==parse_valid
        if not parse_valid:
            # Post-hoc transport diagnosis only. Inner text is never saved as an accepted memory or scientifically re-scored.
            match=re.fullmatch(r'```json\n([\s\S]*)\n```',raw)
            assert match is not None
            inner=parse(match[1]);assert valid_update(inner,s['condition'])
            assert len(raw.encode())<=16384
            assert sc['errors']==['JSON'] and sc['gate']=='REJECT' and result['status']=='FORMAT_REJECT'
            assert sc['joint_state_exact'] is None and not (f/'saved-memory.json').exists()
            fences.append({'id':s['id'],'case':s['case'],'set':s['set'],'condition':s['condition'],'replicate':s['replicate'],
                'classification':'ONE_OUTER_JSON_FENCE_INNER_SCHEMA_VALID', 'raw_sha256':sha256(raw.encode()).hexdigest(),
                'inner_sha256':sha256(match[1].encode()).hexdigest(),'formal_status_unchanged':True,'inner_content_scored':False})
            continue
        assert valid_update(value,s['condition']) and sc['gate']=='PASS' and sc['format_valid'] is True
        trace=load(f/'selection-trace.json')
        assert trace['answer_sha256']==sha256(raw.encode()).hexdigest() and trace['method']==s['condition']
        if s['condition']=='REWRITE':
            memory=value;assert trace['rows']==[]
        else:
            catalog={v['row_id']:v for v in c['update_payload']['row_catalog']}
            chosen={r:catalog[value['shared_choice'][r]] for r in ('A','B')}
            memory={'private_note':value['private_note'],'shared_note':{'coverage':{r:chosen[r]['row'] for r in ('A','B')}}}
            assert trace['rows']==[{'target':r,'row_id':chosen[r]['row_id'],'location':chosen[r]['location'],
                'source_row_sha256':sha256(canonical(chosen[r]['row'])).hexdigest()} for r in ('A','B')]
        assert load(f/'saved-memory.json')==memory==sc['memory']
        accepted_memories[s['pipeline']]=memory
        gold=expected[c['id']];g=memory['shared_note']['coverage'];latest=gold['shared_note']['coverage']
        checks={'private_customer_exact':memory['private_note']['customer']==gold['private_note']['customer'],
            'private_observation_exact':memory['private_note']['coverage']==gold['private_note']['coverage'],
            'shared_rows_exact':{r:g[r]==latest[r] for r in ('A','B')},
            'shared_values_exact':four(g)==four(latest),
            'shared_provenance_exact':all(g[r][k]==latest[r][k] for r in ('A','B') for k in ('observer','revision','origin_id')),
            'shared_latest_exact':g==latest,'joint_state_exact':memory==gold,
            'shared_row_matches_input':{r:any(v['row']==g[r] for v in c['update_payload']['row_catalog']) for r in ('A','B')}}
        for key,value in checks.items():assert value==sc[key],(s['id'],key)
        if not checks['joint_state_exact']:
            bad={r:{'got':g[r],'expected':latest[r],'matching_input_locations':[v['location'] for v in c['update_payload']['row_catalog'] if v['row']==g[r]]}
                 for r in ('A','B') if g[r]!=latest[r]}
            assert len(bad)==1
            for r,v in bad.items():
                assert v['got']['observer']==r and v['got']['revision']<v['expected']['revision']
                assert v['matching_input_locations']==(['GROUP.coverage.'+r] if c['set']=='REPAIR' else ['NOTICE'])
            problems.append(dict(s,role=c['role'],source_group=c['source_group'],notice_relation=c['notice_relation'],
                errors=bad,kind='OLD_ROW_RETAINED' if c['set']=='REPAIR' else 'LATE_NOTICE_ROLLBACK',
                preserved_private=checks['private_customer_exact'] and checks['private_observation_exact']))
    else:
        value=parse(raw)
        assert set(value)=={'coverage'} and set(value['coverage'])=={'A','B'}
        assert all(set(v)=={'paper','digital'} and all(x in ('ALL','NOT_ALL') for x in v.values()) for v in value['coverage'].values())
        values=value['coverage'];group=memory['shared_note']['coverage'];latest=expected[c['id']]['shared_note']['coverage']
        output=choose(values);derived=load(f/'derived-decision.json')
        assert derived['answer_sha256']==sha256(raw.encode()).hexdigest() and derived['extracted_values']==values
        assert derived['channel']==output and derived['four_valid'] is True and derived['additional_model_requests']==0
        checks={'format_valid':True,'four_exact':values==four(group),'four_latest_exact':values==four(latest),
                'channel_note':output==choose(group),'channel_latest':output==choose(latest),'channel_output':output}
        for key,value in checks.items():assert value==sc[key],(s['id'],key)
        p=by_pipeline[s['pipeline']]
        assert p['end_to_end_exact']==(memory==expected[c['id']] and checks['four_exact'] and checks['channel_latest'])

for problem in problems:
    p=by_pipeline[problem['pipeline']];problem.update(read=p['read'],end_to_end_exact=p['end_to_end_exact'])

summary={};paired={}
for method in ('REWRITE','SELECT'):
    summary[method]={}
    for subset in ('REPAIR','GUARD'):
        part=[p for p in report['by_pipeline'] if p['condition']==method and p['set']==subset]
        summary[method][subset]={'joint':stats(p['update']['joint_state_exact'] for p in part),
            'end_to_end':stats(p['end_to_end_exact'] for p in part),
            'accepted':sum(p['update']['gate']=='PASS' for p in part),
            'fenced':sum(f['condition']==method and f['set']==subset for f in fences),
            'by_repeat':{str(rep):stats(p['end_to_end_exact'] for p in part if p['replicate']==rep) for rep in (1,2)}}
        assert summary[method][subset]['joint']==report['methods'][method]['joint_state_exact']['by_set'][subset]
        assert summary[method][subset]['end_to_end']==report['methods'][method]['end_to_end_exact']['by_set'][subset]
for subset in ('REPAIR','GUARD'):
    paired[subset]=dict(Counter(str(by_pipeline[f"{c['id']}-R{rep}-REWRITE"]['end_to_end_exact'])+'->'+
        str(by_pipeline[f"{c['id']}-R{rep}-SELECT"]['end_to_end_exact']) for c in design['cases'] if c['set']==subset for rep in (1,2)))
    rw=summary['REWRITE'][subset]['end_to_end'];se=summary['SELECT'][subset]['end_to_end'];n=rw['n']
    bounds=[(se['correct']-rw['correct']-rw['unresolved'])/n,(se['correct']+se['unresolved']-rw['correct'])/n]
    assert bounds==report['contrasts']['end_to_end_exact']['repair_bounds' if subset=='REPAIR' else 'guard_bounds']

env=load(S/'environment.json');binding=load(S/'tokenizer-binding.json');params=load(S/'loaded-parameters.json');gen=load(S/'generation-config.json')
assert binding['revision']==design['model']['revision']
assert params['devices']==['cuda:0'] and set(params['parameter_dtype_counts'])=={'torch.bfloat16'}
for key in ('temperature','top_p','top_k','repetition_penalty','max_new_tokens','do_sample','use_cache'):
    assert gen[key]==design['model']['generation'][key]
for package,version in design['model']['pins'].items():assert env['packages'][package]==version
assert len(responses)==107 and len(accepted_memories)==35 and len(fences)==37 and len(problems)==11
assert all(p['preserved_private'] for p in problems)
elapsed=load(S/'run-end.json')['elapsed_seconds'];generation=sum(r['generation_seconds'] for r in responses)
result={'kind':'INDEPENDENT_OFFLINE_SOURCE_TRANSPORT_AND_RAW_ANSWER_AUDIT','source_files_checked':len(source_hashes),
    'planned_slots':144,'generated_updates':72,'generated_reads':35,'dependent_missing':37,'all_generated_eos':True,
    'exact_saved_memory_to_read_inputs':35,'exact_readout_responses':35,'exact_readout_fields':140,
    'accepted_private_customer_exact':35,'accepted_private_observation_exact':35,'accepted_shared_rows_match_input':70,
    'accepted_latest_shared_rows':59,'accepted_joint_exact':24,'accepted_latest_channel_correct':25,
    'failure_types':dict(Counter(p['kind'] for p in problems)),
    'fence_types':dict(Counter(f['condition'] for f in fences)),'methods':summary,'paired':paired,
    'runtime':{'elapsed_seconds':elapsed,'generation_seconds':generation,'other_seconds':elapsed-generation},
    'environment':env,'responses':responses,'semantic_problems':problems,'fence_diagnostics':fences,
    'all_primary_metrics_unchanged':True,'posthoc_diagnostics':'Fence envelopes and exact old-row matching only; no counterfactual score or missing READ imputation.',
    'model_calls_during_audit':0,'p_value':None,'confidence_interval':None}
assert sum(p['read'].get('channel_latest') is True for p in report['by_pipeline'])==result['accepted_latest_channel_correct']
write('diagnostics.json',result);write('source-hashes.json',source_hashes)
# Illustrative examples selected after scoring, never used to select cases or thresholds.
example_ids=[fences[0]['id'],next(p['id'] for p in problems if p['kind']=='OLD_ROW_RETAINED' and p['condition']=='SELECT'),
             next(p['id'] for p in problems if p['kind']=='LATE_NOTICE_ROLLBACK')]
examples=[]
for sid in example_ids:
    slot=slots[sid];c=cases[slot['case']];folder=S/'responses'/sid
    ids=[sid]+([slot['pipeline']+'-READ'] if slot['pipeline'] in accepted_memories else [])
    files={}
    for rid in ids:
        f=S/'responses'/rid
        for name in ('input.json','answer.txt','result.json','saved-memory.json','selection-trace.json','derived-decision.json'):
            if (f/name).exists():files[str((f/name).relative_to(A))]=sha256((f/name).read_bytes()).hexdigest()
    examples.append({'id':sid,'case':c['id'],'source_group':c['source_group'],'role':c['role'],'set':c['set'],
        'expected_memory':expected[c['id']],'latest_channel':c['latest_channel'],
        'update_raw':(folder/'answer.txt').read_text(),'pipeline':by_pipeline[slot['pipeline']], 'files_sha256':files})
write('examples.json',{'selection':'Post-hoc illustration only','examples':examples})
print(json.dumps({k:v for k,v in result.items() if k not in ('responses','semantic_problems','fence_diagnostics','environment')},ensure_ascii=False,indent=2))
