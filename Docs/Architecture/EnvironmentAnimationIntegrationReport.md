# Environment + Customer Animation Production Integration

## 1. Git 기준

- 작업 브랜치는 `feature/pr-test`다. 시작 시 로컬 `develop`, `origin/develop`, 원격 `refs/heads/develop`, 작업 브랜치 HEAD가 모두 `d7d275113223722dd0e389157cab24f1f9b3ceb9`였다.
- PR #19 병합 커밋은 `ee2ed55`, PR #20 병합 커밋은 `d7d2751`이다. 두 병합의 변경 목록과 로컬 Production 에셋을 조사했다.
- 시작 시 추적 파일 변경은 없었다. Git이 `ArtSource/Audio/Music/recordshop-expansion-fiqbw4uv/`의 미추적 파일을 열 수 없다고 경고했다. 해당 디렉터리는 작업 대상에서 제외했다.

## 2. 재사용 에셋

| PR | Production에서 사용한 에셋 |
| --- | --- |
| #19 | `BP_Customer`, `BP_Customer01`, `SKEL_C01`, `AM_ListeningToMusic`, `AM_HappyHandGesture`, `AM_ThoughtfulHeadNod`, `AM_Angry`와 연결된 시퀀스 |
| #20 | `L_RecordShop_Greybox_Exterior`, `L_RecordShop_Light_Morning`, `L_RecordShop_Light_Rain`, `L_RecordShop_Light_Sunset`, `L_RecordShop_Light_Closing`, `Art/Environment/Exterior/Materials`의 기존 머티리얼 |

PR #20의 원안과 `build_shop_exterior.py`, `build_day_lighting_presets.py`, `preview_day_lighting.py`를 읽고 `L_Env_ExteriorLighting_Test`를 메인 맵과 비교했다. 테스트 맵에서 검토한 서브레벨을 메인 맵에 등록했다. [PR #20 환경 원안](EnvironmentExteriorDayLighting.md)

## 3. 수정한 Production 에셋

| 패키지 | 변경 |
| --- | --- |
| `/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox` | 외부와 조명 서브레벨 등록, 겹치는 앞벽과 보조 가벽 제거, 기존 전역 조명 정리, 네 실내 조명에 런타임 식별 태그 추가 |
| `/Game/RecordShop/Core/Flow/BP_GameFlowManager` | 기존 `BeginDay`와 `BeginEnding`에 조명 전환 연결, 감상 시작·종료와 결과 확정에 고객 애니메이션 연결 |

Unreal 5.8 Editor Python의 레벨 및 Blueprint Graph Editor API로 두 패키지를 저장했다. 외부·조명 서브레벨과 고객 Blueprint는 PR에서 제공한 패키지를 사용한다.

## 4. 메인 맵 외부 환경

- `L_RecordShop_Greybox_Exterior`는 `LevelStreamingAlwaysLoaded`다. 쇼윈도, 유리문, 거리, 맞은편 건물, 간판이 이 레벨에 있다.
- 메인 맵에서 `GB_Wall_Front_L`, `GB_Wall_Front_R`, `Shop_Vestibule`을 제거했다. 안쪽 문틀과 문 상부는 유지했다. 유리문과 쇼윈도는 Pawn 및 Camera 채널을 차단한다.
- Production의 고객 Spawn, Entry, Exit 마커는 각각 Y `-490`, `-390`, `-440`이다. 문은 Y `-610`에 닫혀 있다. 고객 입장과 퇴장은 기존 실내 마커를 기준으로 진행된다. Target Point, NavMesh, Player Start, 대화·결과 카메라는 기존 Production 맵의 액터를 사용한다.
- 기준 맵과 최종 맵의 기존 Static Mesh 충돌 사용 여부, Object Type, 채널별 응답을 비교했다. Editor 저장 과정에서 턴테이블 RPM 노브와 표시 장식에 다시 활성화된 충돌은 원래의 `No Collision`으로 복구했다.
- `TEST_DirectionalLight`, `TEST_SkyLight`를 제거했다. 스카이 대기는 메인 맵의 `Shop_SkyAtmosphere`가 담당하고, Directional Light와 SkyLight는 현재 조명 서브레벨이 담당한다.

