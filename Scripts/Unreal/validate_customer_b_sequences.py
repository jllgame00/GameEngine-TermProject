"""Real GFM + DialogueManager/UMG B1/B2/B3 branch matrix; unsaved history inputs."""
import unreal,os,json,sys,time,traceback,itertools,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from narrative_validation_support import assert_reference_integrity,struct_value
from customer_b_validation_support import expected_b_rows,expected_score,expected_result
FEEDBACK_REFERENCE=json.loads((ROOT/'Scripts/Unreal/result_feedback_reference.json').read_text(encoding='utf-8'))['legacy_feedback']
NEUTRAL_FEEDBACK=json.loads((ROOT/'Scripts/Unreal/preference_result_feedback.json').read_text(encoding='utf-8-sig'))
FC='/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C';MC='/Game/DialogueManager.DialogueManager_C'
VC='/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C';EC='/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C'
CC='/Game/RecordShop/Characters/Customers/Common/BP_Customer.BP_Customer_C';C01='/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'isolated GFM/DM emitted-line/profile/score fixtures; no rendered-widget or natural-cycle claim','cases':[]}
TEXTS=json.loads((ROOT/'Scripts/Unreal/customer_b_dialogue.json').read_text(encoding='utf-8-sig'))['rows']
def save():OUT.write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf8')
def frames(n=2):
 for _ in range(n):yield
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_BRevisitProbe','/Game/RecordShop/Dev/BRevisitValidation',unreal.Blueprint,factory)
NT=L.get_basic_type_by_name('name');IT=L.get_basic_type_by_name('int');TT=L.get_basic_type_by_name('text');FT=L.get_object_reference_type(unreal.load_class(None,FC));NA=L.get_array_type(NT)
for key,typ in [('Lines',L.get_array_type(L.get_basic_type_by_name('string'))),('Speakers',L.get_array_type(L.get_basic_type_by_name('string'))),('Finishes',IT),('FlowRef',FT)]:assert L.add_member_variable(probe,key,typ)
g=function(probe,'SetFixture');a=inputs(g,[('Flow',FT),('Visit',L.get_object_reference_type(unreal.load_class(None,VC))),('History',L.get_array_type(L.get_object_reference_type(unreal.load_class(None,EC)))),('Profile',L.get_struct_type(unreal.load_asset('/Game/CustomerData')))])
end=g.find_graph_entry_pin()
for key,value in [('ActiveVisit',a['Visit']),('RecommendationHistory',a['History']),('CurrentDay',field(g,a['Visit'],'Day',VC))]:
 n=g.add_set_member_variable_node(key,FC);link(a['Flow'],pin(n,'self'));link(value,pin(n,key));link(end,n.find_execute_pin());end=n.find_then_pin()
n=g.add_set_member_variable_node('CustomerProfile',CC);link(field(g,a['Flow'],'ActiveCustomer',FC),pin(n,'self'));link(a['Profile'],pin(n,'CustomerProfile'));link(end,n.find_execute_pin());end=n.find_then_pin()
end=assign(g,end,'FlowRef',a['Flow']);end=clear(g,end,get(g,'Lines'));clear(g,end,get(g,'Speakers'))
eg=evgraph(probe)
unreal.log('B_PROBE_BUILD_LINE')
line=signature_event(probe,'ObserveLine',[('Speaker',TT),('DialogueText',TT)])
end=line.find_then_pin()
for source,target in [('DialogueText','Lines'),('Speaker','Speakers')]:
 conv=call(eg,'/Script/Engine.KismetTextLibrary.Conv_TextToString');link(pin(line,source,True),pin(conv,'InText'));end=append(eg,end,get(eg,target),pin(conv,'ReturnValue',True))
unreal.log('B_PROBE_BUILD_FINISH')
finish=signature_event(probe,'ObserveFinish',[]);assign(eg,finish.find_then_pin(),'Finishes',calc(eg,'Add_IntInt',A=get(eg,'Finishes'),B=1))
unreal.log('B_PROBE_BUILD_BIND')
bind=signature_event(probe,'BindObservers',[('Flow',FT),('Manager',L.get_object_reference_type(unreal.load_class(None,MC)))]);end=bind.find_then_pin()
for title,event,target,kind in [('OnUpdateDialogueUI',line,'Manager',MC),('OnDialogueFinished',finish,'Manager',MC)]:
 node=action(eg,'Bind Event to '+title,[pin(bind,target,True)],unreal.load_class(None,kind));link(pin(event,'OutputDelegate',True),pin(node,'Delegate'));link(pin(bind,target,True),pin(node,'self'));link(end,node.find_execute_pin());end=node.find_then_pin()
