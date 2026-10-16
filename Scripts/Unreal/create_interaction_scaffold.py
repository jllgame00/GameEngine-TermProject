"""Create the first RecordShop interaction-system asset scaffold.

Run this file manually inside Unreal Editor's Python environment. It creates
only missing assets through AssetTools and supported editor APIs. It never
overwrites an existing asset and does not create Blueprint graph nodes.
"""

import unreal


INPUT_DIR = "/Game/RecordShop/Input"
INTERFACES_DIR = "/Game/RecordShop/Interaction/Interfaces"
COMPONENTS_DIR = "/Game/RecordShop/Interaction/Components"
ACTORS_DIR = "/Game/RecordShop/Interaction/Actors"

IA_INTERACT_PATH = INPUT_DIR + "/IA_Interact"
BPI_INTERACTABLE_PATH = INTERFACES_DIR + "/BPI_Interactable"
BPC_INTERACTION_PATH = COMPONENTS_DIR + "/BPC_Interaction"
BP_RECORD_SHELF_PATH = ACTORS_DIR + "/BP_RecordShelf"

INPUT_CONTEXT_CANDIDATES = (
    "/Game/Input/IMC_Default",
    "/Game/ThirdPerson/Input/IMC_Default",
)

_ASSET_SUBSYSTEM = None
_ASSET_TOOLS = None


def _log(message):
    unreal.log("[RecordShopInteractionScaffold] {0}".format(message))


def _log_warning(message):
    unreal.log_warning("[RecordShopInteractionScaffold] {0}".format(message))


def _log_error(message):
    unreal.log_error("[RecordShopInteractionScaffold] {0}".format(message))


def _get_editor_subsystem(subsystem_class, display_name):
    if not hasattr(unreal, "get_editor_subsystem"):
        raise RuntimeError("unreal.get_editor_subsystem() is unavailable")
    subsystem = unreal.get_editor_subsystem(subsystem_class)
    if subsystem is None:
        raise RuntimeError("Could not obtain {0}".format(display_name))
    return subsystem


def _asset_object_path(asset_path):
    asset_name = asset_path.rsplit("/", 1)[-1]
    return asset_path + "." + asset_name


def _asset_exists(asset_path):
    """Check both package-style and object-style paths without mutating assets."""
    paths_to_check = (asset_path, _asset_object_path(asset_path))
    for path in paths_to_check:
        try:
            if hasattr(_ASSET_SUBSYSTEM, "does_asset_exist"):
                if _ASSET_SUBSYSTEM.does_asset_exist(path):
                    return True
            elif hasattr(unreal, "EditorAssetLibrary"):
                if unreal.EditorAssetLibrary.does_asset_exist(path):
                    return True
        except Exception as error:
            _log_warning("Could not query {0}: {1}".format(path, error))
    return False


def _ensure_directory(directory_path):
    if hasattr(_ASSET_SUBSYSTEM, "make_directory"):
        result = _ASSET_SUBSYSTEM.make_directory(directory_path)
        if result is False:
            _log_warning(
                "Could not create {0}; it may already exist. Continuing.".format(
                    directory_path
                )
            )
        return

    if hasattr(unreal, "EditorAssetLibrary") and hasattr(
        unreal.EditorAssetLibrary, "make_directory"
    ):
        result = unreal.EditorAssetLibrary.make_directory(directory_path)
        if result is False:
            _log_warning(
                "Could not create {0}; it may already exist. Continuing.".format(
                    directory_path
                )
            )
        return

    raise RuntimeError("No supported directory-creation API is available")


def _create_asset(asset_name, package_path, asset_class, factory):
    asset_path = package_path + "/" + asset_name
    if _asset_exists(asset_path):
        _log("Skipped existing asset: {0}".format(asset_path))
        return None, False

    asset = _ASSET_TOOLS.create_asset(asset_name, package_path, asset_class, factory)
    if asset is None:
        raise RuntimeError("AssetTools could not create {0}".format(asset_path))
    _log("Created asset shell: {0}".format(asset_path))
    return asset, True


def _save_created_assets(created_assets):
    if not created_assets:
        return

    if hasattr(_ASSET_SUBSYSTEM, "save_loaded_assets"):
        if not _ASSET_SUBSYSTEM.save_loaded_assets(created_assets, True):
            raise RuntimeError("EditorAssetSubsystem.save_loaded_assets() failed")
        return

    if hasattr(unreal, "EditorAssetLibrary") and hasattr(
        unreal.EditorAssetLibrary, "save_asset"
    ):
        for asset in created_assets:
            if not unreal.EditorAssetLibrary.save_asset(asset.get_path_name()):
                raise RuntimeError(
                    "EditorAssetLibrary.save_asset() failed for {0}".format(
                        asset.get_path_name()
                    )
                )
        return

    raise RuntimeError("No supported asset-save API is available")


def _make_blueprint_factory(parent_class=None):
    factory_class = getattr(unreal, "BlueprintFactory", None)
    if factory_class is None:
        _log_warning("BlueprintFactory is unavailable; Blueprint shells require manual creation.")
        return None

    factory = factory_class()
    if parent_class is not None:
        factory.set_editor_property("parent_class", parent_class)
    try:
        factory.set_editor_property("skip_class_picker", True)
    except Exception:
        _log_warning("BlueprintFactory.skip_class_picker is unavailable; verify creation manually.")
    return factory


