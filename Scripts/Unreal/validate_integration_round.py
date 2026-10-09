"""Read-only production-asset validation; transient PIE interactions are isolated.

Run with Invoke-IntegrationPython.ps1 -Editor. No asset or map is saved.
The first 15 seconds only observe natural customer flow. Later tests invoke
real interactions/buttons or simulated Slate keys and are NOT E2E evidence.
"""
import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir())
OUT = ROOT / 'Saved/OvernightIntegration/Round1/runtime.json'
FLOW = '/Game/RecordShop/Core/Flow/BP_GameFlowManager'
SHELF = '/Game/RecordShop/Interaction/Actors/BP_RecordShelf'
TURNTABLE = '/Game/RecordShop/Interaction/Actors/BP_Turntable'
SELECT_UI = '/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect'
TURNTABLE_UI = '/Game/RecordShop/UI/Turntable/WBP_Turntable'
CUSTOMER = '/Game/RecordShop/Characters/Customers/Common/BP_Customer'
RESULT = {'run_started_utc': datetime.now(timezone.utc).isoformat(),
          'natural': [], 'isolated': {}, 'compiles': {}, 'complete': False}
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)


def save():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(RESULT, indent=2, ensure_ascii=False), encoding='utf-8')


def cls(path):
    return unreal.load_class(None, path + '.' + path.rsplit('/', 1)[1] + '_C')


def check(name, action):
    try:
        RESULT['isolated'][name] = {'pass': True, 'observations': action()}
    except Exception:
        RESULT['isolated'][name] = {'pass': False, 'error': traceback.format_exc()}
    save()


save()  # Invalidate an earlier result even if preflight fails before PIE starts.
RESULT['startup_world'] = editor.get_editor_world().get_path_name()
for path in [FLOW, SHELF, TURNTABLE, SELECT_UI, TURNTABLE_UI, CUSTOMER, '/Game/DialogueManager']:
    RESULT['compiles'][path] = unreal.BlueprintEditorLibrary.compile_blueprint(unreal.load_asset(path))
assert all(RESULT['compiles'].values()), 'Blueprint compile failed'
for path in [SELECT_UI, TURNTABLE_UI]:
    graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(unreal.load_asset(path), 'OnKeyDown')
    comparison = next(node for node in graph.list_all_nodes() if node.find_input_pin('B').is_valid())
    assert comparison.find_input_pin('B').get_pin_value() == 'Escape', 'Saved Escape binding differs'
table = unreal.load_asset('/Game/CustomerDialogue')
RESULT['authored_dialogue'] = json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
level.editor_request_begin_play()
start = time.monotonic()
state = {'began': None, 'sample': -1, 'tested': False, 'ended': False,
         'keyboard': None, 'keyboard_next': 0, 'exit_requested': False}