unreal.log('B_PROBE_FINAL_COMPILE')
assert L.compile_blueprint(probe);observer=unreal.get_default_object(probe.generated_class())
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox');unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play()
started=time.monotonic();phase={'gen':None,'end':None,'busy':False}
def run():
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_class(None,FC))[0];flow.set_editor_property('EnableDaySchedule',False)
 for _ in range(3):flow.call_method('AdvancePrologue');yield from frames()
 deadline=time.monotonic()+40
 while not flow.get_editor_property('DialogueWidgetRef'):
  assert time.monotonic()<deadline;yield
 dm=flow.get_editor_property('DialogueManagerRef');assert str(dm.get_editor_property('ActiveSequenceID'))=='TUTORIAL_Training'
 for _ in range(5):flow.get_editor_property('DialogueWidgetRef').get_editor_property('Next').get_editor_property('on_clicked').broadcast();yield from frames()
 assert not flow.get_editor_property('RecommendationHistory')
 profile=unreal.get_default_object(unreal.load_class(None,C01)).get_editor_property('CustomerProfile');original=profile.export_text()
 observer.call_method(str(bind.get_node_title()),args=(flow,dm));selection_state=flow.get_editor_property('CurrentState')
 cases=[(1,None,None,'normal')]+[(2,key,None,'normal')for key in ('BEST','GOOD','POOR',None)]+[(3,a,b,'normal')for a,b in itertools.product(('BEST','GOOD','POOR'),repeat=2)]+[(3,None,'BEST','normal'),(3,'BEST',None,'normal'),(3,None,None,'normal'),(3,'UNKNOWN','BEST','normal'),(3,'BEST','UNKNOWN','normal'),(2,'BEST',None,'foreign'),(2,'BEST',None,'future'),(2,'UNKNOWN',None,'normal'),(3,'BEST','GOOD','foreign'),(3,'BEST','GOOD','future')]
 for number,first,second,mode in cases:
  visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_B_'+str(number));assert visit.get_editor_property('Narrative'),'B production data missing'
  entries=[]
  for num,result in [(1,first),(2,second)]:
   if result is None:continue
   entry=unreal.new_object(unreal.load_class(None,EC),outer=flow)
   for key,value in dict(CustomerID='A'if mode=='foreign'else 'B',VisitNumber=9 if mode=='future'else num,Day=2 if num==1 else 4,RecordID=({'BEST':'RS003','GOOD':'RS004','POOR':'RS001'}if num==1 else {'BEST':'RS004','GOOD':'RS003','POOR':'RS001'}).get(result,'RS001'),RecommendationScore={'BEST':3,'GOOD':2,'POOR':0 if num==1 else 1}.get(result,3),RecommendationResult=result,Sequence=len(entries)+1).items():entry.set_editor_property(key,value)
   entries.append(entry)
  dm.call_method('CancelDialogueSequence');observer.call_method('SetFixture',args=(flow,visit,entries,profile));flow.call_method('ApplyVisitContext')
  flow.call_method('PrepareRevisitMemory')
  context=flow.call_method('GetActiveVisitMemory');assert (str(context[0]),int(context[1]),int(context[2]))==('B',number,{1:2,2:4,3:6}[number])
  ef=first if mode=='normal'else None;expected=expected_b_rows(number,ef,second if mode=='normal'else None)
  assert list(map(str,dm.get_editor_property('PendingDialogueRows')))==expected,(number,first,second,mode,list(map(str,dm.get_editor_property('PendingDialogueRows'))),expected)
  assert list(map(str,flow.call_method('GetActiveCandidateRecordIDs')))==['RS001','RS002','RS003']
  runtime=flow.get_editor_property('ActiveCustomer').get_editor_property('CustomerProfile')
  assert [str(struct_value(runtime,k))for k in ('CustomerID','Mood','MusicPreference','Personality')]==['B','Restless'if number==1 else 'Quiet','Electronic','Adventurous']
  before_finish=observer.get_editor_property('Finishes');dm.call_method('StartDialogue')
  assert str(dm.get_editor_property('ActiveSequenceID'))=='B_V'+str(number) and list(map(str,dm.get_editor_property('DialogueList')))==expected
  dm.call_method('StartDialogue');assert dm.get_editor_property('CurrentLineIndex')==1 and len(observer.get_editor_property('Lines'))==1
  assert not dm.get_editor_property('HasPendingDialogueSequence')
  for i in range(len(expected)):
   yield from frames()
   dm.call_method('ShowNextLine')
  assert list(map(str,observer.get_editor_property('Lines')))==[TEXTS[row]for row in expected]
  assert len(set(map(str,observer.get_editor_property('Speakers'))))==1
  assert observer.get_editor_property('Finishes')==before_finish+1
  dm.call_method('ShowNextLine');assert observer.get_editor_property('Finishes')==before_finish+1
  assert not dm.get_editor_property('DialogueList')and dm.get_editor_property('ActiveDialogueSource')is None and dm.get_editor_property('PendingDialogueSource')is None
  assert list(flow.get_editor_property('RecommendationHistory'))==entries,'Dialogue mutated History'
  R['cases'].append(dict(visit=number,v1=first,v2=second,mode=mode,rows=expected,lines=len(expected),intro=str(flow.get_editor_property('NarrativeMemoryIntroKey')),pass_=True));save()
 assert unreal.get_default_object(unreal.load_class(None,C01)).get_editor_property('CustomerProfile').export_text()==original
 # Real active-profile calculation/handoff for each B visit and all three LPs.
 for number in (1,2,3):
  visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_B_'+str(number))
  observer.call_method('SetFixture',args=(flow,visit,[],profile));flow.call_method('ApplyVisitContext');flow.call_method('PrepareRevisitMemory')
  for choice in (1,2,3):
   rid='RS00'+str(choice);found,record=flow.get_editor_property('RecordCatalogue').call_method('ResolveRecord',args=(rid,));assert found
   flow.call_method('SetGameFlowState',args=(selection_state,));flow.call_method('ResetRawScore');flow.call_method('HandleRecordSelected',args=(record,))
   assert flow.get_editor_property('RawRecommendationScore')==expected_score('B',number,choice)
   panel=unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('Create',args=(world,unreal.load_class(None,'/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback.WBP_Result_IntegrationFallback_C'),unreal.GameplayStatics.get_player_controller(world,0)))
   panel.call_method('SetRawScoreDisplay',args=(True,expected_score('B',number,choice)))
   feedback=str(panel.get_editor_property('ScoreStatus').get_text())
   assert feedback==NEUTRAL_FEEDBACK[expected_result(expected_score('B',number,choice))],('B Result category text mismatch',number,choice,feedback)
   panel.call_method('SetRawScoreDisplay',args=(False,3))
   assert str(panel.get_editor_property('ScoreStatus').get_text())==FEEDBACK_REFERENCE['UNAVAILABLE']
  for synthetic_score in (0,1,2,3):
   panel.call_method('SetRawScoreDisplay',args=(True,synthetic_score))
   assert str(panel.get_editor_property('ScoreStatus').get_text())==NEUTRAL_FEEDBACK[expected_result(synthetic_score)]
  assert dm.call_method('CalculateLPScore',args=('Quiet','Electronic','Adventurous'))==(2 if number==1 else 3)
  assert not flow.get_editor_property('RecordCatalogue').call_method('ResolveRecord',args=('RS004',))[0]
 # Restore base runtime profile to model the next fresh A/C actor: no B override leaks.
 for identity in ('A','C'):
  visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_'+identity+'_1')
  observer.call_method('SetFixture',args=(flow,visit,[],profile));flow.call_method('ApplyVisitContext');flow.call_method('PrepareRevisitMemory')
  current=flow.get_editor_property('ActiveCustomer').get_editor_property('CustomerProfile')
  assert [str(struct_value(current,k))for k in ('CustomerID','Mood','MusicPreference','Personality')]==[identity,'Quiet','Jazz','Traditional']
  dm.call_method('StartDialogue');assert list(map(str,dm.get_editor_property('DialogueList')))==['C01_Quiet_%02d'%i for i in range(1,6)]
  assert str(dm.get_editor_property('ActiveSequenceID'))==('A_Visit1'if identity=='A'else 'LEGACY_MOOD')
  dm.call_method('CancelDialogueSequence')
  for score,category in [(3,'BEST'),(2,'GOOD'),(1,'POOR'),(0,'POOR')]:
   panel.call_method('SetRawScoreDisplay',args=(True,score))
   assert str(panel.get_editor_property('ScoreStatus').get_text())==FEEDBACK_REFERENCE[category],('Legacy feedback changed',identity,category)
 R['profile_score_vectors']={'B1':[0,0,3],'B2':[1,1,2],'B3':[1,1,2]}
 R['following_customer_isolation']=True;R['preference_neutral_result_and_legacy_feedback']=True
 R['reference_integrity']=assert_reference_integrity();R.update(complete=True,**{'pass':True});save()
def tick(delta):
 if phase['busy']:return
 phase['busy']=True
 try:
  if phase['end']is not None:
   if time.monotonic()-phase['end']>3:unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if phase['gen']is None:phase['gen']=run()
  assert time.monotonic()-started<180
  next(phase['gen'])
 except StopIteration:level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
