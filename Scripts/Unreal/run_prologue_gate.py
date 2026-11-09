"""Run the Prologue Production Gate serially; never stages or edits assets.

Each UE invocation uses the maintained runner's exit/assertion/runtime-log gate.
Rendered input cycles include real audio; direct-call diagnostics are separate.
"""
import argparse, datetime, json, os, pathlib, subprocess, sys
parser=argparse.ArgumentParser()
parser.add_argument('--only',nargs='+',help='Run named checks only')
parser.add_argument('--resume-report',type=pathlib.Path,help='Retain completed checks from this evidence report; original failures remain in the linked report')
options=parser.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/MVPCompletion'
STAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
report=OUT/(STAMP+'-prologue-gate.json')
R={'complete':False,'pass':False,'started_utc':STAMP,'checks':[]}
if options.resume_report:
 previous=json.loads(options.resume_report.read_text(encoding='utf8'))
 assert previous['complete'], 'Wait for the original serial run to finish'
 R['checks']=previous['checks']
 R['previous_report']=str(options.resume_report.resolve())
 R['previous_failures']=[c for c in previous['checks'] if not c['pass']]
checks=[
 ('contract',['Scripts/Unreal/validate_prologue_contract.py'],{}),
 ('opening-guards',['Scripts/Unreal/validate_prologue_guards.py'],{}),
 ('dependencies',['Scripts/Unreal/validate_mvp_dependencies.py'],{}),
]
for choice, rpm, approach, size in [(1,33,'front','1280x720'),(2,45,'front','1280x720'),(3,78,'right','1920x1080')]:
 checks.append(('rs00'+str(choice),['Scripts/Unreal/validate_mvp_cycle.py','--rendered','--windowed','--audio'],{'MVP_NATIVE_UI':'1','MVP_RECORD_CHOICE':str(choice),'MVP_RPM':str(rpm),'MVP_TURNTABLE_APPROACH':approach,'MVP_NATIVE_SIZE':size,'MVP_IMMERSIVE':'0'}))
checks += [('isolated-regressions',['Scripts/Unreal/validate_mvp_regressions.py','--rendered','--audio'],{}),('editor-startup',['Scripts/Unreal/validate_mvp_editor_control.py'],{}),('cook',None,{})]
if options.only:
 assert set(options.only)<={name for name,_,_ in checks}
 checks=[c for c in checks if c[0] in options.only]
OUT.mkdir(parents=True,exist_ok=True)
def save():report.write_text(json.dumps(R,indent=2),encoding='utf8')
save();print('PROLOGUE_GATE',report,flush=True)
for name,args,extra in checks:
 env=os.environ.copy()
 for key in list(env):
  if key.startswith('MVP_'):env.pop(key)
 env.update(extra);env['PYTHONIOENCODING']='utf-8'
 command=[sys.executable,str(ROOT/'Scripts/Unreal/cook_mvp.py')] if args is None else [sys.executable,str(ROOT/'Scripts/Unreal/run_mvp_validation.py'),*args,'--name','prologue-final-'+name]
 print('BEGIN',name,flush=True)
 result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,encoding='utf8',errors='replace')
 log=OUT/(STAMP+'-prologue-gate-'+name+'-host.txt');log.write_text(result.stdout+'\n'+result.stderr,encoding='utf8')
 item={'name':name,'exit_code':result.returncode,'pass':result.returncode==0,'host_output':str(log)}
 try:item['process']=json.loads(result.stdout[result.stdout.index('{'):])
 except Exception:item['parse_error']='Read host output for details'
 R['checks']=[c for c in R['checks'] if c['name']!=name]
 R['checks'].append(item);save();print(('PASS' if item['pass'] else 'FAIL'),name,flush=True)
R['complete']=True;R['pass']=all(c['pass'] for c in R['checks']);save()
print('GATE_COMPLETE',R['pass'],report,flush=True)
sys.exit(0 if R['pass'] else 1)
