# Customer A Revisit Narrative — Design / Implementation Plan

> For agentic workers: execute inline with superpowers:executing-plans. No staging, commits or pushes.

**Goal:** A2/A3 consume real recommendation memories through existing visit routing while A1 remains byte/content-identical.
**Spec:** User's Customer A Gate in this conversation. A only, Quiet/Jazz/Traditional; Day3 Visit2, Day5 Visit3.
**Architecture:** Separate DT_A_RevisitDialogue plus DA_A2/DA_A3 narrative references. Extend the existing optional narrative definition with earlier-memory rows, require-all-memory neutral handling, and two short outro modules. The existing GFM composes rows through GetRecommendationForVisit before OnRevisitMemoryReady; DialogueManager keeps the foundation pending/active lifecycle.
**Tech Stack:** UE5.8, existing Editor Python / BlueprintGraphEditor / DataAsset / DataTable automation.

## Decisions / alternatives

Use modular composition, not nine full scripts or Mood-based appended rows. A2 selects one V1 intro then five common lines. NO_MEMORY has no intro. A3 selects one V2 intro, one V1 recollection, three common lines, and a one-line outro. Both V1/V2 must exist and have recognized Result; otherwise use neutral intro + common beat + clarifying outro, without claiming missing experiences. BEST/GOOD for both permits a modest shop-understands-taste outro; any POOR uses clearer-self-description outro. These are categorical narrative predicates, not a new result score or relationship.

A3's V1 recollection juxtaposes the two experiences; it never guesses which Mood/Genre/Theme factor mismatched. CustomerID/VisitNumber remain owned by ActiveVisit. No LP-title interpolation is introduced; History snapshots retain RecordID for future use.

Keep generic current Result feedback: no competing Result authority or second popup. The next-visit memories provide A-specific reactions. Current selection, catalogue, audio and modal recovery remain untouched.

## Constraints / review focus

- Freeze original CustomerDialogue/C01/ST_RecordData and A1 narrative/reference; never copy A1 into a new source.
- Other 13 queue visits retain unset Narrative; Tutorial remains separate.
- Missing/unknown/foreign customer/future visit memories cannot fabricate prior success.
- GOOD does not imply an exact factor mismatch; POOR does not blame player or resolve life conflict.
- A3 optional fields default inert for all existing foundation fixtures.
- Keep existing zero/unset optional fields behavior, finish/cancel clears and duplicate guards.

## Ledger

- [x] Read-only Editor audit + freeze A1/catalogue/schedule + RED contract.
- [x] Add A-only authoring JSON and install optional composition schema/GFM + A2/A3 data.
- [x] GREEN: exact emitted line sequence for A2 four branches, A3 nine combinations and missing cases; repeated starts, cleanup, unchanged preference and real scores.
- [x] Update foundation/week contracts to recognize only A2/A3 new content and variable authored line count.
- [x] Fresh full foundation regression, full week, real RS1/2/3, audio, startup, dependency and bounded cook.
- [x] Review Korean UI captures, independent source review, final 14-part report and exact inventory.

Ruling: user's detailed implementation request authorizes these reversible production changes; no extra approval gate. Execute in the specified feature branch, preserving clean baseline. No other Customer content or Ending.

Audit RED: 20261109T093855Z-customer-a-audit-red.json. Installer PASS:
20261109T094318Z-customer-a-install-process.json. Matrix GREEN 23 cases:
20261109T095219Z-customer-a-sequences-5-process.json. It records actual emitted
line delegates, not a natural widget presentation. Its shots show tutorial hints
because the isolated fixture calls DM directly after tutorial closure; do not use
those shots to claim visual approval. Real A2/A3 UI captures are in live week.

Ruling: native test probe's duplicated Memory observer crashes during construction;
remove that duplicate and reuse the existing foundation memory-event-order test.
The new matrix still checks real pending rows, emitted text, exact sequence, finish
counter, duplicate Start, source cleanup, profile and actual score. Keep raw crash
logs/snapshot under Saved; native API crash cause remains unconfirmed.

Independent read-only review: no concrete Critical/Important production finding.
Minor dialogue ending '???' stays colloquial, consistent with A1's rough spoken
register; list tone as manual review. Added A2 unknown / A3 foreign/future fixtures.
Full gate session52218: 20261109T095432Z-customer-a-gate.json, serial UE only.


Final GREEN: 20261109T102222Z-customer-a-gate.json; 14/14 groups.
Foundation accepted evidence 20261109T101900Z-narrative-gate.json. Original
095502 foundation run retains the intermittent isolated audio timeout; same 40s
limit rerun completes naturally at 34.203s, no production audio change. Cause
unconfirmed, documented. Fresh final A contract passes all ten protected hashes.
Live week 20261109T095812Z-narrative-week.json:17cycles/16history/7days/final once.
Twelve real A2/A3 UI shots; A2 situation/hint and A3 payoff visually inspected.
Cook 20261109T101740Z-cook-final-process.json GREEN; package NOT RUN.
Source review has no concrete Critical/Important finding after matrix fixes.
Final report: CustomerARevisitNarrativeReport.md. Stop here; no B story expansion.
