"""Authorized post-hoc UR01 envelope-only analysis. Never changes original experiment files."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

A=Path(__file__).resolve().parent
ROOT=A.parents[2]
PREVIOUS=ROOT/'throughline/audits/update-readout-01-result-20260925'
S=PREVIOUS/'received'
sys.path.insert(0,str(ROOT/'scripts'))
import update_readout_01_envelope as envelope
import update_readout_01_scoring as scoring
from aggregate_cross_model_e1_01 import load_payload


def load(p):return json.loads(p.read_bytes())

def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def canon(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()

def four(c):return {r:{m:c[r][m] for m in ('paper','digital')} for r in ('A','B')}

def choose(c):
    available=[m.upper() for m in ('paper','digital') if all(c[r][m]=='ALL' for r in ('A','B'))]
    return available[0] if len(available)==1 else 'UNKNOWN'

def unique_pairs(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ValueError('DUPLICATE_KEY')
        result[k]=v
    return result

def no_constant(v):raise ValueError('NONSTANDARD_NUMBER')

def rawparse(raw):return json.loads(raw,object_pairs_hook=unique_pairs,parse_constant=no_constant)

def count(values):
    values=list(values)
    return {'correct':sum(v is True for v in values),'incorrect':sum(v is False for v in values),
            'unresolved':sum(v is None for v in values),'n':len(values)}


for p,h in load(A/'anchors-before.json').items():assert sha256((ROOT/p).read_bytes()).hexdigest()==h,p
old_manifest=load(A/'previous-artifact-manifest.json')['files_sha256']
for p,h in old_manifest.items():assert sha256((PREVIOUS/p).read_bytes()).hexdigest()==h,p
log=(A/'tests-attempt-1.log').read_text();assert 'Ran 15 tests' in log and log.rstrip().endswith('OK')
design=load(S/'design.json');cases={c['id']:c for c in design['cases']}
formal=load(PREVIOUS/'recomputed.json')['report'];original={p['id']:p for p in formal['by_pipeline']}
source=load_payload(ROOT/'study2/colab/cross_model_e1_01_main_onecell.py')
source_hashes={};truth={}
for c in design['cases']:
    material=source['bundle']['materials'][c['source_group']]
    for p,h in c['source_files_sha256'].items():assert sha256((ROOT/p).read_bytes()).hexdigest()==h;source_hashes[p]=h
    truth[c['id']]={'private_note':{'customer':material['baseline_by_role'][c['role']]['private_note']['customer'],
        'coverage':material['notices'][c['role']]},'shared_note':{'coverage':material['notices']}}
    assert truth[c['id']]==c['expected_memory']
    assert choose(material['notices'])==c['latest_channel']

outcomes={};rows=[];problems=[]
for p in design['pipelines']:
    c=cases[p['case']];prior=original[p['id']];folder=S/'responses'/(p['id']+'-UPDATE')
    raw=(folder/'answer.txt').read_bytes();response=load(folder/'response.json')
    assert raw==response['answer_text'].encode() and response['finish_reason']=='EOS'
    transformed=envelope.normalize(raw,response['finish_reason']);body=transformed.pop('normalized_bytes')
    assert transformed['status'] in ('UNCHANGED','UNWRAPPED') and body is not None
    cohort='ORIGINAL_ACCEPTED' if prior['update']['gate']=='PASS' else 'RECOVERED_FENCE'
    assert (transformed['status']=='UNCHANGED')==(cohort=='ORIGINAL_ACCEPTED')
    assert body==(raw if cohort=='ORIGINAL_ACCEPTED' else raw[8:-4])
    value=rawparse(body)
    reference=scoring.score_update(body,c,p['condition'],design['schemas'][p['condition']],response['finish_reason'])
    assert reference['gate']=='PASS' and reference['format_valid'] is True
    if cohort=='ORIGINAL_ACCEPTED':assert reference==prior['update']
    # Independent reconstruction: visible choices only, no scoring-helper materialization.
    if p['condition']=='REWRITE':memory=value
    else:
        catalog={v['row_id']:v['row'] for v in c['update_payload']['row_catalog']}
        memory={'private_note':value['private_note'],'shared_note':{'coverage':{r:catalog[value['shared_choice'][r]] for r in ('A','B')}}}
    assert memory==reference['memory']
    gold=truth[c['id']];g=memory['shared_note']['coverage'];latest=gold['shared_note']['coverage']
    checks={'private_customer_exact':memory['private_note']['customer']==gold['private_note']['customer'],
        'private_observation_exact':memory['private_note']['coverage']==gold['private_note']['coverage'],
        'shared_rows_exact':{r:g[r]==latest[r] for r in ('A','B')},
        'shared_values_exact':four(g)==four(latest),
        'shared_provenance_exact':all(g[r][k]==latest[r][k] for r in ('A','B') for k in ('observer','revision','origin_id')),
        'shared_latest_exact':g==latest,'joint_state_exact':memory==gold,
        'shared_row_matches_input':{r:any(v['row']==g[r] for v in c['update_payload']['row_catalog']) for r in ('A','B')}}
    for k,v in checks.items():assert reference[k]==v,(p['id'],k)
    observed_read=prior['read']
    assert observed_read['dependency_missing']==(cohort=='RECOVERED_FENCE')
    endpoint=scoring.end_to_end(reference,observed_read)
    assert endpoint==prior['end_to_end_exact']
    if cohort=='RECOVERED_FENCE':
        read_folder=S/'responses'/(p['id']+'-READ')
        assert not (read_folder/'response.json').exists() and not (read_folder/'input.json').exists()
        assert not (folder/'saved-memory.json').exists()
    else:assert memory==load(folder/'saved-memory.json')
    static_channel=choose(g);assert static_channel==scoring.compute_channel(g)
    entry=dict(p,cohort=cohort,role=c['role'],notice_relation=c['notice_relation'],notice_target=c['notice_target'],
        notice_catalog_position=c['notice_catalog_position'],source_condition=c['source_condition'],source_group=c['source_group'],
        normalization=transformed,formal_update=prior['update'],reference_update=reference,
        observed_read=observed_read,reference_end_to_end_observed=endpoint,
        static_note_calculation={'kind':'DETERMINISTIC_FROM_RECONSTRUCTED_NOTE_NOT_LLM_READOUT',
            'channel':static_channel,'latest_channel':c['latest_channel'],'matches_latest':static_channel==c['latest_channel'],
            'read_was_run':cohort=='ORIGINAL_ACCEPTED'})
    rows.append(entry);outcomes[p['id']]={'update':reference,'read':observed_read}
    derived=A/'reference-only'/p['id'];derived.mkdir(parents=True)
    (derived/'raw-update.txt').write_bytes(raw);(derived/'normalized-update.txt').write_bytes(body)
    write(derived/'normalization.json',transformed)
    write(derived/'reconstructed-memory.json',{'kind':'POSTHOC_RECONSTRUCTION_NOT_EXPERIMENT_SAVED_MEMORY',
        'pipeline':p['id'],'normalization_status':transformed['status'],'memory':memory,'choice_trace':reference['choice_trace']})
    write(derived/'reference-score.json',entry)
    if not reference['joint_state_exact']:
        issues=[]
        for key in ('private_customer_exact','private_observation_exact'):
            if not reference[key]:issues.append({'kind':key.upper()+'_MISMATCH'})
        for r in ('A','B'):
            if g[r]==latest[r]:continue
            matches=[v['location'] for v in c['update_payload']['row_catalog'] if v['row']==g[r]]
            if g[r]['observer']!=r:kind='WRONG_OBSERVER_ROW'
            elif matches and g[r]['revision']<latest[r]['revision']:
                kind='LATE_NOTICE_ROLLBACK' if c['set']=='GUARD' and matches==['NOTICE'] else 'OLD_ROW_RETAINED'
            else:kind='MODIFIED_OR_UNKNOWN_ROW'
            issues.append({'target':r,'kind':kind,'actual':g[r],'expected':latest[r],'matching_input_locations':matches})
        problems.append({'id':p['id'],'set':p['set'],'condition':p['condition'],'replicate':p['replicate'],
            'case':p['case'],'source_group':c['source_group'],'cohort':cohort,'issues':issues,
            'static_note_channel':static_channel,'latest_channel':c['latest_channel'],
            'observed_read_output':observed_read.get('channel_output'),'observed_read_ran':cohort=='ORIGINAL_ACCEPTED'})

summary=scoring.summarize(design,outcomes)
for m in scoring.METHODS:
    # The endpoint outcomes are unchanged; the separate private-customer component becomes evaluable.
    for key in ('by_set','by_repeat','criterion_status'):
        assert summary['methods'][m]['end_to_end_exact'][key]==formal['methods'][m]['end_to_end_exact'][key]
assert summary['contrasts']['end_to_end_exact']==formal['contrasts']['end_to_end_exact']
cohorts={}
for cohort in ('ORIGINAL_ACCEPTED','RECOVERED_FENCE','MERGED_REFERENCE'):
    cohorts[cohort]={}
    for m in scoring.METHODS:
        cohorts[cohort][m]={}
        for subset in ('REPAIR','GUARD'):
            part=[r for r in rows if r['condition']==m and r['set']==subset and (cohort=='MERGED_REFERENCE' or r['cohort']==cohort)]
            components={k:count(r['reference_update'][k] for r in part) for k in ('private_customer_exact','private_observation_exact',
                'shared_values_exact','shared_provenance_exact','shared_latest_exact','joint_state_exact')}
            item={'n':len(part),'components':components,'observed_endpoint':count(r['reference_end_to_end_observed'] for r in part),
                'static_note_channel_matches_latest':count(r['static_note_calculation']['matches_latest'] for r in part),
                'by_repeat':{str(rep):count(r['reference_update']['joint_state_exact'] for r in part if r['replicate']==rep) for rep in (1,2)}}
            cohorts[cohort][m][subset]=item
            if cohort=='MERGED_REFERENCE':assert components['joint_state_exact']==summary['methods'][m]['joint_state_exact']['by_set'][subset]
paired={}
for subset in ('REPAIR','GUARD'):
    part=[r for r in rows if r['set']==subset];by={(r['case'],r['replicate'],r['condition']):r for r in part}
    pairs=[{'case':c['id'],'replicate':rep,'rewrite':by[c['id'],rep,'REWRITE']['reference_update']['joint_state_exact'],
        'select':by[c['id'],rep,'SELECT']['reference_update']['joint_state_exact']} for c in design['cases'] if c['set']==subset for rep in (1,2)]
    net=sum(int(p['select'])-int(p['rewrite']) for p in pairs)
    paired[subset]={'counts':dict(Counter(str(p['rewrite'])+'->'+str(p['select']) for p in pairs)),
        'net_select_minus_rewrite':net,'n':len(pairs),
        'by_repeat_net':{str(rep):sum(int(p['select'])-int(p['rewrite']) for p in pairs if p['replicate']==rep) for rep in (1,2)},'pairs':pairs}
    key='repair_bounds' if subset=='REPAIR' else 'guard_bounds'
    assert all(abs(bound-net/len(pairs)) < 1e-12 for bound in summary['contrasts']['joint_state_exact'][key])
result={'kind':'POSTHOC_ENVELOPE_NORMALIZED_REFERENCE_NOT_FORMAL_RESULT','protocol':envelope.PROTOCOL,
    'raw_updates':72,'normalization_counts':dict(Counter(r['normalization']['status'] for r in rows)),
    'bytes_removed':sum(r['normalization']['raw_bytes']-r['normalization']['normalized_bytes_length'] for r in rows),
    'strict_schema_after_normalization':72,'original_accepted_unchanged':35,'recovered_fence_rescored':37,
    'observed_read_count':35,'missing_read_count':37,'source_files_checked':len(source_hashes),
    'merged_summary':summary,'cohorts':cohorts,'paired_updates':paired,
    'failure_types':dict(Counter(i['kind'] for p in problems for i in p['issues'])),
    'problem_pipelines':problems,'pipelines':rows,
    'formal_result_unchanged':True,'old_endpoint_outcomes_unchanged':True,'production_cell_modified':False,
    'model_generations':0,'p_value':None,'confidence_interval':None}
write(A/'reference-analysis.json',result);write(A/'source-hashes.json',source_hashes)
# Recheck all previous evidence after writing the separate derived artifacts.
for p,h in old_manifest.items():assert sha256((PREVIOUS/p).read_bytes()).hexdigest()==h,p
print(json.dumps({k:v for k,v in result.items() if k not in ('pipelines','problem_pipelines','paired_updates')},ensure_ascii=False,indent=2))