## 5. Day 조명

| 시점 | 프리셋 |
| --- | --- |
| 최초 맵 로드, Tutorial, Day 1·2·6 | Morning |
| Day 3·5 | Rain |
| Day 4·7 | Sunset |
| Ending | Closing |

네 조명 서브레벨은 `LevelStreamingDynamic`으로 등록했다. 처음에는 Morning만 로드하고 표시한다. `BeginDay`의 기존 유효성 검사를 통과해 Day가 확정되면 `ApplyDayLighting(DayNumber)`를 실행한다. `ApplyShopLightingPreset`이 네 레벨의 로드·표시 상태를 모두 제출한 뒤 `FlushLevelStreaming`을 호출한다. 전환은 기존 Day UI 설정과 `OnDayStarted` 사이에서 동기적으로 끝난다. Title과 New Game은 기존 레벨 재로드에서 Morning 기본값으로 돌아간다.

## 6. Ending Closing 조명

`BeginEnding`의 기존 `FinalStoryEvent` 및 마지막 방문 완료 검사를 통과한 뒤 Closing을 적용한다. `ShopAreaLighting` 태그가 붙은 `Shop_AreaLight00/01/10/11`의 밝기는 일반 프리셋에서 `950`, Closing에서 `200`이다. 팻말은 선택한 레벨의 기존 `OPEN` 또는 `CLOSED` 텍스트를 표시한다. 마지막 LP의 BGM과 Credits, Title 전환은 기존 GameFlow 경로에서 관리한다.

## 7. Customer Animation Hook

| GameFlow 지점 | `ActiveCustomer` 호출 |
| --- | --- |
| `StartListeningWindow`의 기존 10초 타이머 시작 | 유효한 고객에 `StartCustomerListening()` |
| `EndListeningWindow`의 Listening 상태 검사 통과 직후 | `StopCustomerListening()` 후 기존 Tonearm Return |
| `HandleTurntableCompleted`의 타이머 정리 | 조기 결과 경로에서도 `StopCustomerListening()` |
| `HandleTurntableCompleted`의 Raw 점수 표시 직후 | `PlayCustomerReaction(RawScoreAvailable, ClassifyRecommendationScore(RawRecommendationScore))` |
| 결과 Continue 후 Customer 퇴장 | `BP_Customer.ResultFinished`의 기존 `CleanupCustomerAnimations()` 후 AI 이동 |

`ResultStartedForCustomer`가 Result 경로를 한 번만 실행한다. 고객의 `LastCustomerReaction`도 동일 반응을 중복 차단한다. `ScoreAvailable`은 bool, 반응 구분은 `BEST`, `GOOD`, `POOR` Name 값이다. Tutorial과 Day 1–7 모두 동일한 GameFlow 진입점을 사용한다. Talking과 locomotion은 기존 Customer/AnimBP 경로를 사용한다.

