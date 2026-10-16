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
if a.audio:
 args.remove('-nosound')
 # Offscreen/unfocused validation must reach the mixer. This per-process override
 # does not change the shipped game's focus/audio policy or saved editor settings.
 args+=['-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0',
          '-ini:EditorPerProjectUserSettings:[/Script/UnrealEd.LevelEditorPlaySettings]:SoloAudioInFirstPIEClient=True',
          '-ini:EditorPerProjectUserSettings:[/Script/UnrealEd.LevelEditorMiscSettings]:bAllowBackgroundAudio=True']
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
if data.get('audio_output_capture'):
 import wave,array,math
 capture=pathlib.Path(data['audio_output_capture'])
 try:
  with wave.open(str(capture),'rb') as wav:
   assert wav.getsampwidth()==2
   frames=wav.getnframes();rate=wav.getframerate();channels=wav.getnchannels();samples=array.array('h',wav.readframes(frames))
  peak=max(abs(v) for v in samples)/32768; rms=math.sqrt(sum((v/32768)**2 for v in samples)/len(samples))
  summary['audio_output']={'path':str(capture),'seconds':frames/rate,'channels':channels,'peak':peak,'rms':rms,'pass':peak>.01 and rms>.001 and peak<1}
 except Exception as error:summary['audio_output']={'path':str(capture),'pass':False,'error':repr(error)}
 summary['assertions_pass']=summary['assertions_pass'] and summary['audio_output']['pass']
if data.get('dialogue_next_position_validation'):
 # Cached UMG geometry can be unavailable in PIE. Fail closed on the actual
 # screenshots instead of allowing five identical zero vectors to pass.
 try:
  from PIL import Image
  frames=[x for x in data.get('screenshots_requested',[]) if x['stage'].startswith('dialogue-line-')]
  assert len(frames)==5, 'Expected all five owner dialogue captures'
  boundaries=[]
  for frame in frames:
   with Image.open(frame['path']) as source:
    im=source.convert('RGB');pixels=im.load();rows=[]
    for y in range(int(im.height*.7),int(im.height*.96)):
     start=None
     for x in range(int(im.width*.6),int(im.width*.94)):
      bright=min(pixels[x,y])>150 and max(pixels[x,y])-min(pixels[x,y])<45
      if bright and start is None:start=x
      if not bright and start is not None:
       if im.width*.04<x-start<im.width*.11:rows.append((y,start,x-1))
       start=None
    pairs=[(a,b) for a in rows for b in rows if a[1:]==b[1:] and im.height*.018<b[0]-a[0]<im.height*.06]
    assert len(pairs)==1, ('Next button border not uniquely found',frame['path'],pairs)
    top,bottom=pairs[0];boundaries.append([top[1],top[0],top[2],bottom[0]])
  assert len({tuple(b) for b in boundaries})==1, ('Next moved across dialogue lines',boundaries)
  summary['dialogue_next_pixels']={'pass':True,'boundaries':boundaries,'frames':[x['path'] for x in frames]}
 except Exception as error:summary['dialogue_next_pixels']={'pass':False,'error':repr(error)}
 summary['assertions_pass']=summary['assertions_pass'] and summary['dialogue_next_pixels']['pass']
summary['process_pass']=code==0 and summary['complete'] and summary['assertions_pass'] and summary['gameplay_log_pass']
(folder/(name+'-process.json')).write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2),flush=True)
sys.exit(0 if summary['process_pass'] else 1)
