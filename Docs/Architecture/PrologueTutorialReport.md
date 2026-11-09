# Prologue / Tutorial Production Gate 보고서

## 1. 시작 상태

- 작업 위치: `D:/univ/3-1/GameEngine/Termproject/RecordShop`
- Branch: `feature/prologue-tutorial`
- HEAD: `2ed3fa01b357f449cef00d87c2a452457761d7db`
- 시작 status: clean. 최종 변경은 작업 트리에 남겼으며 staging / commit / push하지 않았다.
- 에셋은 Unreal Editor Python / BlueprintGraphEditor / EditorAssetLibrary로만 수정했다.
  `.uasset` / `.umap` raw edit는 하지 않았다.

## 2. 기존 architecture 감사

| 항목 | 실제 Production 경로 / 소유권 |
| --- | --- |
| Map | `/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox`; map GameMode override 없음 |
| GameMode | 기존 `BP_ThirdPersonGameMode` |
| Player | 기존 `BP_ThirdPersonCharacter` + `BP_ThirdPersonPlayerController`; ShopOwner mesh / animation 유지 |
| Flow | 배치된 `BP_GameFlowManager` 하나가 고객 생성, 대화, 선택, 감상, Result, 퇴장을 조정 |
| Dialogue | 기존 `DialogueManager` component, `CustomerDialogue`의 C01_Quiet_01~05, `WBP_Dialogue` |
| Customer01 | 기존 BP_Customer01 생성 → 실제 navigation → Ready → 대화 / 대기 → Result → 실제 퇴장 |
| Selection | WBP_RecordSelect → BP_RecordShelf.RecordSelected → BP_GameFlowManager.HandleRecordSelected → BP_Turntable.SetRecord |
| Turntable | 기존 단계 / RPM / 동작 / 오디오 / tonearm return / completion 유지 |
| Result | 기존 WBP_Result_IntegrationFallback, raw score, Continue focus 유지 |
| Camera | Flow의 DialogueCamera / ResultCamera, Turntable의 ListeningCamera; 닫기에서 pawn 복귀 |
| Input | 기존 IA_Interact의 E, BPC_Interaction trace; 기존 modal close가 cursor / GameOnly / focus 복구 |
| Persistence | 설정된 custom GameInstance 및 SaveGame 에셋 없음. 이번 작업에서도 추가하지 않음 |
| Intro / Tutorial | 기존 전용 에셋 없음 |

시작 전 9개 Production Blueprint compile은 성공했다. 기존 Turntable comment의
missing NodeGuid 경고는 Editor PostLoad가 만든 GUID를 정상 resave해 해결했다.
최종 dependency / compile 검사에서는 해당 경고가 재발하지 않았다.

## 3. 선택한 architecture

기존 FlowManager에 작은 PrologueStage와 TutorialComplete / TutorialResultSubmitted,
OnTutorialCompleted를 추가했다. 새 manager, Day authority, Save authority는 없다.

새 WBP_Prologue는 기존 Result의 한국어 폰트 / 색 / 패널 스타일과 일반 버튼 연결을
재사용한다. 복사된 Result 전용 함수와 dispatcher는 제거했다. 같은 presentation의
별도 instance를 입력을 가로채지 않는 안내로 사용한다.

Opening modal만 UIOnly / Continue focus를 소유한다. 닫을 때 GameOnly, 숨긴 cursor,
viewport focus를 복구한다. 안내는 camera / input mode를 변경하지 않는다.
기존 modal이 열리면 안내를 숨기며, 완료 안내는 6초 뒤 widget과 polling timer를 해제한다.

## 4. 변경 파일

Production 에셋 4개:

- `Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset`
- `Content/RecordShop/Interaction/Actors/BP_RecordShelf.uasset`
- `Content/RecordShop/Interaction/Actors/BP_Turntable.uasset`
- 신규 `Content/RecordShop/UI/Prologue/WBP_Prologue.uasset`

Shelf / Turntable에는 시작 구간의 조기 상호작용 guard를 추가했다.
기존 dialogue, catalogue, pawn, camera, input mapping, map, audio content는 수정하지 않았다.

Editor 자동화 / 검증:

- 신규 `audit_prologue_context.py`, `install_prologue_tutorial.py`
- 신규 `prologue_validation_support.py`, `validate_prologue_contract.py`, `validate_prologue_guards.py`
- 신규 `run_prologue_gate.py`
- 수정 `validate_mvp_cycle.py`, `validate_mvp_regressions.py`, `validate_mvp_dependencies.py`, `cook_mvp.py`
- 문서 `Docs/Architecture/PrologueTutorial.md`, 본 보고서

## 5. 실제 Flow

New Game → 가게 / 부모님의 일주일 부재 / 7일간 맡을 책임 → 짧은 부모님 메모
→ 8초간 자유 Explore → 기존 Customer01 등장 / 입장 → 기존 Dialogue
→ 진열장 E → 기존 Record Selection → canonical SelectedRecord 전달
→ 턴테이블 E → 기존 Open Cover / Place Record / RPM / Tonearm / Play
→ 실제 LP 감상 / 자연 종료 / tonearm return → 기존 Result / Continue
→ 고객 자연 퇴장 → TutorialComplete / Explore.

기존 UI가 설명하는 대화 / 음반 선택 / 턴테이블 버튼 안내는 중복하지 않는다.
완료는 Result 제출과 고객 퇴장이 모두 끝나야 가능하며 새 고객은 생성하지 않는다.

## 6. 자동 검증 결과

일반 창 모드 기준 필수 Gate 9/9 PASS. 최종 집계:
`Saved/MVPCompletion/20261109T051918Z-prologue-gate.json`

