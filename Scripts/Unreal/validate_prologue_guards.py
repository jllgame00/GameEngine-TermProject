"""Isolated opening guards, direct delegates/calls; not contiguous E2E evidence."""
import json, os, time, traceback
from pathlib import Path
import unreal
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'isolated direct-call opening guards; no saves'}
def save():OUT.write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
def cls(p):return unreal.load_class(None,p+'.'+p.rsplit('/',1)[1]+'_C')
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();start=time.monotonic();phase={'gen':None,'end':None,'busy':False}
def run():
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_all_actors_of_class(world,cls('/Game/RecordShop/Core/Flow/BP_GameFlowManager'))[0]
 pawn=unreal.GameplayStatics.get_player_pawn(world,0)
 original=flow.get_editor_property('PrologueWidgetRef');flow.call_method('BeginPrologue');assert flow.get_editor_property('PrologueWidgetRef')==original
 flow.call_method('CompleteTutorial');flow.call_method('FinishResult');assert not flow.get_editor_property('TutorialComplete') and not flow.get_editor_property('ActiveCustomer')
 for _ in range(3):
  flow.get_editor_property('PrologueWidgetRef').get_editor_property('Continue').get_editor_property('on_clicked').broadcast()
  for _ in range(4):yield
 assert flow.get_editor_property('PrologueStage')==3
 for _ in range(4):flow.call_method('AdvancePrologue');flow.call_method('BeginPrologue');flow.call_method('CompleteTutorial');flow.call_method('FocusPrologue')
 assert flow.get_editor_property('PrologueWidgetRef') is None and not flow.get_editor_property('TutorialComplete')
 pc=unreal.GameplayStatics.get_player_controller(world,0)
 assert not pc.get_editor_property('show_mouse_cursor') and pc.get_view_target()==pawn
 for actor_path,widget_path in [('Interaction/Actors/BP_RecordShelf','UI/RecordSelection/WBP_RecordSelect'),('Interaction/Actors/BP_Turntable','UI/Turntable/WBP_Turntable')]:
  actor=unreal.GameplayStatics.get_all_actors_of_class(world,cls('/Game/RecordShop/'+actor_path))[0]
  actor.call_method('Interact',args=(pawn,))
  assert not unreal.WidgetLibrary.get_all_widgets_of_class(world,cls('/Game/RecordShop/'+widget_path),True),'Opening Explore allowed premature '+widget_path
 R['pass']=True

def tick(delta):
 if phase['busy']:return
 phase['busy']=True
 try:
  if phase['end'] is not None:
   if time.monotonic()-phase['end']>2:
    unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if phase['gen'] is None:phase['gen']=run()
  assert time.monotonic()-start<50
  next(phase['gen'])
 except StopIteration:
  R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:
  R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
