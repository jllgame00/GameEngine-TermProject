# Day System / Customer Queue Production Gate 보고서

1. **시작 상태**
   - 작업 경로: `D:/univ/3-1/GameEngine/Termproject/RecordShop`
   - Branch: `feature/day-system-customer-queue`
   - HEAD: `2ed3fa01b357f449cef00d87c2a452457761d7db`; 시작 worktree clean.
   - 이 HEAD에는 Prologue/Tutorial과 10초 Listening/Store BGM이 없었다. 사용자 선택에 따라 `fe8f16f`의 텍스트 automation을 재사용하고 Editor에서 Prologue 자산을 재생성했다. Git HEAD는 변경하지 않았다.
   - `.uasset`은 Unreal Editor Python / BlueprintGraphEditor / EditorAssetLibrary로만 변경했다. Map, 환경, Character mesh, Dialogue 원본, LP 원본 음악은 변경하지 않았다.

2. **기존 spawn / completion authority**
   - Production map: `/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox`.
   - 기존 ThirdPerson GameMode / Character / Controller 유지. 별도 map GameMode override 없음.
   - 배치된 `BP_GameFlowManager`가 유일한 spawn 및 customer cycle authority다. 기존 SpawnActor 노드 하나를 tutorial과 queue가 함께 사용한다.
   - `BP_Customer.CustomerExited`가 실제 navigation 퇴장 완료를 알린다. Result 제출이 승인한 exit token을 먼저 소비하고, 이전 actor의 dispatcher를 해제 / actor를 제거한 뒤 기존 cleanup과 queue advancement를 수행한다.
   - DialogueManager / 기존 CustomerDialogue / C01 Quiet 5행, Shelf / Turntable / Result production 경로를 재사용한다.
   - 설정된 custom GameInstance / SaveGame 없음. 신규 persistence authority를 만들지 않았다.
   - 시작 감사: `Saved/MVPCompletion/20261109T053312Z-day-start-production-audit.json`.

3. **Day System architecture**
   - 기존 `E_GameFlowState`를 유지하고 같은 GameFlowManager에 CurrentDay, DayPhase, DayCustomersComplete, FinalStoryEventTriggered를 추가했다.
   - `OnTutorialCompleted → BeginDay(1)`; 이후 `DayStarting → CustomerCycle → BetweenCustomers / DayEnding → 다음 Day`.
   - Day 7 종료는 `FinalStoryEventTriggered=true`, `DayPhase=FinalStoryEvent`를 설정한 뒤 `OnFinalStoryEvent(FinalStoryEvent)`를 한 번 발생시킨다. 후속 Ending은 TBD다.
   - 외부 소비용 dispatcher: OnDayStarted, OnDayEnded, OnCustomerVisitCompleted, OnFinalStoryEvent.
   - Day 시작 3초, 고객 간 0.35초, Day 종료 0.75초의 one-shot timer를 사용한다. Queue 완료를 Tick이나 polling으로 판단하지 않는다.

4. **Schedule data architecture**
   - `/Game/RecordShop/Data/Schedule`의 Blueprint PrimaryDataAsset 3개 정의와 24개 instance: Visit 16개, Day 7개, Week 1개.
   - Visit: CustomerID(Name), VisitNumber, Day, OrderInDay, CustomerClass, CustomerData(DataTableRowHandle), StoryEventID, IsPlaceholderContent.
   - CustomerClass가 현재 실제 profile/content reference다. CustomerData row handle은 다음 콘텐츠 연결을 위한 예약 필드이며 현재 runtime에서 읽지 않는다.
   - Day에는 정렬된 Visits 배열, Week에는 Days 배열과 FinalStoryEventID가 있다. 인스턴스 편집으로 ID / class / 방문 순서를 교체할 수 있다.
   - 현재 모든 방문의 class는 기존 BP_Customer01이다. A~H의 새 이야기나 대사는 작성하지 않았다.

