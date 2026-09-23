"""Create the minimal, reusable RecordShop game-flow scaffold.

Run inside Unreal Editor 5.8.2 (or with the PythonScript commandlet). The
script is intentionally idempotent: it reuses assets and the existing map
actor, creates missing Blueprint graphs only once, and saves the map only when
it adds the manager actor.

UE 5.8.2 exposes safe Blueprint graph creation/wiring through
BlueprintGraphEditor, but UserDefinedEnum entries remain unreadable in Python.
The saved manual enum edit is authoritative; this script never recreates or
overwrites E_GameFlowState.
"""

import unreal


FLOW_DIR = "/Game/RecordShop/Core/Flow"
ENUM_PATH = FLOW_DIR + "/E_GameFlowState"
BLUEPRINT_PATH = FLOW_DIR + "/BP_GameFlowManager"
MAP_PATH = "/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox"

ENUM_NAME = "E_GameFlowState"
BLUEPRINT_NAME = "BP_GameFlowManager"
MANAGER_LABEL = "BP_GameFlowManager"
STATE_NAMES = (
    "Explore",
    "Dialogue",
    "RecordSelection",
    "Turntable",
    "Listening",
    "Result",
)
DUMMY_SEQUENCE = (
    "Explore",
    "Dialogue",
    "RecordSelection",
    "Turntable",
    "Listening",
    "Result",
    "Explore",
)

SET_STATE_FUNCTION = "SetGameFlowState"
DEBUG_FUNCTION = "Debug_RunDummyFlow"
CURRENT_STATE_VARIABLE = "CurrentState"

PRINT_STRING_PATH = "/Script/Engine.KismetSystemLibrary.PrintString"
CONCAT_STRING_PATH = "/Script/Engine.KismetStringLibrary.Concat_StrStr"

_ASSET_SUBSYSTEM = None
_ASSET_TOOLS = None
_LEVEL_SUBSYSTEM = None
_ACTOR_SUBSYSTEM = None


def _log(message):
    unreal.log("[RecordShopGameFlow] {0}".format(message))


def _warning(message):
    unreal.log_warning("[RecordShopGameFlow] {0}".format(message))


def _error(message):
    unreal.log_error("[RecordShopGameFlow] {0}".format(message))


def _object_path(asset_path):
    return "{0}.{1}".format(asset_path, asset_path.rsplit("/", 1)[-1])


def _asset_exists(asset_path):
    for candidate in (asset_path, _object_path(asset_path)):
        if _ASSET_SUBSYSTEM.does_asset_exist(candidate):
            return True
    return False


def _load_asset(asset_path):
    asset = unreal.load_asset(asset_path)
    if asset is None:
        raise RuntimeError("Could not load asset: {0}".format(asset_path))
    return asset


def _ensure_directory():
    result = _ASSET_SUBSYSTEM.make_directory(FLOW_DIR)
    if result is False and not _ASSET_SUBSYSTEM.does_directory_exist(FLOW_DIR):
        raise RuntimeError("Could not create content folder: {0}".format(FLOW_DIR))
    _log("PASS folder exists: {0}".format(FLOW_DIR))


def _create_or_load_enum():
    if not _asset_exists(ENUM_PATH):
        raise RuntimeError(
            "Required manually-authored enum is missing; refusing to recreate it: {0}".format(
                ENUM_PATH
            )
        )
    asset = _load_asset(ENUM_PATH)
    if not isinstance(asset, unreal.UserDefinedEnum):
        raise RuntimeError("Existing asset is not a Blueprint Enum: {0}".format(ENUM_PATH))
    _log("Reused authoritative enum without modifying it: {0}".format(ENUM_PATH))
    return asset


