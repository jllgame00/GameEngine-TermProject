"""Fresh-load opening contract, RED before Editor installation."""
import json, os, traceback
from pathlib import Path
import unreal
R = {'complete': False, 'pass': False}
try:
    flow = unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager')
    names = set(map(str, unreal.BlueprintEditorLibrary.list_member_variable_names(flow, False)))
    assert 'TutorialComplete' in names, 'Missing session tutorial completion state'
    assert 'PrologueStage' in names, 'Missing guarded New Game / prologue progression'
    widget = unreal.load_asset('/Game/RecordShop/UI/Prologue/WBP_Prologue')
    assert widget, 'Missing opening UMG presentation'
    R['compiles'] = {bp.get_path_name(): unreal.BlueprintEditorLibrary.compile_blueprint(bp) for bp in (flow, widget)}
    assert all(R['compiles'].values())
    cdo = unreal.get_default_object(flow.generated_class())
    assert not cdo.get_editor_property('TutorialComplete')
    assert cdo.get_editor_property('PrologueStage') == 0
    graph_names = {g.get_name() for g in unreal.BlueprintEditorLibrary.list_graphs(flow)}
    assert {'BeginPrologue', 'AdvancePrologue', 'UpdateTutorialHint', 'CompleteTutorial', 'FocusPrologue', 'DismissTutorialHint'} <= graph_names
    R['pass'] = True
except Exception:
    R['fatal'] = traceback.format_exc()
R['complete'] = True
Path(os.environ['MVP_RESULT']).write_text(json.dumps(R, indent=2, ensure_ascii=False), encoding='utf-8')
