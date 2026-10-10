"""One-time V4 integration via supported Editor graph/widget APIs. No test content.

Missing customer/record scoring mappings deliberately remain unavailable. Audio=None
completes synchronously after the ordinary ordered Play action; it is not playback.
"""
import json, sys, traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir())
sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import *
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager'
TT='/Game/RecordShop/Interaction/Actors/BP_Turntable'
SHELF='/Game/RecordShop/Interaction/Actors/BP_RecordShelf'
DM='/Game/DialogueManager'
UI='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
DUI='/Game/RecordShop/UI/Dialogue/WBP_Dialogue'
TUI='/Game/RecordShop/UI/Turntable/WBP_Turntable'
R={'complete':False,'saved':[]}

def named(g,name):return next(n for n in g.list_all_nodes() if n.get_name()==name)
def chain(previous,node):link(previous,node.find_execute_pin());return node.find_then_pin()
def branch(g,previous,condition,yes=True):
 n=g.add_branch_node();link(condition,pin(n,'Condition'));link(previous,n.find_execute_pin());return pin(n,'then' if yes else 'else',True)
def eq(g,a,value):
 n=call(g,'/Script/Engine.KismetMathLibrary.EqualEqual_IntInt');link(a,pin(n,'A'));val(pin(n,'B'),value);return pin(n,'ReturnValue',True)
def state(g,previous,value):
 n=call(g,FLOW+'.BP_GameFlowManager_C.SetGameFlowState');val(pin(n,'NewState'),'NewEnumerator'+str(value));return chain(previous,n)
def member(g,obj,name,path):
 n=g.add_get_member_variable_node(name,path+'.'+path.rsplit('/',1)[1]+'_C');link(obj,pin(n,'self'));return pin(n,name,True)
def insert(previous,node):
 downstream=list(previous.list_connected_pins());previous.break_pin_links();chain(previous,node)
 for p in downstream:link(node.find_then_pin(),p)
def callself(g,path,previous):return chain(previous,call(g,path))
def boolvar(bp,name):assert evgraph(bp).add_member_variable(name,L.get_basic_type_by_name('bool'))
def selfpin(g):
 n=action(g,'Self');return pin(n,'self',True)
def dispatch(g,name,previous):return chain(previous,action(g,'Call'+name))

