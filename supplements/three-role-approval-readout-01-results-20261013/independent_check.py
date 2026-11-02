"""TAR01 stdlib-only result audit, separate from the fixed experiment scorer.

Parsers/shape checks are retained from the TCV02 result audit. References below
are reconstructed from raw parent records, experiences, and actual receipts.
No returned archive code is imported or executed.
"""
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import zipfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
RESULT=ROOT/'study2/results/three-role-approval-readout-01-20261013'
ARCHIVE=RESULT/'npp-tar01-result-20261013-071229-08c825b9.zip'
CHECKS=Counter()

def check(ok,category,detail=''):
    if not ok:raise AssertionError((category,detail))
    CHECKS[category]+=1

def pairs(items):
    d={}
    for k,v in items:
        check(k not in d,'unique_json_key',k);d[k]=v
    return d

def parse(raw):
    return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))

def shape(obj,schema):
    t=schema['type']
    if t=='object':
        check(type(obj) is dict and set(obj)==set(schema['required']),'schema_object')
        for k,v in obj.items():shape(v,schema['properties'][k])
    elif t=='array':
        check(type(obj) is list and schema['minItems']<=len(obj)<=schema['maxItems'],'schema_array')
        for v in obj:shape(v,schema['items'])
    else:
        check(type(obj) is str,'schema_string')
        check(obj in schema['enum'] if 'enum' in schema else schema['minLength']<=len(obj)<=schema['maxLength'],'schema_value')

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest(v):return sha256(canonical(v)).hexdigest()
def counts(values):
    vs=list(values);return {'planned':len(vs),'correct':sum(v is True for v in vs),'incorrect':sum(v is False for v in vs),'unresolved':sum(v is None for v in vs)}
def save(name,v):
    p=RESULT/name;raw=json.dumps(v,ensure_ascii=False,indent=2)+'\n'
    if p.exists():check(p.read_text()==raw,'unchanged_analysis',name)
    else:p.write_text(raw)