def _create_or_load_blueprint():
    if _asset_exists(BLUEPRINT_PATH):
        asset = _load_asset(BLUEPRINT_PATH)
        if not isinstance(asset, unreal.Blueprint):
            raise RuntimeError("Existing asset is not a Blueprint: {0}".format(BLUEPRINT_PATH))
        _log("Reused existing Blueprint: {0}".format(BLUEPRINT_PATH))
        return asset, False

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    try:
        factory.set_editor_property("skip_class_picker", True)
    except Exception:
        pass
    asset = _ASSET_TOOLS.create_asset(
        BLUEPRINT_NAME,
        FLOW_DIR,
        unreal.Blueprint,
        factory,
    )
    if asset is None:
        raise RuntimeError("AssetTools could not create {0}".format(BLUEPRINT_PATH))
    if not unreal.BlueprintEditorLibrary.compile_blueprint(asset):
        raise RuntimeError("Initial compile failed for {0}".format(BLUEPRINT_PATH))
    _log("Created Actor Blueprint shell: {0}".format(BLUEPRINT_PATH))
    return asset, True


def _enum_pin_type(enum_asset):
    pin_type = unreal.BlueprintEditorLibrary.get_basic_type_by_name("byte")
    exported = pin_type.export_text()
    enum_reference = '"/Script/Engine.UserDefinedEnum\'{0}\'"'.format(
        enum_asset.get_path_name()
    )
    configured = exported.replace(
        "PinSubCategoryObject=None",
        "PinSubCategoryObject={0}".format(enum_reference),
        1,
    )
    pin_type.import_text(configured)
    if enum_asset.get_path_name() not in pin_type.export_text():
        raise RuntimeError("Could not construct E_GameFlowState Blueprint pin type")
    return pin_type


def _member_names(blueprint):
    return tuple(
        str(name).rsplit(".", 1)[-1]
        for name in unreal.BlueprintEditorLibrary.list_member_variable_names(
            blueprint, False
        )
    )


def _pin(node, direction, name):
    finder = node.find_input_pin if direction == "input" else node.find_output_pin
    pin = finder(name)
    if not pin.is_valid():
        raise RuntimeError(
            "Missing {0} pin '{1}' on node {2}".format(
                direction, name, node.get_node_title()
            )
        )
    return pin


def _connect(output_pin, input_pin, description):
    if not output_pin.try_create_connection(input_pin):
        raise RuntimeError("Could not connect {0}".format(description))


def _set_pin(pin, value, description):
    if not pin.set_pin_value(str(value)):
        raise RuntimeError("Could not set {0} to {1}".format(description, value))


def _set_node_position(node, x, y):
    node.set_node_pos(unreal.IntPoint(x, y))


def _ensure_current_state(blueprint, enum_asset):
    names = _member_names(blueprint)
    expected_type = _enum_pin_type(enum_asset)
    if CURRENT_STATE_VARIABLE not in names:
        if not unreal.BlueprintEditorLibrary.add_member_variable(
            blueprint, CURRENT_STATE_VARIABLE, expected_type
        ):
            raise RuntimeError("Could not add CurrentState to BP_GameFlowManager")
        _log("Created CurrentState variable (default is first enum entry: Explore).")
        return True

    actual_type = unreal.BlueprintEditorLibrary.get_member_variable_type(
        blueprint, CURRENT_STATE_VARIABLE
    )
    if actual_type is None:
        raise RuntimeError("CurrentState exists but its type could not be inspected")
    actual_type_text = actual_type.export_text()
    if (
        'PinCategory="byte"' not in actual_type_text
        or enum_asset.get_path_name() not in actual_type_text
    ):
        raise RuntimeError("CurrentState exists with an unexpected non-E_GameFlowState type")
    _log("PASS CurrentState already has E_GameFlowState type.")
    return False


