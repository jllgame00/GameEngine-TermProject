"""Serial C/D production contract/matrix, then the existing complete B/A/Core gate."""
import datetime,json,pathlib,subprocess,sys,os
ROOT=pathlib.Path(__file__).resolve().parents[2];folder=ROOT/'Saved/MVPCompletion'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=folder/(stamp+'-customer-cd-gate.json')
R={'complete':False,'pass':False,'checks':[]}
def save():out.write_text(json.dumps(R,indent=2),encoding='utf8')
print('CUSTOMER_CD_GATE',out,flush=True);save()
checks=[('contract',['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_customer_cd_contract.py','--name','customer-cd-contract']),('matrix',['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_customer_cd_sequences.py','--rendered','--audio','--name','customer-cd-sequences']),('b_a_core',['Scripts/Unreal/run_customer_b_gate.py'])]
for name,args in checks:
 print('BEGIN',name,flush=True);env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
 run=subprocess.run([sys.executable,*args],cwd=ROOT,env=env,capture_output=True,encoding='utf8',errors='replace')
 host=folder/(stamp+'-customer-cd-gate-'+name+'-host.txt');host.write_text(run.stdout+'\n'+run.stderr,encoding='utf8');item={'name':name,'pass':False,'exit_code':run.returncode,'host_output':str(host)}
 try:
  if name=='b_a_core':
   path=next(line.split('CUSTOMER_B_GATE ',1)[1]for line in run.stdout.splitlines()if line.startswith('CUSTOMER_B_GATE '));value=json.loads(pathlib.Path(path).read_text(encoding='utf8'));item['aggregate']=path
   valid=value['complete']and value['pass']and len(value['checks'])==3 and all(c['pass']for c in value['checks'])
  else:value=json.loads(run.stdout[run.stdout.index('{'):]);valid=value['process_pass']
  item.update(process=value,**{'pass':run.returncode==0 and valid})
 except Exception:item['parse_error']='Missing or invalid evidence; inspect host output'
 R['checks'].append(item);save();print('PASS'if item['pass']else 'FAIL',name,flush=True)
 if not item['pass']:break
R['complete']=True;R['pass']=len(R['checks'])==3 and all(c['pass']for c in R['checks']);save()
print('CUSTOMER_CD_GATE_COMPLETE',R['pass'],out,flush=True);sys.exit(0 if R['pass']else 1)
