"""Add idempotent gameplay markers to the existing RecordShop greybox level.

Run this file from Unreal Editor's Python tooling. It loads the existing map,
adds only missing TargetPoint and CameraActor placeholders, and never creates
or replaces a level.
"""

import unreal


MAP_PACKAGE_PATH = "/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox"
MAP_OBJECT_PATH = MAP_PACKAGE_PATH + ".L_RecordShop_Greybox"

FOLDER_CUSTOMER = "Greybox/Gameplay/Customer"
FOLDER_INTERACTION = "Greybox/Gameplay/Interaction"
FOLDER_CAMERAS = "Greybox/Gameplay/Cameras"

_LEVEL_SUBSYSTEM = None
_ACTOR_SUBSYSTEM = None
_EXISTING_LABELS = set()


def _log(message):
    unreal.log("[RecordShopGameplayMarkers] {0}".format(message))


def _log_warning(message):
    unreal.log_warning("[RecordShopGameplayMarkers] {0}".format(message))


def _log_error(message):
    unreal.log_error("[RecordShopGameplayMarkers] {0}".format(message))


def _get_editor_subsystem(subsystem_class, display_name):
    if not hasattr(unreal, "get_editor_subsystem"):
        raise RuntimeError("unreal.get_editor_subsystem() is unavailable")
    if not hasattr(unreal, subsystem_class.__name__):
        raise RuntimeError("{0} is unavailable".format(display_name))

    subsystem = unreal.get_editor_subsystem(subsystem_class)
    if subsystem is None:
        raise RuntimeError("Could not obtain {0}".format(display_name))
    return subsystem


def _target_map_exists():
    """Fail closed if the Asset Registry cannot verify the existing map."""
    try:
        if hasattr(unreal, "EditorAssetSubsystem"):
            asset_subsystem = _get_editor_subsystem(
                unreal.EditorAssetSubsystem, "EditorAssetSubsystem"
            )
            if hasattr(asset_subsystem, "does_asset_exist"):
                return bool(
                    asset_subsystem.does_asset_exist(MAP_OBJECT_PATH)
                    or asset_subsystem.does_asset_exist(MAP_PACKAGE_PATH)
                )

        # Compatibility fallback if the installed editor does not expose the
        # newer subsystem method.
        if hasattr(unreal, "EditorAssetLibrary"):
            return bool(
                unreal.EditorAssetLibrary.does_asset_exist(MAP_OBJECT_PATH)
                or unreal.EditorAssetLibrary.does_asset_exist(MAP_PACKAGE_PATH)
            )
        raise RuntimeError("No supported asset-existence API is available")
    except Exception as error:
        _log_error(
            "Could not verify {0}: {1}. Stopping without loading or changing a level.".format(
                MAP_PACKAGE_PATH, error
            )
        )
        return False


def _set_actor_folder(actor, folder_path):
    """Assign an Outliner folder when supported; folder errors are non-fatal."""
    if not folder_path:
        return

    try:
        if hasattr(actor, "set_folder_path"):
            folder_value = unreal.Name(folder_path) if hasattr(unreal, "Name") else folder_path
            actor.set_folder_path(folder_value)
        elif hasattr(actor, "set_editor_property"):
            actor.set_editor_property("folder_path", folder_path)
    except Exception as error:
        _log_warning(
            "Could not assign {0} to {1}; continuing: {2}".format(
                folder_path, actor.get_actor_label(), error
            )
        )


def _refresh_existing_labels():
    global _EXISTING_LABELS
    _EXISTING_LABELS = set()
    for actor in _ACTOR_SUBSYSTEM.get_all_level_actors():
        if actor is not None:
            _EXISTING_LABELS.add(str(actor.get_actor_label()))


def _spawn_if_missing(label, actor_class, location, rotation, folder_path):
    if label in _EXISTING_LABELS:
        _log("Skipped {0}: an actor with that label already exists.".format(label))
        return False

    try:
        actor = _ACTOR_SUBSYSTEM.spawn_actor_from_class(
            actor_class,
            unreal.Vector(*location),
            rotation,
        )
        if actor is None:
            raise RuntimeError("EditorActorSubsystem returned no actor")
        actor.set_actor_label(label)
        _set_actor_folder(actor, folder_path)
        _EXISTING_LABELS.add(label)
        _log("Created {0}.".format(label))
        return True
    except Exception as error:
        _log_error("Failed to create {0}: {1}".format(label, error))
        raise


