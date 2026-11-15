# Customer C/D Narrative Production Plan

**Goal:** C1/C2 (Day 2/4), D1/D2 (Day 3/6) narrative, runtime profiles and revisit memory, preserving A/B and Core.
**Spec:** User's Customer C/D Production Gate, 2026-11-10.
**Architecture:** Existing explicit router and BP_VisitNarrativeDefinition. Two DialogueData tables, four Narrative assets, four existing visit references. No shared production graph changes.
**Tech stack:** UE 5.8 Editor Python, existing AssetTools/DataTableFunctionLibrary and validation runner.

## Decisions and boundaries

The supplied architecture needs data-only authoring; another router/profile system would duplicate authority. Identity/day/order remain on Schedule visits. No branch/worktree switch, staging, commit or push.

C reduces a large workshop gathering to a small table and two or three invitations, allowing room for their own burden. D distinguishes work from spare time without health/family/achievement stories. C/D appearance = PLACEHOLDER (C01). Dialogue speakers describe roles, without new proper names.

C1/C2 = Quiet/Folk/Sociable; D1/D2 = Quiet/Classical/Reflective. Actual graph CalculateLPScore uses Equal Exactly (String); preserve capitalization. Second visits use MemoryVisitNumbers [1], BEST/GOOD/POOR intro + common body. Missing/unknown means common body only. GOOD cannot establish a particular element mismatch. Unused multi-memory fields stay empty/default.

Production catalogue remains RS001/2/3. C vector 1/2/0, D 1/1/0. RS005/6 absent. Unreachable branches use unsaved history fixtures; natural week has no result/history injection. Existing profile-neutral Result feedback applies automatically; A grade/text authority unchanged.

## Scope map

- New data: DT_C_Dialogue, DT_D_Dialogue, DA_C1/2_Narrative, DA_D1/2_Narrative; only Narrative refs on existing DA_Visit_C_1/2 and DA_Visit_D_1/2.
- New authoring/verification: customer_cd_dialogue.json, reference hashes, installer, contract, sequence matrix, expectations and gate runner.
- Existing callers/fixtures: B contract accepts C/D refs; B next-legacy check uses E. Generic expected_score gains C/D vectors. Week checks their text/profile/Result/captures; foundation mapping/cook require new assets.
- GFM, DialogueManager, class defaults, catalogue, SelectedRecord, Turntable, History, audio, input and map stay unchanged.

## Review focus

Foreign/future/unknown history must not produce false memory. C/D to A/B/E must clear sequence/memory/profile on the next fresh base profile (production spawns fresh actors). First visits ignore stale history. Duplicate Start/finish emits once. Real score checks remain independent of fixture branches.

## Execution ledger

- [x] Read-only Git/Editor audit: feature/customer-narrative-content, HEAD 1f9e6d19689d4a02d7b62b616829fcc281a35059, clean. Successful audit 20261109T161049Z-customer-cd-audit-process.json. First probe mistook an event for a function; raw failure retained, corrected with no asset edits.
- [x] Contract RED: 20261109T161417Z-customer-cd-contract-red.json failed specifically Missing C1 production narrative.
- [x] Data-only install 20261109T161613Z-customer-cd-install-process.json PASS; fresh contract GREEN in running gate.
- [x] Matrix 20261109T161812Z-customer-cd-sequences-process.json PASS, 22 cases; scores, Result and following A/B/E isolation PASS.
- [x] Fresh B/A/core gate: compile/dependencies, routing, Tutorial, 17 cycles/16 histories, natural RS001/2/3, listening/BGM/focus, map, bounded Windows cook.
- [x] Read-only review, exact changed-file inventory, 18-part report including all dialogue and MANUAL REVIEW. Stop at C/D.

Ruling: The user already supplies and authorizes the architecture. Execute inline without another approval checkpoint. No skill commit/cleanup steps override the explicit no-commit instruction; preserve evidence.

Final review: read-only cd_narrative_review found no Critical/Important issues. Minor deferred: D2 BEST time expression may suggest prior outside-shop listening; list in MANUAL REVIEW. Asset/UI/audio judgment is covered by fresh gate and visual inspection, not by the code reviewer.

Final evidence: Saved/MVPCompletion/20261109T161737Z-customer-cd-gate.json (18/18 groups), customer-cd-final-evidence.json; 25 files, 11 Python AST, only four original C/D asset references changed, HEAD/branch unchanged, staged=0. No commits or pushes.
