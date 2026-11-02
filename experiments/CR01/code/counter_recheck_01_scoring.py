"""CR01 deterministic scoring and actual-response carry. No model imports."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
import experience_update_01_design as base

PROTOCOL='COUNTER-RECHECK-01/v0.1'
PROPOSAL_SHA='002487f9c2d45a87c31eefb0afddfc158c427a92287c7531dce1ef53d0b21ce5'
ROLES=('A','B'); MEDIA=('PAPER','DIGITAL'); TYPES=('OPTIMAL','LOWER','DUPLICATE')
STAGES=('FORM','CONFIRM','RECHECK','USE','RECHECK_DIAGNOSTIC')
enc=base.enc; displayed=base.displayed; digest=base.digest; require=base.require
strict_json=base.strict_json; envelope=base.envelope; shape=base.shape
all_known=base.all_known; counts=base.counts; refs_ok=base.refs_ok; legal=base.legal
SCHEMAS={'FORM':base.schema_object({'local':deepcopy(base.LOCAL)}),
         'CONFIRM':deepcopy(base.SCHEMAS['CONFIRM']),'USE':deepcopy(base.SCHEMAS['USE'])}
SCHEMAS['RECHECK']=deepcopy(SCHEMAS['CONFIRM'])
SCHEMAS['RECHECK']['properties']['reply']['properties']['action']['enum']=['ACCEPT','HOLD']
UNDECIDED={'A':'UNDECIDED','B':'UNDECIDED'}

def prompt_stage(stage):return 'RECHECK' if stage=='RECHECK_DIAGNOSTIC' else stage

def case_for(design,slot):return next(c for c in design['cases'] if c['id']==slot['case'])
def source_for(design,slot):
    if 'diagnostic' in slot:return next(x for x in design['diagnostics'] if x['id']==slot['diagnostic'])
    if 'route' in slot:return next(x for x in design['paths'] if x['id']==slot['route'])
    return case_for(design,slot)
def slot_for(design,sid):return next(s for s in design['allocation'] if s['id']==sid)
def form_id(case,role):return f'CR01-{case}-FORM-{role}'

def record(slot,answer,field):
    return {'record_id':'Q'+digest(['CR01',slot['case'],slot['stage'],slot['role'],field])[:10].upper(),
            'author':slot['role'],'body':deepcopy(answer[field])}

def expected(rows):
    rates={}
    for role in sorted({r['observer'] for r in rows}):
        own=[x for x in rows if x['observer']==role];n=sum(x['attempts_per_medium'] for x in own)
        require(n>0,'EMPTY_EXPERIENCE')
        rates[role]={m:Fraction(40*sum(x[m.lower()+'_success'] for x in own),n) for m in MEDIA}
    local={r:max(v,key=v.get) if v['PAPER']!=v['DIGITAL'] else 'UNDECIDED' for r,v in rates.items()}
    options=[{'A':'PAPER','B':'DIGITAL'},{'A':'DIGITAL','B':'PAPER'}]
    totals=[sum(rates[r][a[r]] for r in ROLES) for a in options] if set(rates)==set(ROLES) else []
    return local,[a for a,t in zip(options,totals) if t==max(totals)],rates

def own_summary(payload,medium_order):
    role=payload['holder'];rows=[r for r in payload['experiences'] if r['observer']==role]
    n=sum(r['attempts_per_medium'] for r in rows);values=expected(rows)[2][role]
    require(all(v.denominator==1 for v in values.values()),'NONINTEGER_FIXED_SUMMARY')
    summary={'observer':role,'experience_refs':[r['episode_id'] for r in rows],
        'attempts_per_medium_total':n,'projected_success_per_40':{m:int(values[m]) for m in medium_order}}
    return summary,{'holder':role,'own_rows_sha256':digest(rows),'input_rows_sha256':digest(payload['experiences']),
        'attempts':n,'success_counts':{m:sum(x[m.lower()+'_success'] for x in rows) for m in medium_order},
        'per_40_fraction':{m:[v.numerator,v.denominator] for m,v in values.items()},'summary_sha256':digest(summary)}

def joint_receipt(case,payload):
    rates=expected(case['experiences'])[2];table=case['joint_candidate_totals']
    require(len(table)==2 and {tuple(c['allocation'][r] for r in ROLES) for c in table}=={('PAPER','DIGITAL'),('DIGITAL','PAPER')},'CANDIDATES')
    for c in table:require(sum(rates[r][c['allocation'][r]] for r in ROLES)==c['projected_total_success_per_40_each'],'CANDIDATE_ARITHMETIC')
    require(payload['joint_candidate_totals']==table,'CANDIDATE_CARRY')
    return {'candidate_table_sha256':digest(table),'totals':[c['projected_total_success_per_40_each'] for c in table],
        'by_role':{r:own_summary(dict(payload,holder=r),case['medium_order'])[1] for r in ROLES},'supplied_to_model':True}

def payload_for(design,slot,states):
    case=case_for(design,slot);stage=slot['stage'];role=slot['role'];source=source_for(design,slot)
    p={'holder':role,'experiences':deepcopy(case['experiences'])}
    if stage=='FORM':
        p['experiences']=[r for r in p['experiences'] if r['observer']==role];return p
    def rec(sid,field):return record(slot_for(design,sid),states[sid],field)
    p['own_judgment']=rec(form_id(case['id'],role),'local')
    if stage in ('CONFIRM','RECHECK','RECHECK_DIAGNOSTIC'):
        p['initial_proposal']=deepcopy(source['initial_proposal'])
        if stage=='RECHECK':p['counter_record']=rec(source['confirm_id'],'reply')
        if stage=='RECHECK_DIAGNOSTIC':p['counter_record']=deepcopy(source['counter_record'])
        p['joint_candidate_totals']=deepcopy(case['joint_candidate_totals'])
    else:
        conf=states[source['confirm_id']];has_recheck=conf['reply']['action']=='COUNTER'
        records=[deepcopy(source['initial_proposal']),rec(source['confirm_id'],'reply')]
        if has_recheck:records.append(rec(source['recheck_id'],'reply'))
        if role==case['peer']:p['own_judgment']=rec(source['confirm_id'],'local')
        elif has_recheck:p['own_judgment']=rec(source['recheck_id'],'local')
        p['joint_records']=records
        p['own_experience_summary']=own_summary(p,case['medium_order'])[0]
    return p

def request_for(design,slot,states):
    return {'id':slot['id'],'seed':slot['seed'],'messages':[
        {'role':'system','content':design['prompts'][prompt_stage(slot['stage'])]},
        {'role':'user','content':'資料JSON:\n'+displayed(payload_for(design,slot,states))}]}

def receive(raw,stage,finish='EOS'):
    if raw is None:return {'answer':None,'format_valid':None,'errors':['NO_RESPONSE'],'normalized_bytes':None,
                          'normalization':{'status':'UNRESOLVED','reason':'NO_RESPONSE'}}
    norm=envelope.normalize(raw,finish);candidate=norm.pop('normalized_bytes')
    answer=strict_json.parse(candidate) if candidate is not None else None
    errors=shape(answer,SCHEMAS[prompt_stage(stage)]) if candidate is not None else [norm['reason']]
    return {'answer':None if errors else answer,'format_valid':not errors if finish=='EOS' else None,
            'errors':errors,'normalized_bytes':candidate,'normalization':norm}

def counter_quality(payload):
    p,c=payload['initial_proposal'],payload['counter_record'];b=c['body'];rows=payload['experiences']
    return {'author':c['author']!=p['author'],'action':b['action']=='COUNTER',
        'reply_to':b['reply_to']==p['record_id'],'experience_refs':refs_ok(b['evidence_refs'],[r['episode_id'] for r in rows]),
        'optimal_allocation':b['allocation'] in expected(rows)[1]}

def agreement(records,rows):
    require(len(records) in (2,3),'RECORD_COUNT')
    p,c=records[:2];cb=c['body'];pair=records[-2:]
    linked=c['author']!=p['author'] and cb['reply_to']==p['record_id']
    if len(records)==2:
        k=linked and cb['action']=='ACCEPT' and cb['allocation']==p['body']['allocation'] and legal(cb['allocation'])
    else:
        r=records[2];rb=r['body']
        k=(linked and cb['action']=='COUNTER' and r['author']==p['author'] and rb['action']=='ACCEPT'
           and rb['reply_to']==c['record_id'] and rb['allocation']==cb['allocation'] and legal(cb['allocation']))
    optimal=pair[0]['body']['allocation'] in expected(rows)[1]
    references=all(refs_ok(x['body']['evidence_refs'],[r['episode_id'] for r in rows]) for x in pair)
    return {'K':k,'G':k and optimal and references,'wrong_agreement':k and not(optimal and references),
            'optimal':optimal,'experience_references':references,'decisive_ids':[x['record_id'] for x in pair],
            'allocation':deepcopy(pair[0]['body']['allocation']) if k else deepcopy(UNDECIDED)}

def score(raw,slot,payload,rows,finish='EOS'):
    stage=slot['stage'];receipt=receive(raw,stage,finish);a=receipt['answer']
    result={k:v for k,v in receipt.items() if k!='normalized_bytes'}
    keys=('L','Z_local','Z_team','H','action_contract','reply_reference','experience_references',
          'appropriate_response','counter_valid','V','efficiency_optimal')
    result.update({k:None for k in keys});result.update(carried_answer=deepcopy(a),applicable=None)
    if stage in ('RECHECK','RECHECK_DIAGNOSTIC') and payload is not None:
        result['counter_quality']=counter_quality(payload)
        result['counter_valid']=all(result['counter_quality'].values())
    if a is None:return result
    local,opts,_=expected(rows);role=slot['role'];own=[r['episode_id'] for r in rows if r['observer']==role]
    result.update(applicable=True,L=a['local']['subject']==role and a['local']['choice']==local[role],
                  Z_local=a['local']['subject']==role and refs_ok(a['local']['evidence_refs'],own))
    if stage=='FORM':result['V']=result['L'] and result['Z_local'];return result
    if stage in ('CONFIRM','RECHECK','RECHECK_DIAGNOSTIC'):
        b=a['reply'];allrefs=[r['episode_id'] for r in rows]
        if stage=='CONFIRM':
            p=payload['initial_proposal'];valid=p['body']['allocation'] in opts
            action=(b['action']=='ACCEPT' and b['allocation']==p['body']['allocation'] if valid else
                    (b['action']=='COUNTER' and b['allocation'] in opts and b['allocation']!=p['body']['allocation']) or
                    (b['action']=='HOLD' and b['allocation']==UNDECIDED))
            reply_to=p['record_id']
        else:
            quality=counter_quality(payload);valid=all(quality.values());result['counter_quality']=quality;result['counter_valid']=valid
            reply_to=payload['counter_record']['record_id']
            action=(b['action']==('ACCEPT' if valid else 'HOLD') and
                    b['allocation']==(payload['counter_record']['body']['allocation'] if valid else UNDECIDED))
        result.update(action_contract=action,reply_reference=b['reply_to']==reply_to,
                      experience_references=refs_ok(b['evidence_refs'],allrefs),efficiency_optimal=b['allocation'] in opts)
        result['Z_team']=result['reply_reference'] and result['experience_references']
        result['appropriate_response']=action and result['Z_team']
        result['V']=result['L'] and result['Z_local'] and result['appropriate_response']
    else:
        ag=agreement(payload['joint_records'],rows);basis='SHARED_DECISION' if ag['K'] else 'UNRESOLVED';b=a['team']
        result.update(H=b['allocation']==ag['allocation'] and b['basis']==basis,
            Z_team=refs_ok(b['evidence_refs'],ag['decisive_ids']) and b['basis']==basis,
            efficiency_optimal=b['allocation'] in opts,agreement_from_input=ag)
        result['V']=result['L'] and result['Z_local'] and result['H'] and result['Z_team']
    return result

def skipped_score(slot,rows):
    result=score(None,slot,None,rows);result.update(applicable=False,errors=['SKIPPED_BY_PROTOCOL'])
    return result

def terminal(design,path,outcomes):
    case=case_for(design,{'case':path['case']});conf=outcomes.get(path['confirm_id'],{});ca=conf.get('answer')
    unk={'K':None,'G':None,'wrong_agreement':None,'category':'UNRESOLVED','records':None,'recheck_required':None}
    if ca is None:return unk
    records=[deepcopy(path['initial_proposal']),record(slot_for(design,path['confirm_id']),ca,'reply')]
    required=ca['reply']['action']=='COUNTER';last=conf
    if required:
        last=outcomes.get(path['recheck_id'],{});ra=last.get('answer')
        if ra is None:return dict(unk,recheck_required=True)
        records.append(record(slot_for(design,path['recheck_id']),ra,'reply'))
    ag=agreement(records,case['experiences'])
    if ag['G']:category='CORRECT_AGREEMENT'
    elif ag['wrong_agreement']:category='WRONG_AGREEMENT'
    elif records[-1]['body']['action']=='HOLD':
        # A broken reply/ref is a malformed nonagreement, not an otherwise valid unnecessary hold.
        if last.get('appropriate_response'):category='APPROPRIATE_HOLD'
        elif last.get('Z_team') and records[-1]['body']['allocation']==UNDECIDED:
            category='UNNECESSARY_HOLD'
        else:category='OTHER_NONAGREEMENT'
    else:category='OTHER_NONAGREEMENT'
    return dict(ag,category=category,records=records,recheck_required=required)

def assess(items):
    components={k:{'counts':c,'required':n,'status':('MET_IN_FIXED_SAMPLE' if c['correct']>=n else
        'NOT_MET' if c['correct']+c['unresolved']<n else 'INCONCLUSIVE')} for k,(c,n) in items.items()}
    return {'status':combine(v['status'] for v in components.values()),'components':components}
def combine(states):
    states=list(states)
    return 'NOT_MET' if 'NOT_MET' in states else 'INCONCLUSIVE' if 'INCONCLUSIVE' in states else 'MET_IN_FIXED_SAMPLE'

def summarize(design,outcomes):
    require(not(set(outcomes)-{s['id'] for s in design['allocation']}),'UNEXPECTED_SCORE_ID')
    get=lambda sid:outcomes.get(sid,{})
    paths=[];transitions=[]
    for p in design['paths']:
        case=case_for(design,p);term=terminal(design,p,outcomes)
        required=p['form_ids']+[p['confirm_id']]+list(p['use_ids'].values())
        if term['recheck_required'] is not False:required.append(p['recheck_id'])
        row={'id':p['id'],'case':p['case'],'initial_type':p['initial_type_not_for_model'],
             'strength':case['strength'],'same_personal':case['same_personal'],'proposer':case['proposer'],
             'J':all_known(get(s).get('V') for s in required),
             'I':all_known(get(s).get(k) for s in required for k in ('L','Z_local')),
             'known_failed_response_ids':[s for s in required if get(s).get('V') is False],**term}
        paths.append(row)
        for role in ROLES:
            saved_id=(p['confirm_id'] if role==case['peer'] else
                      p['recheck_id'] if term['recheck_required'] is not False else form_id(case['id'],role))
            before=get(saved_id);after=get(p['use_ids'][role]);v=(before.get('L'),after.get('L'))
            category='UNRESOLVED' if None in v else {(True,True):'TRUE_TRUE',(True,False):'TRUE_FALSE',(False,True):'FALSE_TRUE',(False,False):'FALSE_FALSE'}[v]
            transitions.append({'route':p['id'],'role':role,'saved_response_id':saved_id,
                'saved_L':before.get('L'),'use_L':after.get('L'),'saved_Z_local':before.get('Z_local'),
                'use_Z_local':after.get('Z_local'),'transition':category})
    diagnostics=[dict(id=x['id'],case=x['case'],counter_type=x['counter_type_not_for_model'],
        expected_action=x['expected_action_not_for_model'],D=get(x['id']+'-RECHECK').get('V'),
        action=(get(x['id']+'-RECHECK').get('answer') or {}).get('reply',{}).get('action')) for x in design['diagnostics']]
    metrics={k:counts(r[k] for r in paths) for k in ('J','I','K','G','wrong_agreement')}
    by_type={t:{k:counts(r[k] for r in paths if r['initial_type']==t) for k in metrics} for t in TYPES}
    gate={'J':(metrics['J'],22),'I':(metrics['I'],24),
        'no_wrong_agreement':(counts(None if r['wrong_agreement'] is None else not r['wrong_agreement'] for r in paths),24)}
    for t in TYPES:
        gate['J_'+t]=(by_type[t]['J'],7);gate['G_'+t]=(by_type[t]['G'],7 if t=='OPTIMAL' else 6)
    main_gate=assess(gate);diag_counts=counts(x['D'] for x in diagnostics);diag_gate=assess({'D':(diag_counts,12)})
    stages={}
    for stage in STAGES:
        selected=[get(s['id']) for s in design['allocation'] if s['stage']==stage]
        active=[r for r in selected if r.get('applicable') is not False]
        keys=('format_valid','L','Z_local','V')+ (('H','Z_team') if stage=='USE' else ('action_contract','reply_reference','experience_references') if stage!='FORM' else ())
        stages[stage]={'planned':len(selected),'skipped_by_protocol':len(selected)-len(active),
                       'metrics':{k:counts(r.get(k) for r in active) for k in keys}}
    natural=[get(p['recheck_id']) for p in design['paths'] if get(p['confirm_id']).get('answer',{}) is not None and
             (get(p['confirm_id']).get('answer') or {}).get('reply',{}).get('action')=='COUNTER']
    recheck={}
    for valid in (True,False,None):
        selected=[r for r in natural if r.get('counter_valid') is valid]
        recheck[str(valid)]={'input_quality':valid,'V':counts(r.get('V') for r in selected),
                            'status':'OBSERVED' if selected else 'NOT_EXERCISED'}
    normal=sorted([r['id'] for r in paths if r['J'] is True],key=lambda x:sha256(('CR01-review|2026092902|'+x).encode()).hexdigest())[:6]
    failed=[s['id'] for s in design['allocation'] if get(s['id']).get('applicable') is not False and get(s['id']).get('V') is not True]
    return {'protocol':PROTOCOL,'metrics':metrics,'by_initial_type':by_type,'paths':paths,
        'terminal_categories':dict(Counter(r['category'] for r in paths)),
        'diagnostics':diagnostics,'diagnostic_metrics':{'D':diag_counts,'by_counter_type':{t:counts(x['D'] for x in diagnostics if x['counter_type']==t) for t in TYPES}},
        'main_progression':main_gate,'diagnostic_progression':diag_gate,
        'progression':{'status':combine([main_gate['status'],diag_gate['status']])},
        'stages':stages,'natural_recheck_by_input_quality':recheck,'saved_to_use':transitions,
        'reason_review':{'status':'PENDING_OFFLINE_REVIEW','nonpassing_or_unknown_responses':failed,
            'normal_paths':normal,'wrong_agreement_paths':[r['id'] for r in paths if r['wrong_agreement'] is True],
            'diagnostic_responses':[x['id']+'-RECHECK' for x in diagnostics]},
        'scope':'8 fresh materials, 24 dependent paths sharing 16 FORM responses; 12 artificial counter diagnoses separate. No p-values or population CI.'}
