"""TCV01 uses unchanged TB01 common scoring plus separate comparison diagnostics."""
from collections import Counter
import three_role_boundary_01_scoring as base
import three_role_comparison_vote_01_design as d

strict_json, envelope, counts = base.strict_json, base.envelope, base.counts
METRICS = ('own_holder','own_recommendation','own_sources','vote')


def comparison_reference(payload, case):
    proposed = payload['proposal']['candidate_id']
    other = next(c['candidate_id'] for c in case['candidates'] if c['candidate_id'] != proposed)
    return {'candidate_id':proposed, 'other_candidate_id':other,
            'relation':'HIGHER' if base.best_candidate(case)==proposed else 'LOWER'}


def score(raw, slot, payload, case, finish_reason='EOS'):
    if slot['arm'] == 'DIRECT':
        result = base.score(raw,slot,payload,case,finish_reason)
        result.update(comparison=None,diagnostic_class='NOT_APPLICABLE',extended_strict=result['strict'])
        return result
    result = base.score(None,slot,payload,case)
    result.update(comparison={'binding':None,'relation':None,'correct':None,
        'vote_consistent':None,'comparison_before_vote':None},
        diagnostic_class='UNRESOLVED',extended_strict=None)
    if raw is None: return result
    norm = envelope.normalize(raw,finish_reason)
    result['normalization'] = {k:v for k,v in norm.items() if k!='normalized_bytes'}
    if norm['normalized_bytes'] is None:
        result['format_valid'] = False if finish_reason=='EOS' else None
        result['errors'] = [norm['reason']]; return result
    answer = strict_json.parse(norm['normalized_bytes'])
    errors = base.shape(answer,d.schema_for('COMPARE'))
    result['format_valid'] = not errors
    if errors: result['errors']=errors; return result
    # Projection is ONLY an argument to the unchanged common scorer, never a saved answer repair.
    common = base.score(d.enc({k:answer[k] for k in ('own','vote')}),slot,payload,case)
    result.update({k:v for k,v in common.items() if k not in ('normalization','answer')})
    result['answer'] = answer
    ref = comparison_reference(payload,case); actual = answer['comparison']
    binding = all(actual[k]==ref[k] for k in ('candidate_id','other_candidate_id'))
    relation = actual['relation']==ref['relation']
    comparison_ok = binding and relation
    expected_from_report = 'ACCEPT' if actual['relation']=='HIGHER' else 'HOLD'
    vote = answer['vote']; correct_vote=result['metrics']['vote']
    consistent = (vote['decision']==expected_from_report
                  if binding and vote['proposal_id']==payload['proposal']['proposal_id'] else None)
    result['comparison'] = {'binding':binding,'relation':relation,'correct':comparison_ok,
        'vote_consistent':consistent,'comparison_before_vote':list(answer).index('comparison')<list(answer).index('vote')}
    result['diagnostic_class'] = ('MISBOUND_COMPARISON' if not binding else
        'COMPARISON_'+('CORRECT' if comparison_ok else 'WRONG')+'_VOTE_'+('CORRECT' if correct_vote else 'WRONG'))
    result['extended_strict'] = result['strict'] and comparison_ok
    return result


def classification(values):
    return ('UNRESOLVED' if None in values else 'ALL_CORRECT' if all(values)
            else 'ALL_INCORRECT' if not any(values) else 'MIXED')


def summary_subset(slots, scores):
    return {'strict':counts(scores[s['id']]['strict'] for s in slots),
            'metrics':{m:counts(scores[s['id']]['metrics'][m] for s in slots) for m in METRICS}}