try:
 assert not unreal.EditorAssetLibrary.does_asset_exist(UI),'Already installed; inspect rather than replay'
 flow=unreal.load_asset(FLOW);tt=unreal.load_asset(TT);dm=unreal.load_asset(DM)
 fg=evgraph(flow);tg=evgraph(tt);dg=evgraph(dm)
 # Correct only the demonstrably wrong maximum assignment. AvailableLPs has no
 # usable record lookup contract, so no tag mapping or qualitative rule is added.
 maximum=pin(named(dg,'K2Node_VariableSet_3'),'MaxScore');maximum.break_pin_links()
 link(pin(named(dg,'K2Node_CallFunction_4'),'Outscore',True),maximum)
 assert L.add_event_dispatcher(dm,'OnLPScoreEvaluated')
 assert L.add_event_dispatcher_parameter(dm,'OnLPScoreEvaluated','RawScore',L.get_basic_type_by_name('int'))
 assert L.compile_blueprint(dm)
 scored=action(dg,'CallOnLPScoreEvaluated');calc=named(dg,'K2Node_CallFunction_5')
 link(pin(calc,'Outscore',True),pin(scored,'RawScore'));chain(calc.find_then_pin(),scored)

 # Output events are owned by the existing turntable, independent of UI lifetime.
 for name in ['OnPlaybackStarted','OnTurntableCompleted']:assert L.add_event_dispatcher(tt,name)
 boolvar(tt,'CompletionSent')
 assert tg.add_member_variable('PlaybackAudio',L.get_object_reference_type(unreal.AudioComponent))
 assert L.compile_blueprint(tt)
 finish=function(tt,'CompletePlayback')
 p=branch(finish,finish.find_graph_entry_pin(),get(finish,'HasRecord'))
 p=branch(finish,p,eq(finish,get(finish,'TurntableStep'),5))
 p=branch(finish,p,get(finish,'CompletionSent'),False)
 p=chain(p,setv(finish,'CompletionSent','true'))
 p=chain(p,setv(finish,'PlaybackAudio'))
 dispatch(finish,'OnTurntableCompleted',p)
 assert L.compile_blueprint(tt)
 audio_finished=tg.add_custom_event_node('HandleAudioFinished')
 callself(tg,TT+'.BP_Turntable_C.CompletePlayback',audio_finished.find_then_pin())
 assert L.compile_blueprint(tt)
 play=G.get_graph_editor_by_name(tt,'PlayRecord')
 # Remove the misleading pre-validation PLAYING RECORD print from execution.
 pre=named(play,'K2Node_CallFunction_0');up=pre.find_execute_pin().list_connected_pins()[0];down=pre.find_then_pin().list_connected_pins()[0]
 pre.find_execute_pin().break_pin_links();pre.find_then_pin().break_pin_links();link(up,down)
 noaudio=named(play,'K2Node_CallFunction_4');val(pin(noaudio,'InString'),'NO AUDIO ASSIGNED - completing interaction without playback')
 none_step=named(play,'K2Node_VariableSet_0')
 p=dispatch(play,'OnPlaybackStarted',none_step.find_then_pin())
 callself(play,TT+'.BP_Turntable_C.CompletePlayback',p)
 # Real audio uses an AudioComponent delegate, never a guessed duration.
 sound=named(play,'K2Node_CallFunction_2');audio=pin(sound,'Sound').list_connected_pins()[0]
 upstream=sound.find_execute_pin().list_connected_pins()[0];sound.find_execute_pin().break_pin_links();sound.find_then_pin().break_pin_links()
 start_audio=tg.add_custom_event_node('StartPlaybackAudio')
 record_break=action(tg,'BreakST_RecordData',[get(tg,'CurrentRecord')])
 source=next(x for x in record_break.list_all_pins() if str(x.get_pin_name()).startswith('Audio_'))
 spawn=call(tg,'/Script/Engine.GameplayStatics.CreateSound2D');link(source,pin(spawn,'Sound'));val(pin(spawn,'bAutoDestroy'),'true')
 p=chain(start_audio.find_then_pin(),spawn);setaudio=setv(tg,'PlaybackAudio');link(pin(spawn,'ReturnValue',True),pin(setaudio,'PlaybackAudio'));p=chain(p,setaudio)
 good,bad=valid(tg,get(tg,'PlaybackAudio'),p)
 bind=action(tg,'BindEventtoOnAudioFinished',[get(tg,'PlaybackAudio')],unreal.AudioComponent)
 link(pin(audio_finished,'OutputDelegate',True),pin(bind,'Delegate'));p=chain(good,bind)
 p=chain(p,setv(tg,'TurntableStep','5'));p=dispatch(tg,'OnPlaybackStarted',p)
 start=call(tg,'/Script/Engine.AudioComponent.Play');link(get(tg,'PlaybackAudio'),pin(start,'self'));chain(p,start)
 failure=call(tg,'/Script/Engine.KismetSystemLibrary.PrintString');val(pin(failure,'InString'),'AUDIO COMPONENT UNAVAILABLE - retry Play');chain(bad,failure)
 assert L.compile_blueprint(tt)
 callself(play,TT+'.BP_Turntable_C.StartPlaybackAudio',upstream)

 # New selection resets the local ordered interaction and completion guard.
 reset=G.get_graph_editor_by_name(tt,'SetRecord');last=named(reset,'K2Node_VariableSet_1')
 p=chain(last.find_then_pin(),setv(reset,'CompletionSent','false'))
 p=chain(p,setv(reset,'TurntableStep','0'));chain(p,setv(reset,'SelectedRPM','0'))

 # Minimal integration result: record metadata and honest availability, no judgment.
 settings=unreal.get_default_object(unreal.load_class(None,'/Script/UMGEditor.UMGEditorProjectSettings'))
 old_root=settings.get_editor_property('DefaultRootWidget');old_select=settings.get_editor_property('bUseWidgetTemplateSelector')
 try:
  settings.set_editor_property('bUseWidgetTemplateSelector',False);settings.set_editor_property('DefaultRootWidget',unreal.CanvasPanel)
  ui=unreal.AssetToolsHelpers.get_asset_tools().create_asset('WBP_Result_IntegrationFallback',UI.rsplit('/',1)[0],unreal.WidgetBlueprint,unreal.WidgetBlueprintFactory())
 finally:
  settings.set_editor_property('DefaultRootWidget',old_root);settings.set_editor_property('bUseWidgetTemplateSelector',old_select)
 tree=unreal.find_object(ui,'WidgetTree');root=unreal.find_object(tree,'CanvasPanel_0');assert root
 border=unreal.new_object(unreal.Border,outer=tree,name='ResultPanel');border.set_brush_color(unreal.LinearColor(.025,.025,.035,.97));border.set_padding(unreal.Margin(24,24,24,24))
 slot=root.add_child_to_canvas(border);slot.set_anchors(unreal.Anchors(unreal.Vector2D(.25,.25),unreal.Vector2D(.75,.75)));slot.set_offsets(unreal.Margin(0,0,0,0))
 box=unreal.new_object(unreal.VerticalBox,outer=tree,name='ResultLayout');border.add_child(box)
 for name,text in [('Heading','Result'),('RecordTitle',''),('RecordID',''),('ScoreStatus','Score: unavailable')]:
  label=unreal.new_object(unreal.RichTextBlock,outer=tree,name=name)
  font=unreal.SlateFontInfo();font.set_editor_property('font_object',unreal.load_asset('/Engine/EngineFonts/Roboto'));font.set_editor_property('typeface_font_name','Regular');font.set_editor_property('size',24)
  style=unreal.TextBlockStyle();style.set_editor_property('font',font);style.set_editor_property('color_and_opacity',unreal.SlateColor(specified_color=unreal.LinearColor(1,1,1,1)))
  label.set_default_text_style(style);label.set_auto_wrap_text(True);label.set_text(text);box.add_child_to_vertical_box(label).set_padding(unreal.Margin(0,0,0,18))
 button=unreal.new_object(unreal.Button,outer=tree,name='Continue');label=unreal.new_object(unreal.TextBlock,outer=tree,name='ContinueLabel');label.set_text('Continue');button.add_child(label);box.add_child_to_vertical_box(button)
 assert L.compile_blueprint(ui)
 ug=evgraph(ui);assert ug.add_member_variable('FlowRef',L.get_object_reference_type(cls(FLOW)))
 assert L.add_event_dispatcher(ui,'OnContinue')
 assert L.compile_blueprint(ui)
 init=action(ug,'OnInitialized');clicked=ug.add_custom_event_node('ContinueClicked')
 bind=action(ug,'BindEventtoOnClicked',[get(ug,'Continue')],unreal.Button);link(pin(clicked,'OutputDelegate',True),pin(bind,'Delegate'));chain(init.find_then_pin(),bind)
 dispatch(ug,'OnContinue',clicked.find_then_pin())
 update=function(ui,'SetRecordDisplay')
 for name,param in [('RecordTitle','Title'),('RecordID','RecordIdentifier')]:
  value=update.add_graph_input_parameter(param,L.get_basic_type_by_name('text'))
  n=call(update,'/Script/UMG.RichTextBlock.SetText');link(get(update,name),pin(n,'self'));link(value,pin(n,'InText'))
  if name=='RecordTitle':p=chain(update.find_graph_entry_pin(),n)
  else:chain(p,n)
 assert L.compile_blueprint(ui)
 assert fg.add_member_variable('ResultWidgetRef',L.get_object_reference_type(ui.generated_class()))
 for name in ['ResultStartedForCustomer','ResultSubmitted']:boolvar(flow,name)
 assert L.compile_blueprint(flow)
 # CloseDialogue is cleanup only; only the finished handler advances state.
 close=G.get_graph_editor_by_name(flow,'CloseDialogue');last=named(close,'K2Node_CallFunction_4');last.find_execute_pin().break_pin_links()
 event=next(n for n in fg.list_all_nodes() if str(n.get_node_title())=='HandleDialogueFinished')
 event.find_then_pin().break_pin_links();p,_=valid(fg,get(fg,'DialogueWidgetRef'),event.find_then_pin())
 p=callself(fg,FLOW+'.BP_GameFlowManager_C.CloseDialogue',p);state(fg,p,2)
 selected=named(fg,'K2Node_CallFunction_5');state(fg,selected.find_then_pin(),3)
 # Result close clears references before restoring game input.
 close_result=function(flow,'CloseResult')
 p,_=valid(close_result,get(close_result,'ResultWidgetRef'),close_result.find_graph_entry_pin())
 remove=call(close_result,'/Script/UMG.Widget.RemoveFromParent');link(get(close_result,'ResultWidgetRef'),pin(remove,'self'));p=chain(p,remove)
 clear=close_result.add_set_member_variable_node('FlowRef',UI+'.WBP_Result_IntegrationFallback_C');link(get(close_result,'ResultWidgetRef'),pin(clear,'self'));p=chain(p,clear)
 p=chain(p,setv(close_result,'ResultWidgetRef'));restore(close_result,p)
 assert L.compile_blueprint(flow)
 cleanup=G.get_graph_editor_by_name(flow,'CloseRecordShopInteractionModals');insert(cleanup.find_graph_entry_pin(),call(cleanup,FLOW+'.BP_GameFlowManager_C.CloseResult'))
 # Consume completion once per customer; result starts only with a live customer.
 completed=fg.add_custom_event_node('HandleTurntableCompleted')
 p,_=valid(fg,get(fg,'ActiveCustomer'),completed.find_then_pin())
 p=branch(fg,p,get(fg,'DialogueStartedForCustomer'))
 p=branch(fg,p,eq(fg,get(fg,'CurrentState'),4))
 p=branch(fg,p,get(fg,'ResultStartedForCustomer'),False)
 p=chain(p,setv(fg,'ResultStartedForCustomer','true'))
 p=callself(fg,FLOW+'.BP_GameFlowManager_C.CloseRecordShopInteractionModals',p)
 p=state(fg,p,5)
 create=call(fg,'/Script/UMG.WidgetBlueprintLibrary.Create');val(pin(create,'WidgetType'),UI+'.WBP_Result_IntegrationFallback_C')
 pc=call(fg,'/Script/Engine.GameplayStatics.GetPlayerController');link(pin(pc,'ReturnValue',True),pin(create,'OwningPlayer'));p=chain(p,create)
 cast=action(fg,'CastToWBP_Result_IntegrationFallback',[pin(create,'ReturnValue',True)]);p=chain(p,cast)
 assign=setv(fg,'ResultWidgetRef');castout=next(x for x in cast.list_all_pins() if str(x.get_pin_name()).startswith('As'))
 link(castout,pin(assign,'ResultWidgetRef'));p=chain(p,assign)
 bind=action(fg,'BindEventtoOnContinue',[get(fg,'ResultWidgetRef')],ui.generated_class())
 finish_event=next(n for n in fg.list_all_nodes() if str(n.get_node_title())=='FinishResult');link(pin(finish_event,'OutputDelegate',True),pin(bind,'Delegate'));p=chain(p,bind)
 record=member(fg,get(fg,'TurntableRef'),'CurrentRecord',TT)
 br=action(fg,'BreakST_RecordData',[record]);title=next(x for x in br.list_all_pins() if str(x.get_pin_name()).startswith('Title_'));rid=next(x for x in br.list_all_pins() if str(x.get_pin_name()).startswith('RecordID_'))
 text=call(fg,'/Script/Engine.KismetTextLibrary.Conv_NameToText');link(rid,pin(text,'InName'))
 display=call(fg,UI+'.WBP_Result_IntegrationFallback_C.SetRecordDisplay');link(get(fg,'ResultWidgetRef'),pin(display,'self'));link(title,pin(display,'Title'));link(pin(text,'ReturnValue',True),pin(display,'RecordIdentifier'));p=chain(p,display)
 viewport=call(fg,'/Script/UMG.UserWidget.AddToViewport');link(get(fg,'ResultWidgetRef'),pin(viewport,'self'));val(pin(viewport,'ZOrder'),'20');p=chain(p,viewport)
 cursor=fg.add_set_member_variable_node('bShowMouseCursor','/Script/Engine.PlayerController');val(pin(cursor,'bShowMouseCursor'),'true');link(pin(pc,'ReturnValue',True),pin(cursor,'self'));p=chain(p,cursor)
 mode=call(fg,'/Script/UMG.WidgetBlueprintLibrary.SetInputMode_UIOnlyEx');link(pin(pc,'ReturnValue',True),pin(mode,'PlayerController'));link(get(fg,'ResultWidgetRef'),pin(mode,'InWidgetToFocus'));chain(p,mode)
 # FinishResult is only accepted for the current visible result and only once.
 down=finish_event.find_then_pin().list_connected_pins()[0];finish_event.find_then_pin().break_pin_links()
 p,_=valid(fg,get(fg,'ResultWidgetRef'),finish_event.find_then_pin())
 p=branch(fg,p,get(fg,'ResultSubmitted'),False);p=chain(p,setv(fg,'ResultSubmitted','true'))
 p=callself(fg,FLOW+'.BP_GameFlowManager_C.CloseResult',p);link(p,down)
 started=fg.add_custom_event_node('HandlePlaybackStarted')
 p,_=valid(fg,get(fg,'ActiveCustomer'),started.find_then_pin())
 p=branch(fg,p,eq(fg,get(fg,'CurrentState'),3));state(fg,p,4)
 # Bind before the existing startup sequence, using the map's authoritative actor.
 begin=named(fg,'K2Node_Event_0');down=begin.find_then_pin().list_connected_pins()[0];begin.find_then_pin().break_pin_links()
 p,bad=valid(fg,get(fg,'TurntableRef'),begin.find_then_pin());link(bad,down)
 for name,event in [('OnPlaybackStarted',started),('OnTurntableCompleted',completed)]:
  bind=action(fg,'BindEventto'+name,[get(fg,'TurntableRef')],cls(TT));link(pin(event,'OutputDelegate',True),pin(bind,'Delegate'));p=chain(p,bind)
 link(p,down)
 # Clear cycle guards on actual CustomerExited; no route replacement.
 exited=next(n for n in fg.list_all_nodes() if str(n.get_node_title())=='HandleCustomerExited')
 for name in ['ResultStartedForCustomer','ResultSubmitted']:insert(exited.find_then_pin(),setv(fg,name,'false'))
 # Result blocks shelf/turntable modal creation as dialogue already does.
 assets=[dm,tt,flow,ui]
 for path in [TT,SHELF]:
  bp=unreal.load_asset(path);eg=evgraph(bp);create=next(n for n in eg.list_all_nodes() if n.get_class().get_name()=='K2Node_CreateWidget')
  prev=create.find_execute_pin().list_connected_pins()[0];create.find_execute_pin().break_pin_links()
  find=call(eg,'/Script/UMG.WidgetBlueprintLibrary.GetAllWidgetsOfClass');val(pin(find,'WidgetClass'),UI+'.WBP_Result_IntegrationFallback_C');val(pin(find,'TopLevelOnly'),'true')
  empty=call(eg,'/Script/Engine.KismetArrayLibrary.Array_IsEmpty');link(pin(find,'FoundWidgets',True),pin(empty,'TargetArray'))
  p=chain(prev,find);p=branch(eg,p,pin(empty,'ReturnValue',True));link(p,create.find_execute_pin())
  if bp not in assets:assets.append(bp)
 for bp in assets:
  for graph in L.list_graphs(bp):layout(G.get_graph_editor(graph))
 R['compiles']={bp.get_path_name():L.compile_blueprint(bp) for bp in assets}
 assert all(R['compiles'].values()),R['compiles']
 for bp in assets:
  assert unreal.EditorAssetLibrary.save_loaded_asset(bp);R['saved'].append(bp.get_path_name())
 R['complete']=True
except Exception:R['fatal']=traceback.format_exc()
finally:
 (ROOT/'Saved/MVPCompletion/install.json').write_text(json.dumps(R,indent=2),encoding='utf-8')
 unreal.SystemLibrary.quit_editor()