5. **Queue architecture / 보존 경로**
   - CurrentCustomerIndex, CustomerQueue, ActiveVisit, QueueCycleInProgress로 진행한다.
   - 일회용 CustomerSpawnAuthorized token과 ActiveCustomer guard가 기존 spawn event의 중복 호출도 차단한다.
   - 실제 spawn 직후 기존 CustomerProfile 전체를 보존하면서 CustomerID만 ActiveVisit의 안정적인 ID로 설정한다.
   - Result → 실제 CustomerExited → cleanup → 방문 완료 event → index 증가 → 다음 spawn / Day End 순서다. QueueCycleInProgress는 완료 dispatcher 전에 소비한다.
   - Tutorial에는 ActiveVisit이 없다. Tutorial 퇴장이 끝나야 기존 TutorialComplete가 발생하고 Day 1을 시작한다.
   - SelectedRecord: `WBP_RecordSelect → BP_RecordShelf.RecordSelected → BP_GameFlowManager.HandleRecordSelected → BP_Turntable.SetRecord` 유지.
   - 10초 Listening timer는 기존 Turntable.BeginTonearmReturn을 호출한다. 기존 물리 return / fade / 완료 / Result 경로가 이어진다.
   - Result Continue와 Day Start에서 기존 RS001_Best를 임시 Store BGM으로 낮은 볼륨(0.18)으로 재생한다. Listening / Day End에서 0.6초 fade-out한다. 소스 SoundWave의 looping 설정은 변경하지 않았다.
   - Day UI는 WBP_Prologue 스타일을 재사용한 hit-test-invisible 안내다. Camera / Input / Cursor / Focus 소유권을 변경하지 않는다.

6. **정확한 변경 파일**

   아래 inventory는 보고서 작성 시 `git ls-files --modified`와 `--others --exclude-standard`로 생성한다. Saved의 검증 산출물은 git 대상에서 제외되어 있다.

```text
Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset
Content/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.uasset
Content/RecordShop/Data/Schedule/BP_DayScheduleDefinition.uasset
Content/RecordShop/Data/Schedule/BP_WeekScheduleDefinition.uasset
Content/RecordShop/Data/Schedule/DA_Day01.uasset
Content/RecordShop/Data/Schedule/DA_Day02.uasset
Content/RecordShop/Data/Schedule/DA_Day03.uasset
Content/RecordShop/Data/Schedule/DA_Day04.uasset
Content/RecordShop/Data/Schedule/DA_Day05.uasset
Content/RecordShop/Data/Schedule/DA_Day06.uasset
Content/RecordShop/Data/Schedule/DA_Day07.uasset
Content/RecordShop/Data/Schedule/DA_TemporaryWeek.uasset
Content/RecordShop/Data/Schedule/DA_Visit_A_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_A_2.uasset
Content/RecordShop/Data/Schedule/DA_Visit_A_3.uasset
Content/RecordShop/Data/Schedule/DA_Visit_B_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_B_2.uasset
Content/RecordShop/Data/Schedule/DA_Visit_B_3.uasset
Content/RecordShop/Data/Schedule/DA_Visit_C_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_C_2.uasset
Content/RecordShop/Data/Schedule/DA_Visit_D_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_D_2.uasset
Content/RecordShop/Data/Schedule/DA_Visit_E_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_F_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_G_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_H_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_TEMP_D7_01_1.uasset
Content/RecordShop/Data/Schedule/DA_Visit_TEMP_D7_02_1.uasset
Content/RecordShop/Interaction/Actors/BP_RecordShelf.uasset
Content/RecordShop/Interaction/Actors/BP_Turntable.uasset
Content/RecordShop/UI/Prologue/WBP_Prologue.uasset
Docs/Architecture/DaySystemCustomerQueue.md
Docs/Architecture/DaySystemCustomerQueueReport.md
Docs/Architecture/PrologueTutorial.md
Docs/Architecture/PrologueTutorialReport.md
Scripts/Unreal/audit_prologue_context.py
Scripts/Unreal/cook_mvp.py
Scripts/Unreal/create_day_schedule.py
Scripts/Unreal/day_graph_helpers.py
Scripts/Unreal/install_day_system.py
Scripts/Unreal/install_prologue_tutorial.py
Scripts/Unreal/prologue_validation_support.py
Scripts/Unreal/run_day_gate.py
Scripts/Unreal/run_prologue_gate.py
Scripts/Unreal/validate_day_audio.py
Scripts/Unreal/validate_day_contract.py
Scripts/Unreal/validate_day_editor.py
Scripts/Unreal/validate_day_schedule.py
Scripts/Unreal/validate_day_week.py
Scripts/Unreal/validate_mvp_cycle.py
Scripts/Unreal/validate_mvp_dependencies.py
Scripts/Unreal/validate_mvp_regressions.py
Scripts/Unreal/validate_prologue_contract.py
Scripts/Unreal/validate_prologue_guards.py
```

