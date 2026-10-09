# Checkpoint crash investigation — October 10, 2026

This is the current safety report for the rejected October 9 integration checkpoint. It supersedes the earlier approval and terminal-work statements in the historical reports below and in the October 10 dialogue report.

- **Checkpoint crash repair: PARTIAL. Safe to commit: false. Ready for approval re-audit: no.**
- **Crash reproduced: YES. Full rendered validation: FAIL.** A complete JSON and all passing assertions do not override `0xC0000005` / `-1073741819`.
- **Observed source: engine/editor runtime shutdown (Core/Slate heap destruction).** The native fault was captured after Unreal logged normal exit. The exact retained Slate owner is not established; there is no proven validation cleanup fix or production Blueprint fix.
- **Natural dialogue plumbing: PASS. NullRHI regression: PASS. Blueprint compile: PASS (12/12).** Product E2E remains FAIL.
- **Startup condition errors: EXPLAINED. Production-map cook smoke: PASS with warnings.** No packaged build was produced.
- Branch remains `feature/overnight-integration-2026-10-09`; HEAD remains `69d835ccdbbe887567d4527e12ec9e3d3a8a4a20`.

## Separate blockers

1. **Product / E2E:** `/Game/CustomerDialogue` still contains only the blank `NewRow`. Live customer/dialogue/mood mapping is absent. Last natural stage: production Greybox startup -> customer spawn/entry/Ready -> root DialogueManager.StartDialogue -> exactly one dialogue widget showing the blank row. Automated Next still finishes dialogue and restores Explore/input. Fixtures and injected FinishResult are isolated checks, not natural customer-cycle completion.
2. **Checkpoint safety:** intermittent native access violation during editor process shutdown remains unresolved, including a fresh full D3D12 run. Neither authored dialogue nor unavailable contributor assets explain away this gate.
3. **Independent downstream work:** LP audio and turntable completion notification/Flow handoff, recommendation request/scoring/result contracts and natural Result UI consumption, unavailable contributor mesh/request/presentation binaries, and complete natural E2E remain outstanding. Startup diagnostics are now explained and the current map cooks. Packaging, deterministic repeat-cook equivalence and contributor asset approval are not claimed. Further independent investigation remains possible; autonomous work is not exhausted.

## Rendered process isolation

All runs used the installed UE 5.8.2, CL 56702186. Rendered runs selected D3D12/SM6 on the RTX 3070; NullRHI is recorded separately. Each completed scope has a generated script, exact argv, runtime JSON, log and `-process.json` in ignored `Saved/CheckpointCrashRepair/`. Process JSON records completion, Python fatal state, exit code/hex, final assertion and teardown markers. The reviewable runner additionally checks the expected assertion and compile counts and returns failure for a native exception.

The table's assertion column describes test logic only. Every `0xc0000005` row is a **process FAIL**, despite the assertions passing. Editor-only controls have no gameplay assertions.

| Scope | Assertion groups | Unreal exit | Last assertion | Evidence prefix |
| --- | --- | --- | --- | --- |
| Full D3D12 baseline | 16 / all passed | 0x0 | `selection_exit_cleanup_and_repeat` | `isolate-all` |
| A: natural dialogue observation | 1 / all passed | 0x0 | `dialogue_natural_ready_start_ui` | `isolate-natural` |
| B: Next and close | 2 / all passed | 0xc0000005 | `dialogue_natural_next_finished_explore` | `isolate-close` |
| Additional dialogue fixtures | 6 / all passed | 0xc0000005 | `dialogue_modal_cleanup_idempotent` | `isolate-dialogue` |
| C: Record Selection | 3 / all passed | 0x0 | `selection_reentry_cross_modal_and_all_records` | `serial-selection` |
| D: Turntable (selection setup included) | 8 / all passed | 0xc0000005 | `rpm78_widget_button_path` | `serial-turntable` |
| E: Enhanced Input | 3 / all passed | 0x0 | `physical_input_sphere_trace_interface` | `serial-physical` |
| Slate Escape / reopen | 3 / all passed | 0x0 | `slate_escape_close_reopen_and_unrelated_key` | `serial-keyboard` |
| F: customer exit / repeat cleanup | 4 / all passed | 0x0 | `selection_exit_cleanup_and_repeat` | `serial-exit` |
| Full NullRHI regression | 16 / all passed | 0x0 | `selection_exit_cleanup_and_repeat` | `serial-nullrhi` |
| Wait for PIE stop, trial 1 | 2 / all passed | 0x0 | `dialogue_natural_next_finished_explore` | `serial-staged-close-1` |
| Wait for PIE stop, trial 2 | 2 / all passed | 0x0 | `dialogue_natural_next_finished_explore` | `serial-staged-close-2` |
| Wait for PIE stop, trial 3 | 2 / all passed | 0xc0000005 | `dialogue_natural_next_finished_explore` | `serial-staged-close-3` |
| Final full D3D12, reviewable tool | 16 / all passed | 0xc0000005 | `selection_exit_cleanup_and_repeat` | `20261009T162338958811Z-0-all` |
| Editor startup only, no PIE, trial 1 | 0 / all passed | 0x0 | `N/A (editor-only control)` | `no-pie-startup-1` |
| Editor startup only, no PIE, trial 2 | 0 / all passed | 0xc0000005 | `N/A (editor-only control)` | `no-pie-startup-2` |
| 12 compiles only, no PIE | 0 / all passed | 0xc0000005 | `N/A (editor-only control)` | `no-pie-compile-1` |

