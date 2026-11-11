"""Cold Title/fresh New Game and real-audio Ending matrix; queue completion is isolated."""
import unreal,os,json,sys,time,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from ending_runtime_support import *
from narrative_validation_support import struct_value
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'real UI/audio/travel after explicitly unsaved completed-Day7/accepted-Result fixtures; full natural customer week is separate','cases':[]}
def save():OUT.write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
bp=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager')
g=fn(bp,'PrepareEndingQueueFixture');queue=inputs(g,[('Queue',L.get_array_type(L.get_object_reference_type(unreal.load_class(None,'/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C'))))])['Queue'];end=g.find_graph_entry_pin();end=own(g,end,FC,'ClearPresentationTimers')
yes,no=valid(g,get(g,'PrologueWidgetRef'),end);yes=invoke(g,yes,'/Script/UMG.Widget.RemoveFromParent',self=get(g,'PrologueWidgetRef'))[0]
n=setv(g,'PrologueWidgetRef','None');link(yes,n.find_execute_pin());link(no,n.find_execute_pin());end=n.find_then_pin()
day=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Day07')
for key,value in [('PresentationPhase','Playing'),('CurrentDay',7),('CurrentCustomerIndex',2),('QueueCycleInProgress','false'),('DayPhase','CustomerCycle'),('DayCustomersComplete','false'),('FinalStoryEventTriggered','false'),('ActiveCustomer','None'),('ActiveVisit','None'),('TutorialComplete','true'),('PrologueStage',5)]:end=assign(g,end,key,value)
n=setv(g,'CustomerQueue');link(queue,pin(n,'CustomerQueue'));link(end,n.find_execute_pin())
g=fn(bp,'AcceptEndingAudioFixture');end=assign(g,g.find_graph_entry_pin(),'ResultStartedForCustomer','true');own(g,end,FC,'SetGameFlowState',NewState='NewEnumerator5')
g=fn(bp,'StopEndingAudioFixture');end=assign(g,g.find_graph_entry_pin(),'StoreBGMRequested','false');invoke(g,end,'/Script/Engine.AudioComponent.Stop',self=get(g,'StoreBGMRef'))
assert L.compile_blueprint(bp)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();started=time.monotonic();state={'gen':None,'end':None,'busy':False}
def run():
 yield from wait(lambda:context(editor)is not None)
 current=context(editor);yield from wait(lambda:current[1].get_editor_property('FrontEndInputReady'))
 assert '-recordshopproductionvalidation'not in unreal.SystemLibrary.get_command_line().lower()
 fresh_title(*current);R['cold_title']=True
 if os.environ.get('MVP_ENDING_RESOLUTION'):
  width,height=map(int,os.environ['MVP_ENDING_RESOLUTION'].split('x'));R['viewport_resolution']=list((yield from viewport_size(current[2],width,height)))
 capture=OUT.with_name(OUT.stem+'-cold-title.png');unreal.SystemLibrary.execute_console_command(current[0],'Shot showui filename="'+str(capture)+'" -nosuffix');yield from frames(4);R['cold_title_capture']=str(capture);save()
 current=yield from new_game(editor,current[1]);R['new_game_fresh_world']=True;save()
 cases=[('RS003','normal')]if os.environ.get('MVP_ENDING_SMOKE')=='1'else [(r,'normal')for r in ['RS001','RS002','RS003','RS004','RS005','RS006','NONE']]+[('RS003','zero-fade'),('RS004','stopped'),('RS005','pending-abort')]
 for identity,mode in cases:
  world,flow,pc,pawn=current;flow.call_method('PrepareEndingQueueFixture',args=(list(day.get_editor_property('Visits')),))
  if identity!='NONE':
   ok,record=flow.get_editor_property('RecordCatalogue').call_method('ResolvePlayableRecord',args=(identity,));assert ok
   flow.call_method('HandleRecordSelected',args=(record,));flow.call_method('AcceptEndingAudioFixture');flow.call_method('StartStoreBGM')
   assert str(flow.get_editor_property('CurrentStoreBGMRecordID'))==identity
   ref=flow.get_editor_property('StoreBGMRef');assert ref and ref.is_playing()and ref.get_editor_property('sound')==struct_value(record,'Audio');initial=ref.get_path_name();ref=None
  else:initial=None
  if mode=='zero-fade':flow.set_editor_property('StoreBGMFadeOutDuration',0.0)
  flow.call_method('EndCurrentDay');assert str(flow.get_editor_property('PresentationPhase'))=='EndingPending'
  if identity!='NONE':assert flow.get_editor_property('StoreBGMRef').get_path_name()==initial
  if mode=='pending-abort':
   flow.call_method('ReturnToTitle');flow.call_method('FinishDayTransition');assert not flow.get_editor_property('FinalStoryEventTriggered')and str(flow.get_editor_property('DayPhase'))=='DayEnding';yield from wait(lambda:not alive(flow));yield from wait(lambda:context(editor)is not None)
   current=context(editor);yield from wait(lambda:current[1].get_editor_property('FrontEndInputReady'));fresh_title(*current)
   R['cases'].append(dict(record=identity,mode=mode,cancelled_final_timer=True,title=True));save();current=yield from new_game(editor,current[1]);continue
  yield from wait(lambda:flow.get_editor_property('EndingWidgetRef')is not None)
  assert flow.get_editor_property('FinalStoryEventTriggered')and flow.get_editor_property('CurrentDay')==7
  if identity!='NONE':assert flow.get_editor_property('StoreBGMRef').get_path_name()==initial,'Final hook restarted audio'
  if mode=='stopped':
   # Isolate an already stopped component at the travel boundary; Stop normally loops BGM.
   flow.call_method('StopEndingAudioFixture')
   flow.call_method('ReturnToTitle');yield from wait(lambda:not alive(flow));yield from wait(lambda:context(editor)is not None)
   current=context(editor);yield from wait(lambda:current[1].get_editor_property('FrontEndInputReady'));fresh_title(*current)
   R['cases'].append(dict(record=identity,mode=mode,title=True,title_audio_voices=0));save();current=yield from new_game(editor,current[1]);continue
  # Same-frame callback probes preserve one UI and a single final-day completion.
  if identity=='RS006'and mode=='normal'and os.environ.get('MVP_ENDING_NATURAL_LOOPS')=='1':
   observed=[];deadline=time.monotonic()+75;last=flow.get_editor_property('StoreBGMRef').get_path_name()
   while len(observed)<2:
    assert time.monotonic()<deadline
    ref=flow.get_editor_property('StoreBGMRef')
    if ref and ref.get_path_name()!=last:
     assert ref.is_playing()and ref.get_editor_property('sound')==struct_value(record,'Audio');last=ref.get_path_name();observed.append(last)
    assert len([a for a in unreal.ObjectIterator(unreal.AudioComponent)if a.get_world()==world and a.is_playing()])<=1
    yield
   R['natural_ending_loops']=dict(record=identity,completed_loops=len(observed),components=observed)
  comp=interaction(pawn);current=yield from finish_ending(editor,flow,comp,R,OUT,captures=identity==cases[0][0]and mode=='normal')
  R['cases'].append(dict(record=identity,mode=mode,ending=True,credits=True,title=True,fresh_history=0,title_audio_voices=0));save()
  current=yield from new_game(editor,current[1])
 from ending_validation_support import assert_preservation
 R.update(complete=True,**{'pass':True},preservation=assert_preservation(),new_game_resets=True);save()
def tick(delta):
 if state['busy']:return
 state['busy']=True
 try:
  if state['end']is not None:
   if time.monotonic()-state['end']>3:unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if state['gen']is None:state['gen']=run()
  assert time.monotonic()-started<480
  next(state['gen'])
 except StopIteration:level.editor_request_end_play();state['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['pass']=False;R['complete']=True;save();level.editor_request_end_play();state['end']=time.monotonic()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
