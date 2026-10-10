"""Host runner: fresh evidence with native exit, assertion, and runtime-log gates."""
import argparse, datetime, json, pathlib, subprocess, sys
from mvp_validation_logs import classify_log
p=argparse.ArgumentParser()
p.add_argument('script');p.add_argument('--rendered',action='store_true');p.add_argument('--commandlet',action='store_true');p.add_argument('--audio',action='store_true');p.add_argument('--name',default='validation')
p.add_argument('--windowed',action='store_true',help='Use a native editor window for synthetic Windows keyboard input')
p.add_argument('--result-navigation',action='store_true',help='Use synthetic Slate Tab/Enter navigation for Result in NullRHI')
a=p.parse_args();root=pathlib.Path(__file__).resolve().parents[2]
if pathlib.Path(a.script).name=='validate_mvp_cycle.py' and not (a.result_navigation or (a.rendered and a.windowed)):
 p.error('Cycle Result input requires --rendered --windowed, or --result-navigation for NullRHI.')
folder=root/'Saved/MVPCompletion';folder.mkdir(parents=True,exist_ok=True)
name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+a.name
result=folder/(name+'.json');log=folder/(name+'.log');wrapper=folder/(name+'.py')
script=(root/a.script).resolve()
wrapper.write_text('import os, unreal\nunreal.log("MVP_VALIDATION_SCRIPT_BEGIN")\nos.environ["MVP_RESULT"]='+repr(str(result))+'\nexec(compile(open('+repr(str(script))+',encoding="utf-8-sig").read(),'+repr(str(script))+',"exec"))\n',encoding='utf-8')
if a.result_navigation:
 wrapper.write_text('import os\nos.environ["MVP_RESULT_NAVIGATION"]="1"\n'+wrapper.read_text(encoding='utf-8'),encoding='utf-8')
args=['C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(root/'RecordShop.uproject'),'-EnablePlugins=PythonScriptPlugin,EditorScriptingUtilities','-unattended','-nosound','-nop4','-nosplash','-DDC-ForceMemoryCache','-ddc=(Local=(Type=FileSystem,Path='+str(root/'DerivedDataCache')+'))','-UserDir='+str(folder/'User'),'-abslog='+str(log)]
if not a.rendered:args+=['-nullrhi']
if a.audio:args.remove('-nosound')
args+=['-run=pythonscript','-script='+str(wrapper)] if a.commandlet else ([] if a.windowed else ['-RenderOffscreen'])+['-NoLoadStartupPackages','-ExecutePythonScript='+str(wrapper)]
(folder/(name+'-command.json')).write_text(json.dumps(args,indent=2),encoding='utf-8')
print('START',name,flush=True)
with (folder/(name+'-stdout.txt')).open('w',encoding='utf-8') as out:
 process=subprocess.Popen(args,stdout=out,stderr=subprocess.STDOUT)
 try:code=process.wait(timeout=900)
 except subprocess.TimeoutExpired:process.terminate();code=process.wait();print('TIMEOUT',flush=True)
data=json.loads(result.read_text(encoding='utf-8')) if result.exists() else {}
summary={'exit_code':code,'exit_hex':hex(code & 0xffffffff),'complete':data.get('complete',False),'assertions_pass':data.get('pass',False),'result':str(result),'log':str(log)}
summary.update(classify_log(log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''))
summary['process_pass']=code==0 and summary['complete'] and summary['assertions_pass'] and summary['gameplay_log_pass']
(folder/(name+'-process.json')).write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2),flush=True)
sys.exit(0 if summary['process_pass'] else 1)
