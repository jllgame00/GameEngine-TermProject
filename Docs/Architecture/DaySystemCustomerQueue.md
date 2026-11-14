# Day System / Customer Queue Production Gate

**Goal:** Implement the supplied seven-day, sixteen-visit schedule on the existing
customer cycle. Do not add stories, recommendation history, persistence or endings.

## Starting audit and prerequisite ruling

- Branch feature/day-system-customer-queue; HEAD 2ed3fa01b357f449cef00d87c2a452457761d7db; clean.
- Default production map L_RecordShop_Greybox, existing ThirdPerson GameMode/pawn/controller.
- BP_GameFlowManager owns single spawn and cleanup; BP_Customer.CustomerExited is the completion event.
- Current branch does not contain Prologue; existing feature/prologue-tutorial commit fe8f16f does.
  Reuse its text and verified Editor installer, rather than copying/editing binary assets.
- Current branch has full-track listening and no Store BGM. Ten-second listening and
  Result-to-BGM lifecycle are required prerequisite gaps, recorded explicitly.
- No configured custom GameInstance or SaveGame. No new persistence authority.
- Audit evidence: Saved/MVPCompletion/20261109T053312Z-day-start-production-audit.json.

## Architecture

Keep BP_GameFlowManager as the sole progression/spawn authority. Add orthogonal day
state; keep the existing E_GameFlowState and canonical selected-record path intact.
Reuse the existing spawn/entry/dialogue/selection/turntable/listening/result/exit cycle.
An accepted exit requires the actual active customer and submitted result, consumes
its exit token before cleanup, disconnects the finished actor and then advances once.
No Tick/polling decides queue completion. Short one-shot timers provide transitions.

PrimaryDataAsset definitions model Visit, Day and Week. Visit has CustomerID,
VisitNumber, Day, OrderInDay, CustomerClass (existing profile/content reference),
optional CustomerData row handle and StoryEventID. A Day contains its ordered Visit
array; the Week contains seven ordered Days plus FinalStoryEventID. Temporary
instances contain the exact supplied schedule. Data assets can change customer
classes/content without changing GameFlow. Blueprint-only data assets avoid a new
C++ module or unsupported raw struct edits.

A~H are stable runtime IDs. Customer01 is explicitly temporary presentation/content;
its authored dialogue is reused as a mechanical fixture, not authored A~H story.
Tutorial has no queue visit, and OnTutorialCompleted is the only first-day entry.

CurrentDay=0 before tutorial; days 1..7 use an ordered queue and current index.
Queue empty -> Day End -> fade BGM -> next day, or the single FinalStoryEvent hook.
No eighth day and no invented ending. Day UI is passive Korean presentation, using
existing UMG styling without changing camera, input mode, cursor or focus ownership.

Audio: use existing Turntable playback/return/completion. A ten-second listening
window requests its existing tonearm return. Flow owns a separate configurable
Store BGM component using existing music; stop/fade it at listening and Day End.
No new music, audio manager, or recommendation history is introduced.

## Plan / ledger

- [x] Audit branch, map, production graphs, spawn/exit, content and audio authorities.
- [x] Restore existing Prologue prerequisite through its Editor automation and verify.
- [x] RED: visit/schedule asset contract; build editable data assets and validate all 16 visits.
- [x] Extend existing spawn once, stable visit context and accepted-exit cleanup guards.
- [x] Add event-driven day/queue transitions, passive day presentation and final hook.
- [x] Connect ten-second listening and Store BGM without duplicating turntable logic.
- [x] Verify seven-day live simulation, duplicate/premature calls and tutorial handoff.
- [x] Verify natural RS001/RS002/RS003, tutorial handoff, audio and recovery.
- [x] Verify dependency closure, production startup, compile and bounded Windows cook.
- [x] Review and report 14 requested items, limitations, manual review and commit suggestions.

No staging, commits, pushes, destructive git, raw asset edits or unrelated changes.

Live week evidence: Saved/MVPCompletion/20261109T060758Z-day-full-week.json.
Tutorial1 + queue16 completed; Day starts/ends [1..7] each, final hook exactly once.
CustomerData row handle is reserved; CustomerClass supplies the current profile.
Empty/mismatched edited days must be rejected by the editor contract before use.
The current runtime does not auto-skip an invalid empty day.

Final aggregate: Saved/MVPCompletion/20261109T063354Z-day-gate.json (9/9 PASS).
Initial audio timeouts are retained in 20261109T062002Z-day-gate.json.
Production unchanged; instrumented reruns passed actual natural completion.
