"""Create the first-pass RecordShop greybox in Unreal Editor.

Run this file from Unreal Editor's Python tooling. It creates only the
requested greybox actors and never overwrites an existing target map.
"""

import unreal


MAP_ASSET_PATH = "/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox"
MAP_DIRECTORY = "/Game/RecordShop/Maps/Greybox"

ENGINE_CUBE_PATH = "/Engine/BasicShapes/Cube"
ENGINE_CYLINDER_PATH = "/Engine/BasicShapes/Cylinder"

_LEVEL_SUBSYSTEM = None
_ACTOR_SUBSYSTEM = None
_MESH_CACHE = {}


def _log(message):
    unreal.log("[RecordShopGreybox] {0}".format(message))


def _log_warning(message):
    unreal.log_warning("[RecordShopGreybox] {0}".format(message))


def _log_error(message):
    unreal.log_error("[RecordShopGreybox] {0}".format(message))


def _get_editor_subsystem(subsystem_class, display_name):
    if not hasattr(unreal, "get_editor_subsystem"):
        raise RuntimeError("unreal.get_editor_subsystem() is unavailable")
    if not hasattr(unreal, subsystem_class.__name__):
        raise RuntimeError("{0} is unavailable".format(display_name))

    subsystem = unreal.get_editor_subsystem(subsystem_class)
    if subsystem is None:
        raise RuntimeError("Could not obtain {0}".format(display_name))
    return subsystem


def _get_asset_subsystem():
    if hasattr(unreal, "EditorAssetSubsystem"):
        return _get_editor_subsystem(unreal.EditorAssetSubsystem, "EditorAssetSubsystem")
    return None


def _target_map_exists():
    """Return True on an existing map or an uncertain query (fail closed)."""
    try:
        asset_subsystem = _get_asset_subsystem()
        if asset_subsystem is not None and hasattr(asset_subsystem, "does_asset_exist"):
            return bool(asset_subsystem.does_asset_exist(MAP_ASSET_PATH))

        # Compatibility fallback for an installation that does not expose the
        # UE5 EditorAssetSubsystem method.
        if hasattr(unreal, "EditorAssetLibrary"):
            return bool(unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET_PATH))
        raise RuntimeError("No supported asset-existence API is available")
    except Exception as error:
        _log_error(
            "Could not verify {0}: {1}. Stopping to avoid an unsafe overwrite.".format(
                MAP_ASSET_PATH, error
            )
        )
        return True


def _ensure_map_directory():
    asset_subsystem = _get_asset_subsystem()
    if asset_subsystem is None or not hasattr(asset_subsystem, "make_directory"):
        _log_warning(
            "EditorAssetSubsystem.make_directory() is unavailable; "
            "continuing and letting new_level() resolve the target folder."
        )
        return

    result = asset_subsystem.make_directory(MAP_DIRECTORY)
    if result is False:
        _log_warning(
            "Could not create {0}; it may already exist. Continuing to new_level().".format(
                MAP_DIRECTORY
            )
        )


def _load_mesh(path):
    if path not in _MESH_CACHE:
        mesh = unreal.load_asset(path)
        if mesh is None:
            raise RuntimeError("Could not load engine mesh: {0}".format(path))
        _MESH_CACHE[path] = mesh
    return _MESH_CACHE[path]


def _set_actor_folder(actor, folder):
    """Apply an Outliner folder when the installed UE5 API supports it."""
    if not folder:
        return

    try:
        if hasattr(actor, "set_folder_path"):
            folder_value = unreal.Name(folder) if hasattr(unreal, "Name") else folder
            actor.set_folder_path(folder_value)
        elif hasattr(actor, "set_editor_property"):
            actor.set_editor_property("folder_path", folder)
    except Exception as error:
        _log_warning(
            "Could not assign Outliner folder {0} to {1}; continuing: {2}".format(
                folder, actor.get_actor_label(), error
            )
        )


def _spawn_actor(actor_class, location, rotation=None):
    if rotation is None:
        rotation = unreal.Rotator(0.0, 0.0, 0.0)

    actor = _ACTOR_SUBSYSTEM.spawn_actor_from_class(
        actor_class, unreal.Vector(*location), rotation
    )
    if actor is None:
        raise RuntimeError("EditorActorSubsystem failed to spawn {0}".format(actor_class))
    return actor


def _finish_actor(actor, label, folder):
    actor.set_actor_label(label)
    _set_actor_folder(actor, folder)
    return actor


def spawn_cube(label, location, dimensions, folder=None):
    """Spawn a 100 cm Unreal Cube scaled to the requested dimensions."""
    actor = _spawn_actor(unreal.StaticMeshActor, location)
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    component.set_editor_property("static_mesh", _load_mesh(ENGINE_CUBE_PATH))
    actor.set_actor_scale3d(
        unreal.Vector(
            dimensions[0] / 100.0,
            dimensions[1] / 100.0,
            dimensions[2] / 100.0,
        )
    )
    return _finish_actor(actor, label, folder)


def spawn_cylinder(label, location, diameter, height, folder=None):
    """Spawn a 100 cm Unreal Cylinder as a simple placeholder."""
    actor = _spawn_actor(unreal.StaticMeshActor, location)
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    component.set_editor_property("static_mesh", _load_mesh(ENGINE_CYLINDER_PATH))
    actor.set_actor_scale3d(
        unreal.Vector(diameter / 100.0, diameter / 100.0, height / 100.0)
    )
    return _finish_actor(actor, label, folder)


