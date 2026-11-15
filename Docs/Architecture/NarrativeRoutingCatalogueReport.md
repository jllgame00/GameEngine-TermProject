# Narrative Routing / Catalogue Foundation Production Gate 보고서

## 1. 시작 branch / HEAD / status

- 작업 경로: `D:/univ/3-1/GameEngine/Termproject/RecordShop`.
- Branch: `feature/narrative-routing-catalog`.
- HEAD: `bf949b390e54338f81cc70f87ea9a7cfaadba2e4`; 시작 worktree clean.
- Read-only graph/data 감사: `Saved/MVPCompletion/20261109T075728Z-narrative-start-audit.json`.
- 기존 Production map / ThirdPerson GameMode / Character / 환경 / Input mapping을 유지했다.
- 자산 변경은 Editor Python / BlueprintGraphEditor / AssetTools / EditorAssetLibrary로만 수행했다. Raw asset 편집은 하지 않았다.

## 2. 기존 Mood-only 문제의 root cause

감사 당시 DialogueManager EventGraph의 StartDialogue는 CustomerDialogue의 모든 row name을 읽어 `DialogueData.Mood == CurrentMood`인 행을 DialogueList에 추가한 뒤 이름순 정렬했다. CustomerID와 VisitNumber를 비교하지 않았다. ShowNextLine도 CustomerDialogue를 직접 읽었다. 같은 Mood 대사를 추가하면 서로 섞이는 구조였다.

WBP_RecordSelect는 BTN_LP01/02/03 클릭 delegate에 각각 K2Node_MakeStruct_1/6/0을 직접 연결했다. 이 세 node가 Title/Artist/Tags/Audio의 실제 authoring site였다. 기존 Shelf → GFM → Turntable handoff는 이미 단일 경로였다.

## 3. Dialogue Sequence architecture

- 기존 DialogueManager에 `SetPendingDialogueSequence(SourceTable, OrderedRowNames, SequenceID) → Accepted`, `ClearPendingDialogueSequence`, `CancelDialogueSequence`를 추가했다.
- SourceTable의 row struct, nonempty sequence ID/rows, 모든 row 존재 여부를 먼저 검증한다. 잘못된 pending은 거부/clear하고 Start에서 기존 legacy Mood routing으로 fallback한다.
- Start는 active 동안 재호출을 무시한다. pending을 active source/rows/SequenceID로 한 번 복사하고 pending을 clear한다.
- Next는 같은 active source와 ordered rows만 사용한다. line index를 진행한 뒤 UI event를 알린다. 종료·취소 후 active/pending source, rows, ID, index를 해제하며 늦은 Next가 finish event를 다시 내지 않는다.
- 기존 CalculateLPScore/EvaluateLP의 비교 및 event 경로는 유지했다. 별도 Dialogue manager를 만들지 않았다.
- 기존 BP_CustomerVisitDefinition에 `Narrative` reference를 추가했다. BP_VisitNarrativeDefinition에는 SequenceID, SourceTable, OrderedRows, MemoryVisitNumbers, 결과별 intro row arrays, optional profile override, CandidateRecordIDs, ReviewStatus, ContentVersion이 있다.
- CustomerID/VisitNumber는 이 Definition에 중복 저장하지 않는다. 기존 ActiveVisit의 reference로 resolve한다. 인물별 대형 Branch는 없다.
- READY인 Definition만 소비한다. A1만 DA_A1_Narrative를 연결했으며 원본 CustomerDialogue의 5개 row를 참조한다. 원문을 새 테이블로 복제하지 않았다.
- GFM은 지정된 이전 방문 History 사본을 먼저 읽어 intro key와 row 배열을 구성하고, pending을 설정한 뒤 기존 OnRevisitMemoryReady를 알린다. 이후 기존 StartDialogue로 들어간다.
- 여러 MemoryVisitNumbers는 오름차순·중복 없이 작성한다. 마지막 요청 번호가 intro를 결정하며, 마지막 기록이 없으면 NO_MEMORY다. 유효한 다른 기록들은 snapshot으로 남긴다. 결과 합산/호감도는 없다.

