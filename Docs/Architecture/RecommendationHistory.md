# Recommendation History / Revisit Memory

Spec: user Production Gate (2026-11-09), existing Day System report.
Start: feature/day-system-customer-queue @ 53a942b4e91dda464278c119185eb2294d1f9868; clean.
Audit: Saved/MVPCompletion/20261109T063934Z-history-start-audit.json.

## Design

Keep BP_GameFlowManager as the session history owner. Its lifetime already spans
all seven days; CurrentDay and TutorialComplete are likewise runtime only. A
GameInstance or new Save/Continue authority would add scope without extending this
single-map gate. SelectedRecord ownership remains entirely unchanged.

Use a small Blueprint UObject payload BP_RecommendationHistoryEntry, with only
CustomerID(Name), VisitNumber(int), Day(int), RecordID(Name),
RecommendationScore(int), RecommendationResult(Name: BEST/GOOD/POOR), Sequence(int).
The project is Blueprint-only and its verified Editor Python surface can safely
create Blueprint classes, but does not expose user-struct member editing. This
avoids unsafe struct serialization or introducing a compiled runtime module.
Queries return newly constructed payload copies, never stored mutable objects.
No Record, Customer actor, SoundWave or Widget references are retained in entries.
These primitive fields are suitable for a later value-only SaveGame schema. The
current UObject array is NOT claimed to be a directly serializable save snapshot:
SAVEGAME_NOT_WIRED, RUNTIME_HISTORY_READY after passing verification.

Write once after the accepted Result has populated SetRawScoreDisplay, before
AddToViewport. This captures the same score and record ID shown by Result, before
Continue/exit/cleanup. Selection-time calculation alone must not record history.
Require actual queued ActiveVisit, matching day, valid active customer and Result,
ResultStartedForCustomer, Result state, available score and record. Tutorial has
no ActiveVisit and is intentionally excluded. Key CustomerID+VisitNumber is
first-write-wins; duplicate or later conflicting calls cannot change the entry.
Unavailable score must not become POOR. Use existing UI thresholds: >=3 BEST,
>=2 GOOD, else POOR. Guard the valid production range 0..3.

Public Blueprint queries on the manager:
HasPreviousVisit(CustomerID) -> bool (any committed visit for ID)
GetLatestRecommendation(CustomerID) -> Entry (None if absent)
GetRecommendationHistory(CustomerID) -> Entries (ordered copies)
GetRecommendationForVisit(CustomerID,VisitNumber) -> Entry (None if absent)
GetActiveVisitMemory() -> CustomerID,VisitNumber,Day,HasPrevious,Latest

GetActiveVisitMemory excludes visit numbers >= the current visit, even if called
later during Result. OnRevisitMemoryReady(CustomerID,VisitNumber,HasPrevious)
fires once on accepted dialogue setup, before DialogueManager.StartDialogue.
No narrative text, branching dialogue or memory UI is added. Consumers call the
manager APIs, without traversing the backing array.

New Game means a fresh manager/map session, naturally starting empty. A guarded
ResetRecommendationHistory is allowed only in opening state (day0, no active
customer, tutorial incomplete); repeated BeginPrologue never clears a running day.
Day transitions and customer cleanup never reset history.

RecordID is the canonical ST_RecordData.RecordID Name. Existing catalogue values
are authored in WBP_RecordSelect MakeStruct nodes, not a DataTable. This gate does
not create a second catalogue or migrate selection ownership; a future resolver
should first extract that catalogue into a single shared data authority.

## Plan / ledger

Global: Editor-only asset mutation. No raw assets, unrelated changes, git staging,
commit, push. Stay in requested worktree/branch. No stories/history UI/save system.

- [x] Audit current branch, lifecycle, scoring, Result, IDs and persistence.
- [x] RED: public API/empty-state contract and full-week memory assertions.
- [x] Create entry class; implement copies, lookup, session reset and primitive contract.
- [x] Integrate accepted Result write and pre-dialogue context hook, preserving flow.
- [x] GREEN editor contract and isolated guards/copy isolation/new-game reset.
- [x] Live full week: A1=RS002/GOOD, revisits A/B/C/D, all IDs/entries/days, duplicates.
- [x] Natural RS001/2/3, backend/audio, startup, dependencies/compile and bounded cook.
- [x] Fresh read-only review; final 16-point report and exact file inventory.

Pre-flight: Result write consumes ActiveVisit before cleanup; queries consume entry
class; week validator consumes existing schedule and unchanged native UI helpers.
Ruling: in-place requested feature branch; no alternate worktree or git operations.
Ruling: explicit implementation request authorizes these reversible design choices;
continue inline without introducing a separate approval checkpoint.

Installer probe: no assets saved on first attempt. Construct Object Outer has
friendly name Outer but internal pin self in UE5.8; verified engine source and fixed.

Review: independent read-only review found no Critical/Important defect. Minor
evidence limits retained in report (conflicting duplicate payload, invalid score
combinations, dynamic hook-order trace). Entry fields are instance-editable for
normal payload inspection and unsaved fixture edits; queries still return copies.
Contract harness now uses list_graphs names; list_functions returns descriptors.

Live week GREEN: 20261109T065451Z-history-week.json, 17 actual cycles /
16 entries / exact stable revisit queries / 16 memory hooks / fresh New Game empty.
Editor GREEN: 20261109T065328Z-history-editor.json; 304 packages, 26 BP,
missing/redirector/compile failure 0. Isolated fixture now uses an unsaved runtime
setter instead of Editor editing the protected backing array; rerun pending.

Final GREEN: Saved/MVPCompletion/20261109T071637Z-history-gate.json,
10/10 groups, all native exits0. Runtime session ready; SaveGame not wired.
Guard queries/copy isolation/opening reset passed with unsaved setter fixture.
No staging/commit/push. Stop at history contract; no narrative content.