| 검사 | 결과 |
| --- | --- |
| 새 시작 상태 / presentation / 함수 compile contract | PASS |
| 반복 Begin / Advance, 조기 완료, 조기 Shelf / Turntable guard | PASS |
| Production dependency closure | 276 packages, Blueprint 22개 compile PASS; missing / redirector / compile failure 0 |
| RS001 실제 native 입력 + audio 전체 cycle | PASS |
| RS002 실제 native 입력 + audio 전체 cycle | PASS |
| RS003 실제 native 입력 + audio 전체 cycle | PASS |
| 기존 isolated regression | 22/22 PASS |
| Production editor map startup | PASS |
| Windows loose Cook | PASS; map / Result / 신규 Prologue cooked package 확인, cook error 0 |

각 process는 exit 0, assertion complete/pass, gameplay log gate를 모두 확인했다.
기존 runner의 정확한 15줄 engine startup smoke 진단은 별도 분류된다.
이는 engine 전체 로그에 오류가 전혀 없다는 주장과 구분한다.

Focus 보완 후 contract / guard / dependency / RS001 전체 / Cook을 재검증했다. 동일한 선택·턴테이블·결과 로직의 RS002 / RS003 / isolated 결과는 이전 PASS 증거를 이월했다.

추가 확인: Python syntax, 기존 log classifier unit test 7개, text diff whitespace 검사 PASS.
Cook은 SkipSaveAssetRegistry를 사용하는 bounded smoke이며 packaged executable / staging은 미수행이다.

## 7. 기존 E2E regression / 증거

| Record | 접근 / 해상도 / RPM | 점수 | 최종 결과 |
| --- | --- | --- | --- |
| RS001 | 정면 / 일반 창 / 1280×720 / 33 | 3 | PASS |
| RS002 | 정면 / 1280×720 / 45 | 2 | PASS |
| RS003 | 우측 / 1920×1080 / 78 | 0 | PASS |

각 경로에서 authored dialogue, E trace, 선택 record / audio identity, 물리 조작,
자연 audio completion, Result focus / camera, 퇴장 중 미완료 상태, 퇴장 후 완료,
실제 이동 복구, 완료 후 LP 화면 재진입 / Escape, 안내 해제를 검사했다.

격리 검증기는 cached OwnerInteractionStation을 초기화하지 않던 fixture를 보완했다.
기존 BeginOwnerAlignment → StopOwnerPresentation → EvaluateOwnerContact를 호출하며,
station / readiness 값을 강제로 넣지 않는다. 이 검사는 자연 E2E와 구분한다.

최초 실행의 실패 기록도 유지했다:
`Saved/MVPCompletion/20261109T044756Z-prologue-gate.json`.
최종 집계의 previous_report 연결을 따라 이전 집계와 최초 실패 기록을 확인할 수 있다.

## 8. Known limitations

- 추가한 좌측 80cm 접근 검사는 고정 접촉 목표 위치 assertion에서 미통과했다.
  최종 RS002 필수 경로는 정면에서 재검증했다. 좌측 case를 PASS로 처리하지 않았으며,
  이번 작업에서 기존 alignment / reach / collision 로직은 변경하지 않았다.
  측면 물리 접근은 별도 확인이 필요하다.
- 몰입 화면의 캡처 포함 시작 검사는 focus 손실 기록이 있어 PASS로 처리하지 않았다. 캡처 없는 몰입 시작 / native 진행 / Explore 복귀는 지연 focus 보완 후 PASS다. 정규 전체 cycle 결과는 일반 창 기준이며, 몰입 전환 / 캡처 시 focus는 별도 검토가 필요하다.
- TutorialComplete는 현재 map / session 상태다. map 재시작은 New Game이며 cross-map /
  disk persistence는 다음 phase에서 결정해야 한다.
- 기존 Customer01의 다섯 줄 이야기를 그대로 사용한다. 추가 customer / story는 없다.
- Day System, queue, history, ending, packaged executable은 구현하지 않았다.

## 9. MANUAL REVIEW

에이전트가 720p / 1080p 캡처에서 Intro / 메모의 한국어와 단일 줄 버튼,
Explore 안내, 기존 LP 선택 화면, 완료 안내, Result 화면을 확인했다.
실시간 카메라 전환의 느낌, 8초 Explore 타이밍, 음량 / 음악 감상 품질,
마우스 / gamepad / packaged build 조작과 좌측 접근은 사람의 플레이 확인이 필요하다.
Native 자동화는 UI 키 입력을 합성하고 player의 접근 geometry를 배치한다.
전체 사람 플레이테스트를 대신하지 않는다.

몰입 화면에서 시작 focus 손실을 별도 재현했고, 활성 Prologue에만 0.1초 뒤 focus를 한 번 적용해 보완했다. 보완 후 세 페이지의 native 키 입력과 Explore 이동 복구 검사가 통과했다.

## 10. 다음 Day System phase 진입

현재 handoff는 TutorialComplete=true, CurrentState=Explore, ActiveCustomer=None,
Result UI 종료, pawn camera / cursor / 이동 입력 복구 상태다.
Day System은 TutorialComplete를 조회하거나 OnTutorialCompleted를 구독할 수 있다.
즉시 본편을 시작할 때 DismissTutorialHint로 남은 완료 안내를 정리할 수도 있다.

Day System architecture 작업은 진입 가능하다. 좌측 접근의 별도 검토 항목은 유지한다.
이번 구현은 이 Production Gate에서 멈추며 Day 1 customer를 enqueue하지 않는다.
