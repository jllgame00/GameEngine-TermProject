"""Isolated diagnostics, explicitly not natural-cycle evidence. Never saves assets."""
import os,json,time,traceback,itertools,sys
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import *
def component_state(actor):
    result = {}
    for name in ('Lid', 'Record', 'Tonearm', 'TonearmPivot'):
        component = actor.get_editor_property(name)
        rotation = component.get_editor_property('relative_rotation')
        result[name] = {'rotation': [round(rotation.pitch, 4), round(rotation.yaw, 4),
                                     round(rotation.roll, 4)],
                        'visible': component.is_visible(),
                        'location': component.get_editor_property('relative_location').export_text(),
                        'scale': component.get_editor_property('relative_scale3d').export_text()}
    return result


def stylus_contact(actor):
    """Measure cartridge clearance against actual LOD0 record triangles in world cm.

    Catches hovering/penetration even when the configured arm angle is reached.
    The canonical tonearm cartridge occupies local Y > 45 cm.
    """
    arm = actor.get_editor_property('Tonearm')
    record = actor.get_editor_property('Record')
    vertices, *_ = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(
        arm.get_editor_property('static_mesh'), 0, 0)
    distal = [unreal.MathLibrary.transform_location(arm.get_world_transform(), v)
              for v in vertices if v.y > 45]
    assert distal, 'Canonical cartridge geometry missing'
    tip = min(distal, key=lambda v: v.z)
    vertices, triangles, *_ = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(
        record.get_editor_property('static_mesh'), 0, 0)
    vertices = [unreal.MathLibrary.transform_location(record.get_world_transform(), v)
                for v in vertices]
    hits = []
    for index in range(0, len(triangles), 3):
        a, b, c = [vertices[triangles[index+j]] for j in range(3)]
        denominator = (b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
        if abs(denominator) < 1e-6:
            continue
        u = ((b.y-c.y)*(tip.x-c.x)+(c.x-b.x)*(tip.y-c.y))/denominator
        v = ((c.y-a.y)*(tip.x-c.x)+(a.x-c.x)*(tip.y-c.y))/denominator
        w = 1-u-v
        if min(u, v, w) >= -0.0001:
            hits.append(u*a.z+v*b.z+w*c.z)
    assert hits, 'Stylus is not above the playable record surface'
    return {'tip_xyz': [tip.x, tip.y, tip.z], 'record_surface_z': max(hits),
            'gap_cm': tip.z-max(hits)}


def presentation_motion_checks(world, turntable_class, widget_class, pawn, record, check):
    """Direct deterministic motion checks, including interruption; not natural input."""
    def run():
        statics = unreal.get_default_object(unreal.GameplayStatics)
        transform = unreal.Transform(location=unreal.Vector(0, 0, 3000))
        scale = unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
        actor = statics.call_method('BeginDeferredActorSpawnFromClass', args=(
            world, turntable_class, transform,
            unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, scale))
        actor = statics.call_method('FinishSpawningActor', args=(actor, transform, scale))
        actor.set_actor_tick_enabled(False)
        observations = []
        try:
            def sample(component, property_name, axis):
                return getattr(actor.get_editor_property(component).get_editor_property(property_name), axis)
            for method, component, prop, axis, beginning, ending, setup in (
                ('OpenLid', 'Lid', 'relative_rotation', 'pitch', 0, -70, ()),
                ('PlaceRecord', 'Record', 'relative_location', 'z', 62.383362, 22.383362, ('OpenLid',)),
                ('MoveTonearm', 'TonearmPivot', 'relative_rotation', 'yaw', 0, 35,
                 ('OpenLid', 'PlaceRecord', 'SelectRPM33')),
            ):
                actor.call_method('SetRecord', args=(record,))
                initial = component_state(actor)
                for previous in setup:
                    actor.call_method(previous)
                actor.call_method(method)
                assert abs(sample(component, prop, axis)-beginning) < 0.01, method+' must begin at source start pose'
                actor.call_method('ReceiveTick', args=(0.5,))
                middle = sample(component, prop, axis)
                expected_middle = 35 * 0.5 / 0.6 if method == 'MoveTonearm' else (beginning+ending)/2
                assert abs(middle-expected_middle) < 0.01, (method, middle)
                raised_roll = sample('TonearmPivot', 'relative_rotation', 'roll')
                actor.call_method(method)
                assert abs(sample(component, prop, axis)-middle) < 0.01, 'Repeated action rewound motion'
                actor.call_method('ReceiveTick', args=(0.5,))
                assert abs(sample(component, prop, axis)-ending) < 0.01, method
                if method == 'MoveTonearm':
                    contact = stylus_contact(actor)
                    assert raised_roll < -12, 'Arm did not remain raised during swing'
                    assert -0.02 <= contact['gap_cm'] <= 0.05, ('Stylus must contact record', contact)
                    observations.append({'animated_contact': contact})
                    actor.call_method('SettlePresentationMotion')
                    settled_contact = stylus_contact(actor)
                    assert abs(settled_contact['gap_cm']-contact['gap_cm']) < 0.01, 'Close/settle changed contact'
                observations.append({'action': method, 'midpoint': middle, 'end': ending})
                actor.call_method('SetRecord', args=(record,))
                for previous in setup:
                    actor.call_method(previous)
                actor.call_method(method)
                actor.call_method('ReceiveTick', args=(0.25,))
                actor.call_method('SetRecord', args=(record,))
                actor.call_method('ReceiveTick', args=(2.0,))
                assert component_state(actor) == initial, 'SetRecord did not cancel motion'
            actor.call_method('Interact', args=(pawn,))
            widget = next(w for w in unreal.WidgetLibrary.get_all_widgets_of_class(world, widget_class, True)
                          if w.get_editor_property('TurntableRef') == actor)
            actor.call_method('OpenLid')
            actor.call_method('ReceiveTick', args=(0.25,))
            widget.remove_from_parent()
            assert widget.get_editor_property('TurntableRef') is None
            assert abs(sample('Lid', 'relative_rotation', 'pitch')+70) < 0.01
            settled = component_state(actor)
            actor.call_method('ReceiveTick', args=(2.0,))
            assert component_state(actor) == settled, 'Closed modal left motion running'
            return observations
        finally:
            actor.destroy_actor()
    check('presentation_motion_midpoints_reset_and_close', run)


def owner_placement_checks(world, turntable_class, pawn, record, check):
    """Direct guard/cancellation diagnostics; rendered input-driven proof is in the cycle suite."""
    def run():
        statics = unreal.get_default_object(unreal.GameplayStatics)
        transform = unreal.Transform(location=unreal.Vector(0, 0, 3000))
        scale = unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
        actor = statics.call_method('BeginDeferredActorSpawnFromClass', args=(
            world, turntable_class, transform,
            unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, scale))
        actor = statics.call_method('FinishSpawningActor', args=(actor, transform, scale))
        previous = pawn.get_actor_transform()
        mesh = pawn.get_component_by_class(unreal.SkeletalMeshComponent)
        anim = mesh.get_anim_instance()
        montage = unreal.load_asset('/Game/RecordShop/Animation/Player/Montages/AM_ShopOwner_PlaceRecord')
        try:
            # Reproduce owner feedback: accepted placement from an oblique
            # approach must not silently omit the montage outside the old 24cm gate.
            pawn.set_actor_location_and_rotation(unreal.Vector(45, -80, 3000),
                unreal.Rotator(pitch=0, yaw=90, roll=0), False, True)
            actor.call_method('SetRecord', args=(record,))
            actor.call_method('PlaceRecord')
            assert not anim.montage_is_active(montage), 'Rejected placement animated'
            actor.call_method('OpenLid')
            actor.call_method('PlaceRecord')
            assert anim.montage_is_active(montage), 'Accepted placement lacked montage'
            anim.montage_set_position(montage, .4)
            actor.call_method('PlaceRecord')
            assert abs(anim.montage_get_position(montage)-.4) < .001, 'Repeated placement restarted montage'
            assert actor.get_editor_property('TurntableStep') == 2
            actor.call_method('StopOwnerPresentation')
            assert actor.get_editor_property('OwnerMontageRemaining') == 0
            assert actor.get_editor_property('OwnerAlignmentRemaining') == 0
            assert actor.get_editor_property('TurntableStep') == 2, 'Animation cancellation advanced gameplay'
            hand = unreal.load_asset('/Game/RecordShop/Animation/Player/Montages/AM_ShopOwner_HandInteraction')
            actor.call_method('SelectRPM33');actor.call_method('MoveTonearm')
            assert anim.montage_is_active(hand), 'Accepted tonearm action lacked montage'
            anim.montage_set_position(hand, .4)
            actor.call_method('MoveTonearm')
            assert abs(anim.montage_get_position(hand)-.4) < .001, 'Repeated tonearm action restarted montage'
            actor.call_method('StopOwnerPresentation')
            assert actor.get_editor_property('TurntableStep') == 4, 'Hand cancellation advanced gameplay'
            actor.call_method('SetRecord', args=(record,))
            assert actor.get_editor_property('TurntableStep') == 0
            assert actor.get_editor_property('OwnerMontageRemaining') == 0
            # No actor movement or animation is allowed for a far-away diagnostic turntable.
            pawn.set_actor_location(previous.translation, False, True)
            actor.call_method('OpenLid');actor.call_method('PlaceRecord')
            assert actor.get_editor_property('OwnerMontageRemaining') == 0
            return {'rejected_action': True, 'duplicate_guard': True,
                    'interruption_independent_of_gameplay': True, 'reset': True,
                    'far_player_does_not_fake_contact': True, 'tonearm_duplicate_and_cancel_guard': True}
        finally:
            actor.call_method('StopOwnerPresentation')
            pawn.set_actor_transform(previous, False, True)
            actor.destroy_actor()
    check('owner_placement_guards_cancellation_and_reset', run)


def repeat_setup_checks(world, turntable_class, record, check):
    import re
    record.import_text(re.sub(r'(Audio_[A-Za-z0-9_]+)=(?:None|"[^"]*")', r'\1=None', record.export_text()))
    def run():
        transform = unreal.Transform(location=unreal.Vector(0, 0, 3000))
        statics = unreal.get_default_object(unreal.GameplayStatics)
        scale = unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
        actor = statics.call_method('BeginDeferredActorSpawnFromClass', args=(
            world, turntable_class, transform,
            unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, scale))
        actor = statics.call_method('FinishSpawningActor', args=(actor, transform, scale))
        observations = []
        try:
            for part in ('Base', 'Lid', 'Record', 'Tonearm'):
                component = actor.get_editor_property(part)
                assert component.get_editor_property('static_mesh').get_name() == 'SM_Turntable_'+part
                scale3d = component.get_editor_property('relative_scale3d')
                assert all(abs(value-1) < 0.001 for value in (scale3d.x, scale3d.y, scale3d.z))
            pivot = actor.get_editor_property('TonearmPivot')
            assert actor.get_editor_property('Tonearm').get_attach_parent() == pivot
            initial = component_state(actor)
            actor.call_method('SetRecord', args=(record,))
            for rpm in (33, 45, 78):
                for method in ('OpenLid', 'PlaceRecord', f'SelectRPM{rpm}', 'MoveTonearm', 'PlayRecord'):
                    actor.call_method(method)
                assert actor.get_editor_property('PlaybackRequested')
                assert actor.get_editor_property('PlaybackAudio') is None
                actor.call_method('ReceiveTick', args=(0.3,))
                assert 0 < actor.get_editor_property('TonearmMotionAlpha') < 1
                assert actor.get_editor_property('PlaybackAudio') is None, 'Music before needle contact'
                actor.call_method('ReceiveTick', args=(0.7,))
                contact = stylus_contact(actor)
                assert -0.02 <= contact['gap_cm'] <= 0.05, ('Playback stylus contact', rpm, contact)
                assert not actor.get_editor_property('CompletionSent'), 'Silent presentation skipped physical return'
                actor.call_method('ReceiveTick', args=(1.5,))
                actor.call_method('ReceiveTick', args=(0.0,))
                return_start = stylus_contact(actor)
                assert abs(return_start['gap_cm']-contact['gap_cm']) < 0.01, 'Lift starts from a different contact pose'
                actor.call_method('ReceiveTick', args=(0.42,))
                lifted = pivot.get_editor_property('relative_rotation')
                assert abs(lifted.yaw-35) < 0.01 and lifted.roll < -12, 'Return moved horizontally before lifting'
                lifted_contact = stylus_contact(actor)
                assert lifted_contact['gap_cm'] > 3, ('Stylus failed to lift clear', lifted_contact)
                actor.call_method('ReceiveTick', args=(0.78,))
                assert actor.get_editor_property('CompletionSent')
                before = component_state(actor)
                assert before['Record']['visible']
                actor.call_method('ReceiveTick', args=(0.25,))
                assert component_state(actor) == before, 'Audio=None must not keep spinning'
                actor.call_method('SetRecord', args=(record,))
                after = component_state(actor)
                observations.append({'rpm': rpm, 'before': before, 'after': after,
                                     'contact': contact, 'lifted_contact': lifted_contact})
                assert after == initial, {'initial': initial, 'observations': observations}
                assert actor.get_editor_property('TurntableStep') == 0
                assert actor.get_editor_property('SelectedRPM') == 0
                assert not actor.get_editor_property('CompletionSent')
                assert actor.get_editor_property('HasRecord')
                assert actor.get_editor_property('PlaybackAudio') is None
            # Replacement cancels both silent rotation and an in-progress return.
            # Later ticks must not deliver a stale completion for the new record.
            for elapsed in (0.5, 1.9):
                for method in ('OpenLid', 'PlaceRecord', 'SelectRPM33', 'MoveTonearm', 'PlayRecord'):
                    actor.call_method(method)
                actor.call_method('ReceiveTick', args=(1.0,))
                actor.call_method('ReceiveTick', args=(min(elapsed, 1.5),))
                if elapsed > 1.5:
                    actor.call_method('ReceiveTick', args=(elapsed-1.5,))
                actor.call_method('SetRecord', args=(record,))
                actor.call_method('ReceiveTick', args=(10.0,))
                assert not actor.get_editor_property('CompletionSent')
                assert actor.get_editor_property('TurntableStep') == 0
                assert component_state(actor) == initial
                observations.append({'reset_during_playback_after_seconds': elapsed, 'stale_completion': False})
            return observations
        finally:
            actor.destroy_actor()
    check('completed_playback_repeat_setup_components', run)


def rotation_checks(world, turntable_class, source_record, result, save):
    """Real engine sound fixture, direct tick math, then actual PIE tick observation."""
    import re
    for rpm in (33, 45, 78):
        key = f'rpm{rpm}_playback_rotation'
        actor = None
        camera = None
        observations = []
        try:
            transform = unreal.Transform(location=unreal.Vector(0, 0, 3000))
            statics = unreal.get_default_object(unreal.GameplayStatics)
            scale = unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
            actor = statics.call_method('BeginDeferredActorSpawnFromClass', args=(
                world, turntable_class, transform,
                unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, scale))
            actor = statics.call_method('FinishSpawningActor', args=(actor, transform, scale))
            rendered = '-nullrhi' not in unreal.SystemLibrary.get_command_line().lower()
            if rendered:
                # Unsaved observation camera only; production geometry is untouched.
                pc = unreal.GameplayStatics.get_player_controller(world, 0)
                view_target = pc.get_view_target()
                target = actor.get_actor_location()
                position = target + unreal.Vector(-160, -160, 110)
                view = unreal.Transform(location=position,
                    rotation=unreal.MathLibrary.find_look_at_rotation(position, target))
                camera = statics.call_method('BeginDeferredActorSpawnFromClass', args=(
                    world, unreal.CameraActor.static_class(), view,
                    unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, scale))
                camera = statics.call_method('FinishSpawningActor', args=(camera, view, scale))
                pc.set_view_target_with_blend(camera)
                for _ in range(4):
                    yield
            def capture(label):
                if not rendered:
                    return
                path = Path(os.environ['MVP_RESULT']).with_name(
                    Path(os.environ['MVP_RESULT']).stem+f'-rpm{rpm}-{label}.png')
                unreal.SystemLibrary.execute_console_command(
                    world, 'Shot showui filename="'+str(path)+'" -nosuffix')
                observations.append({'screenshot_requested': str(path), 'stage': label,
                                     'components': component_state(actor)})
            record = actor.get_editor_property('CurrentRecord')
            sound = unreal.load_asset('/Engine/EditorSounds/Notifications/CompileSuccess')
            assert sound
            text = re.sub(r'(Audio_[A-Za-z0-9_]+)=(?:None|"[^"]*")',
                          lambda m: m[1]+'="/Script/Engine.SoundWave\''+sound.get_path_name()+'\'"',
                          source_record.export_text())
            record.import_text(text)
            actor.call_method('SetRecord', args=(record,))
            if rpm == 33:
                for method, alpha in [('OpenLid', 'LidMotionAlpha'),
                                      ('PlaceRecord', 'RecordMotionAlpha'),
                                      ('MoveTonearm', 'TonearmMotionAlpha')]:
                    if method == 'MoveTonearm':
                        actor.call_method('SelectRPM33')
                    actor.call_method(method)
                    deadline = time.monotonic()+8
                    while actor.get_editor_property(alpha) < 0.3:
                        assert time.monotonic() < deadline, 'PIE motion failed to advance'
                        yield
                    progress = actor.get_editor_property(alpha)
                    assert 0.3 <= progress < 1, 'No observable intermediate motion'
                    observations.append({'actual_pie_motion': method, 'alpha': progress,
                                         'components': component_state(actor)})
                    capture(method+'-moving')
                    while actor.get_editor_property(alpha) < 1:
                        assert time.monotonic() < deadline
                        yield
                    capture(method+'-settled')
                    for _ in range(3):
                        yield
                actor.call_method('SetRecord', args=(record,))
            actor.set_actor_tick_enabled(False)
            mesh = actor.get_editor_property('Record')
            def yaw():
                return mesh.get_editor_property('relative_rotation').yaw
            def tick(seconds):
                actor.call_method('ReceiveTick', args=(seconds,))
            initial = yaw()
            tick(0.125)
            assert abs(yaw()-initial) < 0.001, 'Rotation before playback'
            for method in ('OpenLid', 'PlaceRecord', f'SelectRPM{rpm}', 'MoveTonearm', 'PlayRecord'):
                actor.call_method(method)
            actor.call_method('ReceiveTick', args=(1.0,))
            audio = actor.get_editor_property('PlaybackAudio')
            assert audio and audio.is_playing()
            for seconds in (0.125, 0.25):
                before = yaw()
                tick(seconds)
                delta = (yaw()-before) % 360
                expected = rpm * 6 * seconds
                observations.append({'delta_seconds': seconds, 'degrees': delta, 'expected': expected})
                assert abs(delta-expected) < 0.01, observations[-1]
            actor.set_actor_tick_enabled(True)
            before = yaw()
            for _ in range(3):
                yield
            assert abs((yaw()-before+180) % 360-180) > 0.01, 'PIE Tick did not rotate record'
            observations.append({'actual_pie_tick_yaw_before': before, 'after': yaw()})
            capture('playing')
            deadline = time.monotonic()+15
            while not actor.get_editor_property('CompletionSent'):
                assert time.monotonic() < deadline
                yield
            stopped = yaw()
            for _ in range(3):
                yield
            tick(0.25)
            assert abs(yaw()-stopped) < 0.001, 'Rotation continued after completion'
            actor.call_method('SetRecord', args=(source_record,))
            assert abs(yaw()-initial) < 0.001 and not mesh.is_visible()
            capture('reset')
            for _ in range(4):
                yield
            result['isolated'][key] = {'pass': True, 'observations': observations,
                'limit': 'Isolated engine audio fixture and direct ReceiveTick math plus real PIE tick; not natural E2E or authored LP audio.'}
        except Exception:
            result['isolated'][key] = {'pass': False, 'observations': observations,
                                       'error': traceback.format_exc()}
        finally:
            if camera:
                pc.set_view_target_with_blend(view_target)
                camera.destroy_actor()
            if actor:
                audio = actor.get_editor_property('PlaybackAudio')
                if audio:
                    audio.stop()
                actor.destroy_actor()
            save()


def production_audio_replay_checks(world, turntable_class, source_record, result, save):
    """Actual project music reset/replay and fade guard; isolated, not natural E2E."""
    import re
    statics=unreal.get_default_object(unreal.GameplayStatics)
    transform=unreal.Transform(location=unreal.Vector(0,0,3000))
    scaling=unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
    actor=statics.call_method('BeginDeferredActorSpawnFromClass',args=(world,turntable_class,transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,scaling))
    actor=statics.call_method('FinishSpawningActor',args=(actor,transform,scaling))
    observations=[]
    try:
        sound=unreal.load_asset('/Game/RecordShop/Audio/Music/RS001_Best')
        record=actor.get_editor_property('CurrentRecord')
        text=re.sub(r'(Audio_[A-Za-z0-9_]+)=(?:None|"[^"]*")',lambda m:m[1]+'="/Script/Engine.SoundWave\''+sound.get_path_name()+'\'"',source_record.export_text())
        record.import_text(text)
        def music_components():
            # Auto-destroyed audio can leave an expired Python proxy that cannot
            # even be passed to IsValid. Query live UObjects afresh, retaining
            # only scalar evidence across ticks; binding errors still fail.
            return {component.get_path_name(): component.is_playing()
                    for component in unreal.ObjectIterator(unreal.AudioComponent)
                    if component.get_editor_property('sound') == sound}

        for repeat in range(2):
            actor.call_method('SetRecord',args=(record,))
            assert actor.get_editor_property('PlaybackAudio') is None
            before = music_components()
            assert not any(before.values()), ('Previous LP survived reset', before)
            for method in ('OpenLid','PlaceRecord','SelectRPM33','MoveTonearm','PlayRecord'):
                actor.call_method(method)
            assert actor.get_editor_property('PlaybackRequested')
            assert actor.get_editor_property('PlaybackAudio') is None
            deadline=time.monotonic()+4
            while actor.get_editor_property('PlaybackAudio') is None:
                assert time.monotonic()<deadline
                if actor.get_editor_property('TonearmMotionAlpha')<1:
                    assert actor.get_editor_property('TurntableStep')==4
                yield
            audio=actor.get_editor_property('PlaybackAudio')
            assert audio.is_playing() and audio.get_editor_property('sound')==sound
            assert actor.get_editor_property('TonearmMotionAlpha')==1
            assert -0.02<=stylus_contact(actor)['gap_cm']<=0.05
            audio_path = audio.get_path_name()
            actor.call_method('PlayRecord');assert actor.get_editor_property('PlaybackAudio')==audio
            voices = music_components()
            assert [path for path, playing in voices.items() if playing] == [audio_path], ('Overlapping production LP components', voices)
            if repeat==0:
                until=time.monotonic()+1
                while time.monotonic()<until:yield
                actor.call_method('BeginTonearmReturn')
                assert 'FADING_OUT' in str(audio.get_play_state()), str(audio.get_play_state())
            # Do not keep or compare an AudioComponent proxy after completion.
            audio = None
            deadline=time.monotonic()+40
            while not actor.get_editor_property('CompletionSent'):
                assert time.monotonic()<deadline
                yield
            assert actor.get_editor_property('PlaybackAudio') is None
            stopped = music_components()
            assert not any(stopped.values()), ('LP still playing after completion', stopped)
            assert abs(actor.get_editor_property('TonearmPivot').get_editor_property('relative_rotation').yaw)<.01
            observations.append({'repeat':repeat+1,'sound':sound.get_path_name(),'one_component':True,'contact_before_audio':True,'completion':'early fade then physical return' if repeat==0 else 'full natural audio finished callback after reset',
                                 'component_path':audio_path,'before_reset_playback':before,
                                 'during_playback':voices,'after_completion':stopped,
                                 'completed_component':'live and stopped' if audio_path in stopped else 'absent from live components'})
        result['isolated']['production_music_fade_reset_replay']={'pass':True,'observations':observations,'limit':'Isolated direct Turntable commands; all natural recommendation paths are validated separately.'}
    except Exception:
        result['isolated']['production_music_fade_reset_replay']={'pass':False,'observations':observations,'error':traceback.format_exc()}
    finally:
        audio=actor.get_editor_property('PlaybackAudio')
        if audio:audio.stop()
        actor.destroy_actor();save()


def rpm_ui_checks(world, pawn, turntable_class, widget_class, record, check):
    import re
    record.import_text(re.sub(r'(Audio_[A-Za-z0-9_]+)=(?:None|"[^"]*")',r'\1=None',record.export_text()))
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
                click('BTN_Play', 4)
                assert actor.get_editor_property('PlaybackRequested')
                actor.call_method('ReceiveTick', args=(1.0,))
                assert actor.get_editor_property('TurntableStep') == 5
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


def enhanced_input_checks(world, flow, pawn, targets, result, save):
    """Inject IA_Interact into the real local player; never call Interact/TryInteract.

    Paired near/away cases exercise actual collision and interface dispatch. Pawn
    teleporting supplies repeatable geometry, not natural navigation evidence.
    """
    key = 'synthetic_enhanced_input_sphere_trace_interface'
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
        result['enhanced_input_mapping'] = {'action': action.get_path_name(), 'active_keys': mapped_keys}
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


OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'isolated':{},'compiles':{},'provenance':'direct diagnostic calls, button delegates, transient unsaved observer; not E2E'}
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';TT='/Game/RecordShop/Interaction/Actors/BP_Turntable';SHELF='/Game/RecordShop/Interaction/Actors/BP_RecordShelf';DM='/Game/DialogueManager'
DU='/Game/RecordShop/UI/Dialogue/WBP_Dialogue';SU='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect';TU='/Game/RecordShop/UI/Turntable/WBP_Turntable';RU='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
def save():OUT.write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf-8')
def check(name,fn):
 try:R['isolated'][name]={'pass':True,'observations':fn()}
 except Exception:R['isolated'][name]={'pass':False,'error':traceback.format_exc()}
 save()