def _create_set_state_graph(blueprint, enum_asset):
    library = unreal.BlueprintEditorLibrary
    if library.find_graph(blueprint, SET_STATE_FUNCTION) is not None:
        _log("Reused existing function graph: {0}".format(SET_STATE_FUNCTION))
        return False

    editor = unreal.BlueprintGraphEditor.create_and_edit_function_graph(
        blueprint, SET_STATE_FUNCTION
    )
    if editor is None:
        raise RuntimeError("Could not create SetGameFlowState graph")

    try:
        editor.set_function_is_public()
        new_state_pin = editor.add_graph_input_parameter(
            "NewState", _enum_pin_type(enum_asset), ""
        )
        if not new_state_pin.is_valid():
            raise RuntimeError("Could not add NewState input")

        entry_exec = editor.find_graph_entry_pin()
        entry_node = entry_exec.get_owning_node()
        new_state_output = _pin(entry_node, "output", "NewState")

        set_node = editor.add_set_member_variable_node(CURRENT_STATE_VARIABLE)
        concat_node = editor.add_call_function_node(CONCAT_STRING_PATH)
        print_node = editor.add_call_function_node(PRINT_STRING_PATH)
        if set_node is None or concat_node is None or print_node is None:
            raise RuntimeError("Could not create SetGameFlowState implementation nodes")

        _set_node_position(set_node, 260, 0)
        _set_node_position(concat_node, 500, 180)
        _set_node_position(print_node, 740, 0)

        _connect(entry_exec, set_node.find_execute_pin(), "entry -> Set CurrentState")
        _connect(
            new_state_output,
            _pin(set_node, "input", CURRENT_STATE_VARIABLE),
            "NewState -> CurrentState value",
        )
        _set_pin(_pin(concat_node, "input", "A"), "FLOW: ", "debug prefix")
        _connect(
            new_state_output,
            _pin(concat_node, "input", "B"),
            "NewState -> enum-to-string debug conversion",
        )
        _connect(
            set_node.find_then_pin(),
            print_node.find_execute_pin(),
            "Set CurrentState -> Print String",
        )
        _connect(
            _pin(concat_node, "output", "ReturnValue"),
            _pin(print_node, "input", "InString"),
            "FLOW message -> Print String",
        )
    except Exception:
        library.remove_function_graph(blueprint, SET_STATE_FUNCTION)
        raise

    _log("Created SetGameFlowState(NewState) with assignment and readable FLOW debug output.")
    return True


def _discover_internal_enum_names(blueprint):
    """Ask a real enum call pin which literal representation UE accepts.

    This avoids UUserDefinedEnum readback entirely. The temporary graph is
    never saved and is removed immediately after probing the supported pin.
    """
    library = unreal.BlueprintEditorLibrary
    probe_name = "__RecordShop_InternalEnumLiteralProbe"
    if library.find_graph(blueprint, probe_name) is not None:
        raise RuntimeError("Unexpected pre-existing internal enum probe graph")

    editor = unreal.BlueprintGraphEditor.create_and_edit_function_graph(
        blueprint, probe_name
    )
    if editor is None:
        raise RuntimeError("Could not create temporary enum literal probe graph")

    try:
        call_node = editor.add_call_function_node(SET_STATE_FUNCTION)
        if call_node is None:
            raise RuntimeError("Could not create enum literal probe call node")
        state_pin = _pin(call_node, "input", "NewState")
        first_literal = str(state_pin.get_pin_value())

        suffix_start = len(first_literal)
        while suffix_start > 0 and first_literal[suffix_start - 1].isdigit():
            suffix_start -= 1
        if suffix_start == len(first_literal):
            raise RuntimeError(
                "Unexpected enum literal representation: {0}".format(first_literal)
            )

        prefix = first_literal[:suffix_start]
        first_index = int(first_literal[suffix_start:])
        raw_names = []
        for offset, display_name in enumerate(STATE_NAMES):
            candidate = "{0}{1}".format(prefix, first_index + offset)
            if not state_pin.set_pin_value(candidate):
                raise RuntimeError(
                    "UE rejected internal enum literal {0} for {1}".format(
                        candidate, display_name
                    )
                )
            accepted = str(state_pin.get_pin_value())
            if accepted != candidate:
                raise RuntimeError(
                    "UE normalized enum literal {0} unexpectedly to {1}".format(
                        candidate, accepted
                    )
                )
            raw_names.append(candidate)
    finally:
        library.remove_function_graph(blueprint, probe_name)

    _log(
        "PASS UE accepted internal enum literals for the six authoritative display entries: {0}".format(
            ", ".join(raw_names)
        )
    )
    return tuple(raw_names)


