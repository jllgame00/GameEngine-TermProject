# Narrative Routing / Shared Catalogue Foundation

Start: feature/narrative-routing-catalog @ bf949b390e54338f81cc70f87ea9a7cfaadba2e4, clean.
Audit: Saved/MVPCompletion/20261109T075728Z-narrative-start-audit.json.
Scope/spec: user's 2026-11-09 Narrative Foundation Gate. Existing content plan is
approved direction; implementation is limited to infrastructure and tutorial copy.

## Design

Keep existing GFM day/spawn/history/SelectedRecord authority. Keep DialogueManager
and its score calculation. Add pending source/ordered rows/SequenceID and an active
context; Start consumes pending once, Next uses that source, Finish/Cancel clear it.
Guard duplicate Start while active. Validate table row struct and row existence
before activating; invalid pending falls back to the original Mood table. Legacy
source remains CustomerDialogue, whose five C01 rows and package hash are frozen.

Add BP_VisitNarrativeDefinition PrimaryDataAsset and Narrative reference on the
existing visit definition; no duplicated CustomerID/VisitNumber. Optional memory
visit numbers, four intro row arrays, target Mood/Genre/Theme override, candidate
IDs, review status and version. GFM reads memory first, composes selected intro
and ordered current rows, then supplies pending before the existing memory event.
Only ready definitions apply. Day/visit key still comes exclusively from ActiveVisit.

Tutorial uses runtime CustomerID TUTORIAL and generic role label, the existing
C01 mesh, and a separate five-line placeholder-safe instructional DataTable.
A1 uses existing source/rows and A stable ID; tutorial has no queue ActiveVisit and
still never enters general History. Only A1 receives a new Narrative asset binding.
Other visits remain mechanical placeholders, with no final text/candidate approvals.

Create one ST_RecordData DataTable, migrating all three original MakeStruct values
including FText identity, tags, covers and audio. A PrimaryDataAsset catalogue
service resolves ID->record/Found, and playable resolution requires real audio.
Both GFM and UI reference the same catalogue asset. No current selected record is
stored there. Remove UI MakeStruct data; three cached candidate structs are
resolved from visit IDs, then existing OnRecordSelected handoff remains intact.

A missing optional candidate set uses the catalogue's default three IDs. An invalid
explicit set fails closed: exactly three distinct playable IDs required, buttons
stay disabled with a Korean explanation, Escape retains existing recovery. A1
sets RS001/2/3 only. All other visits inherit temporary defaults, not finalized sets.
RS004/5/6 are unsaved fixtures only, never selectable production rows.

Apply per-visit profile overrides to runtime copied CustomerProfile before the
existing DialogueManager CurrentCustomer/CurrentMood assignment. Never change class
defaults. Keep scoring Mood/Genre/Theme; no narrative completion/affinity/endings.

## Plan / ledger

- [x] Read-only audit branch, graphs, source data, authority and automation.
- [x] RED contract: new APIs/data absent; freeze A1 and original catalogue baseline.
- [x] Install shared typed catalogue, Narrative schema, tutorial source and A1 reference.
- [x] Add Dialogue pending/active lifecycle and isolated sequence tests.
- [x] Integrate tutorial identity, memory routing, profile override, candidate selection.
- [x] GREEN isolated routing/catalogue/candidate/memory/override tests with unsaved fixtures.
- [x] Fresh compile/dependencies, native RS1/2/3, tutorial->A1, full 7-day history cycle.
- [x] Audio/startup/bounded cook, independent read-only review, final 16-part report.

Ruling: execute inline in the user's specified existing feature worktree; no git
staging, commits, pushes, branch changes or destructive operations. No raw assets.
Ruling: detailed approved gate authorizes reversible infrastructure choices; no
additional approval checkpoint before completing this implementation.
Ruling: only tutorial instructions are newly authored; no A2/A3/B~H dialogue/audio.

Preflight: catalogue class/data precede UI and GFM consumers; Narrative class
precedes visit reference; Dialogue API precedes GFM router. Regression fixtures
must distinguish TUTORIAL identity/text from A1, instead of asserting C01 tutorial.

Ruling: MemoryVisitNumbers are authored in ascending unique order. The final
requested prior visit governs the intro key; all valid requested entries are
snapshotted. A missing final entry yields NO_MEMORY, even if an older entry exists.
A missing earlier entry does not erase a valid latest entry. No result aggregation
or affinity score is invented. Multi-memory/missing-entry fixtures cover this.
FText namespace/key/source identity is additionally frozen, beyond display hashes.

Saved installers: data 20261109T081347Z-narrative-data-install-3.json;
Dialogue 20261109T081555Z-narrative-dialogue-install.json;
GFM 20261109T083637Z-narrative-flow-install.json;
UI/Shelf 20261109T085232Z-narrative-candidate-ui-install-4.json.
Sequence lifecycle GREEN: 20261109T083333Z-narrative-sequence-green-3.json.
Fresh editor contracts/dependencies GREEN: report in 20261109T085857Z-narrative-gate.json.
Integration core tutorial/profile/memory/multi-memory passed; UI factory test binding
was corrected to reflected WidgetBlueprintLibrary.Create CDO call; rerun current
20261109T090150Z-narrative-gate.json, host session75722.
No production modifications since successful UI installer. Full regression pending.

Integration GREEN: 20261109T090150Z-narrative-integration-process.json.
Core + six-row fixture / reordered three-card UI / invalid IDs & no-audio blocked.
All 12 production groups host running serially: session54394, aggregate
Saved/MVPCompletion/20261109T090428Z-narrative-gate.json.
Reuses current editor, exact unchanged DM sequence evidence and integration passes.
No production asset mutation after UI installer. End pending guards/week/3RS/
isolated audio/startup/cook; do not start another Unreal process concurrently.

Live full-week GREEN: 20261109T090516Z-narrative-week-process.json.
17 cycles (TUTORIAL +16), A1 original line hash/order, 16 history entries,
all day starts/ends [1..7], final hook once, fresh session history empty.
Current aggregate 20261109T090428Z-narrative-gate.json now running native RS001,
then RS002/RS003/isolated/audio/startup/cook. No production changes allowed during
verification except an established fix requiring fresh regression evidence.


Final gate GREEN: Saved/MVPCompletion/20261109T092552Z-narrative-gate.json,
12/12 groups PASS. Original aggregate 090428 retains the isolated audio timeout;
only that diagnostic reran, with scalar wall/world timing and the same deadline.
Full LP natural completion 34.141 seconds, no production audio change. Intermittent
root cause remains unconfirmed and is documented in the final report.
Bounded Windows cook GREEN: 20261109T092432Z-cook-final-process.json.
Native RS001/2/3 all GREEN; original A1 and record identity hashes preserved.
Final 16-part report: Docs/Architecture/NarrativeRoutingCatalogueReport.md.
No staging/commit/push; stop at this foundation gate, no story expansion.
