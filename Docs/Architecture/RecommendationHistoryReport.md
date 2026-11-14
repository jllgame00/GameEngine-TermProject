# Recommendation History / Revisit Memory Production Gate 보고서

## 1. 시작 branch / HEAD / status

- 경로: `D:/univ/3-1/GameEngine/Termproject/RecordShop`.
- Branch: `feature/day-system-customer-queue`.
- HEAD: `53a942b4e91dda464278c119185eb2294d1f9868` (`feat: add seven-day production customer queue`).
- 시작 worktree clean. 앞선 Day Gate 구현이 commit된 상태에서 시작했다.
- Read-only production 감사: `Saved/MVPCompletion/20261109T063934Z-history-start-audit.json`.
- Production map / 기존 ThirdPerson GameMode / Character / Controller / 환경을 유지했다.
- `.uasset`은 Editor Python / BlueprintGraphEditor / EditorAssetLibrary로만 변경했다.

## 2. 기존 Result authority

- `WBP_RecordSelect → BP_RecordShelf.RecordSelected → BP_GameFlowManager.HandleRecordSelected → BP_Turntable.SetRecord` 유지.
- DialogueManager의 기존 Mood / Genre / Theme 계산과 GFM RawRecommendationScore / RawScoreAvailable을 유지했다.
- 점수는 selection 단계에서 계산되지만, 이 단계에는 History를 쓰지 않는다.
- 기존 HandleTurntableCompleted의 accepted Result chain이 ResultStartedForCustomer를 설정하고 Result UI에 현재 레코드와 점수를 전달한다.
- 기존 `SetRawScoreDisplay` 바로 뒤, `AddToViewport` 전에 History 기록 함수를 삽입했다. UI에 전달된 값과 같은 확정 값을 capture한다.
- Result Continue / CustomerExited / cleanup은 기존 GFM과 Customer lifecycle이 계속 소유한다.

## 3. History ownership 선택과 이유

- 기존 `BP_GameFlowManager`가 session History를 소유한다. 이 actor는 같은 Production map에서 Day 1~7 내내 유지된다.
- 기존 TutorialComplete / CurrentDay 역시 runtime 값이다. 설정된 custom GameInstance / SaveGame / serialization authority는 없다.
- GameInstance나 별도 manager를 추가하지 않았다. 현재 SelectedRecord 소유권은 이동시키지 않았다.
- 작은 Blueprint UObject entry를 저장한다. 공개 조회는 entry 사본을 반환한다. Narrative가 반환값을 바꿔도 원본 기록은 바뀌지 않는다.
- 프로젝트는 Blueprint-only다. 현재 검증된 Editor Python에는 사용자 struct의 멤버 편집 API가 없어, raw struct 편집이나 신규 C++ runtime module 대신 기존 Blueprint automation으로 안전하게 생성 가능한 payload class를 선택했다.

## 4. History Entry 구조

`/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry`

| 필드 | 타입 | 의미 |
|---|---|---|
| CustomerID | Name | Schedule의 stable ID |
| VisitNumber | int | Schedule의 방문 번호 |
| Day | int | Schedule의 Day |
| RecordID | Name | 기존 ST_RecordData.RecordID |
| RecommendationScore | int | 확정된 0~3 점수 |
| RecommendationResult | Name | BEST / GOOD / POOR |
| Sequence | int | 세션 내 확정 기록 순서, 1부터 |

Entry에는 Record struct 전체, Customer actor, Widget, SoundWave 등 asset/actor 참조를 저장하지 않는다.
현재 canonical catalogue는 WBP_RecordSelect의 authored MakeStruct 값이다. 이 Gate는 중복 catalogue나 별도 Record resolver를 만들지 않았다. 이후 resolver가 필요하면 기존 catalogue를 단일 공유 data authority로 추출하는 것이 선행 작업이다.

## 5. 저장 시점 / 확정 조건

