"""TAR01: unchanged TB01 six-axis READ scorer plus matched-state summaries."""
import three_role_boundary_01_scoring as base
import three_role_approval_readout_01_design as d

strict_json,envelope=base.strict_json,base.envelope
score=base.score
METRICS=('own_holder','own_recommendation','own_sources','approval_state','agreement','execution')
counts,tri_all=base.counts,base.tri_all

def summarize(design,scores):
    slots=design['allocation'];assert set(scores)=={s['id'] for s in slots}
    def group(sub):
        return {'strict':counts(scores[s['id']]['strict'] for s in sub),
            'metrics':{m:counts(scores[s['id']]['metrics'][m] for s in sub) for m in METRICS}}
    out={'unit':design['unit'],'totals':group(slots)['strict'],'metrics':group(slots)['metrics'],
        'by_arm':{},'triplets':[],'case_replicates':[]}
    for arm in d.ARMS:
        sub=[s for s in slots if s['arm']==arm];g=group(sub)
        g['error_counts']={k:0 for k in ('focal_false_accept','false_agreement','premature_action','over_hold_agreement','over_hold_action','focal_state_other_error')}
        g['interpretable_responses']=sum(scores[s['id']]['answer'] is not None for s in sub)
        for s in sub:
            a=scores[s['id']]['answer']
            if a is None:continue
            focal=d.source_for(design,s)['focal_role'];expected=arm
            e=g['error_counts']
            e['focal_false_accept']+=int(arm!='ACCEPT' and a['approval_state'][focal]=='ACCEPT')
            e['focal_state_other_error']+=int(a['approval_state'][focal]!=expected and not(arm!='ACCEPT' and a['approval_state'][focal]=='ACCEPT'))
            e['false_agreement']+=int(arm!='ACCEPT' and a['agreement']=='AGREED')
            e['premature_action']+=int(arm!='ACCEPT' and a['joint_action']!='HOLD')
            e['over_hold_agreement']+=int(arm=='ACCEPT' and a['agreement']=='PENDING')
            e['over_hold_action']+=int(arm=='ACCEPT' and a['joint_action']=='HOLD')
        out['by_arm'][arm]=g
    for tid in dict.fromkeys(s['triplet_id'] for s in slots):
        sub=[s for s in slots if s['triplet_id']==tid];answers={s['arm']:scores[s['id']]['answer'] for s in sub}
        focal=d.source_for(design,sub[0])['focal_role']
        all_valid=all(a is not None for a in answers.values())
        discriminates=None if answers['MISSING'] is None or answers['HOLD'] is None else (
            answers['MISSING']['approval_state'][focal]=='MISSING' and answers['HOLD']['approval_state'][focal]=='HOLD')
        read_correct=tri_all(scores[s['id']]['metrics'][m] for s in sub for m in METRICS[3:])
        own_correct=tri_all(scores[s['id']]['metrics'][m] for s in sub for m in METRICS[:3])
        own_equal=None if not all_valid else len({d.digest(a['own']) for a in answers.values()})==1
        out['triplets'].append({'id':tid,'case':sub[0]['case'],'role':sub[0]['role'],'repeat':sub[0]['repeat'],
            'strict':tri_all(scores[s['id']]['strict'] for s in sub),'own_correct_all_states':own_correct,
            'own_fields_identical':own_equal,'missing_hold_discrimination':discriminates,
            'agreement_execution_all_states':read_correct})
    out['triplet_totals']=counts(t['strict'] for t in out['triplets'])
    out['paired_metrics']={m:counts(t[m] for t in out['triplets']) for m in
        ('own_correct_all_states','own_fields_identical','missing_hold_discrimination','agreement_execution_all_states')}
    for c in design['cases']:
        for r in d.REPEATS:
            sub=[s for s in slots if s['case']==c['id'] and s['repeat']==r]
            out['case_replicates'].append({'case':c['id'],'repeat':r,'strict':tri_all(scores[s['id']]['strict'] for s in sub)})
    out['case_replicate_totals']=counts(t['strict'] for t in out['case_replicates'])
    missing=out['totals']['unresolved'];failed=out['totals']['incorrect']
    out.update(gate='INCONCLUSIVE' if missing else 'FAIL' if failed else 'PASS_IN_FIXED_READOUT',
        observed_failed_responses=failed,unresolved_responses=missing,
        gate_definition='All 54 responses interpretable and correct on all six axes. Fixed diagnostic, not population inference.',
        provenance={'real_receipt_projection_responses':36,'constructed_HOLD_responses':18,'new_FORM':0,'new_VOTE':0})
    return out
