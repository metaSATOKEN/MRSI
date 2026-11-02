"""Offline manuscript-to-frozen-evidence checks. No inference or rescoring."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
PAPER = ROOT / 'papers/paper-02'
TEXT = (PAPER / 'manuscript-ja-v0.3-2026-09-27.md').read_text()
PLAIN = TEXT.replace('**', '')
checks = []


def check(label, actual, expected):
    checks.append({'check': label, 'actual': actual, 'expected': expected,
                   'pass': actual == expected})


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


sources = read(AUDIT / 'evidence-sources.json')
reports = {s['trial']: read(ROOT / s['aggregate'])['report'] for s in sources}

rs, svr = reports['RS01'], reports['SVR01']
check('RS01 main direct/extract/rule',
      [rs['methods'][x]['main']['correct'] for x in ['DIRECT', 'EXTRACT', 'RULE']], [11, 24, 15])
check('RS01 main sample denominators',
      [rs['methods'][x]['main']['n'] for x in ['DIRECT', 'EXTRACT', 'RULE']], [24, 24, 24])
check('RS01 extraction main + boundaries',
      rs['extraction_exact']['main']['correct'] + sum(x['correct'] for x in rs['extraction_exact']['boundary'].values()), 32)
check('Table 6 RS01', '| 読出し分離：主12材料×2反復 | 11/24 | 24/24 | 15/24 |' in PLAIN, True)
check('SVR01 main direct/extract', [svr['methods'][x]['main']['correct'] for x in ['DIRECT', 'EXTRACT']], [11, 32])
check('SVR01 stale note/latest', [svr['methods']['EXTRACT']['stale']['correct'], svr['latest_channel']['EXTRACT']['STALE']['correct']], [20, 4])
check('Table 6 SVR01', '| 実保存読出し：最新16入力×2反復 | 11/32 | 32/32 | 実施せず |' in PLAIN, True)

orr = reports['OR01']
for arm, name, expected in [('G0P0','なし',[32,25,28,25]), ('G1P0','共同のみ',[32,36,36,32]),
                             ('G0P1','本人のみ',[36,25,28,25]), ('G1P1','両方',[36,36,36,36])]:
    comp = orr['components'][arm]
    values = [sum(comp[s]['update']['private_observation_exact']['correct'] for s in ['REPAIR','GUARD']),
              sum(comp[s]['update']['shared_latest_exact']['correct'] for s in ['REPAIR','GUARD']),
              sum(comp[s]['read']['channel_latest']['correct'] for s in ['REPAIR','GUARD']),
              sum(comp[s]['end_to_end_exact']['correct'] for s in ['REPAIR','GUARD'])]
    check('OR01 '+arm, values, expected)
    check('Table 7 '+name, ('| '+name+' | '+' | '.join(f'{v}/36' for v in values)+' |') in PLAIN, True)
check('OR01 actual calls', orr['attempted_generations'], 91)
check('OR01 logical reads', orr['logical_reads'], 144)

for sid, bad, rows in [('SX01',17,24), ('SX02',23,32)]:
    r = reports[sid]; comp = r['components']
    check(sid+' full paths', r['path'], {'correct':16,'incorrect':0,'unresolved':0,'n':16})
    check(sid+' bad proposals', sum(comp[s]['proposal']['joint']['incorrect'] for s in ['SELF','EXCHANGE','DELAY']), bad)
    check(sid+' saved states', sum(comp[s]['joint']['correct'] for s in ['SELF','EXCHANGE','DELAY']), 96)
    check(sid+' retained customer', sum(comp[s]['customer']['correct'] for s in ['SELF','EXCHANGE','DELAY']), 96)
    src = next(x for x in sources if x['trial']==sid)
    diagnostic = read(ROOT / src['audit'] / 'proposal-diagnostics.json')
    check(sid+' proposal row locations', diagnostic['mismatched_rows'], rows)
    title = '一巡目' if sid == 'SX01' else '二巡目'
    check('Table 8 '+sid, f'| {title} | {bad}/96 | {rows}欄 | 96/96 | 16/16 |' in PLAIN, True)

ru = reports['RU01']
check('RU01 all conditions', [ru['by_arm'][a]['joint']['correct'] for a in ['P0G0','P1G0','P0G1','P1G1']], [32]*4)
check('RU01 full paths',ru['path']['correct'],16)
exru = read(ROOT / 'throughline/audits/role-shared-use-01-result-20260925/example.json')
check('RU01 example identity',exru['run'],'RU01-C07-R1')
check('RU01 example actions',[[c['roles'][r]['actions']['card_animal'] for r in ['A','B']]+[c['roles']['A']['actions']['channel']] for c in exru['conditions']],
      [['DOG','CAT','PAPER'],['CAT','DOG','PAPER'],['DOG','CAT','DIGITAL'],['CAT','DOG','DIGITAL']])

cu = reports['CU01']
check('CU01 target change / nontarget / delay', [cu['customer_subsets'][k]['correct'] for k in ['target_change','non_target_preserved','target_after_delay']], [16,32,2])
check('CU01 full paths',cu['path'],{'correct':2,'incorrect':14,'unresolved':0,'n':16})
check('CU01 closure',cu['criterion_status'],'NOT_MET')
check('CU01 rollback',cu['rollback']['counts'],{'ROLLED_BACK_TO_INITIAL':14,'KEPT_LATEST':2})
check('CU01 read fidelity', [cu['components']['READ'][k]['correct'] for k in ['subject_note','animal_note','four_note_exact','channel_note']], [32]*4)
check('CU01 read latest',cu['components']['READ']['joint']['correct'],18)
exc = read(ROOT / 'throughline/audits/customer-update-01-result-20260926/example.json')
check('CU01 worked example',exc['run']['id'],'CU01-C06-R1')
check('CU01 change saved',exc['stages']['CHANGE']['saved']['private_note']['customer'],exc['new_customer'])
check('CU01 delay saved',exc['stages']['DELAY']['saved']['private_note']['customer'],exc['original_customer'])
answer = exc['stages']['READ']['answer_text']
answer = answer[8:-4] if answer.startswith('```json\n') else answer
check('CU01 raw read excerpt',json.loads(answer)['customer'],{'subject':'A','animal':'CAT'})
for value in ['K5E1ED87EFA479493','K0D9B80C5A23D1363','{"customer":{"subject":"A","animal":"CAT"}}']:
    check('CU01 exact manuscript excerpt '+value,value in TEXT,True)
diagcu = read(ROOT / 'throughline/audits/customer-update-01-result-20260926/proposal-diagnostics.json')
rows = diagcu['rolled_back_exact_customer_rows']
check('CU01 complete rollback traces',len(rows),14)
check('CU01 old row preserved through all failures',all(
    x['proposal']==x['saved']==x['late_notice'] and x['input_current']['revision']>x['saved']['revision']
    and x['read_customer']['animal']==x['saved']['animal'] for x in rows),True)

accounting=[('RS01','読出し分離',0,96,0),('SVR01','実保存読出し',0,104,0),
            ('OR01','保存先比較',36,55,20),('SX01','一巡目',96,32,54),
            ('RU01','用途分離',0,128,125),('SX02','二巡目',96,32,79),
            ('CU01','希望更新診断',64,32,75)]
for sid, label, updates, reads, wraps in accounting:
    r=reports[sid]; perf=r['performance']
    actual_updates=perf.get('UPDATE',{}).get('responses',0)
    if sid=='RU01': actual_reads=perf['responses']
    elif 'READ' in perf: actual_reads=perf['READ']['responses']
    else: actual_reads=sum(x['responses'] for x in perf.values())
    norm=r.get('normalization',{})
    actual_wraps=norm.get('status',{}).get('UNWRAPPED',0) if sid=='RU01' else sum(v.get('status',{}).get('UNWRAPPED',0) for v in norm.values())
    check('Appendix B counts '+sid,[actual_updates,actual_reads,actual_wraps],[updates,reads,wraps])
    check('EOS '+sid,r.get('status_counts',r.get('physical_status_counts')),{'EOS':updates+reads})
    read_text=f'{reads}（144条件分で共用）' if sid=='OR01' else str(reads)
    check('Appendix B manuscript '+sid,f'| {label} | {updates} | {read_text} | {updates+reads} | {wraps} |' in PLAIN,True)

envs = read(AUDIT/'source-environments.json')
for src in sources:
    sid=src['trial']; design=read(ROOT/src['design']); model=design['model']
    check(sid+' revision',model['revision'],'fc05daec18b0a78c049392ed2e771dde82bdf654')
    check(sid+' model / mode',[model['model'],model['dtype'],model['attention'],model['enable_thinking']],['Qwen/Qwen3.5-27B','bfloat16','sdpa',False])
    check(sid+' generation',[model['generation'][k] for k in ['temperature','top_p','top_k','repetition_penalty','max_new_tokens']],[0.7,0.8,20,1.0,2048])
    check(sid+' environment',[envs[sid]['python'],envs[sid]['packages']['torch'],envs[sid]['packages']['transformers'],envs[sid]['packages']['accelerate']],['3.13.15','2.11.0+cu128','5.17.0','1.15.0'])
    check(sid+' raw ZIP unchanged',sha(ROOT/src['archive']),src['archive_sha256'])

# Frozen inputs and first report must stay intact; only navigation may change.
nav={'README.md','study2/README.md','throughline/PROJECT.md','papers/paper-02/README.md'}
anchors=read(AUDIT/'anchors-before.json')
changed=[p for p,h in anchors.items() if p not in nav and sha(ROOT/p)!=h]
check('frozen input changes',changed,[])
ledger_before=read(AUDIT/'ledger-before.json')
ledger=(ROOT/'throughline/audits/ledger-2026-09.md').read_bytes()
check('old ledger prefix',hashlib.sha256(ledger[:ledger_before['bytes']]).hexdigest(),ledger_before['sha256'])

docs=[PAPER/'manuscript-ja-v0.3-2026-09-27.md',PAPER/'evidence-index-v0.3-2026-09-27.md',PAPER/'revision-notes-v0.3-2026-09-27.md',PAPER/'README.md',PAPER/'related-work-review-v0.1-2026-09-27.md']
missing=[];local_links=0
for doc in docs:
    txt=doc.read_text()
    for target in re.findall(r'\]\(([^)]+)\)',txt):
        if target.startswith(('https://','http://','mailto:','#')):continue
        path=(doc.parent/target.split('#')[0]).resolve();local_links+=1
        if path==AUDIT/'verification.json':continue  # Written below in this invocation.
        if not path.exists():missing.append({'file':doc.name,'target':target})
    check('balanced fences '+doc.name,len(re.findall(r'^```',txt,re.M))%2,0)
    check('no local absolute paths '+doc.name,'/Users/' in txt,False)
check('broken local links',missing,[])
check('main section count',len(re.findall(r'^## [1-9]\. ',TEXT,re.M)),9)
check('tables 1 through 10',re.findall(r'^\*\*表(\d+)\.',TEXT,re.M),[str(x) for x in range(1,11)])
check('figure captions',re.findall(r'^\*\*図(\d+)\.',TEXT,re.M),['1','2'])


# Editorial invariants: unchanged empirical tables and methods, plus the newly
# foregrounded within-proposal comparison. These read frozen diagnostics only.
OLD_TEXT = (PAPER/'manuscript-ja-v0.2-2026-09-26.md').read_text()
def section(txt, a, b=None):
    return txt.split(a,1)[1].split(b,1)[0] if b else txt.split(a,1)[1]
def table(txt, n):
    remaining=txt.split('**表'+str(n)+'.',1)[1]
    rows=[]; started=False
    for line in remaining.splitlines():
        if line.startswith('|'):
            rows.append(line);started=True
        elif started:
            break
    return rows
for new,old in [(i,i) for i in range(3,11)]:
    check('unchanged data rows table '+str(new),table(TEXT,new),table(OLD_TEXT,old))
for a,b in [('## 3. 課題とシステム','## 6. 考察'),
            ('## 7. 測定範囲と限界','## 9. データ可用性と申告'),
            ('## 付録A.','## 付録B.')]:
    check('unchanged scientific text '+a,section(TEXT,a,b)==section(OLD_TEXT,a,b),True)
check('title abstract and introduction unchanged',TEXT.split('## 2. 関連研究との位置関係')[0]==OLD_TEXT.split('## 2. 関連研究との位置関係')[0],True)
for a,b in [('## 9. データ可用性と申告','## 参考文献'),('## 付録B.',None)]:
    check('unchanged except S1 link '+a,
          section(TEXT,a,b).replace('evidence-index-v0.3-2026-09-27.md','evidence-index-v0.2-2026-09-26.md')==section(OLD_TEXT,a,b),True)
# All added bibliography URLs must occur in the discussion of related work,
# and must resolve to a version-specific primary arXiv citation.
related=section(TEXT,'## 2. 関連研究との位置関係','## 3. 課題とシステム')
refs=read(AUDIT/'added-bibliography.json')
for ref in refs:
    check('related work source cited '+ref['arxiv'],ref['url'] in related,True)
    check('bibliography title '+ref['arxiv'],ref['title'] in section(TEXT,'## 参考文献','## 付録A.'),True)
check('MemAudit v2 title correct','MemAudit: Auditing Long-Term Agent Memory via Hidden User-State Recovery' in TEXT,True)
check('two MemTrace sources kept distinct',all(x in TEXT for x in ['MemTrace：Deng et al.','MemTrace：Long et al.','2605.28732v1','2606.17328v1']),True)
branches=read(ROOT/'throughline/audits/owner-recency-01-result-20260925/branch-diagnostics.json')
bymethod={a:{r['parent']:r for r in branches if r['arm']==a} for a in ['G0P0','G1P0','G0P1','G1P1']}
check('OR01 same 36 proposals in all branches',len(bymethod['G0P0'])==36 and all(set(x)==set(bymethod['G0P0']) for x in bymethod.values()),True)
private_bad={key for key,r in bymethod['G0P0'].items() if not r['private']}
check('OR01 private failure count',len(private_bad),4)
check('OR01 shared-only correct answer with old private on SAME four',
      all(not bymethod['G1P0'][k]['private'] and bymethod['G1P0'][k]['shared'] and bymethod['G1P0'][k]['channel_latest'] for k in private_bad),True)
check('OR01 private-only repairs SAME four with overlapping shared failure',
      all(bymethod['G0P1'][k]['private'] and not bymethod['G0P1'][k]['shared'] and not bymethod['G0P1'][k]['joint'] for k in private_bad),True)
check('OR01 no joint outcome changes off vs private-only',
      all(bymethod['G0P0'][k]['joint']==bymethod['G0P1'][k]['joint'] for k in bymethod['G0P0']),True)
check('OR01 paired joint successes',sum(r['joint'] for r in bymethod['G0P1'].values()),25)
check('retrospective synthesis marked',all(x in TEXT for x in ['系列全体の取得前仮説ではない','探索を執筆時に統合']),True)
check('CU01 criterion failure remains','目安の全体14/16かつ各7/8を満たさなかった' in TEXT,True)
check('original adaptive selection/protocol account retained',all(x in TEXT for x in ['18材料を再利用','その操作後ノートではなく','生成前に固定して共通適用']),True)
check('no unresolvable pasted-review references',':chatgpt-content-reference' in TEXT,False)
check('evidence index table mapping',all(x in (PAPER/'evidence-index-v0.3-2026-09-27.md').read_text() for x in [
    '| 一巡目（SX01） | 表8・§5.3','| 用途分離（RU01） | 表9・§5.3','| 二巡目（SX02） | 表8・§5.3']),True)

result={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL',
        'checks':checks,'checked_frozen_anchors':len(anchors)-len(nav),'local_links_checked':local_links,
        'new_inference_calls':0,'rescored_research_responses':0,
        'scope':'Existing aggregate and trace checks, manuscript values and links; not independent blind scientific review.',
        'manuscript_sha256':sha(PAPER/'manuscript-ja-v0.3-2026-09-27.md')}
attempt=len(list(AUDIT.glob('verification-attempt-*.json')))+1
(AUDIT/f'verification-attempt-{attempt:02}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(AUDIT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'frozen_anchors':result['checked_frozen_anchors'],
                  'links':local_links,'failures':[x for x in checks if not x['pass']]},ensure_ascii=False))
raise SystemExit(0 if result['status']=='PASS' else 1)