The completed normal-shutdown scopes reached `request_end_play`, `end_play_request_returned`, callback unregistration and `quit_editor_returned`. The failed ones also reached `LogD3D12RHI: ~FD3D12DynamicRHI`, `LogExit: Exiting` and log closure. There was no accompanying fresh Blueprint error, Accessed None, ensure or UObject/widget destruction diagnostic in those logs. The delayed-shutdown experiment explicitly observed PIE stopped, waited two seconds, then quit; its third run still crashed. **Waiting for PIE completion is not a demonstrated repair.** This experiment remains opt-in, and the production validator's default shutdown was not changed.

The close-only reproducer executes no transient turntable spawn, in-memory dialogue fixture, Enhanced Input injection or customer exit. More decisively, `no-pie-startup-2` crashes after simply opening the production editor and calling quit: no PIE, project assertions, runtime customer/UI behavior, input injection or explicit Blueprint compilation. `no-pie-compile-1` also crashes without PIE. These controls rule out the isolated gameplay tests and their cleanup as necessary triggers. They do not establish which editor object retains the failing Slate tree.

A content-free minimal project using matching D3D12/SM6 renderer settings exited 0 three times (`minimal-sm6-1/2/3`). This is a control, not proof that the fault is impossible in the minimal project. A default SM5 minimal-project attempt was explicitly stopped during cold shader compilation and replaced with the matching SM6 control.

An early overlapping diagnostic run hit a separate PSO allocation error `8007000e` before testing (`isolate-selection`, exit 3). Two overlapping processes were deliberately stopped and are recorded in `aborted-overlap.json`; their exits were not retained by the stopped host and are not passing evidence. All affected scopes were rerun with only one rendered Unreal process at a time. The cook used NullRHI. No ensure, automation error or crash reporting switch was suppressed.

## Native shutdown evidence

A local Windows debug-event observer was tried both from process creation and by attaching only after the real Next assertion. The first five debugger observations exited normally; the third late-attach run (`late-debug-close-3`) captured **both first-chance and unhandled** `0xc0000005`, then the same process exit code. The access reads address zero at `ntdll.dll + 0x5fbb0`, after the Unreal log had closed.

The recorded stack words were unwound using the installed DLLs' x64 `.pdata` / unwind metadata, stopping when no recorded return address remained. Export names were accepted only where the export coincides with the containing function start. This identifies the chain through:

`LdrShutdownProcess -> CRT on-exit table -> Core static destruction -> Slate widget tree destruction -> SRichTextBlock::~SRichTextBlock -> FTextLayout::~FTextLayout -> Core text cleanup -> ucrtbase!_free_base -> ntdll!RtlFreeHeap -> native fault`.

Evidence: `late-debug-close-3-debug.json`, `unwound-from-candidate-stack.json`, `late-debug-export-candidates.json`, and the corresponding log. Raw stack candidates are separately labeled; misleading nearest-export labels for private functions are **not** treated as symbolized frames. Installed full engine PDBs are unavailable. Earlier three crash dumps under `Saved/OvernightIntegration/Round1/User/Saved/Crashes` are the historical widget-construction GUID ensures, not this failure.

A further independent native capture (`icu-shutdown-2-debug.json`) confirms the ICU free callback changes from nonzero while PIE is alive to **zero at the first-chance and unhandled exception**. For this installed Core DLL, the free-dispatcher callback is at RVA `0x1dd5f28`; initially it points to RVA `0x352d10`, whose machine code calls `FMemory::GetAllocSize` and `FMemory::Free`, matching `FICUOverrides::Free`. The dispatcher at RVA `0xbe9150` falls back to CRT free when that callback is zero. The second capture preserves full thread-context and stack bytes. A minidump write was attempted but returned `0x800703e6`; that partial file is not treated as a usable dump.

