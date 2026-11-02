"""Offline manuscript checks. Recompute field truth from inputs, not scorer imports."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import hashlib, json, re, zipfile
import extract_paper_data as extract
ROOT=extract.ROOT; OUT=extract.OUT; AUDIT=extract.AUDIT
checks=[]
def check(ok, label):
    if not ok: raise AssertionError(label)
    checks.append(label)
def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    d,e=extract.collect()
    check(d==read(OUT/'paper-data-v0.1-2026-10-13.json'),'paper-data reproducible')
    check(e==read(OUT/'evidence-extract-v0.1-2026-10-13.json'),'evidence extracts reproducible')
    for p,h in d['sources'].items():check(digest(ROOT/p)==h,'source '+p)
    guard=read(ROOT/'throughline/audits/paper-04-scope-20261013/evidence-check.json')['immutable_evidence_sha256']
    for p,h in guard.items():check(digest(ROOT/p)==h,'prior fixed evidence '+p)
    models=[]; metrics=Counter(); failures={}
    for name,folder in extract.RUNS.items():
        p=ROOT/'study2/results'/folder; obj=read(p/'reaggregated.json'); report=obj['report']; models.append(d['runs'][name]['model'])
        with zipfile.ZipFile(next(p.glob('*.zip'))) as z:
            for slot in report['by_slot']:
                sid=slot['id']; prefix='responses/'+sid+'/'
                input_doc=json.loads(z.read(prefix+'input.json'))
                data=json.loads(next(m['content'] for m in input_doc['messages'] if m['role']=='user'))
                answer=json.loads(z.read(prefix+'answer.txt')); role=data['holder']
                obs=[x for x in data['experiences'] if x['owner']==role]
                q={m:40*Fraction(sum(x['observed'][m]['success'] for x in obs),sum(x['observed'][m]['trials'] for x in obs)) for m in ['PAPER','DIGITAL']}
                expected_own=max(q,key=q.get); ids=[x['id'] for x in obs]
                got=answer['own']; calc={'own_holder':got['holder']==role,'own_recommendation':got['recommendation']==expected_own,'own_sources':len(got['evidence_ids'])==len(ids) and set(got['evidence_ids'])==set(ids)}
                if slot['stage']=='VOTE':
                    candidates=data['candidates']; totals={}
                    for c in candidates:
                        total=0
                        for r,m in c['assignment'].items():
                            rr=[x for x in data['experiences'] if x['owner']==r]
                            total+=40*Fraction(sum(x['observed'][m]['success'] for x in rr),sum(x['observed'][m]['trials'] for x in rr))
                        check(total==c['expected_total'],sid+' supplied total '+c['candidate_id']);totals[c['candidate_id']]=total
                    cid=data['proposal']['candidate_id']; other=next(c for c in totals if c!=cid); higher=totals[cid]>totals[other]
                    expected_vote={'proposal_id':data['proposal']['proposal_id'],'decision':'ACCEPT' if higher else 'HOLD'}
                    calc['vote']=answer['vote']==expected_vote
                    if slot.get('arm')=='COMPARE':
                        check(answer['comparison']=={'candidate_id':cid,'other_candidate_id':other,'relation':'HIGHER' if higher else 'LOWER'},sid+' comparison')
                elif slot['stage']=='READ':
                    receipts={r['sender']:r for r in data['receipts']};states={}
                    for r in 'ABC':
                        rec=receipts.get(r)
                        states[r]='MISSING' if rec is None else 'WRONG_PROPOSAL' if rec['proposal_id']!=data['proposal']['proposal_id'] else rec['decision']
                    agreed=all(x=='ACCEPT' for x in states.values());proposal=next(c for c in data['candidates'] if c['candidate_id']==data['proposal']['candidate_id'])
                    calc.update(approval_state=answer['approval_state']==states,agreement=answer['agreement']==('AGREED' if agreed else 'PENDING'),execution=answer['joint_action']==(proposal['assignment'][role] if agreed else 'HOLD'))
                stored=slot['score']['metrics']
                for key,val in calc.items():
                    check(stored[key] is val,sid+' '+key);metrics[(name,key,'correct' if val else 'incorrect')]+=1
                check(slot['score']['strict'] is all(calc.values()),sid+' strict')
                if not all(calc.values()):failures.setdefault(name,[]).append(sid)
    check(all(m==models[0] for m in models),'all five model configurations identical')
    check({n:len(v) for n,v in failures.items()}=={'TB01':1,'TVR01':2,'TCV01':2,'TAR01':1},'all failed response locations')
    text=(OUT/'manuscript-ja-v0.1-2026-10-13.md').read_text()
    check('126/126' in text and metrics['TB01','own_recommendation','correct']==126,'table6 own')
    check(metrics['TB01','vote','correct']==35 and metrics['TB01','execution','correct']==72,'table6 vote/read')
    check(metrics['TAR01','approval_state','correct']==53 and metrics['TAR01','execution','correct']==54,'table7 state/action')
    for name in ('TCV01','TCV02'):
        costs=d['runs'][name]['costs_from_responses']
        line=f"| {'既使用3材料' if name=='TCV01' else '新3材料'} | {costs['DIRECT']['output_tokens']:,} | {costs['COMPARE']['output_tokens']:,} | {costs['DIRECT']['generation_seconds']:.3f} | {costs['COMPARE']['generation_seconds']:.3f} |"
        check(line in text,'table10 '+name)
        for rep in (1,2,3):
            a=d['runs'][name]['summary']['by_arm'];values=[a[x]['by_repeat'][str(rep)]['strict']['correct'] for x in ('DIRECT','COMPARE')]
            check(values==([16,18] if name=='TCV01' and rep==1 else [18,18]),'table9 '+name+str(rep))
    for run in ('TB01','TCV02'):
        for cid,inp in d['runs'][run]['case_inputs'].items():
            values=[]
            for r in 'ABC':
                rr=[x for x in inp['experiences'] if x['owner']==r]
                values.append(','.join(str(sum(x['observed'][m]['success'] for x in rr)) for m in ('PAPER','DIGITAL')))
            ordered=sorted(inp['candidates'],key=lambda c:c['expected_total'],reverse=True)
            desc=lambda c:'／'.join('紙' if c['assignment'][r]=='PAPER' else 'デジタル' for r in 'ABC')+'：'+str(c['expected_total'])
            line='| '+cid+' | '+' | '.join(values)+' | '+' | '.join(map(desc,ordered))+' |'
            check(line in text,'tableA2 '+cid)
    json_example=json.loads(re.search(r'```json\n(.*?)\n```',text,re.S).group(1))
    tar={v['slot']['id']:v for v in e['runs']['TAR01']}
    fail=tar['TAR01-N01-A-R1-MISSING'];check(json_example==fail['parsed_answer'],'verbatim JSON values')
    for rep in (1,2):
        own=[]
        for arm in ('MISSING','HOLD','ACCEPT'):
            item=tar[f'TAR01-N01-A-R{rep}-{arm}'];ans=item['parsed_answer'];own.append(ans['own']);
            check(ans['approval_state']['A']==('HOLD' if rep==1 and arm=='MISSING' else arm),'table8 focal state')
            check(ans['joint_action']==('PAPER' if arm=='ACCEPT' else 'HOLD'),'table8 action')
        check(own[0]==own[1]==own[2],'table8 own fixed')
    check(fail['input']['messages']==tar['TAR01-N01-A-R2-MISSING']['input']['messages'],'same repeated prompt messages')
    check(fail['input']['prepared']==tar['TAR01-N01-A-R2-MISSING']['input']['prepared'],'same repeated token binding')
    check(set(map(int,re.findall(r'^［(\d+)］',text,re.M)))==set(range(1,11)),'bibliography 1..10')
    check(len(re.findall(r'^```mermaid$',text,re.M))==2,'two inline figures')
    for p in OUT.glob('*.md'):
        if p.name.startswith('paper-04-scope'):continue
        content=p.read_text();check(content.count('```')%2==0,'balanced fences '+p.name)
        for link in re.findall(r'\]\(([^)]+)\)',content):
            if re.match(r'^(https?://|mailto:|#)',link):continue
            check((p.parent/link.split('#')[0]).exists(),'link '+p.name+' '+link)
    baseline=AUDIT/'before/throughline/audits/ledger-2026-10.md'
    check((ROOT/'throughline/audits/ledger-2026-10.md').read_bytes().startswith(baseline.read_bytes()),'ledger append-only')
    result={'status':'PASS','checks':len(checks),'scope':'Existing raw answers, field truth, paper extraction, specified tables, exact example values, links, frozen evidence. No new model generation. Literature checked separately against primary documents.','failed_response_ids':failures,'check_labels':checks}
    extract.write(AUDIT/'verification.json',result)
    print(json.dumps({'status':'PASS','checks':len(checks),'failed_response_counts':{k:len(v) for k,v in failures.items()}},ensure_ascii=False))
if __name__=='__main__':main()