def widgets(path):return list(unreal.WidgetLibrary.get_all_widgets_of_class(world,cls(path),True))
def click(w,name):w.get_editor_property(name).get_editor_property('on_clicked').broadcast()
def interact(a):a.call_method('Interact',args=(pawn,))
def count_modals():return {p:len(widgets(p)) for p in [DU,SU,TU,RU]}

save()
import faulthandler
_fault=open(OUT.with_suffix('.trace.txt'),'w')
faulthandler.enable(file=_fault)
# An in-memory observer consumes the actual dispatchers. No package is saved.
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_MVPObserver','/Game/RecordShop/Dev/IntegrationProbe',unreal.Blueprint,factory)
pg=evgraph(probe)
for name in ['Completions','Scores','LastScore']:assert pg.add_member_variable(name,L.get_basic_type_by_name('int'))
assert L.compile_blueprint(probe)
for event_name,member_name in [('ReceiveCompletion','Completions'),('ReceiveScore','Scores')]:
 if event_name=='ReceiveScore':event=signature_event(probe,event_name,[('RawScore',L.get_basic_type_by_name('int'))])
 else:event=pg.add_custom_event_node(event_name)
 pg=evgraph(probe)
 increment=pg.add_macro_node('/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:IncrementInt')
 assert increment
 link(get(pg,member_name),pin(increment,'Value'));link(event.find_then_pin(),pin(increment,' '))
 if event_name=='ReceiveScore':
  last=setv(pg,'LastScore');link(pin(event,'RawScore',True),pin(last,'LastScore'));link(pin(increment,'  ',True),last.find_execute_pin());score_event=event
 else:completion_event=event