Installed `Core/Private/Internationalization/ICUInternationalization.cpp:115` installs Unreal's memory callbacks and `:212` terminates ICU via `u_cleanup`. `ICUText.cpp:344` implements the text BiDi object and its ICU string; `Slate/Public/Framework/Text/TextLayout.h:762` stores that object. The captured late Slate text destructor reaches CRT `_free_base` after the callback reset. **The supported mechanism is a late Slate/ICU lifetime and allocator mismatch during editor DLL shutdown.** The original allocation and the object retaining the rich-text widget were not individually identified, so that ownership detail remains unresolved; private function names inferred from nearby exports are not claimed as exact symbols.

The fault occurs after editor/PIE shutdown and during DLL static cleanup, not inside a Blueprint assertion or Python cleanup call. The editor-only reproducer requires no PIE or project tests. This supports the engine-runtime classification and does not justify altering production Blueprints or the working gameplay cleanup. No speculative cleanup or allocator workaround was promoted as a fix. The checkpoint still fails its normal rendered process gate.

## Startup condition failures

The 15 messages are engine Core smoke tests run at frame 0, before the project Python script or PIE. A fresh content-free project with no RecordShop assets reproduces all 15 and exits 0. Enabling `LogAutomationTest VeryVerbose` exposes the names:

| Engine test | Failed conditions under current Korean localization |
| --- | ---: |
| `FUnifiedErrorTest_CreateErrorMessage` | 7 |
| `FUnifiedErrorTest_CreateErrorMessageWithContext` | 4 |
| `FStructuredLogFormatTest` | 4 |

The same minimal-project control with command-line `-culture=en` runs those tests successfully with zero condition failures. This was a diagnostic comparison only: the validation launcher, project culture and normal diagnostics were not changed. `startup-comparison.json` records the original and English runs; the English helper reused the original result filename, so its process wrapper's `complete=false` means a missing per-name JSON, not an engine failure. Both logs contain the script-start marker after smoke tests and normal process exit.

Installed engine source explains the behavior: `Core/Private/Misc/AutomationTest.cpp:531` automatically runs SmokeFilter tests and disables stack capture for startup; `Core/Public/Misc/LowLevelTestAdapter.h:130` emits the generic Condition failed text. `Core/Tests/Experimental/UnifiedError/UnifiedErrorTests.cpp:479` and `:512` compare localized messages to literal English strings. `Core/Tests/Logging/StructuredLogFormatTest.cpp:21` contains the formatting smoke test. These are genuine engine-test failures under this localization, not RecordShop assertion failures, and they are not suppressed or relabeled as globally clean diagnostics.

## Production-map cook and dependencies

Target: `/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox`.

The initial default cook stalled trying to start Zen with an empty data directory; that attempt was deliberately stopped and retained as `cook-greybox`. The supported `-SkipZenStore` option selected the loose-file cooker without changing project settings. The second process completed: **exit 0, Success - 0 errors**, 593 packages cooked, seven skipped by platform, all 600 processed. Both configured Windows shader formats were retained. Global shader compilation took most of the run; the host watchdog was extended while packages were making progress rather than terminating a progressing cook.

Cooked map artifacts exist at `Saved/CheckpointCrashRepair/Cooked/RecordShop/Content/RecordShop/Maps/Greybox/L_RecordShop_Greybox.umap` (20,439 bytes) and `.uexp` (20,559 bytes). Exact arguments, full log and final process result are `cook-greybox-loose-command.json`, `cook-greybox-loose.log` and `cook-greybox-loose-process.json`.

No missing package/dependency, Blueprint cook error, redirector/reference failure or deterministic-cooking warning was found in that completed log. Ambient warnings include trace-server startup and certificate-store access. Cook's unique warning summary contains certificate access and an AsyncIoDelete output-cleanup warning; shutdown adds cleanup warnings for the generated output directories. The earlier Zen attempt left `ue.projectstore` in the shared temporary output root. These are retained, not suppressed. The cook-generated `Build/Windows/FileOpenOrder/CookerOpenOrder.log` was moved into the ignored evidence directory, preserving it without adding generated Build content to the dirty checkpoint. This is a successful current-map cook smoke check, not a release package, launch test or proof of repeated-cook determinism.

A separate read-only registry/load commandlet (`dependencies.json`, exit 0) traversed 166 packages, including 86 `/Game` packages. It found no missing packages or redirectors and compiled all ten Blueprint assets in that map's package-reference closure. This closure does not substitute for all config-driven or future contributor dependencies. The actual cook provides the broader current-target validation. Unavailable, not-yet-integrated contributor binaries remain unverified.

## Changes, preservation and reproduction

This crash-investigation round changes only:

