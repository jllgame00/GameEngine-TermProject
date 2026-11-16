# Prologue / Tutorial Production Gate

## Scope and architecture

BP_GameFlowManager remains the only progression authority. Extend it with a small
opening phase, one UMG presentation asset and a passive hint instance. Reuse
Customer01, authored dialogue, catalogue, turntable and Result. A separate tutorial
manager would duplicate authority; a cinematic would add unnecessary ownership.

New Game -> context -> parent memo -> eight seconds free Explore -> existing
Customer01 spawn/entry/dialogue -> shelf -> selection -> turntable -> listening ->
Result Continue -> natural customer exit -> TutorialComplete and Explore.

The canonical WBP_RecordSelect -> BP_RecordShelf.RecordSelected ->
BP_GameFlowManager.HandleRecordSelected -> BP_Turntable.SetRecord path stays intact.
No Day System, queue, history, new customer, ending, GameInstance or SaveGame.

Opening modal owns UI input only while displayed and never changes the camera.
Close restores GameOnly, hidden cursor and viewport focus. Hints cannot take focus
or intercept input and hide during existing modals. Existing turntable UI explains
cover, record, RPM and tonearm; do not duplicate those instructions.

TutorialComplete is a public session/map-local bool, set only after a submitted
tutorial Result and natural customer exit. OnTutorialCompleted is the future Day
System hook. It does not spawn another customer. Map restart begins New Game;
cross-map/disk persistence is deferred.

## Implementation and verification ledger

- [x] Starting branch feature/prologue-tutorial; HEAD 2ed3fa01b357f449cef00d87c2a452457761d7db; clean.
- [x] Inspect live production graphs and compile nine existing assets.
- [x] Complete map/GameMode/player/input and persistence/intro inventory.
- [x] Fail opening contract before installation.
- [x] Install manager and UMG through supported Editor Python only.
- [x] Verify opening, guards, hints and completion.
- [x] Run contiguous RS001/RS002/RS003 input cycles and isolated regressions.
- [x] Check dependency closure, production launch and bounded Windows cook.
- [x] Record MANUAL REVIEW and Day System integration contract.

Baseline compile succeeds, but strict log gate finds an existing missing NodeGuid
comment in BP_Turntable.BeginOwnerAlignment. Engine startup smoke errors are tracked
separately by the existing runner. No globally error-free claim.

Implementation choices above are agent decisions within the supplied requirements.
Work remains on the user's branch; no staging, commit or push. Evidence is saved
under Saved/MVPCompletion. No raw uasset/umap writes.

Completion guidance suppresses existing modals, then releases its widget and polling
timer after six seconds. It never takes input or camera ownership.

Review: both initial Korean corruption and completion-modal overlap were reproduced
and repaired. The serial final gate verifies the repaired assets in fresh editors.

The opening also applies its own button focus once after 0.1 seconds, guarded by
a live PrologueWidgetRef, stage below 3, and a valid player controller. This fixes
the reproduced immersive PIE startup focus race without reclaiming Explore focus.


Final required windowed gate: 9/9 PASS, Saved/MVPCompletion/20261109T051918Z-prologue-gate.json.
Existing isolated regression: 22/22 PASS. Windows cook includes Prologue and Result.
Expanded left80 contact-target assertion and immersive capture focus are not accepted
as passing cases; see PrologueTutorialReport.md for the retained limitations.
