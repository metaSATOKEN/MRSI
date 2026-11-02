"""Read-only PART2 replay and descriptive interim diagnostics; no model calls."""
from pathlib import Path
from hashlib import sha256
from collections import Counter,defaultdict
import json,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import cross_model_e1_01_main_runtime as main
from aggregate_cross_model_e1_01 import load_payload
OUT=Path(__file__).parent
SOURCE=OUT/'npp-xm01-main-part2-20260925-031619-48c45e34.zip'
if not SOURCE.exists(): SOURCE=ROOT/SOURCE.name
manifest,files=main.read_archive(SOURCE)
payload=load_payload(ROOT/'study2/colab/cross_model_e1_01_main_onecell.py')
part=manifest['part']
assert part=='PART2' and manifest['kind']=='FINAL'
expected={'bundle':payload['bundle'],'partition':payload['partition'],'contract':payload['contracts'][part], 'allocation':payload['partition']['parts'][part]['allocation'],'code':payload['code']}
main.verify_archive_payload(files,expected)
archive=OUT/SOURCE.name
if archive.exists(): assert archive.read_bytes()==SOURCE.read_bytes()
else: shutil.copyfile(SOURCE,archive)
received=OUT/'received'
for name,raw in files.items():
 p=received/name
 if p.exists(): assert p.read_bytes()==raw
 else:
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
old=next(json.loads(raw) for n,raw in files.items() if n.startswith('report-final-'))
assert len(list((received/'responses').glob('*/result.json')))==768
before={n:sha256((received/n).read_bytes()).hexdigest() for n in files}
replay=main.audit_root(received,payload['bundle'],payload['partition'],expected['contract'])
assert all(sha256((received/n).read_bytes()).hexdigest()==before[n] for n in files)
for key in ('part','collection_status','closed_responses','attempted_generations','received_responses','summary','rows','generation_timings'):
 assert replay[key]==old[key],key
(OUT/'replayed-report.json').write_text(json.dumps(replay,ensure_ascii=False,indent=2)+'\n')
slots=expected['allocation']; rows=replay['rows']; by_stage={};errors=defaultdict(Counter); examples=defaultdict(list)
for method in ('REWRITE','SELECT'):
 for stage in ('MERGE','PROBE'):
  selected=[s for s in slots if s['condition']==method and s['stage']==stage]
  r=[rows[s['id']] for s in selected]
  by_stage[method+'|'+stage]={'planned':len(r),'status':dict(Counter(x['status'] for x in r)),
   'strict':main.core.counts(x['score']['strict'] for x in r),'content':main.core.counts(x['score']['content'] for x in r)}
  for s in selected:
   evpath=received/'responses'/s['id']/'evaluation.json'
   if evpath.exists():
    ev=json.loads(evpath.read_bytes())
    for kind in ('shape_errors','ref_errors'):
     es=ev.get(kind,ev.get('score',{}).get(kind,[]))
     for error in es:
      errors[method+'|'+stage+'|'+kind][str(error)]+=1
     if es and len(examples[method+'|'+stage+'|'+kind])<3: examples[method+'|'+stage+'|'+kind].append({'id':s['id'],'errors':es})
response_types=Counter(); probe_details=Counter(); bindings=Counter(); accepted=Counter(); repeat_gate={}
for s in slots:
 folder=received/'responses'/s['id']
 if (folder/'response.json').exists():
  response=json.loads((folder/'response.json').read_bytes());response_types[response['finish_reason']]+=1
 if s['stage']=='MERGE' and rows[s['id']]['gate']=='PASS':accepted[s['condition']]+=1
 if (folder/'evaluation.json').exists():
  ev=json.loads((folder/'evaluation.json').read_bytes())
  if s['stage']=='MERGE' and s['condition']=='SELECT':
   bindings['recorded_bindings']+=len(ev.get('bindings',[]))
 if s['stage']=='PROBE' and rows[s['id']]['gate']=='PASS':
  answer=json.loads((folder/'answer.txt').read_bytes())
  probe_details[s['condition']+'|'+answer['decision']['channel']]+=1
for method in ('REWRITE','SELECT'):
 patterns=Counter()
 for group in expected['partition']['parts'][part]['groups']:
  for role in ('A','B'):
   branch=sorted([s for s in slots if s['condition']==method and s['group']==group and s['role']==role and s['stage']=='MERGE'],key=lambda s:s['replicate'])
   v=[rows[s['id']]['gate']=='PASS' for s in branch]
   patterns['all_pass' if all(v) else 'all_reject' if not any(v) else 'mixed']+=1
 repeat_gate[method]=dict(patterns)
elapsed=sum(json.loads(raw)['elapsed_seconds'] for n,raw in files.items() if n.startswith('windows/') and n.endswith('-end.json'))
timings=replay['generation_timings']; secs=sum(r['seconds'] for r in timings); tokens=sum(r['tokens'] for r in timings)
proof={'zip_sha256':sha256(SOURCE.read_bytes()).hexdigest(),'files_verified':len(files),'archive_matches_distributed_payload':True,
 'all_scores_and_parents_replayed':True,'received_evidence_unchanged':True,'part':part,'materials':32,'replicates':3,
 'closed':replay['closed_responses'],'attempted':replay['attempted_generations'],'received':replay['received_responses'],
 'response_status':replay['summary']['response_status'],'by_stage':by_stage,'errors':{k:dict(v) for k,v in errors.items()},'examples':dict(examples),
 'finish_reasons':dict(response_types),'accepted_memories_and_probes':dict(accepted),'probe_channel_outputs':dict(probe_details),
 'merge_gate_repeat_patterns_material_role_units':repeat_gate,'select_binding_counts':dict(bindings),
 'elapsed_seconds':elapsed,'generation_seconds':secs,'generated_tokens':tokens,'tokens_per_second':tokens/secs,
 'max_allocated_vram_bytes':max(t['peak_vram_bytes'] for t in timings),
 'new_model_calls_during_analysis':0,'part2_received':True}
(OUT/'verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(proof,ensure_ascii=False,indent=2))
