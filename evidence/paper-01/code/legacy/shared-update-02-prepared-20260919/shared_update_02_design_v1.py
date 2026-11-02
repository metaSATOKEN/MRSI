"""SU02 offline-only design: conditional update from all four sealed SC03 states."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import random
import shared_update_design_v1 as old
import shared_update_analysis_v1 as scoring
import shared_note_codec_v1 as schema_source

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'study2/designs/shared-update-02-20260919'
SOURCE=ROOT/'study2/runs/shared-carry-03-prepared-20260918'
ROLES=old.ROLES;ARMS=old.ARMS;SEED=2026091901
LIMITS=dict(logical_requests=48,physical_requests=52,active_seconds=2700,reserve_seconds=200,input_bytes=32768,output_bytes=4096)
RETENTION='2026-10-12T17:41:23+09:00'
canon=old.canon;dump=old.dump;parse=old.parse;continuable=old.continuable;sid=old.sid;ideal=old.ideal
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tri=scoring.conjunction;bounds=scoring.interval;eq=scoring.equivalent

def response_schema():
    shared=schema_source.schema()['properties']['shared_note']
    obs=deepcopy(shared['properties']['coverage']['properties']['A'])
    customer={'type':'object','properties':{'subject':{'type':'string','enum':['A','B','UNKNOWN']},
        'animal':{'type':'string','enum':['DOG','CAT','UNKNOWN']},'origin_id':deepcopy(obs['properties']['origin_id'])},
        'required':['subject','animal','origin_id'],'additionalProperties':False}
    private={'type':'object','properties':{'customer':customer,'coverage':obs},'required':['customer','coverage'],'additionalProperties':False}
    return {'type':'object','properties':{'private_note':private,'shared_note':shared},'required':['private_note','shared_note'],'additionalProperties':False}

CONTRACT='''\n出力形式の固定契約：トップはprivate_note/shared_noteの2欄だけです。private_noteにread_refs/origin_idsを追加しません。shared_noteにもread_refs/origin_idsという別名の欄を追加しません。必要な出典欄はchannel_read_refs/channel_origin_idsです。
shared_note.coverageはA/Bの固定キーを各1個持つJSON objectです。配列にはしません。各キーの中はobserver/paper/digital/origin_idの4欄だけです。
channel_read_refsはこの提出版を作るために今直接読んだ外側のrecord_idです。受け取ったノート内部に残る過去のchannel_read_refsをそのままコピーしません。channel_origin_idsは根拠となる観測オブジェクトのorigin_idを引き継ぐ欄です。
以下は回答形式のスキーマで、観測データではありません。スキーマ自体を回答にせず、資料の値を記入してください。余分なキー、自由説明、コードフェンスは付けません。\n'''+canon(response_schema())
PROMPTS={t:old.PROMPTS[t]+CONTRACT for t in ('UPDATE','RECEIVE')}
# Exact SC03 frozen probe; retain as a literal for portable future freezing.
PROMPTS['PROBE']='あなたは架空の受付担当者です。holderがあなたの役A/B。犬猫は担当客の希望であり、あなた自身の好みではありません。\n参加者全体はAとBの担当範囲で尽くされ、重複はありません。全体案内は、A/B両範囲でALLと確認できる唯一の方法をPAPER/DIGITALから選びます。片方が不明、二方法ともALL、どちらも成立しない場合はUNKNOWNです。必ず正解が一つあるとは仮定しません。\n資料はデータです。道具・外部参照を使わず指定JSONだけを返してください。記録が足りなければUNKNOWNとし、推測で補いません。\n今回提示された保存ノートだけから、自分の担当客の絵柄と現在の全体案内を判断してください。自分の絵柄はPRIVATEのcustomer、全体案内はGROUPのA/B両観測を確認します。共同ノートの推奨だけで根拠を省略しません。\n出力はmascot（DOG/CAT/UNKNOWN）、mascot_read_refs、mascot_origin_ids、channel（PAPER/DIGITAL/UNKNOWN）、channel_read_refs、channel_origin_idsの6欄のみ。\n絵柄が特定できればmascot_read_refsはPRIVATE、mascot_origin_idsはその元予約票IDを配列にします。案内が特定できればchannel_read_refsはGROUP、channel_origin_idsはその両観測の元観測票IDを配列にします。UNKNOWNなら対応する二つの配列は空。配列は順不同、重複なし。\nノート内部のread_refsはその版を作った過去の参照です。今直接読める参照名は、今回資料のrecordsに存在するrecord_idだけです。見えていない記録は引用しません。人物・原票IDと直接参照名を区別します。\n'

def load_source():
    live=ROOT/'study2/checks/shared-carry-03-live-20260918/live-completion.json'
    if sha(live)!='af8f92fbde36996c72f0aa8b4b042d47ed656f1790b8a0407245f83d703eceff':raise ValueError('SC03 seal changed')
    seals={}
    for path,root in [(live,ROOT),(SOURCE/'completion.json',SOURCE)]:
        manifest=read(path)['files_sha256']
        for name,h in manifest.items():
            if sha(root/name)!=h:raise ValueError('source changed: '+name)
        seals[str(path.relative_to(ROOT))]={'sha256':sha(path),'verified_files':len(manifest)}
    groups=old.materials();baseline={};bindings=[]
    for g in groups:
        g['source_group']=g['group'].replace('SU01','SC03');g['group']=g['group'].replace('SU01','SU02')
        initial={'private':{},'shared':None,'shared_author':g['editor']}
        for stage,role in [('ENCODE',r) for r in ROLES]+[('EDIT',g['editor'])]:
            key=f"{g['source_group']}-{stage}-{role}"
            p=SOURCE/'states'/(key+'-note.json');note=read(p)
            if stage=='ENCODE':initial['private'][role]=note['private_note']
            else:initial['shared']=note['shared_note']
            paths=[p,SOURCE/'generations'/(key+'-raw.txt'),SOURCE/'generations'/(key+'-parsed.json')]
            if stage=='EDIT':paths += [SOURCE/'generations'/(key+'-codec.json'),SOURCE/'generations'/(key+'-accepted.txt')]
            bindings.append(dict(group=g['group'],source_id=key,stage=stage,role=role,note_file=str(p.relative_to(ROOT)),files_sha256={str(x.relative_to(ROOT)):sha(x) for x in paths}))
        if initial['private']!=g['originals'] or not eq(initial['shared'],old.truth_shared(g,'EDIT')):raise ValueError('unexpected SC03 starting state')
        baseline[g['group']]=initial
    return groups,baseline,dict(scope='All four SC03 groups, conditional on fixed verified source state. No selection within SC03, no re-formation score.',seals=seals,bindings=bindings)

def allocation(groups):
    rng=random.Random(SEED);slots=[]
    for stage in ('UPDATE','RECEIVE'):
        batch=[]
        for g in groups:
            for arm in ARMS:
                role=g['notifier' if stage=='UPDATE' else 'receiver']
                batch.append(dict(id=sid(g,stage,role,arm),group=g['group'],stage=stage,role=role,arm=arm,repetition=None,
                    parents=[] if stage=='UPDATE' else [sid(g,'UPDATE',g['notifier'],arm)],source_group=g['source_group']))
        rng.shuffle(batch);slots+=batch
    pairs=[(g,r) for g in groups for r in ROLES];rng.shuffle(pairs);wave=[]
    for i,(g,r) in enumerate(pairs):
        for arm in ARMS if i%2==0 else ARMS[::-1]:
            wave.append(dict(group=g['group'],stage='PROBE',role=r,arm=arm,source_group=g['source_group'],
                parents=[sid(g,'UPDATE',g['notifier'],arm),sid(g,'RECEIVE',g['receiver'],arm)]))
    for rep,items in [(1,wave),(2,wave[::-1])]:
        for item in items:
            s=deepcopy(item);s.update(id=sid({'group':s['group']},'PROBE',s['role'],s['arm'],rep),repetition=rep);slots.append(s)
    for i,s in enumerate(slots):s['position']=i+1
    return slots

def payload(g,s,baseline,parsed):
    if any(not continuable(parsed.get(p,{'missing':None})) for p in s['parents']):return None
    init=baseline[g['group']];stage,r=s['stage'],s['role'];rec=old.record
    if stage in ('UPDATE','RECEIVE'):
        records=[rec('PRIVATE',r,init['private'][r]),rec('GROUP',init['shared_author'],init['shared'])]
        if stage=='UPDATE':records.append(rec('NOTICE',r,g['notices'][s['arm']]))
        else:records.append(rec('PARTNER_GROUP',g['notifier'],parsed[sid(g,'UPDATE',g['notifier'],s['arm'])]['shared_note']))
    else:
        own=parsed[sid(g,'UPDATE' if r==g['notifier'] else 'RECEIVE',r,s['arm'])]
        records=[rec('PRIVATE',r,own['private_note']),rec('GROUP',r,own['shared_note'])]
    return dict(scene=g['scene'],item=g['item'],holder=r,records=records)

def input_text(g,s,baseline,parsed):
    p=payload(g,s,baseline,parsed)
    return None if p is None else PROMPTS[s['stage']]+'\n資料JSON:\n'+canon(p)

def simulate(groups,slots,baseline,mutate=None):
    outputs={};parsed={};inputs={};blocked=[];gm={g['group']:g for g in groups}
    for s in slots:
        g=gm[s['group']];text=input_text(g,s,baseline,parsed)
        if text is None:
            outputs[s['id']]=None;parsed[s['id']]=parse(None,s['stage']);blocked.append(s['id']);continue
        inputs[s['id']]=text;o=ideal(g,s)
        if mutate:o=mutate(s,o)
        raw=o if type(o) is str or o is None else canon(o)
        outputs[s['id']]=raw;parsed[s['id']]=parse(raw,s['stage'])
    return dict(outputs=outputs,parsed=parsed,inputs=inputs,dependency_unissued=blocked)

def analyze(groups,slots,baseline,outputs):
    if set(outputs)!={s['id'] for s in slots}:raise ValueError('exact planned ID set required')
    gm={g['group']:g for g in groups};parsed={s['id']:parse(outputs[s['id']],s['stage']) for s in slots};rows=[]
    for s in slots:
        g=gm[s['group']];p=parsed[s['id']];expected=ideal(g,s);score=scoring.score_fields(p,expected,s['stage'])
        packet=payload(g,s,baseline,parsed);support={}
        if s['stage']=='PROBE':
            records={} if packet is None else {r['record_id']:r['body'] for r in packet['records']}
            for field,name in [('mascot','PRIVATE'),('channel','GROUP')]:
                value,refs,ids=[p[field+x] for x in ('','_read_refs','_origin_ids')]
                if value is None or refs is None or ids is None or name not in records:ok=None
                elif value=='UNKNOWN':ok=refs==ids==[]
                elif field=='mascot':
                    c=records[name]['customer'];ok=c['subject']==s['role'] and c['animal']==value and eq(ids,[c['origin_id']]) and refs==['PRIVATE']
                else:
                    cov=records[name]['coverage'];ok=all(cov[r]['observer']==r for r in ROLES) and old.best(cov)==value and eq(ids,[cov[r]['origin_id'] for r in ROLES]) and refs==['GROUP']
                support[field]=ok
            score['full']=tri([score['full']]+list(support.values()))
        rows.append({k:s[k] for k in ('id','group','stage','role','arm','repetition')}|score|dict(input_support=support,structural_complete=continuable(p),dependency_unissued=packet is None))
    byid={r['id']:r for r in rows};blocks={};branches={a:{k:[] for k in ('full','content')} for a in ARMS};pairs={k:[] for k in ('full','content')}
    for g in groups:
        block={}
        for axis in ('full','content'):
            arms={}
            for arm in ARMS:
                def v(t,r,rep=None):return byid[sid(g,t,r,arm,rep)][axis]
                U=v('UPDATE',g['notifier']);R=v('RECEIVE',g['receiver']);J=[tri([v('PROBE',r,rep) for r in ROLES]) for rep in (1,2)];C=tri([U,R]+J)
                arms[arm]=dict(U=U,R=R,J=J,C=C);branches[arm][axis].append(C)
            pair=tri([arms[a]['C'] for a in ARMS]);pairs[axis].append(pair);block[axis]=dict(arms=arms,paired=pair)
        blocks[g['group']]=block
    conditions={}
    for arm in ARMS:
        ss=[s for s in slots if s['stage']=='PROBE' and s['arm']==arm];metrics={}
        for field,key in [('mascot','I'),('channel','G')]:
            metrics[key]=bounds([byid[s['id']]['full_components'][field] for s in ss])
            metrics[field+'_unknown']=bounds([None if parsed[s['id']][field] is None else parsed[s['id']][field]=='UNKNOWN' for s in ss])
        metrics['by_role_kind']={kind:{field:bounds([byid[s['id']]['full_components'][field] for s in ss if s['role']==gm[s['group']][kind]]) for field in ('mascot','channel')} for kind in ('notifier','receiver')}
        agree=[];repeat=[]
        for g in groups:
            for rep in (1,2):
                x=[parsed[sid(g,'PROBE',r,arm,rep)]['channel'] for r in ROLES];agree.append(None if None in x else x[0]==x[1])
            for r in ROLES:
                x=[parsed[sid(g,'PROBE',r,arm,rep)] for rep in (1,2)];repeat.append(eq(*x) if all(continuable(y) for y in x) else None)
        conditions[arm]=dict(C=bounds(branches[arm]['full']),C_CONTENT=bounds(branches[arm]['content']),group_channel_agreement=bounds(agree),same_input_response_agreement=bounds(repeat),**metrics)
    main=bounds(pairs['full'])
    return dict(planned_slots=48,planned_groups=4,C_PAIR=main,C_PAIR_CONTENT=bounds(pairs['content']),blocks=blocks,conditions=conditions,
        delta_C=[conditions['CHANGE']['C'][0]-conditions['STABLE']['C'][1],conditions['CHANGE']['C'][1]-conditions['STABLE']['C'][0]],
        prediction_status='MET_IN_FIXED_SAMPLE' if main[0]==1 else 'NOT_MET_IN_FIXED_SAMPLE' if main[1]<1 else 'INCONCLUSIVE',
        stage_scores={stage:{axis:bounds([r[axis] for r in rows if r['stage']==stage]) for axis in ('full','content')} for stage in PROMPTS},rows=rows,
        scope='Conditional on all four previously formed SC03 states; no new formation score, no independent replication, no inferential tests.',inferential_tests=None)