def main():
    with zipfile.ZipFile(ARCHIVE) as z:
        check(len(z.namelist())==len(set(z.namelist())),'unique_archive_members')
        files={n:z.read(n) for n in z.namelist()}
    manifest=parse(files.pop('FEEDBACK_MANIFEST.json'))
    check(set(files)==set(manifest['files_sha256']),'manifest_members')
    for n,b in files.items():check(sha256(b).hexdigest()==manifest['files_sha256'][n],'file_hash',n)
    def j(n):return parse(files[n])
    frozen=json.loads((HERE.parent/'three-role-approval-readout-01-preparation-20261013/payload.json').read_bytes())
    check(j('payload.json')==frozen,'frozen_payload')
    design=j('design.json');check(design==json.loads(frozen['design_text']),'frozen_design')
    source=design['source'];report=json.loads((RESULT/'reaggregated.json').read_bytes())['report']
    for n in files:
        if n.startswith('report-') and n.endswith('.json'):check(j(n)==report,'archived_report')
    prerequests={r['id']:r for r in json.loads(frozen['frozen']['requests.json'])}
    pre=j('tokenizer-preflight-read.json');check(pre['status']=='PASS' and pre['blocked_ids']==[],'tokenizer_preflight')
    tokenchecks={r['id']:r for r in pre['checked']};check(set(tokenchecks)==set(prerequests) and len(pre['checked'])==54,'preflight_id_set')
    rows=[];triplets=defaultdict(list);repeat_inputs=defaultdict(list);prepared_by_id={};extracts=[]
    metrics=('own_holder','own_recommendation','own_sources','approval_state','agreement','execution')
    for s in design['allocation']:
        sid=s['id'];path='responses/'+sid+'/';role=s['role'];arm=s['arm']
        inp,response,saved=j(path+'input.json'),j(path+'response.json'),j(path+'result.json')
        src=next(x for x in source['parent_map'] if x['case']==s['case']);case=next(c for c in design['cases'] if c['id']==s['case'])
        def parent(pid,name):return parse(source['records'][pid]['files'][name]['text'])
        payload=deepcopy(parse(parent(src['votes'][role],'input.json')['messages'][1]['content']))
        payload['schema']=design['schemas']['READ'];payload['own_saved_note']=parent(src['forms'][role],'carry-answer.json')['own']
        receipts=[]
        for r in ('A','B','C'):
            actual=parent(src['votes'][r],'carry-answer.json')['vote'];check(actual['decision']=='ACCEPT','real_vote_parent',sid)
            if arm=='MISSING' and r==src['focal_role']:continue
            receipts.append({'sender':r,**actual})
            if arm=='HOLD' and r==src['focal_role']:receipts[-1]['decision']='HOLD'
        payload['receipts']=receipts
        expected_messages=[{'role':'system','content':design['prompts']['READ']},{'role':'user','content':canonical(payload).decode()}]
        check(inp['messages']==expected_messages==prerequests[sid]['messages'],'actual_input_reconstruction',sid)
        check(inp['id']==sid and inp['seed']==s['seed']==response['seed']==prerequests[sid]['seed'],'id_seed',sid)
        form=src['forms'][role];chosen=[form,*src['votes'].values()]
        binding={'archive_sha256':source['archives']['TCV02']['sha256'],'own_form_id':form,
            'parent_files':{p:{n:f['sha256'] for n,f in source['records'][p]['files'].items()} for p in chosen},
            'focal_role':src['focal_role'],'condition':arm,
            'transformation':{'MISSING':'omit_focal_receipt','HOLD':'replace_focal_decision_ACCEPT_with_HOLD','ACCEPT':'unchanged_receipt_projection'}[arm],
            'constructed_HOLD':arm=='HOLD','receipt_order':['A','B','C'],
            'receipts_sha256':digest(receipts),'payload_sha256':digest(payload)}
        check(inp['binding']==binding,'source_and_transformation_binding',sid)
        trace=j(path+'carry-trace.json')
        check(trace=={'parents':binding,'payload_sha256':digest(payload),'host_agreement_supplied':False,'semantic_repair':False,'new_answer_reused':False},'carry_trace',sid)
        prepared=inp['prepared'];prepared_by_id[sid]=prepared
        check(digest(prepared)==tokenchecks[sid]['prepared_sha256'],'actual_preflight_token_hash',sid)
        check(len(prepared['input_ids'])==tokenchecks[sid]['input_tokens'],'input_token_count',sid)
        check(sha256(prepared['rendered_prompt'].encode()).hexdigest()==tokenchecks[sid]['rendered_sha256'],'render_hash',sid)
        rendered=''.join('<|im_start|>'+m['role']+'\n'+m['content'].strip()+'<|im_end|>\n' for m in expected_messages)+'<|im_start|>assistant\n<think>\n\n</think>\n\n'
        check(prepared['rendered_prompt']==rendered,'full_prompt',sid)
        raw=files[path+'answer.txt'];answer=parse(raw);shape(answer,design['schemas']['READ'])
        check(saved['status']=='EOS' and response['finish_reason']=='EOS' and response['output_token_ids'][-1]==248046,'eos',sid)
        check(response['answer_text'].encode()==raw==files[path+'normalized-answer.txt'],'bare_json_no_repair',sid)
        check(answer==j(path+'saved-answer.json')==j(path+'carry-answer.json')==saved['score']['answer'],'saved_answer',sid)
        check(not response.get('synthetic_fixture'),'not_fixture',sid)
        exps=[e for e in case['experiences'] if e['owner']==role]
        rates={m:Fraction(sum(e['observed'][m]['success'] for e in exps),sum(e['observed'][m]['trials'] for e in exps)) for m in ('PAPER','DIGITAL')}
        own={'holder':role,'recommendation':max(rates,key=rates.get),'evidence_ids':[e['id'] for e in exps]}
        states={r:'MISSING' for r in ('A','B','C')}
        for r in receipts:states[r['sender']]=r['decision'] if r['proposal_id']==payload['proposal']['proposal_id'] else 'WRONG_PROPOSAL'
        agreed=all(v=='ACCEPT' for v in states.values())
        selected=next(c for c in case['candidates'] if c['candidate_id']==payload['proposal']['candidate_id'])
        action=selected['assignment'][role] if agreed else 'HOLD'
        expected_answer={'own':own,'approval_state':states,'agreement':'AGREED' if agreed else 'PENDING','joint_action':action}
        own_actual=answer['own']
        local={'own_holder':own_actual['holder']==own['holder'],'own_recommendation':own_actual['recommendation']==own['recommendation'],
            'own_sources':len(own_actual['evidence_ids'])==len(own['evidence_ids']) and set(own_actual['evidence_ids'])==set(own['evidence_ids']),
            'approval_state':answer['approval_state']==states,'agreement':answer['agreement']==expected_answer['agreement'],'execution':answer['joint_action']==action}
        check(saved['score']['metrics']==local and saved['score']['strict']==all(local.values()),'six_axis_scoring',sid)
        byslot=next(x for x in report['by_slot'] if x['id']==sid)
        check(byslot['score']==saved['score'],'saved_aggregate_score',sid)
        row={'id':sid,'case':s['case'],'role':role,'arm':arm,'repeat':s['repeat'],'seed':s['seed'],
            'focal_role':src['focal_role'],'triplet_id':s['triplet_id'],'receipts':receipts,'expected':expected_answer,'answer':answer,
            'metrics':local,'strict':all(local.values()),'raw_sha256':sha256(raw).hexdigest(),
            'prepared_sha256':digest(prepared),'input_tokens':len(prepared['input_ids']),
            'output_tokens':len(response['output_token_ids']),'generation_seconds':response['generation_seconds']}
        rows.append(row);triplets[s['triplet_id']].append(row);repeat_inputs[s['input_key']].append(row)
        if s['case']=='N01' and role=='A':
            extracts.append({'slot':s,'input':payload,'raw_answer':raw.decode(),'expected':expected_answer,'metrics':local,
                'archive_members':{'input':path+'input.json','answer':path+'answer.txt'},'prepared_sha256':digest(prepared)})
    computed={m:counts(r['metrics'][m] for r in rows) for m in metrics}
    check(report['metrics']==computed and report['totals']==counts(r['strict'] for r in rows),'aggregate_axes')
    check(report['gate']==('FAIL' if any(not r['strict'] for r in rows) else 'PASS_IN_FIXED_READOUT'),'formal_gate')
    check(report['status_counts']=={'EOS':54} and report['attempted_generations']==54,'response_counts')
    check(len([n for n in files if n.endswith('/started.json')])==54,'no_extra_generation')
    pairs=[]
    for key,rr in repeat_inputs.items():
        rr=sorted(rr,key=lambda x:x['repeat']);a,b=rr
        check(prepared_by_id[a['id']]==prepared_by_id[b['id']],'identical_input_across_replicates',key)
        pairs.append({'input_key':key,'ids':[a['id'],b['id']],'strict':[a['strict'],b['strict']],
            'answer_changed':a['answer']!=b['answer'],'approval_state_changed':a['answer']['approval_state']!=b['answer']['approval_state']})
    check(report['triplet_totals']==counts(all(r['strict'] for r in rr) for rr in triplets.values()),'triplet_totals')
    for t in report['triplets']:
        rr=triplets[t['id']];own=[r['answer']['own'] for r in rr];armmap={r['arm']:r for r in rr};focal=rr[0]['focal_role']
        check(t['strict']==all(r['strict'] for r in rr),'triplet_strict')
        check(t['own_correct_all_states']==all(r['metrics'][m] for r in rr for m in metrics[:3]),'triplet_own_correct')
        check(t['own_fields_identical']==(own[0]==own[1]==own[2]),'triplet_own_equal')
        check(t['missing_hold_discrimination']==(armmap['MISSING']['answer']['approval_state'][focal]=='MISSING' and armmap['HOLD']['answer']['approval_state'][focal]=='HOLD'),'triplet_discrimination')
        # The legacy name includes approval_state as well as agreement/execution.
        check(t['agreement_execution_all_states']==all(r['metrics'][m] for r in rr for m in metrics[3:]),'legacy_three_axis_metric')
    for t in report['case_replicates']:
        check(t['strict']==all(r['strict'] for r in rows if r['case']==t['case'] and r['repeat']==t['repeat']),'case_replicate')
    check(report['case_replicate_totals']==counts(t['strict'] for t in report['case_replicates']),'case_totals')
    costs={}
    for arm in ('MISSING','HOLD','ACCEPT'):
        rr=[r for r in rows if r['arm']==arm];g=report['by_arm'][arm]
        check(g['strict']==counts(r['strict'] for r in rr),'arm_strict')
        for m in metrics:check(g['metrics'][m]==counts(r['metrics'][m] for r in rr),'arm_axis')
        errors=Counter(dict.fromkeys(g['error_counts'],0))
        for r in rr:
            a=r['answer'];focal=r['focal_role'];errors['focal_false_accept']+=int(arm!='ACCEPT' and a['approval_state'][focal]=='ACCEPT')
            errors['focal_state_other_error']+=int(a['approval_state'][focal]!=arm and not(arm!='ACCEPT' and a['approval_state'][focal]=='ACCEPT'))
            errors['false_agreement']+=int(arm!='ACCEPT' and a['agreement']=='AGREED')
            errors['premature_action']+=int(arm!='ACCEPT' and a['joint_action']!='HOLD')
            errors['over_hold_agreement']+=int(arm=='ACCEPT' and a['agreement']=='PENDING')
            errors['over_hold_action']+=int(arm=='ACCEPT' and a['joint_action']=='HOLD')
        check(dict(errors)==g['error_counts'],'arm_errors')
        costs[arm]={'responses':len(rr),'output_tokens':sum(r['output_tokens'] for r in rr),'generation_seconds':sum(r['generation_seconds'] for r in rr)}
    check(sum(r['output_tokens'] for r in rows)==report['output_tokens'],'output_token_total')
    check(abs(sum(r['generation_seconds'] for r in rows)-report['generation_seconds'])<1e-8,'generation_time_total')
    supplementary={'analysis_timing':'Post-result descriptive audit; formal report unchanged.',
        'agreement_and_execution_only_triplets':counts(all(r['metrics']['agreement'] and r['metrics']['execution'] for r in rr) for rr in triplets.values()),
        'legacy_key_note':'agreement_execution_all_states includes approval_state, agreement, and execution; its 17/18 is not agreement/execution alone.',
        'focal_state_confusion':{arm:dict(Counter(r['answer']['approval_state'][r['focal_role']] for r in rows if r['arm']==arm)) for arm in ('MISSING','HOLD','ACCEPT')},
        'all_own_joint_divergent_readouts':counts(r['strict'] for r in rows if r['role']==r['focal_role']),
        'by_role':{role:counts(r['strict'] for r in rows if r['role']==role) for role in ('A','B','C')},
        'by_case':{case:counts(r['strict'] for r in rows if r['case']==case) for case in ('N01','N02','N03')},
        'by_repeat':{rep:counts(r['strict'] for r in rows if r['repeat']==rep) for rep in (1,2)},
        'repeat_input_count':len(pairs),'repeat_inputs_with_mixed_correctness':sum(len(set(p['strict']))>1 for p in pairs),
        'changed_answers':sum(p['answer_changed'] for p in pairs),'costs':costs,
        'elapsed_seconds':j('run-end.json')['elapsed_seconds'],'environment':j('environment.json'),
        'failure_ids':[r['id'] for r in rows if not r['strict']]}
    save('diagnostics.json',rows);save('evidence-extract.json',{'selection':'Post-result exhaustive six responses for the failed case/reader; no resampling.', 'records':extracts})
    save('repeat-comparison.json',pairs);save('supplementary-analysis.json',supplementary)
    record={'status':'PASS','kind':'WITHIN_PROJECT_STDLIB_CROSSCHECK_NOT_NEW_MODEL_RESULTS',
        'checks':sum(CHECKS.values()),'categories':dict(CHECKS),'archive_sha256':sha256(ARCHIVE.read_bytes()).hexdigest(),
        'sealed_files':len(files),'responses':len(rows),'formal_gate':report['gate'],'totals':report['totals'],
        'model_calls':0,'scorer_imports':0,'formal_score_changes':0,'failure_ids':supplementary['failure_ids']}
    (HERE/'independent-check.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='categories'},ensure_ascii=False))
    print(json.dumps(supplementary,ensure_ascii=False))

if __name__=='__main__':main()