- `Scripts/Unreal/isolate_checkpoint_shutdown.py` (new): serial scope isolation, fresh evidence names, explicit process exit gate, expected assertion/compile counts, editor-only controls and optional PIE-stop experiment. It generates reviewable copies of the existing checks, retaining their assertions and prerequisites. It neither saves assets nor changes the canonical validator's default behavior.
- `Docs/OVERNIGHT_INTEGRATION_2026-10-09.md` (this current safety addendum).
- `Docs/OVERNIGHT_INTEGRATION_2026-10-10.md` (supersession banner and corrected remaining-work conclusion).

The inherited four dialogue integration assets and original validation/installer scripts remain intact. SHA-256 comparison of all 399 Content/Config/project files against this task's starting worktree found no changes. HEAD and index timestamp remained unchanged. No reset, discard, stash, merge, commit, push, pull, fetch, staging or Git metadata write was performed. Test fixtures, logs, generated scripts and cook artifacts stayed outside production content in ignored evidence/cache locations.

Reproduction from the repository root, using host Python:

```powershell
python Scripts/Unreal/isolate_checkpoint_shutdown.py natural close dialogue selection turntable physical keyboard exit all
python Scripts/Unreal/isolate_checkpoint_shutdown.py all --nullrhi
python Scripts/Unreal/isolate_checkpoint_shutdown.py close --staged-shutdown
python Scripts/Unreal/isolate_checkpoint_shutdown.py editor-startup preflight
```

Run these serially. A nonzero Unreal exit always fails the diagnostic command, regardless of completed JSON. Normal startup smoke errors remain visible and explicitly counted. `reviewable-tool-check.json` verifies the new runner returns 0 for the complete NullRHI suite and 1 for the complete-but-crashed D3D12 suite. The fresh dialogue screenshot was inspected and shows one blank panel with Next, consistent with the authored row.

The complete dirty checkpoint still consists of these 12 files (11 inherited plus the new isolation tool):

- `Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset`
- `Content/RecordShop/Interaction/Actors/BP_RecordShelf.uasset`
- `Content/RecordShop/Interaction/Actors/BP_Turntable.uasset`
- `Content/RecordShop/UI/Dialogue/WBP_Dialogue.uasset`
- `Scripts/Unreal/Invoke-IntegrationPython.ps1`
- `Scripts/Unreal/validate_integration_round.py`
- `Scripts/Unreal/dialogue_handoff_checks.py`
- `Scripts/Unreal/integrate_dialogue_handoff.py`
- `Scripts/Unreal/resave_dialogue_integration.py`
- `Scripts/Unreal/isolate_checkpoint_shutdown.py`
- `Docs/OVERNIGHT_INTEGRATION_2026-10-09.md`
- `Docs/OVERNIGHT_INTEGRATION_2026-10-10.md`

## Historical report below — not the current safety verdict

The following pre-dialogue history is retained for provenance. Its old HEAD, feature gaps and validation verdicts describe earlier work only.

# Overnight Integration - 2026-10-09

## Current checkpoint and validation scope

This report supersedes the earlier report on this branch. It describes fresh validation at the HEAD below; the earlier production repairs are already committed and are not changes made by this worker round.

- Repository: `jllgame00/GameEngine-TermProject`.
- Worktree: `D:/univ/3-1/GameEngine/Termproject/RecordShop_overnight`.
- Branch: `feature/overnight-integration-2026-10-09`.
- Harness round: 1 / 3.
- Start/current HEAD: `9a723462a301659922fa30003092605991041b0c` (unchanged).
- Engine: Unreal **5.8.2**, CL 56702186, checked against installed Build.version and a fresh execution.
- Original Round1 PIE baseline started at `2026-10-09T14:06:30.308405+00:00` (23:06 KST). It completed with all seven isolated assertion groups passing and Unreal exit code 0. Checkpoint repair results are recorded separately below.
- **E2E: FAIL / BLOCKED.** Isolated downstream tests are not natural E2E evidence.
- **LAST NATURALLY VERIFIED STAGE:** Start -> customer spawn -> entry/seat route -> CustomerReadyForDialogue -> GameFlow Dialogue.
- **FIRST BLOCKER:** HandleCustomerReadyForDialogue only sets Dialogue state; it does not call DialogueManager.StartDialogue. There is no integrated dialogue UI/Next/finish path.
- **Integration dependencies remain outstanding.** Required latest contributor binaries were absent in the Round1 inventory, and historical exact-remote-ref LFS downloads failed on credentials/network restrictions. Current dialogue has no authored lines or agreed live-customer data mapping. A previous transient Editor Python fallback probe found the widget tree but could not set its protected RootWidget property; no incomplete widget was saved. These dependencies are not a terminal verdict on all local work.
- **Further autonomous work remains available: yes.** This repair extends physical interaction, RPM button and existing scoring-scaffold validation without contributor downloads. Dialogue handoff/UI plumbing, OS keyboard/mouse coverage and startup/cooking investigation remain possible locally. Missing binaries and authored contracts limit integration; they do not make further autonomous work useless.

