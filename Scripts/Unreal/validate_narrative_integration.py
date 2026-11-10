"""Isolated live-world visit/profile/memory/candidate fixtures; never save assets."""
import unreal,json,os,sys,time,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from narrative_validation_support import assert_reference_integrity,canonical_record,struct_value,returned_flag
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';FC=FLOW+'.BP_GameFlowManager_C'
VC='/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C';NC='/Game/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition.BP_VisitNarrativeDefinition_C'
KC='/Game/RecordShop/Data/Records/BP_RecordCatalogue.BP_RecordCatalogue_C';EC='/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C'
MC='/Game/DialogueManager.DialogueManager_C';UI='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect';UC=UI+'.WBP_RecordSelect_C'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'isolated live-world runtime visit/profile/history fixtures and transient 6-row catalogue; not natural cycle evidence'}
def save():OUT.write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
def frames(n=3):
 for _ in range(n):yield

def object_fields(kind,outer,fields):
 obj=unreal.new_object(unreal.load_class(None,kind),outer=outer)
 for key,value in fields.items():obj.set_editor_property(key,value)
 return obj

def table(name,struct,rows):
 f=unreal.DataTableFactory();f.set_editor_property('struct',unreal.load_asset(struct));a=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/RecordShop/Dev/NarrativeValidation',unreal.DataTable,f)
 assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(a,json.dumps(rows,ensure_ascii=False),unreal.load_asset(struct));return a

# Unsaved Blueprint probe permits legitimate runtime setters for protected state.
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_NarrativeProbe','/Game/RecordShop/Dev/NarrativeValidation',unreal.Blueprint,f)
NA=L.get_array_type(L.get_basic_type_by_name('name'));NT=L.get_basic_type_by_name('name');IT=L.get_basic_type_by_name('int');FT=L.get_object_reference_type(unreal.load_class(None,FC));HT=L.get_array_type(L.get_object_reference_type(unreal.load_class(None,EC)))
for key,typ in [('FlowRef',FT),('SeenPendingRows',NA),('SeenIntro',NT),('MemoryEvents',IT),('SelectionEvents',IT),('SelectedID',NT)]:assert L.add_member_variable(probe,key,typ)
g=function(probe,'SetFixture');a=inputs(g,[('Flow',FT),('Visit',L.get_object_reference_type(unreal.load_class(None,VC))),('Day',IT),('History',HT)]);end=g.find_graph_entry_pin()
for key,value in [('ActiveVisit',a['Visit']),('CurrentDay',a['Day']),('RecommendationHistory',a['History'])]:
 n=g.add_set_member_variable_node(key,FC);link(a['Flow'],pin(n,'self'));link(value,pin(n,key));link(end,n.find_execute_pin());end=n.find_then_pin()
