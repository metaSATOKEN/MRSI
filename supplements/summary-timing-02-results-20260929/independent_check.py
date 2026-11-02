"""Post-run evidence check, stdlib only; no import of the experiment scorer."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'study2/results/summary-timing-02-20260929'
ZIP=OUT/'npp-st02-result-20260929-073815-2a1541bf.zip'
checks=[]
def ok(name,condition):
    assert condition,name
    checks.append(name)
def enc(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest(x):return sha256(x).hexdigest()
def write(path,obj):
    with path.open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def unique(pairs):
    out={}
    for k,v in pairs:
        assert k not in out,('duplicate key',k)
        out[k]=v
    return out
def decode(raw):return json.loads(raw,object_pairs_hook=unique)
def schema(v,s):
    if 'enum' in s:return v in s['enum'] and type(v) is str
    if s['type']=='object':return type(v) is dict and set(v)==set(s['properties']) and all(schema(v[k],t) for k,t in s['properties'].items())
    if s['type']=='array':return type(v) is list and len(v)<=s.get('maxItems',10**9) and all(schema(i,s['items']) for i in v)
    if s['type']=='string':return type(v) is str and len(v)<=s.get('maxLength',10**9)
    raise AssertionError(s)
def refs(a,b):return len(a)==len(b)==len(set(a)) and set(a)==set(b)
def legal(a):return set(a)=={'A','B'} and set(a.values())=={'PAPER','DIGITAL'}
def rates(rows):
    return {r:{m:Fraction(40*sum(x[m.lower()+'_success'] for x in rows if x['observer']==r),sum(x['attempts_per_medium'] for x in rows if x['observer']==r)) for m in ('PAPER','DIGITAL')} for r in ('A','B')}
def best(values):
    options=[{'A':'PAPER','B':'DIGITAL'},{'A':'DIGITAL','B':'PAPER'}]
    totals=[sum(values[r][a[r]] for r in ('A','B')) for a in options]
    return [a for a,t in zip(options,totals) if t==max(totals)]
def record(slot,answer,field):
    return {'record_id':'Q'+digest(enc(['CR01',slot['case'],slot['stage'],slot['role'],field]))[:10].upper(),'author':slot['role'],'body':answer[field]}
def counts(v):
    v=list(v);a=sum(x is True for x in v);u=sum(x is None for x in v)
    return {'n':len(v),'correct':a,'incorrect':sum(x is False for x in v),'unresolved':u,'fraction_missing_bounds':[a/len(v),(a+u)/len(v)] if v else [None,None]}
def agreement(records,rows):
    first,second=records[:2];reply=second['body'];pair=records[-2:]
    linked=second['author']!=first['author'] and reply['reply_to']==first['record_id']
    if len(records)==2:
        k=linked and reply['action']=='ACCEPT' and reply['allocation']==first['body']['allocation'] and legal(reply['allocation'])
    else:
        third=records[2];b=third['body']
        k=linked and reply['action']=='COUNTER' and third['author']==first['author'] and b['reply_to']==second['record_id'] and b['action']=='ACCEPT' and b['allocation']==reply['allocation'] and legal(reply['allocation'])
    g=k and pair[0]['body']['allocation'] in best(rates(rows)) and all(refs(x['body']['evidence_refs'],[r['episode_id'] for r in rows]) for x in pair)
    return k,g,pair

with ZipFile(ZIP) as z:
    names=z.namelist();ok('unique_names',len(names)==len(set(names)));files={n:z.read(n) for n in names}
manifest=decode(files['FEEDBACK_MANIFEST.json']);ok('archive_members',set(files)-{'FEEDBACK_MANIFEST.json'}==set(manifest['files_sha256']))
for n,h in manifest['files_sha256'].items():ok('hash:'+n,digest(files[n])==h)
get=lambda n:decode(files[n])
d=get('design.json');report=decode((OUT/'reaggregated.json').read_bytes())['report'];cases={c['id']:c for c in d['cases']}
paths={p['id']:p for p in d['paths']};diags={p['id']:p for p in d['diagnostics']};slots={s['id']:s for s in d['allocation']};initial={r['id']:r for r in get('requests.json')}
local=decode((ROOT/'throughline/audits/summary-timing-02-connection-20260929/payload.json').read_bytes())
ok('payload_bound',get('payload.json')==local)
for n,t in local['code'].items():ok('code:'+n,files['code/'+n]==t.encode()==(ROOT/'scripts'/n).read_bytes())
for n,t in local['frozen'].items():ok('frozen:'+n,files['frozen/'+n]==t.encode())
ok('response_set',{n.split('/')[1] for n in files if n.startswith('responses/')}==set(slots))
answers={};scores={};notes={};timestamps=[];carried=0;use_count=0;skip_count=0
for slot in d['allocation']:
    sid=slot['id'];stage=slot['stage'];arm=slot['condition_not_for_model'];case=cases[slot['case']];prefix='responses/'+sid+'/'
    result=get(prefix+'result.json');expected=result['score'];rows=case['experiences'];v=rates(rows);opts=best(v)
    physicalnames={n[len(prefix):] for n in files if n.startswith(prefix)}-{'result.json'}
    ok('result_files:'+sid,physicalnames==set(result['files_sha256']))
    for name,h in result['files_sha256'].items():ok('result_hash:'+sid+name,digest(files[prefix+name])==h)
    if result['status']=='SKIPPED_BY_PROTOCOL':
        skip_count+=1;ok('skip_stage:'+sid,stage=='RECHECK')
        path=paths[slot['route']];ok('skip_reason:'+sid,answers[path['confirm_id']]['reply']['action'] in ('ACCEPT','HOLD'))
        ok('skip_no_answer:'+sid,not {'input.json','started.json','response.json','answer.txt','carry-answer.json'}&physicalnames)
        ok('skip_unknown_score:'+sid,expected['V'] is None and expected['applicable'] is False)
        scores[sid]={'V':None,'L':None,'Z_local':None};continue
    request=get(prefix+'input.json');response=get(prefix+'response.json');a=decode(files[prefix+'answer.txt']);p=decode(request['messages'][1]['content'].split('\n',1)[1]);answers[sid]=a
    ps='RECHECK' if stage=='RECHECK_DIAGNOSTIC' else stage
    ok('schema:'+sid,schema(a,d['schemas'][ps]))
    ok('EOS:'+sid,result['status']=='EOS' and response['finish_reason']=='EOS' and response['output_token_ids'][-1]==248046)
    ok('real_answer:'+sid,not response.get('synthetic_fixture'))
    ok('response_hash:'+sid,response['payload_sha256']==digest(enc({k:v for k,v in response.items() if k!='payload_sha256'})))
    ok('raw:'+sid,response['answer_text'].encode()==files[prefix+'answer.txt'])
    ok('normalization:'+sid,get(prefix+'normalization.json')['status']=='UNCHANGED' and files[prefix+'normalized-answer.txt']==files[prefix+'answer.txt'])
    ok('saved_answer:'+sid,get(prefix+'saved-answer.json')==get(prefix+'carry-answer.json')==a==expected['answer'])
    ok('seed:'+sid,request['seed']==response['seed']==slot['seed'])
    ok('prompt:'+sid,request['messages'][0]=={'role':'system','content':d['prompts'][ps]})
    ok('limits:'+sid,len(request['prepared']['input_ids'])<=8192 and len(response['output_token_ids'])<=1024 and len(files[prefix+'answer.txt'])<=16384)
    started=get(prefix+'started.json');ok('start:'+sid,started['input_sha256']==digest(files[prefix+'input.json']) and started['seed']==slot['seed']);timestamps.append(started['started_at'])
    ok('holder:'+sid,p['holder']==slot['role'])
    ok('experiences:'+sid,p['experiences']==([r for r in rows if r['observer']==slot['role']] if stage=='FORM' else rows))
    for pid,binding in request['binding']['parents'].items():
        ok('same_condition_parent:'+sid+pid,slots[pid]['condition_not_for_model']==arm)
        par='responses/'+pid+'/';ok('parent_result:'+sid+pid,binding['result_sha256']==digest(files[par+'result.json']))
        ok('parent_carry:'+sid+pid,binding['carry_answer_sha256']==(digest(files[par+'carry-answer.json']) if par+'carry-answer.json' in files else None))
    trace=get(prefix+'carry-trace.json');ok('trace_payload:'+sid,trace['payload_sha256']==digest(enc(p)) and trace['semantic_repair'] is False)
    for item in trace['carried_fields']:
        value=p
        for key in item['target'].strip('/').split('/'):value=value[int(key)] if isinstance(value,list) else value[key]
        ok('trace_target:'+sid+item['target'],value==item['record'])
        if 'parent_id' in item:
            ok('parent_field:'+sid+item['target'],item['record']['body']==answers[item['parent_id']][item['extraction'][1:]]);carried+=1
    role=slot['role'];own=[x for x in rows if x['observer']==role]
    supplied=arm=='EARLY' or stage=='USE'
    ok('summary_presence:'+sid,('own_experience_summary' in p)==supplied)
    calc=get(prefix+'calculation-receipt.json')['own_summary']
    ok('summary_trace:'+sid,calc['supplied_to_model']==supplied and calc['own_rows_sha256']==digest(enc(own)) and calc['input_rows_sha256']==digest(enc(p['experiences'])))
    ok('summary_arithmetic:'+sid,calc['attempts']==sum(r['attempts_per_medium'] for r in own) and calc['success_counts']=={m:sum(r[m.lower()+'_success'] for r in own) for m in ('PAPER','DIGITAL')} and calc['per_40_fraction']=={m:[x.numerator,x.denominator] for m,x in v[role].items()})
    if supplied:
        summary={'observer':role,'experience_refs':[r['episode_id'] for r in own],'attempts_per_medium_total':sum(r['attempts_per_medium'] for r in own),'projected_success_per_40':{m:int(v[role][m]) for m in case['medium_order']}}
        ok('summary_value_and_order:'+sid,p['own_experience_summary']==summary and list(p)[-1]=='own_experience_summary' and list(p['own_experience_summary']['projected_success_per_40'])==case['medium_order'])
        ok('summary_hash:'+sid,calc['summary_sha256']==digest(enc(summary)))
    ok('trace_condition:'+sid,trace['condition']==request['binding']['condition']==arm)
    independent={'L':a['local']['subject']==role and a['local']['choice']==max(v[role],key=v[role].get),
                 'Z_local':a['local']['subject']==role and refs(a['local']['evidence_refs'],[x['episode_id'] for x in own])}
    if stage=='FORM':
        ok('frozen_FORM:'+sid,all(request[k]==value for k,value in initial[sid].items()))
        ok('FORM_keys:'+sid,set(p)==({'holder','experiences','own_experience_summary'} if arm=='EARLY' else {'holder','experiences'}))
        independent['V']=all(independent.values())
    elif stage in ('CONFIRM','RECHECK','RECHECK_DIAGNOSTIC'):
        source=diags[slot['diagnostic']] if 'diagnostic' in slot else paths[slot['route']]
        ok('initial_proposal:'+sid,p['initial_proposal']==source['initial_proposal'])
        fid=f'ST02-{arm}-{case["id"]}-FORM-{role}';ok('own_FORM_carry:'+sid,p['own_judgment']==record(slots[fid],answers[fid],'local'))
        ok('joint_table:'+sid,p['joint_candidate_totals']==case['joint_candidate_totals'])
        ok('input_keys:'+sid,set(p)==({'holder','experiences','own_judgment','initial_proposal','joint_candidate_totals'}|({'counter_record'} if stage!='CONFIRM' else set())|({'own_experience_summary'} if arm=='EARLY' else set())))
        for cand in p['joint_candidate_totals']:ok('candidate_sum:'+sid+cand['candidate_id'],sum(v[r][cand['allocation'][r]] for r in ('A','B'))==cand['projected_total_success_per_40_each'])
        b=a['reply'];proposal=p['initial_proposal']
        if stage=='CONFIRM':
            valid=proposal['body']['allocation'] in opts
            act=(b['action']=='ACCEPT' and b['allocation']==proposal['body']['allocation']) if valid else ((b['action']=='COUNTER' and b['allocation'] in opts and b['allocation']!=proposal['body']['allocation']) or (b['action']=='HOLD' and b['allocation']=={'A':'UNDECIDED','B':'UNDECIDED'}))
            replyid=proposal['record_id']
        else:
            counter=p['counter_record'];cb=counter['body']
            if stage=='RECHECK':ok('actual_counter:'+sid,counter==record(slots[source['confirm_id']],answers[source['confirm_id']],'reply'))
            else:ok('controlled_counter:'+sid,counter==source['counter_record'])
            valid=(counter['author']!=proposal['author'] and cb['action']=='COUNTER' and cb['reply_to']==proposal['record_id'] and refs(cb['evidence_refs'],[x['episode_id'] for x in rows]) and cb['allocation'] in opts)
            independent['counter_valid']=valid
            act=b['action']==('ACCEPT' if valid else 'HOLD') and b['allocation']==(cb['allocation'] if valid else {'A':'UNDECIDED','B':'UNDECIDED'});replyid=counter['record_id']
        independent.update(action_contract=act,reply_reference=b['reply_to']==replyid,experience_references=refs(b['evidence_refs'],[x['episode_id'] for x in rows]),efficiency_optimal=b['allocation'] in opts)
        independent['Z_team']=independent['reply_reference'] and independent['experience_references']
        independent['appropriate_response']=act and independent['Z_team']
        independent['V']=independent['L'] and independent['Z_local'] and independent['appropriate_response']
    else:
        use_count+=1;path=paths[slot['route']];confid=path['confirm_id'];rcid=path['recheck_id']
        records=[path['initial_proposal'],record(slots[confid],answers[confid],'reply')]
        rc=answers[confid]['reply']['action']=='COUNTER'
        if rc:records.append(record(slots[rcid],answers[rcid],'reply'))
        ok('actual_joint_records:'+sid,p['joint_records']==records)
        owner=confid if role==case['peer'] else rcid if rc else f'ST02-{arm}-{case["id"]}-FORM-{role}'
        ok('actual_latest_local:'+sid,p['own_judgment']==record(slots[owner],answers[owner],'local'))
        ok('USE_keys:'+sid,set(p)=={'holder','experiences','own_judgment','joint_records','own_experience_summary'})
        ok('own_summary:'+sid,p['own_experience_summary']=={'observer':role,'experience_refs':[x['episode_id'] for x in own],'attempts_per_medium_total':sum(x['attempts_per_medium'] for x in own),'projected_success_per_40':{m:int(t) for m,t in v[role].items()}})
        k,g,pair=agreement(records,rows);allocation=pair[0]['body']['allocation'] if k else {'A':'UNDECIDED','B':'UNDECIDED'};basis='SHARED_DECISION' if k else 'UNRESOLVED'
        independent.update(H=a['team']['allocation']==allocation and a['team']['basis']==basis,Z_team=a['team']['basis']==basis and refs(a['team']['evidence_refs'],[r['record_id'] for r in pair]),efficiency_optimal=a['team']['allocation'] in opts)
        independent['V']=independent['L'] and independent['Z_local'] and independent['H'] and independent['Z_team']
    for key,value in independent.items():ok('score:'+sid+key,expected[key] is value)
    scores[sid]=independent;notes[sid]={'id':sid,'stage':stage,'case':case['id'],'condition':arm,'role':role,'input_payload':p,'raw_answer':response['answer_text'],'answer':a,'projected_per_40':{r:{m:str(t) for m,t in vals.items()} for r,vals in v.items()},'optimal_allocations':opts,'components':independent}
ok('generation_order',timestamps==sorted(timestamps))
pathrows=[]
for path in d['paths']:
    conf=answers[path['confirm_id']];need=conf['reply']['action']=='COUNTER';records=[path['initial_proposal'],record(slots[path['confirm_id']],conf,'reply')]
    required=path['form_ids']+[path['confirm_id']]+list(path['use_ids'].values())
    last=path['confirm_id']
    if need:
        required.append(path['recheck_id']);last=path['recheck_id'];records.append(record(slots[last],answers[last],'reply'))
    k,g,pair=agreement(records,cases[path['case']]['experiences'])
    category='CORRECT_AGREEMENT' if g else 'WRONG_AGREEMENT' if k else ('APPROPRIATE_HOLD' if scores[last]['appropriate_response'] else 'UNNECESSARY_HOLD') if answers[last]['reply']['action']=='HOLD' else 'OTHER_NONAGREEMENT'
    row={'condition':path['condition_not_for_model'],'id':path['id'],'case':path['case'],'initial_type':path['initial_type_not_for_model'],'J':all(scores[x]['V'] for x in required),'I':all(scores[x]['L'] and scores[x]['Z_local'] for x in required),'K':k,'G':g,'wrong_agreement':k and not g,'category':category}
    stated=next(x for x in report['paths'] if x['id']==path['id'])
    for key in ('J','I','K','G','wrong_agreement','category'):ok('path:'+path['id']+key,row[key]==stated[key])
    pathrows.append(row)
for arm in ('LATE','EARLY'):
    arm_report=report['by_condition'][arm];arm_paths=[x for x in pathrows if x['condition']==arm]
    for key in arm_report['metrics']:ok('metric:'+arm+key,counts(x[key] for x in arm_paths)==arm_report['metrics'][key])
    for typ in ('OPTIMAL','LOWER','DUPLICATE'):
        selected=[x for x in arm_paths if x['initial_type']==typ]
        for key in arm_report['metrics']:ok('by_type:'+arm+typ+key,counts(x[key] for x in selected)==arm_report['by_initial_type'][typ][key])
    ok('terminal_categories:'+arm,dict(Counter(x['category'] for x in arm_paths))==arm_report['terminal_categories'])
    diagrows=[]
    for dg in d['diagnostics']:
        if dg['condition_not_for_model']!=arm:continue
        sid=dg['id']+'-RECHECK';diagrows.append({'id':dg['id'],'D':scores[sid]['V'],'counter_type':dg['counter_type_not_for_model']})
    ok('diag_counts:'+arm,counts(x['D'] for x in diagrows)==arm_report['diagnostic_metrics']['D'])
    for typ in ('OPTIMAL','LOWER','DUPLICATE'):ok('diag_type:'+arm+typ,counts(x['D'] for x in diagrows if x['counter_type']==typ)==arm_report['diagnostic_metrics']['by_counter_type'][typ])
    main_ok=(sum(x['J'] for x in arm_paths)>=22 and all(x['I'] for x in arm_paths) and not any(x['wrong_agreement'] for x in arm_paths) and all(sum(x['J'] for x in arm_paths if x['initial_type']==t)>=7 for t in ('OPTIMAL','LOWER','DUPLICATE')) and all(sum(x['G'] for x in arm_paths if x['initial_type']==t)>=threshold for t,threshold in [('OPTIMAL',7),('LOWER',6),('DUPLICATE',6)]))
    ok('main_gate:'+arm,arm_report['main_progression']['status']==('MET_IN_FIXED_SAMPLE' if main_ok else 'NOT_MET'))
    diag_ok=all(x['D'] for x in diagrows)
    ok('diag_gate:'+arm,arm_report['diagnostic_progression']['status']==('MET_IN_FIXED_SAMPLE' if diag_ok else 'NOT_MET'))
    ok('total_gate:'+arm,arm_report['progression']['status']==('MET_IN_FIXED_SAMPLE' if main_ok and diag_ok else 'NOT_MET'))
    for stage,data in arm_report['stages'].items():
        selected=[s for s in d['allocation'] if s['condition_not_for_model']==arm and s['stage']==stage]
        active=[s for s in selected if s['id'] in answers]
        ok('stage_count:'+arm+stage,len(selected)==data['planned'] and len(selected)-len(active)==data['skipped_by_protocol'])
        for key,value in data['metrics'].items():
            ok('stage_metric:'+arm+stage+key,counts(True if key=='format_valid' else scores[s['id']].get(key) for s in active)==value)
    for quality in (True,False,None):
        subset=[p['recheck_id'] for p in d['paths'] if p['condition_not_for_model']==arm and answers[p['confirm_id']]['reply']['action']=='COUNTER' and scores[p['recheck_id']].get('counter_valid') is quality]
        saved=arm_report['natural_recheck_by_input_quality'][str(quality)]
        ok('natural_quality:'+arm+str(quality),saved['V']==counts(scores[s]['V'] for s in subset) and saved['status']==('OBSERVED' if subset else 'NOT_EXERCISED'))
for t in report['saved_to_use']:
    path=paths[t['route']];role=t['role'];case=cases[path['case']];arm=path['condition_not_for_model']
    rc=answers[path['confirm_id']]['reply']['action']=='COUNTER'
    sid=path['confirm_id'] if role==case['peer'] else path['recheck_id'] if rc else f'ST02-{arm}-{case["id"]}-FORM-{role}'
    b,a=scores[sid],scores[path['use_ids'][role]]
    category=('TRUE_' if b['L'] else 'FALSE_')+('TRUE' if a['L'] else 'FALSE')
    ok('transition:'+path['id']+role,t['saved_response_id']==sid and t['transition']==category and t['saved_L']==b['L'] and t['use_L']==a['L'] and t['saved_Z_local']==b['Z_local'] and t['use_Z_local']==a['Z_local'])
# Independent paired counts and bounds. Fixed denominator includes unknown cells.
def pair_check(label,pairs,stated):
    pairs=list(pairs);n=len(pairs);cat=Counter()
    low=high=0
    for early,late in pairs:
        if early is None or late is None:cat['unresolved']+=1
        else:cat[('both_pass' if early and late else 'both_fail' if not early and not late else 'EARLY_only' if early else 'LATE_only')]+=1
        low+=(0 if early is None else early)-(1 if late is None else late)
        high+=(1 if early is None else early)-(0 if late is None else late)
    direction='IMPROVEMENT_IN_FIXED_SAMPLE' if low>0 else 'DETERIORATION_IN_FIXED_SAMPLE' if high<0 else 'TIE_IN_FIXED_SAMPLE' if low==high==0 else 'UNRESOLVED_DIRECTION'
    ok('pair_n:'+label,stated['n']==n)
    ok('pair_categories:'+label,stated['categories']=={k:cat[k] for k in ('both_pass','EARLY_only','LATE_only','both_fail','unresolved')})
    ok('pair_bounds:'+label,stated['difference_count_bounds']==[low,high] and stated['difference_rate_bounds']==[low/n,high/n] and stated['difference_percentage_point_bounds']==[100*low/n,100*high/n])
    ok('pair_marginals:'+label,stated['EARLY']==counts(e for e,l in pairs) and stated['LATE']==counts(l for e,l in pairs))
    ok('pair_direction:'+label,stated['direction']==direction)
pathindex={x['id']:x for x in pathrows}
for key,stated in report['paired']['path_metrics'].items():
    pair_check('paths-'+key,((pathindex[p['paths']['EARLY']][key],pathindex[p['paths']['LATE']][key]) for p in d['paired_paths']),stated)
pair_check('primary',((pathindex[p['paths']['EARLY']]['I'],pathindex[p['paths']['LATE']]['I']) for p in d['paired_paths']),report['primary'])
for field,groups in report['paired']['by_stratum'].items():
    for value,metrics in groups.items():
        def metadata(p):return p[field] if field in ('case','initial_type') else cases[p['case']][field]
        selected=[p for p in d['paired_paths'] if str(metadata(p))==value]
        for key,stated in metrics.items():pair_check('stratum-'+field+value+key,((pathindex[p['paths']['EARLY']][key],pathindex[p['paths']['LATE']][key]) for p in selected),stated)
for family in ('FORM','USE','diagnostic'):
    section=report['paired'][family]
    expected_pairs=({(c['id']+'-'+role):{a:f'ST02-{a}-{c["id"]}-FORM-{role}' for a in ('LATE','EARLY')} for c in d['cases'] for role in ('A','B')} if family=='FORM' else
        {p['id']+'-'+role:{a:paths[rid]['use_ids'][role] for a,rid in p['paths'].items()} for p in d['paired_paths'] for role in ('A','B')} if family=='USE' else
        {p['id']:{a:rid+'-RECHECK' for a,rid in p['diagnostics'].items()} for p in d['paired_diagnostics']})
    ok('pair_set:'+family,{p['id']:p['response_ids'] for p in section['pairs']}==expected_pairs)
    for key,stated in section['metrics'].items():
        k='V' if key=='D' else key
        pair_check(family+'-'+key,((scores[x['EARLY']][k],scores[x['LATE']][k]) for x in expected_pairs.values()),stated)
normal=sorted([p['id'] for p in d['paired_paths'] if all(pathindex[x]['J'] for x in p['paths'].values())],key=lambda x:digest(('ST02-review|2026092904|'+x).encode()))[:6]
discord=[p['id'] for p in d['paired_paths'] if any(pathindex[p['paths']['EARLY']][k]!=pathindex[p['paths']['LATE']][k] for k in ('I','J'))]
failed=[s['id'] for s in d['allocation'] if s['id'] in answers and not scores[s['id']]['V']]
ok('specified_review',failed==report['reason_review']['nonpassing_or_unknown_responses'] and normal==report['reason_review']['normal_pairs'] and discord==report['reason_review']['discordant_I_or_J_pairs'])
selected=set(failed)|{x['id']+'-RECHECK' for x in d['diagnostics']}
review_paths={x['id'] for x in pathrows if x['wrong_agreement']}
for p in d['paired_paths']:
    if p['id'] in normal+discord:review_paths.update(p['paths'].values())
for s in d['allocation']:
    if s.get('route') in review_paths:selected.add(s['id'])
pending=list(selected)
while pending:
    for pid in slots[pending.pop()]['parents']:
        if pid not in selected:selected.add(pid);pending.append(pid)
ok('review_ancestor_closure',sorted(selected)==report['reason_review']['all_responses_and_ancestors'])
for n in files:
    if n.startswith('report-'):ok('stored_report:'+n,get(n)==report)
end=get('run-end.json');ok('budget',len(answers)==report['attempted_generations']<=248 and len(answers)+skip_count==248 and end['elapsed_seconds']<2700)
ok('revision',get('tokenizer-binding.json')['revision']==d['model']['revision'])
ok('dtype',set(get('loaded-parameters.json')['parameter_dtype_counts'])=={'torch.bfloat16'})
for k,v in d['model']['generation'].items():ok('generation:'+k,get('generation-config.json')[k]==v)
specified=[s['id'] for s in d['allocation'] if s['id'] in selected and s['id'] in notes]
write(HERE/'review-materials.json',{'selection':d['review_rule'],'specified_ids':specified,'specified':[notes[x] for x in specified],'skipped_selected':sorted(x for x in selected if x not in notes)})
write(OUT/'diagnostics.json',{'elapsed_seconds':end['elapsed_seconds'],'environment':get('environment.json'),'normalization':report['normalization'],'stage_components':{a:r['stages'] for a,r in report['by_condition'].items()},'paths':pathrows,'nonpassing':[notes[x] for x in failed],'diagnostics':[notes[x['id']+'-RECHECK'] for x in d['diagnostics']],
 'saved_to_use':report['saved_to_use'],'performance':{stage:{k:({'min':min(v),'max':max(v),'sum':sum(v)} if v else None) if isinstance(v,list) else v for k,v in row.items()} for stage,row in report['performance'].items()}})
write(HERE/'independent-check.json',{'status':'PASS','checks':len(checks),'items':checks,'archive_files':len(manifest['files_sha256']),'responses':len(answers),'skipped_rechecks':skip_count,'actual_parent_extractions':carried,'use_inputs':use_count,'selected_review_responses':len(specified),'summary_inputs_checked':len(answers),'real_model_calls':0,'method':'Separate stdlib implementation; same investigator, not independent human or blind model replication.'})
print(json.dumps({'status':'PASS','checks':len(checks),'responses':len(answers),'skipped_rechecks':skip_count,'actual_parent_extractions':carried,'use_inputs':use_count,'selected_review_responses':len(specified)},ensure_ascii=False))
