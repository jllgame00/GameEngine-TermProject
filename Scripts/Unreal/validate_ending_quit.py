"""Actual Title Quit OnClicked -> production QuitGame; PIE exit, not packaged process exit."""
import unreal,os,json,sys,time,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from ending_runtime_support import *
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'production Title Quit through Slate virtual Enter; observes PIE termination'}
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();state={'gen':None,'end':None,'busy':False};started=time.monotonic()
def run():
 yield from wait(lambda:context(editor)is not None)
 world,flow,pc,pawn=context(editor);yield from wait(lambda:flow.get_editor_property('FrontEndInputReady'))
 panel=fresh_title(world,flow,pc,pawn)
 if os.environ.get('MVP_ENDING_RESOLUTION'):
  width,height=map(int,os.environ['MVP_ENDING_RESOLUTION'].split('x'));R['viewport_resolution']=list((yield from viewport_size(pc,width,height)))
 path=OUT.with_name(OUT.stem+'-title.png');unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(path)+'" -nosuffix');yield from frames(4);R['capture']=str(path)
 button=panel.get_editor_property('Quit');component=interaction(pawn);component.set_focus(button);yield from frames(2)
 key=unreal.Key();key.import_text('Enter');assert component.press_and_release_key(key)
 yield from wait(lambda:editor.get_game_world()is None)
 assert not alive(flow);R.update(complete=True,**{'pass':True},quit_clicked=True,pie_ended=True)
def tick(delta):
 if state['busy']:return
 state['busy']=True
 try:
  if state['end']is not None:
   if time.monotonic()-state['end']>2:unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if state['gen']is None:state['gen']=run()
  assert time.monotonic()-started<90;next(state['gen'])
 except StopIteration:OUT.write_text(json.dumps(R,indent=2),encoding='utf8');state['end']=time.monotonic()
 except Exception:R.update(complete=True,**{'pass':False},fatal=traceback.format_exc());OUT.write_text(json.dumps(R,indent=2),encoding='utf8');level.editor_request_end_play();state['end']=time.monotonic()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
