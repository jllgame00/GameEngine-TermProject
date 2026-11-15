"""Isolated canonical selection/result fixture with real audio; natural week separate."""
import unreal,os,json,time,traceback,sys
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import struct_value
from day_graph_helpers import *
# Unsaved fixture function writes internal state through Blueprint access, not reflected property overrides.
bp=unreal.load_asset("/Game/RecordShop/Core/Flow/BP_GameFlowManager")
g=fn(bp,"PrepareAudioFixtureResult");end=assign(g,g.find_graph_entry_pin(),"ResultStartedForCustomer","true");own(g,end,"/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C","SetGameFlowState",NewState="NewEnumerator5");assert L.compile_blueprint(bp)
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'isolated canonical selection/result fixture; real mixer/components; full natural week separate','records':[]}
def save():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();started=time.monotonic();state={'gen':None,'end':None,'busy':False}
def wait(seconds):
 until=unreal.GameplayStatics.get_time_seconds(world)+seconds
 while unreal.GameplayStatics.get_time_seconds(world)<until:yield
def live():return [a for a in unreal.ObjectIterator(unreal.AudioComponent)if a.is_playing()and a.get_world()==world]
def run():
 global world
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_actor_of_class(world,unreal.load_class(None,'/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C'));tt=flow.get_editor_property('TurntableRef')
 cat=flow.get_editor_property('RecordCatalogue');assert tt and cat
 ok,record=cat.call_method('ResolvePlayableRecord',args=('RS003',));assert ok
 flow.call_method('HandleRecordSelected',args=(record,));assert str(struct_value(tt.get_editor_property('CurrentRecord'),'RecordID'))=='RS003'
 flow.call_method('PrepareAudioFixtureResult')
 flow.call_method('StartStoreBGM');audio=flow.get_editor_property('StoreBGMRef');assert audio and audio.is_playing()
 assert audio.get_editor_property('sound')==struct_value(record,'Audio'),'Result RS003 must become RS003 Store BGM, never fixed RS001'
 R['red_regression_fixed']=True;save()
 flow.call_method('StopStoreBGM');flow.call_method('FinishStoreBGMStop')
 for identity in ('RS001','RS003','RS005','RS006','RS002','RS004'):
  previous=flow.get_editor_property('StoreBGMRef');oldpath=previous.get_path_name()if previous else None
  ok,record=cat.call_method('ResolvePlayableRecord',args=(identity,));assert ok
  flow.call_method('HandleRecordSelected',args=(record,));assert not flow.get_editor_property('StoreBGMRequested')
  flow.call_method('FinishStoreBGMStop');assert flow.get_editor_property('StoreBGMRef')is None
  assert not previous or not previous.is_playing()
  tt.call_method('StartPlaybackAudio');yield from wait(.9)
  listening=tt.get_editor_property('PlaybackAudio');assert listening and listening.is_playing();listening_path=listening.get_path_name()
  assert listening.get_editor_property('sound')==struct_value(record,'Audio')
  assert len(live())==1,[(a.get_path_name(),str(a.get_editor_property('sound')))for a in live()]
  tt.call_method('BeginTonearmReturn');yield from wait(1.4)
  assert tt.get_editor_property('PlaybackAudio')is None
  flow.call_method('PrepareAudioFixtureResult')
  before=len(flow.get_editor_property('RecommendationHistory'))
  flow.call_method('StartStoreBGM');bgm=flow.get_editor_property('StoreBGMRef');assert bgm and bgm.is_playing()
  assert bgm.get_editor_property('sound')==struct_value(record,'Audio')
  assert str(flow.get_editor_property('CurrentStoreBGMRecordID'))==identity
  path=bgm.get_path_name()
  for _ in range(4):flow.call_method('StartStoreBGM');flow.call_method('StoreBGMFinishedEvent')
  assert flow.get_editor_property('StoreBGMRef')==bgm and bgm.get_path_name()==path
  assert len(flow.get_editor_property('RecommendationHistory'))==before
  yield from wait(.7);assert len(live())==1
  assert len(flow.get_components_by_class(unreal.AudioComponent))==1 and not tt.get_components_by_class(unreal.AudioComponent),'Finished component retained by owner'
  R['records'].append({'id':identity,'listening':listening_path,'bgm':path,'previous':oldpath,'same_audio':True,'duplicate_safe':True,'active_components':len(live())});save()
 source=bgm.get_editor_property('sound');duration=source.get_editor_property('duration');deadline=unreal.GameplayStatics.get_time_seconds(world)+duration+4
 while flow.get_editor_property('StoreBGMRef')==bgm:
  assert unreal.GameplayStatics.get_time_seconds(world)<deadline,'BGM did not loop naturally'
  yield
 loop=flow.get_editor_property('StoreBGMRef');assert loop and loop.is_playing()and loop.get_editor_property('sound')==source
 R['natural_loop']={'record':'RS004','first':path,'next':loop.get_path_name(),'duration':duration};save()
 flow.call_method('StopStoreBGM');assert not flow.get_editor_property('StoreBGMRequested')
 yield from wait(.85);assert flow.get_editor_property('StoreBGMRef')is None and not live()
 assert not flow.get_components_by_class(unreal.AudioComponent)and not tt.get_components_by_class(unreal.AudioComponent),'Stopped component leaked'
 assert str(flow.get_editor_property('CurrentStoreBGMRecordID'))=='None'and flow.get_editor_property('StoreBGMSound')is None
 tt.call_method('ClearCompletedRecord');flow.call_method('StartStoreBGM');assert flow.get_editor_property('StoreBGMRef')is None and not live()
 assert not tt.get_editor_property('HasRecord')and str(struct_value(tt.get_editor_property('CurrentRecord'),'RecordID'))=='None'
 R.update(complete=True,**{'pass':True},fade_cleanup=True,invalid_no_fallback=True);save()
def tick(delta):
 if state['busy']:return
 state['busy']=True
 try:
  if state['end']is not None:
   if time.monotonic()-state['end']>3:unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if state['gen']is None:state['gen']=run()
  assert time.monotonic()-started<150
  next(state['gen'])
 except StopIteration:level.editor_request_end_play();state['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();state['end']=time.monotonic()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
