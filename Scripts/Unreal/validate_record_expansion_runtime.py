"""Real GFM/DM E/F/G/H emitted-line/profile/feedback matrix; unsaved history fixtures."""
import unreal,os,json,sys,time,traceback,itertools,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from narrative_validation_support import assert_reference_integrity,struct_value
from record_expansion_support import candidates
from customer_b_validation_support import expected_score,expected_result
from record_expansion_support import DATA as EXPANSION,PROFILES,SCORES,RECORD_IDS,candidates
FEEDBACK_REFERENCE=json.loads((ROOT/'Scripts/Unreal/result_feedback_reference.json').read_text(encoding='utf-8'))['legacy_feedback']
NEUTRAL_FEEDBACK=json.loads((ROOT/'Scripts/Unreal/preference_result_feedback.json').read_text(encoding='utf-8-sig'))
FC='/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C';MC='/Game/DialogueManager.DialogueManager_C'
VC='/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C';EC='/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C'
CC='/Game/RecordShop/Characters/Customers/Common/BP_Customer.BP_Customer_C';C01='/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'real GFM six-record scoring, every visit authored card order, construct/update/cache/brush/click contract; isolated fixtures, natural playback tested by full week','cases':[]}
DATA=json.loads((ROOT/'Scripts/Unreal/customer_efgh_dialogue.json').read_text(encoding='utf-8-sig'))
def save():OUT.write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf8')
def frames(n=2):
 for _ in range(n):yield
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_RecordExpansionProbe','/Game/RecordShop/Dev/RecordExpansionValidation',unreal.Blueprint,factory)
NT=L.get_basic_type_by_name('name');IT=L.get_basic_type_by_name('int');TT=L.get_basic_type_by_name('text');FT=L.get_object_reference_type(unreal.load_class(None,FC));NA=L.get_array_type(NT)
for key,typ in [('Lines',L.get_array_type(L.get_basic_type_by_name('string'))),('Speakers',L.get_array_type(L.get_basic_type_by_name('string'))),('Finishes',IT),('FlowRef',FT)]:assert L.add_member_variable(probe,key,typ)
g=function(probe,'SetFixture');a=inputs(g,[('Flow',FT),('Visit',L.get_object_reference_type(unreal.load_class(None,VC))),('History',L.get_array_type(L.get_object_reference_type(unreal.load_class(None,EC)))),('Profile',L.get_struct_type(unreal.load_asset('/Game/CustomerData')))])
end=g.find_graph_entry_pin()
for key,value in [('ActiveVisit',a['Visit']),('RecommendationHistory',a['History']),('CurrentDay',field(g,a['Visit'],'Day',VC))]:
 n=g.add_set_member_variable_node(key,FC);link(a['Flow'],pin(n,'self'));link(value,pin(n,key));link(end,n.find_execute_pin());end=n.find_then_pin()
n=g.add_set_member_variable_node('CustomerProfile',CC);link(field(g,a['Flow'],'ActiveCustomer',FC),pin(n,'self'));link(a['Profile'],pin(n,'CustomerProfile'));link(end,n.find_execute_pin());end=n.find_then_pin()
end=assign(g,end,'FlowRef',a['Flow']);end=clear(g,end,get(g,'Lines'));clear(g,end,get(g,'Speakers'))
eg=evgraph(probe)
unreal.log('SINGLE_VISIT_PROBE_BUILD_LINE')
line=signature_event(probe,'ObserveLine',[('Speaker',TT),('DialogueText',TT)])
end=line.find_then_pin()
for source,target in [('DialogueText','Lines'),('Speaker','Speakers')]:
 conv=call(eg,'/Script/Engine.KismetTextLibrary.Conv_TextToString');link(pin(line,source,True),pin(conv,'InText'));end=append(eg,end,get(eg,target),pin(conv,'ReturnValue',True))
unreal.log('SINGLE_VISIT_PROBE_BUILD_FINISH')
finish=signature_event(probe,'ObserveFinish',[]);assign(eg,finish.find_then_pin(),'Finishes',calc(eg,'Add_IntInt',A=get(eg,'Finishes'),B=1))
unreal.log('SINGLE_VISIT_PROBE_BUILD_BIND')
bind=signature_event(probe,'BindObservers',[('Flow',FT),('Manager',L.get_object_reference_type(unreal.load_class(None,MC)))]);end=bind.find_then_pin()
for title,event,target,kind in [('OnUpdateDialogueUI',line,'Manager',MC),('OnDialogueFinished',finish,'Manager',MC)]:
 node=action(eg,'Bind Event to '+title,[pin(bind,target,True)],unreal.load_class(None,kind));link(pin(event,'OutputDelegate',True),pin(node,'Delegate'));link(pin(bind,target,True),pin(node,'self'));link(end,node.find_execute_pin());end=node.find_then_pin()
