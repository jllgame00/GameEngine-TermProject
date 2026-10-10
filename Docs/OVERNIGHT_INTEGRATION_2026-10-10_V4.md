# V4 MVP integration - October 10, 2026, repair 1

This is the current report for harness round **1 / 5**, rejected-checkpoint repair **1 / 2**. Branch: `feature/overnight-integration-2026-10-09`; unchanged HEAD: `99530e9071e0aba58b3a7db15ca8cff294b3979c`. Engine: UE 5.8.2 / CL 56702186. The original dirty checkpoint was preserved. No Git writes, fetch, staging, commit, push, reset, branch merge, or binary-file manipulation was performed.

## Current outcome and correction of the rejected conclusion

**Terminal B: HUMAN DEPENDENCY**, after the repair and fresh checks below. The available mechanical customer cycle is exercised through Explore, including default Result focus and ordinary UI completion. Authored dialogue, meaningful live recommendation semantics, contributor assets, physical human-input observation and a permitted packaging environment remain unavailable. This is a worker handoff for independent safety audit, not self-approval to commit or an authored-product completion claim.

The rejected checkpoint was **not** terminal: safe independent work remained. It targeted the non-focusable Result UserWidget with `SetInputMode_UIOnlyEx`; opening Result emitted `LogPlayerController: Error: InputMode:UIOnly - Attempting to focus Non-Focusable widget SObjectWidget`. Its tests explicitly focused Continue and its runner ignored gameplay log errors. The previous Result readiness PASS, globally clean gameplay implications and terminal conclusion were incorrect. The old report is retained at `Saved/MVPCompletion/rejected-worker-report-before-repair1.md`; old evidence remains intact.

The actual production repair changes GameFlow's Result input-mode focus pin to **`ResultWidgetRef.Continue`**, the existing focusable button. The root widget does not need to become focusable. No UI delegate, customer event, completion function, scoring rule or downstream state was injected to make this work. The graph was compiled and saved through supported Editor APIs.

- **Natural mechanical E2E: VERIFIED PASS**, both rendered and NullRHI, with explicitly synthetic inputs and the unchanged blank dialogue fixture.
- **Result default focus and native-window Enter: VERIFIED PASS** in the rendered run, without test-side Result focus correction. Result Continue, actual customer navigation/exit, cleared ActiveCustomer and modal references, hidden cursor and Explore were observed.
- **Rendered process: PASS for the current bounded functional run**, exit 0, no unexpected gameplay/runtime errors. The separate exact engine startup smoke errors remain reported; the process is not globally error-free. Earlier crashing runs remain FAIL/PARTIAL and are not waived.
- **Compilation / dependencies / bounded cook: VERIFIED PASS** on repaired production assets. **Packaging: FAIL / external permission dependency** from actual retained attempts; no successful package or packaged launch exists.
- **LAST NATURAL STAGE:** `CustomerExited -> ActiveCustomer=None -> all modals/reference cleanup -> cursor hidden -> Explore`.
- **FIRST PRODUCT BLOCKER:** blank `BP_Customer.CustomerProfile` and `/Game/CustomerDialogue/NewRow`. Mechanical blank-row progression is not authored narrative readiness. No remaining mechanical blocker was observed in the exercised cycle.

## Eight-area inventory, re-evaluated after repair

