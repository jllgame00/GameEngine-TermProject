"""Read-only production ownership/persistence/intro inventory. Run in Editor."""
import json, os, traceback
from pathlib import Path
import unreal
R = {'complete': False, 'pass': False}
try:
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    R['candidates'] = []
    for data in registry.get_assets_by_path('/Game', True):
        name = str(data.package_name)
        kind = str(data.asset_class_path.asset_name)
        if any(s in name.lower() for s in ('intro', 'tutorial', 'prologue', 'savegame', 'gameinstance', 'gamemode', 'controller', 'interaction')):
            R['candidates'].append({'path': name, 'kind': kind})
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    R['scene'] = [{'label': a.get_actor_label(), 'class': a.get_class().get_path_name()} for a in actors if any(s in a.get_class().get_name() for s in ('FlowManager', 'Shelf', 'Turntable', 'WorldSettings', 'PlayerStart', 'Customer'))]
    settings = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_world_settings()
    R['map_game_mode_override'] = str(settings.get_editor_property('default_game_mode'))
    mode = unreal.get_default_object(unreal.load_class(None, '/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode.BP_ThirdPersonGameMode_C'))
    R['game_mode'] = {key: str(mode.get_editor_property(key)) for key in ('default_pawn_class', 'player_controller_class')}
    R['api'] = {name: str(getattr(unreal.BlueprintGraphEditor, name).__doc__) for name in dir(unreal.BlueprintGraphEditor) if any(s in name for s in ('remove', 'event', 'variable'))}
    R['graph_methods'] = {name: str(getattr(unreal.BlueprintGraphEditor, name).__doc__) for name in dir(unreal.BlueprintGraphEditor) if any(k in name for k in ('cast','delegate','widget'))}
    R['blueprint_methods'] = {name: str(getattr(unreal.BlueprintEditorLibrary, name).__doc__) for name in dir(unreal.BlueprintEditorLibrary) if 'remove' in name}
    R['pass'] = True
except Exception:
    R['fatal'] = traceback.format_exc()
R['complete'] = True
Path(os.environ['MVP_RESULT']).write_text(json.dumps(R, indent=2, ensure_ascii=False), encoding='utf-8')
