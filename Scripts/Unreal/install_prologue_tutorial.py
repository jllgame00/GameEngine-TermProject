"""Install the opening guidance layer with supported UE 5.8 Editor graph APIs.

No raw asset editing. Reuses existing Result UMG styling, removes Result-specific
functions, and retains only its generic button binding. Run using run_mvp_validation.
"""
import json, os, sys, traceback
from pathlib import Path
import unreal
ROOT = Path(unreal.Paths.project_dir())
sys.path.insert(0, str(ROOT / 'Scripts/Unreal'))
from mvp_graph_helpers import *
# Stabilize editor action keys for this process only; never save culture settings.
unreal.InternationalizationLibrary.set_current_language("en", False)
FLOW = '/Game/RecordShop/Core/Flow/BP_GameFlowManager'
UI = '/Game/RecordShop/UI/Prologue/WBP_Prologue'
RU = '/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
R = {'complete': False, 'pass': False, 'saved': []}
OUT = Path(os.environ['MVP_RESULT'])

def report(): OUT.write_text(json.dumps(R, indent=2, ensure_ascii=False), encoding='utf-8')
def save(bp):
    assert L.compile_blueprint(bp), bp.get_path_name()
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    R['saved'].append(bp.get_path_name()); report()
def node(g, name): return next(n for n in g.list_all_nodes() if n.get_name() == name)
def var(bp, name, typ):
    if name not in list(map(str, L.list_member_variable_names(bp, False))):
        assert L.add_member_variable(bp, name, typ)
def fn(bp, name):
    if name in [x.get_name() for x in L.list_graphs(bp)]:
        g = G.get_graph_editor_by_name(bp, name)
        g.remove_nodes([n for n in g.list_all_nodes() if n.get_class().get_name() not in ('K2Node_FunctionEntry', 'K2Node_FunctionResult')])
        return g
    return function(bp, name)
def param(g, name, typ):
    entry = g.find_graph_entry_pin().get_owning_node()
    p = entry.find_output_pin(name)
    return p if p.is_valid() else g.add_graph_input_parameter(name, typ)
def step(g, previous, path, **args):
    n = call(g, path)
    for key, value in args.items():
        if hasattr(value, 'is_valid'): link(value, pin(n, key))
        else: val(pin(n, key), value)
    link(previous, n.find_execute_pin())
    return n.find_then_pin(), n

def math(g, name, **args):
    n = call(g, '/Script/Engine.' + ('KismetStringLibrary.' if 'StrStr' in name else 'KismetMathLibrary.') + name)
    for key, value in args.items():
        if hasattr(value, 'is_valid'): link(value, pin(n, key))
        else: val(pin(n, key), value)
    return pin(n, 'ReturnValue', True)
def assign(g, previous, name, value):
    n = setv(g, name)
    if hasattr(value, 'is_valid'): link(value, pin(n, name))
    else: val(pin(n, name), value)
    link(previous, n.find_execute_pin()); return n.find_then_pin()
def branch(g, previous, condition):
    n = g.add_branch_node(); link(previous, n.find_execute_pin()); link(condition, pin(n, 'Condition'))
    return pin(n, 'then', True), pin(n, 'else', True)
def prop(g, name, target, declaring):
    n = g.add_get_member_variable_node(name, declaring); link(target, pin(n, 'self')); return pin(n, name, True)
def invoke(g, previous, name, **args): return step(g, previous, FLOW + '.BP_GameFlowManager_C:' + name, **args)[0]
def ui_call(g, previous, ref, name, **args): return step(g, previous, UI + '.WBP_Prologue_C:' + name, self=ref, **args)[0]
def presentation(g, previous, ref, title, body, label='계속'):
    return ui_call(g, previous, ref, 'SetPresentation', Title=title, Body=body, Action=label)
def visibility(g, previous, target, value):
    return step(g, previous, '/Script/UMG.Widget.SetVisibility', self=target, InVisibility=value)[0]
