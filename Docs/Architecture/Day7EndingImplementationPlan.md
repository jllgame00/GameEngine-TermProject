# Day 7 / Ending Implementation Plan
> 2026-11-11 현재 구현 결과: [EndingProductionReport.md](EndingProductionReport.md)를 따른다. 사용자 지정 Ending 원문은 CONTENT_LOCK이며 Credits/Title/Day7 오디오 유예를 이번 Gate에 구현했다. 아래 I/J Gate의 미구현 표기와 예상 Asset 수는 이전 계획 이력이다. 실제 변경은 GFM/BPC 기존 2개와 Ending/Title 신규 Widget 2개, 라이선스 고지 및 tooling이다. 검증 결과·MANUAL_REVIEW·외부 권리 미확인은 각각 구분한다.

> 최신 Ending Production Gate: 사용자 확정 원문을 CONTENT_LOCK으로 적용한다. I/J Gate는 완료된 baseline이며 기존35개 미커밋 경로를 보존한다. 이번 구현은 신규 WBP_Ending/WBP_Title, 기존 GFM + BPC_Interaction의 최소 연결, Credits 고지와 검증 tooling이다. 기존 A~J/LP/Day1~6은 변경하지 않는다.
>
> 구현 결정: 같은 Shop map의 fresh OpenLevel을 Title 복귀와 New Game에 사용한다. URL option RecordShopNewGame / RecordShopTitle은 세션 진입만 구분하며 저장 상태를 운반하지 않는다. Cold launch는 Title, legacy automation만 명시적 -RecordShopProductionValidation으로 Prologue에 진입한다. Ending 상태는 기존 enum을 바꾸지 않는 GFM PresentationPhase(Name)이며 Leaving + 목적지로 종료 경로를 한 번 잠근다. Interaction은 이 phase를 읽는 기존 BPC 입구에서 차단한다.
>
> 실행 순서: (1) read-only audit/SHA snapshot/RED 계약 (2) UI와 canonical GFM Ending/Day7 audio/Title travel 구현 (3) Gate A~D 실제 runtime·720p/1080p·무음/중복/EOF 검증 (4) 전체 Narrative/17-cycle/History16·compile/map/cook·가능한 package 검증 (5) 독립 읽기 전용 review, 보호 SHA와 보고서. staging/commit/push 및 새 branch 없음. MANUAL_REVIEW와 CREDIT_VERIFICATION_REQUIRED는 자동 PASS로 바꾸지 않는다.


> 2026-11-10 I/J Production Gate 업데이트: I/J 본문·Result·퇴장 문구는 사용자 CONTENT_LOCK 승인 완료(J 첫 행은 ContentPlan 최종 문구). 아래 계획 중 I/J 데이터·Day7 참조·optional Result 표시만 이번 구현 범위다. Ending A/연락/답장/Credits/Title 방향은 APPROVED_DESIGN이다. FinalStoryEvent 내용, Ending UI/Title/Credits, Day7 오디오 유지 예외는 IMPLEMENTATION_REQUIRED로 남기며 이번에는 변경하지 않는다. MANUAL_REVIEW도 유지한다. 현재 구현/시험 결과는 Day7CustomerProductionReport.md를 따른다. 아래 “구현 미실행” 기록은 이전 설계 Gate baseline이다.
작성일: 2026-11-10  
상태: **CONTENT_LOCK (I/J) / IMPLEMENTATION_REQUIRED (Ending 후속) / MANUAL_REVIEW**

Spec: [Day7EndingContentPlan.md](Day7EndingContentPlan.md). I/J 본문·Result·퇴장 문구는 사용자 CONTENT_LOCK이다. Ending A·부모님 연락·답장·Credits/Title 방향은 APPROVED_DESIGN이며 후속 구현이 필요하다. Ending UI 세부 문구/출처 표기는 CONTENT_LOCK_REVIEW, 실청취/화면 검토는 MANUAL_REVIEW다.

기준 branch `feature/customer-narrative-content`, HEAD `6c848a34b7cc0e6a70c683c5e92dde04bff87854`. 실제 current data/graph/UI/import 근거: [read-only audit](../../Saved/MVPCompletion/20261110T104120Z-day7-content-lock-audit.json). 이는 이전 설계 Gate의 TEMP_D7_01/02 baseline이다. 이번 I/J 교체 결과는 Day7CustomerProductionReport.md에 기록한다. 새 Ending/Title는 아직 없다.

