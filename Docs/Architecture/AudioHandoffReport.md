# Selected LP Store BGM Production Gate

Technical final gate: **26/26 unique groups PASS**, consolidated from successful processes on the unchanged production packages and the corrected complete-week run. [Final evidence](../../Saved/MVPCompletion/audio-handoff-final-evidence.json). The initial aggregate remains FAIL; see section13. Subjective listening and packaged acceptance are separate.

## 1. Starting branch / HEAD / status

`feature/customer-narrative-content`, HEAD `7e94f0cfdafc949bdddd209326da593f1062ff7e`. The previous Record Expansion Gate's 63 uncommitted files were already present. No branch creation, staging, commit or push. Full `git status --short` still fails in Git LFS's MSYS shell (`couldn't create signal pipe, Win32 error 5`). The read-only [start snapshot](../../Saved/MVPCompletion/audio-handoff-start-state.json), scoped non-LFS Git diff, untracked listing and package SHA comparisons provide the inventory; ignored Python caches are not deliverables.

## 2. Fixed RS001 root cause

Actual [pre-change graph evidence](../../Saved/MVPCompletion/20261110T052836Z-audio-handoff-audit.json), not inferred from source alone:

- GFM class default `StoreBGMSound` points to `/Game/RecordShop/Audio/Music/RS001_Best.RS001_Best`.
- `StartStoreBGM` -> `CreateSound2D.Sound` reads that field. No completed RecordID was assigned to it. `BeginDay` and `CloseResult` -> `StartStoreBGM` therefore always used RS001.
- GFM's `StoreBGMRef` and TT's `PlaybackAudio` are distinct auto-destroy AudioComponents, with distinct actor owners. TT `BeginTonearmReturn` fades .45s; after the existing 1.2s return, `CompletePlayback` stops and clears audio before broadcasting completion.
- GFM `StartListeningWindow`, reached from TT `OnPlaybackStarted`, used to stop BGM after new playback began. EndCurrentDay already stopped it before the .75s day transition. Last-day cleanup preceded the FinalStoryEvent hook. Prologue/Dialogue have no separate voice playback path in this flow; no new ducking/ambience system was introduced.

RED [RS003 test](../../Saved/MVPCompletion/20261110T053315Z-audio-handoff-red.json) reproduced actual RS003 selection followed by wrong RS001 BGM. An earlier fixture property-write failure is retained separately; unsaved Blueprint fixture access corrected that test, without altering production instance-editability.

## 3. Final Store BGM ownership

| Responsibility | Authority |
|---|---|
| Selected Record | Existing RecordSelect -> Shelf.RecordSelected -> GFM.HandleRecordSelected -> TT.SetRecord / CurrentRecord |
| RecordID -> playable data | Existing Shared Catalogue ResolvePlayableRecord |
| Ambient playback / demand / loop / stop | Existing GFM |
| Current BGM identity | GFM.CurrentStoreBGMRecordID (runtime only) |
| Current BGM sound | Existing GFM.StoreBGMSound, resolved runtime cache, default None and no longer author editable |
| Current BGM component | Existing GFM.StoreBGMRef, auto-destroy, no level persistence |
| Focused listening component / completion | Existing TT.PlaybackAudio and TT lifecycle |

No duplicated record map/table, playback manager, record-specific branches or new SelectedRecord authority. Public StartStoreBGM is guarded by accepted Result, CurrentState=Result, HasRecord, shared playable resolution and not-already-requested. The old disconnected fixed-source implementation was removed. Existing catalogue and all six LP assets remain byte-identical to this Gate's start.

## 4. Listening -> BGM transition

**Chosen method: same-track restart**, not position transfer. Preserve TT FadeOut(.45), tonearm return(1.2), Stop/clear and completion ordering. After the existing accepted Result/history call, start the same canonical RecordID at source time zero and FadeIn(.5) to .18. The Result screen now has the selected LP's BGM; Continue is an idempotent no-op for audio, rather than restarting it.

The original return timing includes a gap between listening fade-out and Result BGM. This Gate does not claim seamless playback-position continuity or subjectively approved fade quality. Position transfer would require changing the existing TT component lifetime; the user's production-safe restart option preserves it.

## 5. BGM -> next Listening

