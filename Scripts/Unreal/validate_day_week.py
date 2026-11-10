"""One continuous production week: actual navigation/exit, Slate UI, ten-second audio.
Only player approach geometry is a fixture. No day/index/exit/completion state writes.
Direct calls only probe rejection of duplicates and premature day/exit transitions.
"""
import os,json,time,traceback,sys,re
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from day_graph_helpers import *
from narrative_validation_support import digest,struct_value
from record_expansion_support import candidates,DATA
REFERENCE=json.loads((ROOT/'Scripts/Unreal/narrative_reference_baseline.json').read_text(encoding='utf8'))
HISTORY_TEST=os.environ.get('MVP_HISTORY_VALIDATION')=='1'
if HISTORY_TEST:
 from history_validation_support import MemoryChecks
 memory=MemoryChecks()
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'cycles':[],'spawns':[],'scope':'production Prologue + tutorial + all 16 visits; real navigation, Slate buttons and audio; player geometry fixtures; direct calls only test rejection guards'}
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';FC=FLOW+'.BP_GameFlowManager_C'
CUSTOMER='/Game/RecordShop/Characters/Customers/Common/BP_Customer'
TT='/Game/RecordShop/Interaction/Actors/BP_Turntable';SHELF='/Game/RecordShop/Interaction/Actors/BP_RecordShelf'
DU='/Game/RecordShop/UI/Dialogue/WBP_Dialogue';SU='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect';TU='/Game/RecordShop/UI/Turntable/WBP_Turntable';RU='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
VC='/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C'
EXPECTED=[('A',1,1,1),('E',1,1,2),('B',1,2,1),('C',1,2,2),('A',2,3,1),('F',1,3,2),('D',1,3,3),('B',2,4,1),('C',2,4,2),('A',3,5,1),('G',1,5,2),('B',3,6,1),('D',2,6,2),('H',1,6,3),('TEMP_D7_01',1,7,1),('TEMP_D7_02',1,7,2)]
def save():OUT.write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
def frames(n=4):
 for _ in range(n):yield

def widgets(path):return list(unreal.WidgetLibrary.get_all_widgets_of_class(world,cls(path),True))
def wait(predicate,seconds=20):
 deadline=time.monotonic()+seconds
 while not predicate():
  assert time.monotonic()<deadline,'Timed out '+str(predicate)
  yield

def click(widget,name):
 button=widget.get_editor_property(name);assert button.get_is_enabled(),name
 interaction.set_focus(button);button.set_keyboard_focus();yield from frames(2)
 key=unreal.Key();key.import_text('Enter');assert interaction.press_and_release_key(key),name
 yield from frames(3)

def interact(actor,path):
 movement=pawn.get_component_by_class(unreal.CharacterMovementComponent);movement.stop_movement_immediately();movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
 origin,extent=actor.get_actor_bounds(False);component=pawn.get_editor_property('BPC_Interaction');found=False
 candidates=[(0,unreal.Vector(-1,0,0)),(180,unreal.Vector(1,0,0)),(90,unreal.Vector(0,-1,0)),(-90,unreal.Vector(0,1,0))]
 if path==TU:candidates=[(90,unreal.Vector(0,-1,0))]
 for yaw,offset in candidates:
  pos=origin+offset*((extent.x if offset.x else extent.y)+100);pos.z=max(origin.z,100)
  if path==TU:pos=actor.get_actor_location()+unreal.Vector(0,-105,2.2)
  pawn.set_actor_location_and_rotation(pos,unreal.Rotator(pitch=0,yaw=yaw,roll=0),False,True)
  hit=unreal.SystemLibrary.sphere_trace_single(component,pos,pos+pawn.get_actor_forward_vector()*180,60,unreal.TraceTypeQuery.ECC_INTERACTABLE,False,[],unreal.DrawDebugTrace.NONE,True)
  if hit and actor.get_name() in hit.export_text():found=True;break
 assert found,actor.get_name()
 yield from frames()
 sub.inject_input_vector_for_action(unreal.load_asset('/Game/RecordShop/Input/IA_Interact'),unreal.Vector(1,0,0),[],[])
 yield from frames()
 assert len(widgets(path))==1,path
 if path==TU:movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING)

