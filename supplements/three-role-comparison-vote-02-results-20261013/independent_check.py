"""Post-run cross-check using stdlib only; no experiment scorer or model imports.

This is a separately implemented check within the same project, not an
independent replication. The raw archive and the preregistered score stay fixed.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT = ROOT / 'study2/results/three-role-comparison-vote-02-20261013'
ARCHIVE = ROOT / 'npp-tcv02-result-20261013-061923-878369ad.zip'
CHECKS = Counter()


def check(ok, category, detail=''):
    if not ok:
        raise AssertionError((category, detail))
    CHECKS[category] += 1


def pairs(items):
    d = {}
    for k, v in items:
        check(k not in d, 'unique_json_key', k)
        d[k] = v
    return d


def parse(raw):
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def shape(obj, schema):
    t = schema['type']
    if t == 'object':
        check(type(obj) is dict and set(obj) == set(schema['required']), 'schema_object')
        for k, v in obj.items(): shape(v, schema['properties'][k])
    elif t == 'array':
        check(type(obj) is list and schema['minItems'] <= len(obj) <= schema['maxItems'], 'schema_array')
        for v in obj: shape(v, schema['items'])
    else:
        check(type(obj) is str, 'schema_string')
        check(obj in schema['enum'] if 'enum' in schema else schema['minLength'] <= len(obj) <= schema['maxLength'], 'schema_value')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def main():
    with zipfile.ZipFile(ARCHIVE) as z:
        check(len(z.namelist()) == len(set(z.namelist())), 'unique_archive_members')
        files = {n: z.read(n) for n in z.namelist()}
    manifest = parse(files.pop('FEEDBACK_MANIFEST.json'))
    check(set(files) == set(manifest['files_sha256']), 'manifest_members')
    for n, b in files.items(): check(sha256(b).hexdigest() == manifest['files_sha256'][n], 'file_hash', n)
    def j(n): return parse(files[n])
    frozen = json.loads((HERE.parent / 'three-role-comparison-vote-02-preparation-20261013/payload.json').read_bytes())
    check(j('payload.json') == frozen, 'frozen_payload')
    design = j('design.json')
    check(design == json.loads(frozen['design_text']), 'frozen_design')
    report = json.loads((RESULT / 'reaggregated.json').read_bytes())['report']
    for n in files:
        if n.startswith('report-') and n.endswith('.json'): check(j(n) == report, 'archived_report')
    before = {}
    for stage, count in [('FORM',9),('VOTE',108)]:
        pre = j('tokenizer-preflight-'+stage.lower()+'.json')
        check(pre['status'] == 'PASS' and len(pre['checked']) == count and pre['blocked_ids'] == [], 'actual_tokenizer_preflight')
        check({r['id'] for r in pre['checked']} == {s['id'] for s in design['allocation'] if s['stage']==stage}, 'stage_preflight_id_set')
        before.update({r['id']:r for r in pre['checked']})
    check(set(before) == {s['id'] for s in design['allocation']}, 'preflight_id_set')
    old = json.loads((HERE.parent/'three-role-comparison-vote-01-preparation-20261013/payload.json').read_bytes())
    old_design = json.loads(old['design_text'])
    check(design['compare_instruction']==old_design['compare_instruction'] and design['model']==old_design['model'], 'unchanged_comparison_model')
    for a in ('DIRECT','COMPARE'):check(design['schemas'][a]==old_design['schemas'][a], 'unchanged_vote_schema')
    new_ids={e['id'] for c in design['cases'] for e in c['experiences']}
    old_ids={e['id'] for c in old_design['cases'] for e in c['experiences']}
    check(len(new_ids)==18 and not new_ids.intersection(old_ids),'new_experience_ids')
    def signature(c):
        return sorted(tuple(sorted(sum(e['observed'][m]['success'] for e in c['experiences'] if e['owner']==r) for m in ('PAPER','DIGITAL'))) for r in ('A','B','C'))
    check(all(signature(n)!=signature(o) for n in design['cases'] for o in old_design['cases']),'new_numeric_signatures')
    rows, formations, extracts = [], [], []
    parent_uses=Counter(); states={}
    for slot in design['allocation']:
        sid, role, arm, stage = slot['id'], slot['role'], slot['arm'], slot['stage']
        path='responses/'+sid+'/'
        inp,response,saved=j(path+'input.json'),j(path+'response.json'),j(path+'result.json')
        case=next(c for c in design['cases'] if c['id']==slot['case'])
        rates,refs,summary={},{},{}
        for r in ('A','B','C'):
            exp=[e for e in case['experiences'] if e['owner']==r];refs[r]=[e['id'] for e in exp]
            summary[r]={m:{'success':sum(e['observed'][m]['success'] for e in exp),'trials':sum(e['observed'][m]['trials'] for e in exp)} for m in ('PAPER','DIGITAL')}
            rates[r]={m:Fraction(v['success'],v['trials']) for m,v in summary[r].items()}
            for m in summary[r]:summary[r][m]['expected_success_for_40']=int(40*rates[r][m])
        totals={c['candidate_id']:sum(40*rates[r][c['assignment'][r]] for r in rates) for c in case['candidates']}
        check(len(set(totals.values()))==2,'no_tie',sid)
        payload={'holder':role,'scene':case['scene'],'schema':design['schemas'][arm],
            'experiences':[e for e in case['experiences'] if stage!='FORM' or e['owner']==role],
            'own_experience_summary':{'owner':role,'source_ids':refs[role],'by_medium':summary[role]}}
        binding={};parent=None;proposed=None
        if stage=='VOTE':
            table=[]
            for c in case['candidates']:
                check(Counter(c['assignment'].values())==case['resource_count'],'feasible_assignment',sid)
                table.append({**c,'expected_success_by_role':{r:int(40*rates[r][c['assignment'][r]]) for r in rates},
                    'expected_total':int(totals[c['candidate_id']]),'source_ids':[e['id'] for e in case['experiences']]})
            proposed=(max if slot['branch']=='HIGHER' else min)(totals,key=totals.get)
            proposal='P'+sha256(f"TCV02|{case['id']}|{proposed}".encode()).hexdigest()[:8]
            parent=f"TCV02-{case['id']}-FORM-{role}"
            check(slot['parents']==[parent] and parent in states,'form_only_dependency',sid)
            pp='responses/'+parent+'/'
            binding={parent:{'answer_sha256':sha256(files[pp+'answer.txt']).hexdigest(),
                'carry_answer_sha256':sha256(files[pp+'carry-answer.json']).hexdigest(),
                'result_sha256':sha256(files[pp+'result.json']).hexdigest()}}
            payload.update(candidates=table,resource_count=case['resource_count'],
                proposal={'proposal_id':proposal,'candidate_id':proposed},own_saved_note=states[parent]['own'])
            parent_uses[parent]+=1
        else:check(slot['parents']==[],'root_formation',sid)
        instruction=design['prompts'][stage]+(design['compare_instruction'] if arm=='COMPARE' else '')
        expected=[{'role':'system','content':instruction},{'role':'user','content':canonical(payload).decode()}]
        check(inp['messages']==expected,'actual_input_arm_contract',sid)
        check(inp['binding']==binding,'actual_parent_hash_binding',sid)
        check(inp['id']==sid and inp['seed']==slot['seed']==response['seed'],'id_seed',sid)
        prepared=inp['prepared']
        check(sha256(canonical(prepared)).hexdigest()==before[sid]['prepared_sha256'],'preflight_actual_tokenization',sid)
        check(sha256(prepared['rendered_prompt'].encode()).hexdigest()==before[sid]['rendered_sha256'],'render_hash',sid)
        check(len(prepared['input_ids'])==before[sid]['input_tokens'],'input_token_count',sid)
        rendered=''.join('<|im_start|>'+m['role']+'\n'+m['content'].strip()+'<|im_end|>\n' for m in expected)
        rendered+='<|im_start|>assistant\n<think>\n\n</think>\n\n'
        check(prepared['rendered_prompt']==rendered,'full_render',sid)
        raw=files[path+'answer.txt'];answer=parse(raw);shape(answer,design['schemas'][arm])
        check(response['finish_reason']=='EOS' and response['output_token_ids'][-1]==j('tokenizer-binding.json')['eos_token_id'],'eos',sid)
        check(response['answer_text'].encode()==raw==files[path+'normalized-answer.txt'],'no_format_repair',sid)
        check(answer==j(path+'saved-answer.json')==j(path+'carry-answer.json')==saved['score']['answer'],'full_answer_preserved',sid)
        check(saved['score']['format_valid'] is True and not response.get('synthetic_fixture'),'real_valid_response',sid)
        trace=j(path+'carry-trace.json')
        check(trace['semantic_repair'] is False and trace['host_agreement_supplied'] is False,'no_host_repair',sid)
        check(trace['parents']==binding and trace['shared_form_parent']==parent,'trace_parent',sid)
        check(trace['shared_form_answer_sha256']==(binding[parent]['carry_answer_sha256'] if parent else None),'trace_parent_hash',sid)
        check(trace['payload_sha256']==sha256(canonical(payload)).hexdigest(),'trace_payload',sid)
        own=answer['own']
        metrics={'own_holder':own['holder']==role,
            'own_recommendation':own['recommendation']==max(rates[role],key=rates[role].get),
            'own_sources':Counter(own['evidence_ids'])==Counter(refs[role])}
        comparison=None;cls='NOT_APPLICABLE';relation=None;expected_vote=None;offered=None
        if stage=='VOTE':
            relation='HIGHER' if proposed==max(totals,key=totals.get) else 'LOWER'
            expected_vote='ACCEPT' if relation=='HIGHER' else 'HOLD'
            vote=answer['vote'];metrics['vote']=vote=={'proposal_id':proposal,'decision':expected_vote}
            offered=next(c['assignment'][role] for c in case['candidates'] if c['candidate_id']==proposed)
            if arm=='COMPARE':
                c=answer['comparison'];other=next(k for k in totals if k!=proposed)
                bound=c['candidate_id']==proposed and c['other_candidate_id']==other
                correct_relation=c['relation']==relation;correct=bound and correct_relation
                consistent=vote['decision']==('ACCEPT' if c['relation']=='HIGHER' else 'HOLD') if bound and vote['proposal_id']==proposal else None
                comparison={'binding':bound,'relation':correct_relation,'correct':correct,'vote_consistent':consistent,
                    'comparison_before_vote':list(answer).index('comparison')<list(answer).index('vote')}
                cls='MISBOUND_COMPARISON' if not bound else 'COMPARISON_'+('CORRECT' if correct else 'WRONG')+'_VOTE_'+('CORRECT' if metrics['vote'] else 'WRONG')
        strict=all(metrics.values());extended=strict and (comparison['correct'] if comparison else True)
        check(metrics==saved['score']['metrics'] and strict==saved['score']['strict'],'common_scoring',sid)
        check(comparison==saved['score']['comparison'] and cls==saved['score']['diagnostic_class'] and extended==saved['score']['extended_strict'],'comparison_scoring',sid)
        row={**slot,'answer':answer,'expected_vote':expected_vote,'expected_relation':relation,
            'candidate_totals':{k:float(v) for k,v in totals.items()},'own_success_for_40':{k:float(40*v) for k,v in rates[role].items()},
            'offered_assignment':offered,'own_assignment_match':own['recommendation']==offered if offered else None,
            'metrics':metrics,'strict':strict,'comparison':comparison,'diagnostic_class':cls,'extended_strict':extended,
            'input_tokens':len(prepared['input_ids']),'output_tokens':len(response['output_token_ids']),
            'answer_bytes':len(raw),'generation_seconds':response['generation_seconds']}
        if stage=='FORM':formations.append(row);states[sid]=answer
        else:rows.append(row)
        # Descriptive worked examples, selected after observing the completed run.
        if slot['case']=='N01' and role=='A' and (stage=='FORM' or slot['repeat']==1):
            extracts.append({'slot':slot,'input':inp,'raw_answer':raw.decode(),'score':saved['score']})
    check(parent_uses=={r['id']:12 for r in formations},'shared_parent_twelve_uses')
    all_rows=formations+rows
    check(len(all_rows)==report['attempted_generations']==117 and report['stage_counts']=={'FORM':9,'VOTE':108},'response_count')
    check(sum(r['strict'] for r in formations)==report['formation']['strict']['correct']==9,'formation_total')
    for m in ('own_holder','own_recommendation','own_sources'):
        check(sum(r['metrics'][m] for r in formations)==report['formation']['metrics'][m]['correct'],'formation_metric',m)
    check(sum(r['strict'] for r in rows)==report['totals']['correct'],'common_total')
    check(sum(r['output_tokens'] for r in all_rows)==report['output_tokens'],'token_total')
    check(abs(sum(r['generation_seconds'] for r in all_rows)-report['generation_seconds'])<1e-8,'duration_total')
    costs={}
    for arm in ('FORM','DIRECT','COMPARE'):
        group=[r for r in all_rows if r['arm']==arm]
        costs[arm]={'responses':len(group),'output_tokens':sum(r['output_tokens'] for r in group),
            'mean_output_tokens':sum(r['output_tokens'] for r in group)/len(group),
            'mean_answer_bytes':sum(r['answer_bytes'] for r in group)/len(group),
            'generation_seconds':sum(r['generation_seconds'] for r in group),
            'input_tokens_minmax':[min(r['input_tokens'] for r in group),max(r['input_tokens'] for r in group)]}
        if arm=='FORM':continue
        expected=report['by_arm'][arm]
        check(len(group)==expected['strict']['planned']==54 and sum(r['strict'] for r in group)==expected['strict']['correct'],'arm_score',arm)
        for m in group[0]['metrics']:check(sum(r['metrics'][m] for r in group)==expected['metrics'][m]['correct'],'arm_metric',arm+'/'+m)
        for name,field in [('by_repeat','repeat'),('by_offer','branch'),('by_role','role'),('by_case','case')]:
            for level,e in expected[name].items():
                sub=[r for r in group if str(r[field])==level]
                check(len(sub)==e['strict']['planned'] and sum(r['strict'] for r in sub)==e['strict']['correct'],'stratum_total',arm+'/'+name+'/'+level)
                for m in sub[0]['metrics']:check(sum(r['metrics'][m] for r in sub)==e['metrics'][m]['correct'],'stratum_metric',arm+'/'+name+'/'+level+'/'+m)
    for item in report['by_input']:
        sub=sorted([r for r in rows if r['arm']==item['arm'] and r['input_key']==item['key']],key=lambda r:r['repeat'])
        truth=[r['metrics']['vote'] for r in sub];decisions=[r['answer']['vote']['decision'] for r in sub]
        cls='ALL_CORRECT' if all(truth) else 'ALL_INCORRECT' if not any(truth) else 'MIXED'
        check(len(sub)==3 and decisions==item['decisions'] and truth==item['vote_correct'] and cls==item['vote_class'],'repeat_group',item['key'])
    comp=[r for r in rows if r['arm']=='COMPARE'];cd=report['comparison_diagnostics']
    check(dict(Counter(r['diagnostic_class'] for r in comp))==cd['classes'],'comparison_classes')
    check(sum(r['extended_strict'] for r in comp)==cd['extended_strict']['correct'],'extended_total')
    for m in cd['metrics']:check(sum(r['comparison'][m] is True for r in comp)==cd['metrics'][m]['correct'],'comparison_metric',m)
    pc=Counter();seeds=set();delta=0
    for pair in report['paired']['pairs']:
        sub=[r for r in rows if r['pair_id']==pair['pair_id']];a={r['arm']:r['strict'] for r in sub}
        check(len(sub)==2 and sub[0]['seed']==sub[1]['seed'],'pair_seed',pair['pair_id']);seeds.add(sub[0]['seed'])
        cls='BOTH_CORRECT' if all(a.values()) else 'DIRECT_ONLY' if a['DIRECT'] else 'COMPARE_ONLY' if a['COMPARE'] else 'BOTH_INCORRECT'
        d=int(a['COMPARE'])-int(a['DIRECT']);delta+=d;pc[cls]+=1
        check(a['DIRECT']==pair['DIRECT'] and a['COMPARE']==pair['COMPARE'] and cls==pair['class'] and pair['difference_bounds']==[d,d],'paired_score')
    all_seeds={r['seed'] for r in all_rows}
    check(len(seeds)==54 and len(all_seeds)==63 and not all_seeds.intersection(design['source']['old_seeds']),'new_pair_and_form_seeds')
    for rep in (1,2,3):check(Counter(r['arm'] for r in rows if r['repeat']==rep and r['arm_position']==1)=={'DIRECT':9,'COMPARE':9},'balanced_order')
    check(dict(pc)==report['paired']['counts'] and report['paired']['difference_count_bounds']==[delta,delta],'paired_totals')
    check(report['paired']['difference_pp_bounds']==[100*delta/54]*2,'paired_pp')
    check(report['paired']['direction']==('BETTER_ON_COMMON' if delta>0 else 'WORSE_ON_COMMON' if delta<0 else 'TIED_ON_COMMON'),'paired_direction')
    failures=[r['id'] for r in all_rows if not r['strict']]
    vote_gate='FAIL' if any(not r['strict'] for r in rows) or any(not r['extended_strict'] for r in comp) else 'PASS_IN_FIXED_COMPARISON'
    gate='FAIL' if failures else vote_gate
    check(gate==report['gate'] and vote_gate==report['vote_gate'] and report['unresolved_responses']==0,'gate')
    match_counts={a:{('MATCH' if match else 'DIFFERENT'):sum(r['own_assignment_match']==match for r in rows if r['arm']==a) for match in (True,False)} for a in ('DIRECT','COMPARE')}
    result={'status':'PASS','kind':'POSTRUN_STDLIB_CROSSCHECK_WITHIN_SAME_PROJECT','checks':dict(CHECKS),'total_checks':sum(CHECKS.values()),
        'archive_sha256':sha256(ARCHIVE.read_bytes()).hexdigest(),'archive_bytes':ARCHIVE.stat().st_size,'sealed_files':len(files),
        'response_count':117,'formation_count':9,'vote_count':108,'gate':gate,'vote_gate':vote_gate,'failure_ids':failures,
        'paired_counts':dict(pc),'comparison_classes':cd['classes'],'own_assignment_counts':match_counts,
        'elapsed_seconds':j('run-end.json')['elapsed_seconds'],'generation_seconds':report['generation_seconds'],
        'gpu':j('environment.json')['gpu'],'arm_costs':costs,'model_calls_in_this_check':0}
    previous_report=json.loads((ROOT/'study2/results/three-role-comparison-vote-01-20261013/reaggregated.json').read_bytes())['report']
    comparison={'scope':'Separate runs and materials, descriptive only; no pooled denominator.',
        'TCV01':{'material':'previously used triads','formation':'prior TB01 saved notes','by_arm':{a:previous_report['by_arm'][a]['strict'] for a in ('DIRECT','COMPARE')},'paired_counts':previous_report['paired']['counts']},
        'TCV02':{'material':'3 texts/materials not previously used in this study','formation':'9 shared first-pass FORM responses','by_arm':{a:report['by_arm'][a]['strict'] for a in ('DIRECT','COMPARE')},'paired_counts':report['paired']['counts']},
        'TCV02_repeats':report['by_input']}
    outputs=[(HERE/'independent-check.json',result),(RESULT/'diagnostics.json',rows),(RESULT/'formation-diagnostics.json',formations),
        (RESULT/'evidence-extract.json',{'selection':'Post-run descriptive N01/A formation and first-replicate high/low votes, both arms; not prespecified.', 'records':extracts}),
        (RESULT/'repeat-comparison.json',comparison)]
    for p,v in outputs:
        data=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
        if p.exists():check(p.read_bytes()==data,'saved_output_unchanged',str(p))
        else:p.write_bytes(data)
    copy=RESULT/ARCHIVE.name
    if not copy.exists():shutil.copy2(ARCHIVE,copy)
    check(copy.read_bytes()==ARCHIVE.read_bytes(),'copied_archive')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