Canonical HandleRecordSelected calls StopStoreBGM before the existing SetRecord/score path. Stop clears demand, ID and cached sound before unbinding OnAudioFinished and fading .6s; a timer finishes Stop/clear. TT StartPlaybackAudio also calls GFM.FinishStoreBGMStop synchronously **before** its existing CreateSound2D, so a rapid interaction cannot overlap remaining old music with new listening. If a user starts immediately, the remaining fade is truncated to guarantee no overlap. Existing StartListeningWindow cleanup remains a safe redundant guard.

## 6. Day transition policy

Preserve EndCurrentDay -> StopStoreBGM -> .75s day transition. BeginDay now calls ResetDayAudio, not StartStoreBGM: no arbitrary new-day LP is chosen. Reset also clears the completed TT record via a guarded TT API. Day1-7 customer entry and the final hook are checked for no ambient state/audio leak. No FinalStoryEvent content was authored.

## 7. Tutorial policy

Tutorial can use its selected LP during its Result screen, but BeginDay resets BGM demand/identity/sound and completed selection. Its .6s fade completes during the existing 3s day introduction, before Day1's customer cycle. Prologue starts with no requested BGM. Tutorial TUTORIAL identity, five dialogue rows, instructions, focus and history exclusion remain unchanged. No startup RS001 fallback is used.

## 8. RS001~RS006 runtime evidence

[Real-audio fixture evidence](../../Saved/MVPCompletion/20261110T053853Z-audio-handoff-runtime.json), PASS.

| Record | Canonical audio -> same BGM | Active components | Duplicate safe |
|---|---|---:|---|
| RS001 | PASS | 1 | PASS |
| RS003 | PASS | 1 | PASS |
| RS005 | PASS | 1 | PASS |
| RS006 | PASS | 1 | PASS |
| RS002 | PASS | 1 | PASS |
| RS004 | PASS | 1 | PASS |


The isolated real-mixer fixture uses canonical HandleRecordSelected and actual TT audio/return APIs, with a clearly labeled unsaved Result-state setup to avoid gesture geometry. It covers RS001 -> RS003 -> RS005 -> RS006 -> RS002 -> RS004, immediate replacement, same source audio, and natural RS004 looping. The continuous production week separately exercises real UI, needle contact, focused listening, Result, customer exit and day progression.

## 9. Duplicate / idempotence / lifetime

Repeated StartStoreBGM while requested returns without allocation. Injected Finished events while its component is still playing cannot restart it. Stop clears demand and unbinds before fade, preventing old callbacks from reviving a stopped track. AutoDestroy and no-level-persistence remain enabled. Runtime asserts one live audio and one owner-held BGM component after handoff, no TT component after completion, and zero owner-held/playing components after Stop. Continue must retain the current component unless an actual observed natural completion causes the approved loop. An unsaved validation observer counts real OnAudioFinished events, so Dialogue component changes are accepted only for natural EOF, with the same canonical ID/source and one live component. Existing duplicate Result/History probes remain enabled in the natural week.

Empty completed selection is directly rejected with no fallback. Unknown RecordID, mismatched identity and missing Audio are rejected by the shared playable resolver. Missing Audio and unknown ID also have separate integration fixtures; mismatched row identity is protected by the resolver graph, without claiming a dedicated injected runtime case. The isolated BGM test does not claim direct malformed-row injection coverage.

## 10. Full seven-day regression

[Corrected full week](../../Saved/MVPCompletion/20261110T062749Z-narrative-week.json) and [12-group Core aggregate](../../Saved/MVPCompletion/20261110T062749Z-narrative-gate.json), PASS. Tutorial1 + scheduled16 =17 natural cycles; every selected LP becomes the matching BGM. History16 identities/scores/results, duplicate guards and New Game empty history PASS. Day audio resets0..7 =8; same-day Dialogue source retention9; no old BGM at next Listening; no Continue restart. Final day cleanup and the existing FinalStoryEvent hook occur once. This final run had no natural EOF within the bounded Dialogue intervals; separate isolated RS004 and RS001 tests prove natural looping.

| Customer | Visit | Day | Selected / Store BGM |
|---|---:|---:|---|
| TUTORIAL | 0 | 0 | RS001 |
| A | 1 | 1 | RS002 |
| E | 1 | 1 | RS002 |
| B | 1 | 2 | RS003 |
| C | 1 | 2 | RS005 |
| A | 2 | 3 | RS003 |
| F | 1 | 3 | RS003 |
| D | 1 | 3 | RS006 |
| B | 2 | 4 | RS004 |
| C | 2 | 4 | RS005 |
| A | 3 | 5 | RS002 |
| G | 1 | 5 | RS005 |
| B | 3 | 6 | RS004 |
| D | 2 | 6 | RS006 |
| H | 1 | 6 | RS006 |
| TEMP_D7_01 | 1 | 7 | RS001 |
| TEMP_D7_02 | 1 | 7 | RS002 |