bind_event=signature_event(probe,'Observe', [('Turntable',L.get_object_reference_type(cls(TT))),('Manager',L.get_object_reference_type(cls(DM)))])
pg=evgraph(probe)
p=bind_event.find_then_pin()
for obj,dispatcher,event,path in [('Turntable','OnTurntableCompleted',completion_event,TT),('Manager','OnLPScoreEvaluated',score_event,DM)]:
 bind=action(pg,'BindEventto'+dispatcher,[pin(bind_event,obj,True)],cls(path));link(pin(event,'OutputDelegate',True),pin(bind,'Delegate'));link(p,bind.find_execute_pin());p=bind.find_then_pin()
fixture_profile=function(probe,'SetLiveProfileFixture')
customer_path='/Game/RecordShop/Characters/Customers/Common/BP_Customer'
customer_pin=fixture_profile.add_graph_input_parameter('Customer',L.get_object_reference_type(cls(customer_path)))
flow_pin=fixture_profile.add_graph_input_parameter('Flow',L.get_object_reference_type(cls(FLOW)))
profile_pin=fixture_profile.add_graph_input_parameter('Profile',L.get_member_variable_type(unreal.load_asset(DM),'CurrentCustomer'))
setter=fixture_profile.add_set_member_variable_node('CustomerProfile',customer_path+'.BP_Customer_C');link(customer_pin,pin(setter,'self'));link(profile_pin,pin(setter,'CustomerProfile'));link(fixture_profile.find_graph_entry_pin(),setter.find_execute_pin())
reset=fixture_profile.add_set_member_variable_node('DialogueStartedForCustomer',FLOW+'.BP_GameFlowManager_C');link(flow_pin,pin(reset,'self'));val(pin(reset,'DialogueStartedForCustomer'),'false');link(setter.find_then_pin(),reset.find_execute_pin())
score_profile=function(probe,'SetScoringProfileFixture')
manager_pin=score_profile.add_graph_input_parameter('Manager',L.get_object_reference_type(cls(DM)))
profile_pin=score_profile.add_graph_input_parameter('Profile',L.get_member_variable_type(unreal.load_asset(DM),'CurrentCustomer'))
mood_pin=score_profile.add_graph_input_parameter('Mood',L.get_basic_type_by_name('string'))
setter=score_profile.add_set_member_variable_node('CurrentCustomer',DM+'.DialogueManager_C')
link(manager_pin,pin(setter,'self'));link(profile_pin,pin(setter,'CurrentCustomer'));link(score_profile.find_graph_entry_pin(),setter.find_execute_pin())
setter_mood=score_profile.add_set_member_variable_node('CurrentMood',DM+'.DialogueManager_C')
link(manager_pin,pin(setter_mood,'self'));link(mood_pin,pin(setter_mood,'CurrentMood'));link(setter.find_then_pin(),setter_mood.find_execute_pin())
assert L.compile_blueprint(probe)
observer=unreal.get_default_object(probe.generated_class())
observe_method=str(bind_event.get_node_title())
save()
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
for path in [FLOW,TT,SHELF,DM,DU,SU,TU,RU]:R['compiles'][path]=L.compile_blueprint(unreal.load_asset(path))
assert all(R['compiles'].values())
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();start=time.monotonic();phase={'gen':None,'end':None}