end=assign(g,end,'FlowRef',a['Flow'])
eg=evgraph(probe);memory=signature_event(probe,'ObserveMemory',[('CustomerID',NT),('VisitNumber',IT),('HasPrevious',L.get_basic_type_by_name('bool'))]);end=assign(eg,memory.find_then_pin(),'SeenIntro',field(eg,get(eg,'FlowRef'),'NarrativeMemoryIntroKey',FC))
manager=field(eg,get(eg,'FlowRef'),'DialogueManagerRef',FC);end=assign(eg,end,'SeenPendingRows',field(eg,manager,'PendingDialogueRows',MC));assign(eg,end,'MemoryEvents',calc(eg,'Add_IntInt',A=get(eg,'MemoryEvents'),B=1))
record=signature_event(probe,'ObserveRecord',[('Record',L.get_struct_type(unreal.load_asset('/Game/RecordShop/Data/Structs/ST_RecordData')))]);split=action(eg,'Break ST Record Data',[pin(record,'Record',True)]);link(pin(record,'Record',True),pin(split,'ST_RecordData'));end=assign(eg,record.find_then_pin(),'SelectedID',struct_field(split,'RecordID'));assign(eg,end,'SelectionEvents',calc(eg,'Add_IntInt',A=get(eg,'SelectionEvents'),B=1))
bind=signature_event(probe,'BindMemory',[('Flow',FT)]);n=action(eg,'Bind Event to On Revisit Memory Ready',[pin(bind,'Flow',True)],unreal.load_class(None,FC));link(pin(bind,'Flow',True),pin(n,'self'));link(pin(memory,'OutputDelegate',True),pin(n,'Delegate'));link(bind.find_then_pin(),n.find_execute_pin())
widgetbind=signature_event(probe,'BindWidget',[('Widget',L.get_object_reference_type(unreal.load_class(None,UC)))]);n=action(eg,'Bind Event to On Record Selected',[pin(widgetbind,'Widget',True)],unreal.load_class(None,UC));link(pin(widgetbind,'Widget',True),pin(n,'self'));link(pin(record,'OutputDelegate',True),pin(n,'Delegate'));link(widgetbind.find_then_pin(),n.find_execute_pin())
assert L.compile_blueprint(probe);observer=unreal.get_default_object(probe.generated_class())
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();started=time.monotonic();phase={'gen':None,'end':None,'busy':False}
def run():
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_class(None,FC))[0];pc=unreal.GameplayStatics.get_player_controller(world,0)
 flow.set_editor_property('EnableDaySchedule',False)
 R['reference_integrity']=assert_reference_integrity()
 for _ in range(3):flow.call_method('AdvancePrologue');yield from frames()
 deadline=time.monotonic()+40
 while not flow.get_editor_property('DialogueWidgetRef'):
  assert time.monotonic()<deadline;yield
 customer=flow.get_editor_property('ActiveCustomer');manager=flow.get_editor_property('DialogueManagerRef');assert str(struct_value(customer.get_editor_property('CustomerProfile'),'CustomerID'))=='TUTORIAL'
 assert str(manager.get_editor_property('ActiveSequenceID'))=='TUTORIAL_Training'
 for _ in range(5):
  panel=flow.get_editor_property('DialogueWidgetRef');assert panel;panel.get_editor_property('Next').get_editor_property('on_clicked').broadcast();yield from frames()
 assert not flow.get_editor_property('RecommendationHistory');select_state=flow.get_editor_property('CurrentState');assert select_state.value==2
 R['tutorial_identity_and_no_history']=True
 base_default=unreal.get_default_object(unreal.load_class(None,'/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C')).get_editor_property('CustomerProfile').export_text()
 fixture_rows=[dict(Name=key,DialogueID=key,Speaker='fixture',Text=key,Mood='Quiet',MusicPreference='Electronic',IsEndNode=False) for key in ['INTRO_BEST','INTRO_GOOD','INTRO_POOR','INTRO_NONE','BODY']]
 source=table('DT_MemoryFixture','/Game/DialogueData',fixture_rows)
 definition=object_fields(NC,flow,dict(SequenceID='TEST_VISIT',SourceTable=source,OrderedRows=['BODY'],MemoryVisitNumbers=[],BestIntroRows=['INTRO_BEST'],GoodIntroRows=['INTRO_GOOD'],PoorIntroRows=['INTRO_POOR'],NoMemoryIntroRows=['INTRO_NONE'],TargetMoodOverride='Restless',TargetGenreOverride='Electronic',TargetThemeOverride='Adventurous',CandidateRecordIDs=['RS003','RS001','RS002'],ReviewStatus='READY',ContentVersion=1))
 visit=object_fields(VC,flow,dict(CustomerID='B',VisitNumber=1,Day=2,OrderInDay=1,Narrative=definition))
 observer.call_method('SetFixture',args=(flow,visit,2,[]));flow.call_method('ApplyVisitContext');flow.call_method('ConfigureActiveNarrative')
 assert manager.get_editor_property('CurrentMood')=='Restless'
 cat=flow.get_editor_property('RecordCatalogue');ok,rs003=cat.call_method('ResolveRecord',args=('RS003',));assert ok
 flow.call_method('HandleRecordSelected',args=(rs003,));assert flow.get_editor_property('RawScoreAvailable') and flow.get_editor_property('RawRecommendationScore')==3
 definition.set_editor_property('TargetMoodOverride','Quiet');definition.set_editor_property('MemoryVisitNumbers',[1]);visit.set_editor_property('VisitNumber',2);visit.set_editor_property('Day',4)
 observer.call_method(str(bind.get_node_title()),args=(flow,))
 for result,score,key in [('BEST',3,'INTRO_BEST'),('GOOD',2,'INTRO_GOOD'),('POOR',0,'INTRO_POOR'),('NO_MEMORY',0,'INTRO_NONE')]:
  history=[] if result=='NO_MEMORY' else [object_fields(EC,flow,dict(CustomerID='B',VisitNumber=1,Day=2,RecordID='RS002',RecommendationScore=score,RecommendationResult=result,Sequence=1))]
  manager.call_method('CancelDialogueSequence');observer.call_method('SetFixture',args=(flow,visit,4,history));flow.call_method('ApplyVisitContext')
  before=observer.get_editor_property('MemoryEvents');flow.call_method('PrepareRevisitMemory')
  assert observer.get_editor_property('MemoryEvents')==before+1 and str(observer.get_editor_property('SeenIntro'))==result
  assert list(map(str,observer.get_editor_property('SeenPendingRows')))==[key,'BODY']
  manager.call_method('StartDialogue');assert str(manager.get_editor_property('ActiveSequenceID'))=='TEST_VISIT' and list(map(str,manager.get_editor_property('DialogueList')))==[key,'BODY']
  assert manager.get_editor_property('CurrentMood')=='Quiet' and manager.call_method('CalculateLPScore',args=('Quiet','Electronic','Adventurous'))==3
  manager.call_method('CancelDialogueSequence')
 # Multiple snapshots: the last requested prior visit governs the intro.
 visit.set_editor_property('VisitNumber',3);visit.set_editor_property('Day',6);definition.set_editor_property('MemoryVisitNumbers',[1,2])
 for previous,expected_key,expected_count in [([(1,'BEST')],'NO_MEMORY',1), ([(1,'POOR'),(2,'GOOD')],'GOOD',2), ([(2,'GOOD')],'GOOD',1)]:
  entries=[object_fields(EC,flow,dict(CustomerID='B',VisitNumber=num,Day=2 if num==1 else 4,RecordID='RS002',RecommendationScore={'BEST':3,'GOOD':2,'POOR':0}[result],RecommendationResult=result,Sequence=i+1)) for i,(num,result) in enumerate(previous)]
  observer.call_method('SetFixture',args=(flow,visit,6,entries));flow.call_method('PrepareRevisitMemory')
  assert str(flow.get_editor_property('NarrativeMemoryIntroKey'))==expected_key and len(flow.get_editor_property('NarrativeMemoryVisits'))==expected_count
 R['multiple_memories_and_missing_latest_policy']=True
 manager.call_method('CancelDialogueSequence')
 flow.call_method('SetGameFlowState',args=(select_state,));flow.call_method('ResetRawScore');flow.call_method('HandleRecordSelected',args=(rs003,));assert flow.get_editor_property('RawRecommendationScore')==2
 assert unreal.get_default_object(unreal.load_class(None,'/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C')).get_editor_property('CustomerProfile').export_text()==base_default
 R['visit_overrides_and_memory_before_start']=True
 production_table=cat.get_editor_property('Table');rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(production_table));assert len(rows)==6
 rows=[row for row in rows if row['RecordID']in ('RS001','RS002','RS003')];assert len(rows)==3
 triples=[('Quiet','Electronic','Adventurous'),('Quiet','Folk','Sociable'),('Quiet','Classical','Reflective')]
 for i,tags in enumerate(triples,4):
  row=dict(rows[0]);row.update(Name='RS00'+str(i),RecordID='RS00'+str(i),Title='fixture',Artist='fixture',Mood=tags[0],Genre=tags[1],Theme=tags[2],Audio='None',Cover='None');rows.append(row)
 extended=table('DT_SixRecordsFixture','/Game/RecordShop/Data/Structs/ST_RecordData',rows);fixture_cat=object_fields(KC,flow,dict(Table=extended,DefaultCandidateRecordIDs=['RS001','RS002','RS003']))
 for i,tags in enumerate(triples,4):
  ok,data=fixture_cat.call_method('ResolveRecord',args=('RS00'+str(i),));assert ok
  assert tuple(str(struct_value(data,key)) for key in ('Mood','Genre','Theme'))==tags
  assert not fixture_cat.call_method('ResolvePlayableRecord',args=('RS00'+str(i),))[0]
 assert not cat.call_method('ResolveRecord',args=('INVALID',))[0]
 if flow.get_editor_property('RecommendationHistory'):
  entry=flow.call_method('GetLatestRecommendation',args=('B',));assert cat.call_method('ResolveRecord',args=(str(entry.get_editor_property('RecordID')),))[0]
 ids=list(map(str,flow.call_method('GetActiveCandidateRecordIDs')));assert ids==['RS003','RS001','RS002']
 widget=unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('Create',args=(world,unreal.load_class(None,UC),pc))
 assert returned_flag(widget.call_method('ConfigureRecordCandidates',args=(fixture_cat,ids)))
 widget.add_to_viewport(20);yield from frames()
 capture=OUT.with_name(OUT.stem+'-three-candidates.png');unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(capture)+'" -nosuffix');R['three_candidate_capture']=str(capture);yield from frames(4)
 assert list(map(str,widget.get_editor_property('ResolvedCandidateIDs')))==ids and widget.is_in_viewport()
 for index,identity in enumerate(ids,1):
  assert str(struct_value(widget.get_editor_property('CardRecord'+str(index)),'RecordID'))==identity
  assert widget.get_editor_property('BTN_LP0'+str(index)).get_is_enabled()
 observer.call_method(str(widgetbind.get_node_title()),args=(widget,));before=observer.get_editor_property('SelectionEvents');widget.get_editor_property('BTN_LP01').get_editor_property('on_clicked').broadcast();yield from frames()
 assert observer.get_editor_property('SelectionEvents')==before+1 and str(observer.get_editor_property('SelectedID'))=='RS003'
 for invalid in [['RS001','INVALID','RS003'],['RS001','RS001','RS003'],['RS001','RS002'],['RS004','RS002','RS003']]:
  widget=unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('Create',args=(world,unreal.load_class(None,UC),pc));assert not returned_flag(widget.call_method('ConfigureRecordCandidates',args=(fixture_cat,invalid)))
  assert not widget.get_editor_property('ResolvedCandidateIDs') and all(not widget.get_editor_property('BTN_LP0'+str(i)).get_is_enabled() for i in range(1,4))
  observer.call_method(str(widgetbind.get_node_title()),args=(widget,));before=observer.get_editor_property('SelectionEvents');widget.get_editor_property('BTN_LP01').get_editor_property('on_clicked').broadcast();assert observer.get_editor_property('SelectionEvents')==before
 assert len(unreal.DataTableFunctionLibrary.get_data_table_row_names(production_table))==6
 R['six_row_schema_three_candidate_ui_and_invalid_ids']=True
 R['reference_integrity_final']=assert_reference_integrity();R.update(complete=True,**{'pass':True});save()
def tick(delta):
 if phase['busy']:return
 phase['busy']=True
 try:
  if phase['end'] is not None:
   if time.monotonic()-phase['end']>3:
    unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if phase['gen'] is None:phase['gen']=run()
  assert time.monotonic()-started<130
  next(phase['gen'])
 except StopIteration:level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