- 실제 Listening 종료 → 기존 Result 진입 승인 → SetRawScoreDisplay → CommitRecommendationHistory.
- ActiveVisit / ActiveCustomer / Turntable / Result widget 유효, ResultStartedForCustomer, Result state, RawScoreAvailable, Day 일치, 유효한 ID / VisitNumber / 점수 범위를 확인한다.
- `(CustomerID, VisitNumber)`가 이미 있으면 반환한다. 첫 확정 기록을 유지한다.
- Result가 열리기 전 selection / 조기 callback에서는 기록하지 않는다. 사용할 점수가 없는 경우 임의의 POOR를 생성하지 않는다.
- BEST는 score>=3, GOOD은 score>=2, 나머지는 POOR로 기존 Result UI 기준을 따른다. 기록 가능한 점수 범위는 0~3이다.
- Tutorial에는 ActiveVisit이 없으므로 일반 고객 History에 기록하지 않는다.
- 기존 Result에는 Cancel 동작이 없다. 이번 Gate에서 취소 UI나 임시 결과 시스템을 추가하지 않았다.

## 6. 조회 API / Narrative 사용 계약

모두 기존 GameFlowManager에서 Blueprint 호출 가능하다.

| API | 반환 / 의미 |
|---|---|
| HasPreviousVisit(CustomerID) | 해당 ID의 확정 기록 존재 여부, pure |
| GetLatestRecommendation(CustomerID) | 마지막 확정 entry 사본, 없으면 None |
| GetRecommendationHistory(CustomerID) | 해당 ID만, 확정 순서의 사본 배열 |
| GetRecommendationForVisit(CustomerID, VisitNumber) | 정확한 방문의 사본, 없거나 0 이하 번호면 None |
| GetActiveVisitMemory() | CustomerID, VisitNumber, Day, HasPrevious, Latest |

Snapshot을 만드는 조회는 실행 pin을 가진 함수다. Entry는 IsValid로 검사한 뒤 필드를 읽는다. 반환 배열 / entry를 backing storage로 사용하지 않는다.

`GetActiveVisitMemory`는 현재 VisitNumber보다 작은 기록만 포함한다. Result 이후 호출해도 현재 방문을 자신의 이전 방문으로 취급하지 않는다.

`OnRevisitMemoryReady(CustomerID, VisitNumber, HasPrevious)`는 기존 Dialogue setup guard를 통과한 후 DialogueManager.StartDialogue 바로 전에 발생한다. 다음 Narrative는 이 event에서 조회 API를 호출할 수 있다. 실제 대사 / 분기는 작성하지 않았다.

## 7. Day System 연결

- CustomerID / VisitNumber / Day는 기존 ActiveVisit data authority에서 가져온다. History로 방문 번호를 다시 계산하지 않는다.
- Day 시작 / 종료 / 고객 cleanup은 History를 clear하지 않는다.
- New Game은 fresh map / GameFlowManager session이다. 기본 History가 비어 있으며 BeginPlay의 guarded ResetRecommendationHistory로 초기화한다.
- Reset 함수는 private이며 Day 0 / tutorial 미완료 / active customer 없음 조건에서만 동작한다. 진행 중 Day에서 호출해도 기록을 지우지 않는다.
- 반복 BeginPrologue나 Day 전환에는 reset을 연결하지 않았다.

## 8. 정확한 변경 파일

```text
Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset
Content/RecordShop/Data/History/BP_RecommendationHistoryEntry.uasset
Docs/Architecture/RecommendationHistory.md
Docs/Architecture/RecommendationHistoryReport.md
Scripts/Unreal/cook_mvp.py
Scripts/Unreal/history_validation_support.py
Scripts/Unreal/install_recommendation_history.py
Scripts/Unreal/run_history_gate.py
Scripts/Unreal/validate_day_week.py
Scripts/Unreal/validate_history_contract.py
Scripts/Unreal/validate_history_editor.py
Scripts/Unreal/validate_history_guards.py
Scripts/Unreal/validate_history_week.py
```

