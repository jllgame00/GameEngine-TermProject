"""Install the minimal dialogue handoff using UE 5.8 Editor asset/graph APIs.
Run with Invoke-IntegrationPython.ps1 -Editor -AssetConstruction.
Then resave_dialogue_integration.py and validate_integration_round.py with normal diagnostics.
No authored dialogue is generated.
Preconditions deliberately reject a second application; all assets compile before saves.
"""
import json, traceback
from pathlib import Path
import unreal
import faulthandler
_trace=open(Path(unreal.Paths.project_dir(),"Saved/OvernightIntegration/Round1/worker-install-trace.txt"),"w")
faulthandler.dump_traceback_later(40,repeat=True,file=_trace)
L=unreal.BlueprintEditorLibrary
G=unreal.BlueprintGraphEditor
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager'
UI='/Game/RecordShop/UI/Dialogue/WBP_Dialogue'
DM='/Game/DialogueManager'
SHELF='/Game/RecordShop/Interaction/Actors/BP_RecordShelf'
TT='/Game/RecordShop/Interaction/Actors/BP_Turntable'
R={'complete':False,'saved':[]}

def pin(n,name,out=False):
 p=n.find_output_pin(name) if out else n.find_input_pin(name)
 assert p.is_valid(),str(n.get_node_title())+':'+name+' available='+str([str(x.get_pin_name()) for x in n.list_all_pins()])
 return p

def link(a,b):
 assert a.try_create_connection(b),str(a.get_pin_name())+' -> '+str(b.get_pin_name())

def val(p,s): assert p.set_pin_value(str(s)),str(s)
def call(g,path):
 n=g.add_call_function_node(path)
 assert n,path
 return n

def action(g,suffix,context=(),declaring=None):
 unreal.log('INSTALL_ACTION '+suffix)
 names=[str(n) for n in g.list_available_nodes(list(context)) if str(n).rsplit('|',1)[-1].endswith(suffix)]
 assert names, suffix
 for name in names:
  unreal.log('INSTALL_CREATE '+name)
  node=g.create_node_from_name(name,unreal.Vector2D(0,0),list(context),declaring)
  if node:return node
 raise RuntimeError('No matching action '+suffix)

def cls(path):return unreal.load_class(None,path+'.'+path.rsplit('/',1)[1]+'_C')
def get(g,name):return pin(g.add_get_member_variable_node(name),name,True)
def setv(g,name,value=None):
 n=g.add_set_member_variable_node(name)
 if value is not None:val(pin(n,name),value)
 return n

def function(bp,name):return G.create_and_edit_function_graph(bp,name)
def evgraph(bp):return G.get_graph_editor_by_name(bp,'EventGraph')
def valid(g,obj,previous):
 n=g.add_macro_node('/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:IsValid')
 assert n
 link(obj,pin(n,'InputObject'));link(previous,pin(n,'exec'))
 return pin(n,'Is Valid',True),pin(n,'Is Not Valid',True)

def signature_event(bp,name,params):
 assert L.add_event_dispatcher(bp,name+'Signature')
 for key,typ in params: assert L.add_event_dispatcher_parameter(bp,name+'Signature',key,typ)
 assert L.compile_blueprint(bp)
 node=evgraph(bp).add_dispatcher_event_node(name+'Signature')
 assert node
 assert L.remove_event_dispatcher(bp,name+'Signature')
 return node

def restore(g,previous):
 pc=call(g,'/Script/Engine.GameplayStatics.GetPlayerController')
 cursor=g.add_set_member_variable_node('bShowMouseCursor','/Script/Engine.PlayerController')
 val(pin(cursor,'bShowMouseCursor'),'false');link(pin(pc,'ReturnValue',True),pin(cursor,'self'))
 mode=call(g,'/Script/UMG.WidgetBlueprintLibrary.SetInputMode_GameOnly')
 val(pin(mode,'bFlushInput'),'true');link(pin(pc,'ReturnValue',True),pin(mode,'PlayerController'))
 focus=call(g,'/Script/UMG.WidgetBlueprintLibrary.SetFocusToGameViewport')
 link(previous,cursor.find_execute_pin());link(cursor.find_then_pin(),mode.find_execute_pin());link(mode.find_then_pin(),focus.find_execute_pin())
 return focus.find_then_pin()

