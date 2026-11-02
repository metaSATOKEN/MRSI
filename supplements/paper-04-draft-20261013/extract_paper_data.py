"""Extract existing, frozen results for Paper 4; no model calls or scoring changes."""
from pathlib import Path
import json, hashlib, zipfile, copy
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'papers/paper-04'
AUDIT = Path(__file__).resolve().parent
RUNS = {
 'TB01': 'three-role-boundary-01-20261013/attempt-02-complete',
 'TVR01': 'three-role-vote-repeat-01-20261013',
 'TCV01': 'three-role-comparison-vote-01-20261013',
 'TCV02': 'three-role-comparison-vote-02-20261013',
 'TAR01': 'three-role-approval-readout-01-20261013',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n')
def collect():
 data={'version':'0.1','date':'2026-10-13','purpose':'Manuscript extraction of existing results; not new model evidence.', 'runs':{},'sources':{}}
 examples={'selection':'Post-result explanatory examples. TB01: entire failed higher-offer path plus the corresponding second-replicate C vote and readout; TAR01: all six N01/A readouts.', 'runs':{}}
 for name, folder in RUNS.items():
  p=ROOT/'study2/results'/folder; agg=p/'reaggregated.json'; obj=json.loads(agg.read_text()); r=obj['report']
  zp=next(p.glob('*.zip')); assert sha(zp)==obj['archive_sha256']
  for f in sorted(p.glob('*.json')):data['sources'][str(f.relative_to(ROOT))]=sha(f)
  data['sources'][str(zp.relative_to(ROOT))]=sha(zp)
  summary=copy.deepcopy(r)
  for key in ['by_slot','paths','triad_replicates','by_input','triplets','case_replicates']:
   summary.pop(key,None)
  if 'paired' in summary:summary['paired'].pop('pairs',None)
  costs={}; records=[]; case_inputs={}
  with zipfile.ZipFile(zp) as z:
   design=json.loads(z.read('frozen/design.json')); model=design.get('model')
   for s in r['by_slot']:
    sid=s['id']; prefix='responses/'+sid+'/'
    inp=json.loads(z.read(prefix+'input.json')); ans=z.read(prefix+'answer.txt').decode(); resp=json.loads(z.read(prefix+'response.json'))
    assert json.loads(ans)==s['score']['answer']
    assert s['score']['normalization']['status']=='UNCHANGED'
    group=s.get('arm') or s['stage']; c=costs.setdefault(group,{'responses':0,'output_tokens':0,'answer_bytes':0,'generation_seconds':0.0})
    c['responses']+=1;c['output_tokens']+=len(resp['output_token_ids']);c['answer_bytes']+=len(ans.encode());c['generation_seconds']+=resp['generation_seconds']
    if s['stage'] in ('VOTE','READ'):case_inputs.setdefault(s['case'], json.loads(next(m['content'] for m in inp['messages'] if m['role']=='user')))
    take=(name=='TB01' and s['case']=='T02' and s.get('branch')=='HIGHER' and (s['repeat']==1 or (s['role']=='C' and (s['stage']=='VOTE' or s.get('snapshot')=='THREE_RECEIVED')))) or (name=='TAR01' and s['case']=='N01' and s['role']=='A')
    if take:records.append({'slot':{k:v for k,v in s.items() if k!='score'},'input':inp,'payload':json.loads(next(m['content'] for m in inp['messages'] if m['role']=='user')),'raw_answer':ans,'parsed_answer':json.loads(ans),'metrics':s['score']['metrics'],'archive':str(zp.relative_to(ROOT)),'archive_members':{'input':prefix+'input.json','answer':prefix+'answer.txt'}})
   assert sum(c['output_tokens'] for c in costs.values())==r['output_tokens']
   assert abs(sum(c['generation_seconds'] for c in costs.values())-r['generation_seconds'])<1e-7
  data['runs'][name]={'source_directory':str(p.relative_to(ROOT)),'summary':summary,'model':model,'costs_from_responses':costs,'case_inputs':case_inputs}
  if records:examples['runs'][name]=records
  if name=='TAR01': data['runs'][name]['post_result_supplement']=json.loads((p/'supplementary-analysis.json').read_text())
 data['completed_responses_inventory']=sum(v['summary']['attempted_generations'] for v in data['runs'].values())
 assert data['completed_responses_inventory']==459
 return data,examples
if __name__=='__main__':
 d,e=collect();write(OUT/'paper-data-v0.1-2026-10-13.json',d);write(OUT/'evidence-extract-v0.1-2026-10-13.json',e)
 print(json.dumps({'completed_responses_inventory':d['completed_responses_inventory'],'immutable_result_files':len(d['sources']),'examples':{k:len(v) for k,v in e['runs'].items()}}))