Preserved Tutorial + A1/A2/A3, B1/B2/B3, C1/C2, D1/D2, E/F/G/H, explicit dialogue routing, visit profiles, result reactions, score formula, authored three-card order, History16, copied query isolation and duplicate callbacks. Day7 TEMP visits and FinalStoryEvent hook retain approved placeholder behavior; no story content added.

## 11. Audio configuration

| Setting | Final value / owner |
|---|---|
| StoreBGMVolume | .18, GFM explicit editable tuning |
| StoreBGMFadeInDuration | .5 seconds, same GFM tuning |
| StoreBGMFadeOutDuration | .6 seconds, same GFM tuning |
| Listening volume / fade | Existing TT 1.0 / .8s retained |
| Listening return fade / motion | Existing TT .45s / 1.2s retained |
| SoundWave volume | Existing six LP .8 retained |
| Listening duration | Existing GFM10s retained |
| Store looping | Existing completion event recreates same cached source, no source-loop flag changes |

The .18 multiplier is an initial target, not a subjective loudness approval. No repeated new tuning literals across Blueprint call sites. Audio files, import settings, supported RPM33/45/78 and catalogue schema were not changed.

## 12. Exact changed files for this Gate

15 incremental files: two modified Production packages, five modified validation sources, six new tooling/reference files and two new documents.

| File | Status |
|---|---|
| [Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset](../../Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset) | modified |
| [Content/RecordShop/Interaction/Actors/BP_Turntable.uasset](../../Content/RecordShop/Interaction/Actors/BP_Turntable.uasset) | modified |
| [Docs/Architecture/AudioHandoffPlan.md](../../Docs/Architecture/AudioHandoffPlan.md) | new |
| [Docs/Architecture/AudioHandoffReport.md](../../Docs/Architecture/AudioHandoffReport.md) | new |
| [Scripts/Unreal/audio_handoff_reference.json](../../Scripts/Unreal/audio_handoff_reference.json) | new |
| [Scripts/Unreal/audio_handoff_validation_support.py](../../Scripts/Unreal/audio_handoff_validation_support.py) | new |
| [Scripts/Unreal/install_audio_handoff.py](../../Scripts/Unreal/install_audio_handoff.py) | new |
| [Scripts/Unreal/record_expansion_support.py](../../Scripts/Unreal/record_expansion_support.py) | modified |
| [Scripts/Unreal/run_audio_handoff_gate.py](../../Scripts/Unreal/run_audio_handoff_gate.py) | new |
| [Scripts/Unreal/validate_audio_handoff.py](../../Scripts/Unreal/validate_audio_handoff.py) | new |
| [Scripts/Unreal/validate_audio_handoff_contract.py](../../Scripts/Unreal/validate_audio_handoff_contract.py) | new |
| [Scripts/Unreal/validate_day_audio.py](../../Scripts/Unreal/validate_day_audio.py) | modified |
| [Scripts/Unreal/validate_day_week.py](../../Scripts/Unreal/validate_day_week.py) | modified |
| [Scripts/Unreal/validate_mvp_cycle.py](../../Scripts/Unreal/validate_mvp_cycle.py) | modified |
| [Scripts/Unreal/validate_record_expansion_contract.py](../../Scripts/Unreal/validate_record_expansion_contract.py) | modified |


This is incremental to the user's existing unstaged Record Expansion work, not a list that attributes all prior edits to this Gate. The combined worktree currently has [75 reviewed changed paths](../../Saved/MVPCompletion/audio-handoff-combined-inventory.json): prior63 + this15 - three shared validation files. Historical baseline JSON files are unchanged. A new reference declares exactly two allowed package before/after hashes and freezes 74 other function graphs. Hash migration validates known before values and never exempts arbitrary packages.

## 13. Compile / dependencies / map / cook

Dependency closure338 packages;28 Blueprint compilations; missing0, redirector0, compile failures0. Production map startup PASS. Bounded Windows Cook PASS: map1, result/prologue widgets1 each, expansion media6, narrative foundation26, history contract1, week schedule1, days7, visits16. Native RS001/2/3 cycles all passed their first attempt on this production state, including original owner-alignment thresholds. Host unittest11 PASS; changed Python10 sources parse; scoped diff check clean.