def _create_customer_route():
    customer_markers = (
        ("TP_CustomerSpawn", (0.0, -720.0, 100.0)),
        ("TP_CustomerEntry", (0.0, -500.0, 100.0)),
        ("TP_CustomerSeat", (80.0, 290.0, 90.0)),
        ("TP_CustomerExit", (0.0, -720.0, 100.0)),
    )
    created_count = 0
    for label, location in customer_markers:
        if _spawn_if_missing(
            label,
            unreal.TargetPoint,
            location,
            unreal.Rotator(0.0, 90.0, 0.0),
            FOLDER_CUSTOMER,
        ):
            created_count += 1
    return created_count


def _create_interaction_markers():
    interaction_markers = (
        ("TP_RecordBrowse", (-300.0, 0.0, 100.0)),
        ("TP_TurntableInteract", (80.0, 300.0, 100.0)),
        ("TP_DialogueStand", (150.0, 220.0, 100.0)),
    )
    created_count = 0
    for label, location in interaction_markers:
        if _spawn_if_missing(
            label,
            unreal.TargetPoint,
            location,
            unreal.Rotator(0.0, 90.0, 0.0),
            FOLDER_INTERACTION,
        ):
            created_count += 1
    return created_count


def _create_camera_anchors():
    # These transforms are intentionally rough. They are editor-visible
    # composition anchors for the vertical slice, not finished cinematics.
    camera_anchors = (
        (
            "CAM_Dialogue",
            (160.0, 180.0, 150.0),
            unreal.Rotator(-24.0, 126.0, 0.0),
        ),
        (
            "CAM_RecordSelection",
            (-180.0, -90.0, 160.0),
            unreal.Rotator(-13.0, 159.0, 0.0),
        ),
        (
            "CAM_Listening",
            (280.0, 180.0, 170.0),
            unreal.Rotator(-12.0, 140.0, 0.0),
        ),
    )
    created_count = 0
    for label, location, rotation in camera_anchors:
        if _spawn_if_missing(
            label,
            unreal.CameraActor,
            location,
            rotation,
            FOLDER_CAMERAS,
        ):
            created_count += 1
    return created_count


def _save_current_level():
    if not _LEVEL_SUBSYSTEM.save_current_level():
        raise RuntimeError("LevelEditorSubsystem.save_current_level() failed")


def main():
    _log("Checking existing target map: {0}".format(MAP_PACKAGE_PATH))
    if not _target_map_exists():
        _log_error(
            "Target map does not exist or could not be verified. "
            "No replacement map will be created."
        )
        return

    global _LEVEL_SUBSYSTEM, _ACTOR_SUBSYSTEM
    _LEVEL_SUBSYSTEM = _get_editor_subsystem(unreal.LevelEditorSubsystem, "LevelEditorSubsystem")
    _ACTOR_SUBSYSTEM = _get_editor_subsystem(unreal.EditorActorSubsystem, "EditorActorSubsystem")

    _log(
        "LevelEditorSubsystem.load_level() will close the current persistent "
        "level without saving it. Save any current work before continuing."
    )
    if not _LEVEL_SUBSYSTEM.load_level(MAP_PACKAGE_PATH):
        _log_error("Could not load the existing target map. No actors were created.")
        return

    _refresh_existing_labels()
    created_count = 0
    current_label = "customer route markers"
    try:
        created_count += _create_customer_route()
        current_label = "interaction markers"
        created_count += _create_interaction_markers()
        current_label = "camera anchors"
        created_count += _create_camera_anchors()
    except Exception as error:
        _log_error(
            "Gameplay-marker generation failed while processing {0}: {1}. "
            "The current level was not saved automatically.".format(current_label, error)
        )
        raise

    _log(
        "NavMeshBoundsVolume creation was deferred: no reliable brush-volume "
        "sizing API is used by this script. See GreyboxGeneration.md for manual setup."
    )

    if created_count == 0:
        _log("All gameplay markers already exist. Nothing was saved.")
        return

    try:
        _save_current_level()
    except Exception as error:
        _log_error(
            "Gameplay markers were created, but saving the current level failed: {0}".format(
                error
            )
        )
        raise

    _log("Gameplay marker pass completed and the existing level was saved.")


if __name__ == "__main__":
    main()
