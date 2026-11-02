"""Rebuild Paper 4 tables and examples from packaged records, without model calls."""
from pathlib import Path
import argparse,hashlib,json,runpy,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
 out=args.output_dir.resolve()
 if out.exists() or out.is_relative_to(ROOT):ap.error('Choose a new output directory outside this repository.')
 index=json.loads((ROOT/'manifests/PAPER04_SOURCES.json').read_text())
 # Reuse the already checked offline guard; imported replay does not start a run.
 sys.path.insert(0,str(ROOT));import replay;sys.addaudithook(replay.offline_guard)
 with tempfile.TemporaryDirectory(prefix='paper04-source-view-') as temp:
  view=Path(temp).resolve()
  for relative,row in index.items():
   src=(ROOT/row['path']).resolve();dst=(view/relative).resolve()
   if not src.is_relative_to(ROOT) or not dst.is_relative_to(view):raise ValueError('Invalid source mapping')
   if digest(src)!=row['sha256']:raise ValueError('Source hash changed: '+relative)
   dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
  original=runpy.run_path(str(ROOT/'reference-code/paper04/extract_paper_data.py'))
  collect=original['collect'];collect.__globals__['ROOT']=view
  data,examples=collect()
 out.mkdir(parents=True)
 checks={}
 for name,value in [('paper-data-v0.1-2026-10-13.json',data),('evidence-extract-v0.1-2026-10-13.json',examples)]:
  raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode();(out/name).write_bytes(raw)
  checks[name]=raw==(ROOT/'papers/paper-04'/name).read_bytes()
 report={'status':'PASS' if all(checks.values()) else 'FAIL','source_files_checked':len(index),'completed_responses_inventory':data['completed_responses_inventory'],'byte_equal':checks,'model_calls':0}
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
