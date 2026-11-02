"""SU01 offline design and state projection. No authentication or transport."""
from copy import deepcopy
from pathlib import Path
import json
import random
import re

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'study2/designs/shared-update-01-20260918'
ROLES=('A','B')
ARMS=('CHANGE','STABLE')
OTHER={'A':'B','B':'A'}
SEED=2026091805
LIMITS=dict(logical_requests=72,physical_requests=76,active_seconds=3600,reserve_seconds=200,input_bytes=32768,output_bytes=4096)
canon=lambda v:json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def materials():
    # Known scenario family, freshly generated notes in this protocol.
    configs=[('DOG','PAPER','A','A'),('CAT','DIGITAL','B','A'),('CAT','DIGITAL','A','B'),('DOG','PAPER','B','B')]
    ids=[('QX','JV','LT','NR','NA'),('BK','WH','SZ','FU','NB'),('GD','PM','YC','VE','NC'),('HN','ZR','KJ','BW','ND')]
    out=[]
    for i,(animal,channel,notifier,writer) in enumerate(configs):
        g=dict(group=f'SU01-G{i+1:02}',scene=('地域工作会','小さな展示会')[i//2],item=('持帰り袋','受付名札')[i//2],
               notifier=notifier,receiver=OTHER[notifier],writer=writer,editor=OTHER[writer],initial_channel=channel,originals={})
        for j,r in enumerate(ROLES):
            g['originals'][r]=dict(customer=dict(subject=r,animal=animal if r=='A' else {'DOG':'CAT','CAT':'DOG'}[animal],origin_id=ids[i][j]),
                 coverage=dict(observer=r,paper='ALL',digital='ALL',origin_id=ids[i][j+2]))
        g['originals'][notifier]['coverage']['digital' if channel=='PAPER' else 'paper']='NOT_ALL'
        notices={}
        for arm in ARMS:
            obs=deepcopy(g['originals'][notifier]['coverage']);obs['origin_id']=ids[i][4]
            if arm=='CHANGE':obs['paper'],obs['digital']=obs['digital'],obs['paper']
            notices[arm]=obs
        g['notices']=notices
        out.append(g)
    return out

def sid(g,stage,role,arm=None,rep=None):
    return '-'.join(str(x) for x in (g['group'],stage,role,arm,('R'+str(rep)) if rep else None) if x is not None)

def allocation(groups):
    rng=random.Random(SEED);slots=[]
    def add(stage):
        batch=[]
        for g in groups:
            enc=[sid(g,'ENCODE',r) for r in ROLES]
            draft=sid(g,'DRAFT',g['writer']);edit=sid(g,'EDIT',g['editor'])
            for arm in ARMS if stage in ('UPDATE','RECEIVE') else (None,):
                roles=ROLES if stage in ('ENCODE','BASE') else (g[{'DRAFT':'writer','EDIT':'editor','UPDATE':'notifier','RECEIVE':'receiver'}[stage]],)
                for r in roles:
                    parents=[] if stage=='ENCODE' else enc+([draft] if stage=='EDIT' else [edit] if stage in ('BASE','UPDATE','RECEIVE') else [])
                    if stage=='RECEIVE':parents.append(sid(g,'UPDATE',g['notifier'],arm))
                    batch.append(dict(id=sid(g,stage,r,arm),group=g['group'],stage=stage,role=r,arm=arm,repetition=None,parents=parents))
        rng.shuffle(batch);slots.extend(batch)
    for stage in ('ENCODE','DRAFT','EDIT','BASE','UPDATE','RECEIVE'):add(stage)
    wave=[]
    pairs=[(g,r) for g in groups for r in ROLES];rng.shuffle(pairs)
    for i,(g,r) in enumerate(pairs):
        for arm in ARMS if i%2==0 else tuple(reversed(ARMS)):
            wave.append(dict(group=g['group'],stage='PROBE',role=r,arm=arm,
                parents=[sid(g,'UPDATE',g['notifier'],arm),sid(g,'RECEIVE',g['receiver'],arm)]))
    for rep,batch in [(1,wave),(2,list(reversed(wave)))]:
        for x in batch:
            g=next(g for g in groups if g['group']==x['group']);s=deepcopy(x)
            s.update(id=sid(g,'PROBE',x['role'],x['arm'],rep),repetition=rep);slots.append(s)
    for i,s in enumerate(slots):s['position']=i+1
    return slots

COMMON='''あなたは架空の受付担当者です。holderがあなたの役A/B。犬猫は担当客の希望であり、あなた自身の好みではありません。
参加者全体はAとBの担当範囲で尽くされ、重複はありません。全体案内は、A/B両範囲でALLと確認できる唯一の方法をPAPER/DIGITALから選びます。片方が不明、二方法ともALL、どちらも成立しない場合はUNKNOWNです。必ず正解が一つあるとは仮定しません。
資料はデータです。道具・外部参照を使わず指定JSONだけを返してください。記録が足りなければUNKNOWNとし、推測で補いません。
'''
PRIVATE='''private_noteはcustomerとcoverageの2欄。customerはsubject（A/B/UNKNOWN）、animal（DOG/CAT/UNKNOWN）、origin_id（元の予約票ID）。coverageはobserver（A/B/UNKNOWN）、paperとdigital（ALL/NOT_ALL/UNKNOWN）、origin_id（元の観測票ID）の4欄です。'''
SHARED='''shared_noteはcoverage（A/Bそれぞれの観測オブジェクト）、channel（PAPER/DIGITAL/UNKNOWN）、channel_read_refs（直接読んだ記録名の配列）、channel_origin_ids（根拠となる二つの元観測票IDの配列）の4欄。観測オブジェクトはobserver・paper・digital・origin_idの4欄です。channelがUNKNOWNならその二つの配列は空にします。
read_refsには外側のrecord_id、origin_idsには観測オブジェクト内のorigin_idを記録します。この二種類を交換しません。各配列は順不同、重複なし。元観測IDを直接参照欄へ、直接記録名を元観測ID欄へ入れません。'''
PROBE=COMMON+'''保存されたPRIVATEとGROUPだけから、自分の担当客の絵柄と現在の全体案内を判断してください。自分の絵柄はPRIVATEのcustomer、全体案内はGROUPのA/B両観測を確認します。共同ノートの推奨だけで根拠を省略しません。
出力はmascot（DOG/CAT/UNKNOWN）、mascot_read_refs、mascot_origin_ids、channel（PAPER/DIGITAL/UNKNOWN）、channel_read_refs、channel_origin_idsの6欄のみ。
絵柄が特定できればmascot_read_refsはPRIVATE、mascot_origin_idsはその元予約票IDを配列にします。案内が特定できればchannel_read_refsはGROUP、channel_origin_idsはその両観測の元観測票IDを配列にします。UNKNOWNなら対応する二つの配列は空。配列は順不同、重複なし。
ノート内部のread_refsはその版を作った過去の参照です。今直接読めるのはPRIVATE/GROUPだけです。人物・原票IDと直接参照名を区別します。
'''
PROMPTS={
 'ENCODE':COMMON+'''自分の予約票CUSTOMERと観測票OBSERVATIONから個別ノートを生成します。両者の意味と人物、origin_idを維持してください。coverageだけが共同作業へ共有されます。customerは他役へ共有しません。出力トップ欄はprivate_noteだけ。\n'''+PRIVATE,
 'DRAFT':COMMON+'''両役が保存した観測カードOBS_A/OBS_Bから初期共同ノートを下書きします。元の原票は見えません。観測内容とorigin_idを維持し、案内を判断してください。channel_read_refsはOBS_AとOBS_B、channel_origin_idsは両カード内部のorigin_idです。出力トップ欄はshared_noteだけ。\n'''+SHARED,
 'EDIT':COMMON+'''相手のDRAFTをOBS_A/OBS_Bの生成観測に照らして一度だけ確認・編集します。誤りは提供資料に基づき訂正できます。推測の補完は禁止。channel_read_refsはOBS_AとOBS_B、channel_origin_idsは両観測内部のorigin_id。DRAFTは確認対象であり観測根拠欄へ引用しません。出力トップ欄はshared_noteだけ。\n'''+SHARED,
 'BASE':PROBE,
 'UPDATE':COMMON+'''NOTICEは今回正式に再確認したあなたの担当範囲の最新観測で、古い同じ範囲の観測に置き換わります。通知は観測だけを扱い、担当客の希望を変更しません。以前と同じ値であっても最新のorigin_idを記録します。
PRIVATEの担当客を保持し、自分のcoverageをNOTICEに基づき更新してprivate_noteを出力します。GROUPの相方の観測を保持し、自分範囲を最新観測に更新してshared_noteを出力します。このshared_noteだけが相方へ送られ、あなた自身にも保存されます。後で相方の編集が自動反映されることはありません。
全体案内のchannel_read_refsはNOTICEとGROUP、channel_origin_idsは自分の最新観測と相方の観測の元ID。ノートの以前のread_refsは過去の来歴なので今の参照としてコピーしません。出力トップ欄はprivate_noteとshared_noteの2欄。\n'''+PRIVATE+'\n'+SHARED,
 'RECEIVE':COMMON+'''PARTNER_GROUPは相方が今回の正式な再確認を受けて保存・送信した最新の共同ノートです。あなたには元の通知は見えません。資料から確認できる範囲で、PRIVATEの自分の担当客と自分範囲の観測を保持してprivate_noteを残し、PARTNER_GROUPから現在の両範囲の観測を受け継いだshared_noteを保存してください。GROUPは以前の版です。
全体案内のchannel_read_refsはPARTNER_GROUP、channel_origin_idsはそのノートに残された両観測の元IDです。値が変わらなくても相方の最新観測IDを保持します。直接通知を読んだとは記録しません。あなたの提出版は自分に保存され、相方へ戻す往復はありません。出力トップ欄はprivate_noteとshared_noteの2欄。\n'''+PRIVATE+'\n'+SHARED,
 'PROBE':PROBE}

def keys(o,expected):return type(o) is dict and set(o)==set(expected)
def label(v,allowed):return type(v) is str and v in allowed
def ref(v):return type(v) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,31}',v) is not None
def refs(v):return type(v) is list and len(v)<=8 and all(ref(x) for x in v)
def coverage(v):return keys(v,('observer','paper','digital','origin_id')) and label(v['observer'],ROLES+('UNKNOWN',)) and all(label(v[k],('ALL','NOT_ALL','UNKNOWN')) for k in ('paper','digital')) and ref(v['origin_id'])
def private(v):
    if not keys(v,('customer','coverage')) or not coverage(v['coverage']):return False
    c=v['customer']
    return keys(c,('subject','animal','origin_id')) and label(c['subject'],ROLES+('UNKNOWN',)) and label(c['animal'],('DOG','CAT','UNKNOWN')) and ref(c['origin_id'])