## 8. Blueprint, Map, Windows 검증

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| Blueprint Compile 및 메인 맵 로드 | PASS | 새 Editor 세션에서 `BP_GameFlowManager`, `BP_Customer`, `BP_Customer01` 컴파일. 메인 맵의 서브레벨 5개와 Blueprint 연결 확인 |
| Dependency / Redirector | PASS | 메인 맵과 기본 GameMode에서 374개 패키지 순회, Blueprint 계열 30개 컴파일. Missing, Redirector, Compile Fail 각각 0개. 서브레벨 5개와 고객 Montage 4개 의존성 확인 |
| 기존 스크립트의 내러티브 해시 검사 | FAIL | 이전 `narrative_reference_baseline.json`의 `BP_Customer01.uasset` 해시가 PR #19 병합분과 다르다. 현재 파일은 HEAD의 LFS 해시와 일치한다 |
| 네 프리셋 Rendered PIE | PASS | Production 맵에서 프리셋별 안팎 1280×720 캡처 8장. 해당 프리셋만 로드·표시되고 외부 서브레벨이 유지됨 |
| Windows Cook | PASS | UAT의 Cook 종료 코드 0, 762개 패키지, 오류 0건, 경고 12건. Cook 산출물에서 메인 맵, 외부 레벨, 네 조명 레벨과 네 고객 Montage 확인 |
| Windows Stage / Package / Archive | PASS | 최종 Win64 Development UAT 종료 코드 `0`. Archive에 `RecordShop.exe`와 NanumGothic OFL 고지 포함. Stage manifest에서 메인 맵과 서브레벨 5개 확인 |
| Windows 패키지 Map Launch | PASS | 최종 아카이브의 실행 파일을 D3D12로 실행해 메인 맵, 외부 레벨, 초기 Morning의 로드 완료를 로그로 확인. 테스트가 관측 후 실행을 종료 |

Cook 경고에는 PR #19 자산의 기존 `empty engine version` 메시지가 있다. 호스트 테스트 `test_*.py` 20개도 통과했다.
처음 설치된 엔진으로 Stage를 실행할 때 `StagedBuild_RecordShop.ini` 쓰기 권한에 막혔다. 프로젝트 내부 임시 엔진에서 만든 아카이브도 엔진 설정이 잘못된 상대경로로 들어가 부팅에 실패했다. 프로젝트 외부의 쓰기 가능한 임시 경로에 UAT 환경을 구성해 다시 Cook하고 패키징했다. 최종 Stage manifest의 엔진 설정 경로는 `Engine/Config`이며 프로젝트 설정 파일과 설치된 엔진은 수정하지 않았다.

## 9. 17 Cycle 회귀 및 Gate

Rendered PIE에서 Production Title과 UI를 사용한다. 테스트에서 레코드 선반과 턴테이블 접근 위치를 배치하고, 고객 입장, 대화, 감상 10초, 결과, AI 퇴장은 런타임 흐름으로 진행한다.

| Gate | 결과 | 확인한 내용 |
| --- | --- | --- |
| A. Environment | PASS | Production 맵에서 외부 환경과 네 조명 프리셋 표시. 기존 거리와 쇼윈도를 캡처로 확인. Player capsule sweep은 매장 안 접근 구간을 통과하고 유리문 앞 Y `-572.84`에서 정지. 유리문·쇼윈도 Camera 채널 차단, NavMesh 기반 고객 입장과 퇴장 확인 |
| B. Day System | PASS | Day 1–7의 프리셋은 Morning, Morning, Rain, Sunset, Rain, Morning, Sunset 순서. 매번 해당 프리셋만 로드·표시되고 외부 레벨이 유지됨. New Game 직후와 새 Tutorial 후 Day 1에서 Morning 확인 |
| C. Ending | PASS | Day 7 마지막 고객 퇴장 후 `FinalStoryEvent` 1회, Closing만 표시, RectLight 4개 `200`, `CLOSED` 팻말 확인. Ending A와 Credits 9페이지에서 마지막 LP `RS001`의 BGM 유지. Title에서 오디오 정리와 New Game 재진입 확인 |
| D. Customer Animation | PASS | Tutorial 포함 17회 감상 및 결과. BEST 14회, GOOD 2회, POOR 1회. Talking, 9초 이후까지의 Listening 재생 지속, Result 전 감상 정리, 중복 Result 차단, 퇴장 Montage 정리와 다음 고객 초기 상태 확인 |
| E. 전체 회귀 | PASS | Tutorial 1회 + Day 1–7 고객 16회 = 17 Cycle, History 16건, 고객 A–J, RS001–RS006 실제 사용. 기존 LP Audio Handoff와 Title/New Game Reset 통과. 새 게임의 별도 Tutorial 후에도 Day 1의 A로 진입하며 History, UI, 오디오 누출 없음 |

