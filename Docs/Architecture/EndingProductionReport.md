# Ending Production Report

> 최신 재감사(2026-11-11): 기존 미커밋 구현을 보존해 새 17 Cycle/History16 완주, Ending 10사례, Quit, Blueprint/dependency, Windows Cook를 통과했다. 금회 1080p 재실행은 목표 viewport 확보 실패로 BLOCKED이며 동일 자산의 이전 1080p PASS와 구분한다. Package/직접 QA/외부 권리 승인은 여전히 미완료다. 금회 변경 경계와 새 증거는 14절을 따른다.

작성: 2026-11-11 (KST). **IMPLEMENTATION PASS / AUTOMATED REGRESSION PASS / WINDOWS PACKAGE BLOCKED / MANUAL_REVIEW / CREDIT_VERIFICATION_REQUIRED**. 패키징 권한과 외부 권리 확인을 포함한 출시 승인은 완료 상태가 아니다.

## 1. Git Baseline

Branch `feature/customer-narrative-content`, HEAD `6c848a34b7cc0e6a70c683c5e92dde04bff87854`. 시작에는 I/J Gate의 기존 미커밋 35개 경로가 있었다. [시작 status와 SHA768](../../Saved/MVPCompletion/ending-start-state.json)에 보존했다. 새 branch, staging/commit/push, PR merge, raw uasset/umap 편집을 하지 않는다. LFS와 임시 폴더 경고는 별도로 기록한다.

## 2. Production 변경 파일

기존 수정2: `Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset`, `Content/RecordShop/Interaction/Components/BPC_Interaction.uasset`.

신규2: `Content/RecordShop/UI/Ending/WBP_Ending.uasset`, `Content/RecordShop/UI/Title/WBP_Title.uasset`.

신규 고지: `Content/RecordShop/Licenses/NanumGothic_OFL_Full.txt`. 기존 고지는 보존하고 빠진 OFL 전문만 추가했다. 기존 NonUFS Licenses staging 설정을 사용하며 Config는 변경하지 않았다.

GFM의 기존 함수 graph46개와 나머지 기존 Content554개를 SHA/graph digest로 보호했다. Day1~6 Schedule·A~J data·6 LP·Turntable·DialogueManager·Map·기존 UI는 시작 스냅샷과 동일해야 한다. [정확한 migration 경계](../../Scripts/Unreal/ending_reference.json). 정확한 이번 Gate 증분 manifest와 기존 파일 보존 SHA는 [최종 evidence](../../Saved/MVPCompletion/ending-final-evidence.json)를 따른다. 기존 시작35개 변경은 이번 Gate 변경 목록과 분리한다.

## 3. FinalStoryEvent 연결

기존 `HandleCustomerExited` → `EndCurrentDay` → 0.75초 `FinishDayTransition` → 기존 `OnFinalStoryEvent` broadcast를 유지한다. 해당 canonical broadcast 바로 뒤에서 같은 GFM의 `BeginEnding(EventID)`를 호출한다. 새 Story Manager/추가 customer/history cycle은 없다.

`BeginEnding`은 마지막 Day, 실제 FinalStoryEventID/DayPhase/final flag, EndingPending, 빈 ActiveCustomer/ActiveVisit 및 QueueCycle 종료를 모두 요구한다. 시작 후 phase를 먼저 바꾸므로 반복 hook이 UI를 다시 만들지 않는다. Day8·추가 Spawn도 기존 최종 Day guard와 새 presentation guard가 차단한다.

## 4. Ending Dialogue/UI

원문은 [CONTENT_LOCK source](../../Scripts/Unreal/ending_content.json)이며 사용자 승인 표현을 수정하지 않았다.