# Unsaved observer records the actual production dispatchers, including duplicates.
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_DayObserver','/Game/RecordShop/Dev/DayValidation',unreal.Blueprint,factory)
observer_fields=[('StartedDays','int'),('EndedDays','int'),('FinishedIDs','name'),('FinishedVisits','int'),('FinalEvents','name')]
if HISTORY_TEST:observer_fields += [('MemoryIDs','name'),('MemoryVisits','int'),('MemoryPrevious','bool')]
for name,kind in observer_fields:assert L.add_member_variable(probe,name,L.get_array_type(L.get_basic_type_by_name(kind)))
assert L.compile_blueprint(probe)
# Unsaved observer distinguishes natural EOF loops from accidental restarts.
assert L.add_member_variable(probe,'NaturalBGMFinishes',L.get_basic_type_by_name('int'))
assert L.compile_blueprint(probe)
ambient_event=signature_event(probe,'ObserveAmbientFinish',[]);g=evgraph(probe)
assign(g,ambient_event.find_then_pin(),'NaturalBGMFinishes',calc(g,'Add_IntInt',A=get(g,'NaturalBGMFinishes'),B=1))
ambient_bind=signature_event(probe,'BindAmbientFinish',[('Audio',L.get_object_reference_type(unreal.AudioComponent))]);g=evgraph(probe)
node=action(g,'Bind Event to On Audio Finished',[pin(ambient_bind,'Audio',True)],unreal.AudioComponent)
link(pin(ambient_bind,'Audio',True),pin(node,'self'));link(pin(ambient_event,'OutputDelegate',True),pin(node,'Delegate'));link(ambient_bind.find_then_pin(),node.find_execute_pin())
ambient_bind_name=str(ambient_bind.get_node_title())
events=[]
event_specs=[
 ('OnDayStarted',[('Day',L.get_basic_type_by_name('int'))],[('StartedDays','Day')]),
 ('OnDayEnded',[('Day',L.get_basic_type_by_name('int'))],[('EndedDays','Day')]),
 ('OnCustomerVisitCompleted',[('Visit',L.get_object_reference_type(unreal.load_class(None,VC)))],[('FinishedIDs','CustomerID'),('FinishedVisits','VisitNumber')]),
 ('OnFinalStoryEvent',[('EventID',L.get_basic_type_by_name('name'))],[('FinalEvents','EventID')])]
if HISTORY_TEST:event_specs.append(('OnRevisitMemoryReady',[('CustomerID',L.get_basic_type_by_name('name')),('VisitNumber',L.get_basic_type_by_name('int')),('HasPrevious',L.get_basic_type_by_name('bool'))],[('MemoryIDs','CustomerID'),('MemoryVisits','VisitNumber'),('MemoryPrevious','HasPrevious')]))
for dispatcher,parameters,fields in event_specs:
 event=signature_event(probe,'Observe'+dispatcher,parameters);g=evgraph(probe);end=event.find_then_pin()
 for member,source in fields:
  value=field(g,pin(event,'Visit',True),source,VC) if dispatcher=='OnCustomerVisitCompleted' else pin(event,source,True)
  add=call(g,'/Script/Engine.KismetArrayLibrary.Array_Add');link(get(g,member),pin(add,'TargetArray'));link(value,pin(add,'NewItem'));link(end,add.find_execute_pin());end=add.find_then_pin()
 events.append((dispatcher,event))
observer_bind=signature_event(probe,'BindDayEvents',[('Flow',L.get_object_reference_type(cls(FLOW)))])
g=evgraph(probe);end=observer_bind.find_then_pin()
for name,event in events:
 bind=action(g,'Bind Event to '+name,[pin(observer_bind,'Flow',True)],cls(FLOW));link(pin(event,'OutputDelegate',True),pin(bind,'Delegate'));link(end,bind.find_execute_pin());end=bind.find_then_pin()