def _create_dummy_flow_graph(blueprint, raw_names_by_display):
    library = unreal.BlueprintEditorLibrary
    if library.find_graph(blueprint, DEBUG_FUNCTION) is not None:
        _log("Reused existing function graph: {0}".format(DEBUG_FUNCTION))
        return False

    editor = unreal.BlueprintGraphEditor.create_and_edit_function_graph(
        blueprint, DEBUG_FUNCTION
    )
    if editor is None:
        raise RuntimeError("Could not create Debug_RunDummyFlow graph")

    try:
        editor.set_function_is_public()
        previous_exec = editor.find_graph_entry_pin()
        nodes = []
        for index, state_name in enumerate(DUMMY_SEQUENCE):
            call_node = editor.add_call_function_node(SET_STATE_FUNCTION)
            if call_node is None:
                raise RuntimeError("Could not create SetGameFlowState call for {0}".format(state_name))
            _set_node_position(call_node, 260 + (index * 260), 0)
            _set_pin(
                _pin(call_node, "input", "NewState"),
                raw_names_by_display[state_name],
                "dummy state {0}".format(state_name),
            )
            _connect(
                previous_exec,
                call_node.find_execute_pin(),
                "dummy transition to {0}".format(state_name),
            )
            previous_exec = call_node.find_then_pin()
            nodes.append(call_node)

        editor.add_comment_to_nodes(
            "DEVELOPMENT ONLY - deterministic scaffold verification; not production flow",
            nodes,
            60,
        )
    except Exception:
        library.remove_function_graph(blueprint, DEBUG_FUNCTION)
        raise

    _log("Created development-only Debug_RunDummyFlow sequence.")
    return True


def _compile_and_check_graphs(blueprint):
    if not unreal.BlueprintEditorLibrary.compile_blueprint(blueprint):
        raise RuntimeError("BP_GameFlowManager failed to compile")
    for graph_name in (SET_STATE_FUNCTION, DEBUG_FUNCTION):
        editor = unreal.BlueprintGraphEditor.get_graph_editor_by_name(blueprint, graph_name)
        if editor is None:
            raise RuntimeError("Missing expected graph: {0}".format(graph_name))
        errors = editor.list_nodes_with_errors()
        warnings = editor.list_nodes_with_warnings()
        if errors or warnings:
            raise RuntimeError(
                "{0} compiled with node diagnostics: errors={1}, warnings={2}".format(
                    graph_name, len(errors), len(warnings)
                )
            )
    _log("PASS BP_GameFlowManager compiled without graph errors or warnings.")


def _save_assets(assets):
    unique_assets = []
    for asset in assets:
        if asset is not None and asset not in unique_assets:
            unique_assets.append(asset)
    if unique_assets and not _ASSET_SUBSYSTEM.save_loaded_assets(unique_assets, True):
        raise RuntimeError("EditorAssetSubsystem.save_loaded_assets() failed")


def _manager_actors(manager_class):
    return [
        actor
        for actor in _ACTOR_SUBSYSTEM.get_all_level_actors()
        if actor is not None and actor.get_class() == manager_class
    ]