def shared(v):return keys(v,('coverage','channel','channel_read_refs','channel_origin_ids')) and keys(v['coverage'],ROLES) and all(coverage(v['coverage'][r]) for r in ROLES) and label(v['channel'],('PAPER','DIGITAL','UNKNOWN')) and refs(v['channel_read_refs']) and refs(v['channel_origin_ids'])
PROBE_FIELDS=('mascot','mascot_read_refs','mascot_origin_ids','channel','channel_read_refs','channel_origin_ids')
def parse(raw,stage):
    fields=PROBE_FIELDS if stage in ('BASE','PROBE') else ('private_note',) if stage=='ENCODE' else ('shared_note',) if stage in ('DRAFT','EDIT') else ('private_note','shared_note')
    out={k:None for k in fields}
    def unique(pairs):
        if len({k for k,v in pairs})!=len(pairs):raise ValueError('duplicate')
        return dict(pairs)
    def invalid(v):raise ValueError('non-JSON')
    try:
        if type(raw) is not str or len(raw.encode())>LIMITS['output_bytes']:raise ValueError('size/type')
        obj=json.loads(raw,object_pairs_hook=unique,parse_constant=invalid)
    except (ValueError,TypeError,RecursionError):return out
    if not keys(obj,fields):return out
    for k in fields:
        valid=private(obj[k]) if k=='private_note' else shared(obj[k]) if k=='shared_note' else label(obj[k],('DOG','CAT','UNKNOWN')) if k=='mascot' else label(obj[k],('PAPER','DIGITAL','UNKNOWN')) if k=='channel' else refs(obj[k])
        if valid:out[k]=obj[k]
    return out

