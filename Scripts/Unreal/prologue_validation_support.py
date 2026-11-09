"""Shared input-driven opening checks; never edits production assets/state."""
import time
import unreal
UI = '/Game/RecordShop/UI/Prologue/WBP_Prologue'

def exercise_opening(world, flow, pc, pawn, advance, capture=None):
    observations = []
    assert not flow.get_editor_property('TutorialComplete')
    assert flow.get_editor_property('PrologueStage') == 0
    for stage, expected in [(0, '가게의 첫날'), (1, '7일간'), (2, '손님의 이야기를 듣고')]:
        panel = flow.get_editor_property('PrologueWidgetRef')
        assert panel and panel.is_in_viewport()
        assert flow.get_editor_property('PrologueStage') == stage, ('expected',stage,'actual',flow.get_editor_property('PrologueStage'))
        assert flow.get_editor_property('ActiveCustomer') is None
        assert pc.get_editor_property('show_mouse_cursor')
        assert pc.get_view_target() == pawn, 'Opening stole the camera'
        assert panel.get_editor_property('Continue').has_keyboard_focus(), 'Opening has no production button focus'
        body = str(panel.get_editor_property('ScoreStatus').get_text())
        assert expected in body, body
        if stage == 1:
            assert '부모님' in body and '일주일' in body and '레코드숍' in body
        if stage == 2:
            assert '오늘이 첫날' in body and '어울리는 음악' in body
        observations.append({'stage': stage, 'body': body, 'customer_spawned': False, 'production_focus': True})
        if capture: yield from capture('prologue-' + str(stage))
        assert panel.get_editor_property('Continue').has_keyboard_focus(), 'Opening lost production focus after presentation'
        yield from advance(panel)
    assert flow.get_editor_property('PrologueStage') == 3
    assert flow.get_editor_property('PrologueWidgetRef') is None
    assert not pc.get_editor_property('show_mouse_cursor')
    assert pc.get_view_target() == pawn
    hint = flow.get_editor_property('TutorialHintRef')
    assert hint and hint.get_visibility() == unreal.SlateVisibility.HIT_TEST_INVISIBLE
    assert hint.get_editor_property('Continue').get_visibility() == unreal.SlateVisibility.COLLAPSED
    lib = unreal.get_default_object(unreal.load_class(None, '/Script/Engine.SubsystemBlueprintLibrary'))
    sub = lib.call_method('GetLocalPlayerSubSystemFromPlayerController', args=(pc, unreal.EnhancedInputLocalPlayerSubsystem.static_class()))
    before = pawn.get_actor_location(); deadline = time.monotonic() + .35
    while time.monotonic() < deadline:
        sub.inject_input_vector_for_action(unreal.load_asset('/Game/Input/Actions/IA_Move'), unreal.Vector(0,-.25,0), [], [])
        yield
    distance = (pawn.get_actor_location() - before).length()
    assert distance > 5, 'Prologue did not restore Explore movement'
    assert flow.get_editor_property('ActiveCustomer') is None, 'No free Explore interval before first customer'
    observations.append({'stage': 3, 'restored_movement_cm': distance, 'passive_hint': True})
    if capture: yield from capture('tutorial-explore')
    return observations