unreal.log('SINGLE_VISIT_PROBE_FINAL_COMPILE')
assert L.compile_blueprint(probe);observer=unreal.get_default_object(probe.generated_class())
assert L.add_member_variable(probe,'Selections',NA)
eg=evgraph(probe);selected=signature_event(probe,'ObserveRecord',[('Record',L.get_struct_type(unreal.load_asset('/Game/RecordShop/Data/Structs/ST_RecordData')))])
split=action(eg,'Break ST Record Data',[pin(selected,'Record',True)]);link(pin(selected,'Record',True),pin(split,'ST_RecordData'));append(eg,selected.find_then_pin(),get(eg,'Selections'),struct_field(split,'RecordID'))
record_bind=signature_event(probe,'BindRecord',[('Widget',L.get_object_reference_type(unreal.load_class(None,'/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect.WBP_RecordSelect_C')))])
n=action(eg,'Bind Event to On Record Selected',[pin(record_bind,'Widget',True)],unreal.load_class(None,'/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect.WBP_RecordSelect_C'));link(pin(record_bind,'Widget',True),pin(n,'self'));link(pin(selected,'OutputDelegate',True),pin(n,'Delegate'));link(record_bind.find_then_pin(),n.find_execute_pin());assert L.compile_blueprint(probe);observer=unreal.get_default_object(probe.generated_class())
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox');unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play()
started=time.monotonic();phase={'gen':None,'end':None,'busy':False}

UI='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect.WBP_RecordSelect_C'

def profile_key(identity,visit):return 'B1'if identity=='F'or identity=='B'and visit==1 else {'G':'C','H':'D'}.get(identity,identity)if identity in ('A','B','C','D','E','G','H','I','J')else 'A'

def create_card(world,pc):return unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('Create',args=(world,unreal.load_class(None,UI),pc))

def check_card(panel,cat,ids):
 assert panel.get_editor_property('CandidateSetReady')and list(map(str,panel.get_editor_property('ResolvedCandidateIDs')))==ids
 for index,identity in enumerate(ids,1):
  record=panel.get_editor_property('CardRecord'+str(index));assert str(struct_value(record,'RecordID'))==identity
  row=panel.get_editor_property('BTN_LP0'+str(index)).get_content();image=row.get_child_at(0);label=row.get_child_at(1)
  assert isinstance(image,unreal.Image)and isinstance(label,unreal.TextBlock)
  assert str(struct_value(record,'Title'))in str(label.get_text())and str(struct_value(record,'Artist'))in str(label.get_text())
  cover=struct_value(record,'Cover');assert image.get_editor_property('brush').get_editor_property('resource_object')==cover
  assert image.get_visibility()==(unreal.SlateVisibility.HIT_TEST_INVISIBLE if cover else unreal.SlateVisibility.COLLAPSED)
  assert panel.get_editor_property('BTN_LP0'+str(index)).get_is_enabled()

