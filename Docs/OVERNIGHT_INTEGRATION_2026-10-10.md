> **Current V4 checkpoint:** see [OVERNIGHT_INTEGRATION_2026-10-10_V4.md](OVERNIGHT_INTEGRATION_2026-10-10_V4.md) for the implemented full mechanical customer cycle, final validation, remaining dependencies and terminal decision. Everything below describes earlier checkpoints.

> **Safety verdict superseded:** the independent auditor reproduced a D3D12 process exit of `0xC0000005` after assertions completed. The current crash investigation, startup diagnosis and cook results are recorded at the top of [the October 9 checkpoint report](OVERNIGHT_INTEGRATION_2026-10-09.md). Earlier PASS statements below are historical run results, not current checkpoint approval.

# Overnight Integration — 2026-10-10

## Checkpoint

- Branch: `feature/overnight-integration-2026-10-09`; HEAD unchanged: `69d835ccdbbe887567d4527e12ec9e3d3a8a4a20`.
- Harness round 1 / 3, started October 9; this report uses the current Asia/Seoul date after midnight.
- Engine verified locally: UE 5.8.2, CL 56702186.
- **LAST NATURALLY VERIFIED STAGE:** Game start → customer spawn → entry/seat → CustomerReadyForDialogue → DialogueManager.StartDialogue → one dialogue widget and UI update. The existing blank row advances CurrentLineIndex to 1.
- **FIRST BLOCKER:** authored dialogue readiness. `/Game/CustomerDialogue` still contains only `NewRow`, with empty Speaker/Text/Mood/MusicPreference and DialogueID=None. No live-customer → authored customer/mood mapping is available. Plumbing works; this is not a content-complete conversation.
- **Natural E2E: FAIL / BLOCKED.** Automated Next verifies Finished → Explore/input restoration. Later fixtures, interaction calls and injected FinishResult are isolated regression checks, not natural E2E proof.
- **Final rendered validation: VERIFIED PASS for the tested scope.** D3D12 PIE compiles all 12 Blueprints/interfaces and passes all 16 assertion groups; complete=true, assertions_pass=true, no fatal exception, Unreal exit code 0. The UI screenshot was visually inspected. Terminal conditions **B/D** apply to the remaining content and external dependencies.

## Production changes

Four assets were changed only through Unreal Editor Python, asset factory, supported graph APIs and Editor saves:

1. `BP_GameFlowManager`: Ready validates ActiveCustomer, ignores repeated Ready in the same customer cycle, creates/reuses one root DialogueManager component, binds update/finished once, creates one canonical dialogue widget, sets Dialogue, then calls StartDialogue. Existing manager defaults are preserved; customer metadata is not fabricated.
2. New `/Game/RecordShop/UI/Dialogue/WBP_Dialogue`: minimal Speaker/Text display and Next button. Next calls the existing ShowNextLine. OnDialogueFinished closes the UI, clears its manager reference and GameFlow's widget reference, restores game input/cursor/focus, and returns Explore. This is locally built plumbing UI, not the unavailable contributor presentation asset.
3. `BP_RecordShelf` and `BP_Turntable`: a small additional dialogue-widget guard prevents either existing modal from opening over dialogue.
4. Existing customer exit cleanup also closes dialogue and clears its cycle guard. DialogueManager remains one reusable component owned by GameFlow; it is not a stale customer/widget reference. Duplicate Finished callbacks with no dialogue UI leave other interaction modals alone.

The shared Greybox map, root dialogue assets, BP_Customer, ST_RecordData and existing record-selection ownership are unchanged:

`WBP_RecordSelect → BP_RecordShelf.RecordSelected → BP_GameFlowManager.HandleRecordSelected → BP_Turntable.SetRecord / CurrentRecord / HasRecord`.

BP_RecordGameInstance authority was not reintroduced. No contributor merge, obsolete dialogue duplicate, rejected RecordSelection family, private Test Map, _GENERATED map, narrative, scoring rule, queue/day system, commit or push was introduced.

## Validation verdicts

