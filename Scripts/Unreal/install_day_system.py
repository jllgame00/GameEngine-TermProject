"""Add event-driven Day/Queue to the existing production manager. Editor only.
No Tick-based queue detection; no duplicate customer/dialogue/record/turntable flow.
"""
import unreal,os,json,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from day_graph_helpers import *
unreal.InternationalizationLibrary.set_current_language('en',False)
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';FC=FLOW+'.BP_GameFlowManager_C'
TT='/Game/RecordShop/Interaction/Actors/BP_Turntable';TC=TT+'.BP_Turntable_C'
CUSTOMER='/Game/RecordShop/Characters/Customers/Common/BP_Customer';CC=CUSTOMER+'.BP_Customer_C'
UI='/Game/RecordShop/UI/Prologue/WBP_Prologue';UC=UI+'.WBP_Prologue_C'
BASE='/Game/RecordShop/Data/Schedule/'
VC=BASE+'BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C'
DC=BASE+'BP_DayScheduleDefinition.BP_DayScheduleDefinition_C'
WC=BASE+'BP_WeekScheduleDefinition.BP_WeekScheduleDefinition_C'
R={'complete':False,'pass':False,'saved':[]};OUT=Path(os.environ['MVP_RESULT'])
def report():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
def save(bp):
 assert L.compile_blueprint(bp),bp.get_name()
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 R['saved'].append(bp.get_path_name());report()
def run(g,end,name,**args):return own(g,end,FC,name,**args)
def status(g,end,phase):return assign(g,end,'DayPhase',phase)
def stage(g,name):return calc(g,'EqualEqual_NameName',A=get(g,'DayPhase'),B=name)
def check(g,end,condition):return branch(g,end,condition)[0]
def failure(g,end):return run(g,status(g,end,'InvalidSchedule'),'ShowDayPresentation')
def guard(g,end,obj):
 yes,no=valid(g,obj,end);failure(g,no);return yes

def presentation(g,end,title,body):
 ref=get(g,'DayHudRef');yes,no=valid(g,ref,end)
 create=action(g,'Create Widget');val(pin(create,'Class'),UC)
 pc=call(g,'/Script/Engine.GameplayStatics.GetPlayerController');link(pin(pc,'ReturnValue',True),pin(create,'OwningPlayer'));link(no,create.find_execute_pin())
 new=assign(g,create.find_then_pin(),'DayHudRef',pin(create,'ReturnValue',True))
 new,_=invoke(g,new,'/Script/UMG.UserWidget.AddToViewport',self=get(g,'DayHudRef'),ZOrder=10)
 new=own(g,new,UC,'ConfigureHint',self=get(g,'DayHudRef'))
 # Both branches share one content update, without touching focus or camera.
 update=call(g,UC+':SetPresentation');link(yes,update.find_execute_pin());link(new,update.find_execute_pin());link(get(g,'DayHudRef'),pin(update,'self'))
 for key,text in [('Title',title),('Body',body),('Action','')]:
  if hasattr(text,'is_valid'):
   cv=call(g,'/Script/Engine.KismetTextLibrary.Conv_StringToText');link(text,pin(cv,'InString'));link(pin(cv,'ReturnValue',True),pin(update,key))
  else:val(pin(update,key),text)
 return update.find_then_pin()

