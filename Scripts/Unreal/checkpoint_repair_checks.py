"""Additional isolated PIE checks. All positioning/spawning is transient."""
import traceback
import unreal


def rpm_ui_checks(world, pawn, turntable_class, widget_class, record, check):
    for rpm in (45, 78):
        def run(rpm=rpm):
            transform = unreal.Transform(location=unreal.Vector(0, 0, 3000))
            statics = unreal.get_default_object(unreal.GameplayStatics)
            scale = unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
            actor = statics.call_method('BeginDeferredActorSpawnFromClass', args=(
                world, turntable_class, transform,
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, scale))
            actor = statics.call_method('FinishSpawningActor', args=(actor, transform, scale))
            widget = None
            observations = []
            try:
                actor.call_method('SetRecord', args=(record,))
                actor.call_method('Interact', args=(pawn,))
                widgets = list(unreal.WidgetLibrary.get_all_widgets_of_class(world, widget_class, True))
                assert len(widgets) == 1
                widget = widgets[0]
                assert widget.get_editor_property('TurntableRef') == actor
                options = widget.get_editor_property('VB_RPMOptions')

                def click(button, expected):
                    before = actor.get_editor_property('TurntableStep')
                    widget.get_editor_property(button).get_editor_property('on_clicked').broadcast()
                    after = actor.get_editor_property('TurntableStep')
                    observations.append({'button': button, 'before': before, 'after': after,
                                         'rpm': actor.get_editor_property('SelectedRPM'),
                                         'options': str(options.get_visibility())})
                    assert after == expected, observations[-1]

                click('BTN_SelectRPM', 0)
                assert options.get_visibility() == unreal.SlateVisibility.COLLAPSED
                click('BTN_OpenLid', 1)
                click('BTN_PlaceRecord', 2)
                click('BTN_SelectRPM', 2)
                assert options.get_visibility() == unreal.SlateVisibility.VISIBLE
                click(f'BTN_RPM{rpm}', 3)
                assert actor.get_editor_property('SelectedRPM') == rpm
                assert options.get_visibility() == unreal.SlateVisibility.COLLAPSED
                click('BTN_SelectRPM', 3)
                assert options.get_visibility() == unreal.SlateVisibility.COLLAPSED
                click('BTN_MoveTonearm', 4)
                click('BTN_Play', 5)
                click('BTN_Play', 5)
                return {'events': observations, 'limit': 'OnClicked broadcasts, not mouse hit testing; Audio=None.'}
            finally:
                if widget:
                    widget.remove_from_parent()
                actor.destroy_actor()
                pc = unreal.GameplayStatics.get_player_controller(world, 0)
                pc.set_editor_property('show_mouse_cursor', False)
                unreal.WidgetLibrary.set_input_mode_game_only(pc)
        check(f'rpm{rpm}_widget_button_path', run)


def physical_input_checks(world, flow, pawn, targets, result, save):
    """Inject IA_Interact into the real local player; never call Interact/TryInteract.

    Paired near/away cases exercise actual collision and interface dispatch. Pawn
    teleporting supplies repeatable geometry, not natural navigation evidence.
    """
    key = 'physical_input_sphere_trace_interface'
    observations = []
    original = pawn.get_actor_transform()
    movement = pawn.get_component_by_class(unreal.CharacterMovementComponent)
    mode = movement.get_editor_property('movement_mode')
    try:
        pc = unreal.GameplayStatics.get_player_controller(world, 0)
        library = unreal.get_default_object(unreal.load_class(None, '/Script/Engine.SubsystemBlueprintLibrary'))
        subsystem = library.call_method('GetLocalPlayerSubSystemFromPlayerController',
                                        args=(pc, unreal.EnhancedInputLocalPlayerSubsystem.static_class()))
        action = unreal.load_asset('/Game/RecordShop/Input/IA_Interact')
        mapped_keys = [key.export_text() for key in subsystem.query_keys_mapped_to_action(action)]
        assert 'E' in mapped_keys, mapped_keys
        result['physical_input_mapping'] = {'action': action.get_path_name(), 'active_keys': mapped_keys}
        component = pawn.get_editor_property('BPC_Interaction')
        distance = component.get_editor_property('TraceDistance')
        radius = component.get_editor_property('TraceRadius')
        assert distance == 180 and radius == 60
        movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
        movement.stop_movement_immediately()

        def trace():
            start = pawn.get_actor_location()
            end = start + pawn.get_actor_forward_vector() * distance
            hit = unreal.SystemLibrary.sphere_trace_single(
                component, start, end, radius, unreal.TraceTypeQuery.ECC_INTERACTABLE,
                False, [], unreal.DrawDebugTrace.NONE, True)
            return hit

        for actor, widget_class in targets:
            origin, extent = actor.get_actor_bounds(False)
            found = False
            # Search an unobstructed approach using production collision settings.
            for yaw, offset in [(0, unreal.Vector(-1, 0, 0)), (180, unreal.Vector(1, 0, 0)),
                                (90, unreal.Vector(0, -1, 0)), (-90, unreal.Vector(0, 1, 0))]:
                gap = (extent.x if offset.x else extent.y) + 100
                pos = origin + offset * gap
                pos.z = max(origin.z, original.translation.z)
                pawn.set_actor_location_and_rotation(pos, unreal.Rotator(0, yaw, 0), False, True)
                hit = trace()
                if hit and actor.get_name() in hit.export_text():
                    found = True
                    break
            assert found, f'No trace approach found for {actor.get_name()}'
            yield
            near_hit = trace()
            assert near_hit and actor.get_name() in near_hit.export_text()
            assert not unreal.WidgetLibrary.get_all_widgets_of_class(world, widget_class, True)
            subsystem.inject_input_vector_for_action(action, unreal.Vector(1, 0, 0), [], [])
            yield
            widgets = list(unreal.WidgetLibrary.get_all_widgets_of_class(world, widget_class, True))
            observations.append({'target': actor.get_name(), 'case': 'near',
                                 'pawn': str(pawn.get_actor_location()), 'hit': near_hit.export_text(),
                                 'widgets': len(widgets)})
            assert len(widgets) == 1, observations[-1]
            assert widgets[0].get_owning_player() == pc
            flow.call_method('CloseRecordShopInteractionModals')
            subsystem.inject_input_vector_for_action(action, unreal.Vector(), [], [])
            yield
            pawn.set_actor_rotation(unreal.Rotator(0, yaw + 180, 0), True)
            yield
            away_hit = trace()
            assert not away_hit or actor.get_name() not in away_hit.export_text()
            subsystem.inject_input_vector_for_action(action, unreal.Vector(1, 0, 0), [], [])
            yield
            count = len(unreal.WidgetLibrary.get_all_widgets_of_class(world, widget_class, True))
            observations.append({'target': actor.get_name(), 'case': 'away', 'widgets': count,
                                 'hit': away_hit.export_text() if away_hit else None})
            assert count == 0, observations[-1]
            subsystem.inject_input_vector_for_action(action, unreal.Vector(), [], [])
            yield
        result['isolated'][key] = {'pass': True, 'observations': observations,
                                  'limit': 'Enhanced Input action injection; OS E key not synthesized.'}
    except Exception:
        result['isolated'][key] = {'pass': False, 'observations': observations, 'error': traceback.format_exc()}
    finally:
        flow.call_method('CloseRecordShopInteractionModals')
        pawn.set_actor_transform(original, False, True)
        movement.set_movement_mode(mode)
        save()
