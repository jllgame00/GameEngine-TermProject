"""Reclassify an unchanged engine log; preserve original process/assertion evidence."""
import argparse,json,hashlib
from pathlib import Path
from mvp_validation_logs import classify_log
p=argparse.ArgumentParser();p.add_argument('report');a=p.parse_args()
source=Path(a.report).resolve();original=json.loads(source.read_text(encoding='utf-8'));log=Path(original['log']);text=log.read_text(encoding='utf-8',errors='replace')
updated=dict(original);updated.update(classify_log(text))
updated['source_process_report']=str(source);updated['original_process_pass']=original.get('process_pass');updated['original_unexpected_errors']=original.get('unexpected_errors',[])
updated['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest();updated['classifier_sha256']=hashlib.sha256(Path(__file__).with_name('mvp_validation_logs.py').read_bytes()).hexdigest()
updated['reclassification']='Exact pre-engine-init UnifiedError header + optional struct timing displays + contiguous15 conditions; gameplay errors remain failures'
updated['process_pass']=updated['exit_code']==0 and updated.get('complete',False)and updated.get('assertions_pass',False)and updated['gameplay_log_pass']
target=source.with_name(source.name.removesuffix('-process.json')+'-reclassified-process.json');assert target!=source
target.write_text(json.dumps(updated,indent=2),encoding='utf-8')
print(json.dumps({'report':str(target),'process_pass':updated['process_pass'],'known_startup':len(updated['known_startup_engine_smoke_errors']),'unexpected':len(updated['unexpected_errors']),'source_unchanged':True},indent=2))