이전 설계 Gate는 Docs 두 파일만 변경했다. 이번 사용자 승인 구현은 I/J 데이터·Day07·optional Result 표시와 검증 tooling에 한정하며 Editor/Editor Python/검증된 automation만 사용한다. raw byte edit, staging/commit/push 금지.

## 1. 변경 대상 Asset와 source

예정 경로다. 신규 asset이 이미 존재한다고 표시하지 않는다.

| 구분 | Asset | 변경 이유 |
|---|---|---|
| 신규2 | /Game/RecordShop/Data/Narrative/DT_I_Dialogue, DT_J_Dialogue | 기존 /Game/DialogueData struct의 본문 각각4행 |
| 신규2 | /Game/RecordShop/Data/Narrative/DA_I1_Narrative, DA_J1_Narrative | ordered sequence/visit override/candidates/result FText |
| 신규2 | /Game/RecordShop/Data/Schedule/DA_Visit_I_1, DA_Visit_J_1 | I/J stable ID Visit1 Day7 order1/2 |
| 신규1 | /Game/RecordShop/UI/Ending/WBP_Ending | 시작/부모님 연락/답장/완료/Credits를 한 widget의 phases로 표시 |
| 신규1 | /Game/RecordShop/UI/Title/WBP_Title | 새 게임 진입 |
| 수정 | /Game/RecordShop/Data/Schedule/DA_Day07 | Visits를 신규 I/J 두 asset으로 교체 |
| 수정 | /Game/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition | empty-default ResultBestText/ResultGoodText/ResultPoorText/ExitText FText4개 |
| 수정 | /Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback | 기존 grade leaf에서 optional visit text/퇴장 반응 선택 |
| 수정 | /Game/RecordShop/Core/Flow/BP_GameFlowManager | presentation phase, Day7 audio 인계, Ending/Credits/Title/boot 연결 |
| 재사용 | /Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox | 새 Title map 없이 기존 공간 사용, map 변경은 원칙적으로 불필요 |
| 재사용 | DA_RecordCatalogue/DT_RecordCatalogue, RS001~006 SoundWave/Cover, UI NanumGothic, DialogueManager, Customer01 placeholder | metadata/tag/audio/새 customer mesh 수정 불필요 |
| 보존 | BP_Turntable, Day01~06/DA_TemporaryWeek, 기존 A~H/튜토리얼 대사/원본A1 | authority/콘텐츠 유지 |

신규8개, 최소 수정4개를 예상한다. 데이터 참조/compile 결과에 따라 의도적 변경 manifest를 다시 작성하며 이 숫자를 runtime 완료 주장으로 쓰지 않는다.

기존 DA_Visit_TEMP_D7_01_1/02_1은 곧바로 raw rename/delete하지 않는다. DA_Day07 참조에서 제외한 뒤 남은 production 참조를 검사한다. source 폴더에 historical TEMP asset이 남아 있어도 **scheduled visits=16**을 authority로 검증한다. cook closure에 구 TEMP가 잘못 포함되거나 새I/J가 빠지지 않는지 확인한다.

후속 source 작업도 필요하다: I/J authoring source/Editor importer, Ending FText/확정 Credits source, 3-card manifest의 I_1/J_1 항목, 새 validator. 기존 record_expansion.json을 바꿀 경우 records6 내용은 그대로 두고 candidate authoring만 확장한다. **이번에 JSON/DataTable row/source script를 생성하지 않는다.**

## 2. 기존 authority와 연결점

| 책임 | 유지할 authority | 새 연결 |
|---|---|---|
| Day/Queue | 기존 GFM + DA_TemporaryWeek/DA_Day07 | 마지막 두 Visit 참조만 변경 |
| 선택 LP | RecordSelect → Shelf.RecordSelected → GFM.HandleRecordSelected → TT.SetRecord | 변경하지 않음 |
| ID resolve | Shared Catalogue.ResolvePlayableRecord | I/J 후보와 Ending audio 검증도 동일 사용 |
| Score/Result | Mood/Genre/Theme 각1, 기존 3/2/0~1 grade branch | 새 문구만 선택, 재계산 authority 금지 |
| History | GFM.CommitRecommendationHistory, ID+Visit idempotence | I/J 각각1건. Ending/Credits는 저장 없음 |
| Dialogue | GFM.ConfigureActiveNarrative → DM explicit sequence | I_V1/J_V1 ordered4행 |
| Store BGM | GFM 기존 ID/sound/request/ref와 자연 EOF loop | 마지막 날에 한해 Ending UI 진행이 수명 보유 |
| UI 진행 | GFM presentation phase 한 곳 | Title/Playing/EndingPending/EndingDialogue/EndingCompletion/Credits/ReturningToTitle/TitleLoading |

