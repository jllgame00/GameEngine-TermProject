# RecordShop Greybox Generation

`Scripts/Unreal/create_recordshop_greybox.py` is an Unreal Editor Python
automation source file for the first-pass RecordShop greybox.

Target map:

`/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox`

The source files in `Scripts/Unreal/` are intended to be executed by Unreal
Editor after the editor's Python scripting environment has been verified.
They must not be run with the operating-system Python interpreter.

## Safety behavior

Before calling `LevelEditorSubsystem.new_level()`, the greybox-generation
script checks whether the target map already exists. It prefers
`EditorAssetSubsystem` and falls back to `EditorAssetLibrary` only when the
newer subsystem API is unavailable.

If the map exists, the generator logs a clear no-overwrite message and exits.
If the existence query fails, it fails closed and exits rather than risking an
overwrite. It never deletes an existing map.

Before creating a new level, it logs that `LevelEditorSubsystem.new_level()`
will close the current persistent level without saving it. Save any current
work before running the generator.

If generation fails after the new level is created, the script logs that the
map may be partially generated and tells the user to inspect/delete it
manually before retrying. No automatic rollback is claimed or attempted.

## Coordinate and room specification

All dimensions use centimetres. X is left/right, Y is front/back, and Z is
up. The entrance is at -Y and the shop interior extends toward +Y.

The room target is 900 cm wide, 1200 cm deep, and 320 cm tall:

| Label | Location | Dimensions |
| --- | --- | --- |
| `GB_Floor` | `(0, 0, -10)` | `(900, 1200, 20)` |
| `GB_Wall_Left` | `(-460, 0, 160)` | `(20, 1200, 320)` |
| `GB_Wall_Right` | `(460, 0, 160)` | `(20, 1200, 320)` |
| `GB_Wall_Back` | `(0, 610, 160)` | `(920, 20, 320)` |
| `GB_Wall_Front_L` | `(-265, -610, 160)` | `(370, 20, 320)` |
| `GB_Wall_Front_R` | `(265, -610, 160)` | `(370, 20, 320)` |

The split front wall leaves an approximately 160 cm centered entrance. No
ceiling, entry header, threshold, signage, or decorative lighting is created.

## Requested greybox actors

The generator creates the following actors only:

| Area | Actors |
| --- | --- |
| Listening bar | `GB_BarCounter`, `GB_Turntable`, `GB_Speaker_L`, `GB_Speaker_R`, `GB_CustomerSeat_01` |
| Records | `GB_RecordShelf_01`, `GB_RecordShelf_02`, `GB_RecordShelf_03` |
| Cafe/staff | `GB_CafeCounter`, `GB_CoffeeMachine` |
| Gameplay | `PlayerStart_Greybox`, only if no `PlayerStart` is already present |

The listening bar is at `(100, 400, 52.5)` with dimensions `(450, 75, 105)`.
The turntable is at approximately `(80, 400, 111)` with dimensions
`(45, 40, 12)`. The speakers are simple opposite-side placeholders at
`(-90, 400, 135)` and `(270, 400, 135)`, each `(35, 30, 60)`. The stool uses
the engine Cylinder mesh at `(80, 290, 60)` with a 60 cm diameter and 120 cm
height.

The three single-box shelves are each `(40, 120, 180)` at:

- `GB_RecordShelf_01`: `(-420, -250, 90)`
- `GB_RecordShelf_02`: `(-420, 0, 90)`
- `GB_RecordShelf_03`: `(-420, 250, 90)`

The cafe counter is at `(280, -300, 50)` with dimensions `(250, 70, 100)`.
The coffee-machine cube sits on top at `(280, -300, 125)` with dimensions
`(45, 40, 50)`. There is no player coffee gameplay.

If needed, the PlayerStart is created at `(0, -500, 100)` with yaw 90 degrees,
facing +Y into the shop.

## Meshes, helpers, and folders

The generator helpers are intentionally limited to:

- `spawn_cube(label, location, dimensions, folder=None)`
- `spawn_cylinder(label, location, diameter, height, folder=None)`

Both use engine meshes only:

- `/Engine/BasicShapes/Cube`
- `/Engine/BasicShapes/Cylinder`

The 100 cm engine Cube is scaled by `dimensions / 100`. Folder assignment is
attempted under these paths when the actor API supports it:

- `Greybox/Architecture`
- `Greybox/ListeningBar`
- `Greybox/Records`
- `Greybox/Cafe`
- `Greybox/Gameplay`

If folder assignment is unavailable, generation continues. The script does
not create TextRenderActor, PointLight, genre bins, listening booths, a
back-shelving system, checkout/register setup, feature display, ceiling, or
other decorative/invented actors.

## Gameplay Marker Pass

`Scripts/Unreal/add_recordshop_gameplay_markers.py` adds editor-only anchors
to the already-created `L_RecordShop_Greybox` map. It first verifies that the
map exists, then loads that exact map. It never creates a replacement map and
never deletes, moves, or modifies existing greybox actors.

Because `LevelEditorSubsystem.load_level()` closes the current persistent
level without saving it, save any unrelated work before running the marker
pass. The script compares requested labels against every actor in the loaded
level before spawning anything. Existing labels are logged and skipped, so it
is safe to run the pass more than once.

### Customer and interaction target points

These `TargetPoint` actors describe the first customer vertical slice:

`Customer enters → sits → dialogue → player browses LPs → player uses
turntable → listening/reaction → customer exits.`

| Actor | Purpose |
| --- | --- |
| `TP_CustomerSpawn` | Customer start point outside the front entrance. |
| `TP_CustomerEntry` | Entry point just inside the shop. |
| `TP_CustomerSeat` | Customer destination at `GB_CustomerSeat_01`. |
| `TP_CustomerExit` | Temporary exit point outside the front entrance. |
| `TP_RecordBrowse` | Player stance in front of the middle LP shelf. |
| `TP_TurntableInteract` | Player stance in front of the Listening Bar turntable. |
| `TP_DialogueStand` | Conversation stance near the customer seat. |

The script assigns customer-route points to `Greybox/Gameplay/Customer` and
interaction points to `Greybox/Gameplay/Interaction` when actor folder paths
are available. Folder-assignment failures are logged but do not stop marker
generation.

### Camera anchors

The three `CameraActor` placeholders are intentionally rough and must be
visually adjusted in Unreal Editor before any cinematic work:

| Actor | Intended framing |
| --- | --- |
| `CAM_Dialogue` | Player-side view toward the seated customer. |
| `CAM_RecordSelection` | LP shelf and player browsing area. |
| `CAM_Listening` | Customer/listening area and turntable when practical. |

They are organized under `Greybox/Gameplay/Cameras` when supported. They do
not modify the player's existing gameplay camera.

### Navigation setup

`NavMeshBoundsVolume` creation is deliberately deferred. The Python surface
for safely authoring and resizing a brush-backed volume is not relied on by
the marker script, so marker generation does not fake a navigation volume.

To add it manually in Unreal Editor:

1. Open `L_RecordShop_Greybox` from the Content Browser.
2. In the Place Actors panel, drag **Nav Mesh Bounds Volume** into the level.
3. Set its location near `(0, 0, 160)` and resize its brush bounds to cover
   the approximately `900 × 1200 × 320 cm` walkable shop interior.
4. Use **Build > Build Paths** (or the project's configured navigation build
   workflow) and enable the navigation visualization to verify coverage.
5. Keep the volume under `Greybox/Gameplay/Navigation` if Outliner folders
   are available.

The marker script saves the existing map only after every requested marker is
created or safely skipped. If an actor fails to spawn, it logs the failed
label and does not save the current level automatically.

## Unreal APIs to verify before execution

The source uses these UE 5.8 editor APIs:

- `unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)` and
  `does_asset_exist()` for the map guard.
- `unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)` with
  `load_level()`, `new_level()`, and `save_current_level()`.
- `unreal.get_editor_subsystem(unreal.EditorActorSubsystem)` with
  `spawn_actor_from_class()` and `get_all_level_actors()`.
- `unreal.StaticMeshActor`, `unreal.StaticMeshComponent`, `unreal.PlayerStart`,
  `unreal.TargetPoint`, and `unreal.CameraActor`.
- `Actor.set_folder_path()` when available.

Before execution, manually verify that the installed UE 5.8 build exposes
these subsystem methods and that `TargetPoint`, `CameraActor`, and folder-path
assignment behave as expected in the editor.

No `.umap` or `.uasset` is created or edited by these sources until one is
deliberately executed by Unreal Editor. They do not touch ThirdPerson template
assets, create a C++ module, modify `RecordShop.uproject`, commit, or push.