| Ordered target | Status | Current evidence and concrete remaining work |
|---|---|---|
| 1. Live customer / dialogue data | **PARTIAL** | ActiveCustomer.CustomerProfile uses authoritative `/Game/CustomerData`; Ready copies the exact profile to root DialogueManager.CurrentCustomer and its Mood to CurrentMood before StartDialogue. Fresh nondefault-profile/mood diagnostic passes. Customer defaults and the one root NewRow remain blank. Author values and decide any identity-specific DialogueID join; none is invented. |
| 2. Natural dialogue flow | **VERIFIED PASS mechanically; authored content PARTIAL** | Production spawn/entry/seat/Ready opens one root-managed Dialogue UI; synthetic Slate Next traverses ShowNextLine/OnDialogueFinished, closes/clears it, restores input and advances to RecordSelection. Duplicate Ready, premature Result, unmatched mood, late Finished and cross-modal diagnostics pass. |
| 3. Turntable completion | **VERIFIED PASS mechanically; content PARTIAL** | Ordered RPM33 Play naturally emits playback-start/completion and opens Result. Audio=None deterministically completes the interaction without audible playback. Fresh isolated RPM45/78, order/no-record, duplicate completion and record-replacement guards pass. An existing engine notification sound exercises a real AudioComponent/OnAudioFinished once; real LP audio and canonical meshes remain absent. |
| 4. Recommendation | **PARTIAL** | Existing Mood/MusicPreference/Personality equality scoring (one point each) and OnLPScoreEvaluated raw output pass all eight combinations. MaxScore receives candidate Outscore instead of itself. Existing AvailableLPs elements remain unused; candidate inputs are blank. ST_RecordData has no established Preference/Personality lookup. Authoritative catalogue mapping and qualitative rules are needed; no live score or Good/Bad rule is fabricated. |
| 5. Result flow | **VERIFIED PASS for integration fallback** | One permitted `/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback` displays Title/RecordID and `Score: unavailable`. Production focuses Continue; rendered synthetic native Windows Enter completes it without focus correction. NullRHI uses ordinary virtual-user Tab/Enter after checking the owning player's default focus. Duplicate opening/Continue and modal exclusion pass. Contributor presentation remains unavailable. |
| 6. Customer exit | **VERIFIED PASS** | Actual Continue -> guarded FinishResult -> existing ResultFinished AI exit route -> CustomerExited -> ActiveCustomer cleared and Explore. Customer movement graphs match the pre-repair export. No exit teleport or forced CustomerExited is part of E2E. |
| 7. Natural MVP E2E | **VERIFIED PASS, mechanical-only** | Two repaired full contiguous cycles completed with normal input/UI/gameplay handlers. Rendered Continue uses the production keyboard focus; all inputs and geometry setup are disclosed below. Physical human input and authored narrative are not validated. |
| 8. Cook / package readiness | **PARTIAL overall** | Thirteen relevant Blueprint/interface compiles pass in each cycle. Fresh map closure: 167 packages, 87 /Game, 11 closure Blueprint compiles, no missing package/redirector/compile failure. Bounded Windows cook: 594 cooked, seven platform-skipped, zero errors; map and Result output exist. Packaging remains permission-blocked; retained shutdown failures remain unresolved historical external observations. |

## Preserved contracts and scope of the whole checkpoint

The single record-selection authority remains:

`WBP_RecordSelect -> BP_RecordShelf.RecordSelected -> BP_GameFlowManager.HandleRecordSelected -> BP_Turntable.SetRecord`.

BP_Turntable owns CurrentRecord/HasRecord. A new selection resets its step/RPM/completion guard; a record cannot replace active PlaybackAudio. Audio=None completes synchronously after the normal ordered Play action. Real audio uses CreateSound2D -> bind OnAudioFinished -> Play -> guarded CompletePlayback. Flow consumes completion only for the live customer in Listening, once per result cycle. Audio creation failure retains the retryable ordered step. GameInstance selected-record authority was not restored.

CustomerData is the existing UserDefinedStruct with CustomerID, Name, VisitReason, Personality, Mood, MusicPreference, Hint (bool), PreferredTags (bool). CustomerProfile is a typed actor carrier with blank defaults, not an authored customer table. Root DialogueManager still filters root CustomerDialogue by exact Mood equality. Identity is carried, not joined to DialogueID. Authoritative data assets remain `/Game/CustomerData`, `/Game/DialogueData`, `/Game/CustomerDialogue`, `/Game/DialogueManager`; no obsolete organized duplicate was restored.