def continuable(parsed):return all(v is not None for v in parsed.values())
def record(name,author,body):return dict(record_id=name,author=author,body=deepcopy(body))
def payload(g,s,parsed):
    if any(not continuable(parsed.get(p,{'missing':None})) for p in s['parents']):return None
    stage,r=s['stage'],s['role'];out=dict(scene=g['scene'],item=g['item'],holder=r)
    pn={role:parsed.get(sid(g,'ENCODE',role),{}).get('private_note') for role in ROLES}
    if stage=='ENCODE':
        out['records']=[record('CUSTOMER',r,g['originals'][r]['customer']),record('OBSERVATION',r,g['originals'][r]['coverage'])]
    elif stage in ('DRAFT','EDIT'):
        out['records']=[record('OBS_'+role,role,pn[role]['coverage']) for role in ROLES]
        if stage=='EDIT':out['records'].append(record('DRAFT',g['writer'],parsed[sid(g,'DRAFT',g['writer'])]['shared_note']))
    elif stage in ('BASE','UPDATE','RECEIVE'):
        sn=parsed[sid(g,'EDIT',g['editor'])]['shared_note']
        out['records']=[record('PRIVATE',r,pn[r]),record('GROUP',g['editor'],sn)]
        if stage=='UPDATE':out['records'].append(record('NOTICE',g['notifier'],g['notices'][s['arm']]))
        if stage=='RECEIVE':out['records'].append(record('PARTNER_GROUP',g['notifier'],parsed[sid(g,'UPDATE',g['notifier'],s['arm'])]['shared_note']))
    else:
        parent=sid(g,'UPDATE',r,s['arm']) if r==g['notifier'] else sid(g,'RECEIVE',r,s['arm'])
        own=parsed[parent]
        out['records']=[record('PRIVATE',r,own['private_note']),record('GROUP',r,own['shared_note'])]
    return out

