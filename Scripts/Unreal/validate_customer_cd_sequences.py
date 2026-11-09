"""Real GFM/DM C/D emitted-line/profile/feedback matrix; unsaved history fixtures."""
import unreal,os,json,sys,time,traceback,itertools,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from narrative_validation_support import assert_reference_integrity,struct_value
from customer_b_validation_support import expected_score,expected_result
from customer_cd_validation_support import PROFILES,DAYS,SCORES,expected_cd_rows
FEEDBACK_REFERENCE=json.loads((ROOT/'Scripts/Unreal/result_feedback_reference.json').read_text(encoding='utf-8'))['legacy_feedback']
NEUTRAL_FEEDBACK=json.loads((ROOT/'Scripts/Unreal/preference_result_feedback.json').read_text(encoding='utf-8-sig'))
FC='/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C';MC='/Game/DialogueManager.DialogueManager_C'
VC='/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C';EC='/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C'
CC='/Game/RecordShop/Characters/Customers/Common/BP_Customer.BP_Customer_C';C01='/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'isolated GFM/DM emitted-line/profile/score/real Result text fixtures; no natural-cycle claim','cases':[]}
DATA=json.loads((ROOT/'Scripts/Unreal/customer_cd_dialogue.json').read_text(encoding='utf-8-sig'))
def save():OUT.write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf8')
def frames(n=2):
 for _ in range(n):yield
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_CDRevisitProbe','/Game/RecordShop/Dev/CDRevisitValidation',unreal.Blueprint,factory)
NT=L.get_basic_type_by_name('name');IT=L.get_basic_type_by_name('int');TT=L.get_basic_type_by_name('text');FT=L.get_object_reference_type(unreal.load_class(None,FC));NA=L.get_array_type(NT)
for key,typ in [('Lines',L.get_array_type(L.get_basic_type_by_name('string'))),('Speakers',L.get_array_type(L.get_basic_type_by_name('string'))),('Finishes',IT),('FlowRef',FT)]:assert L.add_member_variable(probe,key,typ)
g=function(probe,'SetFixture');a=inputs(g,[('Flow',FT),('Visit',L.get_object_reference_type(unreal.load_class(None,VC))),('History',L.get_array_type(L.get_object_reference_type(unreal.load_class(None,EC)))),('Profile',L.get_struct_type(unreal.load_asset('/Game/CustomerData')))])
end=g.find_graph_entry_pin()
for key,value in [('ActiveVisit',a['Visit']),('RecommendationHistory',a['History']),('CurrentDay',field(g,a['Visit'],'Day',VC))]:
 n=g.add_set_member_variable_node(key,FC);link(a['Flow'],pin(n,'self'));link(value,pin(n,key));link(end,n.find_execute_pin());end=n.find_then_pin()
n=g.add_set_member_variable_node('CustomerProfile',CC);link(field(g,a['Flow'],'ActiveCustomer',FC),pin(n,'self'));link(a['Profile'],pin(n,'CustomerProfile'));link(end,n.find_execute_pin());end=n.find_then_pin()
end=assign(g,end,'FlowRef',a['Flow']);end=clear(g,end,get(g,'Lines'));clear(g,end,get(g,'Speakers'))
eg=evgraph(probe)
unreal.log('CD_PROBE_BUILD_LINE')
line=signature_event(probe,'ObserveLine',[('Speaker',TT),('DialogueText',TT)])
end=line.find_then_pin()
for source,target in [('DialogueText','Lines'),('Speaker','Speakers')]:
 conv=call(eg,'/Script/Engine.KismetTextLibrary.Conv_TextToString');link(pin(line,source,True),pin(conv,'InText'));end=append(eg,end,get(eg,target),pin(conv,'ReturnValue',True))
unreal.log('CD_PROBE_BUILD_FINISH')
finish=signature_event(probe,'ObserveFinish',[]);assign(eg,finish.find_then_pin(),'Finishes',calc(eg,'Add_IntInt',A=get(eg,'Finishes'),B=1))
unreal.log('CD_PROBE_BUILD_BIND')
bind=signature_event(probe,'BindObservers',[('Flow',FT),('Manager',L.get_object_reference_type(unreal.load_class(None,MC)))]);end=bind.find_then_pin()
for title,event,target,kind in [('OnUpdateDialogueUI',line,'Manager',MC),('OnDialogueFinished',finish,'Manager',MC)]:
 node=action(eg,'Bind Event to '+title,[pin(bind,target,True)],unreal.load_class(None,kind));link(pin(event,'OutputDelegate',True),pin(node,'Delegate'));link(pin(bind,target,True),pin(node,'self'));link(end,node.find_execute_pin());end=node.find_then_pin()