assert L.compile_blueprint(probe);observer=unreal.get_default_object(probe.generated_class());bind_name=str(observer_bind.get_node_title())

def observed():
 return {key:[str(x) if key in ('FinishedIDs','FinalEvents','MemoryIDs') else int(x) for x in observer.get_editor_property(key)] for key in (['StartedDays','EndedDays','FinishedIDs','FinishedVisits','FinalEvents']+(['MemoryIDs','MemoryVisits','MemoryPrevious'] if HISTORY_TEST else []))}
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();started=time.monotonic();phase={'gen':None,'end':None,'busy':False}
def run():
 global world,flow,pc,pawn,interaction,sub
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_all_actors_of_class(world,cls(FLOW))[0];pc=unreal.GameplayStatics.get_player_controller(world,0);pawn=unreal.GameplayStatics.get_player_pawn(world,0)
 observer.call_method(bind_name,args=(flow,))
 interaction=pawn.call_method('AddComponentByClass',args=(unreal.WidgetInteractionComponent.static_class(),False,unreal.Transform(),False));interaction.set_component_tick_enabled(False);interaction.activate(True)
 lib=unreal.get_default_object(unreal.load_class(None,'/Script/Engine.SubsystemBlueprintLibrary'));sub=lib.call_method('GetLocalPlayerSubSystemFromPlayerController',args=(pc,unreal.EnhancedInputLocalPlayerSubsystem.static_class()))
 from prologue_validation_support import exercise_opening
 def advance(panel):yield from click(panel,'Continue')
 R['opening']=yield from exercise_opening(world,flow,pc,pawn,advance);save()
 tt=flow.get_editor_property('TurntableRef');shelf=unreal.GameplayStatics.get_all_actors_of_class(world,cls(SHELF))[0]
 home=pawn.get_actor_transform();home_control=pc.get_control_rotation();previous_day=0;previous_bgm_id=None
 for index in range(17):
  yield from wait(lambda:len(widgets(DU))==1,35)
  customer=flow.get_editor_property('ActiveCustomer');assert customer
  assert len(unreal.GameplayStatics.get_all_actors_of_class(world,cls(CUSTOMER)))==1,'Duplicate customer'
  current_day=flow.get_editor_property('CurrentDay');visit=flow.get_editor_property('ActiveVisit')
  if current_day!=previous_day or index==0:
   assert flow.get_editor_property('StoreBGMRef')is None and not flow.get_editor_property('StoreBGMRequested')
   assert str(flow.get_editor_property('CurrentStoreBGMRecordID'))=='None'
   if current_day>0:
    assert not tt.get_editor_property('HasRecord')and str(struct_value(tt.get_editor_property('CurrentRecord'),'RecordID'))=='None'
   R.setdefault('day_audio_reset',[]).append(current_day)
  elif previous_bgm_id:
   ambient=flow.get_editor_property('StoreBGMRef');assert ambient and ambient.is_playing()
   assert str(flow.get_editor_property('CurrentStoreBGMRecordID'))==previous_bgm_id
   ok,prior=flow.get_editor_property('RecordCatalogue').call_method('ResolvePlayableRecord',args=(previous_bgm_id,));assert ok and ambient.get_editor_property('sound')==struct_value(prior,'Audio')
   R.setdefault('dialogue_bgm',[]).append({'customer_index':index,'record':previous_bgm_id,'component':ambient.get_path_name()})
  dialogue_bgm=flow.get_editor_property('StoreBGMRef')
  dialogue_bgm_path=dialogue_bgm.get_path_name()if dialogue_bgm else None
  dialogue_finish_count=observer.get_editor_property('NaturalBGMFinishes')
  if dialogue_bgm:observer.call_method(ambient_bind_name,args=(dialogue_bgm,))
  dialogue_bgm=None
  if index==0:
   assert current_day==0 and visit is None and not flow.get_editor_property('TutorialComplete')
   expected=('TUTORIAL',0,0,0)
  else:
   expected=EXPECTED[index-1];assert flow.get_editor_property('TutorialComplete')
   actual=(str(visit.get_editor_property('CustomerID')),visit.get_editor_property('VisitNumber'),current_day,visit.get_editor_property('OrderInDay'))
   assert actual==expected,(actual,expected)
   assert flow.get_editor_property('CurrentCustomerIndex')==expected[3]-1
   profile=customer.get_editor_property('CustomerProfile');field_name=re.search(r'CustomerID_[A-Za-z0-9_]+(?==)',profile.export_text()).group(0)
   assert str(profile.get_editor_property(field_name))==expected[0],profile.export_text()
  if HISTORY_TEST:memory.before(flow,expected,index)
  actor_path=customer.get_path_name();assert actor_path not in [x['actor'] for x in R['spawns']]
  R['spawns'].append({'actor':actor_path,'id':expected[0],'visit':expected[1],'day':expected[2],'order':expected[3]});R['events']=observed();save();unreal.log('DAY_VALIDATION_VISIT '+str(expected))
  # Direct negative probes must not advance or produce another pawn.
  before=(flow.get_editor_property('CurrentDay'),flow.get_editor_property('CurrentCustomerIndex'),flow.get_editor_property('ActiveCustomer'))
  for _ in range(3):
   flow.call_method('SpawnQueuedCustomer');flow.call_method('SpawnTutorialCustomer');flow.call_method('HandleCustomerExited');flow.call_method('EndCurrentDay');flow.call_method('FinishDayTransition')
  assert before==(flow.get_editor_property('CurrentDay'),flow.get_editor_property('CurrentCustomerIndex'),flow.get_editor_property('ActiveCustomer'))
  manager=flow.get_editor_property('DialogueManagerRef')
  if index==0:assert str(struct_value(customer.get_editor_property('CustomerProfile'),'CustomerID'))=='TUTORIAL' and str(manager.get_editor_property('ActiveSequenceID'))=='TUTORIAL_Training'
  if index==1:assert list(map(str,manager.get_editor_property('DialogueList')))==['C01_Quiet_%02d'%i for i in range(1,6)] and str(manager.get_editor_property('ActiveSequenceID'))=='A_Visit1'
  R.setdefault('dialogue_sequences',[]).append({'customer':expected[0],'visit':expected[1],'sequence':str(manager.get_editor_property('ActiveSequenceID')),'rows':list(map(str,manager.get_editor_property('DialogueList')))})
  sequence_rows=list(map(str,manager.get_editor_property('DialogueList')))
  if expected[0]=='A'and expected[1]in (2,3):
   from customer_a_validation_support import expected_a_rows
   def previous_result(num):
    e=flow.call_method('GetRecommendationForVisit',args=('A',num));return str(e.get_editor_property('RecommendationResult'))if e else None
   assert str(manager.get_editor_property('ActiveSequenceID'))=='A_Visit'+str(expected[1])
   assert sequence_rows==expected_a_rows(expected[1],previous_result(1),previous_result(2)if expected[1]==3 else None)
  elif expected[0]=='B':
   from customer_b_validation_support import expected_b_rows
   def previous_b_result(num):
    e=flow.call_method('GetRecommendationForVisit',args=('B',num));return str(e.get_editor_property('RecommendationResult'))if e else None
   assert str(manager.get_editor_property('ActiveSequenceID'))=='B_V'+str(expected[1])
   assert sequence_rows==expected_b_rows(expected[1],previous_b_result(1)if expected[1]>1 else None,previous_b_result(2)if expected[1]==3 else None)
  elif expected[0]in ('C','D'):
   from customer_cd_validation_support import expected_cd_rows
   prior=flow.call_method('GetRecommendationForVisit',args=(expected[0],1))if expected[1]==2 else None
   assert str(manager.get_editor_property('ActiveSequenceID'))==expected[0]+'_V'+str(expected[1])
   assert sequence_rows==expected_cd_rows(expected[0],expected[1],str(prior.get_editor_property('RecommendationResult'))if prior else None)
  elif expected[0]in ('E','F','G','H'):
   from customer_efgh_validation_support import expected_efgh_rows
   assert str(manager.get_editor_property('ActiveSequenceID'))==expected[0]+'_V1'
   assert sequence_rows==expected_efgh_rows(expected[0])
   assert not flow.call_method('GetActiveVisitMemory')[3]and not flow.get_editor_property('NarrativeMemoryVisits')
  else:assert len(sequence_rows)==5
  active_profile=customer.get_editor_property('CustomerProfile')
  profile_tags=[str(struct_value(active_profile,k))for k in ('Mood','MusicPreference','Personality')]
  from customer_cd_validation_support import PROFILES
  from customer_efgh_validation_support import PROFILES as SINGLE_PROFILES
  PROFILES={**PROFILES,**SINGLE_PROFILES}
  expected_tags=list(PROFILES[expected[0]])if expected[0]in PROFILES else ['Restless'if expected[1]==1 else 'Quiet','Electronic','Adventurous']if expected[0]=='B'else ['Quiet','Jazz','Traditional']
  assert profile_tags==expected_tags
  R.setdefault('runtime_profiles',[]).append({'customer':expected[0],'visit':expected[1],'tags':profile_tags})
  lines=0;seen=[]
  while widgets(DU):
   lines+=1;assert lines<=len(sequence_rows)
   seen.append(str(widgets(DU)[0].get_editor_property('DialogueText').get_text()))
   if expected[0]=='A'and expected[1]in (2,3):
    capture=OUT.with_name(OUT.stem+'-A'+str(expected[1])+'-line'+str(lines)+'.png')
    unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(capture)+'" -nosuffix')
    R.setdefault('a_revisit_ui_captures',[]).append(str(capture));yield from frames(4)
   if expected[0]=='B':
    capture=OUT.with_name(OUT.stem+'-B'+str(expected[1])+'-line'+str(lines)+'.png')
    unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(capture)+'" -nosuffix')
    R.setdefault('b_ui_captures',[]).append(str(capture));yield from frames(4)
   if expected[0]in ('C','D'):
    capture=OUT.with_name(OUT.stem+'-'+expected[0]+str(expected[1])+'-line'+str(lines)+'.png')
    unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(capture)+'" -nosuffix')
    R.setdefault('cd_ui_captures',[]).append(str(capture));yield from frames(4)
   if expected[0]in SINGLE_PROFILES:
    capture=OUT.with_name(OUT.stem+'-'+expected[0]+'1-line'+str(lines)+'.png')
    unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(capture)+'" -nosuffix')
    R.setdefault('efgh_ui_captures',[]).append(str(capture));yield from frames(4)
   yield from click(widgets(DU)[0],'Next')
  assert lines==len(sequence_rows)
  if expected[0]=='A'and expected[1]in (2,3):
   authored=json.loads((Path(unreal.Paths.project_dir())/'Scripts/Unreal/customer_a_dialogue.json').read_text(encoding='utf-8-sig'))['rows']
   assert seen==[authored[row]for row in sequence_rows]
  if expected[0]=='B':
   authored=json.loads((Path(unreal.Paths.project_dir())/'Scripts/Unreal/customer_b_dialogue.json').read_text(encoding='utf-8-sig'))['rows']
   assert seen==[authored[row]for row in sequence_rows]
  if expected[0]in ('C','D'):
   authored=json.loads((ROOT/'Scripts/Unreal/customer_cd_dialogue.json').read_text(encoding='utf-8-sig'))[expected[0]]['rows']
   assert seen==[authored[row]for row in sequence_rows]
  if expected[0]in SINGLE_PROFILES:
   authored=json.loads((ROOT/'Scripts/Unreal/customer_efgh_dialogue.json').read_text(encoding='utf8'))[expected[0]]['rows']
   assert seen==[authored[row]for row in sequence_rows]
  if index==1:assert digest(seen)==REFERENCE['a1_display_lines_sha256']
  assert not manager.get_editor_property('DialogueList') and manager.get_editor_property('ActiveDialogueSource') is None and manager.get_editor_property('PendingDialogueSource') is None
  assert pc.get_view_target()==pawn and not pc.get_editor_property('show_mouse_cursor')
  yield from interact(shelf,SU)
  choice=(2 if index==1 else index%3+1)if HISTORY_TEST else index%3+1
  if expected[0]=='B':choice=3 if expected[1]==1 else 4
  elif expected[0]in ('C','G'):choice=5
  elif expected[0]in ('D','H'):choice=6
  elif expected[0]in SINGLE_PROFILES:choice={'E':2,'F':3}[expected[0]]
  ids=candidates(expected[0],expected[1]);selection=widgets(SU)[0]
  assert list(map(str,flow.call_method('GetActiveCandidateRecordIDs')))==ids
  assert list(map(str,selection.get_editor_property('ResolvedCandidateIDs')))==ids
  card_evidence=[]
  for slot,identity in enumerate(ids,1):
   card=selection.get_editor_property('CardRecord'+str(slot));button=selection.get_editor_property('BTN_LP0'+str(slot))
   assert str(struct_value(card,'RecordID'))==identity and button.get_is_enabled()
   cover=struct_value(card,'Cover');image=button.get_content().get_child_at(0)
   assert image.get_editor_property('brush').get_editor_property('resource_object')==cover
   assert image.is_visible()if cover else image.get_visibility()==unreal.SlateVisibility.COLLAPSED
   card_evidence.append({'slot':slot,'record':identity,'cover':cover.get_path_name()if cover else None})
  capture=OUT.with_name(OUT.stem+'-'+expected[0]+str(expected[1])+'-candidates.png')
  unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(capture)+'" -nosuffix');yield from frames(4)
  R.setdefault('candidate_ui',[]).append({'customer':expected[0],'visit':expected[1],'cards':card_evidence,'capture':str(capture)})
  if dialogue_bgm_path:
   ambient=flow.get_editor_property('StoreBGMRef');assert ambient and ambient.is_playing()
   assert str(flow.get_editor_property('CurrentStoreBGMRecordID'))==previous_bgm_id
   ok,prior=flow.get_editor_property('RecordCatalogue').call_method('ResolvePlayableRecord',args=(previous_bgm_id,));assert ok and ambient.get_editor_property('sound')==struct_value(prior,'Audio')
   finishes=observer.get_editor_property('NaturalBGMFinishes')-dialogue_finish_count
   if ambient.get_path_name()!=dialogue_bgm_path:
    assert finishes>0,'Dialogue restarted BGM without natural audio completion'
    R.setdefault('natural_dialogue_loops',[]).append({'customer_index':index,'record':previous_bgm_id,'before':dialogue_bgm_path,'after':ambient.get_path_name(),'natural_finishes':finishes})
   else:assert finishes==0
   assert len([a for a in unreal.ObjectIterator(unreal.AudioComponent)if a.is_playing()and a.get_world()==world])==1
  selected_id='RS00'+str(choice);slot=ids.index(selected_id)+1
  selected_record=selection.get_editor_property('CardRecord'+str(slot));selected_audio=struct_value(selected_record,'Audio');assert selected_audio
  old_bgm=flow.get_editor_property('StoreBGMRef');old_bgm_path=old_bgm.get_path_name()if old_bgm else None
  old_bgm=None
  yield from click(selection,'BTN_LP0'+str(slot))
  assert not flow.get_editor_property('StoreBGMRequested')
  from customer_b_validation_support import expected_score
  score=expected_score(expected[0],expected[1],choice)
  assert flow.get_editor_property('RawRecommendationScore')==score
  assert str(struct_value(tt.get_editor_property('CurrentRecord'),'RecordID'))==selected_id
  assert struct_value(tt.get_editor_property('CurrentRecord'),'Audio')==selected_audio
  if HISTORY_TEST:memory.selected(flow)
  yield from interact(tt,TU);panel=widgets(TU)[0]
  for button in ('BTN_OpenLid','BTN_PlaceRecord','BTN_SelectRPM','BTN_RPM33','BTN_MoveTonearm','BTN_Play'):
   yield from wait(lambda:panel.get_editor_property(button).get_is_enabled(),8)
   yield from click(panel,button)
  audio=tt.get_editor_property('PlaybackAudio');assert audio and audio.is_playing()
  assert flow.get_editor_property('StoreBGMRef')is None
  assert old_bgm_path not in [a.get_path_name()for a in unreal.ObjectIterator(unreal.AudioComponent)if a.is_playing()and a.get_world()==world],'Previous BGM overlaps Listening'
  assert audio.get_editor_property('sound')==selected_audio,(selected_id,audio.get_editor_property('sound'),selected_audio)
  listen_start=unreal.GameplayStatics.get_time_seconds(world)
  yield from wait(lambda:len(widgets(RU))==1,16)
  elapsed=unreal.GameplayStatics.get_time_seconds(world)-listen_start;assert 9.5<=elapsed<=14,elapsed
  assert tt.get_editor_property('PlaybackAudio') is None
  result_bgm=flow.get_editor_property('StoreBGMRef');assert result_bgm and result_bgm.is_playing()
  assert result_bgm.get_editor_property('sound')==selected_audio and str(flow.get_editor_property('CurrentStoreBGMRecordID'))==selected_id
  result_bgm_path=result_bgm.get_path_name();result_finish_count=observer.get_editor_property('NaturalBGMFinishes')
  observer.call_method(ambient_bind_name,args=(result_bgm,));result_bgm=None
  if HISTORY_TEST:memory.result(flow,expected,index,choice)
  result=widgets(RU)[0];assert result.get_editor_property('Continue').has_keyboard_focus()
  if expected[0]in ('B','C','D','E','F','G','H'):
   from customer_b_validation_support import expected_result
   neutral=json.loads((Path(unreal.Paths.project_dir())/'Scripts/Unreal/preference_result_feedback.json').read_text(encoding='utf-8-sig'))
   feedback=str(result.get_editor_property('ScoreStatus').get_text());assert feedback==neutral[expected_result(score)]
   R.setdefault('b_result_feedback'if expected[0]=='B'else 'efgh_result_feedback'if expected[0]in SINGLE_PROFILES else 'cd_result_feedback',[]).append({'customer':expected[0],'visit':expected[1],'score':score,'text':feedback})
   capture=OUT.with_name(OUT.stem+'-'+expected[0]+str(expected[1])+'-result.png')
   unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(capture)+'" -nosuffix');R.setdefault('b_ui_captures'if expected[0]=='B'else 'efgh_ui_captures'if expected[0]in SINGLE_PROFILES else 'cd_ui_captures',[]).append(str(capture));yield from frames(4)
  # Virtual Slate user activation; production owning-user focus is asserted above.
  yield from click(result,'Continue')
  store=flow.get_editor_property('StoreBGMRef');assert store and store.is_playing()
  if store.get_path_name()!=result_bgm_path:assert observer.get_editor_property('NaturalBGMFinishes')>result_finish_count,'Continue restarted BGM without natural completion'
  assert store.get_editor_property('sound')==selected_audio
  previous_day=current_day;previous_bgm_id=selected_id
  # Restore fixture-only approach location so the player cannot block the exit route.
  pawn.set_actor_transform(home,False,True);pc.set_control_rotation(home_control)
  yield from wait(lambda:flow.get_editor_property('ActiveCustomer') is None,15)
  assert pc.get_view_target()==pawn and not pc.get_editor_property('show_mouse_cursor')
  assert not any(widgets(p) for p in (DU,SU,TU,RU))
  for _ in range(3):flow.call_method('HandleCustomerExited')
  R['cycles'].append({'id':expected[0],'visit':expected[1],'day':expected[2],'listening_to_result_seconds':elapsed,'choice':choice,'slot':slot,'candidates':ids,'audio':selected_audio.get_path_name(),'score':score,'store_bgm_played':True,'store_bgm_id':selected_id,'store_bgm_component':result_bgm_path,'no_overlap':True,'continue_no_restart':True,'recovered':True});R['events']=observed();save()
 assert set(DATA['records']).issubset({'RS00'+str(c['choice'])for c in R['cycles']})
 yield from wait(lambda:flow.get_editor_property('FinalStoryEventTriggered'),8)
 events=observed();assert events['StartedDays']==events['EndedDays']==list(range(1,8)),events
 assert list(zip(events['FinishedIDs'],events['FinishedVisits']))==[(x[0],x[1]) for x in EXPECTED],events
 assert events['FinalEvents']==['FinalStoryEvent'],events
 for _ in range(5):flow.call_method('FinishDayTransition');flow.call_method('EndCurrentDay');flow.call_method('SpawnQueuedCustomer')
 until=time.monotonic()+1
 while time.monotonic()<until:yield
 assert observed()==events and flow.get_editor_property('CurrentDay')==7 and str(flow.get_editor_property('DayPhase'))=='FinalStoryEvent'
 assert flow.get_editor_property('ActiveCustomer') is None and not unreal.GameplayStatics.get_all_actors_of_class(world,cls(CUSTOMER))
 assert flow.get_editor_property('StoreBGMRef') is None and not flow.get_editor_property('StoreBGMRequested')
 before=pawn.get_actor_location();until=time.monotonic()+.35
 while time.monotonic()<until:
  sub.inject_input_vector_for_action(unreal.load_asset('/Game/Input/Actions/IA_Move'),unreal.Vector(0,-.25,0),[],[]);yield
 assert (pawn.get_actor_location()-before).length()>5
 R.update(complete=True,**{'pass':True},events=events,final_day=7,queue_visits=16,tutorial_customers=1)
 if HISTORY_TEST:
  interaction.destroy_component(pawn)
  R['complete']=False;R['pass']=False
  R['history']=memory.finish(flow)
  assert events['MemoryIDs']==[x[0] for x in EXPECTED] and events['MemoryVisits']==[x[1] for x in EXPECTED]
  assert events['MemoryPrevious']==[int(x[1]>1) for x in EXPECTED]
  # A New Game is a fresh world/manager, exactly as production map startup.
  level.editor_request_end_play()
  while editor.get_game_world():yield
  level.editor_request_begin_play()
  while not editor.get_game_world():yield
  fresh_world=editor.get_game_world();fresh=unreal.GameplayStatics.get_all_actors_of_class(fresh_world,cls(FLOW))[0]
  assert not fresh.get_editor_property('RecommendationHistory') and fresh.get_editor_property('CurrentDay')==0 and not fresh.get_editor_property('TutorialComplete')
  for identity in ('A','B','C','D','E','F','G','H'):
   assert not fresh.call_method('HasPreviousVisit',args=(identity,)) and not fresh.call_method('GetRecommendationHistory',args=(identity,))
  R['history']['new_game_fresh_session_empty']=True
  R['complete']=True;R['pass']=True
 if not HISTORY_TEST:interaction.destroy_component(pawn)
 save()

def tick(delta):
 if phase['busy']:return
 phase['busy']=True
 try:
  if phase['end'] is not None:
   if time.monotonic()-phase['end']>3:
    unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if phase['gen'] is None:phase['gen']=run()
  assert time.monotonic()-started<850,'Full week timeout'
  next(phase['gen'])
 except StopIteration:level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