presentation phase는 기존 DayPhase/CurrentState를 대체하지 않는 작은 modal 진행 상태다. 새 AudioManager/HistoryManager/Ending 점수/지속 GameInstance authority를 만들지 않는다. instance state의 초기값은 Title이며 New Game에서 Playing으로 들어간다.

## 3. I/J Dialogue 및 Result 작업

### 데이터 투입 순서

1. 원문 검토 후 namespace CustomerI/CustomerJ와 안정된 row/field key를 가진 FText를 authoring한다.
2. DT_I/J에 본문4행만 작성한다. DialogueID/Name은 I1_Current_01~04, J1_Current_01~04. Speaker와 Text는 콘텐츠 문서 그대로다.
3. Mood=Quiet, MusicPreference=Electronic/Jazz. IsEndNode는 04만 true. 기존 DialogueData에 Theme 열을 발명하지 않는다.
4. Narrative: I_V1/J_V1, SourceTable=각DT, OrderedRows=01→04. 모든 memory intro/outro와 MemoryVisitNumbers는 비운다. override는 I Quiet/Electronic/Adventurous, J Quiet/Jazz/Traditional.
5. Candidate order: I [RS003,RS001,RS004] →2/1/3; J [RS002,RS001,RS003] →2/3/0.
6. 신규 Visit을 Day7 order1/2에 연결하고 CustomerID I/J, VisitNumber1을 사용한다. 기존 BP_Customer01 class, IsPlaceholderContent=true(appearance), StoryEventID=None을 따른다. 미사용 CustomerData row handle은 비워 두고 Narrative를 연결한다. Ending은 Week의 최종 hook이다. class default ID/profile을 영구 변경하지 않는다.
7. 기존 customer presentation을 재사용하며 appearance=PLACEHOLDER를 기록한다. age30/20이 3D 모델로 완성됐다고 주장하지 않는다.
8. 원문 검토가 끝나고 실제 검증 단계에 들어갈 때만 기존 runtime ReviewStatus=READY 계약에 맞게 authoring한다.

### Result/퇴장 반응

현재 공통 중립 feedback만으로는 요청된 개인별 원문이 나오지 않는다. 기존 Narrative Definition에 empty-default FText4개를 추가하고 I/J 두 인스턴스만 값을 가진다. 다른 방문은 빈값 → 기존 legacy/neutral branch다.

WBP_Result의 기존 BEST/GOOD/POOR branch 안에서 read-only active narrative lookup으로 해당 원문을 선택한다. 필요하면 UI 내부 작은 helper 하나를 두되 별도 grade 계산이나 CustomerID별 hardcoded branch를 만들지 않는다. ExitText는 같은 panel의 반응 뒤에 빈 줄로 붙인다. Continue 뒤 새 Dialogue sequence를 열지 않는다.

논리 ID I1_Result_BEST/GOOD/POOR/Exit, J1_Result_*는 FText key 계획이며 새 Dialogue row가 아니다. Result heading/raw score/Available/Continue/focus/한 번의 History commit을 그대로 유지한다.

변경 전후 A1 원본 hash, A~H 문구/기억/프로필과 기존 neutral 설명이 동일한지 확인한다. Narrative schema 변경은 명시적 package hash migration 대상으로 기록하고, 기존 protected hash 검사를 일반적으로 끄지 않는다.

## 4. FinalStoryEvent / Ending 작업

현재 경로는 마지막 고객 퇴장 → AfterCustomerCycle의 index 증가/ActiveVisit clear → EndCurrentDay → FinishDayTransition → OnFinalStoryEvent다. J Result가 나오자마자 시작하는 별도 route를 만들지 않는다.