- 시작: “마지막 손님이 가게를 나섰다. / 부모님에게서 짧은 연락이 왔다.”
- 부모님: “오늘이 마지막 날이네. / 일주일 동안 가게 맡아줘서 고마워. / 마감하면 편히 쉬렴.”
- 답장: “오늘 손님도 다 다녀가셨어요. / 이제 마감할게요.”
- 완료: “일주일의 운영을 마쳤습니다.”, 버튼 “크레딧 보기”.
- Credits 마지막: “함께해 주셔서 고맙습니다.”, 버튼 “타이틀로”.

기존 Prologue Widget의 presentation 구조를 복제한 최소 UMG2개다. Ending은 대사3면/완료1면/Credits5면이며 자동 대기 없이 버튼으로 진행한다. `FrontEndInputDelay=0.15`는 같은 프레임 중복 입력 방지용이다. NanumGothic/자동 줄바꿈/비율 Anchor로 작은 화면을 대응한다. 기존 Shop/pawn camera를 유지하며 새 cinematic/map/mesh/audio는 없다. History는 Ending 평가·분기·표시용으로 읽지 않는다.

## 5. Credits

확정 팀원6명과 사용자 지정 최신 역할(Camera)을 정확히 표시한다. 원본 RS001~006 audio와 RS004~006 cover의 로컬 provenance를 기록한다. NanumGothic NHN2010/OFL1.1 고지와 Unreal Engine 두 법적 고지를 넣었다. 공식 근거: [Unreal EULA §7](https://www.unrealengine.com/eula/unreal), [OFL 전문](https://openfontlicense.org/documents/OFL.txt), [네이버 폰트 라이선스](https://help.naver.com/service/30016/contents/18088?osType=PC).

Cigar_room, Fab Vintage Stereo, ShopOwner/Customer01 모델·외부 애니메이션의 완전한 제작자/배포처/적용 라이선스 증빙은 없다. 실제 namespace/import/dependency만 식별했으며 제작자·링크·권리를 만들어내지 않았다. Credits와 source manifest에 `CREDIT_VERIFICATION_REQUIRED`를 표시했다. **외부 권리 출시 승인은 BLOCKED/추가 증빙 필요**다. UI나 기술 테스트 PASS로 권리 검증을 대체하지 않는다.

## 6. Title / New Game

Cold launch는 Title. 새 게임/게임 종료를 표시한다. 기존 테스트 경로만 runner가 명시적 `-RecordShopProductionValidation`을 넣어 Prologue로 시작한다. 실제 Cold Title 테스트는 `--title`로 이 플래그를 제거한다.

Title 복귀와 New Game 모두 기존 Shop Map을 `OpenLevel(bAbsolute=true)`로 다시 연다. URL의 `RecordShopTitle=1` / `RecordShopNewGame=1`은 부트 목적지만 전달한다. Title option이 legacy test flag보다 우선한다. 새 World의 GFM/PC/pawn/TT/Queue/History/Tutorial/Ending/Timer/UI/Audio가 CDO에서 새로 생긴다. 최종 travel/quit 직전 valid Turntable의 Tick을 끄므로 PC가 먼저 사라지는 종료 프레임에서 EvaluateOwnerContact가 None을 읽지 않는다. 새 World TT의 Tick enabled도 검증한다. SaveGame/Continue나 파일 삭제는 없다. New Game은 기존 BeginPrologue → Tutorial → Day1을 사용한다.

## 7. Day7 Audio Lifecycle

Day1~6 `StopStoreBGM` 경로와 tuning은 유지한다. `EndCurrentDay`의 audio leaf만 `CompleteDayPresentationAudio`로 바꿔 마지막 Day에서 EndingPending을 만들고 기존 GFM audio component를 유지한다. Result 때의 동일 트랙 재시작/FadeIn0.5/Volume0.18 계약은 그대로다. Ending 시작 자체는 Play/재시작/새 component 생성을 하지 않는다. 자연 EOF는 기존 generic BGM loop가 처리한다.

Credits 종료 시 Leaving/destination을 먼저 잠그고 timer/UI/context를 정리한다. `IsPlaying && FadeOutDuration>0`를 Stop 전에 snapshot하고 기존 FadeOut0.6을 사용한다. 소리가 없거나 이미 정지/0초면 즉시 travel, 재생 중이면 기존 fade 시간 뒤 한 번만 FinishFrontEndTravel. 그 함수는 Traveling을 먼저 잠그고 FinishStoreBGMStop/Timer clear 후 OpenLevel 또는 QuitGame을 호출한다. 새 Ending AudioComponent/중복 record map은 없다.

## 8. Duplicate/Reset/Recovery Guard

기존 enum은 유지하고 GFM의 최소 `PresentationPhase(Name)`, `EndingStep`, destination, ready flag, Widget ref를 추가했다. UI callback은 current Widget Origin과 phase/ready를 검증한다. 같은 프레임의 두 번째 호출은 페이지를 건너뛰지 못한다. Leaving/Traveling/Closed에서는 다시 종료하지 않는다.

UIOnly/cursor/PC move-look ignore/pawn DisableInput과 기존 BPC_Interaction 입구의 canonical phase check로 플레이 입력을 차단한다. 처음/다음페이지 Continue에 production SetUserFocus를 적용한다. travel 때 FlowRef를 지운 뒤 Widget을 제거하고 authored GFM timer11종을 명시적으로 취소한다. EndPlay에서 demand/record/audio/timer를 즉시 정리한다. stale callback은 phase/invalid Origin으로 무효다. FinishDayTransition도 Playing 또는 EndingPending에서만 동작해 Leaving 이후 final hook을 새로 broadcast하지 못한다.

설치 스크립트는 one-shot migration이며 현재 Content가 감사 baseline과 다르면 수정 전에 거절한다. 독립 읽기 전용 리뷰에서 중대한 결함은 없었고, 이 재실행 경계를 보완했다.

## 9. 전체 17 Cycle / History16 Regression

**PASS — 전체 연속 플레이:** [20261110T160227Z narrative-week](../../Saved/MVPCompletion/20261110T160227Z-narrative-week.json). 첫 세션 Tutorial1+예정 고객16=17 Cycles, History16(Sequence1~16), DayStarted/Ended 각각1~7, FinalStoryEvent 정확히1회, Ending/Credits flow1회(동일 Widget9면), Ending 중 History16 불변, 6장 모두 실제 Listening. Cold Title → New Game → Prologue/Tutorial → 16 visits → 실제 Ending UI → Credits → Title → fresh New Game을 통과했다. 이어 새 세션의 Tutorial을 추가1회 실제 완료해 Day1 A/History0/TutorialComplete=true까지 확인했다. 이 재시작 Tutorial은 첫 세션17회와 별도 집계다. [최신 전체 aggregate](../../Saved/MVPCompletion/20261110T154617Z-customer-ij-gate.json)의 leaf30개도 모두 PASS다. I/J contract·matrix·실제 GOOD/POOR cycle, 기존 audio ownership,6LP/3 fresh candidate sessions, EFGH/CD/B/A, Core12개를 기존 실행 결과 재사용 없이 새 process로 수행했다. fullweek는 자연 navigation/UI/audio를 사용한다. 플레이어 접근 좌표와 unsaved observer는 fixture이며 day/queue/exit 강제 완료는 하지 않는다. 별도 Ending matrix는 명시적인 unsaved completed-Day7/accepted-Result fixture다.

## 10. Blueprint / Map / Cook

**PASS — Blueprint30개 / dependency344 packages / missing0 / redirector0 / compile failure0:** [현재 dependency 검사](../../Saved/MVPCompletion/20261110T160012Z-narrative-editor-validate_mvp_dependencies.json). 실제 Production map의 Cold Title/완주 launch는 위 fullweek에서 확인했다. **PASS — bounded Windows Cook:** [현재 Cook evidence](../../Saved/MVPCompletion/20261110T162035Z-cook-final-evidence.json), exit0/errors0, map1/Day7개/Visit16개, I/J narrative와 Ending/Title Widget2개, 확장 Audio/Cover6개가 Cook됐다. 기존 cook script의 I/J asset loop가 report timestamp 이름을 덮어쓰는 문제를 발견해 loop 변수명을 고쳤다. 이 Cook evidence는 실제 aggregate에 보존된 동일 stdout 결과를 고유 timestamp로 추출한 것이며 새 실행으로 위장하지 않았다. 실제 command/log는 20261110T162035Z다. **BLOCKED — Windows Package / Packaged Launch:** [UAT result](../../Saved/MVPCompletion/20261110T162441Z-ending-package/result.json), [실제 stdout](../../Saved/MVPCompletion/20261110T162441Z-ending-package/stdout.txt). UAT Cook는 exit0/0errors로 완료했지만 Stage에서 `C:\Program Files\Epic Games\UE_5.8\Engine\Intermediate\Build\BuildCookRun\StagedBuild_RecordShop.ini` 쓰기가 UnauthorizedAccessException으로 거부돼 UAT exit1이었다. 설치된 UAT source가 EngineRoot를 이 위치에 직접 결합함을 확인했다. Engine ACL/설치 파일/저장소 설정 변경 또는 엔진 복제로 우회하지 않았다. 완성 archive/exe가 없으므로 packaged launch와 배포물의 font notice 포함은 NOT RUN/미검증이다. Intermediate의 bootstrap만 실행 가능한 배포물로 주장하지 않는다. UAT가 이번에 생성한 untracked FileOpenOrder 로그2개는 생성시간/미추적/프로젝트 내부 경계를 검증한 뒤 해당 Saved package evidence 폴더로 옮겨 보관했다. 사용자 파일은 이동하지 않았다. Loose cook는 package/launch 검증이 아니다.

## 11. Runtime / Manual Review

현재 실제 결과: 초기 RED 후 installation/contract/smoke PASS. 720p1280×720와1080p1920×1080 실제 PC viewport로 Title/Ending9면을 캡처하고 한글/여백/긴 Credits를 확인했다. 새 QuitLabel 기본 보라색은 기존 UI 톤으로 수정했다. 최신 [Ending runtime matrix](../../Saved/MVPCompletion/20261110T162140Z-ending-runtime-verified.json)는 10개 case 모두 PASS다. 6장 각각 실제 GFM component/동일 source 유지 → Credits → Title audio0 → fresh New Game, 무음, FadeOut0, 정지된 component, pending-abort의 늦은 Day callback 무효화를 확인했다. RS006은 Ending에서 자연 EOF2회를 관찰했고 live voice≤1이었다. fixture의 History0과 별도로 실제 fullweek의 History16도 Ending 전후 동일했다. 최신 [실제 Title Quit](../../Saved/MVPCompletion/20261110T162350Z-ending-quit-verified.json)과 [최종 contract](../../Saved/MVPCompletion/20261110T162427Z-ending-contract-verified.json)도 PASS/exit0/unexpected gameplay error0다. Quit은 실제 OnClicked → QuitGame → PIE 종료를 확인한 것이며 packaged process 종료 증거는 아니다. 호스트 unittest20개도 PASS다. 자동화는 Slate Enter를 보내고 production owning-user focus를 확인한다. 실제 사람이 mouse/gamepad로 조작했다는 주장은 하지 않는다.

MANUAL_REVIEW: BGM 실제 음량/페이드/대화 balance/LP간 체감 loudness, 물리 mouse/gamepad, 현재 Shop 배경의 pawn 외형 노출 미감, 장시간/다회차, packaged executable의 전체 완주 및 최종 표현 품질.

## 12. 알려진 제한 / 실패 이력

초기 authoring API/pin 확인 실패는 asset save 전에 중단했으며 성공한 Editor 설치를 별도 기록했다. Runtime 첫 smoke는 폐기된 World의 Actor proxy 유효성 검사 때문에 harness가 실패했고 보완 후 통과했다. Matrix에서 강제 Stop 직후 기존 BGM natural-loop가 component를 재생성하는 것을 Ending 재시작으로 오판한 assertion은 stopped travel 경계 fixture로 분리했다. noneditable instance bool setter와 layout helper return 누락도 test-only 수정이다. 각각 실패 로그를 삭제하거나 PASS로 바꾸지 않았다. Legacy fixture 진입 실패는 GetCommandLine이 이 엔진에서 impure인데 실행 핀이 미연결인 것이 실제 graph 감사에서 확인됐다. 명시적 테스트 플래그를 읽도록 연결한 뒤 I/J matrix는 정상 Playing으로 진입해 PASS했다. 마지막 고객 종료용 Cursor assertion을 대사 종료에 잘못 적용한 harness 수정도 바로잡았다. 실제 Quit 최초 실행에서 기존 Turntable Tick이 파괴된 PlayerCharacter를 읽는 runtime Error가 발생했다. GFM의 최종 travel 직전에 Tick을 끄는 한 leaf로 수정했고 같은 Quit 검사에서 unexpected error 0을 확인했다. pending-abort에서 늦은 FinishDayTransition 직접 호출이 final flag를 변경할 수 있는 경계는 phase entry guard와 강화한 assertion으로 차단했다.

초기 Review의 installer 재실행 안전성 문제와 이후 stale day callback 지적은 모두 수정했다. 독립 리뷰의 나머지 Critical/Important 구현 결함은 없었다. 전주 All-BEST/All-POOR를 별도2회 완주하지는 않았으며, Ending의 History 미참조/실제 mixed History16 불변/I·J 각 등급의 같은 Ending을 검증했다. 기존 engine startup automation smoke signature와 EOS 연결 Warning은 gameplay 오류와 구분한다. 전체 로그 error-free라고 주장하지 않는다. 이전 Git LFS signal-pipe/Win32 error5는 이번 일반 status 조회에서 재현되지 않았다. 필요 시 command-only filter 비활성 조회를 병행했으며 repo config는 변경하지 않았다. 기존 ArtSource 오디오 temp 빈 폴더와 일부 Saved 과거 cook-output 폴더 permission 제한은 유지된다. 이것들은 이번 gameplay/Cook blocker가 아니며 새 package blocker는 위 Engine staging INI 권한이다.

## 13. Final QA Hand-off

기능 Gate A(Ending) / B(Credits→Title) / C(LP lifecycle) / D(New Game→재Tutorial→Day1)는 자동화 PASS다. Gate E의 A~J/Core/Narrative/17Cycle/History16 및 Blueprint/dependency/map/Cook는 PASS이나 package/packaged launch는 위 권한 문제로 BLOCKED다. 전체 출시/수동 QA를 PASS로 표시하지 않는다. Final QA는 (1) 실제 배포 exe Cold Title의 mouse/gamepad (2) New Game → Prologue 자유 이동 → Tutorial → Day1 (3) A~J 7일 완주 (4) J가 고른 LP와 동일한 Ending/Credits 배경음, 마지막 Fade/Title 무음 (5) 빠른 중복 입력/다시 New Game과 재Tutorial (6) Credits 외부 권리 증빙/고지 최종 대조 순서로 수행한다. External rights/physical QA 미완료 상태를 기술 구현 완료와 구분한다. 추가 고객/LP, 새 Formula/Manager/SaveGame/멀티엔딩은 없다. 이번 구현 범위에서 작업을 마쳤으며 staging/commit/push하지 않았다. 종료 시 branch/HEAD는 시작과 같고 staged0이다. 마지막 독립 읽기 전용 리뷰와 최종 evidence의 보존/30그룹/17Cycle/History16/추가 재Tutorial/호스트20검사가 일치한다. 패키징 권한, 수동 QA, 외부 권리 증빙은 위에 명시한 미완료 항목으로 남긴다.
### 이번 Gate의 정확한 증분 파일 목록

기존 파일 수정12개:

- Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset
- Content/RecordShop/Interaction/Components/BPC_Interaction.uasset
- Docs/Architecture/Day7EndingContentPlan.md
- Docs/Architecture/Day7EndingImplementationPlan.md
- Scripts/Unreal/audio_handoff_validation_support.py
- Scripts/Unreal/cook_mvp.py
- Scripts/Unreal/run_mvp_validation.py
- Scripts/Unreal/run_narrative_gate.py
- Scripts/Unreal/validate_audio_handoff_contract.py
- Scripts/Unreal/validate_customer_efgh_sequences.py
- Scripts/Unreal/validate_customer_ij_contract.py
- Scripts/Unreal/validate_day_week.py

신규20개:

- Content/RecordShop/Licenses/NanumGothic_OFL_Full.txt
- Content/RecordShop/UI/Ending/WBP_Ending.uasset
- Content/RecordShop/UI/Title/WBP_Title.uasset
- Docs/Architecture/EndingProductionReport.md
- Scripts/Unreal/audit_ending.py
- Scripts/Unreal/ending_content.json
- Scripts/Unreal/ending_reference.json
- Scripts/Unreal/ending_runtime_support.py
- Scripts/Unreal/ending_validation_support.py
- Scripts/Unreal/fix_ending_quit_tick.py
- Scripts/Unreal/fix_ending_stale_day.py
- Scripts/Unreal/fix_ending_validation_boot.py
- Scripts/Unreal/install_ending.py
- Scripts/Unreal/package_ending.py
- Scripts/Unreal/polish_ending_title.py
- Scripts/Unreal/test_ending_source.py
- Scripts/Unreal/validate_ending_contract.py
- Scripts/Unreal/validate_ending_quit.py
- Scripts/Unreal/validate_ending_runtime.py
- Scripts/Unreal/validate_ending_week.py

기존 데이터/Record/기타 Content554개는 보존했다. install/fix script는 Editor one-shot authoring 근거이며 현재 설치 Asset에 재실행하지 않는다. Saved에는 명령/로그/PNG/cooked output/실패 package evidence만 남는다. 후속 검증은 `run_customer_ij_gate.py`, `validate_ending_runtime.py --title --rendered --audio`, `validate_ending_quit.py --title --rendered --audio --windowed`, `validate_ending_contract.py --commandlet`을 기존 runner로 실행한다. 패키지는 해당 엔진 staging 경로의 정상 쓰기가 허용된 개발환경에서 `package_ending.py`를 다시 실행해야 한다.
## 14. 2026-11-11 재감사 / 새 실행 증거

### 이번 시작 상태와 변경 경계

이번 요청 시작 시 Ending/Title Asset, 구현·검증 스크립트와 본 보고서가 이미 미커밋 상태로 존재했다. 지정 문서5개 전체와 현재 구현을 읽고 기존 GFM authority를 대조했으며, installer/fix script를 재실행하거나 사용자 작업을 덮어쓰지 않았다. 시작 branch는 `feature/customer-narrative-content`, HEAD는 `6c848a34b7cc0e6a70c683c5e92dde04bff87854`, 미커밋 경로60개, staged0이었다. [금회 시작 status / SHA716](../../Saved/MVPCompletion/20261111T050640Z-ending-reaudit-start.json)을 보존했다. 1~13절의 시작35개 및 구현 증분 목록은 앞선 제작 이력이다.

금회 Production Asset 수정/생성은 **0개**다. 기존 GFM/BPC_Interaction/WBP_Ending/WBP_Title과 A~J/6LP를 그대로 검증했다. 금회 문서 변경은 **본 보고서1개**이며 새 실행 자료는 ignored Saved/MVPCompletion에 남긴다. 본 보고서 갱신 직전 시작716개 파일이 전부 동일했다. 기존 최종 evidence의788개 SHA도 시작 시 모두 일치했다. 기존30개 회귀 leaf의 결과/로그 존재와 PASS를 확인했지만 이30개 전체를 이번에 새로 실행했다고 표시하지 않는다. branch/HEAD 및 index를 유지했고 staging/commit/push/사용자 저장 파일 삭제는 하지 않았다.

### 새 검증 결과

| 검사 | 상태 | 실제 근거 / 범위 |
|---|---|---|
| Ending 계약 / 보호 SHA | PASS | [새 contract process](../../Saved/MVPCompletion/20261111T050652Z-ending-reaudit-contract-process.json), Content554 보존과 승인된 GFM/BPC migration hash |
| Gate A/B/C/D — 720p Ending matrix | PASS | [새 runtime process](../../Saved/MVPCompletion/20261111T050959Z-ending-reaudit-recovered-720-process.json), [결과](../../Saved/MVPCompletion/20261111T050959Z-ending-reaudit-recovered-720.json): viewport1280×720, 10사례, 실제 UI/audio/fresh World travel |
| Gate E — 전체 진행 | PASS | [새 week process](../../Saved/MVPCompletion/20261111T051225Z-ending-reaudit-week-process.json), [결과](../../Saved/MVPCompletion/20261111T051225Z-ending-reaudit-week.json): 첫 세션17 Cycle / History16 / Final hook1 / Ending1 |
| Title Quit | PASS | [새 Quit process](../../Saved/MVPCompletion/20261111T052442Z-ending-reaudit-quit-process.json): 실제 버튼 → QuitGame → PIE 종료. 배포 exe 종료 검증은 아님 |
| Blueprint / Dependency | PASS | [새 dependency process](../../Saved/MVPCompletion/20261111T052518Z-ending-reaudit-dependencies-process.json), [상세](../../Saved/MVPCompletion/20261111T052518Z-ending-reaudit-dependencies.json): Blueprint30 / packages344 / missing0 / redirector0 / compile failure0 |
| Windows Cook | PASS | [새 Cook process](../../Saved/MVPCompletion/20261111T052534Z-cook-final-process.json): exit0/errors0, Shop map, Ending/Title2개, Day7개/Visit16개, I/J narrative와 확장 Audio/Cover6개 포함. 기존 SkipSaveAssetRegistry loose-cook 범위 |
| Host / Python syntax | PASS | 실제 `python -m unittest discover -s Scripts/Unreal -p 'test_*.py' -v` 20개 통과. Unreal Python103개 AST parse 통과 |
| 금회 1920×1080 재실행 | BLOCKED — process FAIL | [실패 process](../../Saved/MVPCompletion/20261111T052325Z-ending-reaudit-1080-process.json): 창 조절 후 viewport1644×1080으로 assertion 실패. 이 실행의 Ending matrix는 시작 전 중단. 새로운1080p PASS로 표시하지 않음 |
| 이전 동일 자산 1920×1080 | PASS — 이전 증거 | [이전 결과](../../Saved/MVPCompletion/20261110T153010Z-ending-ui-1080.json)의 viewport1920×1080/PASS 및 캡처 재확인. 현재 자산 SHA 동일. 새 실행과 구분 |
| Windows Package / Packaged Launch | BLOCKED / NOT RUN | 10절의 UAT Stage 권한 실패 유지. 금회 package 재실행/배포 exe launch 없음. 설치 UAT source의 EngineRoot/Intermediate 쓰기 경로를 읽기 전용으로 재확인 |
| 사람의 직접 QA / 외부 권리 | BLOCKED — MANUAL_REVIEW / CREDIT_VERIFICATION_REQUIRED | 물리 입력, 체감 음량/fade, 장시간 플레이, 배포물·권리 증빙 미완료 |

새 주간은 Cold Title → fresh New Game → 기존 Prologue → Tutorial → A/E/B/C/A/F/D/B/C/A/G/B/D/H/I/J → J 정상 Exit/Cleanup → FinalStoryEvent → Ending → Credits → Title → fresh New Game → 재Tutorial → Day1 A까지 통과했다. 첫 세션 Tutorial1+예정16=17이며 재시작 Tutorial1은 별도다. History는 Sequence1~16이며 Ending 내내16을 유지했다. DayStarted/Ended는 각각1~7, FinalEvents1개, Ending은 동일 Widget9면으로1회다. 두 번째 세션 Day1 A에서 History0/audio leak=false/UI leak=false였다. 고객 완료·퇴장·day progression은 강제하지 않았다. 플레이어 접근 위치/가상 Slate 입력/unsaved observer는 fixture다.

새 Ending matrix는 실제 GFM AudioComponent로 RS001~006 각각의 동일 source를 Credits까지 유지하고 Title에서는 voice0을 확인했다. 무음, FadeOut0, 정지된 component, EndingPending 중 abort/늦은 FinishDayTransition을 포함한다. RS006 자연 EOF2회에서 live voice≤1이었다. 중복 Final/Spawn/Continue/Return 및 위조 Origin은 UI 중복/페이지 건너뛰기/추가 고객을 만들지 않았다. Matrix의 완료 Day7/accepted Result는 명시적 unsaved fixture이며, 실제 J cleanup/History16은 별도 주간 검증 근거다.

### 화면·실패 기록·남은 QA

Agent가 새720p Title 및 Ending/Credits9면을 모두 확인했고 한글/확정 팀원6명·역할/긴 Engine 고지/버튼의 잘림·겹침은 보이지 않았다. 기존 동일 자산1080p의 연락/팀원/긴 고지 캡처도 재검토했다. 사람의 최종 입력·청취·표현 품질 승인과 구분한다. [Epic EULA §7](https://www.unrealengine.com/eula/unreal), [OFL 전문](https://openfontlicense.org/documents/OFL.txt), [네이버 안내](https://help.naver.com/service/30016/contents/18088?osType=PC)를 금회 다시 조회하고 로컬 font 고지와 음악/커버 provenance를 대조했다. 미확인 외부 에셋의 실제 취득 권리를 새로 확정하지 않았다.

최초 runtime `20261111T050733Z`는 -RenderOffscreen에 native window 조절을 요청해 창 검색에서 FAIL했다. 기존 성공 명령의 --windowed와 비교해 명령만 바로잡았으며 Production/검사 코드는 바꾸지 않았다. 다음 `20261111T050914Z`는 서버 재시작으로 Editor 시작 중 중단돼 완료 결과가 없으므로 BLOCKED/미완료다. 복구 후 `20261111T050959Z`가10사례 성공 실행이다. 별도 `20261111T052325Z`1080p 실패도 그대로 보존했다. 성공 실행들의 새 gameplay unexpected error는0이며 알려진 엔진 pre-init smoke signature만 기존 strict classifier로 구분했다.

Final QA는 권한이 허용된 개발환경에서 package를 완성하고 실제 배포물의 Nanum 고지/전문을 확인해야 한다. 그 exe에서1920×1080, 물리 mouse/gamepad, LP 음량/fade, 완주·재시작·Quit를 확인한다. Cigar_room/Fab Vintage Stereo/모델·외부 애니메이션의 제작자·원본 URL·취득 시 적용 license 증빙도 필요하다. 기능 Gate A~D 및 주간/compile/Cook PASS를 package·금회1080p·수동 QA·권리 출시 승인 PASS로 확대하지 않는다. [금회 통합 evidence](../../Saved/MVPCompletion/ending-reaudit-final-evidence.json)에 성공/실패/중단/보존 경계를 함께 기록한다.