def layout(g):
 for i,n in enumerate(g.list_all_nodes()):n.set_node_pos(unreal.IntPoint((i%6)*360,(i//6)*310))

try:
 assert not unreal.EditorAssetLibrary.does_asset_exist(UI),'Dialogue UI already exists; inspect before reapplying'
 flow=unreal.load_asset(FLOW);dm=unreal.load_asset(DM)
 assert not L.find_graph(flow,'CloseDialogue'),'Handoff already installed'
 assert L.compile_blueprint(dm)
 settings=unreal.get_default_object(unreal.load_class(None,'/Script/UMGEditor.UMGEditorProjectSettings'))
 old_root=settings.get_editor_property('DefaultRootWidget');old_select=settings.get_editor_property('bUseWidgetTemplateSelector')
 try:
  settings.set_editor_property('bUseWidgetTemplateSelector',False)
  settings.set_editor_property('DefaultRootWidget',unreal.CanvasPanel)
  ui=unreal.AssetToolsHelpers.get_asset_tools().create_asset('WBP_Dialogue','/Game/RecordShop/UI/Dialogue',unreal.WidgetBlueprint,unreal.WidgetBlueprintFactory())
 finally:
  settings.set_editor_property('DefaultRootWidget',old_root);settings.set_editor_property('bUseWidgetTemplateSelector',old_select)
 assert ui
 tree=unreal.find_object(ui,'WidgetTree');root=unreal.find_object(tree,'CanvasPanel_0');assert root
 border=unreal.new_object(unreal.Border,outer=tree,name='DialoguePanel')
 border.set_brush_color(unreal.LinearColor(0.025,0.025,0.035,0.96));border.set_padding(unreal.Margin(24,18,24,18))
 slot=root.add_child_to_canvas(border);slot.set_anchors(unreal.Anchors(unreal.Vector2D(.1,.68),unreal.Vector2D(.9,.95)));slot.set_offsets(unreal.Margin(0,0,0,0))
 box=unreal.new_object(unreal.VerticalBox,outer=tree,name='DialogueLayout');border.add_child(box)
 for name,size in [('Speaker',22),('DialogueText',26)]:
  text=unreal.new_object(unreal.RichTextBlock,outer=tree,name=name)
  font=unreal.SlateFontInfo();font.set_editor_property('font_object',unreal.load_asset('/Engine/EngineFonts/Roboto'));font.set_editor_property('typeface_font_name','Regular');font.set_editor_property('size',size)
  style=unreal.TextBlockStyle();style.set_editor_property('font',font);style.set_editor_property('color_and_opacity',unreal.SlateColor(specified_color=unreal.LinearColor(1,1,1,1)))
  text.set_default_text_style(style);text.set_auto_wrap_text(True)
  box.add_child_to_vertical_box(text).set_padding(unreal.Margin(0,0,0,12))
 button=unreal.new_object(unreal.Button,outer=tree,name='Next')
 label=unreal.new_object(unreal.TextBlock,outer=tree,name='NextLabel');label.set_text('Next');button.add_child(label)
 box.add_child_to_vertical_box(button).set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_RIGHT)
 assert L.compile_blueprint(ui)
 unreal.get_default_object(ui.generated_class()).set_editor_property('is_focusable',True)
 ug=evgraph(ui);assert ug.add_member_variable('DialogueManagerRef',L.get_object_reference_type(cls(DM)))
 assert L.compile_blueprint(ui)
 # Update only the authored speaker/text; no default narrative.
 update=function(ui,'UpdateDialogue')
 speaker=update.add_graph_input_parameter('SpeakerText',L.get_basic_type_by_name('text'))
 text=update.add_graph_input_parameter('LineText',L.get_basic_type_by_name('text'))
 previous=update.find_graph_entry_pin()
 for member,value in [('Speaker',speaker),('DialogueText',text)]:
  n=call(update,'/Script/UMG.RichTextBlock.SetText');link(get(update,member),pin(n,'self'));link(value,pin(n,'InText'));link(previous,n.find_execute_pin());previous=n.find_then_pin()
 layout(update)
 # Initialize once; OnClicked routes through the existing manager.
 init=action(ug,'OnInitialized')
 clicked=ug.add_custom_event_node('AdvanceDialogue')
 bind=action(ug,'BindEventtoOnClicked',[get(ug,'Next')],unreal.Button)
 link(pin(clicked,'OutputDelegate',True),pin(bind,'Delegate'));link(init.find_then_pin(),bind.find_execute_pin())
 good,_=valid(ug,get(ug,'DialogueManagerRef'),clicked.find_then_pin())
 nextline=call(ug,DM+'.DialogueManager_C.ShowNextLine');link(get(ug,'DialogueManagerRef'),pin(nextline,'self'));link(good,nextline.find_execute_pin())
 layout(ug);assert L.compile_blueprint(ui)
 # Flow owns one manager component and one dialogue widget.
 fg=evgraph(flow)
 existing_nodes={n.get_name() for n in fg.list_all_nodes()}
 for name,typ in [('DialogueManagerRef',L.get_object_reference_type(cls(DM))),('DialogueWidgetRef',L.get_object_reference_type(ui.generated_class())),('DialogueStartedForCustomer',L.get_basic_type_by_name('bool'))]:
  assert fg.add_member_variable(name,typ)
 assert L.compile_blueprint(flow)
 close=function(flow,'CloseDialogue')
 good,bad=valid(close,get(close,'DialogueWidgetRef'),close.find_graph_entry_pin())
 remove=call(close,'/Script/UMG.Widget.RemoveFromParent');link(get(close,'DialogueWidgetRef'),pin(remove,'self'));link(good,remove.find_execute_pin())
 clear_manager=close.add_set_member_variable_node('DialogueManagerRef',UI+'.WBP_Dialogue_C');link(get(close,'DialogueWidgetRef'),pin(clear_manager,'self'));link(remove.find_then_pin(),clear_manager.find_execute_pin())
 clear=setv(close,'DialogueWidgetRef');link(clear_manager.find_then_pin(),clear.find_execute_pin())
 previous=restore(close,clear.find_then_pin())
 state=call(close,FLOW+'.BP_GameFlowManager_C.SetGameFlowState');val(pin(state,'NewState'),'NewEnumerator0');link(previous,state.find_execute_pin())
 layout(close);assert L.compile_blueprint(flow)
 # Preserve dispatcher parameter types directly from the authoritative manager.
 dmgraph=evgraph(dm)
 broadcast=next(n for n in dmgraph.list_all_nodes() if n.get_class().get_name()=='K2Node_CallDelegate' and n.find_input_pin('Speaker').is_valid())
 updated=signature_event(flow,'HandleDialogueUpdate',[(name,pin(broadcast,name).get_pin_type()) for name in ['Speaker','DialogueText']])
 finished=fg.add_custom_event_node('HandleDialogueFinished')
 good,_=valid(fg,get(fg,'DialogueWidgetRef'),updated.find_then_pin())
 updatecall=call(fg,UI+'.WBP_Dialogue_C.UpdateDialogue');link(get(fg,'DialogueWidgetRef'),pin(updatecall,'self'));link(pin(updated,'Speaker',True),pin(updatecall,'SpeakerText'));link(pin(updated,'DialogueText',True),pin(updatecall,'LineText'));link(good,updatecall.find_execute_pin())
 closecall=call(fg,FLOW+'.BP_GameFlowManager_C.CloseDialogue');link(finished.find_then_pin(),closecall.find_execute_pin())
 # Ready guard remains true through the customer cycle, including after UI closes.
 ready=next(n for n in fg.list_all_nodes() if str(n.get_node_title())=='HandleCustomerReadyForDialogue')
 ready.find_then_pin().break_pin_links()
 good,_=valid(fg,get(fg,'ActiveCustomer'),ready.find_then_pin())
 guard=fg.add_branch_node();link(get(fg,'DialogueStartedForCustomer'),pin(guard,'Condition'));link(good,guard.find_execute_pin())
 mark=setv(fg,'DialogueStartedForCustomer','true');link(pin(guard,'else',True),mark.find_execute_pin())
 closeothers=call(fg,FLOW+'.BP_GameFlowManager_C.CloseRecordShopInteractionModals');link(mark.find_then_pin(),closeothers.find_execute_pin())
 good,bad=valid(fg,get(fg,'DialogueManagerRef'),closeothers.find_then_pin())
 add=call(fg,'/Script/Engine.Actor.AddComponentByClass');val(pin(add,'Class'),DM+'.DialogueManager_C');link(bad,add.find_execute_pin())
 transform=call(fg,'/Script/Engine.KismetMathLibrary.MakeTransform');val(pin(transform,'Scale'),'1.000000,1.000000,1.000000');link(pin(transform,'ReturnValue',True),pin(add,'RelativeTransform'))
 cast=action(fg,'CastToDialogueManager',[pin(add,'ReturnValue',True)]);link(add.find_then_pin(),cast.find_execute_pin())
 manager=setv(fg,'DialogueManagerRef');link(pin(cast,'AsDialogue Manager',True),pin(manager,'DialogueManagerRef'));link(cast.find_then_pin(),manager.find_execute_pin())
 previous=manager.find_then_pin()
 for name,event in [('OnUpdateDialogueUI',updated),('OnDialogueFinished',finished)]:
  n=action(fg,'BindEventto'+name,[get(fg,'DialogueManagerRef')],cls(DM));link(pin(event,'OutputDelegate',True),pin(n,'Delegate'));link(previous,n.find_execute_pin());previous=n.find_then_pin()
 # Both reused/new manager paths create the widget before StartDialogue broadcasts.
 create=call(fg,'/Script/UMG.WidgetBlueprintLibrary.Create');val(pin(create,'WidgetType'),UI+'.WBP_Dialogue_C')
 pc=call(fg,'/Script/Engine.GameplayStatics.GetPlayerController');link(pin(pc,'ReturnValue',True),pin(create,'OwningPlayer'));link(good,create.find_execute_pin());link(previous,create.find_execute_pin())
 castui=action(fg,'CastToWBP_Dialogue',[pin(create,'ReturnValue',True)]);link(create.find_then_pin(),castui.find_execute_pin())
 widget=setv(fg,'DialogueWidgetRef');link(pin(castui,'AsWBP Dialogue',True),pin(widget,'DialogueWidgetRef'));link(castui.find_then_pin(),widget.find_execute_pin())
 setmanager=fg.add_set_member_variable_node('DialogueManagerRef',UI+'.WBP_Dialogue_C');link(get(fg,'DialogueWidgetRef'),pin(setmanager,'self'));link(get(fg,'DialogueManagerRef'),pin(setmanager,'DialogueManagerRef'));link(widget.find_then_pin(),setmanager.find_execute_pin())
 viewport=call(fg,'/Script/UMG.UserWidget.AddToViewport');link(get(fg,'DialogueWidgetRef'),pin(viewport,'self'));link(setmanager.find_then_pin(),viewport.find_execute_pin());val(pin(viewport,'ZOrder'),'20')
 cursor=fg.add_set_member_variable_node('bShowMouseCursor','/Script/Engine.PlayerController');val(pin(cursor,'bShowMouseCursor'),'true');link(pin(pc,'ReturnValue',True),pin(cursor,'self'));link(viewport.find_then_pin(),cursor.find_execute_pin())
 mode=call(fg,'/Script/UMG.WidgetBlueprintLibrary.SetInputMode_UIOnlyEx');link(pin(pc,'ReturnValue',True),pin(mode,'PlayerController'));link(get(fg,'DialogueWidgetRef'),pin(mode,'InWidgetToFocus'));link(cursor.find_then_pin(),mode.find_execute_pin())
 state=call(fg,FLOW+'.BP_GameFlowManager_C.SetGameFlowState');val(pin(state,'NewState'),'NewEnumerator1');link(mode.find_then_pin(),state.find_execute_pin())
 start=call(fg,DM+'.DialogueManager_C.StartDialogue');link(get(fg,'DialogueManagerRef'),pin(start,'self'));link(state.find_then_pin(),start.find_execute_pin())
 # Existing customer exit cleanup also closes dialogue and clears the cycle guard.
 cleanup=G.get_graph_editor_by_name(flow,'CloseRecordShopInteractionModals')
 entry=cleanup.find_graph_entry_pin();down=entry.list_connected_pins()[0];entry.break_pin_links()
 c=call(cleanup,FLOW+'.BP_GameFlowManager_C.CloseDialogue');link(entry,c.find_execute_pin());link(c.find_then_pin(),down)
 exited=next(n for n in fg.list_all_nodes() if str(n.get_node_title())=='HandleCustomerExited')
 down=exited.find_then_pin().list_connected_pins()[0];exited.find_then_pin().break_pin_links()
 reset=setv(fg,'DialogueStartedForCustomer','false');link(exited.find_then_pin(),reset.find_execute_pin());link(reset.find_then_pin(),down)
 # A live dialogue blocks both existing interaction modals.
 assets=[ui,flow]
 for path in [SHELF,TT]:
  bp=unreal.load_asset(path);eg=evgraph(bp)
  create=next(n for n in eg.list_all_nodes() if n.get_class().get_name()=='K2Node_CreateWidget')
  previous=create.find_execute_pin().list_connected_pins()[0];create.find_execute_pin().break_pin_links()
  find=call(eg,'/Script/UMG.WidgetBlueprintLibrary.GetAllWidgetsOfClass');val(pin(find,'WidgetClass'),UI+'.WBP_Dialogue_C');val(pin(find,'TopLevelOnly'),'true')
  empty=call(eg,'/Script/Engine.KismetArrayLibrary.Array_IsEmpty');link(pin(find,'FoundWidgets',True),pin(empty,'TargetArray'))
  branch=eg.add_branch_node();link(pin(empty,'ReturnValue',True),pin(branch,'Condition'));link(previous,find.find_execute_pin());link(find.find_then_pin(),branch.find_execute_pin());link(branch.find_then_pin(),create.find_execute_pin())
  eg.add_comment_to_nodes('Dialogue owns input until its existing Next/Finished path closes it.',[find,empty,branch],50)
  assets.append(bp)
 new_nodes=[n for n in fg.list_all_nodes() if n.get_name() not in existing_nodes]
 for i,n in enumerate(new_nodes):n.set_node_pos(unreal.IntPoint((i%7)*400,2600+(i//7)*350))
 R['compiles']={bp.get_path_name():L.compile_blueprint(bp) for bp in assets+[dm]}
 assert all(R['compiles'].values()),R['compiles']
 for bp in assets:
  assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
  R['saved'].append(bp.get_path_name())
 R['complete']=True
except Exception:R['error']=traceback.format_exc()
finally:
 Path(unreal.Paths.project_dir(),'Saved/OvernightIntegration/Round1/worker-dialogue-install.json').write_text(json.dumps(R,indent=2),encoding='utf-8')
 faulthandler.cancel_dump_traceback_later()
 unreal.SystemLibrary.quit_editor()
