"""Post-run evidence check, stdlib only; no import of the experiment scorer."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'study2/results/confirm-support-01-20260929'
ZIP=OUT/'npp-cs01-result-20260929-041214-53d27bd7.zip'
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
def agreed(p,c):
    b=c['body']
    return p['author']!=c['author'] and b['reply_to']==p['record_id'] and b['action']=='ACCEPT' and b['allocation']==p['body']['allocation'] and legal(b['allocation'])

with ZipFile(ZIP) as z:
    names=z.namelist();ok('unique_archive_names',len(names)==len(set(names)))
    files={n:z.read(n) for n in names}
manifest=decode(files['FEEDBACK_MANIFEST.json'])
ok('archive_members',set(files)-{'FEEDBACK_MANIFEST.json'}==set(manifest['files_sha256']))
for n,h in manifest['files_sha256'].items():ok('hash:'+n,digest(files[n])==h)
get=lambda n:decode(files[n])
d=get('design.json');report=decode((OUT/'reaggregated.json').read_bytes())['report']
packets={p['id']:p for p in d['packets']};initial={x['id']:x for x in get('requests.json')}
contract=get('contract.json');local_payload=decode((ROOT/'throughline/audits/confirm-support-01-connection-20260929/payload.json').read_bytes())
ok('payload_binding',get('payload.json')==local_payload)
for n,source in local_payload['code'].items():ok('code:'+n,files['code/'+n]==source.encode()==(ROOT/'scripts'/n).read_bytes())
for n,source in local_payload['frozen'].items():ok('frozen:'+n,files['frozen/'+n]==source.encode())
with ZipFile(ROOT/d['source_archive']) as z:
    ok('source_archive',digest((ROOT/d['source_archive']).read_bytes())==d['source_archive_sha256'])
    for n,h in d['source_bindings'].items():ok('source_binding:'+n,digest(z.read(n))==h)
    for p in d['packets']:
        if p['kind']=='MAIN':
            source=decode(z.read(p['source_confirm_input']))
            ok('original_BASE:'+p['id'],initial[p['id']+'-BASE-CONFIRM']['messages'][1]['content']==source['messages'][1]['content'])
ok('response_set',{n.split('/')[1] for n in files if n.startswith('responses/')}=={s['id'] for s in d['allocation']})
slotmap={s['id']:s for s in d['allocation']};answers={};scores={};notes={};timestamps=[]
for slot in d['allocation']:
    sid=slot['id'];p=packets[slot['packet']];prefix='responses/'+sid+'/'
    request=get(prefix+'input.json');response=get(prefix+'response.json');saved=get(prefix+'result.json');score=saved['score']
    answer=decode(files[prefix+'answer.txt']);payload=decode(request['messages'][1]['content'].split('\n',1)[1]);rows=payload['experiences'];values=rates(rows);opts=best(values)
    answers[sid]=answer
    ok('raw_response:'+sid,response['answer_text'].encode()==files[prefix+'answer.txt'])
    ok('response_hash:'+sid,response['payload_sha256']==digest(enc({k:v for k,v in response.items() if k!='payload_sha256'})))
    ok('schema:'+sid,schema(answer,d['schemas'][slot['stage']]))
    ok('EOS:'+sid,response['finish_reason']=='EOS' and response['output_token_ids'][-1]==248046 and saved['status']=='EOS')
    ok('actual_not_synthetic:'+sid,not response.get('synthetic_fixture'))
    ok('seed:'+sid,response['seed']==request['seed']==slot['seed'])
    ok('prompt:'+sid,request['messages'][0]['content']==d['prompts'][slot['stage']])
    ok('limits:'+sid,len(request['prepared']['input_ids'])<=8192 and len(response['output_token_ids'])<=1024 and len(files[prefix+'answer.txt'])<=16384)
    ok('saved_raw_exact:'+sid,get(prefix+'saved-answer.json')==get(prefix+'carry-answer.json')==answer==score['answer'])
    ok('normalization:'+sid,get(prefix+'normalization.json')['status']=='UNCHANGED' and files[prefix+'normalized-answer.txt']==files[prefix+'answer.txt'])
    started=get(prefix+'started.json');ok('input_binding:'+sid,started['input_sha256']==digest(files[prefix+'input.json']));timestamps.append(started['started_at'])
    own=[r for r in rows if r['observer']==slot['role']];local_best=max(values[slot['role']],key=values[slot['role']].get)
    independent={'L':answer['local']['subject']==slot['role'] and answer['local']['choice']==local_best,
                 'Z_local':refs(answer['local']['evidence_refs'],[r['episode_id'] for r in own])}
    if slot['stage']=='CONFIRM':
        ok('frozen_request:'+sid,all(request[k]==v for k,v in initial[sid].items()))
        ok('confirm_payload:'+sid,payload==p['payloads'][slot['method']])
        for candidate in p['payloads']['SUPPORT']['joint_candidate_totals']:
            total=sum(values[r][candidate['allocation'][r]] for r in ('A','B'))
            ok('candidate_value:'+sid+candidate['candidate_id'],total==candidate['projected_total_success_per_40_each'])
        ok('paired_only_support:'+sid,{k:v for k,v in p['payloads']['SUPPORT'].items() if k!='joint_candidate_totals'}==p['payloads']['BASE'])
        reply=answer['reply'];allocation=reply['allocation'];proposal=payload['proposal']
        optimal_input=proposal['body']['allocation'] in opts
        action_ok=(reply['action']=='ACCEPT' and allocation==proposal['body']['allocation']) if optimal_input else ((reply['action']=='COUNTER' and allocation in opts and allocation!=proposal['body']['allocation']) or (reply['action']=='HOLD' and allocation=={'A':'UNDECIDED','B':'UNDECIDED'}))
        independent.update(K=agreed(proposal,{'author':slot['role'],'body':reply}),
            action_contract=action_ok,reply_reference=reply['reply_to']==proposal['record_id'],
            experience_references=refs(reply['evidence_refs'],[x['episode_id'] for x in rows]),efficiency_optimal=allocation in opts)
        independent['C']=independent['K'] and independent['efficiency_optimal']
        independent['Z_team']=independent['reply_reference'] and independent['experience_references']
        independent['appropriate_response']=action_ok and independent['Z_team']
        independent['V']=independent['L'] and independent['Z_local'] and independent['appropriate_response']
        if p['kind']=='MAIN':
            ok('main_proposal_optimal:'+sid,optimal_input)
            proposer=payload['proposer_judgment']['body'];target=p['target']
            ok('saved_proposer_correct:'+sid,proposer['subject']==target and proposer['choice']==max(values[target],key=values[target].get) and refs(proposer['evidence_refs'],[r['episode_id'] for r in rows if r['observer']==target]))
    else:
        pid=slot['parents'][0];parent=answers[pid];parent_slot=slotmap[pid]
        records={k:{'author':parent_slot['role'],'body':parent[k], 'record_id':'Q'+digest(enc(['CS01',slot['packet'],parent_slot['role'],k]))[:10].upper()} for k in ('local','reply')}
        expected_joint=[rec for role in p['role_order'] for rec in (p['payloads']['BASE']['proposal'],records['reply']) if rec['author']==role]
        ok('carry_reply:'+sid,payload['joint_records']==expected_joint)
        expected_own=p['payloads']['BASE']['proposer_judgment'] if slot['role']==p['target'] else records['local']
        ok('carry_local:'+sid,payload['own_judgment']==expected_own)
        ok('input_boundary:'+sid,set(payload)=={'holder','experiences','own_judgment','joint_records','own_experience_summary'})
        ok('experiences:'+sid,rows==p['payloads']['BASE']['experiences'])
        summary=payload['own_experience_summary'];ok('own_summary:'+sid,summary=={'observer':slot['role'],'experience_refs':[r['episode_id'] for r in own],'attempts_per_medium_total':sum(r['attempts_per_medium'] for r in own),'projected_success_per_40':{k:int(v) for k,v in values[slot['role']].items()}})
        binding=request['binding']['parents'][pid]
        ok('parent_binding:'+sid,binding['carry_answer_sha256']==digest(files['responses/'+pid+'/carry-answer.json']) and binding['result_sha256']==digest(files['responses/'+pid+'/result.json']))
        proposal=next(rec for rec in expected_joint if 'action' not in rec['body']);confirmation=next(rec for rec in expected_joint if 'action' in rec['body'])
        k=agreed(proposal,confirmation);expected_allocation=proposal['body']['allocation'] if k else {'A':'UNDECIDED','B':'UNDECIDED'};basis='SHARED_DECISION' if k else 'UNRESOLVED'
        independent.update(H=answer['team']['allocation']==expected_allocation and answer['team']['basis']==basis,
            Z_team=answer['team']['basis']==basis and refs(answer['team']['evidence_refs'],[rec['record_id'] for rec in expected_joint]),
            efficiency_optimal=answer['team']['allocation'] in opts)
    independent['Z']=independent['Z_local'] and independent['Z_team']
    for key,value in independent.items():ok('score:'+sid+':'+key,score[key] is value)
    scores[sid]=independent
    notes[sid]={'id':sid,'stage':slot['stage'],'kind':p['kind'],'input_payload':payload,'raw_answer':response['answer_text'],'answer':answer,
                'projected_per_40':{r:{m:str(v) for m,v in vs.items()} for r,vs in values.items()},'optimal_allocations':opts,'independent_components':independent}
ok('generation_order',timestamps==sorted(timestamps))
path_rows=[]
for p in d['packets']:
    if p['kind']!='MAIN':continue
    for method in ('BASE','SUPPORT'):
        route=p['id']+'-'+method;c=scores[route+'-CONFIRM'];uses={r:scores[route+'-USE-'+r] for r in ('A','B')}
        row={'id':route,'packet':p['id'],'root':p['root'],'method':method,'V':c['V'],'J':all([c['V'],c['C']]+[u[k] for u in uses.values() for k in ('L','H','Z')]),'U_target':uses[p['target']]['L'] and uses[p['target']]['Z_local'],'U_peer':uses[p['peer']]['L'] and uses[p['peer']]['Z_local']}
        expected=next(x for x in report['paths'] if x['id']==route)
        for key in ('V','J','U_target','U_peer'):ok('path:'+route+':'+key,row[key]==expected[key])
        path_rows.append(row)
for metric in ('V','J','U_target','U_peer'):
    categories=Counter()
    for p in d['packets']:
        if p['kind']!='MAIN':continue
        pair=tuple(next(x[metric] for x in path_rows if x['packet']==p['id'] and x['method']==m) for m in ('BASE','SUPPORT'))
        categories[{(True,True):'BOTH',(False,True):'SUPPORT_ONLY',(True,False):'BASE_ONLY',(False,False):'NEITHER'}[pair]]+=1
    ok('paired:'+metric,dict(categories)==report['paired'][metric]['categories'])
for row in report['pairs']:
    expected=all(x['J'] for x in path_rows if x['root']==row['root'] and x['method']==row['method'])
    ok('Q:'+row['root']+row['method'],expected==row['Q'])
normal=sorted([r['id'] for r in path_rows if r['J']],key=lambda rid:digest(('CS01-review|2026092901|'+rid).encode()))[:8]
failed=[s['id'] for s in d['allocation'] if not (scores[s['id']]['V'] if s['stage']=='CONFIRM' else all(scores[s['id']][k] for k in ('L','H','Z')))]
ok('review_selection',normal==report['reason_review']['normal_paths'] and failed==report['reason_review']['nonpassing_or_unknown_responses'])
for n in files:
    if n.startswith('report-'):ok('saved_report:'+n,get(n)==report)
end=get('run-end.json');ok('budget',len(answers)==report['attempted_generations']==208 and end['elapsed_seconds']<3600)
ok('model_revision',get('tokenizer-binding.json')['revision']==d['model']['revision'])
ok('dtype',set(get('loaded-parameters.json')['parameter_dtype_counts'])=={'torch.bfloat16'})
for k,v in d['model']['generation'].items():ok('generation_config:'+k,get('generation-config.json')[k]==v)
specified=failed+[route+suffix for route in normal for suffix in ('-CONFIRM','-USE-A','-USE-B')]
write(HERE/'review-materials.json',{'selection':'12 nonpassing answers plus 8 preselected normal paths; primary investigator unblinded review','specified_ids':specified,'specified':[notes[s] for s in specified], 'controls':[notes[s['id']] for s in d['allocation'] if packets[s['packet']]['kind']=='CONTROL'], 'main_failure_followup':[notes[x['id']+'-USE-'+role] for x in path_rows if not x['J'] for role in ('A','B')]})
diagnostics={'elapsed_seconds':end['elapsed_seconds'],'environment':get('environment.json'),'normalization':report['normalization'],'performance':{},
    'main_failures':[notes[s] for s in failed if notes[s]['kind']=='MAIN'],'controls':[notes[s['id']] for s in d['allocation'] if packets[s['packet']]['kind']=='CONTROL'],
    'old_failure_followup':{packet:{m:next(x['V'] for x in path_rows if x['packet']==packet and x['method']==m) for m in ('BASE','SUPPORT')} for packet in ['CS01-M11-REVERSE','CS01-M12-REINFORCE','CS01-M14-REVERSE']}}
for stage,p in report['performance'].items():diagnostics['performance'][stage]={k:{'min':min(v),'max':max(v),'sum':sum(v)} if isinstance(v,list) else v for k,v in p.items()}
write(OUT/'diagnostics.json',diagnostics)
write(HERE/'independent-check.json',{'status':'PASS','checks':len(checks),'items':checks,'archive_files':len(manifest['files_sha256']),'real_model_calls':0,'method':'Separate stdlib implementation, all 208 raw responses; this is not independent human or blind model replication.'})
print(json.dumps({'status':'PASS','checks':len(checks),'archive_files':len(manifest['files_sha256']),'responses':len(answers),'carry_inputs':128,'review_responses':len(specified)},ensure_ascii=False))