ST_RecordData has RecordID, Title, Artist, Genre, Mood, Energy, Theme, Cover, Audio. Genre-to-MusicPreference and Energy/Theme-to-Personality mappings do not exist. The original candidate loop does not read AvailableLPs entries. Its blank candidate inputs happen to score 3 against the blank fixture; validating the MaxScore assignment does not make that a meaningful catalogue maximum. The natural cycle does not invoke scoring with invented values. Result's explicit score unavailability preserves that limitation.

Dialogue, selection, turntable and Result each retain guarded modal ownership and explicit close/input restoration. Selection close unbinds OnRecordSelected. Turntable close synchronously clears TurntableRef. Result close unbinds OnContinue, removes the widget, clears references and restores input. Destruct remains a secondary safeguard, since it can be delayed by Slate. No general UI-manager rewrite or queue/day system was introduced.

## Changed files and review coverage

The entire dirty checkpoint was inspected, including all script/report changes, current graphs/defaults, and local contributor inventory. Eight production assets are changed/new from HEAD; only GameFlow changed further during this repair:

- `Content/DialogueManager.uasset`
- `Content/RecordShop/Characters/Customers/Common/BP_Customer.uasset`
- `Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset` - repaired Result focus target.
- `Content/RecordShop/Interaction/Actors/BP_RecordShelf.uasset`
- `Content/RecordShop/Interaction/Actors/BP_Turntable.uasset`
- `Content/RecordShop/UI/RecordSelection/WBP_RecordSelect.uasset`
- `Content/RecordShop/UI/Turntable/WBP_Turntable.uasset`
- `Content/RecordShop/UI/Result/WBP_Result_IntegrationFallback.uasset` - new integration fallback from the preserved attempt.

Text changes: the current V4 report and historical report pointer; `Invoke-IntegrationPython.ps1`; migration scripts `complete_mvp_flow.py`, `connect_live_customer_profile.py`, `harden_mvp_lifecycle.py`, `finish_mvp_modal_cleanup.py`; shared `mvp_graph_helpers.py`; validation scripts `run_mvp_validation.py`, `validate_mvp_cycle.py`, `validate_mvp_regressions.py`, `validate_mvp_dependencies.py`, `validate_mvp_editor_control.py`, `cook_mvp.py`; new repair/gate scripts `repair_result_focus.py`, `mvp_validation_logs.py`, `test_mvp_validation_logs.py`.

Migration scripts are one-time provenance, not tests to replay on completed assets. The new focus repair also checks the original target before mutation. The launcher construction workaround remains restricted to the two original widget installers; repair and all validation use normal diagnostics. Root data, production Greybox, ST_RecordData, project/config, GameInstance and rejected selection assets remain unchanged. Hash inspection confirms **273 unchanged tracked Content binaries match their HEAD LFS hashes**. All generated evidence is ignored Saved output. No generated fixture/observer Content was saved.

## Input and fixture provenance

| Stage | Exact pathway / limitation |
|---|---|
| Startup, spawn, entry/seat, Ready, StartDialogue/UI | Production Greybox PIE startup and existing customer navigation; observed rather than injected. |
| Dialogue Next, record choice, ordered turntable controls | Synthetic WidgetInteraction Slate Enter -> deliberately focused real button -> normal OnClicked handler. Test focus selection for these earlier stages is disclosed. |
| Shelf and turntable interaction | Synthetic Enhanced Input IA_Interact -> active E mapping -> production sphere trace/interface -> modal. Pawn is positioned for repeatable trace geometry and movement is held; physical walking is not claimed. |
| Rendered Result Continue | Production SetInputMode focuses Continue. Test asserts `has_keyboard_focus()` and `has_user_focus(pc)`, then posts WM_KEYDOWN/WM_KEYUP Enter to this editor process's native window. No set_focus, set_keyboard_focus, window activation, click broadcast or direct completion call occurs for Result. These are synthetic Windows messages, not physical OS/human keypress evidence. |
| NullRHI Result Continue | Native windows do not exist under NullRHI. The separate virtual Slate user navigates using synthetic Tab then Enter, without a test-side focus setter. The actual owning player's production keyboard/user focus is asserted first. This is navigation coverage, not native keyboard delivery. |
| Exit / Explore | Existing AI exit route and real CustomerExited following Continue. Customer position, modal absence, cleared references and hidden cursor are asserted. |
| Isolated regressions | Direct calls/delegate broadcasts, in-memory profile values, temporary observer and engine audio fixture; never natural-stage evidence. The legacy assertion name `physical_input_sphere_trace_interface` denotes synthetic Enhanced Input, not physical input. |
| Physical player/keyboard input | **UNVERIFIED**; requires human observation. |