## 9. A / B / C / D 반복 방문 검증

| Customer | Verified entries (Visit / Day / LP / Score / Result) |
|---|---|
| A | V1 / D1 / RS002 / 2 / GOOD; V2 / D3 / RS003 / 0 / POOR; V3 / D5 / RS002 / 2 / GOOD |
| B | V1 / D2 / RS001 / 3 / BEST; V2 / D4 / RS003 / 0 / POOR; V3 / D6 / RS001 / 3 / BEST |
| C | V1 / D2 / RS002 / 2 / GOOD; V2 / D4 / RS001 / 3 / BEST |
| D | V1 / D3 / RS002 / 2 / GOOD; V2 / D6 / RS002 / 2 / GOOD |
| E | V1 / D1 / RS003 / 0 / POOR |
| F | V1 / D3 / RS001 / 3 / BEST |
| G | V1 / D5 / RS003 / 0 / POOR |
| H | V1 / D6 / RS003 / 0 / POOR |
| TEMP_D7_01 | V1 / D7 / RS001 / 3 / BEST |
| TEMP_D7_02 | V1 / D7 / RS002 / 2 / GOOD |

Live evidence: `Saved/MVPCompletion/20261109T065451Z-history-week.json`. Tutorial 1 + queue 16 cycles PASS; 16 history entries.
A/B/C/D revisit APIs and active previous-only context PASS. E/F/G/H had no prior record on entry. New Game fresh session empty PASS.
Day started/ended [1..7]; FinalStoryEvent once; memory events 16 with exact IDs/visit numbers and expected previous flags.

## 10. 중복 기록 방지 결과

Same-visit HandleTurntableCompleted and private commit probes were repeated three times at Result. Entry count and payload stayed unchanged. Early selection-time commit rejected; active-day reset rejected. Query snapshot mutation did not alter canonical records.

Tutorial did not create a general history entry. Every distinct queued visit created one entry, using the authored VisitNumber. No cross-customer records appeared.

## 11. 기존 E2E / 공통 regression

| Group | Result | Process evidence |
|---|---|---|
| editor | PASS | `20261109T065327Z-history-editor.json` |
| week | PASS | `20261109T065451Z-history-week.json` |
| rs001 | PASS | `20261109T070449Z-history-rs001.json` |
| rs002 | PASS | `20261109T070627Z-history-rs002.json` |
| rs003 | PASS | `20261109T070803Z-history-rs003.json` |
| isolated | PASS | `20261109T070941Z-history-isolated.json` |
| audio | PASS | `20261109T071156Z-history-audio.json` |
| startup | PASS | `20261109T071320Z-history-startup.json` |
| cook | PASS | `20261109T071349Z-cook-final.log` |

304 dependency packages / 26 Blueprint compiles; missing packages, redirectors and compile failures: 0.
Natural scores: RS001=3 / RS002=2 / RS003=0. Prologue/Tutorial, current-record identity, physical turntable steps, ten-second listening, Result/Store BGM, input/cursor/focus/camera recovery passed.
Loose Windows cook included the production map, Result/Prologue UI, seven-day schedule and BP_RecommendationHistoryEntry. Not a packaged executable test.
Known engine startup smoke errors are classified separately; gameplay unexpected errors were zero in passing process reports.

## 12. Persistence 현재 수준

- `RUNTIME_HISTORY_READY`: verified across Day 1~7 and fresh New Game reset.
- `SAVEGAME_NOT_WIRED`: disk slot, save/load, Continue, cross-map persistence를 구현하지 않았다.
- Entry의 primitive 필드 7개는 후속 SaveGame value schema로 복사하기 쉽다. 현재 UObject reference 배열을 그대로 저장하면 완전한 payload가 직렬화된다고 주장하지 않는다.
- `SAVEGAME_READY_BUT_NOT_WIRED`라는 이름으로 검증되지 않은 serialization 호환성을 보장하지 않는다. 실제 SaveGame archive/schema 및 round-trip 검증은 후속 persistence phase에 남긴다.