try:
 bp=unreal.load_asset(FLOW);assert bp
 assert not ('DaySystemInstalled' in list(map(str,L.list_member_variable_names(bp,False))) and unreal.get_default_object(bp.generated_class()).get_editor_property('DaySystemInstalled')), 'Day system already installed'
 types={'CurrentDay':L.get_basic_type_by_name('int'),'CurrentCustomerIndex':L.get_basic_type_by_name('int'),'DayPhase':L.get_basic_type_by_name('name'),'DayCustomersComplete':L.get_basic_type_by_name('bool'),'FinalStoryEventTriggered':L.get_basic_type_by_name('bool'),'EnableDaySchedule':L.get_basic_type_by_name('bool'),'DaySystemInitialized':L.get_basic_type_by_name('bool'),'DaySystemInstalled':L.get_basic_type_by_name('bool'),'QueueCycleInProgress':L.get_basic_type_by_name('bool'),'AwaitingCustomerExit':L.get_basic_type_by_name('bool'),'CustomerSpawnAuthorized':L.get_basic_type_by_name('bool'),'WeekSchedule':L.get_object_reference_type(unreal.load_class(None,WC)),'CustomerQueue':L.get_array_type(L.get_object_reference_type(unreal.load_class(None,VC))),'ActiveVisit':L.get_object_reference_type(unreal.load_class(None,VC)),'SelectedCustomerClass':L.get_class_reference_type(cls(CUSTOMER)),'DayHudRef':L.get_object_reference_type(cls(UI)),'ListeningDuration':L.get_member_variable_type(unreal.load_asset(TT),'TonearmMotionAlpha'),'StoreBGMRequested':L.get_basic_type_by_name('bool'),'StoreBGMRef':L.get_object_reference_type(unreal.AudioComponent),'StoreBGMSound':L.get_object_reference_type(unreal.SoundBase)}
 old=list(map(str,L.list_member_variable_names(bp,False)))
 for name,typ in types.items():
  if name not in old:assert L.add_member_variable(bp,name,typ),name
 for name in ('WeekSchedule','EnableDaySchedule','ListeningDuration','StoreBGMSound'):L.set_blueprint_variable_instance_editable(bp,name,True)
 funcs=['InitializeDaySystem','BeginDay','SpawnQueuedCustomer','ApplyVisitContext','AfterCustomerCycle','EndCurrentDay','FinishDayTransition','ShowDayPresentation','HideDayPresentation','StartListeningWindow','EndListeningWindow','StopStoreBGM']
 for name in funcs:fn(bp,name)
 g=G.get_graph_editor_by_name(bp,'BeginDay');param(g,'DayNumber',L.get_basic_type_by_name('int'))
 for name,params in [('OnDayStarted',[('Day',L.get_basic_type_by_name('int'))]),('OnDayEnded',[('Day',L.get_basic_type_by_name('int'))]),('OnCustomerVisitCompleted',[('Visit',types['ActiveVisit'])]),('OnFinalStoryEvent',[('EventID',L.get_basic_type_by_name('name'))])]:
  if name not in list(map(str,L.list_event_dispatchers(bp))):
   assert L.add_event_dispatcher(bp,name)
   for key,typ in params:assert L.add_event_dispatcher_parameter(bp,name,key,typ)
 eg=evgraph(bp)
 tutorial=eg.add_custom_event_node('HandleTutorialCompletedForDays')
 bgm=eg.add_custom_event_node('StartStoreBGM')
 bgm_end=eg.add_custom_event_node('StoreBGMFinishedEvent')
 assert L.compile_blueprint(bp)
 cdo=unreal.get_default_object(bp.generated_class())
 for key,value in dict(CurrentDay=0,CurrentCustomerIndex=0,DayPhase='AwaitingTutorial',DayCustomersComplete=False,FinalStoryEventTriggered=False,EnableDaySchedule=True,DaySystemInitialized=False,QueueCycleInProgress=False,AwaitingCustomerExit=False,WeekSchedule=unreal.load_asset(BASE+'DA_TemporaryWeek'),SelectedCustomerClass=cls('/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01'),ListeningDuration=10.0,StoreBGMSound=unreal.load_asset('/Game/RecordShop/Audio/Music/RS001_Best')).items():cdo.set_editor_property(key,value)

 g=fn(bp,'InitializeDaySystem');yes,end=branch(g,g.find_graph_entry_pin(),get(g,'DaySystemInitialized'))
 end=assign(g,end,'DaySystemInitialized','true');status(g,end,'AwaitingTutorial')
 g=fn(bp,'ShowDayPresentation');end=g.find_graph_entry_pin()
 title=calc(g,'Concat_StrStr',A='DAY ',B=calc(g,'Conv_IntToString',InInt=get(g,'CurrentDay')))
 final,normal=branch(g,end,get(g,'FinalStoryEventTriggered'));presentation(g,final,title,'방문 일정 완료 · TBD')
 bad,normal=branch(g,normal,stage(g,'InvalidSchedule'));presentation(g,bad,title,'방문 일정 데이터를 확인해 주세요.')
 ending,normal=branch(g,normal,stage(g,'DayEnding'));presentation(g,ending,title,'오늘의 방문 일정 완료')
 body=calc(g,'Concat_StrStr',A=calc(g,'Conv_IntToString',InInt=array_len(g,get(g,'CustomerQueue'))),B='명의 손님이 방문합니다.')
 presentation(g,normal,title,body)
 g=fn(bp,'HideDayPresentation');end,no=valid(g,get(g,'DayHudRef'),g.find_graph_entry_pin())
 end,_=invoke(g,end,'/Script/UMG.Widget.RemoveFromParent',self=get(g,'DayHudRef'));assign(g,end,'DayHudRef','None')

 g=fn(bp,'BeginDay');number=param(g,'DayNumber',L.get_basic_type_by_name('int'));end=g.find_graph_entry_pin()
 end=check(g,end,get(g,'EnableDaySchedule'));end=check(g,end,get(g,'TutorialComplete'))
 end=check(g,end,calc(g,'BooleanOR',A=stage(g,'AwaitingTutorial'),B=stage(g,'DayEnding')))
 end=check(g,end,calc(g,'EqualEqual_IntInt',A=number,B=calc(g,'Add_IntInt',A=get(g,'CurrentDay'),B=1)))
 active,end=valid(g,get(g,'ActiveCustomer'),end)
 end=guard(g,end,get(g,'WeekSchedule'))
 days=field(g,get(g,'WeekSchedule'),'Days',WC)
 end=check(g,end,calc(g,'GreaterEqual_IntInt',A=number,B=1));end=check(g,end,calc(g,'LessEqual_IntInt',A=number,B=array_len(g,days)))
 definition=item(g,days,calc(g,'Subtract_IntInt',A=number,B=1));end=guard(g,end,definition)
 end=check(g,end,calc(g,'EqualEqual_IntInt',A=field(g,definition,'Day',DC),B=number))
 end=assign(g,end,'CustomerQueue',field(g,definition,'Visits',DC));end=check(g,end,calc(g,'Greater_IntInt',A=array_len(g,get(g,'CustomerQueue')),B=0))
 end=assign(g,end,'CurrentDay',number);end=assign(g,end,'CurrentCustomerIndex',0);end=assign(g,end,'ActiveVisit','None');end=assign(g,end,'DayCustomersComplete','false');end=assign(g,end,'QueueCycleInProgress','false')
 end=status(g,end,'DayStarting');end=run(g,end,'DismissTutorialHint');end=run(g,end,'ShowDayPresentation');end=run(g,end,'StartStoreBGM')
 end=dispatch(g,end,'On Day Started',Day=get(g,'CurrentDay'));timer(g,end,'SpawnQueuedCustomer',3)

 g=fn(bp,'SpawnQueuedCustomer');end=g.find_graph_entry_pin()
 end=check(g,end,get(g,'EnableDaySchedule'));end=check(g,end,get(g,'TutorialComplete'))
 end=check(g,end,calc(g,'BooleanOR',A=stage(g,'DayStarting'),B=stage(g,'BetweenCustomers')))
 yes,end=branch(g,end,get(g,'QueueCycleInProgress'));yes,end=valid(g,get(g,'ActiveCustomer'),end)
 end=check(g,end,calc(g,'Less_IntInt',A=get(g,'CurrentCustomerIndex'),B=array_len(g,get(g,'CustomerQueue'))))
 visit=item(g,get(g,'CustomerQueue'),get(g,'CurrentCustomerIndex'));end=guard(g,end,visit)
 for condition in [calc(g,'EqualEqual_IntInt',A=field(g,visit,'Day',VC),B=get(g,'CurrentDay')),calc(g,'EqualEqual_IntInt',A=field(g,visit,'OrderInDay',VC),B=calc(g,'Add_IntInt',A=get(g,'CurrentCustomerIndex'),B=1)),calc(g,'Greater_IntInt',A=field(g,visit,'VisitNumber',VC),B=0),calc(g,'NotEqual_NameName',A=field(g,visit,'CustomerID',VC),B='None')]:
  end,bad=branch(g,end,condition);failure(g,bad)
 end,bad=branch(g,end,calc(g,'NotEqual_ClassClass',A=field(g,visit,'CustomerClass',VC),B='None'));failure(g,bad)
 end=assign(g,end,'ActiveVisit',visit);end=assign(g,end,'SelectedCustomerClass',field(g,visit,'CustomerClass',VC));end=assign(g,end,'QueueCycleInProgress','true');end=status(g,end,'CustomerCycle')
 end=run(g,end,'HideDayPresentation');end=run(g,end,'CloseRecordShopInteractionModals');end=assign(g,end,'CustomerSpawnAuthorized','true');run(g,end,'SpawnTutorialCustomer')

 g=fn(bp,'ApplyVisitContext');end,no=valid(g,get(g,'ActiveVisit'),g.find_graph_entry_pin());end=guard(g,end,get(g,'ActiveCustomer'))
 profile=field(g,get(g,'ActiveCustomer'),'CustomerProfile',CC)
 split=action(g,'Break Customer Data',[profile]);link(profile,next(p for p in split.list_input_pins() if str(p.get_pin_name())=='CustomerData'))
 make=action(g,'Make Customer Data')
 for p in make.list_input_pins():
  key=str(p.get_pin_name())
  if '_' not in key:continue
  if key.startswith('CustomerID_'):link(calc(g,'Conv_NameToString',InName=field(g,get(g,'ActiveVisit'),'CustomerID',VC)),p)
  else:
   source=split.find_output_pin(key)
   if source.is_valid():link(source,p)
 setter=g.add_set_member_variable_node('CustomerProfile',CC);link(get(g,'ActiveCustomer'),pin(setter,'self'));link(make.list_output_pins()[0],pin(setter,'CustomerProfile'));link(end,setter.find_execute_pin())

 g=fn(bp,'AfterCustomerCycle');end,no=valid(g,get(g,'ActiveVisit'),g.find_graph_entry_pin());end=check(g,end,get(g,'QueueCycleInProgress'));end=check(g,end,stage(g,'CustomerCycle'))
 end=assign(g,end,'QueueCycleInProgress','false');end=dispatch(g,end,'On Customer Visit Completed',Visit=get(g,'ActiveVisit'));end=assign(g,end,'ActiveVisit','None')
 end=assign(g,end,'CurrentCustomerIndex',calc(g,'Add_IntInt',A=get(g,'CurrentCustomerIndex'),B=1))
 more,last=branch(g,end,calc(g,'Less_IntInt',A=get(g,'CurrentCustomerIndex'),B=array_len(g,get(g,'CustomerQueue'))))
 more=status(g,more,'BetweenCustomers');timer(g,more,'SpawnQueuedCustomer',.35)
 run(g,last,'EndCurrentDay')

 g=fn(bp,'EndCurrentDay');end=check(g,g.find_graph_entry_pin(),stage(g,'CustomerCycle'))
 end=check(g,end,calc(g,'GreaterEqual_IntInt',A=get(g,'CurrentCustomerIndex'),B=array_len(g,get(g,'CustomerQueue'))))
 yes,end=branch(g,end,get(g,'QueueCycleInProgress'));yes,end=valid(g,get(g,'ActiveCustomer'),end)
 end=status(g,end,'DayEnding');end=assign(g,end,'DayCustomersComplete','true');end=run(g,end,'StopStoreBGM');end=run(g,end,'ShowDayPresentation')
 end=dispatch(g,end,'On Day Ended',Day=get(g,'CurrentDay'));timer(g,end,'FinishDayTransition',.75)
 g=fn(bp,'FinishDayTransition');end=check(g,g.find_graph_entry_pin(),stage(g,'DayEnding'))
 more,last=branch(g,end,calc(g,'Less_IntInt',A=get(g,'CurrentDay'),B=array_len(g,field(g,get(g,'WeekSchedule'),'Days',WC))))
 run(g,more,'BeginDay',DayNumber=calc(g,'Add_IntInt',A=get(g,'CurrentDay'),B=1))
 yes,last=branch(g,last,get(g,'FinalStoryEventTriggered'));last=assign(g,last,'FinalStoryEventTriggered','true');last=status(g,last,'FinalStoryEvent');last=run(g,last,'ShowDayPresentation')
 dispatch(g,last,'On Final Story Event',EventID=field(g,get(g,'WeekSchedule'),'FinalStoryEventID',WC))

 g=fn(bp,'StartListeningWindow');end=run(g,g.find_graph_entry_pin(),'StopStoreBGM');timer(g,end,'EndListeningWindow',get(g,'ListeningDuration'))
 g=fn(bp,'EndListeningWindow');end,no=valid(g,get(g,'ActiveCustomer'),g.find_graph_entry_pin());end,no=valid(g,get(g,'TurntableRef'),end)
 equal=calc(g,'EqualEqual_ByteByte',A=get(g,'CurrentState'),B=4);end=check(g,end,equal)
 invoke(g,end,TC+':BeginTonearmReturn',self=get(g,'TurntableRef'))
 g=fn(bp,'StopStoreBGM');end=assign(g,g.find_graph_entry_pin(),'StoreBGMRequested','false');yes,no=valid(g,get(g,'StoreBGMRef'),end)
 yes,_=invoke(g,yes,'/Script/Engine.AudioComponent.FadeOut',self=get(g,'StoreBGMRef'),FadeOutDuration=.6,FadeVolumeLevel=0)
 endnode=setv(g,'StoreBGMRef','None');link(yes,endnode.find_execute_pin());link(no,endnode.find_execute_pin())

 # Store BGM is a separate component on the same authority. Loop by completion
 # event so source LP SoundWaves and their nonlooping semantics remain unchanged.
 g=eg;end=assign(g,bgm.find_then_pin(),'StoreBGMRequested','true')
 yes,no=valid(g,get(g,'StoreBGMRef'),end);playing=call(g,'/Script/Engine.AudioComponent.IsPlaying');link(get(g,'StoreBGMRef'),pin(playing,'self'));playing,stopped=branch(g,yes,pin(playing,'ReturnValue',True))
 create=call(g,'/Script/Engine.GameplayStatics.CreateSound2D');link(no,create.find_execute_pin());link(stopped,create.find_execute_pin());link(get(g,'StoreBGMSound'),pin(create,'Sound'));val(pin(create,'bAutoDestroy'),'true');val(pin(create,'bPersistAcrossLevelTransition'),'false')
 end=assign(g,create.find_then_pin(),'StoreBGMRef',pin(create,'ReturnValue',True));end,invalid=valid(g,get(g,'StoreBGMRef'),end)
 bind=action(g,'Bind Event to On Audio Finished',[get(g,'StoreBGMRef')],unreal.AudioComponent);link(pin(bgm_end,'OutputDelegate',True),pin(bind,'Delegate'));link(end,bind.find_execute_pin())
 invoke(g,bind.find_then_pin(),'/Script/Engine.AudioComponent.FadeIn',self=get(g,'StoreBGMRef'),FadeInDuration=.5,FadeVolumeLevel=.18)
 end=check(g,bgm_end.find_then_pin(),get(g,'StoreBGMRequested'));run(g,end,'StartStoreBGM')
 end=check(g,tutorial.find_then_pin(),get(g,'EnableDaySchedule'));end=run(g,end,'DismissTutorialHint');run(g,end,'BeginDay',DayNumber=1)
 assert L.compile_blueprint(bp)

 # The sole existing spawn node serves tutorial and all queued visits.
 spawn=byname(eg,'K2Node_SpawnActorFromClass_0');val(pin(spawn,'Class'),CC);link(get(eg,'SelectedCustomerClass'),pin(spawn,'Class'))
 apply=call(eg,FC+':ApplyVisitContext');splice(byname(eg,'K2Node_VariableSet_0').find_then_pin(),apply)
 # A one-use spawn token also protects the reused legacy event itself.
 tutorial_graph=G.get_graph_editor_by_name(bp,'StartTutorialCustomer')
 tutorial_call=next(n for n in tutorial_graph.list_all_nodes() if str(n.get_node_title()).replace(' ','')=='SpawnTutorialCustomer')
 grant=setv(tutorial_graph,'CustomerSpawnAuthorized','true')
 splice(list(tutorial_call.find_execute_pin().list_connected_pins())[0],grant)
 legacy=next(n for n in eg.list_all_nodes() if n.get_class().get_name()=='K2Node_CustomEvent' and str(n.get_node_title()).replace(' ','')=='SpawnTutorialCustomer')
 legacy.find_then_pin().break_pin_links()
 permitted=check(eg,legacy.find_then_pin(),get(eg,'CustomerSpawnAuthorized'));permitted=assign(eg,permitted,'CustomerSpawnAuthorized','false')
 occupied,permitted=valid(eg,get(eg,'ActiveCustomer'),permitted);link(permitted,spawn.find_execute_pin())
 # Bind tutorial completion once during original BeginPlay, before prologue entry.
 start=byname(eg,'K2Node_Event_0').find_then_pin();initial=call(eg,FC+':InitializeDaySystem');splice(start,initial)
 bind=action(eg,'Bind Event to On Tutorial Completed',[selfref(eg)],cls(FLOW));link(pin(tutorial,'OutputDelegate',True),pin(bind,'Delegate'));splice(initial.find_then_pin(),bind)
 # Accepted Result owns the only exit token; duplicate/late exits are rejected.
 awaiting=setv(eg,'AwaitingCustomerExit','true');splice(byname(eg,'K2Node_VariableSet_11').find_then_pin(),awaiting)
 end=byname(eg,'K2Node_CustomEvent_4').find_then_pin();after=list(end.list_connected_pins());end.break_pin_links()
 end=check(eg,end,get(eg,'AwaitingCustomerExit'));end=check(eg,end,get(eg,'ResultSubmitted'));end,no=valid(eg,get(eg,'ActiveCustomer'),end)
 end=assign(eg,end,'AwaitingCustomerExit','false')
 unbind=action(eg,'Unbind all Events from Customer Exited',[get(eg,'ActiveCustomer')],cls(CUSTOMER));link(end,unbind.find_execute_pin())
 end,_=invoke(eg,unbind.find_then_pin(),'/Script/Engine.Actor.K2_DestroyActor',self=get(eg,'ActiveCustomer'))
 for p in after:link(end,p)
 advance=call(eg,FC+':AfterCustomerCycle');splice(byname(eg,'K2Node_CallFunction_3').find_then_pin(),advance)
 listen=call(eg,FC+':StartListeningWindow');splice(byname(eg,'K2Node_CallFunction_33').find_then_pin(),listen)
 # Stop a pending window before Result; start store music only after Continue.
 clear=call(eg,'/Script/Engine.KismetSystemLibrary.K2_ClearTimer');link(selfref(eg),pin(clear,'Object'));val(pin(clear,'FunctionName'),'EndListeningWindow');splice(byname(eg,'K2Node_CallFunction_25').find_then_pin(),clear)
 music=call(eg,FC+':StartStoreBGM');splice(byname(eg,'K2Node_CallFunction_32').find_then_pin(),music)
 assert L.compile_blueprint(bp)
 unreal.get_default_object(bp.generated_class()).set_editor_property('DaySystemInstalled',True)
 for name in funcs:layout(G.get_graph_editor_by_name(bp,name))
 save(bp);R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;report()