The one unchanged blank NewRow and existing Test_record_01/02/03 options are the mechanical fixture. No generated narrative, customer values, audio, persistent fixtures or downstream stages were inserted. The nondefault profile diagnostic restores values in memory. The transient audio fixture is `/Engine/EditorSounds/Notifications/CompileSuccess`; it validates actual callback plumbing, not LP content or audible quality. The observer Blueprint is never saved.

## Fresh repair evidence

All prefixes below are under `Saved/MVPCompletion/`. Runner prefixes have `.json`, `.log`, `-stdout.txt`, `-command.json` (exact argv) and `-process.json`. Process JSON now includes native exit, assertion status, unexpected errors, separately identified startup errors, gameplay_log_pass and globally_error_free.

| Prefix | Observed result |
|---|---|
| `20261010T043327Z-repair1-focus` | Supported graph edit, GameFlow/Result compile and GameFlow normal save; exit 0. |
| `20261010T043658Z-repair1-cycle-native-rendered` | Thirteen compiles; complete natural mechanical cycle, owning-player default focus and native-window synthetic Enter; exit 0; zero unexpected runtime errors. `.png` visually inspected: one readable Result, RECORD OPTION 1, Test_record_01, Score: unavailable, Continue. |
| `20261010T044010Z-repair1-cycle-null-navigation` | Thirteen compiles; complete natural cycle with virtual Slate Tab/Enter at Result and default owning-player focus assertions; exit 0; zero unexpected runtime errors. |
| `20261010T044105Z-repair1-final-regressions` | Thirteen isolated assertion groups PASS; exit 0; zero unexpected runtime errors. Covers profile/mood, dialogue guards, eight scores/dispatcher/max assignment, all records, RPM45/78, completion/Result duplication, default focus/repeat Continue, exit/cleanup, IA trace route, Escape/reopen, no-record rejection and real engine-audio callback/replacement protection. |
| `20261010T043950Z-repair1-inventory` | Fresh full current graph/default export, all included Blueprints compiled; exit 0. Graph comparison confirms the focus-target change and preserved customer route. |
| `20261010T044032Z-repair1-dependencies` | 167 packages / 87 /Game / 11 closure Blueprint compiles; no missing packages, redirectors, compile failures or project SoundWave/SoundCue/MetaSoundSource; exit 0. |
| `20261010T044138Z-cook-final` | Windows production-map cook smoke; exit 0; 594 cooked, seven platform-skipped, 0 errors / one certificate-store warning. Greybox and fallback Result cooked assets exist. `-SkipSaveAssetRegistry` bounds the smoke and avoids nonignored CookerOpenOrder generation; not package/stage/registry readiness. |
| `20261010T044201Z-repair1-rendered-control` | Current-assets editor-only startup/quit: no PIE, compilation, fixtures or gameplay. Exit 0; reproduces the exact 15 startup engine smoke errors and no unexpected errors. No current shutdown crash was reproduced. |
| `repair1-contributors.json`, `repair1-hygiene.json` | Fresh local-ref/LFS availability; current changed-file hashes, preserved Content checks and unchanged HEAD. No fetch. |
| `repair1-rejected-log-recheck.json` | New classifier rejects the retained auditor rendered log specifically at line 2109 for LogPlayerController focus Error. |
| `20261010T044116Z-repair1-negative-log-probe` | Intentional commandlet error with assertion JSON set true: runner rejects; native exit 1, gameplay_log_pass false. This is log-gate evidence only. |
| `20261010T044244Z-repair1-negative-editor-log` | Intentional editor log error with **native exit 0 and assertion JSON true**: host runner correctly exits 1, gameplay_log_pass/process_pass false. Proves that a logged error independently fails validation even when the process and assertions succeed. Not gameplay evidence. |

