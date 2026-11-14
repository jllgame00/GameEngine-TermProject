"""Isolated real DialogueManager sequence semantics; unsaved tables/observer only."""
import unreal,json,os,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from narrative_validation_support import digest,text_literal,assert_reference_integrity,returned_flag
unreal.InternationalizationLibrary.set_current_language('en',False)
R={'complete':False,'pass':False,'scope':'isolated synchronous component/delegate diagnostics; no natural customer cycle claim'}
OUT=Path(os.environ['MVP_RESULT']);MC='/Game/DialogueManager.DialogueManager_C'
try:
 R['reference_integrity']=assert_reference_integrity()
 bp=unreal.load_asset('/Game/DialogueManager');assert 'SetPendingDialogueSequence' in [g.get_name() for g in L.list_graphs(bp)]
 factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
 probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_SequenceObserver','/Game/RecordShop/Dev/SequenceValidation',unreal.Blueprint,factory)
 for name,typ in [('Lines',L.get_array_type(L.get_basic_type_by_name('string'))),('Finished',L.get_basic_type_by_name('int'))]:assert L.add_member_variable(probe,name,typ)
 update=signature_event(probe,'ObserveLine',[('Speaker',L.get_basic_type_by_name('text')),('DialogueText',L.get_basic_type_by_name('text'))])
 eg=evgraph(probe);text=call(eg,'/Script/Engine.KismetTextLibrary.Conv_TextToString');link(pin(update,'DialogueText',True),pin(text,'InText'));append(eg,update.find_then_pin(),get(eg,'Lines'),pin(text,'ReturnValue',True))
 done=signature_event(probe,'ObserveFinished',[]);assign(eg,done.find_then_pin(),'Finished',calc(eg,'Add_IntInt',A=get(eg,'Finished'),B=1))
 bind=signature_event(probe,'BindManager',[('Manager',L.get_object_reference_type(unreal.load_class(None,MC))),('Mood',L.get_basic_type_by_name('string'))]);end=bind.find_then_pin()
 for dispatcher,event in [('OnUpdateDialogueUI',update),('OnDialogueFinished',done)]:
  n=action(eg,'Bind Event to '+dispatcher,[pin(bind,'Manager',True)],unreal.load_class(None,MC));link(pin(bind,'Manager',True),pin(n,'self'));link(pin(event,'OutputDelegate',True),pin(n,'Delegate'));link(end,n.find_execute_pin());end=n.find_then_pin()
 setter=eg.add_set_member_variable_node('CurrentMood',MC);link(pin(bind,'Manager',True),pin(setter,'self'));link(pin(bind,'Mood',True),pin(setter,'CurrentMood'));link(end,setter.find_execute_pin())
 assert L.compile_blueprint(probe);observer=unreal.get_default_object(probe.generated_class())
 manager=unreal.new_object(unreal.load_class(None,MC),outer=observer);observer.call_method(str(bind.get_node_title()),args=(manager,'Quiet'))
 def lines():return list(map(str,observer.get_editor_property('Lines')))
 def count():return observer.get_editor_property('Finished')
 def table(name,rows):
  f=unreal.DataTableFactory();f.set_editor_property('struct',unreal.load_asset('/Game/DialogueData'))
  a=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/RecordShop/Dev/SequenceValidation',unreal.DataTable,f)
  data=[dict(Name=key,DialogueID=key,Speaker='fixture',Text=text,Mood='Quiet',MusicPreference='Jazz',IsEndNode=False) for key,text in rows]
  assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(a,json.dumps(data),unreal.load_asset('/Game/DialogueData'));return a
 a=table('DT_SequenceA',[('A_One','fixture A1'),('A_Two','fixture A2'),('Other_Quiet','unreferenced row A')]);b=table('DT_SequenceB',[('B_One','fixture B1'),('B_Two','fixture B2'),('Other_Quiet','unreferenced row B')])
 assert returned_flag(manager.call_method('SetPendingDialogueSequence',args=(a,['A_Two','A_One'],'TEST_A')))
 manager.call_method('StartDialogue');assert lines()==['fixture A2']
 assert manager.get_editor_property('ActiveDialogueSource')==a and str(manager.get_editor_property('ActiveSequenceID'))=='TEST_A'
 assert not manager.get_editor_property('HasPendingDialogueSequence') and not manager.get_editor_property('PendingDialogueRows')
 for _ in range(3):manager.call_method('StartDialogue')
 assert lines()==['fixture A2'] and manager.get_editor_property('CurrentLineIndex')==1
 rejected=manager.call_method('SetPendingDialogueSequence',args=(b,['B_One'],'WHILE_ACTIVE'));R['while_active_return']={'type':type(rejected).__name__,'value':str(rejected),'active':manager.get_editor_property('DialogueSequenceActive'),'pending':manager.get_editor_property('HasPendingDialogueSequence')};assert not returned_flag(rejected)
 manager.call_method('ShowNextLine');assert lines()==['fixture A2','fixture A1'];manager.call_method('ShowNextLine')
 assert count()==1 and not manager.get_editor_property('DialogueSequenceActive') and manager.get_editor_property('ActiveDialogueSource') is None and not manager.get_editor_property('DialogueList')
 for _ in range(3):manager.call_method('ShowNextLine')
 assert count()==1
 assert returned_flag(manager.call_method('SetPendingDialogueSequence',args=(b,['B_One','B_Two'],'TEST_B')))
 manager.call_method('StartDialogue');manager.call_method('ShowNextLine');manager.call_method('ShowNextLine')
 assert lines()[-2:]==['fixture B1','fixture B2'] and count()==2
 R['explicit_order_source_isolation_and_duplicates']=True
 legacy=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/CustomerDialogue')))
 expected=[text_literal(r['Text']) for r in legacy]
 for source,rows,identity in [(None,['A_One'],'NULL'),(a,[],'EMPTY'),(a,['missing'],'MISSING'),(a,['A_One'],'None'),(unreal.load_asset('/Game/RecordShop/Data/Records/DT_RecordCatalogue'),['RS001'],'WRONG_STRUCT')]:
  before=len(lines());finished=count();assert not returned_flag(manager.call_method('SetPendingDialogueSequence',args=(source,rows,identity)))
  manager.call_method('StartDialogue');assert list(map(str,manager.get_editor_property('DialogueList')))==['C01_Quiet_%02d'%i for i in range(1,6)]
  for _ in range(5):manager.call_method('ShowNextLine')
  assert lines()[before:]==expected and count()==finished+1
 R['invalid_sequences_safe_legacy_fallback']=True
 assert returned_flag(manager.call_method('SetPendingDialogueSequence',args=(b,['B_Two'],'CANCEL')))
 manager.call_method('StartDialogue');finished=count();manager.call_method('CancelDialogueSequence');manager.call_method('ShowNextLine')
 assert count()==finished and manager.get_editor_property('ActiveDialogueSource') is None and manager.get_editor_property('PendingDialogueSource') is None
 before=len(lines());manager.call_method('StartDialogue')
 for _ in range(5):manager.call_method('ShowNextLine')
 assert lines()[before:]==expected
 R['cancel_clear_and_next_customer_no_leak']=True;R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
