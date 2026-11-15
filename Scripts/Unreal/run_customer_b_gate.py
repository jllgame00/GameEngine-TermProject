"""Customer B matrix plus fresh Customer A and complete foundation regression."""
import argparse,datetime,json,pathlib,subprocess,sys,os
p=argparse.ArgumentParser();p.add_argument('--reuse-b-contract');p.add_argument('--reuse-b-matrix');p.add_argument('--reuse-a-gate');a=p.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[2];folder=ROOT/'Saved/MVPCompletion'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=folder/(stamp+'-customer-b-gate.json')
R={'complete':False,'pass':False,'checks':[]}
def save():out.write_text(json.dumps(R,indent=2),encoding='utf8')
def execute(name,cmd):
 print('BEGIN',name,flush=True);env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
 run=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,encoding='utf8',errors='replace');host=folder/(stamp+'-customer-b-gate-'+name+'-host.txt');host.write_text(run.stdout+'\n'+run.stderr,encoding='utf8')
 c={'name':name,'pass':run.returncode==0,'exit_code':run.returncode,'host_output':str(host)}
 try:
  if name=='a_and_core':
   path=next(line.split('CUSTOMER_A_GATE ',1)[1]for line in run.stdout.splitlines()if line.startswith('CUSTOMER_A_GATE '));c['aggregate']=path;c['process']=json.loads(pathlib.Path(path).read_text(encoding='utf8'))
  else:c['process']=json.loads(run.stdout[run.stdout.index('{'):])
 except Exception:c['parse_error']='Inspect host output';c['pass']=False
 R['checks'].append(c);save();print(('PASS'if c['pass']else 'FAIL'),name,flush=True)
print('CUSTOMER_B_GATE',out,flush=True);save()
if a.reuse_b_contract:
 value=json.loads(pathlib.Path(a.reuse_b_contract).read_text(encoding='utf8'));assert value['process_pass'];R['checks'].append({'name':'contract','pass':True,'reused_process_report':str(pathlib.Path(a.reuse_b_contract).resolve()),'process':value});save()
else:execute('contract',[sys.executable,'Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_customer_b_contract.py','--name','customer-b-contract'])
if a.reuse_b_matrix:
 value=json.loads(pathlib.Path(a.reuse_b_matrix).read_text(encoding='utf8'));assert value['process_pass'];R['checks'].append({'name':'matrix','pass':True,'reused_process_report':str(pathlib.Path(a.reuse_b_matrix).resolve()),'process':value});save()
else:execute('matrix',[sys.executable,'Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_customer_b_sequences.py','--rendered','--audio','--name','customer-b-sequences'])
if a.reuse_a_gate:
 value=json.loads(pathlib.Path(a.reuse_a_gate).read_text(encoding='utf8'))
 assert value['complete']and value['pass']and len(value['checks'])==3 and all(c['pass']for c in value['checks'])
 R['checks'].append({'name':'a_and_core','pass':True,'reused_aggregate':str(pathlib.Path(a.reuse_a_gate).resolve()),'process':value});save()
else:execute('a_and_core',[sys.executable,'Scripts/Unreal/run_customer_a_gate.py'])
R['complete']=True;R['pass']=all(c['pass']for c in R['checks']);save();print('CUSTOMER_B_GATE_COMPLETE',R['pass'],out,flush=True);sys.exit(0 if R['pass']else 1)