7. **Day 1~7 live simulation**

   | Day | 실제 완료 순서 | 결과 |
   | --- | --- | --- |
   | 1 | A1 → E1 | PASS |
   | 2 | B1 → C1 | PASS |
   | 3 | A2 → F1 → D1 | PASS |
   | 4 | B2 → C2 | PASS |
   | 5 | A3 → G1 | PASS |
   | 6 | B3 → D2 → H1 | PASS |
   | 7 | TEMP_D7_01 → TEMP_D7_02 → FinalStoryEvent | PASS |

   - 실제 Tutorial 1회 + queue 16회의 production cycle을 연속 실행했다. 각 cycle은 실제 entry / dialogue UI / shelf / selection / cover / record / RPM / tonearm / audio / Result / navigation exit를 사용했다.
   - 접근 위치와 입력은 automation fixture다. Day, index, exit 완료 상태를 테스트가 직접 설정하지 않았다.
   - Day 시작 / 종료 event는 각각 [1,2,3,4,5,6,7], FinalStoryEvent는 1회. 각 활성 시점 Customer actor 1명, 최종 0명.
   - 중복 spawn / 조기 exit / 조기 Day End / 반복 transition 호출을 거부했다. 각 방문은 서로 다른 spawn actor였다.
   - evidence: `Saved/MVPCompletion/20261109T060758Z-day-full-week.json` 및 `-process.json`.

8. **A / B / C / D 반복 방문**
   - A = Day 1 / 3 / 5, VisitNumber [1,2,3].
   - B = Day 2 / 4 / 6, VisitNumber [1,2,3].
   - C = Day 2 / 4, VisitNumber [1,2].
   - D = Day 3 / 6, VisitNumber [1,2].
   - 각 실제 pawn의 CustomerProfile.CustomerID가 해당 stable ID와 일치함을 검증했다. Recommendation History는 저장하지 않았다.

9. **기존 RS001 / RS002 / RS003 regression**
   - 실제 native UI / E interaction / camera / cursor / focus / 이동 복귀 경로에서 각각 score 3 / 2 / 0 PASS.
   - SelectedRecord와 실제 Turntable audio identity를 검사했다. RPM 33 / 45 / 78 경로를 각각 사용했다.
   - Listening 10초 + 기존 arm return 후 Result. RS001 측정 11.131초. Result Continue 뒤 Store BGM과 Day 1 A1 단일 spawn을 확인했다.
   - RS001 evidence: `20261109T060435Z-day-natural-rs001-process.json`; RS002 / RS003은 gate report의 process 경로 참조.

10. **Prologue / Tutorial regression 및 공통 검증**
    - New Game → Prologue 3개 presentation → Explore 이동 → Tutorial 고객 → 기존 전체 cycle → TutorialComplete → Day 1 A1 PASS.
    - Prologue 중 일반 고객 없음, Tutorial/Day queue 중복 없음. Tutorial hint가 정상 해제된다.
    - fresh editor contract: dependency 303 packages, Blueprint 25개 compile 성공, missing / redirector / compile failure 0.
    - Production default map launch PASS.
    - Windows bounded loose Cook PASS: map, Result, Prologue, Week, Day 7개, Visit 16개 포함; exit 0 / cook errors 0.
    - Cook은 SkipSaveAssetRegistry smoke다. packaged executable / staging 검증을 의미하지 않는다.
    - Editor 시작의 기존 engine smoke error 15개는 정확한 알려진 패턴으로 분리한다. gameplay unexpected error는 0이며 전체 Editor log가 무오류라는 주장은 하지 않는다.
    - 최종 audio / isolated 결과와 aggregate evidence는 아래 Final verification에 기록한다.