기존 타이머는 10초다. 톤암 복귀를 포함해 테스트가 측정한 감상 시작부터 결과 UI까지의 구간은 `11.108–11.177초`였다. 최종 PIE 프로세스는 종료 코드 `0`과 예상 밖 런타임 오류 `0건`으로 마쳤다.

## 10. 자동화 및 수동 확인

- 자동 캡처 8장을 검토해 매장 안에서 쇼윈도 너머 거리와 맞은편 건물이 보이고, 바깥에서 간판과 유리문이 표시되는 것을 확인했다. Closing에서 매장 조명이 어두워지고 팻말이 `CLOSED`로 바뀐다.
- 별도 Rendered PIE에서 BEST·GOOD·POOR Montage가 자연 종료하는지 확인했다. 같은 결과를 다시 호출하거나 점수 없는 결과를 전달하면 재생하지 않았다. 각 Montage와 시퀀스는 `SKEL_C01`을 사용했다. 세 반응에서 캡슐 이동과 종료 후 Root의 평면 이동은 각각 `0.0 cm`로 측정됐다.
- 검증용 카메라, 고객과 관측 Blueprint는 테스트 세션에만 사용했다.

## 11. 남은 최종 폴리싱

- 실제 조작으로 쇼윈도·문 앞까지 이동하고 카메라가 충돌할 때의 구도와 움직임을 확인한다.
- 실제 Day 전환 구간의 노출 적응과 프레임 지연, 각 고객 반응의 발 위치와 블렌드 구도를 눈으로 확인한다.
- 패키지 실행 파일에서 New Game부터 Credits까지 직접 플레이해 조명 전환과 오디오 믹스를 확인한다. 전체 진행 자동화는 Rendered PIE에서 실행했고, 패키지 실행은 부팅과 초기 레벨 로드까지 검증했다.

## 검증 근거

- [최종 17 Cycle 판정](../../Saved/MVPCompletion/20261118T054859Z-env-animation-production-week-process.json)과 [상세 이벤트·History·조명 상태](../../Saved/MVPCompletion/20261118T054859Z-env-animation-production-week.json)
- [의존성 및 컴파일 판정](../../Saved/MVPCompletion/20261118T053508Z-env-animation-dependency-closure-process.json), [Player 충돌 판정](../../Saved/MVPCompletion/20261118T055435Z-env-animation-player-collision.json), [렌더 캡처 8장 요약](../../Saved/EnvironmentAnimationIntegration/lighting-contact-sheet.jpg)
- [최종 Windows UAT 로그](../../Saved/MVPCompletion/20261118T055952Z-ending-package/stdout.txt), [패키지 초기 레벨 로드](../../Saved/EnvironmentAnimationIntegration/packaged-final-streaming.json), [Windows 아카이브](../../Saved/MVPCompletion/20261118T055952Z-ending-package/Archive/Windows)

`feature/pr-test` 작업 트리에 Production 패키지 2개와 이 보고서를 남겼다. Git staging, commit, push는 수행하지 않았다.


## 12. Narrative Baseline Hash Regression Fix Gate

**PASS.** 8절의 내러티브 해시 실패는 PR #19 병합 이전의 `BP_Customer01` SHA를 공유 Narrative 기준으로 사용하면서 발생했다. 기존 검사로 이 실패를 재현했다. Production 대사, 추천, History 및 고객 라이프사이클에서는 회귀가 발견되지 않았다.

| 에셋 | PR #19 병합 전 SHA 접두부 | PR #19 병합본 및 현재 Production SHA 접두부 |
| --- | --- | --- |
| `BP_Customer01` | `8a3048d31d10` | `55edfcc6a0bc` |
| `BP_Customer` | `264e9ddfc301` | `dfc1bac708cc` |
| `SKEL_C01` | `d7499bb2ca0c` | `5cf0e748dd42` |