Rendered natural timing: Result **04:37:29.456 UTC**, Continue/FinishResult **04:37:30.452 UTC**, CustomerExited/Explore **04:37:31.422 UTC**, normal log closure **04:37:42.061 UTC**, native exit 0. The corresponding process and screenshot are retained.

The gate's five host unit tests pass: exact startup-block classification; audited PlayerController rejection; extra/gameplay automation-error rejection; missing logs/Blueprint errors/ensures/assertions/fatals rejected; clean commandlet accepted. Startup classification is limited to exactly 15 contiguous `LogAutomationTest: Error: Condition failed` lines following the engine UnifiedError test and before engine initialization and project-script markers. Any changed count/context or other error fails. Known startup errors remain visible and make globally_error_free false; they are not silently discarded.

Reproduce from the repository root (serial Editor runs):

```powershell
python Scripts/Unreal/test_mvp_validation_logs.py
python Scripts/Unreal/run_mvp_validation.py Scripts/Unreal/validate_mvp_cycle.py --name cycle-rendered --rendered --windowed
python Scripts/Unreal/run_mvp_validation.py Scripts/Unreal/validate_mvp_cycle.py --name cycle-null --result-navigation
python Scripts/Unreal/run_mvp_validation.py Scripts/Unreal/validate_mvp_regressions.py --name regressions --audio
python Scripts/Unreal/run_mvp_validation.py Scripts/Unreal/validate_mvp_dependencies.py --name dependencies --commandlet
python Scripts/Unreal/run_mvp_validation.py Scripts/Unreal/validate_mvp_editor_control.py --name control --rendered
python Scripts/Unreal/cook_mvp.py
```

## Retained failed attempts and external constraints

Repair test failures are retained as FAIL, not converted to PASS: `043402Z-repair1-cycle-null`, `043538Z-repair1-cycle-window-null`, `043617Z-repair1-cycle-native-null` reached Result and passed production focus assertions but could not find a native Windows input window under NullRHI. The successful rendered native-window test and explicitly labeled NullRHI navigation test resolve the coverage separately. `043758Z-repair1-regressions` checked focus in the same frame as direct Play, before queued owning-player Slate input-mode operations were applied, and timed out without Continue. Its successor waits four frames, reads focus without assigning it, and passes the complete regression set. No production behavior was relaxed for these tests.

Historical `20261010T041442Z-v4-final-cycle-rendered` and earlier editor-only controls exhibited late `0xC0000005`; they remain failed/partial runs. The original report also missed a gameplay focus error in those cycles, so its no-gameplay-error premise and blanket PARTIAL_SAFE rationale are withdrawn. This repair's rendered cycle and fresh editor-only control both exit 0. That is current bounded success, not a repair of or waiver for an intermittent Slate/ICU shutdown defect. Any recurrence needs fresh diagnostics and control evidence under the stated policy.

Packaging was actually attempted in `20261010T040744Z-package/` and `20261010T040804Z-package/`. The first fails staging (exit 103) for missing `Binaries/Win64/RecordShop.target`, required by GameplayStateTree's temporary target. The build-enabled retry fails in UBT Log.BackupLogFile with UnauthorizedAccessException (exit -532462766), before compilation. The installed `UnrealBuildTool.cs:213-223` backs up the user Trace.uba before ordinary log redirection, using Windows special-folder resolution. Workspace-directed UAT logs/stage/archive do not redirect this early write. No executable/archive exists. This permission boundary is unchanged by the focus edit; repeating the same blocked build would not add validation. No engine patch, permission bypass or plugin disabling was attempted.