def self_node(g):
    normalize=lambda text: ''.join(c for c in text.lower() if c.isalnum())
    available=list(map(str,g.list_available_nodes([])))
    candidates=[n for n in available if normalize(n.rsplit('|',1)[-1]) in ('self','selfreference','getareferencetoself')]
    assert candidates, 'No Self menu action'
    n=g.create_node_from_name(candidates[0],unreal.Vector2D(0,0),[])
    assert n
    return n

def timer(g, previous, name, seconds, loop=False):
    n = call(g, '/Script/Engine.KismetSystemLibrary.K2_SetTimer')
    link(pin(self_node(g), 'self', True), pin(n, 'Object'))
    val(pin(n, 'FunctionName'), name); val(pin(n, 'Time'), seconds); val(pin(n, 'bLooping'), str(loop).lower())
    link(previous, n.find_execute_pin()); return n.find_then_pin()
def splice(previous, n):
    after = list(previous.list_connected_pins()); previous.break_pin_links(); link(previous, n.find_execute_pin())
    for p in after: link(n.find_then_pin(), p)
def create_ui(g, previous, member):
    # K2 CreateWidget specializes its return pin when Class is assigned.
    n = action(g, 'Create Widget'); val(pin(n, 'Class'), UI + '.WBP_Prologue_C')
    pc = call(g, '/Script/Engine.GameplayStatics.GetPlayerController')
    link(pin(pc, 'ReturnValue', True), pin(n, 'OwningPlayer')); link(previous, n.find_execute_pin())
    end = assign(g, n.find_then_pin(), member, pin(n, 'ReturnValue', True))
    ref = get(g, member)
    end, _ = step(g, end, '/Script/UMG.UserWidget.AddToViewport', self=ref, ZOrder=20)
    return end, ref

def install_opening_gate(path):
    unreal.log('OPENING_GATE load '+path)
    asset=unreal.load_asset(path);g=evgraph(asset)
    unreal.log('OPENING_GATE inspect '+path)
    if any(str(n.get_node_title()).replace(' ','')=='GetPrologueStage' for n in g.list_all_nodes()):
        return
    unreal.log('OPENING_GATE event '+path)
    event=g.find_event_node('Interact');assert event, path
    before=event.find_then_pin();after=list(before.list_connected_pins());assert after
    before.break_pin_links()
    unreal.log('OPENING_GATE manager '+path)
    manager=call(g,'/Script/Engine.GameplayStatics.GetActorOfClass')
    val(pin(manager,'ActorClass'),FLOW+'.BP_GameFlowManager_C')
    target=pin(manager,'ReturnValue',True)
    link(before,manager.find_execute_pin())
    yes,missing=valid(g,target,manager.find_then_pin())
    unreal.log('OPENING_GATE stage '+path)
    stage=prop(g,'PrologueStage',target,FLOW+'.BP_GameFlowManager_C')
    allowed,blocked=branch(g,yes,math(g,'GreaterEqual_IntInt',A=stage,B=4))
    for dest in after:link(allowed,dest);link(missing,dest)
    unreal.log('OPENING_GATE save '+path)
    save(asset)

