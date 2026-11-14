"""Three independent candidate sessions, then the complete existing narrative/core gate."""
import datetime,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];F=ROOT/'Saved/MVPCompletion';F.mkdir(parents=True,exist_ok=True)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');OUT=F/(stamp+'-records456-gate.json')
R={'complete':False,'pass':False,'checks':[]};digests=[]

def save():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')

checks=[('contract',['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_record_expansion_contract.py','--name','records456-contract'])]
for n in range(1,4):checks.append(('order'+str(n),['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_record_expansion_runtime.py','--rendered','--audio','--name','records456-order'+str(n)]))
checks.append(('narrative_core',['Scripts/Unreal/run_customer_efgh_gate.py']))
print('RECORD_EXPANSION_GATE',OUT,flush=True);save()
for name,args in checks:
 print('BEGIN',name,flush=True);env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
 run=subprocess.run([sys.executable,*args],cwd=ROOT,env=env,capture_output=True,encoding='utf8',errors='replace');host=F/(stamp+'-records456-'+name+'-host.txt');host.write_text(run.stdout+'\n'+run.stderr,encoding='utf8')
 item={'name':name,'pass':False,'exit_code':run.returncode,'host_output':str(host)}
 try:
  if name=='narrative_core':
   path=next(line.split('CUSTOMER_EFGH_GATE ',1)[1]for line in run.stdout.splitlines()if line.startswith('CUSTOMER_EFGH_GATE '));value=json.loads(pathlib.Path(path).read_text(encoding='utf8'));item['aggregate']=path;valid=value['complete']and value['pass']and len(value['checks'])==3 and all(c['pass']for c in value['checks'])
  else:
   value=json.loads(run.stdout[run.stdout.index('{'):]);valid=value['process_pass']
   if name.startswith('order')and valid:
    data=json.loads(pathlib.Path(value['result']).read_text(encoding='utf8'));assert len(data['cases'])==16 and data['actual_score_paths']==96 and data['permutation_clicks']==18
    semantic=[{k:v for k,v in c.items()if k!='capture'}for c in data['cases']];digest=hashlib.sha256(json.dumps(semantic,sort_keys=True).encode()).hexdigest();digests.append(digest);assert len(set(digests))==1,'Fresh-session order/profile changed';item['order_digest']=digest
  item.update(process=value,**{'pass':run.returncode==0 and valid})
 except Exception as error:item['parse_or_contract_error']=repr(error)
 R['checks'].append(item);save();print('PASS'if item['pass']else 'FAIL',name,flush=True)
 if not item['pass']:break
R.update(complete=True,**{'pass':len(R['checks'])==5 and all(c['pass']for c in R['checks'])},fresh_order_digests=digests);save()
print('RECORD_EXPANSION_GATE_COMPLETE',R['pass'],OUT,flush=True);sys.exit(0 if R['pass']else 1)
