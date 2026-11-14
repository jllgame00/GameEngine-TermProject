"""One-shot Editor Ending/Title migration; reject changed baseline before authoring."""
import unreal,os,json,sys,hashlib,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';FC=FLOW+'.BP_GameFlowManager_C'
BPC='/Game/RecordShop/Interaction/Components/BPC_Interaction'
ENDING='/Game/RecordShop/UI/Ending/WBP_Ending';EC=ENDING+'.WBP_Ending_C'
TITLE='/Game/RecordShop/UI/Title/WBP_Title';TC=TITLE+'.WBP_Title_C'
PROLOGUE='/Game/RecordShop/UI/Prologue/WBP_Prologue'
WC='/Game/RecordShop/Data/Schedule/BP_WeekScheduleDefinition.BP_WeekScheduleDefinition_C'
MAP='/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'saved':[]}
DATA=json.loads((ROOT/'Scripts/Unreal/ending_content.json').read_text(encoding='utf8'))
NT=L.get_basic_type_by_name('name');IT=L.get_basic_type_by_name('int');BT=L.get_basic_type_by_name('bool');WT=L.get_object_reference_type(unreal.UserWidget)
CHANGED={'EventGraph','BeginPrologue','AdvancePrologue','StartTutorialCustomer','BeginDay','SpawnQueuedCustomer','StartListeningWindow','EndCurrentDay','FinishDayTransition'}
def owncall(g,end,name,**args):return own(g,end,FC,name,**args)
def phase(g,value):return calc(g,'EqualEqual_NameName',A=get(g,'PresentationPhase'),B=value)
def addvar(bp,name,kind):
 if name not in list(map(str,L.list_member_variable_names(bp,False))):assert L.add_member_variable(bp,name,kind)
def save(bp):
 assert L.compile_blueprint(bp),bp.get_path_name();assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 R['saved'].append(bp.get_path_name());OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
def graph(bp,name):
 return [{'id':n.get_name(),'title':str(n.get_node_title()),'class':n.get_class().get_name(),'pins':[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[q.get_owning_node().get_name()+':'+str(q.get_pin_name())for q in p.list_connected_pins()]}for p in n.list_all_pins()]}for n in G.get_graph_editor_by_name(bp,name).list_all_nodes()]
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest()
def guard_entry(bp,name,allowed_path=FC+':IsGameplayPresentation'):
 g=G.get_graph_editor_by_name(bp,name);entry=g.find_graph_entry_pin();after=list(entry.list_connected_pins());entry.break_pin_links()
 n=call(g,allowed_path);yes,_=branch(g,entry,pin(n,'Allowed',True))
 for p in after:link(yes,p)
def new_ui(path):
 bp=unreal.load_asset(path)
 if bp is None:bp=unreal.EditorAssetLibrary.duplicate_asset(PROLOGUE,path)
 assert bp;return bp
def widgets(bp):
 tree=next(t for t in unreal.ObjectIterator(unreal.WidgetTree)if t.get_outer()==bp)
 return {w.get_name():w for w in unreal.ObjectIterator(unreal.Widget)if w.get_outer()==tree}