## Changes and worktree hygiene

The checkpoint repair changes this report and validation tooling only: `Scripts/Unreal/validate_integration_round.py`, `Scripts/Unreal/checkpoint_repair_checks.py`, and `Scripts/Unreal/inspect_checkpoint_repair.py`. Production Content, Config and the project file remain untouched. No fetch or Git metadata write was performed during this repair; contributor download attempts described below are historical Round1 evidence.

Inherited repairs in HEAD include selection/turntable modal guards, Escape and input restoration, CustomerExited modal cleanup, Greybox startup configuration, and ActiveCustomer clearing. This round independently revalidated them rather than counting them as new implementation.

No asset/map was saved by the validation runs or the transient widget-construction probe. No binary asset editing, raw asset moves/renames, contributor branch merge, staging, commit, push, reset, or main/develop modification was performed. The shared Greybox map, BP_RecordGameInstance, root dialogue assets, and customer asset remain unchanged.

## Fresh validation verdicts

The baseline runtime script first observed natural flow for 15 seconds. It then invokes real Blueprint interactions, button delegates, and Slate key routing in an isolated UEDPIE world. Baseline exit was checked at approximately 45 seconds; the extended repair script checks at or after 60 seconds once diagnostics have completed. The script never calls Debug_RunDummyFlow.

| Gate / area | Verdict | Fresh evidence and limits |
| --- | --- | --- |
| Startup | VERIFIED PASS for editor/PIE | Initial editor world and UEDPIE world are L_RecordShop_Greybox; DefaultEngine.ini also points both startup/default maps there. Packaged startup remains unverified. |
| A. Customer | VERIFIED PASS for current route | Natural customer spawn/movement reaches Dialogue and stays there throughout the observation window. Current readiness graph supplies the state transition. Contributor movement polish is not imported. |
| B. Dialogue | PARTIAL scaffold; FAIL handoff | DialogueManager compiles, but fresh graph export confirms no StartDialogue call or integrated dialogue UI in GameFlow. CustomerDialogue has one blank row. UI update/Next/finish/input restoration are unverified. |
| C. Record selection | VERIFIED PASS in isolated PIE | Repeated interactions across two shelves create one widget and block turntable UI. Each BTN_LP01/02/03 delegate forwards its ST_RecordData to CurrentRecord/HasRecord, closes selection, and hides the cursor. Baseline direct Actor.Interact calls did not validate physical interaction; the repair coverage and limitations are recorded below. The actual component uses a sphere trace, not a line trace. |
| Modal safety | VERIFIED PASS for current two interaction UIs | Repeated turntable interaction creates one widget and blocks selection. Escape closes/reopens each UI twice; F10 leaves it open. Cursor/input restoration and cleanup pass. Dialogue and Result modal safety cannot be claimed before their integration. |
| D. Turntable | PARTIAL overall; RPM45/78 event paths PASS | Invalid step-zero operations are rejected; valid order advances 0 -> 1 -> 2 -> 3 -> 4 -> 5 at RPM 33. The repair also verifies RPM45 and RPM78 through WBP_Turntable buttons. Repeated PlayRecord stays at 5. A transient actor with HasRecord=false rejects playback at step 4. Audio=None only exercises the placeholder branch. Actual audio and TurntableCompleted remain unverified. |
| E. Recommendation | PARTIAL scaffold audit; BLOCKED integrated output | Existing CalculateLPScore and EvaluateLP behavior is now inspected and exercised; see repair findings below. Latest request/turntable binaries remain absent and selected-record -> request -> consumed recommendation is not established. No vocabulary, threshold, or result was invented. |
| F. Result / exit | PARTIAL overall; VERIFIED PASS isolated exit/cleanup | Diagnostic FinishResult invokes ResultFinished and customer exit; CustomerExited clears ActiveCustomer, returns Explore, closes turntable UI, and restores cursor/input. Repeated exit consumer also clears selection UI. Natural Result UI/completion is absent. |
| G. Natural E2E | FAIL / BLOCKED | Natural progress stops at Dialogue before StartDialogue. All later injected operations are isolated regression evidence only. |
| Real turntable meshes | UNVERIFIED / BLOCKED | All four canonical mesh binaries are absent; dependencies, transforms, pivot placement and motion cannot be inspected. |
| Packaging | UNVERIFIED / deliberately omitted | Vertical slice does not pass; packaging/startup smoke test is deferred under priority 9. |

The original baseline compiled seven Blueprints successfully: BP_GameFlowManager, BP_RecordShelf, BP_Turntable, WBP_RecordSelect, WBP_Turntable, BP_Customer, and root DialogueManager. The repair reruns compilation and also covers the player, controller, interaction component and interface.

