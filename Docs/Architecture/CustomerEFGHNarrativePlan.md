# Customer E/F/G/H Narrative Production Plan

**Goal:** Day1 E1, Day3 F1, Day5 G1, Day6 H1 single-visit narrative/profile/result contracts.
**Spec:** User Production Gate request, 2026-11-10, sections 0-16.
**Architecture:** Existing BP_VisitNarrativeDefinition + explicit ordered sequence + shared catalogue. Data-only production change: four tables, four definitions, four visit references. Existing neutral Result feedback is the reaction contract; no customer-specific outcome graph.
**Tech stack:** UE5.8 Editor Python AssetTools/DataTableFunctionLibrary/EditorAssetLibrary and existing validation runners.

## Constraints and scope
Current branch/HEAD remain feature/customer-narrative-content / 9a7d8813f37d0558c0bcb7510220dd36e3fa6424. No new branch, staging, commit, push or raw package writes. No RS004-006, new audio/cover/mesh, quests, combined visit, Day7 narrative or ending.

E cafe shift then waiting for a friend: Quiet/Jazz/Sociable. F university student waiting out rain for a bus: Restless/Electronic/Adventurous. G repair worker writing a postcard after field work: Quiet/Folk/Sociable. H local resident taking a break from a crossword: Quiet/Classical/Reflective. Four rows each; no past/future visit language, no puzzle answer. Age is characterization, never a reason for genre. E/F/G/H appearance = PLACEHOLDER.

## Tasks and interfaces
- [x] 1. READ-ONLY AUDIT: Git and all original Content hashes in Saved/MVPCompletion/customer-efgh-start-state.json; fresh Editor audit of routing/profile/schedule/result/catalogue/presentation. No production writes before audit completes.
- [x] 2. RED contract: create validate_customer_efgh_contract.py with literal days/profiles, empty memory fields, ordered rows, source text, placeholder and RS001-003-only assertions. Run with run_mvp_validation.py; expect Missing E1 production narrative.
- [x] 3. Author data via install_customer_efgh_narrative.py: customer_efgh_dialogue.json -> DT_E/F/G/H_Dialogue and DA_E/F/G/H1_Narrative -> existing visits. Shared graphs, class defaults and catalogue remain byte-identical. Run fresh GREEN contract.
- [x] 4. Runtime matrix: validate_customer_efgh_sequences.py exercises real GFM/DM line emission, duplicate Start/Next, cancel/complete clear, stale history ignored, all 12 actual score paths and synthetic neutral Result grades. Check F->D/E/A/legacy isolation and original class default. Fixture history never becomes runtime authority.
- [x] 5. Update existing fixtures/callers: B/CD next-legacy uses TEMP_D7_01 (E now explicit); contracts allow E-H refs; expected_score includes literal E/F/G/H vectors; validate_day_week verifies all new rows/profiles/reactions, screenshots and actual E RS002/F RS003 BEST. cook_mvp requires eight new narrative packages.
- [x] 6. Serial run_customer_efgh_gate.py wraps contract/matrix and fresh CD/B/A/Core gate: history16 identities/duplicate callback, tutorial TUTORIAL, week16 visits/17 cycles, FinalStoryEvent once, routing, SelectedRecord, listening10s, BGM, camera/input/focus, compile/dependencies/redirectors/map and bounded Windows cook.
- [x] 7. Review current diff, protected hashes, manual text/UI screenshots and evidence. Deliver CustomerEFGHNarrativeReport.md with requested 18 items and exact file list. No gameplay expansion.

## Review focus
Wrong profile/route, F Restless leakage, stale current/foreign history causing a false memory, cancel leaving pending context, actual G/H BEST fabricated, duplicate Result history, stale validators assuming E legacy, Korean text clipping. Matrix + natural week must detect these. Actual hardware gamepad and packaged executable are manual pending unless exercised.

## Execution ledger
Ruling: User explicitly supplies and authorizes architecture and execution. Continue inline; no extra design approval, worktree or commit workflow. Use existing neutral Result text (optional bespoke reactions deferred) to preserve shared production graphs and A/B/C/D feedback byte-for-byte.

Task 1: complete - READ-ONLY Editor audit 20261110T020234Z PASS.
Task 2: complete - RED 20261110T020408Z failed Missing E1 production narrative.
Task 3: complete - Editor install 20261110T020531Z PASS; fresh contract 20261110T020910Z PASS.
Task 4: complete - matrix 20261110T020948Z PASS: 20 history fixtures, 12 actual scores, cancel and following profile/sequence isolation.
Task 5: complete - fixture/cook/week callers updated; all Unreal Python syntax and 11 host unit tests PASS.
Ruling: First matrix 20261110T020649Z failed on a test-only missing TEMP_D7_01_1 suffix. Verified schedule naming and corrected all affected test fixtures; no production fix was needed.
Final code review: efgh_review found no Critical/Important/Minor issues; all 532 original protected assets match. Natural week visuals, downstream gate, cook and final inventory remain pending.

Task 6: complete - original serial gate had one RS002 alignment failure; all other19 groups passed. Same strict RS002 rerun passed (max frame displacement1.850cm versus original21.54cm); no source/asset/threshold changes. Reused11 successful foundation reports + retry yields12/12 foundation. Reconciled customer-efgh-final-evidence.json independently accepts20/20 atomic groups; original FAIL aggregate retained.
Task 7: complete - all16 dialogue +4 Result captures visually reviewed; report18 sections and exact29-file inventory complete. Manual physical gamepad/package/subjective pacing and intermittent low-FPS alignment remain listed. Original Content532 hashes protected; branch/HEAD unchanged, staged0. Stop at E/F/G/H.

Final reporting review: efgh_review independently confirmed18 sections, exact29-file inventory,16 authored dialogue lines,20 passing final groups, unchanged15cm assertion, and accurate original FAIL/retry/manual-risk disclosure. No reporting defects found.