try:
    bp = unreal.load_asset(FLOW)
    assert 'PrologueInstalled' not in list(map(str, L.list_member_variable_names(bp, False))) or not unreal.get_default_object(bp.generated_class()).get_editor_property('PrologueInstalled'), 'Already installed; do not rerun on a completed installation'
    for name, typ in [('PrologueStage', 'int'), ('TutorialComplete', 'bool'), ('TutorialResultSubmitted', 'bool'), ('LastTutorialHint', 'string')]:
        var(bp, name, L.get_basic_type_by_name(typ))
    names = ('BeginPrologue', 'AdvancePrologue', 'StartTutorialCustomer', 'UpdateTutorialHint', 'SetTutorialHint', 'CompleteTutorial', 'DismissTutorialHint', 'FocusPrologue')
    for name in names:
        if name not in [x.get_name() for x in L.list_graphs(bp)]: function(bp, name)
    assert L.compile_blueprint(bp)

    # Visual reuse only: remove the copied Result-specific graph implementations.
    ui = unreal.load_asset(UI)
    if not ui:
        ui = unreal.EditorAssetLibrary.duplicate_asset(RU, UI)
    assert ui
    for name in ('SetRecordDisplay', 'SetRawScoreDisplay'):
        L.remove_function_graph(ui, name)
    ug = evgraph(ui)
    callback = node(ug, 'K2Node_CustomEvent_0')
    callback.find_then_pin().break_pin_links()
    ug.remove_nodes([n for n in ug.list_all_nodes() if n.get_class().get_name() == 'K2Node_CallDelegate'])
    advance = call(ug, FLOW + '.BP_GameFlowManager_C:AdvancePrologue')
    link(get(ug, 'FlowRef'), pin(advance, 'self')); link(callback.find_then_pin(), advance.find_execute_pin())
    # The generic OnInitialized Continue-button binding remains; no Result behavior.
    L.remove_event_dispatcher(ui, 'OnContinue')
    ug.remove_nodes([n for n in ug.list_all_nodes() if n.get_class().get_name() == 'K2Node_ClearDelegate'])
    tree = next(t for t in unreal.ObjectIterator(unreal.WidgetTree) if t.get_outer() == ui)
    widgets = {w.get_name(): w for w in unreal.ObjectIterator(unreal.Widget) if w.get_outer() == tree}
    widgets['Heading'].set_visibility(unreal.SlateVisibility.COLLAPSED)
    widgets['RecordTitle'].set_text('레코드숍')
    widgets['ScoreStatus'].set_visibility(unreal.SlateVisibility.VISIBLE)
    widgets['ScoreStatus'].set_text('가게의 첫날을 시작합니다.')
    widgets['ScoreStatus'].set_default_font(unreal.SlateFontInfo(font_object=unreal.load_asset('/Game/RecordShop/UI/Fonts/NanumGothic_Font'), typeface_font_name='Default', size=22))
    widgets['RecordID'].remove_from_parent()
    widgets['RecordID'].set_visibility(unreal.SlateVisibility.VISIBLE)
    widgets['RecordID'].set_auto_wrap_text(False)
    widgets['RecordID'].set_default_font(unreal.SlateFontInfo(font_object=unreal.load_asset('/Game/RecordShop/UI/Fonts/NanumGothic_Font'),typeface_font_name='Default',size=22))
    widgets['RecordID'].set_text('새 게임')
    widgets['Continue'].set_content(widgets['RecordID'])
    widgets['ResultPanel'].slot.set_anchors(unreal.Anchors(unreal.Vector2D(.14,.22), unreal.Vector2D(.86,.78)))
    assert L.compile_blueprint(ui)
    g = fn(ui, 'SetPresentation')
    title = param(g, 'Title', L.get_basic_type_by_name('text')); body = param(g, 'Body', L.get_basic_type_by_name('text')); label = param(g, 'Action', L.get_basic_type_by_name('text'))
    end = g.find_graph_entry_pin()
    for member, value in [('RecordTitle', title), ('ScoreStatus', body), ('RecordID', label)]:
        end, _ = step(g, end, '/Script/UMG.RichTextBlock.SetText', self=get(g, member), InText=value)
    g = fn(ui, 'ConfigureHint'); end = visibility(g, g.find_graph_entry_pin(), get(g, 'Continue'), 'Collapsed')
    end = visibility(g, end, pin(self_node(g), 'self', True), 'HitTestInvisible')
    layout_parent = call(g, '/Script/UMG.Widget.GetParent'); link(get(g, 'RecordTitle'), pin(layout_parent, 'self'))
    panel_parent = call(g, '/Script/UMG.Widget.GetParent'); link(pin(layout_parent,'ReturnValue',True),pin(panel_parent,'self'))
    slot = call(g, '/Script/UMG.WidgetLayoutLibrary.SlotAsCanvasSlot'); link(pin(panel_parent,'ReturnValue',True), pin(slot, 'Widget'))
    end, _ = step(g, end, '/Script/UMG.CanvasPanelSlot.SetAnchors', self=pin(slot, 'ReturnValue', True), InAnchors='(Minimum=(X=0.03,Y=0.03),Maximum=(X=0.70,Y=0.25))')
    save(ui)

    for name in ('PrologueWidgetRef', 'TutorialHintRef'): var(bp, name, L.get_object_reference_type(ui.generated_class()))
    if 'OnTutorialCompleted' not in [g.get_name() for g in L.list_graphs(bp)]:
        assert L.add_event_dispatcher(bp, 'OnTutorialCompleted')
    assert L.compile_blueprint(bp)
    g = fn(bp, 'BeginPrologue')
    entry, ignored = branch(g, g.find_graph_entry_pin(), math(g, 'EqualEqual_IntInt', A=get(g,'PrologueStage'), B=0))
    yes, no = valid(g, get(g, 'PrologueWidgetRef'), entry)
    end, ref = create_ui(g, no, 'PrologueWidgetRef')
    setref = g.add_set_member_variable_node('FlowRef', UI + '.WBP_Prologue_C')
    link(ref, pin(setref, 'self')); link(pin(self_node(g), 'self', True), pin(setref, 'FlowRef')); link(end, setref.find_execute_pin()); end = setref.find_then_pin()
    pc = call(g, '/Script/Engine.GameplayStatics.GetPlayerController'); cursor = g.add_set_member_variable_node('bShowMouseCursor', '/Script/Engine.PlayerController')
    link(pin(pc, 'ReturnValue', True), pin(cursor, 'self')); val(pin(cursor, 'bShowMouseCursor'), 'true'); link(end, cursor.find_execute_pin())
    button = prop(g, 'Continue', ref, UI + '.WBP_Prologue_C')
    end,_=step(g, cursor.find_then_pin(), '/Script/UMG.WidgetBlueprintLibrary.SetInputMode_UIOnlyEx', PlayerController=pin(pc,'ReturnValue',True), InWidgetToFocus=button, bFlushInput='true')
    # PIE/immersive viewport initialization can claim focus after actor BeginPlay.
    # One deferred application belongs only to the still-active opening modal.
    timer(g,end,'FocusPrologue',.1)

    g=fn(bp,'FocusPrologue');end,no=valid(g,get(g,'PrologueWidgetRef'),g.find_graph_entry_pin())
    end,no=branch(g,end,math(g,'Less_IntInt',A=get(g,'PrologueStage'),B=3))
    pc=call(g,'/Script/Engine.GameplayStatics.GetPlayerController')
    end,no=valid(g,pin(pc,'ReturnValue',True),end)
    button=prop(g,'Continue',get(g,'PrologueWidgetRef'),UI+'.WBP_Prologue_C')
    step(g,end,'/Script/UMG.Widget.SetUserFocus',self=button,PlayerController=pin(pc,'ReturnValue',True))

    g = fn(bp, 'AdvancePrologue'); end = g.find_graph_entry_pin()
    for stage, title, body, label in [
        (0, '첫날', '이곳은 부모님이 운영하시는 작은 레코드숍이다.\n부모님은 일주일 동안 가게를 비우신다.\n그동안 내가 7일간 가게를 맡게 되었다.', '메모 읽기'),
        (1, '부모님의 메모', '아직 가게 일이 익숙하지 않겠지만,\n손님의 이야기를 듣고 어울리는 음악을 골라주면 된단다.\n오늘이 첫날이야.', '가게 둘러보기')]:
        yes, end = branch(g, end, math(g, 'EqualEqual_IntInt', A=get(g,'PrologueStage'), B=stage))
        yes = assign(g, yes, 'PrologueStage', stage+1)
        presentation(g, yes, get(g,'PrologueWidgetRef'), title, body, label)
    yes, no = branch(g, end, math(g,'EqualEqual_IntInt', A=get(g,'PrologueStage'), B=2))
    end = assign(g, yes, 'PrologueStage', 3)
    end, _ = step(g, end, '/Script/UMG.Widget.RemoveFromParent', self=get(g,'PrologueWidgetRef'))
    end = assign(g, end, 'PrologueWidgetRef', 'None'); end = restore(g, end)
    end, ref = create_ui(g, end, 'TutorialHintRef'); end = ui_call(g, end, ref, 'ConfigureHint')
    end = invoke(g, end, 'UpdateTutorialHint'); end = timer(g, end, 'UpdateTutorialHint', .25, True)
    timer(g, end, 'StartTutorialCustomer', 8)

    # Set hint content only when it changes, avoiding persistent Slate invalidation.
    g = fn(bp,'SetTutorialHint'); text = param(g,'Message',L.get_basic_type_by_name('string'))
    end, no = branch(g,g.find_graph_entry_pin(),math(g,'NotEqual_StrStr', A=get(g,'LastTutorialHint'), B=text))
    end = assign(g,end,'LastTutorialHint',text)
    end, no = valid(g,get(g,'TutorialHintRef'),end)
    hide, show = branch(g,end,math(g,'EqualEqual_StrStr',A=text,B=''))
    visibility(g,hide,get(g,'TutorialHintRef'),'Collapsed')
    end = visibility(g,show,get(g,'TutorialHintRef'),'HitTestInvisible')
    conv = call(g,'/Script/Engine.KismetTextLibrary.Conv_StringToText');link(text,pin(conv,'InString'))
    presentation(g,end,get(g,'TutorialHintRef'),'첫날 안내',pin(conv,'ReturnValue',True),'')

    assert L.compile_blueprint(bp)
    g = fn(bp,'UpdateTutorialHint'); end,missing=valid(g,get(g,'TutorialHintRef'),g.find_graph_entry_pin())
    yes, end = branch(g,end,math(g,'EqualEqual_IntInt',A=get(g,'PrologueStage'),B=3))
    invoke(g,yes,'SetTutorialHint',Message='이동 키로 가게를 둘러보세요.\n곧 첫 손님이 찾아옵니다.')
    # Existing UIs already describe dialogue, selection and every turntable action.
    for path in ('Dialogue/WBP_Dialogue','RecordSelection/WBP_RecordSelect','Turntable/WBP_Turntable','Result/WBP_Result_IntegrationFallback'):
        end, found = step(g,end,'/Script/UMG.WidgetBlueprintLibrary.GetAllWidgetsOfClass',WidgetClass='/Game/RecordShop/UI/'+path+'.'+path.rsplit('/',1)[1]+'_C',TopLevelOnly='true')
        empty = call(g,'/Script/Engine.KismetArrayLibrary.Array_IsEmpty');link(pin(found,'FoundWidgets',True),pin(empty,'TargetArray'))
        end, hide = branch(g,end,pin(empty,'ReturnValue',True));invoke(g,hide,'SetTutorialHint',Message='')
    yes, end = branch(g,end,get(g,'TutorialComplete'))
    invoke(g,yes,'SetTutorialHint',Message='튜토리얼 완료\n첫 손님을 무사히 배웅했다. 가게를 자유롭게 둘러보자.')
    for state, message in [(2,'LP 진열장 앞에서 E를 눌러\n손님에게 어울리는 음반을 골라주세요.'),(3,'턴테이블 앞에서 E를 누르세요.\n화면의 순서대로 음반을 재생해 보세요.')]:
        eq=call(g,'/Script/Engine.KismetMathLibrary.EqualEqual_ByteByte');link(get(g,'CurrentState'),pin(eq,'A'));val(pin(eq,'B'),state)
        yes,end=branch(g,end,pin(eq,'ReturnValue',True));invoke(g,yes,'SetTutorialHint',Message=message)
    entering=call(g,'/Script/Engine.KismetMathLibrary.EqualEqual_ByteByte');link(get(g,'CurrentState'),pin(entering,'A'));val(pin(entering,'B'),0)
    entry,quiet=branch(g,end,pin(entering,'ReturnValue',True))
    invoke(g,entry,'SetTutorialHint',Message='첫 손님이 들어오고 있습니다.\n손님의 이야기를 들어보세요.')
    invoke(g,quiet,'SetTutorialHint',Message='')

    g = fn(bp,'StartTutorialCustomer'); yes,no=branch(g,g.find_graph_entry_pin(),math(g,'EqualEqual_IntInt',A=get(g,'PrologueStage'),B=3))
    end=assign(g,yes,'PrologueStage',4)
    # Original spawn chain will be called once from this guarded event.
    eg=evgraph(bp)
    event=next((n for n in eg.list_all_nodes() if n.get_class().get_name()=='K2Node_CustomEvent' and str(n.get_node_title()).replace(' ','')=='SpawnTutorialCustomer'),None)
    if event is None:event=eg.add_custom_event_node('SpawnTutorialCustomer')
    assert L.compile_blueprint(bp)
    end=invoke(g,end,'SpawnTutorialCustomer')
    seq=node(eg,'K2Node_ExecutionSequence_0');spawn=node(eg,'K2Node_SpawnActorFromClass_0')
    pin(seq,'then_1',True).break_pin_links();link(event.find_then_pin(),spawn.find_execute_pin())
    begin=call(eg,FLOW+'.BP_GameFlowManager_C:BeginPrologue');link(pin(seq,'then_1',True),begin.find_execute_pin())

    g=fn(bp,'CompleteTutorial');active,end=valid(g,get(g,'ActiveCustomer'),g.find_graph_entry_pin())
    end,no=branch(g,end,math(g,'EqualEqual_IntInt',A=get(g,'PrologueStage'),B=4))
    end,no=branch(g,end,get(g,'TutorialResultSubmitted'))
    yes,end=branch(g,end,get(g,'TutorialComplete'))
    end=assign(g,end,'TutorialComplete','true');end=assign(g,end,'PrologueStage',5)
    end=invoke(g,end,'UpdateTutorialHint')
    end=timer(g,end,'DismissTutorialHint',6)
    dispatch=action(g,'Call On Tutorial Completed');link(end,dispatch.find_execute_pin())
    g=fn(bp,'DismissTutorialHint');end=g.find_graph_entry_pin()
    end,_=step(g,end,'/Script/Engine.KismetSystemLibrary.K2_ClearTimer',Object=pin(self_node(g),'self',True),FunctionName='UpdateTutorialHint')
    end,no=valid(g,get(g,'TutorialHintRef'),end)
    end,_=step(g,end,'/Script/UMG.Widget.RemoveFromParent',self=get(g,'TutorialHintRef'))
    assign(g,end,'TutorialHintRef','None')
    # Completion is only reachable after the existing accepted Result -> exit route.
    flag=setv(eg,'TutorialResultSubmitted','true');splice(node(eg,'K2Node_VariableSet_11').find_then_pin(),flag)
    complete=call(eg,FLOW+'.BP_GameFlowManager_C:CompleteTutorial');splice(node(eg,'K2Node_CallFunction_3').find_then_pin(),complete)
    var(bp,'PrologueInstalled',L.get_basic_type_by_name('bool'))
    assert L.compile_blueprint(bp)
    for graph in L.list_graphs(bp):
        if graph.get_name() in names:layout(G.get_graph_editor(graph))
    save(bp)
    # Existing invalid comment GUID is presentation metadata, never gameplay logic.
    tt=unreal.load_asset('/Game/RecordShop/Interaction/Actors/BP_Turntable')
    # PostLoad creates the missing GUID; persist the editor's repair.
    save(tt)
    install_opening_gate('/Game/RecordShop/Interaction/Actors/BP_RecordShelf')
    install_opening_gate('/Game/RecordShop/Interaction/Actors/BP_Turntable')
    unreal.get_default_object(bp.generated_class()).set_editor_property('PrologueInstalled',True)
    save(bp)
    R['pass']=True
except Exception:
    R['fatal']=traceback.format_exc()
R['complete']=True;report()
