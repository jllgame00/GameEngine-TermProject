"""Isolated diagnostics, explicitly not natural-cycle evidence. Never saves assets."""
import os,json,time,traceback,itertools,sys
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import *
from checkpoint_repair_checks import rpm_ui_checks,physical_input_checks
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'isolated':{},'compiles':{},'provenance':'direct diagnostic calls, button delegates, transient unsaved observer; not E2E'}
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';TT='/Game/RecordShop/Interaction/Actors/BP_Turntable';SHELF='/Game/RecordShop/Interaction/Actors/BP_RecordShelf';DM='/Game/DialogueManager'
DU='/Game/RecordShop/UI/Dialogue/WBP_Dialogue';SU='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect';TU='/Game/RecordShop/UI/Turntable/WBP_Turntable';RU='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
def save():OUT.write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf-8')
def check(name,fn):
 try:R['isolated'][name]={'pass':True,'observations':fn()}
 except Exception:R['isolated'][name]={'pass':False,'error':traceback.format_exc()}
 save()
def widgets(path):return list(unreal.WidgetLibrary.get_all_widgets_of_class(world,cls(path),True))
def click(w,name):w.get_editor_property(name).get_editor_property('on_clicked').broadcast()
def interact(a):a.call_method('Interact',args=(pawn,))
def count_modals():return {p:len(widgets(p)) for p in [DU,SU,TU,RU]}

save()
import faulthandler
_fault=open(OUT.with_suffix('.trace.txt'),'w')
faulthandler.enable(file=_fault)
# An in-memory observer consumes the actual dispatchers. No package is saved.
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_MVPObserver','/Game/RecordShop/Dev/IntegrationProbe',unreal.Blueprint,factory)
pg=evgraph(probe)
for name in ['Completions','Scores','LastScore']:assert pg.add_member_variable(name,L.get_basic_type_by_name('int'))
assert L.compile_blueprint(probe)
for event_name,member_name in [('ReceiveCompletion','Completions'),('ReceiveScore','Scores')]:
 if event_name=='ReceiveScore':event=signature_event(probe,event_name,[('RawScore',L.get_basic_type_by_name('int'))])
 else:event=pg.add_custom_event_node(event_name)
 pg=evgraph(probe)
 increment=pg.add_macro_node('/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:IncrementInt')
 assert increment
 link(get(pg,member_name),pin(increment,'Value'));link(event.find_then_pin(),pin(increment,' '))
 if event_name=='ReceiveScore':
  last=setv(pg,'LastScore');link(pin(event,'RawScore',True),pin(last,'LastScore'));link(pin(increment,'  ',True),last.find_execute_pin());score_event=event
 else:completion_event=event
bind_event=signature_event(probe,'Observe', [('Turntable',L.get_object_reference_type(cls(TT))),('Manager',L.get_object_reference_type(cls(DM)))])
pg=evgraph(probe)
p=bind_event.find_then_pin()
for obj,dispatcher,event,path in [('Turntable','OnTurntableCompleted',completion_event,TT),('Manager','OnLPScoreEvaluated',score_event,DM)]:
 bind=action(pg,'BindEventto'+dispatcher,[pin(bind_event,obj,True)],cls(path));link(pin(event,'OutputDelegate',True),pin(bind,'Delegate'));link(p,bind.find_execute_pin());p=bind.find_then_pin()
fixture_profile=function(probe,'SetLiveProfileFixture')
customer_path='/Game/RecordShop/Characters/Customers/Common/BP_Customer'
customer_pin=fixture_profile.add_graph_input_parameter('Customer',L.get_object_reference_type(cls(customer_path)))
flow_pin=fixture_profile.add_graph_input_parameter('Flow',L.get_object_reference_type(cls(FLOW)))
profile_pin=fixture_profile.add_graph_input_parameter('Profile',L.get_member_variable_type(unreal.load_asset(DM),'CurrentCustomer'))
setter=fixture_profile.add_set_member_variable_node('CustomerProfile',customer_path+'.BP_Customer_C');link(customer_pin,pin(setter,'self'));link(profile_pin,pin(setter,'CustomerProfile'));link(fixture_profile.find_graph_entry_pin(),setter.find_execute_pin())
reset=fixture_profile.add_set_member_variable_node('DialogueStartedForCustomer',FLOW+'.BP_GameFlowManager_C');link(flow_pin,pin(reset,'self'));val(pin(reset,'DialogueStartedForCustomer'),'false');link(setter.find_then_pin(),reset.find_execute_pin())
assert L.compile_blueprint(probe)
observer=unreal.get_default_object(probe.generated_class())
observe_method=str(bind_event.get_node_title())
save()
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
for path in [FLOW,TT,SHELF,DM,DU,SU,TU,RU]:R['compiles'][path]=L.compile_blueprint(unreal.load_asset(path))
assert all(R['compiles'].values())
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();start=time.monotonic();phase={'gen':None,'end':None}