## 4. Tutorial identity 분리

- 새 Customer class/mesh를 만들지 않고 기존 BP_Customer01 presentation을 재사용한다.
- spawn 직후 runtime CustomerProfile.CustomerID를 TUTORIAL로, 표시 역할을 연습 손님으로 설정한다. 원본 C01 class default는 변경하지 않는다.
- DA_TutorialNarrative / DT_TutorialDialogue의 짧은 5행 연습 안내를 사용한다. 실제 새 캐릭터 이름/스토리는 없다.
- Tutorial은 ActiveVisit이 없어 일반 Recommendation History에 들어가지 않는다.
- 이후 Day 1 A는 별도 actor이며 ID=A, VisitNumber=1, SequenceID=A_Visit1로 기존 C01 5행을 사용한다. Tutorial과 합치거나 VisitNumber를 변경하지 않았다.

## 5. Catalogue ownership

- 단일 record row authority: `/Game/RecordShop/Data/Records/DT_RecordCatalogue`, row struct ST_RecordData.
- BP_RecordCatalogue / DA_RecordCatalogue는 해당 table과 임시 default candidate ID 3개를 참조하는 lookup service다. 추가 record payload 복사본을 authoring하지 않는다.
- `ResolveRecord(RecordID) → Found, Record`는 typed row를 조회한다. `ResolvePlayableRecord`는 ID 일치와 실제 Audio reference도 확인한다.
- 원본 RS001~003의 Title/Artist localization identity, Mood/Genre/Theme/Energy, Cover, Audio 값을 그대로 이전했다.
- History의 RecordID도 같은 서비스로 resolve할 수 있다.
- GameInstance나 catalogue에 SelectedRecord 상태를 옮기지 않았다. 선택은 계속 `WBP_RecordSelect → BP_RecordShelf.RecordSelected → BP_GameFlowManager.HandleRecordSelected → BP_Turntable.SetRecord`다.

## 6. Visit candidate architecture

- optional CandidateRecordIDs는 Visit의 Narrative reference 안에 있다. A1만 RS001/RS002/RS003을 명시했다.
- 다른 방문은 Definition이 없거나 후보가 비어 있으면 catalogue의 임시 default 3개를 사용한다. 다른 방문의 최종 후보 구성을 확정한 것이 아니다.
- Shelf가 active visit 후보 ID와 shared catalogue를 기존 widget에 전달한다. UI는 정확히 3개, 서로 다른 ID, resolve 가능한 playable record인지 검증한 뒤 캐시 3개와 표시를 갱신한다.
- 기존 3-button layout/폰트/선택 delegate/복귀 경로를 유지했다. 원래 MakeStruct payload authoring은 제거했다.
- 카드의 Title/Artist/3요소 표시는 resolve된 실제 데이터에서 만든다. 내부 tag의 표시명만 한국어로 변환한다.
- invalid ID/중복/후보 수 오류/audio 없는 row는 세 버튼을 비활성화하고 한국어 오류를 표시한다. 원래 Escape close/input recovery는 남아 있다. 잘못된 후보를 조용히 다른 LP로 바꾸지 않는다.
- RS004/005/006은 Production table에 없다. 6-row transient fixture로 schema와 3개 subset 선택을 검증하며 Audio 없는 후보의 선택은 거부한다.

## 7. Mood override 준비 구조

- TargetMoodOverride / TargetGenreOverride / TargetThemeOverride는 unset이면 원래 profile 값을 유지한다.
- spawn 때 복사된 runtime profile에만 적용하고, accepted Dialogue setup에서 같은 profile을 기존 DialogueManager.CurrentCustomer/CurrentMood에 동기화한다.
- Genre는 MusicPreference, Theme는 Personality에 연결한다. scoring formula는 기존 세 비교 그대로다.
- B1 Restless/Electronic/Adventurous, B2 Quiet/Electronic/Adventurous 전환은 unsaved fixture로만 검증한다. B의 Production data를 확정 적용하지 않았다.

