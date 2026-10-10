"""Dialogue assertions for the real production Ready path and isolated edge cases."""
import json
import unreal

UI='/Game/RecordShop/UI/Dialogue/WBP_Dialogue'
DM='/Game/DialogueManager'

def dialogue_checks(world,flow,cls,result,check):
    pc=unreal.GameplayStatics.get_player_controller(world,0)
    pawn=unreal.GameplayStatics.get_player_pawn(world,0)
    def widgets(): return list(unreal.WidgetLibrary.get_all_widgets_of_class(world,cls(UI),True))
    manager=flow.get_editor_property('DialogueManagerRef')
    current=widgets()
    result['natural_dialogue']={
        'manager':str(manager),'widgets':len(current),
        'line_index':manager.get_editor_property('CurrentLineIndex') if manager else None,
        'rows':[str(x) for x in manager.get_editor_property('DialogueList')] if manager else None,
        'speaker':str(current[0].get_editor_property('Speaker').get_text()) if current else None,
        'text':str(current[0].get_editor_property('DialogueText').get_text()) if current else None,
        'cursor':pc.get_editor_property('show_mouse_cursor'),
        'note':'Observation only, before repeated callbacks, fixture broadcasts or button injection.'}
    def handoff():
        assert manager and len(current)==1, result['natural_dialogue']
        assert manager.get_owner()==flow
        assert len(flow.get_components_by_class(cls(DM)))==1
        assert flow.get_editor_property('DialogueStartedForCustomer')
        assert manager.get_editor_property('CurrentLineIndex')==1
        assert current[0].get_editor_property('DialogueManagerRef')==manager
        assert pc.get_editor_property('show_mouse_cursor')
        assert current[0].get_owning_player()==pc
        return result['natural_dialogue']
    check('dialogue_natural_ready_start_ui',handoff)
    def natural_next():
        assert len(widgets())==1
        current[0].get_editor_property('Next').get_editor_property('on_clicked').broadcast()
        assert not widgets()
        assert flow.get_editor_property('DialogueWidgetRef') is None
        assert str(flow.get_editor_property('CurrentState'))=='<E_GameFlowState.EXPLORE: 0>'
        assert not pc.get_editor_property('show_mouse_cursor')
        result['natural_dialogue_next']={'state':'Explore','widgets':0,'cursor':False,
            'input':'Next button delegate, after observation; no downstream flow callback or data fixture injected.'}
        return result['natural_dialogue_next']
    check('dialogue_natural_next_finished_explore',natural_next)
    # Unsaved diagnostic actor: Blueprint setters respect protected editor-instance flags.
    # This helper never participates in the natural Ready/Next path above.
    factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
    fixture=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_DialogueTestFixture','/Game/RecordShop/Dev/IntegrationProbe',unreal.Blueprint,factory)
    graph=unreal.BlueprintGraphEditor.create_and_edit_function_graph(fixture,'ResetCycle')
    target=graph.add_graph_input_parameter('Flow',unreal.BlueprintEditorLibrary.get_object_reference_type(flow.get_class()))
    mood=graph.add_graph_input_parameter('Mood',unreal.BlueprintEditorLibrary.get_basic_type_by_name('string'))
    reset=graph.add_set_member_variable_node('DialogueStartedForCustomer',flow.get_class().get_path_name())
    assert target.try_create_connection(reset.find_input_pin('self'))
    assert graph.find_graph_entry_pin().try_create_connection(reset.find_execute_pin())
    getmanager=graph.add_get_member_variable_node('DialogueManagerRef',flow.get_class().get_path_name())
    assert target.try_create_connection(getmanager.find_input_pin('self'))
    setmood=graph.add_set_member_variable_node('CurrentMood',manager.get_class().get_path_name())
    assert getmanager.find_output_pin('DialogueManagerRef').try_create_connection(setmood.find_input_pin('self'))
    assert mood.try_create_connection(setmood.find_input_pin('CurrentMood'))
    assert reset.find_then_pin().try_create_connection(setmood.find_execute_pin())
    assert unreal.BlueprintEditorLibrary.compile_blueprint(fixture)
    fixture_object=unreal.get_default_object(fixture.generated_class())
    def reset_cycle(mood=''):
        fixture_object.call_method('ResetCycle',args=(flow,mood))
    def reentry():
        # Subsequent cases are isolated diagnostics, explicitly reopening the same cycle.
        reset_cycle()
        flow.call_method('HandleCustomerReadyForDialogue')
        current[:]=widgets()
        assert len(widgets())==1
        for _ in range(3):flow.call_method('HandleCustomerReadyForDialogue')
        assert len(widgets())==1 and widgets()[0]==current[0]
        assert len(flow.get_components_by_class(cls(DM)))==1
        assert manager.get_editor_property('CurrentLineIndex')==1
        for actor_path,widget_path in [('/Game/RecordShop/Interaction/Actors/BP_RecordShelf','/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect'),('/Game/RecordShop/Interaction/Actors/BP_Turntable','/Game/RecordShop/UI/Turntable/WBP_Turntable')]:
            actor=unreal.GameplayStatics.get_all_actors_of_class(world,cls(actor_path))[0]
            actor.call_method('Interact',args=(pawn,))
            assert not unreal.WidgetLibrary.get_all_widgets_of_class(world,cls(widget_path),True)
        return {'dialogue_widgets':1,'manager_components':1,'repeated_ready':3,'other_modals':0}
    check('dialogue_reentry_and_cross_modal',reentry)
    def update_finish():
        # Synthetic strings verify forwarding only; never written to authored data.
        table=unreal.load_asset('/Game/CustomerDialogue')
        original=unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table)
        rows=json.loads(original);rows[0]['Speaker']='speaker-fixture';rows[0]['Text']='line-fixture'
        try:
            assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps(rows))
            manager.call_method('StartDialogue')
            assert str(current[0].get_editor_property('Speaker').get_text())=='speaker-fixture'
            assert str(current[0].get_editor_property('DialogueText').get_text())=='line-fixture'
        finally:
            assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,original)
        manager.call_method('StartDialogue')
        current[0].get_editor_property('Next').get_editor_property('on_clicked').broadcast()
        assert not widgets()
        assert flow.get_editor_property('DialogueWidgetRef') is None
        assert current[0].get_editor_property('DialogueManagerRef') is None
        assert str(flow.get_editor_property('CurrentState'))=='<E_GameFlowState.EXPLORE: 0>'
        assert not pc.get_editor_property('show_mouse_cursor')
        flow.call_method('HandleCustomerReadyForDialogue')
        manager.call_method('ShowNextLine')
        assert not widgets(), 'Late Ready/Finished reopened dialogue'
        return {'forwarded_speaker_and_text':True,'next_button_closed':True,'widget_ref':None,'cursor':False,'state':'Explore','late_callback_safe':True}
    check('dialogue_update_next_finished_input_restore',update_finish)
    def empty_content():
        reset_cycle('integration-unmatched-fixture')
        flow.call_method('HandleCustomerReadyForDialogue')
        assert len(manager.get_editor_property('DialogueList'))==0
        assert not widgets()
        assert flow.get_editor_property('DialogueWidgetRef') is None
        assert str(flow.get_editor_property('CurrentState'))=='<E_GameFlowState.EXPLORE: 0>'
        assert not pc.get_editor_property('show_mouse_cursor')
        assert len(flow.get_components_by_class(cls(DM)))==1
        reset_cycle()
        return {'no_matching_rows':True,'widgets':0,'state':'Explore','manager_reused':True}
    check('dialogue_empty_content_finishes_synchronously',empty_content)
    def exit_cleanup():
        reset_cycle()
        flow.call_method('HandleCustomerReadyForDialogue')
        assert len(widgets())==1
        old=widgets()[0]
        flow.call_method('CloseRecordShopInteractionModals')
        flow.call_method('CloseRecordShopInteractionModals')
        assert not widgets()
        assert flow.get_editor_property('DialogueWidgetRef') is None
        assert old.get_editor_property('DialogueManagerRef') is None
        assert not pc.get_editor_property('show_mouse_cursor')
        return {'cleanup_idempotent':True,'widgets':0,'widget_and_manager_refs_cleared':True}
    check('dialogue_modal_cleanup_idempotent',exit_cleanup)