All seven original baseline assertion groups passed: no-record playback rejection; all-record selection/re-entry/cross-modal guard; turntable re-entry/cross-modal guard; valid/invalid turntable order; Slate Escape/reopen/unrelated-key behavior; exit cleanup; repeated selection exit cleanup. `exit_before` is an observation, not an eighth assertion.

Runtime uses NullRHI, offscreen Slate, and no sound. It validates execution, widget counts, key routing and lifecycle state, not visual design, mesh appearance or audible playback. The cited `round1-baseline.log` contains **15** startup `LogAutomationTest: Error: Condition failed` messages, confirmed by a fresh count (lines 1526-1540), plus network warnings. Their cause has not been established as a production regression, but they prevent claiming a globally clean log. They are not passing automation tests; the seven baseline PASS verdicts apply only to the explicit script assertions. No Blueprint `Accessed None`, infinite-loop or fatal-error entry was found by the focused log scan.

Fresh graph inspection and runtime forwarding preserve the authoritative path:

`WBP_RecordSelect -> BP_RecordShelf.RecordSelected -> BP_GameFlowManager.HandleRecordSelected -> BP_Turntable.SetRecord / CurrentRecord / HasRecord`.

## Checkpoint repair: player input and RPM button paths

`repair-runtime.json` records the extended PIE run started at `2026-10-09T14:30:33.659441+00:00` (23:30 KST). Its first 15 seconds remain observation-only; all subsequent positioning, input injection and downstream actions are isolated diagnostics. Eleven Blueprints/interfaces compile successfully: the original seven plus BP_ThirdPersonCharacter, BP_ThirdPersonPlayerController, BPC_Interaction and BPI_Interactable.

Final runtime verdict: **complete=true, no fatal exception, all ten assertion groups PASS, Unreal exit code 0**. These are the original seven groups plus physical input and the two RPM button groups. Natural progress still stops at GameFlow Dialogue. The final runtime log again has 15 startup condition messages, two existing missing-NodeGuid cooking warnings, and no focused Accessed None/infinite-loop/fatal matches. No globally clean log or successful cook is claimed.

**PHYSICAL TRYINTERACT: PASS for the automated player-input/trace/interface path.** The real local player's active Enhanced Input mapping includes E -> IA_Interact. The test injects IA_Interact through EnhancedInputLocalPlayerSubsystem; it does not call Actor.Interact, TryInteract or the generated input handler. The saved player graph connects IA_Interact.Started to BPC_Interaction.TryInteract. That component executes a sphere trace from owner location along owner forward, distance 180 and radius 60, on the Interactable channel (TraceTypeQuery3 / Python ECC_INTERACTABLE), then checks and calls BPI_Interactable.Interact on the hit actor.

The test positions the live pawn near one existing shelf and the production turntable and records a matching sphere hit on its actual InteractionVolume: shelf sweep distance 40, turntable approximately 79.58. Injected action opens exactly one appropriate widget owned by the player. After modal cleanup, reversing the pawn's direction produces no hit and no widget for both targets. The test restores pawn transform/movement and modal state. Limits: this is synthetic Enhanced Input with transient pawn positioning, not an OS E-key or natural walking/navigation test; the saved mapping and active runtime mapping are both inspected.

**RPM45 UI PATH: PASS. RPM78 UI PATH: PASS.** Each uses a fresh transient turntable with a current test record and the real WBP_Turntable instance. OnClicked broadcasts drive BTN_OpenLid -> BTN_PlaceRecord -> BTN_SelectRPM -> BTN_RPM45/78 -> BTN_MoveTonearm -> BTN_Play. The test verifies the widget's TurntableRef, steps 0 -> 1 -> 2 -> 3 -> 4 -> 5, exact SelectedRPM, RPM options becoming Visible at step 2 and Collapsed after selection, rejection of the selector outside step 2, and repeated Play remaining at 5. No direct RPM function call substitutes for the widget event. Limits: button delegates are exercised, not pointer hit testing; the selected records have Audio=None.

Three earlier runtime attempts are retained as `repair-runtime-attempt1/2/3.json` and matching logs. Their physical-input assertions failed on test-tool API lookup/conversion errors before action injection. They are not passing evidence and do not establish production defects. The final run uses reflected subsystem lookup and the inspected custom collision enum.

## Checkpoint repair: existing recommendation scaffold

Fresh read-only graph exports and transient-object calls are in `repair-inspection.json`. All seven inspected Blueprints/interfaces compiled. The probe completed without an exception; it never saves an asset or changes production scoring.

