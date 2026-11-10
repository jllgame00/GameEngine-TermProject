"""Isolated real-audio Store BGM lifecycle; no simulated time or forced completion."""
import json,os,time,traceback
from pathlib import Path
import unreal
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'isolated real audio loop/fade plumbing; no customer cycle claim'}
def save():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
import sys
sys.path.insert(0,str(Path(unreal.Paths.project_dir())/'Scripts/Unreal'))
from day_graph_helpers import *
bp=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager');g=fn(bp,'PrepareAudioFixtureResult');end=assign(g,g.find_graph_entry_pin(),'ResultStartedForCustomer','true');own(g,end,'/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C','SetGameFlowState',NewState='NewEnumerator5');assert L.compile_blueprint(bp)
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();started=time.monotonic();phase={'gen':None,'end':None,'busy':False}
def run():
 while not editor.get_game_world():yield
 world=editor.get_game_world();kind=unreal.load_class(None,'/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C')
 flow=unreal.GameplayStatics.get_all_actors_of_class(world,kind)[0];pc=unreal.GameplayStatics.get_player_controller(world,0);view=pc.get_view_target();cursor=pc.get_editor_property('show_mouse_cursor')
 panel=flow.get_editor_property('PrologueWidgetRef');assert panel
 assert flow.get_editor_property('StoreBGMRef')is None
 ok,record=flow.get_editor_property('RecordCatalogue').call_method('ResolvePlayableRecord',args=('RS001',));assert ok
 flow.call_method('HandleRecordSelected',args=(record,));flow.call_method('PrepareAudioFixtureResult')
 flow.call_method('StartStoreBGM');audio=flow.get_editor_property('StoreBGMRef');assert audio and audio.is_playing()
 original=audio.get_path_name();source=audio.get_editor_property('sound').get_path_name();duration=audio.get_editor_property('sound').get_editor_property('duration')
 for _ in range(4):flow.call_method('StartStoreBGM')
 assert flow.get_editor_property('StoreBGMRef').get_path_name()==original
 R['loop_start']={'component':original,'sound':source,'duration':duration,'looping':audio.get_editor_property('sound').get_editor_property('looping')};save()
 audio=None;deadline=time.monotonic()+duration+5
 while True:
  current=flow.get_editor_property('StoreBGMRef')
  if current and current.get_path_name()!=original:
   assert current.is_playing() and current.get_editor_property('sound').get_path_name()==source
   break
  if time.monotonic()>=deadline:
   R['loop_timeout']={'requested':flow.get_editor_property('StoreBGMRequested'),'component':current.get_path_name() if current else None,'state':str(current.get_play_state()) if current else None,'world_time':unreal.GameplayStatics.get_time_seconds(world)};save()
   raise AssertionError('Natural BGM completion did not loop')
  yield
 next_path=current.get_path_name()
 R['natural_loop']={'first_component':original,'next_component':next_path,'sound':source,'duration':duration,'one_live_reference':True}
 current=None
 # Listening entry clears demand immediately; the reference clears after the fade.
 flow.call_method('StartListeningWindow');assert not flow.get_editor_property('StoreBGMRequested')
 until=time.monotonic()+1
 while time.monotonic()<until:yield
 assert flow.get_editor_property('StoreBGMRef')is None
 assert next_path not in [c.get_path_name() for c in unreal.ObjectIterator(unreal.AudioComponent) if c.is_playing()]
 for _ in range(3):flow.call_method('StopStoreBGM')
 assert pc.get_view_target()==view and pc.get_editor_property('show_mouse_cursor')==cursor
 assert flow.get_editor_property('PrologueWidgetRef')==panel and not flow.get_editor_property('TutorialComplete') and flow.get_editor_property('CurrentDay')==0
 R['fade_stop_and_idempotency']=True;R['complete']=True;R['pass']=True;save()
def tick(delta):
 if phase['busy']:return
 phase['busy']=True
 try:
  if phase['end'] is not None:
   if time.monotonic()-phase['end']>3:
    unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if phase['gen'] is None:phase['gen']=run()
  assert time.monotonic()-started<75
  next(phase['gen'])
 except StopIteration:level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