def _make_interface_factory():
    factory_class = getattr(unreal, "BlueprintInterfaceFactory", None)
    if factory_class is None:
        _log_warning(
            "BlueprintInterfaceFactory is unavailable; BPI_Interactable must be created manually."
        )
        return None
    return factory_class()


def _configure_input_action(asset):
    try:
        asset.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
        _log("Configured IA_Interact as Digital/Bool.")
    except Exception as error:
        _log_warning(
            "IA_Interact was created but its Boolean value type could not be set: {0}. "
            "Set Value Type to Digital/Bool manually.".format(error)
        )


def _create_input_action():
    factory_class = getattr(unreal, "InputAction_Factory", None)
    if factory_class is None:
        _log_warning("InputAction_Factory is unavailable; IA_Interact requires manual creation.")
        return None, False

    asset, created = _create_asset(
        "IA_Interact",
        INPUT_DIR,
        unreal.InputAction,
        factory_class(),
    )
    if created:
        _configure_input_action(asset)
    return asset, created


def _configure_interaction_component(blueprint):
    library = getattr(unreal, "BlueprintEditorLibrary", None)
    if library is None:
        _log_warning(
            "BlueprintEditorLibrary is unavailable; BPC_Interaction remains a shell. "
            "Add TryInteract and the variables manually."
        )
        return

    graph = library.add_function_graph(blueprint, "TryInteract")
    if graph is None:
        _log_warning("Could not add TryInteract; add the empty function manually.")

    real_type = library.get_basic_type_by_name("real")
    for variable_name in ("TraceDistance", "TraceRadius"):
        if not library.add_member_variable(blueprint, variable_name, real_type):
            _log_warning("Could not add {0}; add it manually as a Float.".format(variable_name))

    _log_warning(
        "TraceDistance and TraceRadius were added without defaults where supported. "
        "Set both Blueprint defaults manually to 180.0 and 60.0."
    )
    if hasattr(library, "compile_blueprint"):
        library.compile_blueprint(blueprint)


def _create_interaction_component():
    factory = _make_blueprint_factory(unreal.ActorComponent)
    if factory is None:
        return None, False

    asset, created = _create_asset(
        "BPC_Interaction",
        COMPONENTS_DIR,
        unreal.Blueprint,
        factory,
    )
    if created:
        _configure_interaction_component(asset)
    return asset, created


def _create_interface():
    factory = _make_interface_factory()
    if factory is None:
        return None, False

    asset, created = _create_asset(
        "BPI_Interactable",
        INTERFACES_DIR,
        unreal.Blueprint,
        factory,
    )
    if created:
        _log_warning(
            "BPI_Interactable is a shell only. Add Interact(Interactor: Actor Object Reference) "
            "manually in the Blueprint Interface editor."
        )
    return asset, created


def _create_record_shelf():
    factory = _make_blueprint_factory(unreal.Actor)
    if factory is None:
        return None, False

    asset, created = _create_asset(
        "BP_RecordShelf",
        ACTORS_DIR,
        unreal.Blueprint,
        factory,
    )
    if created:
        _log_warning(
            "BP_RecordShelf is an Actor shell only. Add BoxCollision, keep DefaultSceneRoot, "
            "and implement BPI_Interactable manually. No Static Mesh was added."
        )
    return asset, created


def _report_input_mapping_contexts():
    found_paths = []
    for package_path in INPUT_CONTEXT_CANDIDATES:
        if _asset_exists(package_path):
            found_paths.append(package_path)

    if not found_paths:
        _log_warning(
            "No candidate Enhanced Input Mapping Context was found. "
            "Inspect the ThirdPerson assets manually."
        )
    else:
        for package_path in found_paths:
            _log("Existing mapping context found: {0}".format(package_path))
            object_path = _asset_object_path(package_path)
            if hasattr(_ASSET_SUBSYSTEM, "find_package_referencers_for_asset"):
                try:
                    referencers = _ASSET_SUBSYSTEM.find_package_referencers_for_asset(
                        object_path, False
                    )
                    if referencers:
                        _log(
                            "Mapping-context referencers for {0}: {1}".format(
                                package_path, list(referencers)
                            )
                        )
                except Exception as error:
                    _log_warning("Could not inspect mapping-context referencers: {0}".format(error))

    _log(
        "Do not modify the mapping context automatically. Manually open the existing "
        "ThirdPerson mapping context, add IA_Interact, and bind keyboard E."
    )


def main():
    global _ASSET_SUBSYSTEM, _ASSET_TOOLS
    _ASSET_SUBSYSTEM = _get_editor_subsystem(
        unreal.EditorAssetSubsystem, "EditorAssetSubsystem"
    )
    _ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
    if _ASSET_TOOLS is None:
        raise RuntimeError("AssetToolsHelpers returned no AssetTools instance")

    for directory_path in (INPUT_DIR, INTERFACES_DIR, COMPONENTS_DIR, ACTORS_DIR):
        _ensure_directory(directory_path)

    _report_input_mapping_contexts()
    created_assets = []

    for creator in (
        _create_input_action,
        _create_interface,
        _create_interaction_component,
        _create_record_shelf,
    ):
        try:
            asset, created = creator()
            if created:
                created_assets.append(asset)
        except Exception as error:
            _log_error("Asset scaffold step failed: {0}".format(error))

    _save_created_assets(created_assets)
    _log("Interaction scaffold pass completed. Existing assets were not overwritten.")


if __name__ == "__main__":
    main()