1. Day7 마지막 완료가 승인되면 presentation phase=EndingPending으로 한 번 인계한다.
2. 기존 OnDayEnded와 .75초 FinishDayTransition, FinalStoryEventTriggered 1회 guard를 유지한다. BeginDay8은 호출하지 않는다.
3. hook 수신은 EndingPending에서만 Ending UI를 한 번 열 수 있다. 기존 HideDayPresentation으로 DAY/TBD panel을 내리고 새 WBP_Ending으로 focus를 옮긴다.
4. EndingDialogue 안의 시작→부모님 연락→답장을 순서대로 표시한다. 새 부모님 actor/보이스/채팅 입력은 없다.
5. 답장 Continue 뒤 EndingCompletion, “크레딧 보기” 뒤 Credits로 전환한다. Hook 발생 flag를 UI 완료 flag로 재해석하지 않는다.
6. 이미 열린 hook/중복 Continue는 진행을 중복 생성하지 않는다. text index를 한 번 갱신한 뒤 같은 입력 재수락을 막는다.
7. 시작 시점/scene는 기존 Shop/플레이어 시점이 기본이다. camera/fade를 채택해도 새 cinematic framework가 필요하지 않다.

기존 WBP_Prologue의 Continue는 AdvancePrologue용이다. 그 인스턴스나 binding을 Ending에 연결하지 않는다. 시각 구성/폰트/presentation 패턴만 재사용한다.

## 5. BGM Cleanup 변경 최소 범위

**Day1~6 및 Tutorial 보존:** EndCurrentDay→StopStoreBGM, BeginDay/ResetDayAudio, 다음 Listening 전 fade/Stop, 기존 TT audio 완료는 그대로다. BP_Turntable 변경은 필요하지 않다.

### Day7 마지막 완료 분기

기존 EndCurrentDay 완료 guard 뒤, CurrentDay가 마지막 scheduled day(현재7)이며 전체 queue가 끝났고 ActiveCustomer/QueueCycleInProgress가 없는 경우에만 EndingPending으로 들어간다. 이 분기에서만 StopStoreBGM 호출을 건너뛰고 기존 StoreBGMRef/ID/sound/request를 보유한다.

- J1 History의 RecordID, 현재 BGM ID, catalogue resolve sound가 일치해야 한다. History Score/Result는 읽어 Ending을 평가하지 않는다.
- 이미 playing이면 Play/FadeIn/Seek를 호출하지 않는다. UI phase 전환에서 playback position을 되감지 않는다.
- 자연 EOF는 기존 StoreBGMFinishedEvent→PlayCurrentStoreBGM이 같은 source로 반복한다. callback은 History/Result를 호출하지 않는다.
- EOF 직전/직후 ref가 바뀌는 window는 source/request를 기준으로 다룬다. 복구 시 기존 PlayCurrentStoreBGM의 IsPlaying guard로 동시 voice를 막는다.
- accepted Result를 요구하는 StartStoreBGM을 Ending 재생의 새 진입점으로 부르지 않는다.
- source/ID/audio가 누락되면 진단 후 무음으로 같은 Ending을 진행한다. 고정 RS001이나 점수별 음악 fallback은 없다.

### Credits → Title

1. “타이틀로” 수락 즉시 ReturningToTitle로 잠근다. 같은 click/keypress/hook은 무시한다.
2. 기다리기 전에 SpawnQueuedCustomer/EndListeningWindow/FinishDayTransition 등 pending gameplay timer를 취소하고 기존 Day/고객 UI를 내린다. Ending/Credits 버튼·외부 callback도 무효화한다. fade 표시용 widget을 유지하더라도 새 UI 진행은 수락하지 않는다. EndingPending 중 abort라도 .75초 Final timer가 DAY/TBD 화면을 다시 열지 못해야 한다.
3. 기존 StopStoreBGM을 호출한다. requested=false/ID·sound clear와 Finished unbind가 먼저여서 fade/Stop 도중 loop가 되살아나지 않는다.
4. 유효한 재생 ref와 양수 fade 시간이 있으면 기존 StoreBGMFadeOutDuration(.6초 기본값)을 기다린 뒤 FinishStoreBGMStop을 확정한다. 숫자를 여러 graph에 복제하지 않는다.
5. **ref/오디오가 없거나 이미 정지했거나 fade 시간이0이면 같은 Return finalizer로 즉시 합류한다.** 기존 StopStoreBGM의 invalid-ref branch는 FinishStoreBGMStop timer를 만들지 않으므로 그 timer의 발생만 기다리지 않는다. quiet degraded Ending도 Title로 정상 복귀한다.
6. finalizer는 아직 ReturningToTitle인지 확인하고 ref None/owned playing LP voice0을 확보한다. 즉시 TitleLoading으로 바꿔 한 번만 기존 Shop map을 OpenLevel한다. Return 전용 지연 callback도 정리해 이중 reload를 막는다.
7. 정상 abort/back도 이 중앙 cleanup을 사용한다. bPersistAcrossLevelTransition=false/auto-destroy를 유지하고 새 world에는 이전 component/record/UI를 전달하지 않는다.