def run():
 global world,flow,pawn,pc
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_all_actors_of_class(world,cls(FLOW))[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0)
 while not widgets(DU):
  assert time.monotonic()-start<70
  yield
 manager=flow.get_editor_property('DialogueManagerRef');tt=flow.get_editor_property('TurntableRef');shelves=list(unreal.GameplayStatics.get_all_actors_of_class(world,cls(SHELF)))
 observer.call_method(observe_method,args=(tt,manager))
 def dialogue_guards():
  original=widgets(DU)[0]
  for _ in range(3):flow.call_method('HandleCustomerReadyForDialogue')
  flow.call_method('FinishResult');assert flow.get_editor_property('ActiveCustomer');assert not flow.get_editor_property('ResultSubmitted')
  interact(tt);interact(shelves[0]);assert widgets(DU)==[original];assert not widgets(SU) and not widgets(TU)
  assert len(flow.get_components_by_class(cls(DM)))==1

  for _ in range(5):click(original,'Next')
  assert not widgets(DU);assert original.get_editor_property('DialogueManagerRef') is None
  assert int(flow.get_editor_property('CurrentState').value)==2
  manager.call_method('ShowNextLine');assert int(flow.get_editor_property('CurrentState').value)==2
  return {'one_manager':True,'repeated_ready':3,'premature_finish_rejected':True,'late_finish_idempotent':True}
 check('dialogue_and_premature_result_guards',dialogue_guards)
 def live_profile():
  import re
  customer=flow.get_editor_property('ActiveCustomer');profile=customer.get_editor_property('CustomerProfile');original=profile.export_text()
  fixture=original
  for name,value in [('CustomerID','probe-customer'),('Mood','probe-mood'),('Personality','probe-personality'),('MusicPreference','probe-preference')]:
   fixture=re.sub(r'('+name+r'_[A-Za-z0-9_]+)=\"[^\"]*\"',lambda m:m[1]+'="'+value+'"',fixture)
  assert fixture!=original
  try:
   profile.import_text(fixture);observer.call_method('SetLiveProfileFixture',args=(customer,flow,profile));flow.call_method('HandleCustomerReadyForDialogue')
   assert manager.get_editor_property('CurrentCustomer').export_text()==customer.get_editor_property('CustomerProfile').export_text()
   assert 'probe-customer' in manager.get_editor_property('CurrentCustomer').export_text();assert manager.get_editor_property('CurrentMood')=='probe-mood'
   assert len(manager.get_editor_property('DialogueList'))==0 and not widgets(DU)
  finally:
   profile.import_text(original);observer.call_method('SetLiveProfileFixture',args=(customer,flow,profile));flow.call_method('HandleCustomerReadyForDialogue')
   for _ in range(5):
    if widgets(DU):click(widgets(DU)[0],'Next')
  assert manager.get_editor_property('CurrentMood')=='Quiet'
  return {'typed_active_customer_profile_copied':True,'mood_from_profile':True,'unmatched_mood_finishes_normally':True,'fixture':'in-memory live actor profile; restored; no table edits; diagnostic Ready invocation only'}
 check('live_customer_profile_and_mood_mapping',live_profile)
 def score_contract():
  records=[]
  for matches in itertools.product([False,True],repeat=3):
   args=tuple(value if match else 'nonmatching-isolated-fixture' for value,match in zip(('Quiet','Jazz','Traditional'),matches))
   score=manager.call_method('CalculateLPScore',args=args);assert score==sum(matches)
   before=observer.get_editor_property('Scores');manager.call_method('EvaluateLP',args=(*args,['fixture-only']))
   assert observer.get_editor_property('Scores')==before+1;assert observer.get_editor_property('LastScore')==score
   assert manager.get_editor_property('MaxScore')==0
   records.append({'matches':matches,'score':score,'output':observer.get_editor_property('LastScore')})
  manager.call_method('EvaluateLP',args=('x','x','x',[]));assert manager.get_editor_property('MaxScore')==0
  return {'cases':records,'maximum_assignment_repaired':True,'limitation':'AvailableLPs remains unused by the existing scaffold; MaxScore is not used for presentation. Three explicit profile comparisons produce 0-3.'}
 check('raw_score_output_all_eight_combinations',score_contract)
 def selection_guards():
  observed=[]
  for i in range(3):
   interact(shelves[0]);interact(shelves[0]);interact(shelves[1]);interact(tt)
   assert len(widgets(SU))==1 and not widgets(TU)
   click(widgets(SU)[0],f'BTN_LP0{i+1}');assert not widgets(SU);assert not pc.get_editor_property('show_mouse_cursor');assert tt.get_editor_property('HasRecord')
   record=tt.get_editor_property('CurrentRecord').export_text();assert f'RS00{i+1}' in record
   assert flow.get_editor_property('RawScoreAvailable') and flow.get_editor_property('RawRecommendationScore')==[3,2,0][i]
   observed.append(record)
  return observed
 check('selection_ownership_all_records_and_modals',selection_guards)
 def optional_score():
  import re
  assert flow.get_editor_property('RawScoreAvailable')
  flow.call_method('EvaluateRecordScore',args=('','Jazz','Traditional'))
  assert not flow.get_editor_property('RawScoreAvailable'), 'Blank record inputs must remain unavailable'
  profile=manager.get_editor_property('CurrentCustomer');original=profile.export_text()
  original_mood=manager.get_editor_property('CurrentMood')
  fixture=original
  for name,value in [('Personality','fixture-personality'),('MusicPreference','fixture-preference')]:
   fixture=re.sub(r'('+name+r'_[A-Za-z0-9_]+)=\"[^\"]*\"',lambda m:m[1]+'="'+value+'"',fixture)
  try:
   blank=original
   for key in ('Personality','MusicPreference'):
    blank=re.sub(r'('+key+r'_[A-Za-z0-9_]+)=\"[^\"]*\"',lambda match:match[1]+'=""',blank)
   profile.import_text(blank);observer.call_method('SetScoringProfileFixture',args=(manager,profile,'Quiet'))
   flow.call_method('EvaluateRecordScore',args=('Quiet','Jazz','Traditional'))
   assert not flow.get_editor_property('RawScoreAvailable'), 'Blank customer inputs must remain unavailable'
   profile.import_text(fixture);observer.call_method('SetScoringProfileFixture',args=(manager,profile,'fixture-mood'))
   observations=[]
   for inputs,expected in [(('fixture-mood','fixture-preference','fixture-personality'),3),
                           (('other','other','other'),0),
                           (('fixture-mood','other','other'),1)]:
    flow.call_method('EvaluateRecordScore',args=inputs)
    assert flow.get_editor_property('RawScoreAvailable')
    assert flow.get_editor_property('RawRecommendationScore')==expected
    observations.append({'inputs':inputs,'raw_score':expected})
   flow.call_method('EvaluateRecordScore',args=('','fixture-preference','fixture-personality'))
   assert not flow.get_editor_property('RawScoreAvailable')
   manager.call_method('EvaluateLP',args=('fixture-mood','fixture-preference','fixture-personality',[]))
   assert not flow.get_editor_property('RawScoreAvailable'), 'Unsolicited output must not certify missing inputs'
   flow.call_method('EvaluateRecordScore',args=('fixture-mood','other','other'))
   flow.call_method('HandleRecordSelected',args=(tt.get_editor_property('CurrentRecord'),))
   assert flow.get_editor_property('RawScoreAvailable') and flow.get_editor_property('RawRecommendationScore')==0, 'Record reselection did not recompute its own score'
   flow.call_method('EvaluateRecordScore',args=('fixture-mood','other','other'))
   return {'cases':observations,'limit':'In-memory explicit scoring/profile fixtures; no authored mapping or qualitative meaning.'}
  finally:
   profile.import_text(original);observer.call_method('SetScoringProfileFixture',args=(manager,profile,original_mood))
 check('optional_raw_score_availability_and_propagation',optional_score)
 presentation_motion_checks(world,cls(TT),cls(TU),pawn,tt.get_editor_property('CurrentRecord'),check)
 owner_placement_checks(world,cls(TT),pawn,tt.get_editor_property('CurrentRecord'),check)
 rpm_ui_checks(world,pawn,cls(TT),cls(TU),tt.get_editor_property('CurrentRecord'),check)
 repeat_setup_checks(world,cls(TT),tt.get_editor_property('CurrentRecord'),check)
 def completion_guards():
  import re
  silent=tt.get_editor_property('CurrentRecord')
  silent.import_text(re.sub(r'(Audio_[A-Za-z0-9_]+)=(?:None|"[^"]*")',r'\1=None',silent.export_text()))
  tt.call_method('SetRecord',args=(silent,))
  interact(tt);interact(tt);interact(shelves[0]);assert len(widgets(TU))==1 and not widgets(SU)
  w=widgets(TU)[0];initial=observer.get_editor_property('Completions')
  for name in ['BTN_Play','BTN_MoveTonearm','BTN_PlaceRecord','BTN_RPM78']:click(w,name)
  assert tt.get_editor_property('TurntableStep')==0;assert observer.get_editor_property('Completions')==initial
  for name in ['BTN_OpenLid','BTN_PlaceRecord','BTN_RPM33','BTN_MoveTonearm','BTN_Play']:click(w,name)
  tt.call_method('ReceiveTick',args=(1.0,));tt.call_method('ReceiveTick',args=(1.5,));tt.call_method('ReceiveTick',args=(1.2,))
  assert tt.get_editor_property('CompletionSent');assert observer.get_editor_property('Completions')==initial+1
  assert w.get_editor_property('TurntableRef') is None
  result=widgets(RU)[0]
  for _ in range(3):tt.call_method('PlayRecord');tt.call_method('CompletePlayback');flow.call_method('HandleTurntableCompleted')
  assert widgets(RU)==[result];assert observer.get_editor_property('Completions')==initial+1
  interact(tt);interact(shelves[0]);assert not widgets(TU) and not widgets(SU)
  assert pc.get_editor_property('show_mouse_cursor')
  assert str(result.get_editor_property('RecordID').get_text())=='RS003'
  assert str(result.get_editor_property('ScoreStatus').get_text()).startswith('아쉬운 선택')
  flow.call_method('EvaluateRecordScore',args=('late','late','late'))
  manager.call_method('EvaluateLP',args=('late','late','late',[]))
  assert flow.get_editor_property('RawScoreAvailable') and flow.get_editor_property('RawRecommendationScore')==1
  return {'one_completion':True,'one_result':True,'cross_modal_blocked':True}
 check('completion_result_and_duplicate_guards',completion_guards)
 # SetInputMode queues owning-player Slate operations until the frame finishes.
 # Observe focus on subsequent frames without assigning any test-side focus.
 for _ in range(4):yield
 if '-nullrhi' not in unreal.SystemLibrary.get_command_line().lower():
  screenshot=OUT.with_name(OUT.stem+'-raw-score-result.png')
  unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(screenshot)+'" -nosuffix')
  R['raw_score_screenshot_requested']=str(screenshot)
  for _ in range(3):yield
 def focused_continue():
  result=widgets(RU)[0]
  assert result.get_editor_property('Continue').has_keyboard_focus(), 'Result default keyboard focus'
  assert result.get_editor_property('Continue').has_user_focus(pc), 'Result owning player focus'
  click(result,'Continue');click(result,'Continue');flow.call_method('FinishResult')
  assert flow.get_editor_property('ResultWidgetRef') is None;assert not widgets(RU);assert not pc.get_editor_property('show_mouse_cursor')
  return {'repeat_continue_guarded':True,'production_continue_focus':True,'test_focus_correction':False}
 check('result_default_focus_and_repeat_continue',focused_continue)
 while flow.get_editor_property('ActiveCustomer'):
  assert time.monotonic()-start<100,'Customer exit timeout'
  yield
 def cleanup():
  assert not flow.get_editor_property('RawScoreAvailable')
  assert flow.get_editor_property('RawRecommendationScore')==0
  assert int(flow.get_editor_property('CurrentState').value)==0;assert not any(count_modals().values());assert not pc.get_editor_property('show_mouse_cursor')
  assert flow.get_editor_property('DialogueWidgetRef') is None and flow.get_editor_property('ResultWidgetRef') is None
  flow.call_method('HandleCustomerExited');flow.call_method('CloseRecordShopInteractionModals')
  assert not any(count_modals().values())
  return {'active_customer':None,'modals':count_modals(),'state':'Explore'}
 check('actual_exit_and_repeated_cleanup',cleanup)
 yield from enhanced_input_checks(world,flow,pawn,[(shelves[0],cls(SU)),(tt,cls(TU))],R,save)
 interaction=pawn.call_method('AddComponentByClass',args=(unreal.WidgetInteractionComponent.static_class(),False,unreal.Transform(),False))
 interaction.set_component_tick_enabled(False);interaction.activate(True)
 try:
  escape=unreal.Key();escape.import_text('Escape');other_key=unreal.Key();other_key.import_text('F10');observed=[]
  for actor,path in [(shelves[0],SU),(tt,TU)]:
   for repeat in range(2):
    interact(actor);w=widgets(path)[0]
    yield
    interaction.set_focus(w)
    yield
    interaction.press_and_release_key(other_key);assert widgets(path)==[w]
    assert interaction.press_and_release_key(escape)
    yield
    assert not widgets(path);assert not pc.get_editor_property('show_mouse_cursor')
    if path==TU:
     assert w.get_editor_property('TurntableRef') is None
     deadline=time.monotonic()+0.3
     while time.monotonic()<deadline:yield
     assert pc.get_view_target()==pawn, 'Escape close did not restore the player camera'
    observed.append({'widget':path,'repeat':repeat+1,'closed_by':'synthetic Slate Escape','cursor':False})
  R['isolated']['escape_reopen_and_destroy_reference_cleanup']={'pass':True,'observations':observed};save()
 except Exception:R['isolated']['escape_reopen_and_destroy_reference_cleanup']={'pass':False,'error':traceback.format_exc()};save()
 finally:interaction.destroy_component(pawn)
 def no_record():
  statics=unreal.get_default_object(unreal.GameplayStatics);transform=unreal.Transform(location=unreal.Vector(0,0,3000));scale=unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
  a=statics.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls(TT),transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,scale));a=statics.call_method('FinishSpawningActor',args=(a,transform,scale))
  try:
   for name in ['OpenLid','PlaceRecord','SelectRPM33','MoveTonearm','PlayRecord','CompletePlayback']:a.call_method(name)
   assert a.get_editor_property('TurntableStep')==4;assert not a.get_editor_property('CompletionSent')
   return {'step':4,'completion':False}
  finally:a.destroy_actor()
 check('no_record_rejects_play_and_completion',no_record)
 if '-nosound' not in unreal.SystemLibrary.get_command_line().lower():
  yield from rotation_checks(world,cls(TT),tt.get_editor_property('CurrentRecord'),R,save)
  # Isolated callback plumbing with an existing ENGINE notification sound.
  # This is neither authored LP audio nor part of natural customer-cycle evidence.
  statics=unreal.get_default_object(unreal.GameplayStatics);transform=unreal.Transform(location=unreal.Vector(0,0,3000));scale=unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT
  a=statics.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls(TT),transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,scale));a=statics.call_method('FinishSpawningActor',args=(a,transform,scale))
  try:
   record=tt.get_editor_property('CurrentRecord');original=record.export_text()
   sound=unreal.load_asset('/Engine/EditorSounds/Notifications/CompileSuccess');assert sound
   import re
   edited=re.sub(r'(Audio_[A-Za-z0-9_]+)=(?:None|"[^"]*")',lambda m:m[1]+'="/Script/Engine.SoundWave\''+sound.get_path_name()+'\'"',original)
   assert edited!=original;record.import_text(edited)
   a.call_method('SetRecord',args=(record,));observer.call_method(observe_method,args=(a,manager))
   before=observer.get_editor_property('Completions')
   for method in ['OpenLid','PlaceRecord','SelectRPM33','MoveTonearm','PlayRecord']:a.call_method(method)
   a.call_method('ReceiveTick',args=(1.0,))
   audio=a.get_editor_property('PlaybackAudio');assert audio and audio.is_playing(),'Audio device did not start the diagnostic sound'
   assert not a.get_editor_property('CompletionSent');assert a.get_editor_property('TurntableStep')==5
   # The owned record must remain unchanged until real audio ends.
   other=tt.get_editor_property('CurrentRecord');other.import_text(original.replace('RS003','replacement-fixture'))
   before_components=component_state(a)
   a.call_method('SetRecord',args=(other,));assert 'replacement-fixture' not in a.get_editor_property('CurrentRecord').export_text()
   assert component_state(a)==before_components, 'Rejected replacement reset active components'
   a.call_method('PlayRecord');assert a.get_editor_property('PlaybackAudio')==audio
   deadline=time.monotonic()+15
   while not a.get_editor_property('CompletionSent'):
    assert time.monotonic()<deadline,'Actual OnAudioFinished did not complete'
    yield
   assert observer.get_editor_property('Completions')==before+1;assert a.get_editor_property('PlaybackAudio') is None
   a.call_method('CompletePlayback');assert observer.get_editor_property('Completions')==before+1
   R['isolated']['real_audio_component_callback']={'pass':True,'source':sound.get_path_name(),'completion_delta':1,'replacement_during_playback_rejected':True,'limit':'engine notification fixture only; no authored LP asset and no audible-quality claim'};save()
  except Exception:R['isolated']['real_audio_component_callback']={'pass':False,'error':traceback.format_exc()};save()
  finally:a.destroy_actor()
  yield from production_audio_replay_checks(world,cls(TT),tt.get_editor_property('CurrentRecord'),R,save)
 R['complete']=True;R['pass']=all(x.get('pass',True) for x in R['isolated'].values());save()

def tick(delta):
 if phase.get('busy'):return
 phase['busy']=True
 try:
  if phase['end'] is not None:
   if time.monotonic()-phase['end']>3:
    unreal.unregister_slate_post_tick_callback(handle)
    # The Python executor must release its notification before engine shutdown.
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if phase['gen'] is None:phase['gen']=run()
  assert time.monotonic()-start<240
  next(phase['gen'])
 except StopIteration:level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