## 8. 정확한 변경 파일

```text
Content/DialogueManager.uasset
Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset
Content/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition.uasset
Content/RecordShop/Data/Narrative/DA_A1_Narrative.uasset
Content/RecordShop/Data/Narrative/DA_TutorialNarrative.uasset
Content/RecordShop/Data/Narrative/DT_TutorialDialogue.uasset
Content/RecordShop/Data/Records/BP_RecordCatalogue.uasset
Content/RecordShop/Data/Records/DA_RecordCatalogue.uasset
Content/RecordShop/Data/Records/DT_RecordCatalogue.uasset
Content/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.uasset
Content/RecordShop/Data/Schedule/DA_Visit_A_1.uasset
Content/RecordShop/Interaction/Actors/BP_RecordShelf.uasset
Content/RecordShop/UI/RecordSelection/WBP_RecordSelect.uasset
Docs/Architecture/NarrativeRoutingCatalogue.md
Docs/Architecture/NarrativeRoutingCatalogueReport.md
Scripts/Unreal/cook_mvp.py
Scripts/Unreal/history_validation_support.py
Scripts/Unreal/install_dialogue_sequences.py
Scripts/Unreal/install_narrative_data.py
Scripts/Unreal/install_narrative_flow.py
Scripts/Unreal/install_record_candidate_ui.py
Scripts/Unreal/narrative_graph_helpers.py
Scripts/Unreal/narrative_reference_baseline.json
Scripts/Unreal/narrative_validation_support.py
Scripts/Unreal/run_narrative_gate.py
Scripts/Unreal/validate_day_week.py
Scripts/Unreal/validate_mvp_cycle.py
Scripts/Unreal/validate_mvp_dependencies.py
Scripts/Unreal/validate_mvp_regressions.py
Scripts/Unreal/validate_narrative_contract.py
Scripts/Unreal/validate_narrative_editor.py
Scripts/Unreal/validate_narrative_integration.py
Scripts/Unreal/validate_sequence_routing.py
```

## 9. A1 regression

Frozen CustomerDialogue package / 5-row content hash and original Customer01 / ST_RecordData package hashes PASS. Original Title/Artist FText namespace/key/source hashes PASS.

Live week A1 used SequenceID=A_Visit1, exact C01_Quiet_01..05 order; displayed line hash PASS. It followed the separate tutorial cycle and created A Visit1 history normally.

## 10. Tutorial regression

Live Tutorial used CustomerID=TUTORIAL / SequenceID=TUTORIAL_Training / TUTORIAL_01..05. It created no general history entry. Day 1 then spawned the separate A/Visit1 actor. Existing presentation/turntable/listening/result/exit path is reused.

## 11. Record catalogue / sequence / candidate regression

Sequence diagnostics PASS: explicit order, same-Mood source isolation, duplicate Start/rejected active replacement, five invalid pending cases, finish/cancel context clear and next legacy session.

Integration PASS: four memory intro keys before Start, multiple/mixed-missing memories, runtime B1/B2 override influencing real GFM score, original class defaults unchanged. Six-row transient catalogue supports approved RS004~006 tag combinations, but rows without audio are not playable. Reordered three-candidate widget rendered and emitted the correct selected ID; invalid/duplicate/count/no-audio sets were disabled.

Source review found no Critical/Important defect, including the final public content-accessor/cast UI implementation. Its fixed three TextBlock button-content structure is checked by the installer. Screenshot: Saved/MVPCompletion/20261109T090150Z-narrative-integration-three-candidates.png (isolated fixture; normal native captures remain separate).

## 12. Day / History / 기존 E2E regression

Final aggregate: `Saved/MVPCompletion/20261109T092552Z-narrative-gate.json` — complete=true / pass=true, 12/12 groups PASS. It reuses the successful unchanged-production reports from the serial run, then reruns only the failed isolated diagnostic. Original run/failure is retained in `20261109T090428Z-narrative-gate.json`.