| Gate | Verdict | Evidence / limit |
| --- | --- | --- |
| Startup | VERIFIED PASS, editor/PIE | Greybox remains the startup and PIE world. Packaging is not claimed. |
| A Customer | VERIFIED PASS | Observation-only first 15 seconds reaches Ready and the production dialogue handoff. Existing route is preserved. |
| B Dialogue | VERIFIED PASS plumbing; PARTIAL content | Natural Start/UI; Next-button delegate → Finished → Explore/cursor hidden; speaker/text forwarding; one manager/widget; repeated Ready; cross-modal exclusion; synchronous empty-match finish; repeated modal cleanup all pass in isolated PIE. Actual authored lines/customer mapping remain absent. |
| C Record selection | VERIFIED PASS, isolated PIE | All three LP choices reach Turntable.CurrentRecord/HasRecord; repeated/sibling-shelf interactions keep one widget; selection blocks turntable; physical Enhanced Input/sphere-trace/interface checks still pass. |
| D Turntable | PARTIAL | Modal and Escape/input guards, valid/invalid order, no-record rejection, repeat Play, and real RPM45/78 button paths pass. Current LP Audio=None; real playback and TurntableCompleted are unverified. |
| E Recommendation | PARTIAL scaffold / BLOCKED | Existing scoring is unchanged. Latest request/output binaries are unavailable; agreed request/tag/result semantics are absent. No Good/Bad result is invented. |
| F Result / exit | PARTIAL; exit regression VERIFIED PASS | Injected FinishResult still drives customer exit, clears ActiveCustomer, closes modals and returns Explore. Natural Result UI/RecommendationResult consumption is unavailable. |
| G Natural E2E | FAIL / BLOCKED | Last natural stage is dialogue UI update. Downstream diagnostics do not prove a full customer cycle. |
| Real meshes / pivots | UNVERIFIED / BLOCKED | Four latest canonical turntable mesh binaries are absent. No transforms/pivots or appearance claim. |
| Packaging | UNVERIFIED / deliberately omitted | Priority 9 requires a passing vertical slice. |

Fresh baseline before changes: 11 Blueprints/interfaces compile; original 10 runtime assertion groups pass; exit 0. After changes, the normal-diagnostics NullRHI run compiles 12 Blueprints/interfaces and passes **16 assertion groups** (six dialogue + original ten); complete=true, no fatal exception, exit 0.

The final normal-diagnostics D3D12 run also passes all 16 assertion groups, including exit cleanup with ActiveCustomer=None, Explore, zero modals and cursor hidden. `worker-dialogue.png` (1280?720) shows the Greybox PIE viewport with the bottom dialogue panel and Next button; empty Speaker/Text matches the blank authored row. This verifies rendering presence, not authored-content quality or human design approval. First D3D12 startup required approximately six minutes of shader compilation.

Both normal-diagnostics runtime logs contain the same **15 pre-existing `LogAutomationTest: Error: Condition failed` startup messages** observed in the baseline, plus network warnings. Their cause is not resolved, so no globally clean-log/automation-suite PASS is claimed. The final rendered log has **zero** missing-NodeGuid warnings, Blueprint compile errors, Accessed None, infinite-loop matches or ensure failures. Earlier two comment-node GUID warnings were resolved by Editor resave.

The first post-change run already passed the natural Start/UI/Next path and existing regressions. Four additional diagnostic cases failed on Python API limitations (noneditable instance properties and an unexposed Blueprint delegate broadcast); these are retained as failed attempts, not counted as passes. The repaired diagnostic harness uses an **unsaved** Blueprint fixture for setters and a temporarily modified in-memory table for speaker/text forwarding, restored in `finally`. It does not save the fixture, table, map or production assets. Fixture operations occur only after observation and the real Next-button path.

Input coverage uses button delegates, synthetic Enhanced Input and Slate key routing. It does not establish an OS mouse click, natural walking, audible output, or human design approval. `Debug_RunDummyFlow` is never used.

## Latest fetched contributor refs

Resolved by ref name from local remote-tracking refs; no successful online fetch is claimed.

| Ref | Current HEAD | Audit decision |
| --- | --- | --- |
| origin/develop | aa1b9a440d1cd21205c34bf79e0027596cc21cc6 | Baseline only. |
| origin/feature/environment-art | 9927497acf49c433034bdf520d3ad5c6a20398ee | Four canonical meshes identified, all required LFS OIDs absent. No map import. |
| origin/feature/turntable-recommendation | 2edde0dc4b4ac7fcb5a58319b481de8a429e0620 | Latest ST_CustomerRequest/BP_Turntable LFS OIDs absent. Cannot safely port uninspected logic or GameInstance ownership. |
| hyeon-fork/feature/ui-presentation | f5a66494ca7de7edcb50b3fadfa1038015ca336d | Latest WBP_Dialogue/WDP_SelectionResult OIDs absent. A fresh exact-ref targeted download fails at configured proxy 127.0.0.1:9 (connection refused). Fallback dialogue UI is created directly in the canonical folder. |
| origin/feature/customer-ai | d50de5d968c8e56f4575c6d5c2bd7b8dea808afc | New Customer01 character/animation assets after movement polish; not merely a merge. Common BP_Customer remains the previous contributor OID and is absent locally. Current passing route preserved; character presentation/private map not imported. |
| origin/feature/dialogue-data | df6774f5faf274eb83b57600aa347bb3605121f6 | All four authoritative root assets match pre-round HEAD. No newer usable authored dialogue. |