def diagnostics(world, flow):
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    shelves = list(unreal.GameplayStatics.get_all_actors_of_class(world, cls(SHELF)))
    tt = unreal.GameplayStatics.get_all_actors_of_class(world, cls(TURNTABLE))[0]

    def widgets(path):
        return list(unreal.WidgetLibrary.get_all_widgets_of_class(world, cls(path), True))

    def interact(actor):
        actor.call_method('Interact', args=(pawn,))

    def clean_test_widgets():
        # Emergency test isolation only. This cannot make a failed close test pass.
        for w in widgets(SELECT_UI) + widgets(TURNTABLE_UI):
            w.remove_from_parent()
        pc.set_editor_property('show_mouse_cursor', False)
        unreal.WidgetLibrary.set_input_mode_game_only(pc)

    def no_record_playback():
        # A transient second turntable preserves the production actor's selection.
        transform = unreal.Transform()
        statics = unreal.get_default_object(unreal.GameplayStatics)
        scale = unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
        actor = statics.call_method('BeginDeferredActorSpawnFromClass', args=(
            world, cls(TURNTABLE), transform,
            unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, scale))
        actor = statics.call_method('FinishSpawningActor', args=(actor, transform, scale))
        try:
            assert not actor.get_editor_property('HasRecord')
            for method in ['OpenLid', 'PlaceRecord', 'SelectRPM33', 'MoveTonearm']:
                actor.call_method(method)
            assert actor.get_editor_property('TurntableStep') == 4
            actor.call_method('PlayRecord')
            assert actor.get_editor_property('TurntableStep') == 4
            return {'has_record': False, 'step_before': 4, 'step_after': 4}
        finally:
            actor.destroy_actor()

    check('no_record_rejects_playback', no_record_playback)

    def selection():
        observations = []
        for index in range(3):
            interact(shelves[0])
            interact(shelves[0])
            interact(shelves[1])
            interact(tt)
            current = widgets(SELECT_UI)
            assert len(current) == 1, f'Selection count: {len(current)}'
            assert len(widgets(TURNTABLE_UI)) == 0, 'Turntable opened over selection'
            assert pc.get_editor_property('show_mouse_cursor')
            current[0].get_editor_property(f'BTN_LP0{index + 1}').get_editor_property('on_clicked').broadcast()
            record = tt.get_editor_property('CurrentRecord').export_text()
            assert f'Test_record_0{index + 1}' in record, record
            assert tt.get_editor_property('HasRecord')
            assert not widgets(SELECT_UI), 'Selection did not close'
            assert not pc.get_editor_property('show_mouse_cursor'), 'Cursor not restored'
            observations.append({'button': index + 1, 'record': record, 'remaining_widgets': 0, 'cursor': False})
        return observations

    check('selection_reentry_cross_modal_and_all_records', selection)
    clean_test_widgets()

    def turntable_reentry():
        interact(tt)
        interact(tt)
        interact(shelves[0])
        interact(shelves[1])
        assert len(widgets(TURNTABLE_UI)) == 1
        assert not widgets(SELECT_UI)
        assert pc.get_editor_property('show_mouse_cursor')
        return {'turntable_widgets': 1, 'selection_widgets': 0,
                'owner': str(widgets(TURNTABLE_UI)[0].get_owning_player())}

    check('turntable_reentry_cross_modal', turntable_reentry)
    clean_test_widgets()

    def keyboard_closes():
        # WidgetInteraction routes actual Slate key events to the focused widget.
        # The component exists only in this PIE world, and is destroyed below.
        interaction = pawn.call_method('AddComponentByClass', args=(
            unreal.WidgetInteractionComponent.static_class(), False, unreal.Transform(), False))
        interaction.set_component_tick_enabled(False)
        interaction.activate(True)
        escape = unreal.Key()
        escape.import_text('Escape')
        other = unreal.Key()
        other.import_text('F10')
        observations = []
        try:
            for path, actor in [(SELECT_UI, shelves[0]), (TURNTABLE_UI, tt)]:
                for repeat in range(2):
                    interact(actor)
                    widget = widgets(path)[0]
                    # Slate needs a frame to attach the new viewport widget.
                    yield
                    assert widget.get_editor_property('is_focusable'), 'Widget is not focusable'
                    interaction.activate(True)
                    interaction.set_focus(widget)
                    yield
                    focus = widget.has_any_user_focus()
                    RESULT['keyboard_probe'] = {'widget': path, 'any_user_focus': focus,
                                                'escape': escape.export_text(),
                                                'component_active': interaction.is_active()}
                    save()
                    interaction.press_and_release_key(other)
                    assert len(widgets(path)) == 1, 'Unrelated key closed UI'
                    handled = interaction.press_and_release_key(escape)
                    assert not widgets(path), f'Escape did not close {path}'
                    assert not pc.get_editor_property('show_mouse_cursor'), 'Cursor not restored'
                    observations.append({'widget': path, 'cycle': repeat + 1,
                                         'escape_handled': handled, 'remaining_widgets': 0,
                                         'cursor': False})
        finally:
            interaction.destroy_component(pawn)
        RESULT['isolated']['slate_escape_close_reopen_and_unrelated_key'] = {
            'pass': True, 'observations': observations}

    def turntable_order():
        observations = []
        calls = [('PlaceRecord', 0), ('PlayRecord', 0), ('MoveTonearm', 0),
                 ('OpenLid', 1), ('PlaceRecord', 2), ('SelectRPM33', 3),
                 ('MoveTonearm', 4), ('PlayRecord', 5), ('PlayRecord', 5)]
        for method, expected in calls:
            before = tt.get_editor_property('TurntableStep')
            tt.call_method(method)
            after = tt.get_editor_property('TurntableStep')
            assert after == expected, (method, before, after, expected)
            observations.append({'call': method, 'before': before, 'after': after})
        return {'steps': observations, 'rpm': tt.get_editor_property('SelectedRPM'),
                'audio_limit': 'Current authored records have Audio=None; audible playback is unverified.'}

    check('turntable_invalid_valid_order_and_repeat', turntable_order)
    state['keyboard'] = keyboard_closes()