| Group | Result / scope | Evidence under Saved/MVPCompletion |
|---|---|---|
| Editor | PASS: Prologue/Day/Schedule/History/Narrative contracts; 28 Blueprint compiles; 311-package dependency closure, missing/redirector/compile failure 0 | 20261109T085857Z-narrative-editor-process.json |
| Sequence | PASS: ordered explicit rows, same-Mood isolation, duplicate start, five invalid cases, finish/cancel/legacy | 20261109T083333Z-narrative-sequence-green-3-process.json |
| Integration | PASS: memory/context/override; six-row unsaved fixture; real reordered three-card widget and fail-closed candidates | 20261109T090150Z-narrative-integration-process.json |
| History guards | PASS: idempotency, rejection, per-customer isolation and reset guards | 20261109T090428Z-narrative-guards-process.json |
| Continuous week | PASS: Tutorial + 16 customer cycles / 17 unique actors; Day 1~7, memory/history, cleanup, final hook once | 20261109T090516Z-narrative-week-process.json |
| Native RS001 | PASS: score 3 / BEST, RPM33, physical station/motion, UI and input recovery | 20261109T091519Z-narrative-rs001-process.json |
| Native RS002 | PASS: score 2 / GOOD, RPM45, same natural cycle | 20261109T091658Z-narrative-rs002-process.json |
| Native RS003 | PASS: score 0 / POOR, RPM78, same natural cycle | 20261109T091838Z-narrative-rs003-process.json |
| Isolated legacy backend | PASS on rerun: unmatched Mood, modal/focus/Escape guards, RPM math, callbacks, original LP fade/reset/full completion | 20261109T092552Z-narrative-isolated-process.json |
| Store BGM | PASS: actual natural loop, single reference, fade/stop/idempotency, Prologue input/camera unchanged | 20261109T092230Z-narrative-audio-process.json |
| Map startup | PASS: production map launch/control lifecycle | 20261109T092401Z-narrative-startup-process.json |
| Windows cook | PASS: exit 0, errors 0; map/Result/Prologue/History/new foundation, 7 days / 16 visits cooked | 20261109T092432Z-cook-final-process.json |

Continuous live queue order:

```text
D1 A1 -> E1
D2 B1 -> C1
D3 A2 -> F1 -> D1
D4 B2 -> C2
D5 A3 -> G1
D6 B3 -> D2 -> H1
D7 TEMP_D7_01 -> TEMP_D7_02 -> FinalStoryEvent (once)
```

All seven starts/ends were exactly [1..7]. A/B have Visits 1/2/3, C/D 1/2; 16 History entries remain through day changes. Tutorial creates no A entry. Each completed recommendation RecordID resolves through the shared catalogue; a second fresh PIE session starts with empty History. Existing duplicate spawn/day/result guards pass. Queue tests use an explicitly labeled approach fixture for geometry; native RS1/2/3 use physical input and collision-resolved station paths.

The existing Listening timer remains 10 seconds. Native measured Play-to-Result durations are 11.159 / 11.167 / 11.166 seconds, including physical tonearm return. Result -> Store BGM, camera/cursor/focus and restored movement pass without test-side recovery corrections.

The first isolated LP reset/full-playback diagnostic timed out at the unchanged 40-second deadline while the audio component remained PLAYING. The same failure pattern exists in the earlier Day Gate report `20261109T062325Z-day-isolated.json`. No production audio/turntable change was made. Scalar wall/world timing was added; rerun passed full natural completion at 34.141 seconds (world 34.215 seconds), with early fade at 1.219 seconds and no overlapping voices. The intermittent timeout root cause is not established; the initial failure is not discarded or claimed fixed.

All process reports show zero unexpected gameplay errors. Existing engine startup smoke-test `Condition failed` messages are explicitly classified separately; this is not a claim that every Editor log is globally error-free. Cook uses SkipSaveAssetRegistry: packaged/staged executable validation is NOT RUN.