오디오 인계는 같은 GFM 소유권의 용도 변화다. 마지막 날 cleanup을 무조건 삭제하거나 모든 Day transition을 skip하는 공통 flag를 만들지 않는다. 다음 세션의 Title/Prologue는 무음이 기본이다.

## 6. Credits / Title 연결

### Credits

확정 팀원6명/역할은 콘텐츠 문서10절을 그대로 사용한다. 문구는 콘텐츠 문서8절에 있다. 팀원 page → 음악/아트/외부 출처 → 필요한 법적 고지를 짧은 정적 pages로 구성하고 마지막에 “함께해 주셔서 고맙습니다.” / “타이틀로”를 둔다. static pages 수는 실제 license 분량에 따라 조정하되 크레딧을 읽기도 전에 자동 종료하지 않는다.

확인된 Nanum 고지/OFL 전문, Engine의 필요한 고지와 실제 포함 third-party notices를 대조한다. 현재 NonUFS의 RecordShop/Licenses stage 설정은 재사용하고 packaged 결과에서 파일/전문을 확인한다. CREDIT_VERIFICATION_REQUIRED를 출시 placeholder로 넣지 않는다. 미확정 권리 자료는 release sign-off 대상이지 가짜 작가/URL/license로 채울 칸이 아니다.

### Title / New Game

현재 전용 Title나 shipped New Game UI는 없다. 기존 GameDefaultMap은 Shop이고 BeginPlay가 BeginPrologue를 직접 호출한다.

- 최초 boot에서 GFM 참조 초기화/이벤트 bind/History 초기화는 유지한다. BeginPrologue 호출 위치만 Title presentation gate로 연결한다.
- WBP_Title 기본 focus=새 게임, UI-only/cursor visible. 단일 phase guard로 New Game을 한 번 수락하고 Title를 제거한 뒤 기존 BeginPrologue로 간다.
- Credits Return은 audio cleanup 뒤 같은 Shop map을 새로 열어 Title를 만든다. 새 MainMenu map/Level은 추가하지 않는다.
- Title 복귀에 ResetRecommendationHistory만 호출하는 in-place reset은 불충분하다. 새 world/GFM/actors를 사용해 Day/Queue/History/Tutorial/record/UI/timer를 함께 초기화한다.
- Title에는 Continue/SaveGame을 추가하지 않는다. 새 persistent state에 이전 History나 LP를 저장하지 않는다.
- Focus를 지연 적용할 경우 여전히 해당 Title/Ending phase일 때만 적용해 다음 UI의 focus를 빼앗지 않게 한다.

새 world Title의 초기 조건: Day0/초기 DayPhase, ActiveCustomer/Visit 없음, queue 미진행, History0, TutorialComplete=false/초기 PrologueStage, 선택 record/재생 없음, Result/Dialogue/pending sequence refs 없음. New Game 후에만 기존 Tutorial을 시작한다.

## 7. 회귀 테스트 계획

이번 Gate에서 실행하는 것은 data/graph read-only 감사와 문서/비변경 검증뿐이다. 아래는 **후속 구현 acceptance**다.