def _ensure_manager_in_map(blueprint):
    if not _asset_exists(MAP_PATH):
        raise RuntimeError("Integration map does not exist: {0}".format(MAP_PATH))
    _warning(
        "Loading the integration map can close another currently open level; "
        "save unrelated Editor work before running this script interactively."
    )
    if not _LEVEL_SUBSYSTEM.load_level(MAP_PATH):
        raise RuntimeError("Could not load integration map: {0}".format(MAP_PATH))

    manager_class = unreal.BlueprintEditorLibrary.generated_class(blueprint)
    if manager_class is None:
        raise RuntimeError("BP_GameFlowManager has no generated class")

    actors = _manager_actors(manager_class)
    if len(actors) > 1:
        raise RuntimeError(
            "Found {0} BP_GameFlowManager actors; refusing to delete actors automatically".format(
                len(actors)
            )
        )
    if len(actors) == 1:
        _log("PASS exactly one BP_GameFlowManager already exists in the map.")
        return False

    actor = _ACTOR_SUBSYSTEM.spawn_actor_from_class(
        manager_class,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    if actor is None:
        raise RuntimeError("Could not spawn BP_GameFlowManager in the integration map")
    actor.set_actor_label(MANAGER_LABEL)
    try:
        actor.set_folder_path("RecordShop/Core")
    except Exception:
        _warning("Actor folder assignment is unavailable; placement is still valid.")
    if not _LEVEL_SUBSYSTEM.save_current_level():
        raise RuntimeError("Manager was spawned, but saving the integration map failed")
    _log("Placed exactly one BP_GameFlowManager and saved the integration map.")
    return True


def _validate(blueprint, enum_asset):
    failures = []
    names = _member_names(blueprint)
    if CURRENT_STATE_VARIABLE not in names:
        failures.append("CurrentState is missing")
    else:
        variable_type = unreal.BlueprintEditorLibrary.get_member_variable_type(
            blueprint, CURRENT_STATE_VARIABLE
        )
        if (
            variable_type is None
            or enum_asset.get_path_name() not in variable_type.export_text()
        ):
            failures.append("CurrentState is not typed as E_GameFlowState")

    for graph_name in (SET_STATE_FUNCTION, DEBUG_FUNCTION):
        if unreal.BlueprintEditorLibrary.find_graph(blueprint, graph_name) is None:
            failures.append("{0} is missing".format(graph_name))

    manager_class = unreal.BlueprintEditorLibrary.generated_class(blueprint)
    actor_count = len(_manager_actors(manager_class)) if manager_class is not None else 0
    if actor_count != 1:
        failures.append("integration map manager count is {0}, expected 1".format(actor_count))

    if failures:
        for failure in failures:
            _error("FAIL validation: {0}".format(failure))
        return False

    _log(
        "PASS using authoritative saved enum display order: {0}".format(
            ", ".join(STATE_NAMES)
        )
    )
    _log("PASS CurrentState uses E_GameFlowState and defaults to Explore (enum index 0).")
    _log("PASS SetGameFlowState updates CurrentState and prints FLOW: <State>.")
    _log("PASS Debug_RunDummyFlow runs the requested seven-step cycle.")
    _log("PASS exactly one BP_GameFlowManager is placed in the integration map.")
    return True


def main():
    global _ASSET_SUBSYSTEM, _ASSET_TOOLS, _LEVEL_SUBSYSTEM, _ACTOR_SUBSYSTEM
    _ASSET_SUBSYSTEM = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    _LEVEL_SUBSYSTEM = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    _ACTOR_SUBSYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    _ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
    if None in (_ASSET_SUBSYSTEM, _LEVEL_SUBSYSTEM, _ACTOR_SUBSYSTEM, _ASSET_TOOLS):
        raise RuntimeError("Required Unreal Editor subsystems are unavailable")

    _ensure_directory()
    enum_asset = _create_or_load_enum()
    _enum_pin_type(enum_asset)
    _log("PASS authoritative E_GameFlowState is usable as a Blueprint pin type.")
    blueprint, blueprint_created = _create_or_load_blueprint()
    _save_assets([blueprint if blueprint_created else None])

    blueprint_modified = _ensure_current_state(blueprint, enum_asset)
    blueprint_modified |= _create_set_state_graph(blueprint, enum_asset)
    if blueprint_modified:
        if not unreal.BlueprintEditorLibrary.compile_blueprint(blueprint):
            raise RuntimeError("Compile failed before creating Debug_RunDummyFlow")
    if unreal.BlueprintEditorLibrary.find_graph(blueprint, DEBUG_FUNCTION) is None:
        raw_names = _discover_internal_enum_names(blueprint)
        raw_names_by_display = dict(zip(STATE_NAMES, raw_names))
        blueprint_modified |= _create_dummy_flow_graph(
            blueprint, raw_names_by_display
        )
    else:
        # A rerun must not dirty the Blueprint merely to rediscover literals that
        # are only needed while constructing the debug graph.
        blueprint_modified |= _create_dummy_flow_graph(blueprint, {})
    _compile_and_check_graphs(blueprint)
    _save_assets([blueprint if blueprint_modified else None])

    _ensure_manager_in_map(blueprint)
    if not _validate(blueprint, enum_asset):
        raise RuntimeError("Game-flow scaffold validation failed")
    _log("PASS game-flow scaffold completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exception:
        _error("FAIL: {0}".format(exception))
        raise