def _player_start_exists():
    for actor in _ACTOR_SUBSYSTEM.get_all_level_actors():
        if actor is not None and actor.is_a(unreal.PlayerStart):
            return True
    return False


def _spawn_player_start_if_needed():
    if _player_start_exists():
        _log("A PlayerStart already exists; no additional PlayerStart was created.")
        return None

    player_start = _spawn_actor(
        unreal.PlayerStart,
        (0.0, -500.0, 100.0),
        unreal.Rotator(0.0, 90.0, 0.0),
    )
    return _finish_actor(player_start, "PlayerStart_Greybox", "Greybox/Gameplay")


def _build_room():
    spawn_cube("GB_Floor", (0.0, 0.0, -10.0), (900.0, 1200.0, 20.0), "Greybox/Architecture")
    spawn_cube("GB_Wall_Left", (-460.0, 0.0, 160.0), (20.0, 1200.0, 320.0), "Greybox/Architecture")
    spawn_cube("GB_Wall_Right", (460.0, 0.0, 160.0), (20.0, 1200.0, 320.0), "Greybox/Architecture")
    spawn_cube("GB_Wall_Back", (0.0, 610.0, 160.0), (920.0, 20.0, 320.0), "Greybox/Architecture")
    spawn_cube("GB_Wall_Front_L", (-265.0, -610.0, 160.0), (370.0, 20.0, 320.0), "Greybox/Architecture")
    spawn_cube("GB_Wall_Front_R", (265.0, -610.0, 160.0), (370.0, 20.0, 320.0), "Greybox/Architecture")


def _build_listening_bar():
    spawn_cube("GB_BarCounter", (100.0, 400.0, 52.5), (450.0, 75.0, 105.0), "Greybox/ListeningBar")
    spawn_cube("GB_Turntable", (80.0, 400.0, 111.0), (45.0, 40.0, 12.0), "Greybox/ListeningBar")
    spawn_cube("GB_Speaker_L", (-90.0, 400.0, 135.0), (35.0, 30.0, 60.0), "Greybox/ListeningBar")
    spawn_cube("GB_Speaker_R", (270.0, 400.0, 135.0), (35.0, 30.0, 60.0), "Greybox/ListeningBar")
    spawn_cylinder("GB_CustomerSeat_01", (80.0, 290.0, 60.0), 60.0, 120.0, "Greybox/ListeningBar")


def _build_record_shelves():
    shelf_dimensions = (40.0, 120.0, 180.0)
    spawn_cube("GB_RecordShelf_01", (-420.0, -250.0, 90.0), shelf_dimensions, "Greybox/Records")
    spawn_cube("GB_RecordShelf_02", (-420.0, 0.0, 90.0), shelf_dimensions, "Greybox/Records")
    spawn_cube("GB_RecordShelf_03", (-420.0, 250.0, 90.0), shelf_dimensions, "Greybox/Records")


def _build_cafe_zone():
    spawn_cube("GB_CafeCounter", (280.0, -300.0, 50.0), (250.0, 70.0, 100.0), "Greybox/Cafe")
    spawn_cube("GB_CoffeeMachine", (280.0, -300.0, 125.0), (45.0, 40.0, 50.0), "Greybox/Cafe")


def build_greybox():
    _build_room()
    _build_listening_bar()
    _build_record_shelves()
    _build_cafe_zone()
    _spawn_player_start_if_needed()


def _save_current_level():
    result = _LEVEL_SUBSYSTEM.save_current_level()
    if result is False:
        raise RuntimeError("LevelEditorSubsystem.save_current_level() failed")


def main():
    _log("Checking target map: {0}".format(MAP_ASSET_PATH))
    if _target_map_exists():
        _log(
            "Target map already exists at {0}; exiting without overwriting it.".format(
                MAP_ASSET_PATH
            )
        )
        return

    global _LEVEL_SUBSYSTEM, _ACTOR_SUBSYSTEM
    _LEVEL_SUBSYSTEM = _get_editor_subsystem(unreal.LevelEditorSubsystem, "LevelEditorSubsystem")
    _ACTOR_SUBSYSTEM = _get_editor_subsystem(unreal.EditorActorSubsystem, "EditorActorSubsystem")
    level_created = False

    try:
        _ensure_map_directory()
        _log(
            "LevelEditorSubsystem.new_level() will close the current persistent "
            "level without saving it. Save any current work before continuing."
        )
        new_level_result = _LEVEL_SUBSYSTEM.new_level(MAP_ASSET_PATH)
        if new_level_result is False:
            raise RuntimeError("LevelEditorSubsystem.new_level() failed")
        level_created = True

        build_greybox()
        _save_current_level()
    except Exception as error:
        if level_created:
            _log_error(
                "Greybox generation failed after new_level(); the new map may now "
                "exist in a partially generated state: {0}".format(error)
            )
            _log_error(
                "Inspect the generated map and delete it manually in Unreal Editor "
                "before retrying. No automatic deletion or rollback is attempted."
            )
        else:
            _log_error("Greybox generation stopped before a new level was created: {0}".format(error))
        raise

    _log("Created and saved {0}.".format(MAP_ASSET_PATH))


if __name__ == "__main__":
    main()