## Current locally fetched contributor inventory

Resolved refs by name again; no fetch/LFS download. Full SHAs, paths, OIDs and worktree/shared-cache availability are in `repair1-contributors.json`. Ref tips remain those available at round start; their currency beyond the locally fetched state is unknown. `origin/develop` remains `aa1b9a440d1cd21205c34bf79e0027596cc21cc6`.

| Local ref / tip prefix | Exact dependencies and availability |
|---|---|
| origin/feature/environment-art / 9927497 | Missing LFS binaries under `Content/RecordShop/Art/Environment/ListeningBar/Turntable/`: `SM_Turntable_Base.uasset`, `SM_Turntable_Lid.uasset`, `SM_Turntable_Record.uasset`, `SM_Turntable_Tonearm.uasset`. Art/pivot integration is blocked; no private map or generated garbage imported. |
| origin/feature/turntable-recommendation / 2edde0d | Missing `Content/RecordShop/Data/Structs/ST_CustomerRequest.uasset`, `Content/RecordShop/Interaction/Actors/BP_Turntable.uasset`, `Content/RecordShop/UI/Turntable/WBP_Turntable.uasset`. Binary request/completion/RecommendationResult semantics cannot be inspected. No separately identifiable authored audio in the available branch Content delta. |
| hyeon-fork/feature/ui-presentation / f5a6649 | Missing `Content/ThirdPerson/Blueprints/WBP_Dialogue.uasset` and `Content/ThirdPerson/Blueprints/WDP_SelectionResult.uasset`; dependencies cannot be resolved without binaries. Rejected WBP_RecordSelection families are not integrated. |
| origin/feature/customer-ai / d50de5d | Real newer movement/Customer01 work exists beyond merge-from-develop. Missing `Content/RecordShop/Characters/Customers/Common/BP_Customer.uasset` and `Content/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.uasset` at this ref. Locally integrated route remains usable and validated. |
| origin/feature/dialogue-data / df6774f | Root CustomerData, DialogueData, CustomerDialogue and original manager are locally cached scaffold. Root data hashes still match blank production data. No newer usable authored content; obsolete organized duplicates remain excluded. |

## Remaining work and independent handoff

**No safe independent required implementation or local validation remains within the available contract after these repairs and checks.** The exact residual dependencies across the eight areas are:

1. Supply authored CustomerProfile values and dialogue rows; decide any identity-specific join. This blocks authored areas 1/2/7, not the now exercised mechanics.
2. Define record-to-Preference/Personality inputs and candidate lookup, then connect established raw-score output to Result. Define qualitative rules separately. These authoritative design inputs block meaningful areas 4/5; inventing tags, weights, thresholds or judgments would be unsafe.
3. Supply actual LP audio and usable contributor request/result/UI/customer/mesh binaries. Then validate actual authored playback, presentation and pivots. Current callback and fallback UI mechanics are already checked.
4. Provide a build environment permitted to write UBT's required user trace location, or an authoritative supported tool fix; then build, package and launch. Preserve historical shutdown evidence and investigate any recurrence. Physical player-input verification requires a human.

Mechanical E2E completion is separate from authored narrative, meaningful recommendation, art/audio polish and packaging. The independent auditor decides whole-checkpoint safety. The outer harness alone owns staging, audited commit and push.

Final hygiene: all 25 changed/new paths inspected (eight production assets, two reports and fifteen script/launcher files); Python syntax and text whitespace checks pass. Staged diff is empty, branch/HEAD are unchanged, protected binaries match HEAD and no Unreal validation process remains running. No forbidden/generated checkpoint paths are present. No additional independent local implementation or validation task remains pending.