| 그룹 | 필수 검증 |
|---|---|
| I/J 데이터 | 본문4행/마지막 end flag, approved tags, explicit order, memory 없음, 표기/refs 유효 |
| 점수 | 6 LP 전체 I=1/1/2/3/1/1, J=3/2/0/1/1/1. 실제 DM score path와 grades. 원본 A=3/2/0 보존 |
| 후보/순서 | 각3 unique valid, 여러 fresh session의 authored order/버튼 index 동일 |
| Result | I/J grade별 원문/퇴장 text, 기존 grade/neutral/Available/focus 보존. 기존 A~H default empty fields fallback |
| Profile/sequence | I→J 및 다음 session leak 없음, 완료/취소 clear, 원본 A1 hash 보존 |
| History | scheduled16, I/J 각1, Tutorial/Ending/Credits 제외, duplicate Result/History callback idempotent, read-only query isolation |
| Audio 인계 | J가 RS001/2/3 각각 골라도 동일 source 유지, Result→Exit→Final→Dialogue→Completion→Credits 사이 불필요 restart 없음 |
| Voice/lifetime | UI 전환/중복 hook에서 한 active LP voice, EOF 직전 인계/긴 대기/여러 자연 loop, 오래된 callback, cleanup 후0 |
| Day | Day1~6 cleanup 기존 PASS. Day7만 Ending 소유로 유지, Day 재진입/8일차 금지, 마지막 hook1회 |
| Title | Return double click1회, fade 완료 또는 no-audio 즉시 완료 뒤 audio0/map reload1회; EndingPending abort 시 pending timer로 DAY/TBD가 다시 열리지 않음, Title에서 즉시 고객 spawn/Prologue auto 진행 없음 |
| New Game | Title→New Game1회, 새 Tutorial/Day0/History0/선택 없음. 두 번째 전체 session도 이전 기록/LP 없음 |
| 기존 Core | Tutorial/A1~3/B1~3/C1~2/D1~2/E~H, 6 LP, canonical SelectedRecord/TT/Listening, Camera/Input/Cursor/Focus |
| 비평가 Ending | All BEST/All POOR fixtures에서 같은 Ending/크레딧. 마지막 LP 누락은 진단·무음, 가짜 곡 없음 |
| 배포 | Blueprint compile, dependency/redirector/missing package, startup map, bounded Windows cook, packaged executable/UI/audio/notices |

기존 validate_day_week/validate_mvp_cycle/prologue_validation_support 등 entry fixture는 이제 “Title→New Game→기존 opening”으로 확장해야 한다. 기존 Day7의 “Final hook 시 BGM 없음” assertion은 승인된 새 계약에 따라 “Ending/Credits 동안 같은 LP, Title 전에0”으로 **Day7에만** 변경한다. 다른 날의 no-leak 검사를 완화하지 않는다.

기존 7일 validator가 TEMP identity를 기대하는 부분과 신규 I/J narrative를 아직 모르는 contract/matrix도 명시적으로 갱신한다. source asset 총개수와 실제 scheduled16을 혼동하지 않는다. 새 schema/GFM/Result 의도적 hash 변경은 좁은 migration으로 선언하고 과거 baseline/실패 로그를 덮거나 보호 검사를 제거하지 않는다.

자연 loop는 새 component를 만들 수 있고 AutoDestroy된 Python handle은 null이 될 수 있다. 검사에서는 live world component/path/source/ID와 실제 finish event를 관찰한다. 긴 interval의 여러 loop를 검증할 때는 매번 새 component도 observer에 연결해 단발 EOF 관찰만으로 모든 restart를 정당화하지 않는다.

## 8. 사용자 수동 검증과 완료 기준

**CONTENT_LOCK_REVIEW**
- I/J 본문·grade별 반응·퇴장 원문과 Ending 시작/부모님 연락/답장/완료/Credits/Title 문구를 검토한다.
- 개인별 Result 텍스트가 기존 style과 맞고 부모님 연락이 성적 총평처럼 들리지 않는지 확인한다.
- 제작 근거와 실제 저작자/권리자 표시를 혼동하지 않도록 Credits source 문구를 검토한다.

**MANUAL_REVIEW**
- 한국어 줄바꿈/가독성/4행 길이, 기존 placeholder 나이 표현 한계.
- RS001/2/3이 마지막일 때 분위기, 저음량 balance, 자연 loop 경계, Ending/크레딧 pacing/피로도.
- 실제 mouse/gamepad/keyboard focus, 빠른 연속 입력, 긴 대기, abort/Title 복귀, New Game 두 번째 session.
- packaged 화면/오디오와 license notice/전문, 외부 자료 검증 후 credit 누락 여부.

후속 완료 기준: 사용자 원문 검토를 마친 콘텐츠만 적용하고, 실제16방문과 단일 Ending/마지막LP/Title/NewGame 및 기존 Core regression이 PASS해야 한다. 외부 권리 미확정 항목은 출시 전 검증 목록에서 별도로 해결한다. 이번 문서 작업을 그 구현/출시 완료로 표시하지 않는다.