def configure_ui(bp,is_title):
 ws=widgets(bp);font=unreal.load_asset('/Game/RecordShop/UI/Fonts/NanumGothic_Font')
 for key,size in [('RecordTitle',36 if is_title else 32),('ScoreStatus',22),('RecordID',22)]:ws[key].set_default_font(unreal.SlateFontInfo(font_object=font,typeface_font_name='Default',size=size))
 ws['Heading'].set_visibility(unreal.SlateVisibility.COLLAPSED);ws['ScoreStatus'].set_auto_wrap_text(True)
 ws['ResultPanel'].slot.set_anchors(unreal.Anchors(unreal.Vector2D(.25,.23)if is_title else unreal.Vector2D(.12,.10),unreal.Vector2D(.75,.77)if is_title else unreal.Vector2D(.88,.90)))
 ws['ResultPanel'].slot.set_offsets(unreal.Margin(0,0,0,0))
 ws['ScoreStatus'].slot.set_size(unreal.SlateChildSize(1,unreal.SlateSizeRule.FILL))
 if is_title:
  ws['RecordTitle'].set_text(DATA['title']);ws['ScoreStatus'].set_text('');ws['RecordID'].set_text(DATA['new_game'])
  if 'Quit'not in ws:
   quit=unreal.EditorUtilityLibrary.add_source_widget(bp,unreal.Button,'Quit','ResultLayout')
   quit.set_style(ws['Continue'].get_editor_property('widget_style'))
   label=unreal.EditorUtilityLibrary.add_source_widget(bp,unreal.RichTextBlock,'QuitLabel','Quit')
   label.set_default_font(unreal.SlateFontInfo(font_object=font,typeface_font_name='Default',size=22));label.set_text(DATA['quit_game']);quit.slot.set_padding(unreal.Margin(0,12,0,0))
   label.set_default_color_and_opacity(unreal.SlateColor(specified_color=unreal.LinearColor(.92,.91,.87,1)))
   quit.set_background_color(ws['Continue'].get_editor_property('background_color'))
 assert L.compile_blueprint(bp)
 g=evgraph(bp);callback=byname(g,'K2Node_CustomEvent_0');callback.find_then_pin().break_pin_links()
 yes,_=valid(g,get(g,'FlowRef'),callback.find_then_pin())
 own(g,yes,FC,'StartNewGame'if is_title else 'AdvanceEnding',self=get(g,'FlowRef'),Origin=selfref(g))
 if is_title and not any(str(n.get_node_title())=='HandleQuit'for n in g.list_all_nodes()):
  event=g.add_custom_event_node('HandleQuit');yes,_=valid(g,get(g,'FlowRef'),event.find_then_pin());own(g,yes,FC,'QuitToDesktop',self=get(g,'FlowRef'),Origin=selfref(g))
  init=next(n for n in g.list_all_nodes()if n.get_class().get_name()=='K2Node_Event'and 'Initialized'in str(n.get_node_title()))
  bind=action(g,'Bind Event to OnClicked',[get(g,'Quit')],unreal.Button);link(get(g,'Quit'),pin(bind,'self'));link(pin(event,'OutputDelegate',True),pin(bind,'Delegate'));splice(init.find_then_pin(),bind)
 assert L.compile_blueprint(bp)
def create_ui(g,end,member,path):
 n=action(g,'Create Widget');val(pin(n,'Class'),path+'.'+path.rsplit('/',1)[-1]+'_C')
 pc=call(g,'/Script/Engine.GameplayStatics.GetPlayerController');link(pin(pc,'ReturnValue',True),pin(n,'OwningPlayer'));link(end,n.find_execute_pin())
 end=assign(g,n.find_then_pin(),member,pin(n,'ReturnValue',True));ref=get(g,member)
 setter=g.add_set_member_variable_node('FlowRef',TC if path==TITLE else EC);link(ref,pin(setter,'self'));link(selfref(g),pin(setter,'FlowRef'));link(end,setter.find_execute_pin())
 return invoke(g,setter.find_then_pin(),'/Script/UMG.UserWidget.AddToViewport',self=ref,ZOrder=100)[0]