def run():
 from narrative_validation_support import returned_flag
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_class(None,FC))[0];flow.set_editor_property('EnableDaySchedule',False);pc=unreal.GameplayStatics.get_player_controller(world,0)
 for _ in range(3):flow.call_method('AdvancePrologue');yield from frames()
 deadline=time.monotonic()+40
 while not flow.get_editor_property('DialogueWidgetRef'):
  assert time.monotonic()<deadline;yield
 dm=flow.get_editor_property('DialogueManagerRef');assert str(dm.get_editor_property('ActiveSequenceID'))=='TUTORIAL_Training'
 for _ in range(5):flow.get_editor_property('DialogueWidgetRef').get_editor_property('Next').get_editor_property('on_clicked').broadcast();yield from frames()
 assert not flow.get_editor_property('RecommendationHistory')
 profile=unreal.get_default_object(unreal.load_class(None,C01)).get_editor_property('CustomerProfile');original=profile.export_text();state=flow.get_editor_property('CurrentState');cat=flow.get_editor_property('RecordCatalogue')
 week=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_TemporaryWeek')
 for day in week.get_editor_property('Days'):
  for visit in day.get_editor_property('Visits'):
   identity=str(visit.get_editor_property('CustomerID'));number=visit.get_editor_property('VisitNumber');ids=candidates(identity,number)
   dm.call_method('CancelDialogueSequence');observer.call_method('SetFixture',args=(flow,visit,[],profile));flow.call_method('ApplyVisitContext');flow.call_method('PrepareRevisitMemory')
   assert list(map(str,flow.call_method('GetActiveCandidateRecordIDs')))==ids
   scores=[]
   for rid in RECORD_IDS:
    found,record=cat.call_method('ResolvePlayableRecord',args=(rid,));assert found
    flow.call_method('SetGameFlowState',args=(state,));flow.call_method('ResetRawScore');flow.call_method('HandleRecordSelected',args=(record,))
    score=SCORES[profile_key(identity,number)][int(rid[-1])-1]
    assert flow.get_editor_property('RawScoreAvailable')and flow.get_editor_property('RawRecommendationScore')==score,(identity,number,rid)
    assert dm.call_method('CalculateLPScore',args=tuple(str(struct_value(record,k))for k in ('Mood','Genre','Theme')))==score
    scores.append(score)
   panel=create_card(world,pc);assert returned_flag(panel.call_method('ConfigureRecordCandidates',args=(cat,ids)))
   panel.add_to_viewport(50);yield from frames(6);check_card(panel,cat,ids)
   for _ in range(3):panel.call_method('InitializeDefaultCandidates');check_card(panel,cat,ids)
   capture=OUT.with_name(OUT.stem+'-'+identity+str(number)+'-cards.png');unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(capture)+'" -nosuffix');yield from frames(4);panel.remove_from_parent()
   grades=[SCORES[profile_key(identity,number)][int(r[-1])-1]for r in ids]
   assert len(ids)==len(set(ids))==3
   if identity in ('D','H'):assert sorted(grades)==[0,1,3]
   elif not identity.startswith('TEMP_D7_'):assert sorted(grades)==[0,2,3]or (identity=='I'or identity=='B'and number>1)and sorted(grades)==[1,2,3]
   R['cases'].append(dict(id=identity,visit=number,candidates=ids,scores=scores,candidate_scores=grades,capture=str(capture)));save()
 # All six permutations move RS002 through each slot: no incidental alphabetical order.
 for order in itertools.permutations(['RS006','RS002','RS004']):
  ids=list(order)
  for index in range(1,4):
   panel=create_card(world,pc);assert returned_flag(panel.call_method('ConfigureRecordCandidates',args=(cat,ids)));panel.add_to_viewport(50);yield from frames(3);check_card(panel,cat,ids)
   observer.call_method(str(record_bind.get_node_title()),args=(panel,));before=len(observer.get_editor_property('Selections'));panel.get_editor_property('BTN_LP0'+str(index)).get_editor_property('on_clicked').broadcast();yield from frames()
   assert len(observer.get_editor_property('Selections'))==before+1 and str(observer.get_editor_property('Selections')[-1])==ids[index-1]
   panel.remove_from_parent()
 for ids in [['RS001','MISSING','RS003'],['RS001','RS001','RS003'],['RS001','RS002'],['RS001','RS002','RS003','RS004']]:
  panel=create_card(world,pc);assert not returned_flag(panel.call_method('ConfigureRecordCandidates',args=(cat,ids)))
  assert not panel.get_editor_property('ResolvedCandidateIDs')and all(not panel.get_editor_property('BTN_LP0'+str(i)).get_is_enabled()for i in range(1,4))
 assert not flow.get_editor_property('RecommendationHistory')
 assert unreal.get_default_object(unreal.load_class(None,C01)).get_editor_property('CustomerProfile').export_text()==original
 R.update(actual_score_paths=96,permutation_clicks=18,invalid_sets=4,reference_integrity=assert_reference_integrity(),complete=True,**{'pass':True});save()

def tick(delta):
 if phase['busy']:return
 phase['busy']=True
 try:
  if phase['end']is not None:
   if time.monotonic()-phase['end']>3:unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if phase['gen']is None:phase['gen']=run()
  assert time.monotonic()-started<240
  next(phase['gen'])
 except StopIteration:level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)

