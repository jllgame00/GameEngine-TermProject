"""Serial history gate; reuse explicit successful process reports only."""
import argparse,datetime,json,os,pathlib,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--reuse',nargs='*',default=[]);p.add_argument('--only',nargs='*');a=p.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[2];FOLDER=ROOT/'Saved/MVPCompletion';FOLDER.mkdir(parents=True,exist_ok=True)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');output=FOLDER/(stamp+'-history-gate.json')
R={'complete':False,'pass':False,'checks':[],'scope':'Recommendation History/Revisit Memory, runtime session only; isolated fixtures labeled separately'}
def save():output.write_text(json.dumps(R,indent=2),encoding='utf8')
keys=[('history-editor','editor'),('history-guards','guards'),('history-week','week'),('history-rs001','rs001'),('history-rs002','rs002'),('history-rs003','rs003'),('history-isolated','isolated'),('history-audio','audio'),('history-startup','startup'),('-cook-final-','cook')]
for path in a.reuse:
 info=json.loads(pathlib.Path(path).read_text(encoding='utf8'));name=next((name for key,name in keys if key in pathlib.Path(path).name),None);assert name,path
 assert info.get('pass') if name=='cook' else info.get('process_pass'),path
 assert name not in [c['name'] for c in R['checks']],name
 R['checks'].append({'name':name,'pass':True,'reused_process_report':str(pathlib.Path(path).resolve()),'process':info})
checks=[('editor',['Scripts/Unreal/validate_history_editor.py'],{}),('guards',['Scripts/Unreal/validate_history_guards.py','--rendered','--audio'],{}),('week',['Scripts/Unreal/validate_history_week.py','--rendered','--audio'],{})]
for choice in (1,2,3):checks.append(('rs00'+str(choice),['Scripts/Unreal/validate_mvp_cycle.py','--rendered','--windowed','--audio'],{'MVP_NATIVE_UI':'1','MVP_RECORD_CHOICE':str(choice),'MVP_RPM':str({1:33,2:45,3:78}[choice]),'MVP_TURNTABLE_APPROACH':'front'}))
checks += [('isolated',['Scripts/Unreal/validate_mvp_regressions.py','--rendered','--audio'],{}),('audio',['Scripts/Unreal/validate_day_audio.py','--rendered','--audio'],{}),('startup',['Scripts/Unreal/validate_mvp_editor_control.py'],{}),('cook',None,{})]
if a.only:
 assert set(a.only)<={c[0] for c in checks}
 checks=[c for c in checks if c[0] in a.only]
R['requested_checks']=[c[0] for c in checks];save();print('HISTORY_GATE',output,flush=True)
for name,args,extra in checks:
 if any(c['name']==name and c['pass'] for c in R['checks']):continue
 env=os.environ.copy()
 for key in list(env):
  if key.startswith('MVP_'):env.pop(key)
 env.update(extra);env['PYTHONIOENCODING']='utf-8'
 cmd=[sys.executable,str(ROOT/'Scripts/Unreal/cook_mvp.py')] if args is None else [sys.executable,str(ROOT/'Scripts/Unreal/run_mvp_validation.py'),*args,'--name','history-'+name]
 print('BEGIN',name,flush=True);run=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,encoding='utf8',errors='replace')
 host=FOLDER/(stamp+'-history-gate-'+name+'-host.txt');host.write_text(run.stdout+'\n'+run.stderr,encoding='utf8')
 result={'name':name,'pass':run.returncode==0,'exit_code':run.returncode,'host_output':str(host)}
 try:result['process']=json.loads(run.stdout[run.stdout.index('{'):])
 except Exception:result['parse_error']='Inspect host output'
 R['checks'].append(result);save();print(('PASS' if result['pass'] else 'FAIL'),name,flush=True)
R['complete']=True;R['pass']=all(c['pass'] for c in R['checks']);save();print('HISTORY_GATE_COMPLETE',R['pass'],output,flush=True)
sys.exit(0 if R['pass'] else 1)