[Consolidated26-group evidence](../../Saved/MVPCompletion/audio-handoff-final-evidence.json):25 successful process results from this Gate retained explicitly; only the complete natural week was freshly rerun after harness corrections. No production package changed between these executions. The [initial aggregate](../../Saved/MVPCompletion/20261110T053837Z-audio-handoff-gate.json) remains failed and is not presented as a passing run.

Execution diagnostics retained:

- [First week055751](../../Saved/MVPCompletion/20261110T055751Z-narrative-week.json),6 cycles: test dereferenced an already auto-destroyed component wrapper. Fixed by checking the retained path against actual live world components; no-overlap assertion preserved.
- [Second week061330](../../Saved/MVPCompletion/20261110T061330Z-narrative-week.json),11 cycles: test required unchanged component across Dialogue despite approved EOF loop replacement. Fixed by observing actual finish events and validating source/ID/single active component. Final bounded intervals did not themselves hit EOF, so no claim of direct natural-Dialogue-EOF coverage.
- [Obsolete062426 aggregate](../../Saved/MVPCompletion/20261110T062426Z-narrative-gate.json): cancelled because a host patch assertion had prevented the observer change. Only owned Cmd PID42708 was stopped after executable-path/exact UTC-start validation; user Editor untouched.
- [Final week062749](../../Saved/MVPCompletion/20261110T062749Z-narrative-week.json): all17 cycles and History16 PASS with the corrected observer. Neither failures nor process statuses were overwritten.

| Group | Result | Evidence |
|---|---|---|
| audio_contract | PASS | [evidence](../../Saved/MVPCompletion/20261110T053837Z-audio-handoff-contract.json) |
| audio_runtime | PASS | [evidence](../../Saved/MVPCompletion/20261110T053853Z-audio-handoff-runtime.json) |
| full_regression/contract | PASS | [evidence](../../Saved/MVPCompletion/20261110T054007Z-records456-contract.json) |
| full_regression/order1 | PASS | [evidence](../../Saved/MVPCompletion/20261110T054049Z-records456-order1.json) |
| full_regression/order2 | PASS | [evidence](../../Saved/MVPCompletion/20261110T054316Z-records456-order2.json) |
| full_regression/order3 | PASS | [evidence](../../Saved/MVPCompletion/20261110T054418Z-records456-order3.json) |
| full_regression/narrative_core/contract | PASS | [evidence](../../Saved/MVPCompletion/20261110T054525Z-customer-efgh-contract.json) |
| full_regression/narrative_core/matrix | PASS | [evidence](../../Saved/MVPCompletion/20261110T054601Z-customer-efgh-sequences.json) |
| full_regression/narrative_core/cd_b_a_core/contract | PASS | [evidence](../../Saved/MVPCompletion/20261110T054712Z-customer-cd-contract.json) |
| full_regression/narrative_core/cd_b_a_core/matrix | PASS | [evidence](../../Saved/MVPCompletion/20261110T054743Z-customer-cd-sequences.json) |
| full_regression/narrative_core/cd_b_a_core/b_a_core/contract | PASS | [evidence](../../Saved/MVPCompletion/20261110T054844Z-customer-b-contract.json) |
| full_regression/narrative_core/cd_b_a_core/b_a_core/matrix | PASS | [evidence](../../Saved/MVPCompletion/20261110T054914Z-customer-b-sequences.json) |
| full_regression/narrative_core/cd_b_a_core/b_a_core/a_and_core/contract | PASS | [evidence](../../Saved/MVPCompletion/20261110T055025Z-customer-a-contract.json) |
| full_regression/narrative_core/cd_b_a_core/b_a_core/a_and_core/matrix | PASS | [evidence](../../Saved/MVPCompletion/20261110T055049Z-customer-a-sequences.json) |
| corrected_core/editor | PASS | [evidence](../../Saved/MVPCompletion/20261110T055209Z-narrative-editor.json) |
| corrected_core/sequence | PASS | [evidence](../../Saved/MVPCompletion/20261110T055250Z-narrative-sequence.json) |
| corrected_core/integration | PASS | [evidence](../../Saved/MVPCompletion/20261110T055336Z-narrative-integration.json) |
| corrected_core/guards | PASS | [evidence](../../Saved/MVPCompletion/20261110T055621Z-narrative-guards.json) |
| corrected_core/rs001 | PASS | [evidence](../../Saved/MVPCompletion/20261110T060243Z-narrative-rs001.json) |
| corrected_core/rs002 | PASS | [evidence](../../Saved/MVPCompletion/20261110T060554Z-narrative-rs002.json) |
| corrected_core/rs003 | PASS | [evidence](../../Saved/MVPCompletion/20261110T060730Z-narrative-rs003.json) |
| corrected_core/isolated | PASS | [evidence](../../Saved/MVPCompletion/20261110T060901Z-narrative-isolated.json) |
| corrected_core/audio | PASS | [evidence](../../Saved/MVPCompletion/20261110T061043Z-narrative-audio.json) |
| corrected_core/startup | PASS | [evidence](../../Saved/MVPCompletion/20261110T061148Z-narrative-startup.json) |
| corrected_core/cook | PASS | [evidence](../../Saved/MVPCompletion/20261110T061211Z-cook-final.log) |
| corrected_core/week | PASS | [evidence](../../Saved/MVPCompletion/20261110T062749Z-narrative-week.json) |


