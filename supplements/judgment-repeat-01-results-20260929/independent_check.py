"""JR01 offline audit with stdlib-only scoring; no imports of the study scorer/runtime."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import stat
from zipfile import ZipFile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'study2/results/judgment-repeat-01-20260929'
SOURCE=ROOT/'npp-jr01-result-20260929-092936-6e2d67ef.zip'
FIXED=ROOT/'study2/designs/judgment-repeat-01-20260929'
checks=[]
def ok(name,value):
    assert value,name
    checks.append(name)
def enc(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest(raw):return sha256(raw).hexdigest()
def parse(raw):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('duplicate '+k)
            d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)))
def shape(a,s):
    if 'enum' in s:return any(type(a) is type(v) and a==v for v in s['enum'])
    t=s.get('type')
    if t=='object':return type(a) is dict and set(a)==set(s['required']) and all(shape(v,s['properties'][k]) for k,v in a.items())
    if t=='array':return type(a) is list and len(a)>=s.get('minItems',0) and len(a)<=s.get('maxItems',9999) and all(shape(v,s['items']) for v in a)
    if t=='string':return type(a) is str and ('enum' not in s or a in s['enum']) and len(a)>=s.get('minLength',0) and len(a)<=s.get('maxLength',999999)
    raise ValueError('unknown schema type '+str(t))
def refs(got,expected):return len(got)==len(expected) and len(set(got))==len(got) and set(got)==set(expected)
def legal(a):return type(a) is dict and set(a)=={'A','B'} and sorted(a.values())==['DIGITAL','PAPER']
def compute(payload,a,slot):
    rows=payload['experiences'];role=slot['role'];rates={};local={}
    for owner in {r['observer'] for r in rows}:
        rr=[r for r in rows if r['observer']==owner];n=sum(r['attempts_per_medium'] for r in rr)
        rates[owner]={m:Fraction(40*sum(r[m.lower()+'_success'] for r in rr),n) for m in ('PAPER','DIGITAL')}
        rate=rates[owner];local[owner]='UNDECIDED' if rate['PAPER']==rate['DIGITAL'] else max(rate,key=rate.get)
    ownrefs=[r['episode_id'] for r in rows if r['observer']==role]
    l=a['local']['subject']==role and a['local']['choice']==local[role]
    z=a['local']['subject']==role and refs(a['local']['evidence_refs'],ownrefs)
    result={'L':l,'Z_local':z,'F':None,'B':None,'C':None,'V':l and z,'K0':None,'G0':None,'bad_accept':None}
    if slot['stage']=='FORM':result['F']=result['V'];return result,rates,local,None
    opts=[{'A':'PAPER','B':'DIGITAL'},{'A':'DIGITAL','B':'PAPER'}]
    totals=[sum(rates[r][x[r]] for r in ('A','B')) for x in opts]
    best=[x for x,t in zip(opts,totals) if t==max(totals)]
    p=payload['initial_proposal'];b=a['reply'];allrefs=[r['episode_id'] for r in rows]
    action=(b['action']=='ACCEPT' and b['allocation']==p['body']['allocation']) if p['body']['allocation'] in best else ((b['action']=='COUNTER' and b['allocation'] in best and b['allocation']!=p['body']['allocation']) or (b['action']=='HOLD' and b['allocation']=={'A':'UNDECIDED','B':'UNDECIDED'}))
    reply_ref=b['reply_to']==p['record_id'];experience_ref=refs(b['evidence_refs'],allrefs);c=action and reply_ref and experience_ref
    k=p['author']!=role and reply_ref and b['action']=='ACCEPT' and b['allocation']==p['body']['allocation'] and legal(b['allocation'])
    g=k and p['body']['allocation'] in best and refs(p['body']['evidence_refs'],allrefs) and experience_ref
    result.update(B=l and z,C=c,V=l and z and c,K0=k,G0=g,bad_accept=b['action']=='ACCEPT' and not c,
                  appropriate_response=c,action_contract=action,reply_reference=reply_ref,experience_references=experience_ref,
                  Z_team=reply_ref and experience_ref,efficiency_optimal=b['allocation'] in best)
    own=payload['own_judgment']['body'];ownvalid=own['subject']==role and own['choice']==local[role] and refs(own['evidence_refs'],ownrefs)
    result.update(own_input_valid=ownvalid,transition=str(ownvalid).upper()+'_'+str(l and z).upper())
    return result,rates,local,{'best':best,'totals':[int(t) if t.denominator==1 else str(t) for t in totals],'options':opts}

with ZipFile(SOURCE) as z:
    names=z.namelist();ok('unique_members',len(names)==len(set(names)))
    ok('size_limit',len(names)<7500 and sum(x.file_size for x in z.infolist())<250000000)
    for item in z.infolist():
        p=PurePosixPath(item.filename)
        ok('path:'+item.filename,not p.is_absolute() and '..' not in p.parts and str(p)==item.filename and '\\' not in str(p) and not stat.S_ISLNK(item.external_attr>>16))
    files={n:z.read(n) for n in names};manifest=parse(files.pop('FEEDBACK_MANIFEST.json'))
    ok('member_set',set(files)==set(manifest['files_sha256']))
    for n,b in files.items():ok('hash:'+n,digest(b)==manifest['files_sha256'][n])
report=json.loads((OUT/'reaggregated.json').read_bytes())['report'];design=parse(files['design.json']);requests=parse(files['requests.json'])
fixed_manifest=json.loads((FIXED/'MANIFEST.json').read_bytes())
for name,h in fixed_manifest.items():ok('fixed:'+name,digest((FIXED/name).read_bytes())==h and files['frozen/'+name]==(FIXED/name).read_bytes())
ok('design_exact',files['design.json']==(FIXED/'materials-proposal.json').read_bytes())
ok('requests_exact',files['requests.json']==(FIXED/'requests.json').read_bytes())
for n in files:
    if n.startswith('report-') and n.endswith('.json'):ok('original_report:'+n,parse(files[n])==report)
packed=parse(files['payload.json'])
for name,text in packed['code'].items():ok('code:'+name,files['code/'+name]==text.encode()==(ROOT/'scripts'/name).read_bytes())
ok('planned_scope',len(requests)==len(design['allocation'])==240 and Counter(s['stage'] for s in design['allocation'])=={'FORM':96,'CONFIRM':144})
ok('response_set',{n.split('/')[1] for n in files if n.startswith('responses/')}=={s['id'] for s in design['allocation']})
ok('no_model_synthetic',all(not parse(b).get('synthetic_fixture') for n,b in files.items() if n.startswith('responses/') and n.endswith('/response.json')))
ok('generation_count',len([n for n in files if n.startswith('responses/') and n.endswith('/started.json')])==240)
ok('no_errors',not any('error-' in n or n.endswith('-error.json') for n in files))
ok('end_time',parse(files['run-end.json'])['elapsed_seconds']<=2700)
ok('pins',parse(files['environment.json'])['packages']['transformers']=='5.17.0' and parse(files['environment.json'])['packages']['accelerate']=='1.15.0')
config=parse(files['generation-config.json'])
for k,v in design['model']['generation'].items():ok('generation:'+k,config[k]==v)
ok('tokenizer_binding',parse(files['tokenizer-binding.json'])==design['source_tokenizer_binding'])
old_path=ROOT/design['source']['path'];ok('old_source_sha',digest(old_path.read_bytes())==design['source']['sha256'])
oldzip=ZipFile(old_path);templates=json.loads((FIXED/'source-inputs.json').read_text());parents=json.loads((FIXED/'source-parent-evidence.json').read_text())
rawrows=[];truths={};by_slot={r['id']:r for r in report['by_slot']};previous_start=None
for slot,request in zip(design['allocation'],requests):
    sid=slot['id'];pre='responses/'+sid+'/'
    raw=files[pre+'answer.txt'];a=parse(raw);inp=parse(files[pre+'input.json']);resp=parse(files[pre+'response.json']);result=parse(files[pre+'result.json'])
    started=parse(files[pre+'started.json']);template=templates[slot['source_id']]
    oldinputraw=oldzip.read('responses/'+slot['source_id']+'/input.json');oldinput=parse(oldinputraw)
    ok('schema:'+sid,shape(a,design['schemas'][slot['stage']]))
    ok('raw_plain:'+sid,parse(files[pre+'normalization.json'])['status']=='UNCHANGED' and files[pre+'normalized-answer.txt']==raw)
    ok('message_exact:'+sid,inp['messages']==request['messages']==oldinput['messages'])
    ok('oldinput_hash:'+sid,digest(oldinputraw)==template['source_input_sha256'])
    ok('token_exact:'+sid,inp['prepared']==oldinput['prepared'])
    ok('token_limits:'+sid,len(inp['prepared']['input_ids'])<=8192 and len(resp['output_token_ids'])<=1024 and len(raw)<=16384)
    ok('eos:'+sid,resp['finish_reason']=='EOS' and resp['output_token_ids'][-1]==248046 and resp['answer_text'].encode()==raw and resp['decoded_with_special_tokens']==resp['answer_text']+'<|im_end|>')
    ok('response_hash:'+sid,resp['payload_sha256']==digest(enc({k:v for k,v in resp.items() if k!='payload_sha256'})))
    ok('started_hash:'+sid,started['input_sha256']==digest(files[pre+'input.json']))
    seed=int(digest(enc([2026092905,slot['repeat'],slot['case'],slot['stage'],slot['role']]))[:8],16)%(2**31-1)
    ok('seed:'+sid,slot['seed']==request['seed']==inp['seed']==resp['seed']==started['seed']==seed)
    if previous_start is not None:ok('order:'+sid,started['started_at']>=previous_start)
    previous_start=started['started_at']
    ok('new_parents_none:'+sid,slot['parents']==[] and inp['binding']['new_parent_ids']==[])
    for pid,binding in inp['binding']['source_parents'].items():
        for key,name in [('source_saved_answer_sha256','saved-answer.json'),('source_raw_text_sha256','answer.txt'),('source_carry_answer_sha256','carry-answer.json'),('source_result_sha256','result.json')]:
            ok('old_parent_hash:'+sid+':'+pid+':'+key,binding[key]==digest(oldzip.read('responses/'+pid+'/'+name)))
    payload=parse(inp['messages'][1]['content'].split('\n',1)[1]);calc,rates,local,joint=compute(payload,a,slot);truths[sid]=calc
    if slot['stage']=='CONFIRM':
        pid='ST02-'+slot['condition_not_for_model']+'-'+slot['case']+'-FORM-'+slot['role']
        parent=parse(oldzip.read('responses/'+pid+'/carry-answer.json'))
        ok('fixed_own_content:'+sid,payload['own_judgment']['body']==parent['local'])
        for c in payload['joint_candidate_totals']:
            ok('joint_total:'+sid+':'+str(c['allocation']),sum(rates[r][c['allocation'][r]] for r in ('A','B'))==c['projected_total_success_per_40_each'])
    ok('summary_presence:'+sid,('own_experience_summary' in payload)==(slot['condition_not_for_model']=='EARLY'))
    if 'own_experience_summary' in payload:
        summary=payload['own_experience_summary'];rr=[r for r in payload['experiences'] if r['observer']==slot['role']]
        ok('own_summary:'+sid,summary['observer']==slot['role'] and summary['experience_refs']==[r['episode_id'] for r in rr] and summary['attempts_per_medium_total']==sum(r['attempts_per_medium'] for r in rr) and summary['projected_success_per_40']=={m:int(v) for m,v in rates[slot['role']].items()})
    ok('result_status:'+sid,result['status']==by_slot[sid]['status']=='EOS')
    ok('result_file_set:'+sid,{n[len(pre):] for n in files if n.startswith(pre) and n!=pre+'result.json'}==set(result['files_sha256']))
    for n,h in result['files_sha256'].items():ok('result_hash:'+sid+':'+n,digest(files[pre+n])==h)
    for k,v in calc.items():ok('independent_score:'+sid+':'+k,result['score'][k]==by_slot[sid]['score'][k]==v)
    ok('saved_answer:'+sid,parse(files[pre+'saved-answer.json'])==parse(files[pre+'carry-answer.json'])==a==result['score']['answer'])
    rawrows.append({'id':sid,'source_id':slot['source_id'],'repeat':slot['repeat'],'case':slot['case'],'stage':slot['stage'],'role':slot['role'],'arm':slot['condition_not_for_model'],'initial_type':slot['initial_type_not_for_model'],
                    'raw':raw.decode(),'payload':payload,'source_input_sha256':template['source_input_sha256'],'own_rates':{m:int(v) for m,v in rates[slot['role']].items()},'expected_local':local[slot['role']], 'joint':joint,'score':calc})
oldzip.close()
for rep in (1,2,3):
    for stage,keys in [('FORM',('F',)),('CONFIRM',('B','C','V','K0','G0','bad_accept'))]:
        for arm in ('LATE','EARLY'):
            ids=[s['id'] for s in design['allocation'] if s['repeat']==rep and s['stage']==stage and s['condition_not_for_model']==arm]
            for k in keys:
                count=report['by_repeat'][str(rep)][stage]['by_condition'][arm][k]
                ok(f'counts:{rep}:{stage}:{arm}:{k}',count['n']==len(ids) and count['correct']==sum(truths[i][k] for i in ids) and count['unresolved']==0)
        for k in keys:
            pairs=[p for p in design['paired_responses'] if p['repeat']==rep and p['stage']==stage]
            vals=[(truths[p['response_ids']['EARLY']][k],truths[p['response_ids']['LATE']][k]) for p in pairs]
            diff=sum(e-l for e,l in vals);p=report['by_repeat'][str(rep)][stage]['paired'][k]
            ok(f'paired:{rep}:{stage}:{k}',p['difference_count_bounds']==[diff,diff] and p['n']==len(vals))
for cell in report['fixed_input_stability']:
    for k,metric in cell['metrics'].items():
        values=[truths[i][k] for i in cell['response_ids']];p=sum(values);status='ALL_PASS' if p==3 else 'ALL_FAIL' if p==0 else 'MIXED'
        ok('stability:'+cell['source_id']+':'+k,metric['outcomes']==values and metric['correct']==p and metric['status']==status)
    answers=[parse(next(r['raw'] for r in rawrows if r['id']==i)) for i in cell['response_ids']]
    ok('json_stability:'+cell['source_id'],cell['answer_json_distinct_known']==len({digest(enc(a)) for a in answers}))
    if cell['stage']=='CONFIRM':ok('action_stability:'+cell['source_id'],cell['actions']==[a['reply']['action'] for a in answers])
# Selection reconstructed independently rather than trusting the reported review list.
slots={s['id']:s for s in design['allocation']};selected={i for i,t in truths.items() if not t['V']}
for cell in report['fixed_input_stability']:
    keys=('F',) if cell['stage']=='FORM' else ('B','C','V')
    mixed=any(len({truths[i][k] for i in cell['response_ids']})>1 for k in keys)
    if mixed or cell['known_action_variation']:selected.update(cell['response_ids'])
selected.update(s['id'] for s in design['allocation'] if s['stage']=='CONFIRM' and s['case']=='N05' and s['initial_type_not_for_model']=='LOWER')
for stage in ('FORM','CONFIRM'):
    eligible=[]
    for pair in design['paired_responses']:
        if pair['repeat']!=1 or pair['stage']!=stage:continue
        src={slots[i]['source_id'] for i in pair['response_ids'].values()};ids=[s['id'] for s in slots.values() if s['source_id'] in src]
        if all(truths[i]['V'] for i in ids):eligible.append((pair['fixed_pair_id'],ids))
    eligible.sort(key=lambda x:digest(('JR01-review|2026092905|'+stage+'|'+x[0]).encode()))
    ok('normal_selection:'+stage,report['reason_review']['normal_pairs'][stage]==[x[0] for x in eligible[:4]])
    for _,ids in eligible[:4]:selected.update(ids)
ok('review_selection',selected==set(report['reason_review']['all_response_ids']))
review={'responses':[r for r in rawrows if r['id'] in selected],
        'source_parents':{p:parents[p] for p in report['reason_review']['fixed_source_parents']},
        'source_inputs':{s:templates[s] for s in report['reason_review']['fixed_source_inputs']}}
(HERE/'review-materials.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
(OUT/'diagnostics.json').write_text(json.dumps({'all_responses':rawrows,'review_responses':len(selected),'nonpassing':sum(not x['V'] for x in truths.values()),'performance':report['performance'],'normalization':report['normalization']},ensure_ascii=False,indent=2)+'\n')
for n,h in json.loads((HERE/'protected-before.json').read_bytes()).items():ok('protected:'+n,digest((ROOT/n).read_bytes())==h)
result={'status':'PASS','checks':len(checks),'items':checks,'response_count':240,'sealed_files':len(files),
        'review_responses':len(selected),'review_source_inputs':len(review['source_inputs']),'review_source_parents':len(review['source_parents']),
        'model_calls':0,'scorer_imports':0,'scope':'Independent arithmetic, source carry, response structure, paired/stability summaries, and review selection.'}
(HERE/'independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='items'},ensure_ascii=False))
