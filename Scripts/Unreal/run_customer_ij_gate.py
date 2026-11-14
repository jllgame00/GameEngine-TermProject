"""Serial I/J plus full audio, six-record, A-H, Tutorial and Core regression gate."""
import datetime,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];F=ROOT/'Saved/MVPCompletion'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');OUT=F/(stamp+'-customer-ij-gate.json')
R={'complete':False,'pass':False,'checks':[]}
def save():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
checks=[('contract',['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_customer_ij_contract.py','--commandlet','--name','customer-ij-contract'],{}),('matrix',['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_customer_ij_sequences.py','--rendered','--audio','--name','customer-ij-sequences'],{})]
for grade in ('GOOD','POOR'):
 checks.append((grade.lower(),['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_customer_ij_cycles.py','--rendered','--audio','--name','customer-ij-'+grade.lower()],{'MVP_DAY7_GRADE':grade}))
checks.append(('full_regression',['Scripts/Unreal/run_audio_handoff_gate.py'],{}))
print('CUSTOMER_IJ_GATE',OUT,flush=True);save()
for name,args,extra in checks:
 env=os.environ.copy()
 for key in list(env):
  if key.startswith('MVP_'):env.pop(key)
 env.update(extra);env['PYTHONIOENCODING']='utf-8'
 print('BEGIN',name,flush=True);run=subprocess.run([sys.executable,*args],cwd=ROOT,env=env,capture_output=True,encoding='utf8',errors='replace')
 host=F/(stamp+'-customer-ij-'+name+'-host.txt');host.write_text(run.stdout+'\n'+run.stderr,encoding='utf8');item={'name':name,'pass':False,'exit_code':run.returncode,'host_output':str(host)}
 try:
  if name=='full_regression':
   path=next(line.split('AUDIO_HANDOFF_GATE ',1)[1]for line in run.stdout.splitlines()if line.startswith('AUDIO_HANDOFF_GATE '));value=json.loads(pathlib.Path(path).read_text(encoding='utf8'));item['aggregate']=path;valid=value['complete']and value['pass']and len(value['checks'])==3 and all(c['pass']for c in value['checks'])
  else:value=json.loads(run.stdout[run.stdout.index('{'):]);valid=value['process_pass']
  item.update(process=value,**{'pass':run.returncode==0 and valid})
 except Exception as error:item['error']=repr(error)
 R['checks'].append(item);save();print('PASS'if item['pass']else 'FAIL',name,flush=True)
 if not item['pass']:break
R.update(complete=True,**{'pass':len(R['checks'])==5 and all(c['pass']for c in R['checks'])});save();print('CUSTOMER_IJ_GATE_COMPLETE',R['pass'],OUT,flush=True);sys.exit(0 if R['pass']else 1)