unreal.log('CD_PROBE_FINAL_COMPILE')
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
 for identity in ('C','D'):
  # Synthetic BEST (and D GOOD) input is not a claim that current LPs can earn it.
  cases=[(1,None,'normal'),(1,'BEST','normal')]+[(2,key,'normal')for key in ('BEST','GOOD','POOR',None,'UNKNOWN')]+[(2,'BEST',mode)for mode in ('foreign-peer','foreign-A','foreign-B','future')]
  for number,result,mode in cases:
   visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_'+identity+'_'+str(number));assert visit.get_editor_property('Narrative'),'C/D production data missing'
   entries=[]
   if result is not None:
    prior_id=({'C':'D','D':'C'}[identity]if mode=='foreign-peer'else mode[-1]if mode.startswith('foreign-')else identity)
    entry=unreal.new_object(unreal.load_class(None,EC),outer=flow)
    # Future RecordIDs are history-only unsaved fixtures, never selected/playable LPs.
    for key,value in dict(CustomerID=prior_id,VisitNumber=9 if mode=='future'else 1,Day=DAYS[identity][0],RecordID=({'BEST':'RS005','GOOD':'RS002','POOR':'RS003'}if identity=='C'else {'BEST':'RS006','GOOD':'RS005','POOR':'RS001'}).get(result,'RS001'),RecommendationScore={'BEST':3,'GOOD':2,'POOR':1}.get(result,3),RecommendationResult=result,Sequence=1).items():entry.set_editor_property(key,value)
    entries=[entry]
   dm.call_method('CancelDialogueSequence');observer.call_method('SetFixture',args=(flow,visit,entries,profile));flow.call_method('ApplyVisitContext');flow.call_method('PrepareRevisitMemory')
   context=flow.call_method('GetActiveVisitMemory');assert (str(context[0]),int(context[1]),int(context[2]))==(identity,number,DAYS[identity][number-1])
   previous=result if mode=='normal'and number==2 else None
   assert bool(context[3])==bool(number==2 and result is not None and mode=='normal')
   if context[3]:assert str(context[4].get_editor_property('CustomerID'))==identity and context[4].get_editor_property('VisitNumber')==1
   expected=expected_cd_rows(identity,number,previous)
   assert list(map(str,dm.get_editor_property('PendingDialogueRows')))==expected,(identity,number,result,mode)
   assert list(map(str,flow.call_method('GetActiveCandidateRecordIDs')))==['RS001','RS002','RS003']
   runtime=flow.get_editor_property('ActiveCustomer').get_editor_property('CustomerProfile')
   assert [str(struct_value(runtime,k))for k in ('CustomerID','Mood','MusicPreference','Personality')]==[identity,*PROFILES[identity]]
   assert dm.get_editor_property('CurrentCustomer').export_text()==runtime.export_text()and dm.get_editor_property('CurrentMood')=='Quiet'
   before_finish=observer.get_editor_property('Finishes');dm.call_method('StartDialogue')
   assert str(dm.get_editor_property('ActiveSequenceID'))==identity+'_V'+str(number)and list(map(str,dm.get_editor_property('DialogueList')))==expected
   assert dm.get_editor_property('ActiveDialogueSource')==unreal.load_asset(DATA[identity]['source'])
   dm.call_method('StartDialogue');assert dm.get_editor_property('CurrentLineIndex')==1 and len(observer.get_editor_property('Lines'))==1
   assert not dm.get_editor_property('HasPendingDialogueSequence')
   for _ in expected:yield from frames();dm.call_method('ShowNextLine')
   assert list(map(str,observer.get_editor_property('Lines')))==[DATA[identity]['rows'][row]for row in expected]
   assert set(map(str,observer.get_editor_property('Speakers')))=={DATA[identity]['speaker']}
   assert observer.get_editor_property('Finishes')==before_finish+1
   dm.call_method('ShowNextLine');assert observer.get_editor_property('Finishes')==before_finish+1
   assert not dm.get_editor_property('DialogueList')and dm.get_editor_property('ActiveDialogueSource')is None and dm.get_editor_property('PendingDialogueSource')is None
   assert not dm.get_editor_property('HasPendingDialogueSequence')and not dm.get_editor_property('DialogueSequenceActive')
   assert list(flow.get_editor_property('RecommendationHistory'))==entries,'Dialogue mutated History'
   R['cases'].append(dict(customer=identity,visit=number,previous=result,mode=mode,rows=expected,lines=len(expected),intro=str(flow.get_editor_property('NarrativeMemoryIntroKey')),pass_=True));save()
  for number in (1,2):
   visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_'+identity+'_'+str(number))
   observer.call_method('SetFixture',args=(flow,visit,[],profile));flow.call_method('ApplyVisitContext');flow.call_method('PrepareRevisitMemory')
   for choice in (1,2,3):
    rid='RS00'+str(choice);found,record=flow.get_editor_property('RecordCatalogue').call_method('ResolveRecord',args=(rid,));assert found
    flow.call_method('SetGameFlowState',args=(selection_state,));flow.call_method('ResetRawScore');flow.call_method('HandleRecordSelected',args=(record,))
    score=SCORES[identity][choice-1];assert flow.get_editor_property('RawRecommendationScore')==score
    assert dm.call_method('CalculateLPScore',args=(str(struct_value(record,'Mood')),str(struct_value(record,'Genre')),str(struct_value(record,'Theme'))))==score
    panel=unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('Create',args=(world,unreal.load_class(None,'/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback.WBP_Result_IntegrationFallback_C'),unreal.GameplayStatics.get_player_controller(world,0)))
    panel.call_method('SetRawScoreDisplay',args=(True,score));assert str(panel.get_editor_property('ScoreStatus').get_text())==NEUTRAL_FEEDBACK[expected_result(score)]
   for score in (0,1,2,3):
    panel.call_method('SetRawScoreDisplay',args=(True,score));assert str(panel.get_editor_property('ScoreStatus').get_text())==NEUTRAL_FEEDBACK[expected_result(score)]
   panel.call_method('SetRawScoreDisplay',args=(False,3));assert str(panel.get_editor_property('ScoreStatus').get_text())==FEEDBACK_REFERENCE['UNAVAILABLE']
   assert dm.call_method('CalculateLPScore',args=PROFILES[identity])==3
   for future in ('RS004','RS005','RS006'):assert not flow.get_editor_property('RecordCatalogue').call_method('ResolveRecord',args=(future,))[0]
   assert not flow.get_editor_property('RecommendationHistory'),'Selection recorded History'
 # Simulate the fresh base-profile instance created by the production spawn authority.
 for identity in ('A','B','E'):
  visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_'+identity+'_1')
  dm.call_method('CancelDialogueSequence');observer.call_method('SetFixture',args=(flow,visit,entries,profile));flow.call_method('ApplyVisitContext');flow.call_method('PrepareRevisitMemory')
  current=flow.get_editor_property('ActiveCustomer').get_editor_property('CustomerProfile')
  tags=['Restless','Electronic','Adventurous']if identity=='B'else ['Quiet','Jazz','Traditional']
  assert [str(struct_value(current,k))for k in ('CustomerID','Mood','MusicPreference','Personality')]==[identity,*tags]
  assert not flow.call_method('GetActiveVisitMemory')[3]and not flow.get_editor_property('NarrativeMemoryVisits')
  dm.call_method('StartDialogue');assert str(dm.get_editor_property('ActiveSequenceID'))=={'A':'A_Visit1','B':'B_V1','E':'LEGACY_MOOD'}[identity]
  assert list(map(str,dm.get_editor_property('DialogueList')))==(['B1_Current_%02d'%i for i in range(1,7)]if identity=='B'else ['C01_Quiet_%02d'%i for i in range(1,6)])
  dm.call_method('CancelDialogueSequence')
  if identity!='B':
   for score in (0,1,2,3):
    panel.call_method('SetRawScoreDisplay',args=(True,score));assert str(panel.get_editor_property('ScoreStatus').get_text())==FEEDBACK_REFERENCE[expected_result(score)]
 assert unreal.get_default_object(unreal.load_class(None,C01)).get_editor_property('CustomerProfile').export_text()==original
 R.update(profile_score_vectors={k:list(v)for k,v in SCORES.items()},following_customer_isolation=True,neutral_and_legacy_feedback=True,reference_integrity=assert_reference_integrity(),complete=True,**{'pass':True});save()
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