Nine targeted LFS objects remain absent in both the shared and workspace-local caches. No credential, proxy, persistent Git configuration or unresolved pointer in Content was changed. Full remote-tracking refs were used for the fresh download attempt.

## Evidence and reproduction

Ignored evidence: `Saved/OvernightIntegration/Round1/`.

- `worker-baseline.log` and inherited-name `repair-runtime.json`: this worker's fresh pre-change baseline, started 2026-10-09T14:54:04Z.
- `worker-dialogue-install.json` / `worker-dialogue-install7.log`: four assets saved only after all five compile checks pass.
- `worker-resave.json` / `worker-resave.log`: all four production changes recompiled/resaved with normal diagnostics.
- `worker-runtime-nullrhi-pass.json` / `worker-runtime2.log`: 12 compiles, 16 assertion groups pass, exit 0.
- `worker-runtime-attempt1.json` / `worker-runtime.log`: failed test-tool attempts, retained separately.
- `worker-runtime.json` / `worker-runtime-rendered.log`: final D3D12 validation, 12 compiles and 16 passing assertion groups.
- `worker-dialogue.png`: visually inspected rendered UI before diagnostic fixtures.
- `worker-preserved-contracts.json`: unchanged SHA-256 values for root data/manager assets, Greybox map, BP_Customer and ST_RecordData.
- `worker-contributors.json`: refreshed exact-ref/OID cache inventory, including the newer customer branch head.

Re-run validation on the completed worktree:

```powershell
& Scripts/Unreal/Invoke-IntegrationPython.ps1 -Script Scripts/Unreal/validate_integration_round.py -Name verify-dialogue -Editor
& Scripts/Unreal/Invoke-IntegrationPython.ps1 -Script Scripts/Unreal/validate_integration_round.py -Name verify-dialogue-rendered -Editor -Rendered
```

`integrate_dialogue_handoff.py` is a one-time installer for the pre-round assets and rejects reapplication. New widget construction exposed UE's missing-widget-GUID fixup diagnostics; crash-report collection stalled two unsaved attempts. Only the constructor run used `-AssetConstruction` (`-handleensurepercent=0`); the launcher restricts this switch to that installer. Normal-diagnostics resave and subsequent validation do not suppress ensures. No protected-property bypass or binary patch was used. The engine fixes widget GUIDs during compilation; the subsequent resave also persists comment-node GUID repairs.

## Modified files

- `Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset`
- `Content/RecordShop/Interaction/Actors/BP_RecordShelf.uasset`
- `Content/RecordShop/Interaction/Actors/BP_Turntable.uasset`
- `Content/RecordShop/UI/Dialogue/WBP_Dialogue.uasset` (new)
- `Scripts/Unreal/integrate_dialogue_handoff.py` (new one-time installer)
- `Scripts/Unreal/resave_dialogue_integration.py` (new Editor GUID-fixup resave)
- `Scripts/Unreal/dialogue_handoff_checks.py` (new runtime coverage)
- `Scripts/Unreal/validate_integration_round.py`
- `Scripts/Unreal/Invoke-IntegrationPython.ps1`
- `Docs/OVERNIGHT_INTEGRATION_2026-10-09.md` (historical-report pointer)
- `Docs/OVERNIGHT_INTEGRATION_2026-10-10.md` (this report)

Python syntax compilation and text `git diff --check` pass. No transient fixture/probe asset is saved. The worktree intentionally remains uncommitted.

## Remaining blockers and terminal decision

Authored dialogue/customer mapping, LP audio, request/scoring vocabulary and result semantics need repository/team content. Mesh, contributor completion/request logic and Result UI inspection additionally require accessible LFS binaries. These are explicit **B/D terminal dependencies**, not a reason to leave locally feasible dialogue plumbing undone. Visual presentation/pivots remain unapproved.

Independent work remains: isolate the rendered process failure, validate production-map cooking, investigate startup diagnostics, and inspect completion/result contracts. Authored dialogue and unavailable LFS assets do not block these investigations. No commit or other Git metadata write is authorized in the crash-repair task.