Bounded Windows cook is a loose-cook check using the existing runner. It does not claim a staged/packaged executable or packaged-device audio test. All Unreal mutations used supported Blueprint Editor APIs and saved only GFM/TT; no raw uasset/umap edits.

## 14. Known limitations

- Same-track restart at Result, with existing return timing; no playback-position continuity guarantee. Natural source looping can also have a component-recreation boundary.
- Ultra-fast next Play may truncate the old fade to guarantee clean ownership.
- Existing native owner-alignment timing risk from the prior Gate is distinct from candidate ordering; no alignment assertion was relaxed.
- The isolated audio fixture intentionally injects Result state; production week supplies natural end-to-end evidence.
- Known engine startup smoke-test log messages are classified separately by existing automation. Passing gameplay evidence is not a claim that every engine log is globally error-free.
- The unsaved observer covers bounded Dialogue/Result intervals, observing the interval-entry component. It is not an exhaustive multi-loop long-session audit; its finish allowance relies on the current explicit Stop paths unbinding first.
- Human audio quality/volume, real hardware input and packaged validation remain pending.

## 15. MANUAL REVIEW

All require human acceptance: Store BGM loudness; Listening -> BGM restart/fade/gap; BGM -> next Listening fade; Dialogue balance; RS001~006 perceived loudness; actual mouse/gamepad; packaged executable audio; long-session fatigue. No subjective pass is inferred from component state, waveform statistics or screenshots.

## 16. Git LFS / temporary folder permissions

The previous LFS status shell failure remains; no repository configuration changes were attempted. Source SHA comparisons and scoped Git inventory are available, and the index is checked separately. The previously reported empty `ArtSource/Audio/Music/recordshop-expansion-fiqbw4uv` directory remains permission-denied; it is not an imported/cooked asset. These did not prevent Editor validation/cook, but a normal workstation should resolve status/LFS and source cleanup before a release commit/reproducibility check. They block a complete release-workflow status audit in this sandbox; they are not demonstrated runtime/cook blockers. A release still requires normal Git/LFS status review and packaged/manual audio acceptance.

## 17. Day7 / Ending Phase readiness

**Technically ready for a separately authorized Day7/Ending Phase after this Audio Gate**. This Gate stops at Audio/BGM ownership and transitions. Day7 narrative, ending, FinalStoryEvent content, overlap/event, mesh and world expansion were not implemented. Technical readiness does not substitute for the manual audio/input/package acceptance above or authorize new story content.

## 18. Suggested commit plan

No staging/commit/push performed. The prior LP Gate and this Gate share three currently uncommitted validation files, so a path-only two-commit split can create an invalid intermediate state. Recommend one reviewed integrated commit for the current75-path LP-content + audio-handoff change: `feat(records): complete six-LP content and selected-record store BGM`. If two commits are required, first reconstruct/review the exact pre-handoff versions of those shared validators, then apply the handoff diff as a second commit. Use an explicit reviewed path list; never use `git add .`. Human audio and packaged acceptance remain required before release.

Final independent read-only review: PASS, no Critical/Important findings. Evidence groups, week/history table,15 incremental paths,74 protected graph manifest, current package hashes and working links were cross-checked.