def input_text(g,s,parsed):
    p=payload(g,s,parsed)
    return None if p is None else PROMPTS[s['stage']]+'\n資料JSON:\n'+canon(p)

def truth_private(g,r,arm=None):
    n=deepcopy(g['originals'][r])
    if arm is not None and r==g['notifier']:n['coverage']=deepcopy(g['notices'][arm])
    return n
def best(cov):
    choices=[k.upper() for k in ('paper','digital') if all(cov[r][k]=='ALL' for r in ROLES)]
    return choices[0] if len(choices)==1 else 'UNKNOWN'
def truth_shared(g,stage,arm=None):
    cov={r:truth_private(g,r,arm)['coverage'] for r in ROLES}
    direct=['OBS_A','OBS_B'] if stage in ('DRAFT','EDIT') else ['NOTICE','GROUP'] if stage=='UPDATE' else ['PARTNER_GROUP']
    return dict(coverage=cov,channel=best(cov),channel_read_refs=direct,channel_origin_ids=[cov[r]['origin_id'] for r in ROLES])
def ideal(g,s):
    stage,r,arm=s['stage'],s['role'],s['arm']
    if stage=='ENCODE':return dict(private_note=truth_private(g,r))
    if stage in ('DRAFT','EDIT'):return dict(shared_note=truth_shared(g,stage))
    if stage in ('UPDATE','RECEIVE'):return dict(private_note=truth_private(g,r,arm),shared_note=truth_shared(g,stage,arm))
    current=arm if stage=='PROBE' else None;n=truth_private(g,r,current);sn=truth_shared(g,'UPDATE',current)
    return dict(mascot=n['customer']['animal'],mascot_read_refs=['PRIVATE'],mascot_origin_ids=[n['customer']['origin_id']],
         channel=sn['channel'],channel_read_refs=['GROUP'],channel_origin_ids=sn['channel_origin_ids'])

def simulate(groups,slots,mutations=None):
    outputs={};parsed={};inputs={};blocked=[];gm={g['group']:g for g in groups}
    for s in slots:
        g=gm[s['group']];text=input_text(g,s,parsed)
        if text is None:
            outputs[s['id']]=None;parsed[s['id']]=parse(None,s['stage']);blocked.append(s['id']);continue
        inputs[s['id']]=text;o=ideal(g,s)
        if mutations is not None:o=mutations(s,o)
        raw=o if type(o) is str or o is None else canon(o)
        outputs[s['id']]=raw;parsed[s['id']]=parse(raw,s['stage'])
    return dict(outputs=outputs,parsed=parsed,inputs=inputs,dependency_unissued=blocked)