11. **알려진 제한**
    - 임시 고객은 모두 기존 C01의 mesh / profile / dialogue를 사용한다. stable identity와 visit data만 분리되어 있다.
    - CustomerData row selector 및 StoryEventID의 실제 콘텐츠 실행은 후속 phase 범위다. 현재 방문 완료 payload에서 조회할 수 있다.
    - malformed / empty Day 데이터는 editor contract에서 먼저 검출해야 한다. runtime이 빈 Day를 자동으로 건너뛰지는 않는다.
    - 자동 중복 검사는 순차적인 중복 / 조기 호출과 실제 tutorial handoff를 포함한다. 임의의 외부 dispatcher consumer가 동기적으로 재진입하는 모든 경우를 검증했다고 주장하지 않는다.
    - cross-map persistence, Save/Continue, Recommendation History, Relationship, 경제 시스템, 실제 Ending은 구현하지 않았다.
    - 이전 Prologue 보고서의 선택적 immersive / 측면 접근 관련 육안 제한은 별도 항목이다. 이번 natural E2E는 일반 창 / front 접근 기준이다.

12. **MANUAL REVIEW**
    - Day header의 3초 가독성, Day End 0.75초 간격, FinalStoryEvent TBD 표시.
    - Store BGM 음량 / fade 및 10초 감상 pacing을 실제 스피커로 청취.
    - camera blend / collision station의 편안함, 일반 마우스와 gamepad focus 조작.
    - 실제 배포용 packaged build에서 UI / 입력 / audio 확인.
    - 자동 screenshot의 DAY 1 안내는 기존 Korean 스타일과 비차단 presentation으로 확인했다. 최종 UI art polish는 수행하지 않았다.

13. **다음 Recommendation History Phase**
    - 최종 Gate PASS를 전제로 진입 가능하다. stable CustomerID + VisitNumber와 OnCustomerVisitCompleted(Visit)가 다음 단계 연결 지점이다.
    - 같은 ID의 기록을 어떤 저장 authority와 데이터 형식에 둘지 다음 phase에서 결정한다. 이번 구현은 history / story로 진행하지 않고 멈춘다.

14. **추천 commit 단위 / message**
    - Production assets + seed schedule + 재현 installer를 함께: `feat: add seven-day production customer queue`.
    - regression automation / 보고서: `test: verify day progression and customer cycle regressions`.
    - BP_GameFlowManager binary에는 Prologue 선행 복구와 Day 변경이 함께 들어 있다. binary를 텍스트처럼 부분 staging하지 않는다.
    - 실제 staging / commit / push는 수행하지 않았다.

## Final verification

- Aggregate: `Saved/MVPCompletion/20261109T063354Z-day-gate.json`: complete=true, pass=true, **9/9 groups PASS**.
- This aggregate references each original process report; successful production tests were not rerun after documentation-only edits.
- Editor/data/dependency: `20261109T060123Z-day-editor-green-process.json`.
- Full live week: `20261109T060758Z-day-full-week-process.json`.
- Natural RS001: `20261109T060435Z-day-natural-rs001-process.json`.
- Natural RS002: `20261109T062003Z-day-natural-rs002-process.json`.
- Natural RS003: `20261109T062144Z-day-natural-rs003-process.json`.
- Isolated backend regressions: `20261109T063053Z-day-isolated-process.json`.
- Real Store BGM natural loop/fade: `20261109T062832Z-day-audio-process.json`.
- Startup: original process path is retained in aggregate.
- Cook: `20261109T062734Z-cook-final-process.json`.
- Initial isolated natural-LP completion and BGM-loop checks timed out in `20261109T062002Z-day-gate.json`. Audio buffer-starvation messages coincided with those runs. These failed reports remain; no production change was made to obtain the passing reruns. Host timing remains a diagnostic limitation; audible quality requires MANUAL REVIEW.
- Changed Python files parse successfully; `git diff --check` passed (line-ending advisory only). Final branch and HEAD equal starting values. Worktree changes remain unstaged.