- `CalculateLPScore` resets its local TempScore and adds one for each exact string match: Mood against CurrentMood, Preference against CurrentCustomer.MusicPreference, and Personality against CurrentCustomer.Personality. CurrentCustomer.Mood is not used by this comparison. All eight match/nonmatch combinations against the current blank defaults produced the observed 0-3 sum; all blank inputs score 3 and all nonmatching inputs score 0. These are existing implementation semantics, not approved design rules or authored customer evidence.
- `EvaluateLP` accepts three strings and an AvailableLPs **Text array**, resets MaxScore to 0, then iterates the array. Its Array Element output is disconnected. The loop's CalculateLPScore inputs are blank/unconnected. If the score exceeds MaxScore, the Set MaxScore node reads the old MaxScore back into itself instead of the calculated score.
- The loop Completed pin calls CalculateLPScore with the event's three strings, but that call's execution output is disconnected. Its score feeds a `>=` comparison whose Branch has no execution input and no connected true/false outputs. There is no chosen LP output, return value, result broadcast or consumer on this path. Calls with empty, one-item and two-item fixture arrays, each with blank and nonmatching strings, all returned None and left MaxScore=0.
- `StartDialogue` still selects the single blank NewRow and advances CurrentLineIndex to 1; ShowNextLine leaves the index at 1. Graphs contain update/finished broadcasts, but a live integrated UI and customer/request mapping remain absent.

Recommendation scaffold verdict is **PARTIAL**: current calculation and disconnected output behavior are verified; usable recommendation output is blocked. Although the MaxScore self-assignment is mechanically wrong for tracking a maximum, fixing that alone would leave the unused LP entries and disconnected result path. No production repair is necessary to complete this audit, and choosing LP metadata, result semantics or output consumers would require a contract. Production scoring was left untouched.

## Historical Round1 contributor audit (no fetch during repair)

Refs were resolved by name from the current local remote-tracking refs and match the harness's latest fetched heads. No new successful online fetch is claimed.

| Ref | Resolved HEAD | Decision |
| --- | --- | --- |
| origin/develop | aa1b9a440d1cd21205c34bf79e0027596cc21cc6 | Baseline only; unchanged. |
| origin/feature/environment-art | 9927497acf49c433034bdf520d3ad5c6a20398ee | Four canonical turntable meshes identified; binaries unavailable. No wholesale merge or Test Map import. |
| origin/feature/turntable-recommendation | 2edde0dc4b4ac7fcb5a58319b481de8a429e0620 | Latest ST_CustomerRequest and BP_Turntable binaries unavailable. Completion/audio/recommendation logic cannot be safely inspected or ported from commit text. GameInstance ownership must remain excluded. |
| hyeon-fork/feature/ui-presentation | f5a66494ca7de7edcb50b3fadfa1038015ca336d | WBP_Dialogue and WDP_SelectionResult binaries unavailable. Rejected RecordSelection families not imported. Future canonical-folder relocation must use Unreal Editor asset operations. |
| origin/feature/customer-ai | 9e7d6a7901862a125dcf59e5603ff243fa61abb4 | Genuine movement/test-flow polish after the develop merge; affects BP_Customer and private L_CustomerAI_Test. New customer binary absent. Current passing route preserved. |
| origin/feature/dialogue-data | df6774f5faf274eb83b57600aa347bb3605121f6 | All four authoritative root assets match HEAD at Git/LFS-pointer level. No newer authored dialogue identified. Organized duplicates are not restored. |

Fresh inventory checks found all nine targeted objects absent in both shared and workspace-local LFS caches: four meshes, ST_CustomerRequest, latest BP_Turntable, two dialogue/result widgets, and latest BP_Customer.

Targeted hydration attempts used an absolute workspace-local `lfs.storage` and command-scoped Git options:

- Initial calls using short `feature/...` names resolved local heads, not the required remote-tracking heads. Their apparent success did **not** hydrate the latest candidates. One unrelated older LFS object is present in the ignored local cache; no production asset was imported from it. The initial progress message about successful UI downloading was corrected after this check.
- Retried using the explicit latest remote-tracking refs. Origin mesh and turntable/request fetches failed because Git credentials were unavailable and credential-helper execution failed. The recorded exact-ref turntable fetch exit code is 2.
- Exact-ref fork dialogue/result UI fetch failed because configured proxy `127.0.0.1:9` refused the connection; exit code 2.
- Future hydration must use full `refs/remotes/origin/...` or `refs/remotes/hyeon-fork/...`, or a SHA freshly resolved from those refs. A zero fetch exit code for a short local branch name is not evidence that the latest candidate OIDs exist.

No credentials, proxy settings, security settings, persistent Git configuration, or Content files were changed by these attempts. No unresolved LFS pointer was written into production Content.

## Content and implementation blockers