## 13. Known limitations

- A2/A3/B~H의 최종 narrative와 candidate set은 미구현이다. 현재 이 방문들은 기존 C01 mechanical placeholder/legacy fallback을 사용한다.
- Legacy fallback은 의도적으로 Mood-only다. 새 final narrative는 별도 source와 명시적 sequence를 사용해야 한다. 원본 CustomerDialogue에 새 Quiet 대사를 단순 append하지 않는다.
- memory intro 모듈도 data contract와 fixture까지다. 실제 A2/B 등의 BEST/GOOD/POOR 문구는 작성하지 않았다.
- candidate 수는 이번 UI 계약에서 정확히 3개다. Cover를 보여주는 새 card art나 6-card 전체 목록을 만들지 않았다.
- Tutorial은 연습 안내 text이며 같은 C01 mesh를 재사용한다. 별도 art/voice는 없다.
- Catalogue default candidate 3개는 임시 fallback이다. 모든 방문의 BEST/GOOD/POOR 구성을 보장하는 콘텐츠 정책이 아니다.
- SaveGame/Continue, 합석, Background NPC, Relationship/호감도, 경제/재고, Ending은 추가하지 않았다. Day 7 FinalStoryEvent 뒤는 TBD다.
- Blueprint array 입력은 Editor Python에서 in/out 반환값으로 함께 나타날 수 있다. 테스트는 Accepted/Ready bool을 명시적으로 추출한다. Blueprint는 해당 output pin을 사용한다.
- The isolated real-audio replay diagnostic has an inherited intermittent timeout; final rerun passes, but its root cause remains unconfirmed. Actual-device listening remains manual review.
- independent source review에서 Critical/Important 결함은 발견되지 않았다. FText identity hash와 multi-memory 누락 검사를 리뷰 후 보강했다.

## 14. MANUAL REVIEW

- Tutorial 안내 5행의 길이/말투와 기존 C01 presentation 재사용의 자연스러움.
- dynamic 3-card text의 줄바꿈/가독성, invalid 후보 화면에서 Escape 복귀.
- mouse/gamepad 실제 focus, camera blend, collision station 접근감.
- 10초 Listening / Store BGM 음량·fade의 실제 청취.
- packaged executable. Cook은 bounded loose smoke이며 packaging/staging 실행 확인은 아니다.

## 15. 다음 Narrative Content Phase

최종 자동 Gate는 12/12 PASS이며, A2 소량의 실제 sequence부터 적용할 준비가 됐다. 기존 Visit.Narrative reference와 pending/active source를 사용하고, A1 원문을 수정하거나 복제하지 않는다. 실제 7일 Dialogue 대량 작성으로 넘어가지 않고 여기서 멈춘다.

## 16. 추천 commit 계획

- `feat: add visit dialogue sequence routing and tutorial identity`.
- `feat: centralize record catalogue and visit candidate selection`.
- `test: verify narrative foundation and production regressions`.
- BP_GameFlowManager에는 두 기반의 연결이 함께 들어 있어 binary를 텍스트처럼 부분 staging하지 않는다. 연결된 자산/automation은 함께 검토하는 단위가 적절하다.
- 실제 staging / commit / push는 수행하지 않았다. 작업 branch와 HEAD를 유지한다.

Final worktree verification: branch/HEAD unchanged; 33 changed files (13 assets, 17 Python, 1 reference JSON, 2 docs), no staged files. All 17 changed Python files parse, git diff --check passes, and the frozen original package/row/record checks pass. No production asset was changed after the successful UI/Shelf installer at 08:52:32 UTC; subsequent changes were validation instrumentation/docs only.

Reference audit / RED / installers / original failed diagnostic are preserved under Saved/MVPCompletion; the final aggregate links every accepted report. Exact file inventory is section 8. No staging, commit, push or raw asset edit was performed.
