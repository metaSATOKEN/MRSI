"""Offline replay of saved outputs. No generation, credentials, or transport.

Frozen scorers are unchanged. Additional reporting is post-study; it does not
replace original scores. Run `python3 replay.py` from any working directory.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
from itertools import product
import hashlib,json,sys,math,statistics
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
# This process refuses network and child-process calls, including imported code.
def offline_guard(event,args):
    if event.startswith('socket.') or event in ('subprocess.Popen','os.system','os.posix_spawn'):
        raise RuntimeError('OFFLINE_REPLAY_FORBIDS:'+event)
sys.addaudithook(offline_guard)
sys.path.insert(0,str(ROOT/'code'))
import paper01_pair_design_v1 as pair
import row_carry_02_design_v1 as rc2
import row_carry_design_v1 as rc1
import shared_merge_02_design_v1 as sm2
from scipy.stats import beta,binomtest
import scipy

def read(p):return json.loads(p.read_text())
checks=[]
def check(name,value):
    checks.append({'name':name,'pass':bool(value)})
    if not value:raise AssertionError(name)
def same(a,b):
    if type(a) in (float,int) and type(b) in (float,int):return abs(a-b)<1e-10
    if isinstance(a,dict) and isinstance(b,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return type(a)==type(b) and a==b

def validate_manifest():
    manifest=read(ROOT/'MANIFEST.json')
    for rel,h in manifest['sha256'].items():
        p=ROOT/rel;check('hash:'+rel,p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==h)
    return len(manifest['sha256'])
# During preparation only --unsealed is used; distributed instructions use sealed mode.
file_count=0 if '--unsealed' in sys.argv else validate_manifest()

base=ROOT/'data/pair';c=read(base/'configuration.json');official=read(base/'analysis.json')
scores={};states={};received={};request_models=set()
for s in c['allocation']:
    sid=s['id'];m=c['materials'][s['group']]
    raw=(base/'generations'/f'{sid}-raw.txt').read_bytes()
    incoming=read(base/'states'/f'{sid}-incoming.json')
    projected=pair.e1_input(m,s,states) if s['experiment']=='E1' else pair.e2_input(m,s,states)
    check('input:'+sid,projected==incoming)
    req=read(base/'requests'/f'{sid}.json');request_models.add(req['model'])
    check('request keys:'+sid,set(req)=={'input','model','reasoning','tools','tool_choice','parallel_tool_calls','store','stream'})
    check('request tools:'+sid,req['tools']==[] and req['tool_choice']=='none' and req['parallel_tool_calls'] is False)
    expected_prompt=(base/'frozen'/('prompt-e2-'+s['stage'].lower()+'.txt' if s['experiment']=='E2' else 'prompt-e1-'+s['stage'].lower()+'-'+(s['condition'].lower() if s['stage']=='MERGE' else 'common')+'.txt')).read_text()
    check('request instruction:'+sid,req['input'][0]['content'][0]['text']==expected_prompt)
    check('request payload:'+sid,req['input'][1]['content'][0]['text']=='\n資料JSON:\n'+pair.json_bytes(incoming).decode())
    ev=pair.e1_evaluate(m,s,raw,incoming) if s['experiment']=='E1' else pair.e2_evaluate(m,s,raw,incoming)
    scores[sid]=ev['score'];check('score:'+sid,same(ev['score'],official['slot_scores'][sid]))
    received[sid]=raw
    if s['stage']!='PROBE' and ev['gate']=='PASS':
        state=ev['normalized']['memory'] if s['experiment']=='E1' else ev['value']
        states[sid]=state
        check('save:'+sid,state==read(base/'states'/f'{sid}-saved.json'))
aggregate=pair.aggregate(c['materials'],c['allocation'],scores)
check('E1/E2 complete aggregate',same(aggregate,official['analysis']))
check('main p missing',aggregate['E1']['strict']['statistics']['exact_mcnemar_two_sided_p'] is None)
check('raw 704, state 352',len(received)==704 and len(states)==352)

# The brace correction is explicitly post hoc, in a separate derived variable.
sid='E1-G23-REWRITE-PROBE-B';raw=received[sid]
check('only final brace',len(raw)==227 and raw[-1:]==b'}')
s=next(s for s in c['allocation'] if s['id']==sid)
derived=pair.e1_evaluate(c['materials'][s['group']],s,raw[:-1],read(base/'states'/f'{sid}-incoming.json'))
check('posthoc corrected score',derived['score']['strict'] is True)
ref_scores=deepcopy(scores);ref_scores[sid]=derived['score']
reference=pair.aggregate(c['materials'],c['allocation'],ref_scores)
check('reference p one',reference['E1']['strict']['statistics']['exact_mcnemar_two_sided_p']==1.0)
check('formal unchanged after reference',scores[sid]['strict'] is None)

old_results={}
for name,mod in [('shared-merge-02',sm2),('row-carry-01',rc1),('row-carry-02',rc2)]:
    b=ROOT/'data'/name;config=read(b/'configuration.json');expected=read(b/'analysis.json')
    memory={};ss={}
    for s in config['allocation']:
        sid=s['id'];m=config['materials'][s['group']]
        raw=(b/'generations'/f'{sid}-raw.txt').read_bytes();incoming=read(b/'states'/f'{sid}-incoming.json')
        projected=mod.input_for(s,config['root_payloads'],memory) if name=='row-carry-01' else mod.input_for(m,s,memory)
        check('old input:'+sid,projected==incoming)
        if name=='shared-merge-02':
            ev=mod.inspect(raw,incoming,s['stage']);score=mod.score(m,s,raw,incoming);v=ev['value']
        else:
            ev=mod.evaluate(m,s,raw,incoming);score=ev['score'];v=ev['normalized']
        ss[sid]=score;check('old score:'+sid,same(score,expected['slot_scores'][sid]))
        if s['stage']!='PROBE' and ev['gate']=='PASS':
            memory[sid]=v['memory'];check('old save:'+sid,memory[sid]==read(b/'states'/f'{sid}-note.json'))
    if name=='shared-merge-02':
        groups={mode:{g:rc2.tri_and(ss[s['id']][mode] for s in config['allocation'] if s['group']==g) for g in config['materials']} for mode in ['strict','content']}
        check('SM02 groups',groups==expected['by_group']);old_results[name]=groups
    else:
        agg=mod.aggregate(config['allocation'],ss);check(name+' aggregate',same(agg,expected['aggregate']));old_results[name]=agg

# Descriptive supplemental tables reproduce the audit; not additional tests.
intervals={}
for mode in ('strict','content'):
    g=aggregate['E1'][mode]['groups'];pairs=[(x['REWRITE'],x['SELECT']) for x in g.values()]
    possible=pair.paired_counts_possible(pairs);rows=[]
    for a,b in possible:
        L=lambda k:0. if k==0 else float(beta.ppf(.0125,k,65-k))
        U=lambda k:1. if k==64 else float(beta.ppf(.9875,k+1,64-k))
        rows.append({'SELECT_only':a,'REWRITE_only':b,'Lselect':L(a),'Uselect':U(a),'Lrewrite':L(b),'Urewrite':U(b),'ci95':[L(a)-U(b),U(a)-L(b)]})
    intervals[mode]=rows
shared={method:{g:rc2.tri_and(scores[f'{g}-{method}-MERGE-{role}']['parts'][f'shared_note.coverage.{owner}']['strict'] for role in ['A','B'] for owner in ['A','B']) for g in c['materials'] if g.startswith('E1')} for method in ['REWRITE','SELECT']}
check('shared group count',[sum(x is True for x in shared[m].values()) for m in ['REWRITE','SELECT']]==[61,64])
cp8={str(k):list(binomtest(k,8).proportion_ci(confidence_level=.95,method='exact')) for k in [0,8]}
strata={}
for axis,ix in [('scene_name',0),('area',1)]:
    rows={}
    for g,v in aggregate['E1']['strict']['groups'].items():
        label=c['materials'][g]['scene'].split('・')[ix];r,s=v['REWRITE'],v['SELECT']
        cat='unknown' if r is None or s is None else 'both' if r and s else 'REWRITE_only' if r else 'SELECT_only' if s else 'neither'
        rows.setdefault(label,Counter())[cat]+=1
    strata[axis]={label:dict(cnt) for label,cnt in rows.items()}

# v0.7 post-study descriptions: no added significance tests.
audit=read(ROOT/'references/analysis/paper-01-rereview-20260922/numerical-audit.json')
output_bytes=[]
for method in ('REWRITE','SELECT'):
    for stage in ('MERGE','PROBE'):
        chosen=[s for s in c['allocation'] if s['experiment']=='E1' and s['condition']==method and s['stage']==stage]
        values=[len(received[s['id']]) for s in chosen]
        output_bytes.append(dict(condition=method,stage=stage,n_answers=len(values),mean_bytes=statistics.mean(values),median_bytes=statistics.median(values),min_bytes=min(values),max_bytes=max(values),total_bytes=sum(values)))
check('posthoc raw output bytes',same(output_bytes,audit['E1_raw_output_bytes']))
a=sum(shared['SELECT'][g] and not shared['REWRITE'][g] for g in shared['SELECT'])
b=sum(shared['REWRITE'][g] and not shared['SELECT'][g] for g in shared['SELECT'])
component_interval=dict(delta=(a-b)/64,SELECT_only=a,REWRITE_only=b,
    SELECT_CP975=[L(a),U(a)],REWRITE_CP975=[L(b),U(b)],nominal_CI95=[L(a)-U(b),U(a)-L(b)])
check('posthoc shared component interval',same(component_interval,{k:audit['shared_groups'][k] for k in component_interval}))
g=aggregate['E1']['strict']['groups']
known=sum(None not in v.values() and v['REWRITE']!=v['SELECT'] for v in g.values())
missing=sum(None in v.values() for v in g.values())
discordance=dict(known=known,unresolved=missing,possible_counts=[known,known+missing],possible_fraction=[known/64,(known+missing)/64])
check('discordance description',discordance['possible_counts']==audit['discordance']['possible_counts'])
retention=read(ROOT/'RETENTION.json')
check('approved no-deadline policy',retention['status']=='APPROVED_ACTIVE' and retention['deletion_deadline'] is None)

# Preserve original scores for the other eight studies without claiming rescoring.
index=read(ROOT/'data/study-index.json')
reported={}
for name in index:
    if name in old_results or name=='pair':continue
    original=read(ROOT/'data'/name/'analysis.json')
    reported[name]={k:v for k,v in original.items() if k in ['planned_groups','planned_slots','prediction_status','status_counts','F','E_BOTH','E_VALUE','E_NOREF','C_PAIR','C_PAIR_CONTENT','E_PAIR','E_PAIR_CONTENT','M_PAIR','M_PAIR_CONTENT','aggregate','summary']}

out=ROOT/'replay-output';out.mkdir(exist_ok=True)
result={'status':'PASS','replay_scope':'704 E1/E2 + 88 SM02/RC01/RC02 answers rescored; other eight studies retain original reported analyses',
    'python':sys.version.split()[0],'scipy':scipy.__version__,'requested_models':sorted(request_models),
    'scored_answers':792,'preserved_raw_answers':sum(r['answers'] for r in index.values()),'saved_pair_states':len(states),
    'checks_passed':len(checks),'manifest_files_checked':file_count,'formal':aggregate,'posthoc_brace_reference':reference,
    'exploratory_replayed':old_results,'exploratory_original_summaries':reported,
    'interval_components':intervals,'shared_row_groups_posthoc':shared,'label_strata_posthoc':strata,'E2_nominal_CP95_posthoc':cp8,
    'shared_component_interval_posthoc':component_interval,'output_bytes_posthoc':output_bytes,'discordance_description':discordance,
    'retention':retention['retention'],'network_calls':0,'new_model_requests':0}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# 保存済み証拠の再計算結果','','原回答の再取得・意味修理は行わない。正式な未確定と事後参考値を別掲する。','',
'| E1／固定64組 | REWRITE 成立/不成立/未確定 | SELECT 成立/不成立/未確定 | 欠測上下限pt | 95%包絡pt |','| --- | --- | --- | --- | --- |']
for mode in ['strict','content']:
    rec=aggregate['E1'][mode];stat=rec['statistics'];counts=[]
    for method in ['REWRITE','SELECT']:
        vals=[x[method] for x in rec['groups'].values()];counts.append('/'.join(str(sum(v is flag for v in vals)) for flag in [True,False,None]))
    fmt=lambda xs:'〜'.join(f'{x*100:.2f}' for x in xs)
    lines.append(f"| {mode} | {counts[0]} | {counts[1]} | {fmt(stat['delta_bounds'])} | {fmt(stat['conservative_ci95'])} |")
lines+=['','正式主p値は未算出。括弧補正後の事後参考p値は1.000。','',
'共同4行の事後組単位集約：REWRITE 61/64、SELECT 64/64。','',
'| E2／各8場面 | 完遂 | 根拠適合 |','| --- | ---: | ---: |']
for cell,metrics in aggregate['E2'].items():
    lines.append(f"| {cell} | {sum(metrics['completion']['groups'].values())}/8 | {sum(metrics['evidence_appropriate']['groups'].values())}/8 |")
lines+=['','名目CP95%：8/8は63.06〜100%、0/8は0〜36.94%。二項モデルの作業仮定付き・事後記述補足。', '',
'原回答792件を再採点し、元の成分採点と一致。収録原回答は旧系列423＋追加704＝1,127件。詳細はresults.json。','']
lines+=['','共同観測成分の事後差：+4.6875ポイント、名目95%区間−5.867991〜14.435629ポイント。組間独立を仮定し、成分選択の多重性は未調整。追加検定なし。',
    '確定食違い9組・未確定1組。可能な食違いは9〜10/64。','',
    '| 方式 | 工程 | 回答数 | 平均UTF-8 bytes | 中央値 | 最小 | 最大 |',
    '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
for r in output_bytes:
    lines.append(f"| {r['condition']} | {r['stage']} | {r['n_answers']} | {r['mean_bytes']:.4f} | {r['median_bytes']:.1f} | {r['min_bytes']} | {r['max_bytes']} |")
lines+=['','出力長はJSON未確定1件を含む無修正の原回答。tokensや推論量ではない。','']
(out/'tables.md').write_text('\n'.join(lines))
print(json.dumps({k:result[k] for k in ['status','scored_answers','preserved_raw_answers','checks_passed','manifest_files_checked','network_calls','new_model_requests']},ensure_ascii=False))