def tick(delta):
    try:
        world = editor.get_game_world()
        if not world:
            if time.monotonic() - start > 90:
                raise RuntimeError('PIE world unavailable after 90 seconds')
            return
        if state['began'] is None:
            state['began'] = time.monotonic()
            RESULT['world'] = world.get_path_name()
            RESULT['is_pie'] = level.is_in_play_in_editor()
        elapsed = time.monotonic() - state['began']
        flow = unreal.GameplayStatics.get_all_actors_of_class(world, cls(FLOW))[0]
        active = flow.get_editor_property('ActiveCustomer')
        if not state['tested'] and int(elapsed) != state['sample']:
            state['sample'] = int(elapsed)
            RESULT['natural'].append({'seconds': round(elapsed, 2),
                                      'state': str(flow.get_editor_property('CurrentState')),
                                      'customer': active.get_name() if active else None,
                                      'location': str(active.get_actor_location()) if active else None})
            save()
        if elapsed >= 15 and not state['tested']:
            state['tested'] = True
            RESULT['last_natural_state'] = str(flow.get_editor_property('CurrentState'))
            diagnostics(world, flow)
        if state['keyboard'] is not None and elapsed >= state['keyboard_next']:
            state['keyboard_next'] = elapsed + 0.5
            try:
                next(state['keyboard'])
            except StopIteration:
                state['keyboard'] = None
            except Exception:
                RESULT['isolated']['slate_escape_close_reopen_and_unrelated_key'] = {
                    'pass': False, 'error': traceback.format_exc()}
                state['keyboard'] = None
            save()
        if state['tested'] and state['keyboard'] is None and not state['exit_requested']:
            state['exit_requested'] = True
            flow.call_method('CloseRecordShopInteractionModals')
            pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
            tt = unreal.GameplayStatics.get_all_actors_of_class(world, cls(TURNTABLE))[0]
            tt.call_method('Interact', args=(pawn,))
            assert len(unreal.WidgetLibrary.get_all_widgets_of_class(world, cls(TURNTABLE_UI), True)) == 1
            RESULT['isolated']['exit_before'] = {
                'state': str(flow.get_editor_property('CurrentState')),
                'customer': str(flow.get_editor_property('ActiveCustomer')),
                'note': 'FinishResult is injected ONLY for isolated lifecycle regression.'}
            flow.call_method('FinishResult')
            save()
        if elapsed >= 45 and not state['ended']:
            state['ended'] = True
            pc = unreal.GameplayStatics.get_player_controller(world, 0)
            remaining = sum(len(unreal.WidgetLibrary.get_all_widgets_of_class(world, cls(path), True))
                            for path in [SELECT_UI, TURNTABLE_UI])
            RESULT['isolated']['exit_after'] = {
                'pass': active is None and str(flow.get_editor_property('CurrentState')) == '<E_GameFlowState.EXPLORE: 0>'
                        and remaining == 0 and not pc.get_editor_property('show_mouse_cursor'),
                'active_customer': str(active), 'state': str(flow.get_editor_property('CurrentState')),
                'remaining_modals': remaining, 'cursor': pc.get_editor_property('show_mouse_cursor')}
            def repeat_exit_cleanup():
                shelf = unreal.GameplayStatics.get_all_actors_of_class(world, cls(SHELF))[0]
                pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
                shelf.call_method('Interact', args=(pawn,))
                assert len(unreal.WidgetLibrary.get_all_widgets_of_class(world, cls(SELECT_UI), True)) == 1
                flow.call_method('HandleCustomerExited')
                flow.call_method('HandleCustomerExited')
                assert not unreal.WidgetLibrary.get_all_widgets_of_class(world, cls(SELECT_UI), True)
                assert not pc.get_editor_property('show_mouse_cursor')
                return {'kind': 'isolated repeated exit consumer, not another natural customer cycle',
                        'remaining_modals': 0, 'cursor': False}
            check('selection_exit_cleanup_and_repeat', repeat_exit_cleanup)
            RESULT['complete'] = True
            save()
            level.editor_request_end_play()
            unreal.unregister_slate_post_tick_callback(handle)
            unreal.SystemLibrary.quit_editor()
    except Exception:
        RESULT['fatal'] = traceback.format_exc()
        save()
        level.editor_request_end_play()
        unreal.unregister_slate_post_tick_callback(handle)
        unreal.SystemLibrary.quit_editor()


handle = unreal.register_slate_post_tick_callback(tick)
save()
