"""Add temporary test lighting to the existing RecordShop greybox map."""

import unreal


TARGET_MAP = "/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox"
LIGHTING_FOLDER = "Greybox/Lighting/Test"
DIRECTIONAL_INTENSITY = 10.0
SKY_INTENSITY = 1.0

_LEVEL_SUBSYSTEM = None
_ACTOR_SUBSYSTEM = None
_EXISTING_LABELS = set()


def _log(message):
    unreal.log("[RecordShopLighting] {0}".format(message))


def _warning(message):
    unreal.log_warning("[RecordShopLighting] {0}".format(message))


def _error(message):
    unreal.log_error("[RecordShopLighting] {0}".format(message))


def _asset_exists(asset_path):
    try:
        asset_subsystem_class = getattr(unreal, "EditorAssetSubsystem", None)
        if asset_subsystem_class is not None:
            asset_subsystem = unreal.get_editor_subsystem(asset_subsystem_class)
            if asset_subsystem is not None:
                return bool(asset_subsystem.does_asset_exist(asset_path))
    except Exception as exc:
        _warning("EditorAssetSubsystem existence check failed: {0}".format(exc))

    try:
        asset_library = getattr(unreal, "EditorAssetLibrary", None)
        if asset_library is not None:
            return bool(asset_library.does_asset_exist(asset_path))
    except Exception as exc:
        _error("Fallback asset existence check failed for {0}: {1}".format(asset_path, exc))
        return False

    _error("No supported asset existence API is available for {0}.".format(asset_path))
    return False


def _set_folder(actor):
    try:
        set_folder_path = getattr(actor, "set_folder_path", None)
        if callable(set_folder_path):
            name_type = getattr(unreal, "Name", None)
            set_folder_path(name_type(LIGHTING_FOLDER) if name_type else LIGHTING_FOLDER)
            return
        actor.set_editor_property("folder_path", LIGHTING_FOLDER)
    except Exception as exc:
        _warning("Could not assign folder '{0}': {1}".format(LIGHTING_FOLDER, exc))


def _refresh_existing_labels():
    global _EXISTING_LABELS
    _EXISTING_LABELS = {
        str(actor.get_actor_label())
        for actor in _ACTOR_SUBSYSTEM.get_all_level_actors()
        if actor is not None
    }


def _configure_directional(actor):
    component_class = getattr(unreal, "DirectionalLightComponent", None)
    if component_class is None:
        raise RuntimeError("unreal.DirectionalLightComponent is unavailable.")
    component = actor.get_component_by_class(component_class)
    if component is None:
        raise RuntimeError("DirectionalLightComponent was not found on the spawned actor.")
    component.set_editor_property("intensity", DIRECTIONAL_INTENSITY)


def _configure_sky(actor):
    component_class = getattr(unreal, "SkyLightComponent", None)
    if component_class is None:
        raise RuntimeError("unreal.SkyLightComponent is unavailable.")
    component = actor.get_component_by_class(component_class)
    if component is None:
        raise RuntimeError("SkyLightComponent was not found on the spawned actor.")
    component.set_editor_property("intensity", SKY_INTENSITY)


def _spawn_if_missing(label, actor_class, location, rotation, configure=None):
    if label in _EXISTING_LABELS:
        _log("Skipped existing actor label: {0}".format(label))
        return
    if actor_class is None:
        raise RuntimeError("Required Unreal class is unavailable for {0}.".format(label))

    actor = _ACTOR_SUBSYSTEM.spawn_actor_from_class(
        actor_class, unreal.Vector(*location), rotation
    )
    if actor is None:
        raise RuntimeError("spawn_actor_from_class returned None for {0}.".format(label))

    actor.set_actor_label(label)
    _set_folder(actor)
    if configure is not None:
        configure(actor)
    _EXISTING_LABELS.add(label)
    _log("Created {0} ({1}).".format(label, actor_class.__name__))


def main():
    global _LEVEL_SUBSYSTEM, _ACTOR_SUBSYSTEM

    if not _asset_exists(TARGET_MAP):
        _error("Target map does not exist; no level was loaded: {0}".format(TARGET_MAP))
        return

    level_subsystem_class = getattr(unreal, "LevelEditorSubsystem", None)
    actor_subsystem_class = getattr(unreal, "EditorActorSubsystem", None)
    if level_subsystem_class is None:
        _error("Required Unreal class is unavailable: unreal.LevelEditorSubsystem")
        return
    if actor_subsystem_class is None:
        _error("Required Unreal class is unavailable: unreal.EditorActorSubsystem")
        return

    _LEVEL_SUBSYSTEM = unreal.get_editor_subsystem(level_subsystem_class)
    _ACTOR_SUBSYSTEM = unreal.get_editor_subsystem(actor_subsystem_class)
    if _LEVEL_SUBSYSTEM is None:
        _error("Could not obtain LevelEditorSubsystem.")
        return
    if _ACTOR_SUBSYSTEM is None:
        _error("Could not obtain EditorActorSubsystem.")
        return
    if not callable(getattr(_LEVEL_SUBSYSTEM, "load_level", None)):
        _error("LevelEditorSubsystem.load_level is unavailable.")
        return
    if not callable(getattr(_LEVEL_SUBSYSTEM, "save_current_level", None)):
        _error("LevelEditorSubsystem.save_current_level is unavailable.")
        return
    if not callable(getattr(_ACTOR_SUBSYSTEM, "spawn_actor_from_class", None)):
        _error("EditorActorSubsystem.spawn_actor_from_class is unavailable.")
        return

    for label, class_name in (
        ("TEST_DirectionalLight", "DirectionalLight"),
        ("TEST_SkyLight", "SkyLight"),
        ("TEST_SkyAtmosphere", "SkyAtmosphere"),
    ):
        if getattr(unreal, class_name, None) is None:
            _error("Required Unreal class is unavailable for {0}: unreal.{1}".format(label, class_name))
            return

    _warning(
        "LevelEditorSubsystem.load_level() will close the current persistent "
        "level without saving it. Save current work before continuing."
    )
    if not _LEVEL_SUBSYSTEM.load_level(TARGET_MAP):
        _error("Could not load existing target map: {0}".format(TARGET_MAP))
        return

    _refresh_existing_labels()
    try:
        _spawn_if_missing(
            "TEST_DirectionalLight", unreal.DirectionalLight,
            (0.0, 0.0, 500.0), unreal.Rotator(-45.0, -30.0, 0.0),
            _configure_directional,
        )
        _spawn_if_missing(
            "TEST_SkyLight", unreal.SkyLight,
            (0.0, 0.0, 300.0), unreal.Rotator(0.0, 0.0, 0.0),
            _configure_sky,
        )
        _spawn_if_missing(
            "TEST_SkyAtmosphere", unreal.SkyAtmosphere,
            (0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0),
        )
    except Exception as exc:
        _error(
            "Lighting pass failed: {0}. The new map may now contain partially "
            "generated actors; existing created actors were not deleted and no "
            "rollback is claimed.".format(exc)
        )
        return

    if not _LEVEL_SUBSYSTEM.save_current_level():
        _error("Lighting actors were created, but saving the current level failed.")
        return
    _log("Greybox test-lighting pass completed and the current level was saved.")


if __name__ == "__main__":
    main()