def run():
 global world,flow,pawn,pc
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_all_actors_of_class(world,cls(FLOW))[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0)
 while not widgets(DU):
  assert time.monotonic()-start<70
  yield
 manager=flow.get_editor_property('DialogueManagerRef');tt=flow.get_editor_property('TurntableRef');shelves=list(unreal.GameplayStatics.get_all_actors_of_class(world,cls(SHELF)))
 observer.call_method(observe_method,args=(tt,manager))
 def dialogue_guards():
  original=widgets(DU)[0]
  for _ in range(3):flow.call_method('HandleCustomerReadyForDialogue')
  flow.call_method('FinishResult');assert flow.get_editor_property('ActiveCustomer');assert not flow.get_editor_property('ResultSubmitted')
  interact(tt);interact(shelves[0]);assert widgets(DU)==[original];assert not widgets(SU) and not widgets(TU)
  assert len(flow.get_components_by_class(cls(DM)))==1
  click(original,'Next');assert not widgets(DU);assert original.get_editor_property('DialogueManagerRef') is None
  assert int(flow.get_editor_property('CurrentState').value)==2
  manager.call_method('ShowNextLine');assert int(flow.get_editor_property('CurrentState').value)==2
  return {'one_manager':True,'repeated_ready':3,'premature_finish_rejected':True,'late_finish_idempotent':True}
 check('dialogue_and_premature_result_guards',dialogue_guards)
 def live_profile():
  import re
  customer=flow.get_editor_property('ActiveCustomer');profile=customer.get_editor_property('CustomerProfile');original=profile.export_text()
  fixture=original
  for name,value in [('CustomerID','probe-customer'),('Mood','probe-mood'),('Personality','probe-personality'),('MusicPreference','probe-preference')]:
   fixture=re.sub(r'('+name+r'_[A-Za-z0-9_]+)=\"[^\"]*\"',lambda m:m[1]+'="'+value+'"',fixture)
  assert fixture!=original
  try:
   profile.import_text(fixture);observer.call_method('SetLiveProfileFixture',args=(customer,flow,profile));flow.call_method('HandleCustomerReadyForDialogue')
   assert manager.get_editor_property('CurrentCustomer').export_text()==customer.get_editor_property('CustomerProfile').export_text()
   assert 'probe-customer' in manager.get_editor_property('CurrentCustomer').export_text();assert manager.get_editor_property('CurrentMood')=='probe-mood'
   assert len(manager.get_editor_property('DialogueList'))==0 and not widgets(DU)
  finally:
   profile.import_text(original);observer.call_method('SetLiveProfileFixture',args=(customer,flow,profile));flow.call_method('HandleCustomerReadyForDialogue')
   if widgets(DU):click(widgets(DU)[0],'Next')
  assert manager.get_editor_property('CurrentMood')==''
  return {'typed_active_customer_profile_copied':True,'mood_from_profile':True,'unmatched_mood_finishes_normally':True,'fixture':'in-memory live actor profile; restored; no table edits; diagnostic Ready invocation only'}
 check('live_customer_profile_and_mood_mapping',live_profile)
 def score_contract():
  records=[]
  for matches in itertools.product([False,True],repeat=3):
   args=tuple('' if x else 'nonmatching-isolated-fixture' for x in matches)
   score=manager.call_method('CalculateLPScore',args=args);assert score==sum(matches)
   before=observer.get_editor_property('Scores');manager.call_method('EvaluateLP',args=(*args,['fixture-only']))
   assert observer.get_editor_property('Scores')==before+1;assert observer.get_editor_property('LastScore')==score
   assert manager.get_editor_property('MaxScore')==3
   records.append({'matches':matches,'score':score,'output':observer.get_editor_property('LastScore')})
  manager.call_method('EvaluateLP',args=('x','x','x',[]));assert manager.get_editor_property('MaxScore')==0
  return {'cases':records,'maximum_assignment_repaired':True,'limitation':'AvailableLPs elements are unused by existing scaffold. Blank candidate inputs yield 3; this is not a meaningful catalogue maximum or qualitative evaluation.'}
 check('raw_score_output_all_eight_combinations',score_contract)
 def selection_guards():
  observed=[]
  for i in range(3):
   interact(shelves[0]);interact(shelves[0]);interact(shelves[1]);interact(tt)
   assert len(widgets(SU))==1 and not widgets(TU)
   click(widgets(SU)[0],f'BTN_LP0{i+1}');assert not widgets(SU);assert not pc.get_editor_property('show_mouse_cursor');assert tt.get_editor_property('HasRecord')
   record=tt.get_editor_property('CurrentRecord').export_text();assert f'Test_record_0{i+1}' in record;observed.append(record)
  return observed
 check('selection_ownership_all_records_and_modals',selection_guards)
 rpm_ui_checks(world,pawn,cls(TT),cls(TU),tt.get_editor_property('CurrentRecord'),check)
 def completion_guards():
  interact(tt);interact(tt);interact(shelves[0]);assert len(widgets(TU))==1 and not widgets(SU)
  w=widgets(TU)[0];initial=observer.get_editor_property('Completions')
  for name in ['BTN_Play','BTN_MoveTonearm','BTN_PlaceRecord','BTN_RPM78']:click(w,name)
  assert tt.get_editor_property('TurntableStep')==0;assert observer.get_editor_property('Completions')==initial
  for name in ['BTN_OpenLid','BTN_PlaceRecord','BTN_RPM33','BTN_MoveTonearm','BTN_Play']:click(w,name)
  assert tt.get_editor_property('CompletionSent');assert observer.get_editor_property('Completions')==initial+1
  assert w.get_editor_property('TurntableRef') is None
  result=widgets(RU)[0]
  for _ in range(3):tt.call_method('PlayRecord');tt.call_method('CompletePlayback');flow.call_method('HandleTurntableCompleted')
  assert widgets(RU)==[result];assert observer.get_editor_property('Completions')==initial+1
  interact(tt);interact(shelves[0]);assert not widgets(TU) and not widgets(SU)
  assert pc.get_editor_property('show_mouse_cursor')
  assert str(result.get_editor_property('RecordID').get_text())=='Test_record_03'
  return {'one_completion':True,'one_result':True,'cross_modal_blocked':True}
 check('completion_result_and_duplicate_guards',completion_guards)
 # SetInputMode queues owning-player Slate operations until the frame finishes.
 # Observe focus on subsequent frames without assigning any test-side focus.
 for _ in range(4):yield
 def focused_continue():
  result=widgets(RU)[0]
  assert result.get_editor_property('Continue').has_keyboard_focus(), 'Result default keyboard focus'
  assert result.get_editor_property('Continue').has_user_focus(pc), 'Result owning player focus'
  click(result,'Continue');click(result,'Continue');flow.call_method('FinishResult')
  assert flow.get_editor_property('ResultWidgetRef') is None;assert not widgets(RU);assert not pc.get_editor_property('show_mouse_cursor')
  return {'repeat_continue_guarded':True,'production_continue_focus':True,'test_focus_correction':False}
 check('result_default_focus_and_repeat_continue',focused_continue)
 while flow.get_editor_property('ActiveCustomer'):
  assert time.monotonic()-start<100,'Customer exit timeout'
  yield
 def cleanup():
  assert int(flow.get_editor_property('CurrentState').value)==0;assert not any(count_modals().values());assert not pc.get_editor_property('show_mouse_cursor')
  assert flow.get_editor_property('DialogueWidgetRef') is None and flow.get_editor_property('ResultWidgetRef') is None
  flow.call_method('HandleCustomerExited');flow.call_method('CloseRecordShopInteractionModals')
  assert not any(count_modals().values())
  return {'active_customer':None,'modals':count_modals(),'state':'Explore'}
 check('actual_exit_and_repeated_cleanup',cleanup)
 yield from physical_input_checks(world,flow,pawn,[(shelves[0],cls(SU)),(tt,cls(TU))],R,save)
 interaction=pawn.call_method('AddComponentByClass',args=(unreal.WidgetInteractionComponent.static_class(),False,unreal.Transform(),False))
 interaction.set_component_tick_enabled(False);interaction.activate(True)
 try:
  escape=unreal.Key();escape.import_text('Escape');other_key=unreal.Key();other_key.import_text('F10');observed=[]
  for actor,path in [(shelves[0],SU),(tt,TU)]:
   for repeat in range(2):
    interact(actor);w=widgets(path)[0]
    yield
    interaction.set_focus(w)
    yield
    interaction.press_and_release_key(other_key);assert widgets(path)==[w]
    assert interaction.press_and_release_key(escape)
    yield
    assert not widgets(path);assert not pc.get_editor_property('show_mouse_cursor')
    if path==TU:assert w.get_editor_property('TurntableRef') is None
    observed.append({'widget':path,'repeat':repeat+1,'closed_by':'synthetic Slate Escape','cursor':False})
  R['isolated']['escape_reopen_and_destroy_reference_cleanup']={'pass':True,'observations':observed};save()
 except Exception:R['isolated']['escape_reopen_and_destroy_reference_cleanup']={'pass':False,'error':traceback.format_exc()};save()
 finally:interaction.destroy_component(pawn)
 def no_record():
  statics=unreal.get_default_object(unreal.GameplayStatics);transform=unreal.Transform(location=unreal.Vector(0,0,3000));scale=unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
  a=statics.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls(TT),transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,scale));a=statics.call_method('FinishSpawningActor',args=(a,transform,scale))
  try:
   for name in ['OpenLid','PlaceRecord','SelectRPM33','MoveTonearm','PlayRecord','CompletePlayback']:a.call_method(name)
   assert a.get_editor_property('TurntableStep')==4;assert not a.get_editor_property('CompletionSent')
   return {'step':4,'completion':False}
  finally:a.destroy_actor()
 check('no_record_rejects_play_and_completion',no_record)
 if '-nosound' not in unreal.SystemLibrary.get_command_line().lower():
  # Isolated callback plumbing with an existing ENGINE notification sound.
  # This is neither authored LP audio nor part of natural customer-cycle evidence.
  statics=unreal.get_default_object(unreal.GameplayStatics);transform=unreal.Transform(location=unreal.Vector(0,0,3000));scale=unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
  a=statics.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls(TT),transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,scale));a=statics.call_method('FinishSpawningActor',args=(a,transform,scale))
  try:
   record=tt.get_editor_property('CurrentRecord');original=record.export_text()
   sound=unreal.load_asset('/Engine/EditorSounds/Notifications/CompileSuccess');assert sound
   import re
   edited=re.sub(r'(Audio_[A-Za-z0-9_]+)=None',lambda m:m[1]+'="/Script/Engine.SoundWave\''+sound.get_path_name()+'\'"',original)
   assert edited!=original;record.import_text(edited)
   a.call_method('SetRecord',args=(record,));observer.call_method(observe_method,args=(a,manager))
   before=observer.get_editor_property('Completions')
   for method in ['OpenLid','PlaceRecord','SelectRPM33','MoveTonearm','PlayRecord']:a.call_method(method)
   audio=a.get_editor_property('PlaybackAudio');assert audio and audio.is_playing(),'Audio device did not start the diagnostic sound'
   assert not a.get_editor_property('CompletionSent');assert a.get_editor_property('TurntableStep')==5
   # The owned record must remain unchanged until real audio ends.
   other=tt.get_editor_property('CurrentRecord');other.import_text(original.replace('Test_record_03','replacement-fixture'))
   a.call_method('SetRecord',args=(other,));assert 'replacement-fixture' not in a.get_editor_property('CurrentRecord').export_text()
   a.call_method('PlayRecord');assert a.get_editor_property('PlaybackAudio')==audio
   deadline=time.monotonic()+15
   while not a.get_editor_property('CompletionSent'):
    assert time.monotonic()<deadline,'Actual OnAudioFinished did not complete'
    yield
   assert observer.get_editor_property('Completions')==before+1;assert a.get_editor_property('PlaybackAudio') is None
   a.call_method('CompletePlayback');assert observer.get_editor_property('Completions')==before+1
   R['isolated']['real_audio_component_callback']={'pass':True,'source':sound.get_path_name(),'completion_delta':1,'replacement_during_playback_rejected':True,'limit':'engine notification fixture only; no authored LP asset and no audible-quality claim'};save()
  except Exception:R['isolated']['real_audio_component_callback']={'pass':False,'error':traceback.format_exc()};save()
  finally:a.destroy_actor()
 R['complete']=True;R['pass']=all(x.get('pass',True) for x in R['isolated'].values());save()

def tick(delta):
 if phase.get('busy'):return
 phase['busy']=True
 try:
  if phase['end'] is not None:
   if time.monotonic()-phase['end']>3:unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
   return
  if phase['gen'] is None:phase['gen']=run()
  assert time.monotonic()-start<150
  next(phase['gen'])
 except StopIteration:level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