def summarize(design, scores):
    slots=design['allocation']; assert set(scores)=={s['id'] for s in slots}
    result={'unit':design['unit'],'totals':counts(scores[s['id']]['strict'] for s in slots),
            'by_arm':{},'by_input':[],'paired':{},'comparison_diagnostics':{}}
    for arm in d.ARMS:
        sub=[s for s in slots if s['arm']==arm]; out=summary_subset(sub,scores)
        for name,key,levels in [('by_repeat','repeat',d.REPEATS),('by_offer','branch',('HIGHER','LOWER')),
                                ('by_role','role',('A','B','C')),('by_case','case',('T01','T02','T03'))]:
            out[name]={str(level):summary_subset([s for s in sub if s[key]==level],scores) for level in levels}
        errors=Counter()
        for s in sub:
            v=scores[s['id']];a=v['answer'];p=d.payload_for(design,s)
            if a is None: errors['UNRESOLVED_RESPONSE']+=1; continue
            if a['vote']['proposal_id']!=p['proposal']['proposal_id']: errors['WRONG_PROPOSAL_ID']+=1
            if s['branch']=='HIGHER' and a['vote']['decision']=='HOLD': errors['HIGHER_HOLD']+=1
            if s['branch']=='LOWER' and a['vote']['decision']=='ACCEPT': errors['LOWER_ACCEPT']+=1
            if any(v['metrics'][m] is False for m in METRICS[:3]): errors['OWN_INFORMATION_ERROR']+=1
        out['errors_by_type']=dict(errors)
        result['by_arm'][arm]=out
        for item in design['source']['items']:
            group=sorted([s for s in sub if s['input_key']==item['key']],key=lambda s:s['repeat'])
            rows=[scores[s['id']] for s in group]
            decisions=[r['answer']['vote']['decision'] if r['answer'] else None for r in rows]
            vote_records=[r['answer']['vote'] if r['answer'] else None for r in rows]
            voting=[r['metrics']['vote'] for r in rows];common=[r['strict'] for r in rows]
            result['by_input'].append({'key':item['key'],'arm':arm,'slots':[s['id'] for s in group],
                'decisions':decisions,'vote_records':vote_records,'vote_correct':voting,'strict':common,
                'vote_class':classification(voting),'strict_class':classification(common),
                'identical_decisions':None if None in decisions else len(set(decisions))==1,
                'identical_votes':None if None in vote_records else all(v==vote_records[0] for v in vote_records),
                'diagnostic_classes':[r['diagnostic_class'] for r in rows],
                'comparisons':[r['comparison'] for r in rows]})
        out['vote_repeat_classes']=dict(Counter(x['vote_class'] for x in result['by_input'] if x['arm']==arm))
    comp=[scores[s['id']] for s in slots if s['arm']=='COMPARE']
    result['comparison_diagnostics']={'classes':dict(Counter(r['diagnostic_class'] for r in comp)),
        'extended_strict':counts(r['extended_strict'] for r in comp),
        'metrics':{m:counts(r['comparison'][m] for r in comp)
                   for m in ('binding','relation','correct','vote_consistent','comparison_before_vote')}}
    pair_rows=[];pair_counts=Counter();lo=0;hi=0
    for pair in dict.fromkeys(s['pair_id'] for s in slots):
        a={s['arm']:scores[s['id']]['strict'] for s in slots if s['pair_id']==pair}
        direct,compare=a['DIRECT'],a['COMPARE']
        label=('UNRESOLVED' if None in (direct,compare) else 'BOTH_CORRECT' if direct and compare
               else 'DIRECT_ONLY' if direct else 'COMPARE_ONLY' if compare else 'BOTH_INCORRECT')
        pair_counts[label]+=1
        lower=(int(compare) if compare is not None else 0)-(int(direct) if direct is not None else 1)
        upper=(int(compare) if compare is not None else 1)-(int(direct) if direct is not None else 0)
        lo+=lower;hi+=upper
        pair_rows.append({'pair_id':pair,'DIRECT':direct,'COMPARE':compare,'class':label,'difference_bounds':[lower,upper]})
    direction=('INCONCLUSIVE' if pair_counts['UNRESOLVED'] else
               'BETTER_ON_COMMON' if lo>0 else 'WORSE_ON_COMMON' if lo<0 else 'TIED_ON_COMMON')
    result['paired']={'counts':dict(pair_counts),'pairs':pair_rows,'n_pairs':54,
        'difference_count_bounds':[lo,hi],'difference_pp_bounds':[100*lo/54,100*hi/54],'direction':direction}
    missing=result['totals']['unresolved'];failures=result['totals']['incorrect']
    comp_bad=result['comparison_diagnostics']['extended_strict']['incorrect']
    result.update(gate='INCONCLUSIVE' if missing else 'FAIL' if failures or comp_bad else 'PASS_IN_FIXED_COMPARISON',
        observed_failed_responses=failures,unresolved_responses=missing,
        gate_definition='All 108 common outcomes and 54 comparison-extended outcomes correct; condition direction reported separately.')
    result['prespecified_focus']=[x for x in result['by_input'] if x['key'] in ('T02-C-HIGHER','T03-A-LOWER')]
    return result
