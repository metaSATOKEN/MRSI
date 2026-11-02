"""CS01 frozen contract, deterministic scoring and actual-response carry. No model imports."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
import experience_update_01_design as base

PROPOSAL_SHA='e7dd9e3bd387e64cf1326894f81ff9707e44cb12f3c0fd65de79b762d16851fa'
SOURCE_ZIP_SHA='26b40a51c11b2f72f6569483dba2b4240436d991e16b5c9046e41671b5606b4d'
PROTOCOL='CONFIRM-SUPPORT-01/v0.1'
METHODS=('BASE','SUPPORT');ROLES=('A','B');MEDIA=('PAPER','DIGITAL')
enc=base.enc;displayed=base.displayed;digest=base.digest;require=base.require
strict_json=base.strict_json;envelope=base.envelope;shape=base.shape
all_known=base.all_known;counts=base.counts;split_records=base.split_records


def packet_for(design,slot):
    return next(p for p in design['packets'] if p['id']==slot['packet'])


def rows_for(packet):
    keys=list(base.ROW_KEYS[:5])+[m.lower()+'_success' for m in packet['medium_order']]
    return [{k:r[k] for k in keys} for r in packet['payloads']['BASE']['experiences']]


def own_summary(payload,medium_order):
    role=payload['holder'];rows=[r for r in payload['experiences'] if r['observer']==role]
    n=sum(r['attempts_per_medium'] for r in rows);require(n>0,'EMPTY_OWN_EXPERIENCE')
    sums={m:sum(r[m.lower()+'_success'] for r in rows) for m in medium_order}
    projected={m:Fraction(40*sums[m],n) for m in medium_order}
    require(all(v.denominator==1 for v in projected.values()),'NON_INTEGER_FROZEN_PREDICTION')
    summary={'observer':role,'experience_refs':[r['episode_id'] for r in rows],
             'attempts_per_medium_total':n,'projected_success_per_40':{m:int(v) for m,v in projected.items()}}
    return summary,{'holder':role,'input_rows_sha256':digest(payload['experiences']),
                    'own_rows_sha256':digest(rows),'experience_refs':summary['experience_refs'],
                    'attempts':n,'success_counts':sums,'per_40_fraction':{m:[v.numerator,v.denominator] for m,v in projected.items()},
                    'summary_sha256':digest(summary),'semantic_repair':False}


def joint_receipt(packet,payload):
    candidates=packet['payloads']['SUPPORT']['joint_candidate_totals'];values={};details={}
    for role in ROLES:
        summary,receipt=own_summary(dict(payload,holder=role),packet['medium_order'])
        values[role]=summary['projected_success_per_40'];details[role]=receipt
    table=deepcopy(candidates)
    for row in table:
        value=sum(values[r][row['allocation'][r]] for r in ROLES)
        require(value==row['projected_total_success_per_40_each'],'JOINT_TOTAL_CHANGED')
    supplied='joint_candidate_totals' in payload
    if supplied:require(payload['joint_candidate_totals']==table,'SUPPLIED_TOTAL_CHANGED')
    return {'by_role':details,'candidate_table_sha256':digest(table),'supplied_to_model':supplied,
            'totals':[r['projected_total_success_per_40_each'] for r in table]}


def record(slot,answer,field):
    return {'author':slot['role'],'body':json.loads(enc(answer[field])),
            'record_id':'Q'+digest(['CS01',slot['packet'],slot['role'],field])[:10].upper()}


def payload_for(design,slot,states):
    packet=packet_for(design,slot)
    if slot['stage']=='CONFIRM':return deepcopy(packet['payloads'][slot['method']])
    require(packet['kind']=='MAIN' and len(slot['parents'])==1,'USE_DEPENDENCY')
    parent=next(s for s in design['allocation'] if s['id']==slot['parents'][0])
    answer=states[parent['id']];source=packet['payloads']['BASE']
    p={'holder':slot['role'],'experiences':rows_for(packet)}
    p['own_judgment']=(deepcopy(source['proposer_judgment']) if slot['role']==packet['target'] else record(parent,answer,'local'))
    records=[deepcopy(source['proposal']),record(parent,answer,'reply')]
    p['joint_records']=[rec for role in packet['role_order'] for rec in records if rec['author']==role]
    p['own_experience_summary']=own_summary(p,packet['medium_order'])[0]
    require(p['own_experience_summary']==packet['own_summaries_by_role'][slot['role']],'OWN_SUMMARY_CHANGED')
    return p


def request_for(design,slot,states):
    return {'id':slot['id'],'seed':slot['seed'],'messages':[
        {'role':'system','content':design['prompts'][slot['stage']]},
        {'role':'user','content':'資料JSON:\n'+displayed(payload_for(design,slot,states))}]}


def receive(raw,stage,finish='EOS',method=None):
    return base.receive(raw,stage,finish)


def score(raw,slot,payload,rows,finish='EOS'):
    # Legacy scorer's temporary confirmation ID uses block; its agreement check
    # depends only on author, actual reply_to, action and allocation.
    result=base.score(raw,dict(slot,block=slot['packet']),payload,rows,finish)
    result['carried_answer']=deepcopy(result['answer'])
    result['V']=all_known([result['L'],result['Z_local'],result['appropriate_response']]) if slot['stage']=='CONFIRM' else None
    return result


def assess(items):
    components={key:{'counts':c,'required':n,'status':('MET_IN_FIXED_SAMPLE' if c['correct']>=n else
        'NOT_MET' if c['correct']+c['unresolved']<n else 'INCONCLUSIVE')} for key,(c,n) in items.items()}
    status=[v['status'] for v in components.values()]
    return {'status':'NOT_MET' if 'NOT_MET' in status else 'INCONCLUSIVE' if 'INCONCLUSIVE' in status else 'MET_IN_FIXED_SAMPLE',
            'components':components}


def paired(rows,metric):
    require(len(rows)==32,'PAIRED_DENOMINATOR')
    without=counts(r['BASE'] for r in rows);with_support=counts(r['SUPPORT'] for r in rows)
    for row in rows:
        values=row['BASE'],row['SUPPORT']
        row['category']='UNRESOLVED' if None in values else {(True,True):'BOTH',(True,False):'BASE_ONLY',
            (False,True):'SUPPORT_ONLY',(False,False):'NEITHER'}[values]
    return {'metric':metric,'n_paired_conditions':32,'BASE':without,'SUPPORT':with_support,
            'difference_missing_bounds':[(with_support['correct']-without['correct']-without['unresolved'])/32,
                                         (with_support['correct']+with_support['unresolved']-without['correct'])/32],
            'categories':dict(Counter(r['category'] for r in rows)),'rows':rows,'not_a_confidence_interval':True}


def summarize(design,outcomes):
    require(not set(outcomes)-{s['id'] for s in design['allocation']},'UNEXPECTED_OUTCOME')
    get=lambda sid:outcomes.get(sid,{})
    main=[];controls=[];pairs=[];diagnostics=[]
    for p in design['packets']:
        for method in METHODS:
            route=p['id']+'-'+method;conf=get(route+'-CONFIRM')
            row={k:p[k] for k in ('id','kind','root','experience_condition','strength','same_personal',
                                 'target_yields','transition','source_history_set','target','peer')}
            row.update(id=route,packet=p['id'],method=method,V=conf.get('V'),L=conf.get('L'),
                Z_local=conf.get('Z_local'),appropriate_response=conf.get('appropriate_response'),
                K=conf.get('K'),C=conf.get('C'),action_contract=conf.get('action_contract'),
                reply_reference=conf.get('reply_reference'),experience_references=conf.get('experience_references'),
                action=(conf.get('answer') or {}).get('reply',{}).get('action'))
            if p['kind']=='CONTROL':
                row.update(control_type=p['control_type'],D=conf.get('V'));controls.append(row);continue
            uses={r:get(route+'-USE-'+r) for r in ROLES}
            row.update(J=all_known([conf.get('V'),conf.get('C')]+[u.get(k) for u in uses.values() for k in ('L','H','Z')]),
                U_target=all_known([uses[p['target']].get(k) for k in ('L','Z_local')]),
                U_peer=all_known([uses[p['peer']].get(k) for k in ('L','Z_local')]),
                S=uses[p['target']].get('L'),I=all_known([conf.get('L'),uses[p['peer']].get('L')]),uses=uses)
            main.append(row)
            for role in ROLES:
                saved_L=True if role==p['target'] else conf.get('L')
                saved_Z=True if role==p['target'] else conf.get('Z_local')
                used=uses[role].get('L');comb=(saved_L,used)
                category='UNRESOLVED' if None in comb else {(True,True):'TRUE_TRUE',(True,False):'TRUE_FALSE',
                    (False,True):'FALSE_TRUE',(False,False):'FALSE_FALSE'}[comb]
                diagnostics.append({'route':route,'role':role,'function':'TARGET' if role==p['target'] else 'PEER',
                    'saved_L':saved_L,'saved_Z_local':saved_Z,'use_L':used,'use_Z_local':uses[role].get('Z_local'),
                    'transition':category})
    for method in METHODS:
        for root in sorted({r['root'] for r in main}):
            rows=[r for r in main if r['root']==root and r['method']==method]
            require(len(rows)==2,'TWO_EXPERIENCE_CONDITIONS')
            pairs.append({'root':root,'method':method,'strength':rows[0]['strength'],
                'source_history_set':rows[0]['source_history_set'],
                'Q':all_known(r['J'] for r in rows),'S_target':all_known(r['S'] for r in rows),
                'I_peer':all_known(r['I'] for r in rows)})
    metrics={};confirmation_gates={};end_gates={};control_metrics={};strata={}
    for method in METHODS:
        rows=[r for r in main if r['method']==method];pr=[r for r in pairs if r['method']==method]
        cr=[r for r in controls if r['method']==method]
        metrics[method]={k:counts(r[k] for r in rows) for k in ('V','L','Z_local','appropriate_response','K','C',
             'action_contract','reply_reference','experience_references','J','U_target','U_peer')}
        metrics[method].update({k:counts(r[k] for r in pr) for k in ('Q','S_target','I_peer')})
        metrics[method].update({k:counts(u.get(k) for r in rows for u in r['uses'].values()) for k in ('H','Z','efficiency_optimal')})
        control_metrics[method]={'D':counts(r['D'] for r in cr),
            'by_type':{t:{'D':counts(r['D'] for r in cr if r['control_type']==t),
                         'actions':dict(Counter(r['action'] or 'UNKNOWN' for r in cr if r['control_type']==t))}
                       for t in ('SUBOPTIMAL_LEGAL','ILLEGAL_DUPLICATE')}}
        confirmation_gates[method]=assess({'V':(metrics[method]['V'],30),'L':(metrics[method]['L'],32),
            'Z_local':(metrics[method]['Z_local'],32),'control_D':(control_metrics[method]['D'],8)})
        items={k:(metrics[method][k],n) for k,n in [('Q',14),('S_target',16),('I_peer',16)]}
        for field,values in [('source_history_set',(1,2)),('strength',('WEAK','STRONG'))]:
            for value in values:items[f'Q_{field}_{value}']=(counts(r['Q'] for r in pr if r[field]==value),7)
        end_gates[method]=assess(items)
        strata[method]={}
        for field in ('strength','same_personal','experience_condition','source_history_set','target_yields','transition'):
            strata[method][field]={str(v):{k:counts(r[k] for r in rows if r[field]==v) for k in ('V','L','Z_local','C','J','U_target','U_peer')}
                                  for v in sorted({r[field] for r in rows},key=str)}
        strata[method]['strength_preference_experience']=[{'strength':s,'same_personal':same,'experience_condition':arm,
            'V':counts(r['V'] for r in rows if (r['strength'],r['same_personal'],r['experience_condition'])==(s,same,arm))}
            for s in ('WEAK','STRONG') for same in (False,True) for arm in ('REVERSE','REINFORCE')]
    paired_results={}
    for metric in ('V','J','U_target','U_peer'):
        paired_results[metric]=paired([{'packet':p['id'],**{m:next(r[metric] for r in main if r['packet']==p['id'] and r['method']==m) for m in METHODS}}
                                       for p in design['packets'] if p['kind']=='MAIN'],metric)
    review=sorted([r['id'] for r in main if r['J'] is True],
                  key=lambda rid:sha256(('CS01-review|2026092901|'+rid).encode()).hexdigest())[:8]
    failed=[s['id'] for s in design['allocation'] if
            (get(s['id']).get('V') if s['stage']=='CONFIRM' else all_known(get(s['id']).get(k) for k in ('L','H','Z'))) is not True]
    states=[confirmation_gates['SUPPORT']['status'],end_gates['SUPPORT']['status']]
    return {'protocol':PROTOCOL,'metrics':metrics,'control_metrics':control_metrics,'paired':paired_results,
        'confirmation_progression':confirmation_gates['SUPPORT'],'confirmation_progression_by_method':confirmation_gates,
        'end_to_end_progression':end_gates['SUPPORT'],'end_to_end_progression_by_method':end_gates,
        'progression':{'status':'NOT_MET' if 'NOT_MET' in states else 'INCONCLUSIVE' if 'INCONCLUSIVE' in states else 'MET_IN_FIXED_SAMPLE'},
        'paths':main,'controls':controls,'pairs':pairs,'strata':strata,'saved_to_use':diagnostics,
        'reason_review':{'status':'PENDING_OFFLINE_REVIEW','nonpassing_or_unknown_responses':failed,'normal_paths':review},
        'scope':'32 paired known conditions from 16 source roots; 8 derived controls separately; no population inference'}
