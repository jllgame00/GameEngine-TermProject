"""Repair the Result focus target with supported Editor graph APIs, then save."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir())
sys.path.insert(0, str(ROOT / 'Scripts/Unreal'))
from mvp_graph_helpers import evgraph, get, link, pin

FLOW = '/Game/RecordShop/Core/Flow/BP_GameFlowManager'
RESULT = '/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
report = {'complete': False, 'pass': False, 'saved': []}
try:
    flow = unreal.load_asset(FLOW)
    result = unreal.load_asset(RESULT)
    assert unreal.BlueprintEditorLibrary.compile_blueprint(result)
    graph = evgraph(flow)
    mode = next(n for n in graph.list_all_nodes() if n.get_name() == 'K2Node_CallFunction_31')
    target = pin(mode, 'InWidgetToFocus')
    previous = target.list_connected_pins()
    assert len(previous) == 1 and str(previous[0].get_pin_name()) == 'ResultWidgetRef'
    button = graph.add_get_member_variable_node('Continue', RESULT + '.WBP_Result_IntegrationFallback_C')
    link(get(graph, 'ResultWidgetRef'), pin(button, 'self'))
    target.break_pin_links()
    link(pin(button, 'Continue', True), target)
    report['focus_target'] = 'ResultWidgetRef.Continue (focusable SButton)'
    report['compiles'] = {p: unreal.BlueprintEditorLibrary.compile_blueprint(unreal.load_asset(p)) for p in [FLOW, RESULT]}
    assert all(report['compiles'].values())
    assert unreal.EditorAssetLibrary.save_loaded_asset(flow)
    report['saved'].append(flow.get_path_name())
    report['pass'] = True
except Exception:
    report['fatal'] = traceback.format_exc()
finally:
    report['complete'] = True
    Path(os.environ['MVP_RESULT']).write_text(json.dumps(report, indent=2), encoding='utf-8')
