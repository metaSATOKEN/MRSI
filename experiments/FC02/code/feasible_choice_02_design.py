"""FC02 fixed materials, explicit candidate copying and scoring; stdlib only."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import zipfile
import experience_update_01_design as base

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'study2/designs/feasible-choice-02-20260928/frozen-v0.1'
PROPOSAL=ROOT/'study2/designs/feasible-choice-02-20260928/materials-proposal.json'
PROPOSAL_SHA='379561aa43e2adba9a9cd33c599359b20f19e8ab9279cc01a909148f7d711b0e'
SOURCE_ZIP=ROOT/'study2/results/feasible-choice-01-20260928/npp-fc01-result-20260928-071028-7f89d155.zip'
SOURCE_ZIP_SHA='839423abccb5142bdaecb87db1a415839f0a65b498db76b8ec35d4412459b792'
PROTOCOL='FEASIBLE-CHOICE-02/v0.1'
METHODS=('DIRECT','SELECT'); ARMS=base.ARMS; ROLES=base.ROLES; MEDIA=base.MEDIA; CHOICES=base.CHOICES
enc=base.enc; displayed=base.displayed; digest=base.digest; require=base.require
shape=base.shape; legal=base.legal; refs_ok=base.refs_ok; all_known=base.all_known; counts=base.counts
strict_json=base.strict_json; envelope=base.envelope
expected_from_rows=base.expected_from_rows; split_records=base.split_records; agreement=base.agreement

SELECT_PROPOSAL=base.schema_object({'candidate_id':{'type':'string','maxLength':64},'evidence_refs':base.REFS})
SCHEMAS={'PROPOSE_DIRECT':deepcopy(base.SCHEMAS['PROPOSE']),
         'PROPOSE_SELECT':base.schema_object({'local':base.LOCAL,'proposal':SELECT_PROPOSAL}),
         'CONFIRM':deepcopy(base.SCHEMAS['CONFIRM']),'USE':deepcopy(base.SCHEMAS['USE'])}
PROPOSE_COMMON=base.COMMON+'''あなたには新しい第3回の経験が届いています。previous_private_judgmentsは二役の以前の本人判断、previous_joint_recordsは以前の共同提案と確認の履歴です。以前は未合意の場合もあります。
現在の全経験から本人判断を更新し、今回の共同案を一つ提案してください。割付が以前と同じでも、現在の資料であらためて提案します。まだ相手の今回の承認はありません。
candidatesは共同作業で実施可能な二つの割付です。candidate_idはその資料内の名前で、優劣や順位を示しません。各候補について現在の予測成功人数を比べ、合計が最大の案を選んでください。本人の推奨は自分の区画の累積経験から答えます。
出力はlocalとproposalの二キーです。proposalのevidence_refsは両役の五経験IDすべてです。
'''
PROMPTS={'PROPOSE_DIRECT':PROPOSE_COMMON+'''proposalはallocationとevidence_refsです。選んだ候補の割付を、allocationのA/B固定キーにPAPERまたはDIGITALで書いてください。candidate_idは出力しません。判断できなければallocationはA/BともUNDECIDEDです。
''',
         'PROPOSE_SELECT':PROPOSE_COMMON+'''proposalはcandidate_idとevidence_refsです。選んだ候補のcandidate_idをXまたはYで書いてください。allocationは出力しません。判断できなければcandidate_idはUNDECIDEDです。実行器は候補IDに対応する割付をそのまま複製します。どの案が適切かの選び直しはしません。
''', 'CONFIRM':base.PROMPTS['CONFIRM'],'USE':base.PROMPTS['USE']}


def prompt_key(slot):
    return 'PROPOSE_'+slot['method'] if slot['stage']=='PROPOSE' else slot['stage']


def receive(raw,stage,finish='EOS',method='DIRECT'):
    if raw is None:
        return {'answer':None,'format_valid':None,'errors':['NO_RESPONSE'],'normalized_bytes':None,
                'normalization':{'status':'UNRESOLVED','reason':'NO_RESPONSE'}}
    norm=envelope.normalize(raw,finish); candidate=norm.pop('normalized_bytes')
    a=strict_json.parse(candidate) if candidate is not None else None
    key='PROPOSE_'+method if stage=='PROPOSE' else stage
    errors=shape(a,SCHEMAS[key]) if candidate is not None else [norm['reason']]
    return {'answer':a if not errors else None,'format_valid':not errors if finish=='EOS' else None,
            'errors':errors,'normalized_bytes':candidate,'normalization':norm}


def carried_answer(slot,answer,payload):
    """Bind a label to the supplied table; no arithmetic or correctness oracle."""
    if slot['stage']!='PROPOSE' or slot['method']=='DIRECT':
        return deepcopy(answer),{'status':'UNCHANGED','semantic_repair':False}
    table=payload['candidates']; cid=answer['proposal']['candidate_id']
    trace={'status':None,'candidate_id':cid,'candidate_table_sha256':digest(table),
           'raw_proposal_sha256':digest(answer['proposal']),'semantic_repair':False}
    if cid=='UNDECIDED':
        allocation={r:'UNDECIDED' for r in ROLES}
        trace.update(status='EXPLICIT_HOLD',source_pointer=None)
    else:
        found=[(i,c) for i,c in enumerate(table) if c['candidate_id']==cid]
        if len(found)!=1:
            trace.update(status='UNKNOWN_CANDIDATE_ID',source_pointer=None)
            return None,trace
        i,selected=found[0];allocation=deepcopy(selected['allocation'])
        trace.update(status='SELECTED_CANDIDATE_COPIED',source_pointer=f'/candidates/{i}/allocation',
                     selected_candidate=deepcopy(selected))
    carry={'local':deepcopy(answer['local']),
           'proposal':{'allocation':allocation,'evidence_refs':deepcopy(answer['proposal']['evidence_refs'])}}
    trace['carried_proposal_sha256']=digest(carry['proposal'])
    return carry,trace


def case_rows(source,branch):
    keys=list(base.ROW_KEYS[:5])+[m.lower()+'_success' for m in source['medium_display_order']]
    return [{k:row[k] for k in keys} for row in branch['model_source']['experiences']]


def record(slot,answer,field):
    return {'author':slot['role'],'body':json.loads(enc(answer[field])),
            'record_id':'Q'+digest(['FC02',slot['block'],slot['role'],field])[:10].upper()}


def payload_for(design,slot,states,source=None):
    source=json.loads(enc(source or next(r for r in design['roots'] if r['id']==slot['root'])))
    branch=next(b for b in design['branches'] if b['id']==slot['branch'])
    p={'holder':slot['role'],'experiences':case_rows(source,branch)}
    order=source['role_display_order'];slots={s['id']:s for s in design['allocation']}
    if slot['stage'] in ('PROPOSE','CONFIRM'):
        p['previous_private_judgments']=[source['previous_private_judgments'][r] for r in order]
        p['previous_joint_records']=source['previous_joint_records']
    if slot['stage']=='PROPOSE':
        p['candidates']=[{'candidate_id':c['candidate_id'],'allocation':{r:c['allocation'][r] for r in ROLES}}
                         for c in branch['candidates']]
    elif slot['stage']=='CONFIRM':
        parent=slots[slot['parents'][0]];answer=states[parent['id']]
        p['proposer_judgment']=record(parent,answer,'local');p['proposal']=record(parent,answer,'proposal')
    else:
        ps,cs=[slots[i] for i in slot['parents']];pa,ca=[states[s['id']] for s in (ps,cs)]
        owner_slot,owner_answer=(ps,pa) if slot['role']==ps['role'] else (cs,ca)
        p['own_judgment']=record(owner_slot,owner_answer,'local')
        records=[record(ps,pa,'proposal'),record(cs,ca,'reply')]
        p['joint_records']=[r for owner in order for r in records if r['author']==owner]
    return p


def request_for(design,slot,states,source=None):
    return {'id':slot['id'],'seed':slot['seed'],'messages':[
        {'role':'system','content':design['prompts'][prompt_key(slot)]},
        {'role':'user','content':'資料JSON:\n'+displayed(payload_for(design,slot,states,source))}]}


def score(raw,slot,payload,rows,finish='EOS'):
    # CONFIRM/USE semantics come from the unchanged, sealed EU01 implementation.
    if slot['stage']!='PROPOSE':
        r=base.score(raw,slot,payload,rows,finish)
        r.update(carried_answer=deepcopy(r['answer']),candidate_binding=None,
                 candidate_binding_valid=None,F=None,O=None,P=None)
        return r
    rec=receive(raw,slot['stage'],finish,slot['method']); a=rec['answer']
    r={k:v for k,v in rec.items() if k!='normalized_bytes'}
    keys=('L','Z','Z_local','Z_team','H','K','C','efficiency_optimal','reply_reference',
          'experience_references','action_contract','appropriate_response','F','O','P','candidate_binding_valid')
    r.update({k:None for k in keys});r.update(carried_answer=None,candidate_binding=None)
    if a is None:return r
    local,opts=expected_from_rows(rows);role=slot['role']
    own=[x['episode_id'] for x in rows if x['observer']==role];allrefs=[x['episode_id'] for x in rows]
    r['L']=a['local']['subject']==role and a['local']['choice']==local[role]
    r['Z_local']=a['local']['subject']==role and refs_ok(a['local']['evidence_refs'],own)
    r['experience_references']=refs_ok(a['proposal']['evidence_refs'],allrefs)
    r['Z_team']=r['experience_references'];r['Z']=r['Z_local'] and r['Z_team']
    carry,trace=carried_answer(slot,a,payload);r.update(carried_answer=carry,candidate_binding=trace)
    r['candidate_binding_valid']=carry is not None
    r['F']=carry is not None and legal(carry['proposal']['allocation'])
    r['O']=carry is not None and carry['proposal']['allocation'] in opts
    r['efficiency_optimal']=r['O'];r['P']=r['L'] and r['Z'] and r['O']
    return r


def build_design(proposal):
    roots=deepcopy(proposal['sources']);byroot={r['id']:r for r in roots}
    branches=deepcopy(proposal['branches']);bybranch={b['id']:b for b in branches}
    allocation=deepcopy(proposal['allocation']);runs=deepcopy(proposal['runs'])
    for s in allocation:
        r=byroot[s['root']]
        s.update(planned_stage=s['stage'],stage=s['stage'].split('-')[0],arm=s['experience_condition'],
                 block=r['block'],replicate=r['source_repeat'],case=r['case_id'],
                 function='TARGET' if s['role']==r['new_experience_recipient'] else 'PEER')
    for run in runs:
        r=byroot[run['root']];b=bybranch[run['branch']]
        run.update(arm=run['experience_condition'],replicate=r['source_repeat'],case=r['case_id'],
                   target=r['new_experience_recipient'],peer=r['peer'],baseline_K=r['baseline_not_for_model']['K'],
                   transition=b['expected_not_for_model']['transition'],
                   same_personal=b['expected_not_for_model']['same_personal_recommendations'],
                   strength=b['strength_not_for_model'],
                   target_yields=b['expected_not_for_model']['target_yields_own_preferred_medium'])
    return {'protocol':PROTOCOL,'proposal_sha256':PROPOSAL_SHA,'source_zip_sha256':SOURCE_ZIP_SHA,
            'roots':roots,'branches':branches,'runs':runs,'allocation':allocation,'prompts':PROMPTS,'schemas':SCHEMAS,
            'model':deepcopy(proposal['model']),'progress_gate':deepcopy(proposal['progress_gate']),
            'inherited_progress_gate':deepcopy(proposal['inherited_progress_gate']),
            'max_generations':256,'seconds_including_setup':5400}


def summarize(design,outcomes):
    require(not(set(outcomes)-{s['id'] for s in design['allocation']}),'UNEXPECTED_RESPONSE')
    get=lambda sid:outcomes.get(sid,{})
    paths=[];pairs=[];metrics={};progress={};inherited_progress={}
    for run in design['runs']:
        p=get(run['propose_id']);c=get(run['confirm_id']);uses=[get(i) for i in run['use_ids'].values()]
        j=all_known([p.get('L'),p.get('Z'),c.get('L'),c.get('Z'),c.get('C')]+[u.get(k) for u in uses for k in ('L','H','Z')])
        paths.append(dict(run,F=p.get('F'),O=p.get('O'),P=p.get('P'),K=c.get('K'),C=c.get('C'),J=j))
    pathkeys=('F','O','P','K','C','J');pairkeys=('Q','S_target','I_peer')
    stagekeys={'PROPOSE':('format_valid','candidate_binding_valid','F','O','P','L','Z','Z_local','Z_team'),
               'CONFIRM':('format_valid','L','Z','K','C','reply_reference','experience_references','action_contract','appropriate_response'),
               'USE':('format_valid','L','H','Z','Z_local','Z_team','efficiency_optimal')}
    for method in METHODS:
        selected=[p for p in paths if p['method']==method];pairrows=[]
        for root in design['roots']:
            ps=[next(p for p in selected if p['root']==root['id'] and p['arm']==arm) for arm in ARMS]
            own=all_known(get(i).get('L') for p in ps for i in (p['propose_id'],p['use_ids'][p['target']]))
            peer=all_known(get(i).get('L') for p in ps for i in (p['confirm_id'],p['use_ids'][p['peer']]))
            pairrows.append({'root':root['id'],'method':method,'replicate':root['source_repeat'],
                             'baseline_K':root['baseline_not_for_model']['K'],'strength':ps[0]['strength'],
                             'Q':all_known(p['J'] for p in ps),
                             'S_target':own,'I_peer':peer,'J_by_arm':{p['arm']:p['J'] for p in ps}})
        pairs.extend(pairrows)
        m={k:counts(p[k] for p in selected) for k in pathkeys}
        m.update({k:counts(p[k] for p in pairrows) for k in pairkeys})
        for field,values,label in [('same_personal',(True,False),'by_same_personal'),('arm',ARMS,'by_arm'),
                                    ('replicate',(1,2),'by_source_repeat'),('strength',('WEAK','STRONG'),'by_strength'),('transition',('CHANGE','KEEP','NO_PRIOR_AGREEMENT'),'by_transition')]:
            m[label]={str(v):{k:counts(p[k] for p in selected if p[field]==v) for k in pathkeys} for v in values}
        m['pair_by_source_repeat']={str(rep):{k:counts(p[k] for p in pairrows if p['replicate']==rep) for k in pairkeys} for rep in (1,2)}
        m['pair_by_strength']={v:{k:counts(p[k] for p in pairrows if p['strength']==v) for k in pairkeys} for v in ('WEAK','STRONG')}
        m['by_strength_preference_arm']=[{'strength':v,'same_personal':same,'arm':arm,
            'metrics':{k:counts(p[k] for p in selected if p['strength']==v and p['same_personal']==same and p['arm']==arm) for k in pathkeys}}
            for v in ('WEAK','STRONG') for same in (True,False) for arm in ARMS]
        m['pair_by_baseline_agreement']={str(v):{k:counts(p[k] for p in pairrows if p['baseline_K']==v) for k in pairkeys} for v in (True,False)}
        slots=[s for s in design['allocation'] if s['method']==method]
        m['stages']={stage:{k:counts(get(s['id']).get(k) for s in slots if s['stage']==stage) for k in keys} for stage,keys in stagekeys.items()}
        m['by_stage_and_function']={stage:{f:{k:counts(get(s['id']).get(k) for s in slots if s['stage']==stage and s['function']==f)
                                              for k in (('L','Z') if stage!='USE' else ('L','Z','H'))}
                                         for f in ('TARGET','PEER')} for stage in stagekeys}
        gate=design['progress_gate']
        tests={'Q_total':(m['Q'],gate['Q_min']),
               **{'Q_repeat_'+str(rep):(m['pair_by_source_repeat'][str(rep)]['Q'],gate['Q_each_source_repeat_min']) for rep in (1,2)},
               'S_target':(m['S_target'],gate['S_target']),'I_peer':(m['I_peer'],gate['I_peer'])}
        def assess(items):
            components={name:{'counts':c,'required':n,'status':('MET_IN_FIXED_SAMPLE' if c['correct']>=n else
                'NOT_MET' if c['correct']+c['unresolved']<n else 'INCONCLUSIVE')} for name,(c,n) in items.items()}
            statuses=[x['status'] for x in components.values()]
            return {'status':'NOT_MET' if 'NOT_MET' in statuses else 'INCONCLUSIVE' if 'INCONCLUSIVE' in statuses else 'MET_IN_FIXED_SAMPLE',
                    'components':components}
        inherited_progress[method]=assess(tests)
        tests.update({'Q_strength_'+v:(m['pair_by_strength'][v]['Q'],gate['Q_each_strength_min']) for v in ('WEAK','STRONG')})
        progress[method]=assess(tests);metrics[method]=m
    paired=[]
    for branch in design['branches']:
        d=next(p for p in paths if p['branch']==branch['id'] and p['method']=='DIRECT')
        s=next(p for p in paths if p['branch']==branch['id'] and p['method']=='SELECT')
        v=(d['P'],s['P'])
        category='UNRESOLVED' if None in v else {(True,True):'BOTH', (True,False):'DIRECT_ONLY',
                    (False,True):'SELECT_ONLY',(False,False):'NEITHER'}[v]
        paired.append({'branch':branch['id'],'root':d['root'],'arm':d['arm'],'same_personal':d['same_personal'],'strength':d['strength'],
                       'DIRECT_P':v[0],'SELECT_P':v[1],'category':category})
    d,s=metrics['DIRECT']['P'],metrics['SELECT']['P']
    comparison={'primary':'P','direction':'SELECT_MINUS_DIRECT','n_paired_conditions':32,
        'paired_categories':{k:sum(p['category']==k for p in paired) for k in ('BOTH','DIRECT_ONLY','SELECT_ONLY','NEITHER','UNRESOLVED')},
        'difference_missing_bounds':[(s['correct']-d['correct']-d['unresolved'])/32,
                                     (s['correct']+s['unresolved']-d['correct'])/32],
        'paired_conditions':paired,'not_a_confidence_interval':True}
    return {'kind':'FC02_NEW_EXPERIENCE_TRANSFER_ON_RETAINED_HISTORIES','planned_calls':256,'source_roots':16,
            'common_conditions':32,'method_paths':64,'source_repeats':2,'paths':paths,'pairs':pairs,'metrics':metrics,
            'comparison':comparison,'progression':{'criterion':'FC02_TRANSFER','status':progress['SELECT']['status'],'target_method':'SELECT','by_method':progress},
            'inherited_progression':{'criterion':'FC01_INHERITED','status':inherited_progress['SELECT']['status'],'target_method':'SELECT','by_method':inherited_progress},
            'inference':'New session-3 experiences on retained histories; no independent-N, p-values or population CI. Strength is not fully crossed within a stored history. Candidate visibility common to both methods.'}


def validate_source_template(branch, raw):
    """Verify only the preregistered session-3 fields replace the real old input."""
    binding=branch['source_template']
    require(sha256(raw).hexdigest()==binding['sha256'],'SOURCE_TEMPLATE_HASH')
    original=json.loads(json.loads(raw)['messages'][1]['content'].split('資料JSON:'+chr(10),1)[1])
    require(set(original)=={'holder','experiences','previous_private_judgments','previous_joint_records','candidates'},'SOURCE_TEMPLATE_KEYS')
    original.pop('candidates')
    current=branch['model_source']
    require(set(current)==set(original),'SOURCE_KEYS_CHANGED')
    require(len(original['experiences'])==len(current['experiences'])==5,'EXPERIENCE_COUNT')
    require(original['experiences'][:4]==current['experiences'][:4],'OLD_EXPERIENCES_CHANGED')
    require(all(original[k]==current[k] for k in original if k!='experiences'),'OLD_STATE_CHANGED')
    oldrow,newrow=original['experiences'][4],current['experiences'][4]
    allowed={'episode_id','paper_success','digital_success'}
    require(set(oldrow)==set(newrow) and all(oldrow[k]==newrow[k] for k in oldrow if k not in allowed),'NEW_EXPERIENCE_SHAPE_CHANGED')
    require(newrow['episode_id'] not in {x['episode_id'] for x in original['experiences']},'NEW_ID_NOT_NEW')
    require(newrow['session']==3 and newrow['attempts_per_medium']==40,'NEW_EXPERIENCE_SCOPE')
    require(all(type(newrow[k]) is int and 0<=newrow[k]<=40 for k in ('paper_success','digital_success')),'NEW_SUCCESS_COUNTS')
    require(binding['replacement_fields']==['experiences/4/episode_id','experiences/4/paper_success','experiences/4/digital_success'],'REPLACEMENT_CONTRACT')
    return current


def freeze():
    require(sha256(PROPOSAL.read_bytes()).hexdigest()==PROPOSAL_SHA,'PROPOSAL_CHANGED')
    require(sha256(SOURCE_ZIP.read_bytes()).hexdigest()==SOURCE_ZIP_SHA,'SOURCE_ZIP_CHANGED')
    design=json.loads(enc(build_design(json.loads(PROPOSAL.read_bytes()))))
    files={'design.json':enc(design)+b'\n','materials-proposal.json':PROPOSAL.read_bytes(),
           'initial-requests.json':enc([request_for(design,s,{}) for s in design['allocation'] if s['stage']=='PROPOSE'])+b'\n'}
    for key in SCHEMAS:
        files['schemas/'+key+'.json']=enc(SCHEMAS[key])+b'\n';files['prompts/'+key+'.txt']=PROMPTS[key].encode()
    for source in design['roots']:files['sources/'+source['id']+'.json']=enc(source)+b'\n'
    with zipfile.ZipFile(SOURCE_ZIP) as z:
        manifest=json.loads(z.read('FEEDBACK_MANIFEST.json'))['files_sha256']
        for branch in design['branches']:
            binding=branch['source_template'];raw=z.read(binding['member'])
            require(sha256(raw).hexdigest()==binding['sha256']==manifest[binding['member']],'SOURCE_INPUT_HASH')
            validate_source_template(branch,raw)
            files['original/'+binding['member']]=raw
        for stage in SCHEMAS:
            prompt=z.read('frozen/prompts/'+stage+'.txt');schema=z.read('frozen/schemas/'+stage+'.json')
            require(prompt==PROMPTS[stage].encode() and json.loads(schema)==SCHEMAS[stage],'FC01_PROMPT_SCHEMA_CHANGED')
            files['inherited/prompts/'+stage+'.txt']=prompt
            files['inherited/schemas/'+stage+'.json']=schema
        require(z.read('code/experience_update_01_design.py')==(ROOT/'scripts/experience_update_01_design.py').read_bytes(),'BASE_CODE_CHANGED')
    for name in ('feasible_choice_02_design.py','experience_update_01_design.py','readout_split_01_scoring.py','update_readout_01_envelope.py'):
        files[name]=(ROOT/'scripts'/name).read_bytes()
    files['MANIFEST.json']=enc({n:sha256(raw).hexdigest() for n,raw in files.items()})+b'\n'
    OUT.mkdir(parents=True,exist_ok=True)
    require(not any(OUT.iterdir()),'FREEZE_REQUIRES_EMPTY_DESTINATION')
    for name,raw in files.items():
        p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    print(json.dumps({'folder':str(OUT),'files':len(files),'calls':256,'design_sha256':sha256(files['design.json']).hexdigest()}))


if __name__=='__main__':freeze()