## 13. Known limitations / review

- 현재 A~H / Day 7은 기존 Customer01의 임시 presentation / dialogue를 사용한다.
- 조회는 작은 16개 방문 배열을 순회한다. 별도 index/cache authority를 만들지 않았다.
- Schedule / ID를 변경한 뒤 이전 기록을 migration하는 기능은 없다.
- 내부 backing array를 외부 Narrative에서 직접 수정하는 사용법은 지원하지 않는다. 공개 query API만 사용한다.
- 미확정 score / invalid Day / 범위 밖 score 거부는 code guard가 있다. 자동 isolated 진단의 범위를 최종 검증 항목과 구분한다.
- 독립 read-only 코드 리뷰에서 Critical / Important 결함은 발견되지 않았다. Minor: 중복 검사는 같은 payload 반복이고, 임의의 상충 payload나 모든 malformed Result 조합을 동적 검증하지 않는다. Hook의 StartDialogue 이전 순서는 graph 연결로 확인하며 dispatcher 순서 전체를 동적 trace하지 않는다.
- Story / Relationship / Ending / 새 UI / Character Art / Save/Continue를 추가하지 않았다.

## 14. MANUAL REVIEW

- 기존 Korean Result UI / camera blend / focus / 커서 / 이동 복귀의 실제 플레이 감각.
- 스피커 청취로 10초 Listening / Store BGM 음량과 fade 확인.
- 다음 Narrative 담당자가 Blueprint에서 OnRevisitMemoryReady를 bind하고 snapshot API 반환값을 사용하는 흐름 확인.
- Packaged executable 및 gamepad 조작. Cook은 loose cook smoke이며 packaged build 검증이 아니다.
- 이번 Gate는 플레이어용 History UI나 재방문 대사를 추가하지 않으므로 신규 narrative 화면 육안 검증 대상은 없다.

## 15. 다음 Revisit Narrative Phase 진입 가능 여부

최종 Gate가 PASS하면 진입 가능하다. OnRevisitMemoryReady와 GetActiveVisitMemory / 고객별 query가 연결 지점이다. 실제 Story 분기 구현으로 넘어가지 않고 여기서 멈춘다.

## 16. 추천 commit 계획

- 자산 + 재현 installer + data contract: `feat: add session recommendation history and revisit memory`.
- 검증 자동화 + 문서: `test: verify revisit history across the seven-day queue`.
- 실제 staging / commit / push는 수행하지 않았다. 기존 브랜치와 HEAD를 유지한다.

## Final evidence

- `Saved/MVPCompletion/20261109T071637Z-history-gate.json`: complete=true / pass=true / **10 groups PASS**.
- The aggregate retains explicit original process reports, assertions, native exits and log classification. Passing production runs were reused without rerunning after documentation-only edits.
- API/copy/reset diagnostics: `20261109T071444Z-history-guards-process.json` PASS. Fixture writes use an unsaved Blueprint setter; the production backing array remains non-editable in the Editor instance panel.
- All passing Unreal processes exited 0. Cook errors 0; missing/redirector/compile failure 0. Known engine startup smoke errors are retained separately, so the full Editor log is not claimed globally error-free.
- First installer probe saved no assets: internal Construct Object Outer pin name is `self`; the engine source established the correct name. An initial contract harness used function descriptors as names; it now checks graph names. Initial isolated fixture setup was refused by Editor edit flags and was replaced with explicit unsaved runtime setters. Those original diagnostic reports remain under Saved.
- No production change was needed after the full ten-check run began; the final rerun changed the guard test fixture only.
- Python syntax and git diff whitespace checks passed. Branch/HEAD preserved; no staged files, commits or pushes.
- Gate PASS: Revisit Narrative Phase can consume the documented snapshot APIs. Actual narrative branching remains unimplemented by scope.

