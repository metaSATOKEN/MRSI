"""Unchanged TB01 per-vote scoring, with TVR01 repetition summaries."""
from collections import Counter
import three_role_boundary_01_scoring as base
import three_role_vote_repeat_01_design as d

score = base.score
strict_json, envelope = base.strict_json, base.envelope
counts = base.counts
METRICS = ('own_holder','own_recommendation','own_sources','vote')


def repeat_class(values):
    if None in values: return 'UNRESOLVED'
    if all(values): return 'ALL_CORRECT'
    if not any(values): return 'ALL_INCORRECT'
    return 'MIXED'


def summarize(design, scores):
    slots=design['allocation']
    assert set(scores)=={s['id'] for s in slots}
    report={'unit':design['unit'],'totals':counts(scores[s['id']]['strict'] for s in slots),
            'metrics':{m:counts(scores[s['id']]['metrics'][m] for s in slots) for m in METRICS},
            'by_repeat':{},'by_offer':{},'by_role':{},'by_case':{},'by_own_assignment_match':{},'by_input':[]}
    for name,key,levels in [('by_repeat','repeat',d.REPEATS),('by_offer','branch',('HIGHER','LOWER')),
                            ('by_role','role',('A','B','C')),('by_case','case',('T01','T02','T03'))]:
        for level in levels:
            subset=[s for s in slots if s[key]==level]
            report[name][str(level)]={'strict':counts(scores[s['id']]['strict'] for s in subset),
                'metrics':{m:counts(scores[s['id']]['metrics'][m] for s in subset) for m in METRICS}}
    errors=Counter()
    for item in design['source']['items']:
        group=sorted([s for s in slots if s['input_key']==item['key']],key=lambda s:s['repeat'])
        results=[scores[s['id']] for s in group]
        case=d.case_for(design,group[0]);p=d.payload_for(design,group[0])
        own=base.own_reference(case,item['role'])
        candidate=next(c for c in case['candidates'] if c['candidate_id']==p['proposal']['candidate_id'])
        match=own['recommendation']==candidate['assignment'][item['role']]
        decisions=[v['answer']['vote']['decision'] if v['answer'] else None for v in results]
        vote_records=[v['answer']['vote'] if v['answer'] else None for v in results]
        voting=[v['metrics']['vote'] for v in results]
        strict=[v['strict'] for v in results]
        for v in results:
            if v['answer'] is None: errors['UNRESOLVED_RESPONSE']+=1;continue
            a=v['answer']
            if a['vote']['proposal_id']!=p['proposal']['proposal_id']:errors['WRONG_PROPOSAL_ID']+=1
            if item['branch']=='HIGHER' and a['vote']['decision']=='HOLD':errors['HIGHER_HOLD']+=1
            if item['branch']=='LOWER' and a['vote']['decision']=='ACCEPT':errors['LOWER_ACCEPT']+=1
            if any(v['metrics'][m] is False for m in METRICS[:3]):errors['OWN_INFORMATION_ERROR']+=1
        report['by_input'].append({'key':item['key'],'case':item['case'],'role':item['role'],'offer':item['branch'],
            'source_slot_id':item['source_slot_id'],'slots':[s['id'] for s in group],
            'own_assignment_match':match,'decisions':decisions,'vote_records':vote_records,
            'vote_correct':voting,'strict':strict,'vote_class':repeat_class(voting),'strict_class':repeat_class(strict),
            'identical_decisions':None if None in decisions else len(set(decisions))==1,
            'identical_votes':None if None in vote_records else all(x==vote_records[0] for x in vote_records),
            'metrics':{m:[v['metrics'][m] for v in results] for m in METRICS}})
    for match in (True,False):
        rows=[x for x in report['by_input'] if x['own_assignment_match']==match]
        report['by_own_assignment_match'][str(match)]={'inputs':len(rows),
            'strict':counts(v for r in rows for v in r['strict']), 'vote':counts(v for r in rows for v in r['vote_correct'])}
    report['vote_repeat_classes']=dict(Counter(x['vote_class'] for x in report['by_input']))
    report['strict_repeat_classes']=dict(Counter(x['strict_class'] for x in report['by_input']))
    report['errors_by_type']=dict(errors)
    report['prespecified_focus']=next(x for x in report['by_input'] if x['key']=='T02-C-HIGHER')
    missing=report['totals']['unresolved']; failures=report['totals']['incorrect']
    report.update(gate='INCONCLUSIVE' if missing else 'FAIL' if failures else 'PASS_IN_FIXED_REPEAT',
        observed_failed_responses=failures,unresolved_responses=missing,
        gate_definition='All 54 new responses interpretable and all four axes correct; no old outcome pooling.')
    return report
