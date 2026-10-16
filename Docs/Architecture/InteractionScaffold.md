# Interaction Scaffold

`Scripts/Unreal/create_interaction_scaffold.py` creates the first interaction
asset shells for the RecordShop vertical slice. It is editor-only automation:
run it manually inside Unreal Editor after the required editor scripting
plugins are enabled. It must not be run with system Python.

The script creates the four requested Content Browser folders if missing:

- `/Game/RecordShop/Input`
- `/Game/RecordShop/Interaction/Interfaces`
- `/Game/RecordShop/Interaction/Components`
- `/Game/RecordShop/Interaction/Actors`

Before each asset is created, the script checks both package-style and
object-style asset paths. Existing assets are logged and skipped. No existing
ThirdPerson asset, greybox map, GameMode, Character Blueprint, mapping context,
`.umap`, or `.uproject` is modified.

## Assets

| Asset | Intended role | Automation status |
| --- | --- | --- |
| `/Game/RecordShop/Input/IA_Interact` | Enhanced Input action for interaction | Created with `InputAction_Factory`; value type is set to Digital/Bool. |
| `/Game/RecordShop/Interaction/Interfaces/BPI_Interactable` | Common interaction contract | Blueprint Interface shell only. `Interact(Interactor: Actor Object Reference)` remains manual. |
| `/Game/RecordShop/Interaction/Components/BPC_Interaction` | Future player interaction component | ActorComponent Blueprint shell; attempts an empty `TryInteract` function graph and `TraceDistance`/`TraceRadius` float/real variables. Defaults remain manual. |
| `/Game/RecordShop/Interaction/Actors/BP_RecordShelf` | Interaction-volume actor over the greybox shelf | Actor Blueprint shell only. BoxCollision, interface implementation, and graph logic remain manual. No Static Mesh is added. |

The script saves newly created assets through the editor asset subsystem after
the scaffold pass. It never passes an overwrite flag to AssetTools.

## Existing input mapping

Repository inspection found the existing mapping context at:

`/Game/Input/IMC_Default`

The existing ThirdPerson PlayerController asset references this mapping
context. The likely path `/Game/ThirdPerson/Input/IMC_Default` is not present.
The script reports candidate contexts and, where supported, their asset
referencers. It does not edit the mapping context.

Manual mapping step:

1. Open `/Game/Input/IMC_Default` in the Content Browser.
2. Add `IA_Interact` as an action mapping.
3. Bind the keyboard `E` key.
4. Save the existing mapping context.

## Manual Blueprint setup

The script intentionally does not serialize Event Graph nodes or attempt
unsupported interface-signature/component-edit operations.

### BPI_Interactable

Open `BPI_Interactable` and add:

- Function: `Interact`
- Input: `Interactor`
- Type: Actor Object Reference

The interface function is a contract only; its implementation belongs to the
Blueprint that implements it.

### BPC_Interaction

Open `BPC_Interaction` and verify or add:

- Function: `TryInteract`
- `TraceDistance`: Float, default `180.0`
- `TraceRadius`: Float, default `60.0`

No Event Graph nodes are created by the scaffold. Add the future logic
manually:

`Owner → Forward Sphere Trace (about 180 cm, radius 60 cm) → Hit Actor → Does
Implement Interface (BPI_Interactable) → Interact`

### BP_RecordShelf

Open `BP_RecordShelf` and manually:

1. Keep `DefaultSceneRoot`.
2. Add a `BoxCollision` component sized to the interaction volume.
3. Add `BPI_Interactable` under Class Settings → Interfaces.
4. Implement `Interact` with a Print String node containing exactly:
   `Record Shelf Interacted`.
5. Do not add a Static Mesh in this scaffold pass.

### Player Character

Open the existing `BP_ThirdPersonCharacter` and add `BPC_Interaction` as a
component. Do not replace or redesign the existing character. In the existing
input handling, connect:

`IA_Interact Started → BPC_Interaction.TryInteract`

The exact component-reference and Enhanced Input event wiring remain manual.

### Place the shelf actor

After `BP_RecordShelf` is configured, place it over the existing greybox actor
`GB_RecordShelf_02`, approximately at its current location `(-420, 0, 90)`.
The Blueprint should serve as an interaction volume over the shelf; it should
not replace or delete the greybox actor.

## Automation boundary

The safe automated portion is limited to AssetTools creation, folder creation,
the Boolean InputAction value type, Blueprint parent-class shells, the empty
`TryInteract` graph, and the two typed interaction variables where
`BlueprintEditorLibrary` supports them. The script does not create interface
parameters, component templates, implemented-interface entries, default values,
Event Graph nodes, or input mappings.

This boundary follows the documented editor APIs for `AssetTools.create_asset`,
`InputAction_Factory`, `BlueprintFactory`, and
`BlueprintEditorLibrary.add_function_graph` / `add_member_variable`. Verify
the installed UE 5.8.2 editor surfaces before execution.

## PASS condition

After the manual Blueprint and input setup:

`approach shelf → press E → "Record Shelf Interacted"`

The pass is complete when the message appears while interacting with the
`BP_RecordShelf` volume over `GB_RecordShelf_02`.