try:
 unreal.InternationalizationLibrary.set_current_language('en',False)
 baseline=json.loads((ROOT/'Saved/MVPCompletion/ending-start-state.json').read_text())
 for path,sha in baseline['files_sha256'].items():
  if path.startswith('Content/'):assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,'One-shot installer requires original audited baseline: '+path
 bp=unreal.load_asset(FLOW);component=unreal.load_asset(BPC)
 before_graphs={name:digest(graph(bp,name))for name in [str(g.get_name())for g in L.list_graphs(bp)]}
 original_component=digest(graph(component,'TryInteract'))
 ending=new_ui(ENDING);title=new_ui(TITLE)
 for name,typ in [('PresentationPhase',NT),('FrontEndDestination',NT),('EndingStep',IT),('FrontEndInputReady',BT),('FrontEndInputDelay',L.get_member_variable_type(bp,'StoreBGMFadeInDuration')),('EndingWidgetRef',L.get_object_reference_type(ending.generated_class())),('TitleWidgetRef',L.get_object_reference_type(title.generated_class()))]:addvar(bp,name,typ)
 timer_names={'ReadyFrontEndInput','FinishFrontEndTravel'}
 for name in before_graphs:
  for node in G.get_graph_editor_by_name(bp,name).list_all_nodes():
   if str(node.get_node_title()).replace(' ','')=='SetTimerbyFunctionName':
    p=pin(node,'FunctionName');assert not p.list_connected_pins(),'Dynamic timer needs an explicit cleanup contract';timer_names.add(p.get_pin_value())
 methods=['BootPresentation','ShowTitle','BeginEnding','RefreshEndingPresentation','AdvanceEnding','StartNewGame','QuitToDesktop','ReturnToTitle','BeginFrontEndTravel','FinishFrontEndTravel','LockPresentationInput','ReadyFrontEndInput','RemoveFrontEndWidgets','IsGameplayPresentation','CompleteDayPresentationAudio','ClearPresentationTimers']
 for name in methods:
  g=fn(bp,name)
  if name in ('AdvanceEnding','StartNewGame','QuitToDesktop'):inputs(g,[('Origin',WT)])
  if name=='BeginEnding':inputs(g,[('EventID',NT)])
  if name=='BeginFrontEndTravel':inputs(g,[('Destination',NT)])
  if name=='IsGameplayPresentation':outputs(g,[('Allowed',BT)]);g.set_is_pure_function(True)
 assert L.compile_blueprint(bp)
 configure_ui(ending,False);configure_ui(title,True)
 g=fn(bp,'ClearPresentationTimers');end=g.find_graph_entry_pin()
 for name in sorted(timer_names):end=clear_timer(g,end,name)
 g=fn(bp,'IsGameplayPresentation');ret(g,g.find_graph_entry_pin(),Allowed=phase(g,'Playing'))
 # UI-only + existing pawn input stack blocks movement, look and interaction.
 g=fn(bp,'LockPresentationInput');n=call(g,'/Script/Engine.GameplayStatics.GetPlayerController');pc=pin(n,'ReturnValue',True);end,_=valid(g,pc,g.find_graph_entry_pin())
 setter=g.add_set_member_variable_node('bShowMouseCursor','/Script/Engine.PlayerController');link(pc,pin(setter,'self'));val(pin(setter,'bShowMouseCursor'),'true');link(end,setter.find_execute_pin());end=setter.find_then_pin()
 for name in ('SetIgnoreMoveInput','SetIgnoreLookInput'):end=invoke(g,end,'/Script/Engine.Controller.'+name,self=pc,bNewMoveInput='true')[0]if name=='SetIgnoreMoveInput'else invoke(g,end,'/Script/Engine.Controller.'+name,self=pc,bNewLookInput='true')[0]
 end=invoke(g,end,'/Script/UMG.WidgetBlueprintLibrary.SetInputMode_UIOnlyEx',PlayerController=pc,bFlushInput='true')[0]
 n=call(g,'/Script/Engine.GameplayStatics.GetPlayerPawn');pawn=pin(n,'ReturnValue',True);end,_=valid(g,pawn,end);invoke(g,end,'/Script/Engine.Actor.DisableInput',self=pawn,PlayerController=pc)
 g=fn(bp,'RemoveFrontEndWidgets');end=g.find_graph_entry_pin()
 for member,kind in [('EndingWidgetRef',EC),('TitleWidgetRef',TC)]:
  yes,no=valid(g,get(g,member),end);setter=g.add_set_member_variable_node('FlowRef',kind);link(get(g,member),pin(setter,'self'));val(pin(setter,'FlowRef'),'None');link(yes,setter.find_execute_pin())
  yes=invoke(g,setter.find_then_pin(),'/Script/UMG.Widget.RemoveFromParent',self=get(g,member))[0];join=setv(g,member,'None');link(yes,join.find_execute_pin());link(no,join.find_execute_pin());end=join.find_then_pin()
 g=fn(bp,'ReadyFrontEndInput');end=g.find_graph_entry_pin();allowed=calc(g,'BooleanOR',A=phase(g,'Title'),B=calc(g,'BooleanOR',A=phase(g,'EndingDialogue'),B=calc(g,'BooleanOR',A=phase(g,'EndingCompletion'),B=phase(g,'Credits'))));end=check(g,end,allowed);end=assign(g,end,'FrontEndInputReady','true')
 is_title,other=branch(g,end,phase(g,'Title'))
 for path,member,kind in [(is_title,'TitleWidgetRef',TC),(other,'EndingWidgetRef',EC)]:
  path,_=valid(g,get(g,member),path);button=field(g,get(g,member),'Continue',kind);path=invoke(g,path,'/Script/UMG.Widget.SetIsEnabled',self=button,bInIsEnabled='true')[0]
  pc=call(g,'/Script/Engine.GameplayStatics.GetPlayerController');path=invoke(g,path,'/Script/UMG.Widget.SetUserFocus',self=button,PlayerController=pin(pc,'ReturnValue',True))[0]
  if member=='TitleWidgetRef':invoke(g,path,'/Script/UMG.Widget.SetIsEnabled',self=field(g,get(g,member),'Quit',kind),bInIsEnabled='true')
 g=fn(bp,'ShowTitle');end=check(g,g.find_graph_entry_pin(),phase(g,'Boot'));end=assign(g,end,'PresentationPhase','Title');end=assign(g,end,'FrontEndInputReady','false');end=owncall(g,end,'RemoveFrontEndWidgets');end=create_ui(g,end,'TitleWidgetRef',TITLE);end=owncall(g,end,'LockPresentationInput');timer(g,end,'ReadyFrontEndInput',get(g,'FrontEndInputDelay'))
 g=fn(bp,'BootPresentation');end=check(g,g.find_graph_entry_pin(),phase(g,'Boot'))
 mode=call(g,'/Script/Engine.GameplayStatics.GetGameMode');opts=field(g,pin(mode,'ReturnValue',True),'OptionsString','/Script/Engine.GameModeBase')
 def has_option(key):
  n=call(g,'/Script/Engine.GameplayStatics.HasOption');link(opts,pin(n,'Options'));val(pin(n,'InKey'),key);return pin(n,'ReturnValue',True)
 show,decide=branch(g,end,has_option('RecordShopTitle'));owncall(g,show,'ShowTitle')
 cmd=call(g,'/Script/Engine.KismetSystemLibrary.GetCommandLine');contains=call(g,'/Script/Engine.KismetStringLibrary.Contains');link(pin(cmd,'ReturnValue',True),pin(contains,'SearchIn'));val(pin(contains,'Substring'),'-RecordShopProductionValidation')
 link(decide,cmd.find_execute_pin());play,show=branch(g,cmd.find_then_pin(),calc(g,'BooleanOR',A=has_option('RecordShopNewGame'),B=pin(contains,'ReturnValue',True)));owncall(g,show,'ShowTitle');play=assign(g,play,'PresentationPhase','Playing');owncall(g,play,'BeginPrologue')
 g=fn(bp,'CompleteDayPresentationAudio');end=g.find_graph_entry_pin();last,normal=branch(g,end,calc(g,'EqualEqual_IntInt',A=get(g,'CurrentDay'),B=array_len(g,field(g,get(g,'WeekSchedule'),'Days',WC))))
 owncall(g,normal,'StopStoreBGM');last=assign(g,last,'PresentationPhase','EndingPending');owncall(g,last,'LockPresentationInput')
 g=fn(bp,'BeginEnding');event_id=inputs(g,[('EventID',NT)])['EventID'];end=check(g,g.find_graph_entry_pin(),phase(g,'EndingPending'))
 for condition in [get(g,'FinalStoryEventTriggered'),calc(g,'EqualEqual_NameName',A=get(g,'DayPhase'),B='FinalStoryEvent'),calc(g,'EqualEqual_NameName',A=event_id,B=field(g,get(g,'WeekSchedule'),'FinalStoryEventID',WC)),calc(g,'EqualEqual_IntInt',A=get(g,'CurrentDay'),B=array_len(g,field(g,get(g,'WeekSchedule'),'Days',WC))),calc(g,'Not_PreBool',A=get(g,'QueueCycleInProgress')),calc(g,'Not_PreBool',A=bool_valid(g,get(g,'ActiveCustomer'))),calc(g,'Not_PreBool',A=bool_valid(g,get(g,'ActiveVisit')))]:end=check(g,end,condition)
 end=assign(g,end,'PresentationPhase','EndingDialogue');end=assign(g,end,'EndingStep',0);end=owncall(g,end,'CloseRecordShopInteractionModals');end=owncall(g,end,'ClearNarrativeVisitContext');end=owncall(g,end,'HideDayPresentation');end=create_ui(g,end,'EndingWidgetRef',ENDING);owncall(g,end,'RefreshEndingPresentation')
 g=fn(bp,'RefreshEndingPresentation');end,_=valid(g,get(g,'EndingWidgetRef'),g.find_graph_entry_pin());end=assign(g,end,'FrontEndInputReady','false')
 end=invoke(g,end,'/Script/UMG.Widget.SetIsEnabled',self=field(g,get(g,'EndingWidgetRef'),'Continue',EC),bInIsEnabled='false')[0]
 for index,page in enumerate(DATA['pages']):
  yes,end=branch(g,end,calc(g,'EqualEqual_IntInt',A=get(g,'EndingStep'),B=index));yes=assign(g,yes,'PresentationPhase',page['phase']);yes=own(g,yes,EC,'SetPresentation',self=get(g,'EndingWidgetRef'),Title=page['title'],Body=page['body'],Action=page['action']);yes=owncall(g,yes,'LockPresentationInput');timer(g,yes,'ReadyFrontEndInput',get(g,'FrontEndInputDelay'))
 g=fn(bp,'AdvanceEnding');origin=inputs(g,[('Origin',WT)])['Origin'];end=check(g,g.find_graph_entry_pin(),get(g,'FrontEndInputReady'));end=check(g,end,calc(g,'EqualEqual_ObjectObject',A=origin,B=get(g,'EndingWidgetRef')))
 allowed=calc(g,'BooleanOR',A=phase(g,'EndingDialogue'),B=calc(g,'BooleanOR',A=phase(g,'EndingCompletion'),B=phase(g,'Credits')));end=check(g,end,allowed);end=assign(g,end,'FrontEndInputReady','false')
 last,more=branch(g,end,calc(g,'EqualEqual_IntInt',A=get(g,'EndingStep'),B=len(DATA['pages'])-1));owncall(g,last,'ReturnToTitle')
 increment=setv(g,'EndingStep');link(calc(g,'Add_IntInt',A=get(g,'EndingStep'),B=1),pin(increment,'EndingStep'));link(more,increment.find_execute_pin());owncall(g,increment.find_then_pin(),'RefreshEndingPresentation')
 for name,dest in [('StartNewGame','NewGame'),('QuitToDesktop','Quit')]:
  g=fn(bp,name);origin=inputs(g,[('Origin',WT)])['Origin'];end=check(g,g.find_graph_entry_pin(),phase(g,'Title'));end=check(g,end,get(g,'FrontEndInputReady'));end=check(g,end,calc(g,'EqualEqual_ObjectObject',A=origin,B=get(g,'TitleWidgetRef')));owncall(g,end,'BeginFrontEndTravel',Destination=dest)
 g=fn(bp,'ReturnToTitle');allowed=calc(g,'BooleanOR',A=phase(g,'EndingPending'),B=calc(g,'BooleanOR',A=phase(g,'EndingDialogue'),B=calc(g,'BooleanOR',A=phase(g,'EndingCompletion'),B=phase(g,'Credits'))));end=check(g,g.find_graph_entry_pin(),allowed);owncall(g,end,'BeginFrontEndTravel',Destination='Title')
 g=fn(bp,'BeginFrontEndTravel');dest=inputs(g,[('Destination',NT)])['Destination'];end=g.find_graph_entry_pin()
 is_title=calc(g,'EqualEqual_NameName',A=dest,B='Title');other=calc(g,'BooleanOR',A=calc(g,'EqualEqual_NameName',A=dest,B='NewGame'),B=calc(g,'EqualEqual_NameName',A=dest,B='Quit'))
 allowed=calc(g,'BooleanOR',A=calc(g,'BooleanAND',A=phase(g,'Title'),B=other),B=calc(g,'BooleanAND',A=is_title,B=calc(g,'BooleanOR',A=phase(g,'EndingPending'),B=calc(g,'BooleanOR',A=phase(g,'EndingDialogue'),B=calc(g,'BooleanOR',A=phase(g,'EndingCompletion'),B=phase(g,'Credits'))))))
 end=check(g,end,allowed);end=assign(g,end,'PresentationPhase','Leaving');end=assign(g,end,'FrontEndDestination',dest);end=assign(g,end,'FrontEndInputReady','false')
 end=owncall(g,end,'ClearPresentationTimers')
 end=owncall(g,end,'CloseRecordShopInteractionModals');end=owncall(g,end,'ClearNarrativeVisitContext');end=owncall(g,end,'HideDayPresentation');end=owncall(g,end,'DismissTutorialHint');end=owncall(g,end,'RemoveFrontEndWidgets');end=owncall(g,end,'LockPresentationInput')
 # Snapshot before Stop can auto-destroy a zero-duration fade component.
 assert g.add_local_variable('WaitForAudio',BT);end=local_set(g,end,'WaitForAudio','false');yes,no=valid(g,get(g,'StoreBGMRef'),end)
 playing=call(g,'/Script/Engine.AudioComponent.IsPlaying');link(get(g,'StoreBGMRef'),pin(playing,'self'));positive=calc(g,'Greater_DoubleDouble',A=get(g,'StoreBGMFadeOutDuration'),B=0)
 yes=local_set(g,yes,'WaitForAudio',calc(g,'BooleanAND',A=pin(playing,'ReturnValue',True),B=positive));stop=call(g,FC+':StopStoreBGM');link(yes,stop.find_execute_pin());link(no,stop.find_execute_pin())
 wait,instant=branch(g,stop.find_then_pin(),local_get(g,'WaitForAudio'));timer(g,wait,'FinishFrontEndTravel',get(g,'StoreBGMFadeOutDuration'));owncall(g,instant,'FinishFrontEndTravel')
 g=fn(bp,'FinishFrontEndTravel');end=check(g,g.find_graph_entry_pin(),phase(g,'Leaving'));end=assign(g,end,'PresentationPhase','Traveling');end=owncall(g,end,'FinishStoreBGMStop');end=owncall(g,end,'ClearPresentationTimers')
 ready,missing=valid(g,get(g,'TurntableRef'),end);ready=invoke(g,ready,'/Script/Engine.Actor.SetActorTickEnabled',self=get(g,'TurntableRef'),bEnabled='false')[0]
 quit,travel=branch(g,ready,calc(g,'EqualEqual_NameName',A=get(g,'FrontEndDestination'),B='Quit'));link(missing,quit.get_owning_node().find_execute_pin());invoke(g,quit,'/Script/Engine.KismetSystemLibrary.QuitGame',QuitPreference='Quit',bIgnorePlatformRestrictions='false')
 options=call(g,'/Script/Engine.KismetMathLibrary.SelectString');val(pin(options,'A'),'RecordShopNewGame=1');val(pin(options,'B'),'RecordShopTitle=1');link(calc(g,'EqualEqual_NameName',A=get(g,'FrontEndDestination'),B='NewGame'),pin(options,'bPickA'))
 invoke(g,travel,'/Script/Engine.GameplayStatics.OpenLevel',LevelName=MAP,bAbsolute='true',Options=pin(options,'ReturnValue',True))
 assert L.compile_blueprint(bp)
 # Preserve the current queue/day transition chain; replace only its audio-policy call.
 g=G.get_graph_editor_by_name(bp,'EndCurrentDay');old=next(n for n in g.list_all_nodes()if str(n.get_node_title()).replace(' ','')=='StopStoreBGM');parents=list(old.find_execute_pin().list_connected_pins());children=list(old.find_then_pin().list_connected_pins());g.remove_nodes([old]);node=call(g,FC+':CompleteDayPresentationAudio')
 for p in parents:link(p,node.find_execute_pin())
 for p in children:link(node.find_then_pin(),p)
 g=G.get_graph_editor_by_name(bp,'FinishDayTransition');old=next(n for n in g.list_all_nodes()if str(n.get_node_title()).replace(' ','')=='ShowDayPresentation');parents=list(old.find_execute_pin().list_connected_pins());children=list(old.find_then_pin().list_connected_pins());g.remove_nodes([old]);node=call(g,FC+':HideDayPresentation')
 for p in parents:link(p,node.find_execute_pin())
 for p in children:link(node.find_then_pin(),p)
 final_dispatch=next(n for n in g.list_all_nodes()if n.get_class().get_name()=='K2Node_CallDelegate')
 owncall(g,final_dispatch.find_then_pin(),'BeginEnding',EventID=field(g,get(g,'WeekSchedule'),'FinalStoryEventID',WC))
 entry=g.find_graph_entry_pin();after=list(entry.list_connected_pins());entry.break_pin_links();yes=check(g,entry,calc(g,'BooleanOR',A=phase(g,'Playing'),B=phase(g,'EndingPending')))
 for p in after:link(yes,p)
 for name in ('BeginPrologue','AdvancePrologue','StartTutorialCustomer','BeginDay','SpawnQueuedCustomer','StartListeningWindow'):guard_entry(bp,name)
 eg=evgraph(bp);old=next(n for n in eg.list_all_nodes()if str(n.get_node_title()).replace(' ','')=='BeginPrologue');parents=list(old.find_execute_pin().list_connected_pins());eg.remove_nodes([old])
 for p in parents:owncall(eg,p,'BootPresentation')
 selected=next(n for n in eg.list_all_nodes()if n.get_class().get_name()=='K2Node_CustomEvent'and str(n.get_node_title()).replace(' ','')=='HandleRecordSelected');after=list(selected.find_then_pin().list_connected_pins());selected.find_then_pin().break_pin_links();allowed=call(eg,FC+':IsGameplayPresentation');yes,_=branch(eg,selected.find_then_pin(),pin(allowed,'Allowed',True))
 for p in after:link(yes,p)
 end_event=action(eg,'Event EndPlay');end=assign(eg,end_event.find_then_pin(),'PresentationPhase','Closed');end=assign(eg,end,'FrontEndInputReady','false');end=assign(eg,end,'StoreBGMRequested','false');end=assign(eg,end,'CurrentStoreBGMRecordID','None');end=assign(eg,end,'StoreBGMSound','None');end=owncall(eg,end,'FinishStoreBGMStop');owncall(eg,end,'ClearPresentationTimers')
 # One existing interaction entry reads the canonical presentation state.
 g=G.get_graph_editor_by_name(component,'TryInteract');entry=g.find_graph_entry_pin();after=list(entry.list_connected_pins());entry.break_pin_links();end,n=invoke(g,entry,'/Script/Engine.GameplayStatics.GetActorOfClass',ActorClass=FC);target=pin(n,'ReturnValue',True);end,missing=valid(g,target,end);allowed=call(g,FC+':IsGameplayPresentation');link(target,pin(allowed,'self'));yes,_=branch(g,end,pin(allowed,'Allowed',True))
 for p in after:link(yes,p);link(missing,p)
 assert L.compile_blueprint(bp);cdo=unreal.get_default_object(bp.generated_class())
 for k,v in dict(PresentationPhase='Boot',FrontEndDestination='None',EndingStep=0,FrontEndInputReady=False,FrontEndInputDelay=.15,EndingWidgetRef=None,TitleWidgetRef=None).items():cdo.set_editor_property(k,v)
 protected={name:sha for name,sha in before_graphs.items()if name not in CHANGED}
 for name,sha in protected.items():assert digest(graph(bp,name))==sha,name
 for item in (ending,title,component,bp):save(item)
 package_paths=['Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset','Content/RecordShop/Interaction/Components/BPC_Interaction.uasset']
 unchanged={p:h for p,h in baseline['files_sha256'].items()if p.startswith('Content/')and p not in package_paths}
 for p,h in unchanged.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 reference={'packages':{p:dict(before=baseline['files_sha256'][p],after=hashlib.sha256((ROOT/p).read_bytes()).hexdigest())for p in package_paths},'unchanged_sha256':unchanged,'protected_graphs':{FLOW:protected},'changed_graphs':{FLOW:{name:dict(before=before_graphs[name],after=digest(graph(bp,name)))for name in CHANGED},BPC:{'TryInteract':dict(before=original_component,after=digest(graph(component,'TryInteract')))}}}
 (ROOT/'Scripts/Unreal/ending_reference.json').write_text(json.dumps(reference,indent=2),encoding='utf8');R.update(protected_assets=len(unchanged),protected_graphs=len(protected),**{'pass':True})
except Exception:R['fatal']=traceback.format_exc();R['pass']=False
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
