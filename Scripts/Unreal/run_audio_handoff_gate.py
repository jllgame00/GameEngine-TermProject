"""Fresh real audio ownership plus the full six-record/Narrative/Core gate."""
import datetime,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];F=ROOT/'Saved/MVPCompletion';stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');OUT=F/(stamp+'-audio-handoff-gate.json');R={'complete':False,'pass':False,'checks':[]}
def save():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
checks=[('audio_contract',['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_audio_handoff_contract.py','--commandlet','--name','audio-handoff-contract']),('audio_runtime',['Scripts/Unreal/run_mvp_validation.py','Scripts/Unreal/validate_audio_handoff.py','--audio','--name','audio-handoff-runtime']),('full_regression',['Scripts/Unreal/run_record_expansion_gate.py'])]
print('AUDIO_HANDOFF_GATE',OUT,flush=True);save()
for name,args in checks:
 print('BEGIN',name,flush=True);env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';run=subprocess.run([sys.executable,*args],cwd=ROOT,env=env,capture_output=True,encoding='utf8',errors='replace');host=F/(stamp+'-audio-handoff-'+name+'-host.txt');host.write_text(run.stdout+'\n'+run.stderr,encoding='utf8');item={'name':name,'pass':False,'exit_code':run.returncode,'host_output':str(host)}
 try:
  if name=='full_regression':
   path=next(line.split('RECORD_EXPANSION_GATE ',1)[1]for line in run.stdout.splitlines()if line.startswith('RECORD_EXPANSION_GATE '));value=json.loads(pathlib.Path(path).read_text(encoding='utf8'));item['aggregate']=path;valid=value['complete']and value['pass']and len(value['checks'])==5 and all(c['pass']for c in value['checks'])
  else:value=json.loads(run.stdout[run.stdout.index('{'):]);valid=value['process_pass']
  item.update(process=value,**{'pass':run.returncode==0 and valid})
 except Exception as error:item['error']=repr(error)
 R['checks'].append(item);save();print('PASS'if item['pass']else 'FAIL',name,flush=True)
 if not item['pass']:break
R.update(complete=True,**{'pass':len(R['checks'])==3 and all(c['pass']for c in R['checks'])});save();print('AUDIO_HANDOFF_GATE_COMPLETE',R['pass'],OUT,flush=True);sys.exit(0 if R['pass']else 1)