Fresh Unreal export of CustomerDialogue contains exactly one row, NewRow: DialogueID=None; Speaker/Text/Mood/MusicPreference empty; IsEndNode=false.

Root DialogueManager is an ActorComponent with empty CurrentMood and DialogueList defaults. Its existing dialogue/scoring scaffold is not connected to GameFlow. GameFlow has no DialogueManager member or dialogue UI integration. Current live BP_Customer exposes route targets and lifecycle dispatchers, with no authored customer-data mapping established by the inspected current defaults. Wiring blank values into a fabricated customer context would not establish content readiness.

Priority 1/2 next work is to integrate a usable DialogueManager with update/finished bindings and one dialogue widget; content readiness must remain partial until actual authored lines and the customer mapping exist. Blank content alone does not prohibit plumbing work. The intended contributor widget cannot currently be loaded/migrated, and the attempted local creation fallback hit protected Editor Python properties. The fresh unsaved probe successfully found `WidgetTree` through `unreal.find_object`, then failed at `tree.set_editor_property('RootWidget', root)`. This establishes a limitation of that attempted API path, not that Unreal cannot create a dialogue UI. No native plugin, property-protection bypass, binary patch or unfinished production handoff was introduced.

Independent priority 3 already passes. Mesh, contributor recommendation and Result presentation integration remain blocked by their missing binaries; scoring also needs agreed request semantics. Existing test LP records have Audio=None and Cover=None; no audible playback or completion result can be claimed from them. Existing exit cleanup passes when invoked diagnostically. Packaging and visual/pivot approval remain deliberately deferred.

No narrative dialogue, authored result text, customer metadata, tag vocabulary, or scoring semantics were invented. No completion event was falsely emitted at placeholder audio start. No full day/customer queue was added.

## Evidence and reproduction

Repair evidence under ignored `Saved/OvernightIntegration/Round1/`:

- `repair-runtime.json` and `repair-runtime.log`: final 11 compiles, ten assertion groups, trace hit details, active E mapping, both RPM event sequences, natural samples and isolated cleanup; exit code 0.
- `repair-inspection.json` and `repair-inspection.log`: fresh graphs, default input mapping, eight CalculateLPScore combinations and six EvaluateLP calls; complete=true, no fatal exception, exit code 0.
- `repair-runtime-attempt1/2/3.json` and matching logs: failed test-tool discovery attempts, excluded from final PASS evidence.
- `repair-summary.json`: explicit verdict aggregation and per-log condition/error/NodeGuid counts. `repair-production-hashes.json` verifies all 398 Content/Config/project files remain byte-identical across the final runtime run; Git scope also shows no production changes.

Original Round1 evidence under ignored `Saved/OvernightIntegration/Round1/` (preserved separately from repair outputs):

- `runtime.json`: run timestamp, complete=true, seven passing assertion groups, seven successful compiles, natural samples, authored table, and diagnostic boundary.
- `round1-baseline.log`: actual fresh PIE execution and shutdown, exit code 0.
- `graphs-current.json` and `round1-graphs.log`: fresh read-only Unreal graph/default/table/map inventory; commandlet exit code 0 and no per-asset inspection exceptions.
- `contributor-round1.json`: ref-resolved candidate OIDs and both cache-presence checks.
- `round1-lfs-turntable.txt` and `round1-lfs-ui.txt`: exact-remote-ref, absolute-local-cache download failures.
- `dialogue-probe.py`, `dialogue-probe.json`, and `dialogue-probe.log`: unsaved widget-construction attempt and protected RootWidget exception. Commandlet exit code 0 is not a successful construction verdict; the JSON records the exception.

Older evidence files in that directory belong to prior runs and are not substituted for this round's observations. Generated logs/JSON/cache files remain ignored and are not harness commit deliverables.

Reproduce the runtime checks from the repository root:

```powershell
./Scripts/Unreal/Invoke-IntegrationPython.ps1 -Script Scripts/Unreal/validate_integration_round.py -Name repair-runtime -Editor
./Scripts/Unreal/Invoke-IntegrationPython.ps1 -Script Scripts/Unreal/inspect_checkpoint_repair.py -Name repair-inspection
```

Read JSON with UTF-8 explicitly in Windows PowerShell. The commands write `repair-runtime.json` and `repair-inspection.json`. Inspect `complete`, `fatal`, every assertion, and the log; Unreal exit code 0 alone is not a test verdict. The runtime script invalidates stale JSON before preflight. Neither its passing isolated tests nor any manually injected FinishResult proves natural E2E.

No commit, push, fetch, staging or Git metadata write was performed during this checkpoint repair. The report and three validation scripts are the only changed files; HEAD remains `9a723462a301659922fa30003092605991041b0c`. Independent re-audit must distinguish successful isolated checks from the still-failing natural E2E.
