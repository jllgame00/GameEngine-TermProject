"""Read-only graph, input mapping and scoring scaffold evidence. Never saves assets."""
import itertools
import json
import traceback
from pathlib import Path
import unreal

out = {'complete': False, 'graphs': {}, 'scaffold': {}}
out['trace_enum'] = {name: str(getattr(unreal.TraceTypeQuery, name))
                     for name in dir(unreal.TraceTypeQuery) if name.startswith(('ECC_', 'TRACE_'))}
dest = Path(unreal.Paths.project_dir(), 'Saved/OvernightIntegration/Round1/repair-inspection.json')
paths = [
    '/Game/RecordShop/Interaction/Components/BPC_Interaction',
    '/Game/RecordShop/Interaction/Interfaces/BPI_Interactable',
    '/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter',
    '/Game/ThirdPerson/Blueprints/BP_ThirdPersonPlayerController',
    '/Game/RecordShop/Core/Flow/BP_GameFlowManager',
    '/Game/RecordShop/UI/Turntable/WBP_Turntable', '/Game/DialogueManager',
]
try:
    for path in paths:
        bp = unreal.load_asset(path)
        info = {'compile': unreal.BlueprintEditorLibrary.compile_blueprint(bp), 'graphs': {}}
        for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
            info['graphs'][graph.get_name()] = [
                {'id': n.get_name(), 'title': str(n.get_node_title()),
                 'pins': [{'name': str(p.get_pin_name()), 'direction': str(p.get_pin_direction()),
                           'type': str(p.get_pin_type_display_string()), 'value': p.get_pin_value(),
                           'links': [q.get_owning_node().get_name() + ':' + str(q.get_pin_name())
                                     for q in p.list_connected_pins()]} for p in n.list_all_pins()]}
                for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes()]
        cdo = unreal.get_default_object(bp.generated_class())
        info['defaults'] = {str(n): str(cdo.get_editor_property(str(n)))
                            for n in unreal.BlueprintEditorLibrary.list_member_variable_names(bp, False)}
        out['graphs'][path] = info
    context = unreal.load_asset('/Game/Input/IMC_Default')
    out['input_mappings'] = [m.export_text() for m in context.get_editor_property('default_key_mappings').get_editor_property('mappings')]
    manager = unreal.new_object(unreal.load_class(None, '/Game/DialogueManager.DialogueManager_C'))
    scaffold = out['scaffold']
    manager.call_method('StartDialogue')
    scaffold['start'] = {'rows': [str(r) for r in manager.get_editor_property('DialogueList')],
                         'index': manager.get_editor_property('CurrentLineIndex')}
    manager.call_method('ShowNextLine')
    scaffold['next_index'] = manager.get_editor_property('CurrentLineIndex')
    scaffold['customer_default'] = manager.get_editor_property('CurrentCustomer').export_text()
    scaffold['scores'] = []
    for matches in itertools.product([False, True], repeat=3):
        args = tuple('' if match else 'repair-nonmatching-fixture' for match in matches)
        score = manager.call_method('CalculateLPScore', args=args)
        assert score == sum(matches), (matches, score)
        scaffold['scores'].append({'matches': matches, 'score': score})
    scaffold['evaluate'] = []
    for available in [[], ['fixture-a'], ['fixture-a', 'fixture-b']]:
        for args in [('', '', ''), ('repair-fixture',) * 3]:
            returned = manager.call_method('EvaluateLP', args=(*args, available))
            maximum = manager.get_editor_property('MaxScore')
            assert maximum == 0, maximum
            scaffold['evaluate'].append({'args': args, 'available': available,
                                         'max_score': maximum, 'return': str(returned)})
    out['complete'] = True
except Exception:
    out['fatal'] = traceback.format_exc()
finally:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    unreal.log('CHECKPOINT_REPAIR_INSPECTION_COMPLETE')