병합 커밋 `ee2ed55`의 Git LFS 객체와 현재 파일의 SHA-256을 대조했다. 별도 Editor 세션에서 병합 전후 에셋을 비교했다.

- `BP_Customer01`의 Talking 함수는 공용 Animation API를 호출하며 기존 Talking Montage를 재사용한다. `CustomerProfile`, AI Controller 설정, 이동·캡슐 설정, 메시와 AnimBP 및 오프셋, 메시 본 이름 66개가 일치했다. Production의 Talking·Listening·BEST·GOOD·POOR Montage와 소스 시퀀스가 모두 `SKEL_C01`을 사용했다.
- `BP_Customer`의 입장, 착석, 대화 준비, 퇴장 이벤트 및 AI 이동 노드는 유지됐다. `ResultFinished`와 기존 퇴장 이동 사이에 `CleanupCustomerAnimations`가 추가됐다.
- A1 원본 DataTable, 추천·방문·내러티브 데이터, 결과 위젯을 포함한 75개 패키지는 PR #19 이전·HEAD·현재 Production의 바이트 해시가 일치했다. 이번 작업 전후에는 이 패키지들과 고객 에셋 3개, 통합 GameFlow 및 메인 맵을 합친 80개 패키지의 SHA가 일치했다.

공유 `narrative_reference_baseline.json`에서 `BP_Customer01.uasset` 항목 하나를 승인된 SHA-256 `55edfcc6a0bc55600d48c4482d44382cc2f6af9b1a10f097ed7f450de5e60092`로 갱신했다. A1 원본 에셋, 원본 5행, 화면에 표시되는 5행, `ST_RecordData`, 기존 레코드의 의미 및 제목·아티스트 해시는 기존 값을 사용한다. 검사 로직과 단계별 과거 보존 스냅숏은 기존 값을 사용한다.

| 재검증 | 결과 | 근거 |
| --- | --- | --- |
| 공유 Narrative Editor Gate | PASS | A1 원본 5행 해시, 레코드 해시, A–J 방문 정의 및 Blueprint 의존성 검사 통과 |
| Dialogue Sequence | PASS | 출력 순서와 소스 분리, 잘못된 시퀀스의 기존 대화 복귀, 취소 후 고객 간 상태 누출 검사 통과 |
| Narrative Integration 및 History Guards | PASS | 방문별 프로필과 추천 점수, 재방문 메모리, 후보 LP, History 복사·중복·초기화 보호 검사 통과 |
| 17 Cycle Rendered PIE | PASS | A1 화면 표시 5행 해시 일치, A–J 대화 및 입장·퇴장, BEST 14회·GOOD 2회·POOR 1회, History 16건, Ending 및 새 게임의 Day 1 초기화. 프로세스 종료 코드 0, 예상 밖 런타임 오류 0건 |
| 호스트 테스트 | PASS | `test_*.py` 20개 통과 |

이번 재실행 범위는 공유 Narrative 검사와 Production PIE다. 단계별 이관용 보존 스냅숏과 Cook·Packaging은 별도 검증 범위다.

- [갱신 전 실패 재현](../../Saved/MVPCompletion/20261118T061523Z-narrative-hash-red.json)과 [PR #19 에셋 및 라이프사이클 비교](../../Saved/NarrativeBaselineHash/asset-audit.json)
- [Narrative Editor·Sequence·Integration·History Guard 재실행](../../Saved/MVPCompletion/20261118T061950Z-narrative-gate.json)
- [17 Cycle 재실행 판정](../../Saved/MVPCompletion/20261118T061702Z-narrative-hash-full-week-process.json)과 [상세 History 및 방문 결과](../../Saved/MVPCompletion/20261118T061702Z-narrative-hash-full-week.json)
