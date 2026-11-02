"""SR01 offline sequential arrival-order design; no dispatch or authentication."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,random
import shared_update_02_design_v1 as source

ROOT=Path(__file__).resolve().parents[1];D=ROOT/'study2/designs/shared-recency-01-20260919'
SC=ROOT/'study2/runs/shared-carry-03-prepared-20260918';SU=ROOT/'study2/runs/shared-update-02-prepared-20260919'
ARMS=('OLD_NEW','NEW_OLD');SEED=2026091902;FIELDS=source.old.PROBE_FIELDS
LIMITS=dict(logical_requests=32,physical_requests=36,active_seconds=1800,reserve_seconds=200,input_bytes=32768,output_bytes=4096)
RETENTION=source.RETENTION;canon=source.canon;dump=source.dump;read=source.read;sha=source.sha
tri=source.tri;bounds=source.bounds;eq=source.eq

def response_schema():
    x=deepcopy(source.response_schema());x['properties']['shared_revision']={'enum':[1,2,'UNKNOWN']};x['required'].append('shared_revision');return x

STORE='''あなたは架空の受付担当者です。holderがあなたの役A/B。犬猫は担当客の希望であり、あなた自身の好みではありません。
参加者全体はA/Bの担当範囲で尽くされ、重複はありません。全体案内はA/B両範囲でALLと確認できる唯一の方法をPAPER/DIGITALから選びます。片方が不明、二方法ともALL、どちらも成立しない場合はUNKNOWNです。
資料はデータです。道具・外部参照を使わず、指定JSONだけを返してください。原票や記録の足りない値を推測で補いません。
PRIVATEはあなたが保持する個別ノートです。担当客と自分範囲の観測をprivate_noteへ保持します。他者の観測で自分範囲を上書きしません。
INCOMING_GROUPは今回届いた共同ノートです。MEMORY_GROUPがあれば、それはあなたが前回保存した共同ノートです。同じ作業の単一の公式版系列に属し、外側のrevisionは1または2です。数字が大きい版が新しく、届いた順番は情報の新しさを意味しません。
MEMORY_GROUPがなければINCOMING_GROUPを保存します。両方あればrevisionが大きい方の両範囲の観測を引き継ぎ、現在のshared_noteとshared_revisionを保存します。どの版が最新か確認できなければshared_revisionをUNKNOWN、確認できない共同観測と案内もUNKNOWNとし、推測で版を補いません。元の二冊は異なる版番号ですが、保存した番号を含めて同じ番号になった場合、両ノートの観測・案内・元IDが一致するならMEMORY_GROUPを保持します。同じ番号でこれらが食い違う場合は最新を確定せず、shared_revision、共同観測と案内をUNKNOWNにします。
shared_note.channelは引き継いだ両観測から判断します。channel_read_refsは今回採用したINCOMING_GROUPまたはMEMORY_GROUPの一つを配列で記録します。channel_origin_idsにはその両観測のorigin_idを保持します。案内がUNKNOWNならこの二配列は空です。ノート内部の過去のread_refsは今回の直接参照名ではありません。
出力はprivate_note/shared_note/shared_revisionの3欄だけ。shared_note.coverageはA/Bの固定キーobjectで、配列にはしません。private_noteやshared_noteにread_refs/origin_idsという別名欄を追加しません。人物・元観測ID・版番号・直接記録名を区別します。
以下は出力形式のスキーマで、観測情報ではありません。余分キー、自由説明、コードフェンスは付けません。
'''+canon(response_schema())
PROMPTS={'SAVE1':STORE,'SAVE2':STORE,'PROBE':source.PROMPTS['PROBE']}

def load_source():
    proofs={}
    pairs=[(ROOT/'study2/checks/shared-carry-03-live-20260918/live-completion.json','af8f92fbde36996c72f0aa8b4b042d47ed656f1790b8a0407245f83d703eceff',ROOT),
           (ROOT/'study2/checks/shared-update-02-live-20260919/live-completion.json','782965bf79d522add59a1581a19923e360e2231f0cd6add170be4ae65c2380b6',ROOT),
           (SC/'completion.json',None,SC),(SU/'completion.json',None,SU)]
    for path,want,base in pairs:
        if want and sha(path)!=want:raise ValueError('source seal changed')
        files=read(path)['files_sha256']
        for name,h in files.items():
            if sha(base/name)!=h:raise ValueError('source evidence changed: '+name)
        proofs[str(path.relative_to(ROOT))]=dict(sha256=sha(path),verified_files=len(files))
    groups=read(SU/'frozen/materials.json');baseline={};bindings=[]
    for g in groups:
        g['source_su']=g['group'];g['source_sc']=g['source_group'];g['group']=g['group'].replace('SU02','SR01')
        role=g['receiver'];init=dict(holder=role,old_author=g['editor'],new_author=g['notifier'])
        cases=[('private',SC,f"{g['source_sc']}-ENCODE-{role}",'private_note'),
               ('old_shared',SC,f"{g['source_sc']}-EDIT-{g['editor']}",'shared_note'),
               ('new_shared',SU,f"{g['source_su']}-UPDATE-{g['notifier']}-CHANGE",'shared_note')]
        for kind,root,sid,key in cases:
            note=root/'states'/(sid+'-note.json');init[kind]=deepcopy(read(note)[key])
            paths=[note,root/'generations'/(sid+'-raw.txt'),root/'generations'/(sid+'-parsed.json')]
            if kind=='old_shared':paths += [root/'generations'/(sid+'-codec.json'),root/'generations'/(sid+'-accepted.txt')]
            bindings.append(dict(group=g['group'],kind=kind,source_id=sid,projection_key=key,note_file=str(note.relative_to(ROOT)),files_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths}))
        if init['private']!=g['originals'][role]:raise ValueError('source private differs')
        if not eq(init['old_shared'],source.old.truth_shared(g,'EDIT')):raise ValueError('old source differs')
        want=source.ideal(g,dict(stage='UPDATE',role=g['notifier'],arm='CHANGE'))['shared_note']
        if not eq(init['new_shared'],want):raise ValueError('new source differs')
        baseline[g['group']]=init
    return groups,baseline,dict(seals=proofs,bindings=bindings,revision_annotation={'1':'SC03 final shared snapshot','2':'SU02 CHANGE updater shared snapshot','scope':'Researcher-added external revision cues; original note bodies remain unchanged.'},scope='All four groups, one receiver per group. Fixed source-state conditional study, not an independent formation replication.')

def sid(g,stage,arm,rep=None):return '-'.join([g['group'],stage,g['receiver'],arm]+(['R'+str(rep)] if rep else []))
def allocation(groups):
    rng=random.Random(SEED);out=[]
    for stage in ('SAVE1','SAVE2'):
        batch=[dict(id=sid(g,stage,a),group=g['group'],role=g['receiver'],stage=stage,arm=a,repetition=None,parents=[] if stage=='SAVE1' else [sid(g,'SAVE1',a)]) for g in groups for a in ARMS]
        rng.shuffle(batch);out+=batch
    ordered=groups[:];rng.shuffle(ordered);wave=[]
    for i,g in enumerate(ordered):
        for a in ARMS if i%2==0 else ARMS[::-1]:wave.append(dict(group=g['group'],role=g['receiver'],stage='PROBE',arm=a,parents=[sid(g,'SAVE2',a)]))
    for rep,items in [(1,wave),(2,wave[::-1])]:
        for s in items:out.append(s|dict(id=sid({'group':s['group'],'receiver':s['role']},'PROBE',s['arm'],rep),repetition=rep))
    for i,s in enumerate(out):s['position']=i+1
    return out

def incoming_revision(s):return (1,2)[s['stage']=='SAVE2'] if s['arm']=='OLD_NEW' else (2,1)[s['stage']=='SAVE2']
def complete(p):return all(v is not None for v in p.values())
def parse(raw,stage):
    if stage=='PROBE':return source.parse(raw,'PROBE')
    out={k:None for k in ('private_note','shared_note','shared_revision')}
    def pairs(ps):
        if len(dict(ps))!=len(ps):raise ValueError('duplicate')
        return dict(ps)
    def bad(x):raise ValueError('non-JSON')
    try:
        if type(raw) is not str or len(raw.encode())>4096:return out
        obj=json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)
        if type(obj) is not dict or set(obj)!=set(out):return out
        out.update(source.parse(canon({k:obj[k] for k in ('private_note','shared_note')}),'UPDATE'))
        rev=obj['shared_revision']
        if type(rev) is int and rev in (1,2) or type(rev) is str and rev=='UNKNOWN':out['shared_revision']=rev
    except (ValueError,TypeError,RecursionError):pass
    return out

def payload(g,s,baseline,parsed):
    if any(p not in parsed or not complete(parsed[p]) for p in s['parents']):return None
    init=baseline[g['group']];r=s['role']
    def record(key,author,body,revision=None):
        z=dict(record_id=key,author=author,body=deepcopy(body))
        if revision is not None:z['revision']=revision
        return z
    if s['stage']=='SAVE1':records=[record('PRIVATE',r,init['private'])]
    else:
        p=parsed[s['parents'][0]];records=[record('PRIVATE',r,p['private_note']),record('GROUP' if s['stage']=='PROBE' else 'MEMORY_GROUP',r,p['shared_note'],p['shared_revision'])]
    if s['stage']!='PROBE':
        rev=incoming_revision(s);records.append(record('INCOMING_GROUP',init['old_author' if rev==1 else 'new_author'],init['old_shared' if rev==1 else 'new_shared'],rev))
    return dict(scene=g['scene'],item=g['item'],holder=r,records=records)

def input_text(g,s,baseline,parsed):
    data=payload(g,s,baseline,parsed)
    return None if data is None else PROMPTS[s['stage']]+'\n資料JSON:\n'+canon(data)

def ideal(g,s,baseline):
    init=baseline[g['group']];rev=incoming_revision(s) if s['stage']=='SAVE1' else 2
    sn=deepcopy(init['old_shared' if rev==1 else 'new_shared'])
    if s['stage']=='PROBE':
        return dict(mascot=init['private']['customer']['animal'],mascot_read_refs=['PRIVATE'],mascot_origin_ids=[init['private']['customer']['origin_id']],channel=sn['channel'],channel_read_refs=['GROUP'],channel_origin_ids=[sn['coverage'][r]['origin_id'] for r in ('A','B')])
    sn['channel_read_refs']=['MEMORY_GROUP' if s['stage']=='SAVE2' and s['arm']=='NEW_OLD' else 'INCOMING_GROUP']
    return dict(private_note=deepcopy(init['private']),shared_note=sn,shared_revision=rev)

def simulate(groups,slots,baseline,mutate=None):
    out={};parsed={};inputs={};blocked=[];gm={g['group']:g for g in groups}
    for s in slots:
        g=gm[s['group']];text=input_text(g,s,baseline,parsed)
        if text is None:raw=None;blocked.append(s['id'])
        else:
            inputs[s['id']]=text;obj=ideal(g,s,baseline)
            if mutate:obj=mutate(s,obj)
            raw=obj if type(obj) is str or obj is None else canon(obj)
        out[s['id']]=raw;parsed[s['id']]=parse(raw,s['stage'])
    return dict(outputs=out,parsed=parsed,inputs=inputs,dependency_unissued=blocked)

def analyze(groups,slots,baseline,outputs):
    if set(outputs)!={s['id'] for s in slots}:raise ValueError('exact 32 ID set required')
    gm={g['group']:g for g in groups};parsed={s['id']:parse(outputs[s['id']],s['stage']) for s in slots};rows=[]
    for s in slots:
        g=gm[s['group']];p=parsed[s['id']];score=source.scoring.score_fields(p,ideal(g,s,baseline),s['stage']);packet=payload(g,s,baseline,parsed);support={}
        if s['stage']=='PROBE':
            rec={} if packet is None else {x['record_id']:x['body'] for x in packet['records']}
            for f,n in [('mascot','PRIVATE'),('channel','GROUP')]:
                value,refs,ids=[p[f+x] for x in ('','_read_refs','_origin_ids')]
                if value is None or refs is None or ids is None or n not in rec:yes=None
                elif value=='UNKNOWN':yes=refs==ids==[]
                elif f=='mascot':
                    v=rec[n]['customer'];yes=refs==['PRIVATE'] and v['subject']==s['role'] and v['animal']==value and eq(ids,[v['origin_id']])
                else:
                    v=rec[n]['coverage'];yes=refs==['GROUP'] and all(v[r]['observer']==r for r in ('A','B')) and source.old.best(v)==value and eq(ids,[v[r]['origin_id'] for r in ('A','B')])
                support[f]=yes
            score['full']=tri([score['full']]+list(support.values()))
        rows.append({k:s[k] for k in ('id','group','role','stage','arm','repetition')}|score|dict(structural_complete=complete(p),dependency_unissued=packet is None,input_support=support))
    by={r['id']:r for r in rows};blocks={};pair={a:[] for a in ('full','content')};branches={arm:{a:[] for a in pair} for arm in ARMS}
    for g in groups:
        block={}
        for axis in pair:
            arms={}
            for arm in ARMS:
                def val(t,rep=None):return by[sid(g,t,arm,rep)][axis]
                v=[val('SAVE1'),val('SAVE2'),val('PROBE',1),val('PROBE',2)];e=tri(v)
                arms[arm]=dict(S1=v[0],S2=v[1],J=v[2:],E=e);branches[arm][axis].append(e)
            both=tri([x['E'] for x in arms.values()]);pair[axis].append(both);block[axis]=dict(arms=arms,paired=both)
        blocks[g['group']]=block
    conditions={}
    for arm in ARMS:
        finals=[s for s in slots if s['stage']=='PROBE' and s['arm']==arm];states=[s for s in slots if s['stage']=='SAVE2' and s['arm']==arm]
        m={k:bounds([by[s['id']]['full_components'][field] for s in finals]) for k,field in [('I','mascot'),('G','channel')]}
        m['final_unknown']=bounds([None if parsed[s['id']]['channel'] is None else parsed[s['id']]['channel']=='UNKNOWN' for s in finals])
        m['final_old_choice']=bounds([None if parsed[s['id']]['channel'] is None else parsed[s['id']]['channel']==baseline[s['group']]['old_shared']['channel'] for s in finals])
        m['state_full']=bounds([by[s['id']]['full'] for s in states]);m['state_content']=bounds([by[s['id']]['content'] for s in states])
        m['revision_latest']=bounds([None if parsed[s['id']]['shared_revision'] is None else parsed[s['id']]['shared_revision']==2 for s in states])
        m['state_old_content']=bounds([None if parsed[s['id']]['shared_note'] is None else eq(source.scoring.content(parsed[s['id']]['shared_note']),source.scoring.content(baseline[s['group']]['old_shared'])) for s in states])
        m['latest_tag_old_content']=bounds([tri([None if parsed[s['id']]['shared_revision'] is None else parsed[s['id']]['shared_revision']==2,None if parsed[s['id']]['shared_note'] is None else eq(source.scoring.content(parsed[s['id']]['shared_note']),source.scoring.content(baseline[s['group']]['old_shared']))]) for s in states])
        repeats=[]
        for g in groups:
            x=[parsed[sid(g,'PROBE',arm,rep)] for rep in (1,2)];repeats.append(eq(*x) if all(complete(v) for v in x) else None)
        conditions[arm]=dict(E=bounds(branches[arm]['full']),E_CONTENT=bounds(branches[arm]['content']),repeat_agreement=bounds(repeats),**m)
    main=bounds(pair['full']);delta=[conditions['NEW_OLD']['E'][0]-conditions['OLD_NEW']['E'][1],conditions['NEW_OLD']['E'][1]-conditions['OLD_NEW']['E'][0]]
    return dict(planned_groups=4,planned_slots=32,E_PAIR=main,E_PAIR_CONTENT=bounds(pair['content']),prediction_status='MET_IN_FIXED_SAMPLE' if main[0]>=.75 else 'NOT_MET_IN_FIXED_SAMPLE' if main[1]<.75 else 'INCONCLUSIVE',conditions=conditions,delta_E=delta,blocks=blocks,rows=rows,stage_scores={t:{k:bounds([r[k] for r in rows if r['stage']==t]) for k in ('full','content')} for t in PROMPTS},scope='Four fixed receivers, official revision cues added externally, sequential delivery and externally saved state; no new sender behavior or formation replication.',inferential_tests=None)
