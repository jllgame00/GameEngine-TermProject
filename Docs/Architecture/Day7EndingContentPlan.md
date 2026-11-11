# Day 7 / Ending — Content Lock
> 2026-11-11 Ending Production 업데이트: 기존 GFM의 FinalStoryEvent를 Ending → Credits → 같은 Shop Map의 Title로 연결했다. New Game은 fresh OpenLevel → 기존 Prologue/Tutorial/Day1이다. Day7만 마지막 LP를 Credits까지 유지하며 Title 이동 시 기존 FadeOut/Stop을 사용한다. 사용자 승인 원문은 Scripts/Unreal/ending_content.json과 실제 WBP 표시를 대조한다. 기존 I/J·A~H·LP 원문/태그는 변경하지 않는다. 아래의 “이번에는 I/J만/Ending 미구현” 표현은 이전 Gate 이력이며 현재 구현/검증 상태는 [EndingProductionReport.md](EndingProductionReport.md)를 따른다. 외부 에셋 권리에는 CREDIT_VERIFICATION_REQUIRED가 남으며 MANUAL_REVIEW를 자동 PASS로 바꾸지 않는다.

작성일: 2026-11-10  
문서 상태: **APPROVED_DESIGN / CONTENT_LOCK (I/J 및 사용자 승인 Ending 원문) / MANUAL_REVIEW / CREDIT_VERIFICATION_REQUIRED**  
후속 사용자 최종 승인: I/J 원문과 단일 Ending A의 시작·부모님 연락·답장·완료·Credits 마지막·버튼 문구는 CONTENT_LOCK이다. J 첫 행은 아래 확정 원문을 유지한다. 실제 청취·물리 입력 검토와 외부 권리 검증은 별도다.

현재 구현 Gate는 I/J만 대상으로 한다. 아래 Ending/Title/Day7 오디오 예외는 다음 Gate의 IMPLEMENTATION_REQUIRED이며 이번에는 적용하지 않는다. 현재 Day7도 기존 EndCurrentDay 오디오 cleanup을 유지한다. 실제 구현·검증 결과는 [Day7CustomerProductionReport.md](Day7CustomerProductionReport.md)를 따른다. 아래 read-only 감사와 비변경 기록은 이전 설계 Gate의 이력이다.

## 1. 상태와 이번 사용자 결정

| 상태 | 의미 |
|---|---|
| APPROVED_DESIGN | 이번 사용자가 선택한 인물/profile/Ending 방향/진행 계약 |
| CONTENT_LOCK | 사용자 최종 승인된 I/J 원문 및 Ending 시작·연락·답장·완료·마지막 Credits·버튼 |
| CONTENT_LOCK_REVIEW | Ending UI 세부 문구/출처 표시 등 아직 별도 검토가 남은 표기 |
| IMPLEMENTATION_REQUIRED | 실제 asset/graph/UI/data 연결이 필요한 항목. 이번에 구현하지 않음 |
| MANUAL_REVIEW | 실제 화면·청취·입력·packaged 실행 등 사람의 확인 필요 |
| CREDIT_VERIFICATION_REQUIRED | 외부 출처/제작자/적용 라이선스 증빙 미확정. 출시 전 확인 대상 |

**APPROVED_DESIGN**

- I: 30대, 수영 뒤 방문, Quiet / Electronic / Adventurous, RS004 BEST, 1회 방문.
- J: 20대, 장보기 뒤 방문, Quiet / Jazz / Traditional, RS001 BEST, 1회 방문. A와 태그가 같아도 변경하지 않는다.
- Ending A: 부모님의 짧은 원격 연락과 플레이어의 답장. 실제 귀환 장면 없음.
- 단일 Ending. 추천 합산점수·BEST 수·호감도·성공/실패 판정 없음.
- J Result의 선택 LP를 Customer Exit → Ending → Completion → Credits까지 유지하고, Audio Fade Out 뒤 Title로 복귀한다.
- Credits와 Title/New Game을 포함한다. 새 실행에는 이전 Day/Queue/History/Tutorial/선택 LP가 누출되지 않는다.
- 사용자 후속 응답으로 확정한 6명 이름/역할을 Credits에 사용한다.

**채택하지 않은 이전 후보**

| 이전 내용 | 이번 상태 |
|---|---|
| Option B: 플레이어 마감 메모/일지 중심 Ending | 제외. 새 마감 일지 작성 연출을 섞지 않음 |
| Option C: 부모님 매장 귀환 | 제외. 부모님 mesh/귀환 camera/인사 cutscene 불필요 |
| Day7도 Fade/Stop 후 무음 Ending으로 끝내는 기본 추천 | 이번 사용자 선택으로 대체. Day1~6 cleanup은 그대로, Day7만 Ending 소유권 인계 |
| Credits 선택 사항 / “처음부터”만 있는 완료 화면 | 대체. Credits → Title → New Game이 필요한 구현 범위 |
| 이전 I/J 원문 검토 대기 | 후속 사용자 승인으로 CONTENT_LOCK. READY/실제 테스트 결과는 별도 기록 |

이전 문서는 전체 읽고 현재 source/실제 자산과 대조했다. 승인된 설계와 새로 작성한 문구를 같은 상태로 묶지 않는다.

## 2. 설계 Gate 당시 Production 감사

- 경로: `D:\univ\3-1\GameEngine\Termproject\RecordShop`.
- Branch: `feature/customer-narrative-content`; HEAD: `6c848a34b7cc0e6a70c683c5e92dde04bff87854`.
- 시작 상태: 기존 이 문서만 untracked. staged 파일 없음. 기존 audio 임시 폴더 permission warning은 유지된다. Git LFS signal-pipe 오류는 이번 status 조회에서 재현되지 않았다.
- [이번 read-only Editor 감사](../../Saved/MVPCompletion/20261110T104120Z-day7-content-lock-audit.json): 실제 Shared Catalogue 여섯 LP resolve, graph node/pin, E~H DataTable, Schedule16, UI registry7개, import 기록31개를 읽었다. asset save/compile/row 생성/PIE를 실행하지 않았다.
- 최초 감사 probe는 없는 StructureEditorLibrary API 조회에서 중단됐다. 이를 제거한 최종 read-only 감사가 PASS했으며 앞선 실패 로그는 Saved에 남긴다. 이는 구현/회귀 테스트 PASS가 아니다.
- 현재 Day7은 여전히 TEMP_D7_01 / TEMP_D7_02이며 I/J 자산은 없다.

| 구간 | 확정 운영 순서 |
|---|---|
| Tutorial | 연습 cycle. scheduled History 제외 |
| Day1 | A1 → E1 |
| Day2 | B1 → C1 |
| Day3 | A2 → F1 → D1 |
| Day4 | B2 → C2 |
| Day5 | A3 → G1 |
| Day6 | B3 → D2 → H1 |
| Day7 적용 설계 | I1 → J1 → FinalStoryEvent |

I/J는 TEMP 슬롯 대체다. History16은 유지하며 Tutorial을 포함한 17건으로 바꾸지 않는다. 승인 설계 적용 후 고유 고객 A~J는 10명이며 “16명을 만족시켰다”라고 쓰지 않는다. 부모님의 연락과 Ending을 추가 customer/history entry로 만들지 않는다.

A~H의 작은 closure는 그대로다. Ending이 화해/작업 성공/모임 성공/생활 개선을 확정하거나 그 공을 플레이어에게 돌리지 않는다. Source: [A](../../Scripts/Unreal/customer_a_dialogue.json), [B](../../Scripts/Unreal/customer_b_dialogue.json), [C/D](../../Scripts/Unreal/customer_cd_dialogue.json), [E~H](../../Scripts/Unreal/customer_efgh_dialogue.json).

## 3. Customer I — 승인 설계와 원문

### APPROVED_DESIGN

30대의 수영을 마친 손님. 운동 자체의 성과나 사건 없이, 귀가 전에 조용한 새 전자음의 결을 들어보고 싶다. 담백한 존댓말로 자신의 요청을 말한다. 직업·성별·가족·건강 문제는 추가하지 않는다. 수영장/운동 기구/젖은 옷 prop도 필요 없다.

Profile: **Quiet / Electronic / Adventurous**, CustomerID **I**, VisitNumber **1**, Day7 첫 번째 방문. Presentation은 기존 placeholder 재사용이며 실제 30대 3D 외형 완성으로 표시하지 않는다.

### CONTENT_LOCK — 본문 4행

| 계획 RowID | Speaker | Production 투입 검토 원문 |
|---|---|---|
| I1_Current_01 | 수영을 마친 손님 | 수영하고 돌아가는 길이에요. 잠깐 앉아서 음반 하나 듣고 가려고요. |
| I1_Current_02 | 수영을 마친 손님 | 지금은 박자가 밀어붙이지 않고, 소리 사이에 여유가 있었으면 해요. |
| I1_Current_03 | 수영을 마친 손님 | 작게 번지는 신스나, 전자음의 질감이 조금씩 달라지는 곡이 궁금해요. |
| I1_Current_04 | 수영을 마친 손님 | 늘 듣던 것과 다른 소리도 괜찮아요. 조용하지만 낯선 음반으로 골라 주실래요? |

Quiet는 2행의 밀도/여유, Electronic은 3행의 신스/전자음, Adventurous는 3~4행의 낯선 소리에 대한 호기심이다. 나이나 취미가 정답 단서가 아니다. F의 버스 대기, B의 작업/평가 Arc와 구분한다. 재방문 기억과 다음 방문 약속은 없다.

### CONTENT_LOCK — Result / 퇴장 반응

| 논리 ContentID | 사용 시점 | 원문 |
|---|---|---|
| I1_Result_BEST | 기존 grade=BEST | 조용한데 음색이 낯설어서, 제가 찾던 쪽이에요. |
| I1_Result_GOOD | 기존 grade=GOOD | 흥미로운 소리네요. 생각했던 분위기와는 조금 달라요. |
| I1_Result_POOR | 기존 grade=POOR | 오늘 듣고 싶던 전자음의 질감과는 조금 다르네요. |
| I1_Exit | Result 뒤 퇴장 직전의 중립 반응 | 추천해 주셔서 고마워요. 이만 가볼게요. |

퇴장 문구는 Result panel의 반응 아래에 표시하고 Continue 뒤에는 기존 퇴장만 진행하는 최소안을 사용한다. 별도 퇴장 Dialogue cycle/History callback을 추가하지 않는다. 어떤 grade에서도 운동이나 삶이 개선됐다고 말하지 않는다.

## 4. Customer J — 승인 설계와 원문

### APPROVED_DESIGN

20대의 장보기를 마친 손님. 남은 시간에 익숙하고 편안한 재즈를 듣고 가려 한다. 평범한 존댓말이며 A의 노년 말투·세대 불만·재방문 관계를 가져오지 않는다. 장보기는 한 줄 배경이고 상점 이동/가방 prop/경제 gameplay는 없다. Day7이 실제 주말이라고도 새로 확정하지 않는다.

Profile: **Quiet / Jazz / Traditional**, CustomerID **J**, VisitNumber **1**, Day7 두 번째 방문. A와 같은 tag는 유지한다. 취향은 연령이 아닌 아래 요청으로 읽힌다. Appearance=PLACEHOLDER.

### CONTENT_LOCK — 본문 4행

| 계획 RowID | Speaker | Production 투입 검토 원문 |
|---|---|---|
| J1_Current_01 | 장을 본 손님 | 오늘은 장을 일찍 다 봤네요. 잠깐 음악을 듣고 가려고요. |
| J1_Current_02 | 장을 본 손님 | 큰 소리나 급한 변화 없이, 편하게 따라갈 수 있는 곡이면 좋겠어요. |
| J1_Current_03 | 장을 본 손님 | 피아노와 베이스가 있는 작은 재즈 합주를 좋아해요. |
| J1_Current_04 | 장을 본 손님 | 새로운 곡이어도 선율과 진행은 익숙했으면 해요. 전통적인 재즈 연주 쪽으로 골라주시겠어요? |

Quiet는 2행, Jazz는 3행, Traditional은 4행이다. 새로운 곡 자체를 거부하거나 옛 음악이 우월하다고 주장하지 않는다. 특정 실존 스탠더드 곡을 요구하는 대사가 아니므로 original RS001 Audio 교체도 불필요하다.

### CONTENT_LOCK — Result / 퇴장 반응

| 논리 ContentID | 사용 시점 | 원문 |
|---|---|---|
| J1_Result_BEST | 기존 grade=BEST | 익숙한 흐름을 편하게 따라들을 수 있네요. |
| J1_Result_GOOD | 기존 grade=GOOD | 편하게 들었어요. 떠올렸던 재즈의 느낌과는 조금 다르네요. |
| J1_Result_POOR | 기존 grade=POOR | 오늘은 조금 더 익숙한 재즈 연주를 듣고 싶었어요. |
| J1_Exit | Result 뒤 퇴장 직전의 중립 반응 | 음반 골라주셔서 고마워요. 그럼 가볼게요. |

J도 Result panel 내 반응/퇴장 문구 후 기존 Continue/Exit를 따른다. 마지막 손님이라는 이유로 손님 전체를 대표해 플레이어를 평가하지 않는다. GOOD/POOR여도 같은 Ending으로 간다.

## 5. 실제 여섯 LP와 점수 검산

이번 read-only Editor에서 현재 DA_RecordCatalogue → ResolvePlayableRecord로 여섯 장을 직접 조회했다. 기존 식 **Mood + Genre + Theme 정확 일치 각 1점**을 대입했다. Formula/RecordID/tag를 수정하지 않았다.

| LP / 실제 Title | Mood / Genre / Theme | I 점수 | J 점수 |
|---|---|---:|---:|
| RS001 비 갠 오후 | Quiet / Jazz / Traditional | 1 POOR | 3 BEST |
| RS002 새벽의 찻집 | Quiet / Jazz / Sociable | 1 POOR | 2 GOOD |
| RS003 네온 질주 | Restless / Electronic / Adventurous | 2 GOOD | 0 POOR |
| RS004 빛의 잔결 | Quiet / Electronic / Adventurous | 3 BEST | 1 POOR |
| RS005 마주 놓은 의자 | Quiet / Folk / Sociable | 1 POOR | 1 POOR |
| RS006 남겨 둔 쉼표 | Quiet / Classical / Reflective | 1 POOR | 1 POOR |

**CONTENT_LOCK — I/J authored 후보 순서**

| Visit | CandidateRecordIDs의 명시적 순서 | 순서대로 점수 |
|---|---|---|
| I1 | [RS003, RS001, RS004] | GOOD2 / POOR1 / BEST3 |
| J1 | [RS002, RS001, RS003] | GOOD2 / BEST3 / POOR0 |

3개 unique valid ID이며 BEST 위치도 고정하지 않는다. Author order가 authority다. 기존 A~H candidate는 바꾸지 않는다. 기존 D/H에 GOOD가 없는 제한도 그대로이며 이번에 전체 score matrix를 재설계하지 않는다.

이 표의 원래 근거는 read-only data 조회와 설계 산술 검산이다. 이번 I/J Production 적용/실제 runtime 검증 결과는 Day7CustomerProductionReport.md에서 별도로 기록한다.

## 6. Dialogue / Row / History 투입 계약

I/J 부분은 이번 Production Gate의 적용 계약이다. 실제 적용/검증 결과는 보고서를 따른다. Ending은 IMPLEMENTATION_REQUIRED로 남는다.

| 영역 | 적용 계획 |
|---|---|
| 본문 DataTable | /Game/RecordShop/Data/Narrative/DT_I_Dialogue, DT_J_Dialogue 각각 4행. 기존 /Game/DialogueData struct 재사용 |
| Row 필드 | Name/DialogueID=위 RowID, Speaker/Text=검토 후 승인 FText, Mood=Quiet, MusicPreference=Electronic 또는 Jazz |
| 종료 표시 | 01~03 IsEndNode=false, 04만 true. 본문에 Result/Exit/Ending row를 섞지 않음 |
| Theme authority | DialogueData에 Theme 열을 새로 만들지 않음. Narrative.TargetThemeOverride → runtime CustomerProfile.Personality 사용 |
| Narrative asset | DA_I1_Narrative / DA_J1_Narrative. SequenceID=I_V1 / J_V1, SourceTable=각 DT, OrderedRows=위 01→04 |
| override | I Quiet/Electronic/Adventurous; J Quiet/Jazz/Traditional. customer class default 불변 |
| 기억 | MemoryVisitNumbers와 모든 memory intro/outro 목록 비움. Previous Recommendation Memory/다음 방문 branch 없음 |
| 후보 | 5절의 explicit CandidateRecordIDs |
| Schedule | 새 DA_Visit_I_1 / DA_Visit_J_1을 DA_Day07.Visits 두 슬롯에 연결. 기존 TEMP asset은 즉시 삭제/rename하지 않고 production 참조에서 제외 |
| Visit 표시/예약 필드 | 기존 BP_Customer01 presentation, IsPlaceholderContent=true(appearance). Narrative는 새 I/J definition. StoryEventID=None, 사용되지 않는 CustomerData row handle은 비워 두며 Ending은 Week의 최종 hook 사용 |
| History | CustomerID I/J, VisitNumber1, Day7. 기존 Result commit이 선택 RecordID/Score/Result를 각각 한 건 저장 |
| Sequence 의미 | I_V1/J_V1은 Dialogue SequenceID. History.Sequence는 계속 저장 순서 정수이며 최종 J는 정상 전체 주간 실행에서 16 |
| clear / cancel | 기존 pending consume-once, dialogue 완료/취소 context clear, runtime override leak 방지 유지 |

현재 E/F/G/H 실제 본문은 각각 4행이다. I/J도 상황1행 + 소리 요청3행으로 같은 분량/존댓말을 따른다. A~D의 재방문 도입과 달리 기억 문장을 붙이지 않는다. I/J 원문은 CONTENT_LOCK이며 이번 Gate에서 runtime ReviewStatus=READY로 투입한다.

**Result 원문 연결 최소안:** 설계 Gate 당시 WBP_Result_IntegrationFallback의 중립화 architecture에는 고객별 반응 원문 선택이 없었다. 이번 I/J Gate에서는 이 최소안을 적용한다. BP_VisitNarrativeDefinition에 비어 있는 FText 기본값 ResultBestText/ResultGoodText/ResultPoorText/ExitText를 추가하는 계획이다. I/J asset에만 검토 후 승인 원문을 넣고, 기존 grade branch가 해당 text를 읽는다. 기존 A~H/Tutorial은 empty → 현재 legacy/neutral fallback을 그대로 유지한다. 별도 reaction table/manager/새 grade authority는 만들지 않는다.

위 I1_Result_*/J1_Result_* 및 Exit ID는 문서상 ContentID이고 실제 Dialogue row가 아니다. FText namespace CustomerI/CustomerJ와 안정된 key에 대응할 계획이다. Reaction + 빈 줄 + ExitText를 Result 설명에 표시하며 score/grade heading/Available/Continue 동작은 유지한다. 별도 완료 callback이나 추가 History 저장은 없다.

## 7. 채택된 Ending A

**APPROVED_DESIGN:** 부모님의 연락에 짧게 답하면서 맡은 일주일을 끝낸다. 부모님은 현재 Shop에 등장하지 않고, 플레이어의 마감 일지를 중심 장면으로 만들지 않는다. 원문은 다음 절의 사용자 최종 승인 CONTENT_LOCK이다.

| 순서 | 진행 계약 |
|---|---|
| J Result | 기존 Result/History 확정과 선택 LP Store BGM 시작 |
| Customer Exit | Continue 뒤 기존 퇴장. 고객이 남아 있는데 Ending을 끼워 넣지 않음 |
| Day7 완료 | 기존 Queue 완료 조건/OnDayEnded/FinalStoryEvent 1회 guard 보존. 오디오는 EndingPending 소유로 유지 |
| Ending Dialogue | 시작 문구 → 부모님 연락 → 플레이어 답장. 기존 Shop 시점과 text UI |
| Completion | 7일 완료 문구. 점수·등급·고객 성공 여부 없음 |
| Credits | 확정 팀원/확인된 출처·license 고지. 마지막 LP 계속 재생 |
| Return | 사용자 “타이틀로” → BGM Fade Out/Stop → Title |
| New Game | 새 세션에서 부모님 안내/Tutorial부터. 이전 실행 상태 누출 없음 |

진행은 Continue로 읽는 속도를 존중한다. 30~50초는 Ending 원문 읽기 목표이지 강제 타이머가 아니다. Credits는 짧은 정적 page로 설계하며 자동 scrolling framework는 불필요하다. 부모님 actor/portrait/전화기 model/음성/새음악/새map은 없다.

## 8. Ending / UI 원문 전문

**사용자 지정 시작·부모님 연락·답장·완료·Credits 마지막·버튼 원문: CONTENT_LOCK.** 화면 소제목/부가 출처 정보는 구현 표기이며 MANUAL_REVIEW와 권리 검증을 유지한다. 실제 표시 source는 ending_content.json, 구현 결과는 EndingProductionReport.md다.

| 논리 ID / Speaker | 표시 원문 |
|---|---|
| Ending_Start_Title | 마지막 영업을 마치고 |
| Ending_Start_Text / 내레이션 | 마지막 손님이 가게를 나섰다.\n부모님에게서 짧은 연락이 왔다. |
| Ending_Parents_Title | 부모님에게서 온 연락 |
| Ending_Parents_Text / 부모님 | 오늘이 마지막 날이네.\n일주일 동안 가게 맡아줘서 고마워.\n마감하면 편히 쉬렴. |
| Ending_Reply_Title | 답장 |
| Ending_Reply_Text / 플레이어 | 오늘 손님도 다 다녀가셨어요.\n이제 마감할게요. |
| Ending_Continue | 계속 |
| Ending_Complete_Title | 일주일의 운영을 마쳤습니다. |
| Ending_Complete_Body | 미표시 — 빈 FText. 성적표/통계 본문 없음 |
| Ending_EnterCredits | 크레딧 보기 |
| Credits_Team_Title | 만든 사람들 |
| Credits_Source_Title | 음악과 아트 |
| Credits_License_Title | Unreal Engine / 외부 에셋 출처 검증 |
| Credits_Next | 다음 |
| Credits_End_Text | 함께해 주셔서 고맙습니다. |
| Credits_ReturnTitle | 타이틀로 |
| Title_Title | RecordShop |
| Title_NewGame | 새 게임 |
| Title_Quit | 게임 종료 |

표의 \n은 명시적인 표시 줄바꿈이다. 연락/답장은 고정 text presentation이며 타이핑·발송 gameplay가 아니다. 이전 후보의 “메모 옆에 마감 기록을 남긴다”라는 새 일지 연출은 사용하지 않는다.

현재 Production의 실제 Prologue 안내([AdvancePrologue source](../../Scripts/Unreal/install_prologue_tutorial.py)):

> 아직 가게 일이 익숙하지 않겠지만,  
> 손님의 이야기를 듣고 어울리는 음악을 골라주면 된단다.  
> 오늘이 첫날이야.

Ending의 “오늘이 마지막 날이네”가 시작의 “첫날”과 가볍게 대응한다. 플레이어는 손님을 맞은 사실만 답한다. 추천을 잘했다는 평가, 손님 삶의 해결, 새 과거사·귀환 일정·가게 미래 계획을 쓰지 않는다. 모든 Result 조합에 위 원문이 동일하다.

## 9. 마지막 LP 유지/종료 설계

**APPROVED_DESIGN:** J가 실제 선택한 LP를 Credits까지 유지한다. **IMPLEMENTATION_REQUIRED:** 아래 최소 변경. 현재 이미 되는 동작이라고 표시하지 않는다.

### 현재 정지 위치

실제 graph 감사의 EndCurrentDay는 CustomerCycle/queue 완료/비진행/ActiveCustomer 없음 guard 뒤 DayPhase=DayEnding, DayCustomersComplete=true를 설정하고 **StopStoreBGM을 호출**한다. 이어 ShowDayPresentation → OnDayEnded → .75초 FinishDayTransition이다. 마지막 날은 FinalStoryEventTriggered를 한 번 설정하고 OnFinalStoryEvent를 dispatch한다.

현재 StopStoreBGM은 requested=false, CurrentStoreBGMRecordID=None, StoreBGMSound=None을 먼저 설정하고, Finished delegate 해제 → .6초 Fade Out → FinishStoreBGMStop timer로 Stop/ref clear한다. 따라서 현재 Hook에는 음악이 남지 않는다. StartStoreBGM/BeginCompletedStoreBGM은 accepted Result 조건을 요구하므로 Hook에서 다시 호출하는 것이 유지안은 아니다.

### 최소 변경 경계

- Day1~6 EndCurrentDay → StopStoreBGM 및 다음 BeginDay/ResetDayAudio는 그대로 둔다.
- Day7 마지막 완료에 한해 **기존 GFM**이 EndingPending 소유로 인계한다. 이미 재생 중인 StoreBGMRef/ID/sound/request를 유지하며 여기서 Play/FadeIn/seek를 다시 호출하지 않는다.
- 새 BGM manager, duplicated record map, 새 SelectedRecord는 없다. 기존 cache가 canonical Shared Catalogue audio 및 J1 History.RecordID와 맞는지 확인한다. Score/Result는 Ending 선택 조건으로 읽지 않는다.
- 기존 자연 EOF loop handler는 PlayCurrentStoreBGM을 사용하므로 Result state 밖에서도 같은 source로 반복 가능하다. EOF의 component 교체는 정상이며 UI 전환으로 곡을 재시작하는 것과 구분한다.
- 최종 EOF와 인계가 겹치면 기존 request/ID가 유효할 때 idempotent PlayCurrentStoreBGM으로 복구할 수 있으나, 이미 playing component가 있으면 새 voice를 만들지 않는다.
- invalid/missing audio일 때는 진단을 남기고 같은 Ending을 무음으로 진행한다. RS001 등 고정 fallback이나 Bad Ending은 없다.
- Ending/Completion/Credits 전환은 음악 정지 없이 같은 source를 유지한다. Title로 갈 때는 ReturningToTitle로 먼저 잠그고 pending gameplay timer와 이전 UI callback을 무효화한 뒤 StopStoreBGM → fade 완료/FinishStoreBGMStop → voice0/ref None → TitleLoading → 단일 map reload를 따른다.
- ref/audio가 없거나 이미 정지했거나 fade 시간이0이면 같은 Return finalizer로 즉시 합류한다. 기존 StopStoreBGM의 invalid-ref branch는 완료 timer를 만들지 않으므로 이를 기다리며 멈추면 안 된다.
- EndingPending 중 abort에서는 .75초 FinishDayTransition 등 pending timer를 fade 대기 전에 취소해 DAY/TBD panel의 재등장을 막는다.
- 반복 Return/Continue/Final hook은 같은 동작을 다시 시작하지 않는다. Title/새 세션/종료·abort에서는 요청/ID/sound/ref와 관련 timer가 남지 않아야 한다.

GFM에 Title/Playing/EndingPending/EndingDialogue/EndingCompletion/Credits/ReturningToTitle/TitleLoading을 구분하는 **한 presentation phase**를 두는 계획으로 새 시스템을 최소화한다. 기존 DayPhase와 History를 대체하지 않는다. BP_Turntable의 Listening/완료 authority는 수정할 필요가 없다.

## 10. Credits 확정 팀원 / 원문

**APPROVED_DESIGN — 사용자가 이번 Gate 후속 응답으로 확정한 이름/역할.** 출처 지시: 노션 「게임엔진기초 → 텀프로젝트 → 07. 역할별 개발 계약 · Branch · Asset Owner」. 아래 명단은 그 페이지를 추측해 복원한 것이 아니라 사용자에게 직접 제공받은 확정 정보다.

| 표시 이름 | 표시 역할 |
|---|---|
| 정우빈 | Integration / Core Flow / Camera |
| 전찬 | Interaction / Recommendation / Turntable |
| 주정은 | NPC / AI / Animation |
| 조현우 | UI / 2D / Audio / Presentation |
| 김민서 | Environment / 3D / Lighting |
| 박준혁 | Dialogue / Data / Narrative |

이 표의 이름/역할은 크레딧에 그대로 사용한다. Git alias/PR 계정과 실명을 임의 매핑하지 않는다.

**CONTENT_LOCK_REVIEW — 음악/아트 표시 초안**

- 오리지널 음악 — RecordShop 로컬 합성 음원 · RS001~RS006
- 커버 원본 — RecordShop 코드 기반 벡터 일러스트 · RS004~RS006
- 제작 도구 지원 표기는 실제 provenance의 “OpenAI Codex for RecordShop”에 근거해 검토한다. 이를 실존 작곡가/디자이너 이름으로 바꾸지 않는다.
- 게임 속 Artist 값(창가의 세 사람/유월의 등불/신호등 오락실/느린 회로/나무결 셋/작은 방 실내악)은 fictional metadata이며 실제 권리자·팀원 크레딧이 아니다.

Credits는 팀원 → 음악/아트/외부 출처 → 필요한 사용권 고지 순서의 짧은 정적 page를 기본으로 한다. 마지막 문구와 버튼은 8절을 사용한다. 미확인 출처를 “기타 무료 에셋”으로 뭉뚱그리거나 가짜 크레딧으로 채우지 않는다.

## 11. Credits 출처/라이선스 감사와 출시 전 확인

| 대상 | 실제 확인 근거 | 확인한 사실 / 권리 표기 | 상태 |
|---|---|---|---|
| Unreal Engine 5.8 | RecordShop.uproject, Epic 공식 EULA §1/§7(a) | 엔진 제공자 Epic Games, Inc.; Engine/Examples/Starter Content 범주와 credits 고지 요구 확인 | 원문 고지 삽입/해당 계약 적용 확인 IMPLEMENTATION_REQUIRED / MANUAL_REVIEW |
| NanumGothic | ArtSource/Fonts와 Content/RecordShop/Licenses의 실제 license, UI font assets | Copyright (c) 2010 NHN Corporation, SIL Open Font License1.1. 디자이너 이름은 별도 추측하지 않음 | 확인됨; Credits 표기와 license 전문 배포 확인 필요 |
| RS001~003 음악 | ArtSource/Audio/Music/compose_music.py | 로컬 합성 original arrangement, 외부 다운로드/샘플/곡 참조 없음이라는 제작 source 확인 | 제작 근거 확인; 표기 문구 CONTENT_LOCK_REVIEW |
| RS004~006 음악 | compose_expansion.py, expansion-audio-provenance.json | 전체 note/rhythm/timbre 로컬 합성, 외부 샘플 없음 | 제작 근거 확인; 별도 상업 음원 라이선스로 표시하지 않음 |
| RS004~006 Cover | Covers/README.md, provenance.json, generate_covers.py | 코드 기반 original vector, 외부 이미지/폰트/참조 없음; author 기록 OpenAI Codex for RecordShop | 제작 근거 확인; 표기 문구 CONTENT_LOCK_REVIEW |
| Cigar_room namespace | 현재 mesh import 기록/프로젝트 vendor namespace | 두 mesh FBX 파일명만 확인. 제작자/배포 페이지/적용 license 없음 | CREDIT_VERIFICATION_REQUIRED |
| Fab/Vintage_Stereo_Hi-Fi_Stack_w__Speakers | 현재 Content 경로와 기존 production dependency 근거 | namespace/사용 흔적은 있으나 제작자·정확한 상품 페이지·취득 license 증빙 없음 | CREDIT_VERIFICATION_REQUIRED |
| ShopOwner/Customer01 모델·Talking/Sending Fax animation | 현재 import 기록, ShopOwner README/source-manifest, PR14 | FBX 파일명과 contributor 작업은 확인. upstream 제작자·다운로드 페이지·원본 license는 미확정 | CREDIT_VERIFICATION_REQUIRED |
| MM/MF 계열 animation 등 | 현재 import filename/asset paths | 파일명만으로 원본 배포처/프로젝트 또는 license를 단정할 수 없음 | CREDIT_VERIFICATION_REQUIRED |

근거:
- [글꼴 license 전문](../../Content/RecordShop/Licenses/NanumGothic_License.txt), [DefaultGame.ini](../../Config/DefaultGame.ini): 현재 RecordShop/Licenses를 NonUFS로 stage하는 설정은 이미 있다. 실제 packaged 배포물에 notice/전문이 포함되는지는 아직 검증하지 않았다.
- [Epic 공식 EULA](https://www.unrealengine.com/eula/unreal): credits가 있으면 §7(a)의 두 고지 원문을 제품명/해당 연도로 치환해 포함할 계획이다. 짧은 “엔진 — Unreal Engine” 한 줄로 대체하지 않는다. 전문 문구 삽입은 원문 대조 후 진행한다. §1은 Fab 등 별도 배포 콘텐츠를 엔진 license 범주와 구분하므로 Fab license를 이 EULA로 대체해 확정하지 않는다.
- [Audio 제작 source](../../ArtSource/Audio/Music/compose_music.py), [확장 음악 provenance](../../ArtSource/Audio/Music/expansion-audio-provenance.json), [Cover source 설명](../../ArtSource/Records/Covers/README.md), [Cover provenance](../../ArtSource/Records/Covers/provenance.json).
- [ShopOwner source 설명](../../ArtSource/Characters/ShopOwner/README.md), [source manifest](../../ArtSource/Characters/ShopOwner/source-manifest.json), [실제 PR14](https://github.com/jllgame00/GameEngine-TermProject/pull/14): contributor 계정 laneve471과 작업 범위는 확인되지만 upstream 권리 증명은 아니다.

위 표는 전체 외부 권리를 확인했다는 선언이 아니다. Sending Fax/Talking/리그 이름으로 Mixamo 등 공급자를 추정하거나 제작자·URL·CC/MIT/Fab Standard/UE-only license를 임의 채우지 않는다. 제작 도구 NumPy/SciPy/FFmpeg/Matplotlib 사용과 배포물에 해당 도구가 포함되는지는 구분한다.

**출시 전 별도 확인 목록**

1. 각 vendor/모델/animation의 실제 상품/원본 URL, 제작자 또는 권리자, 취득 시 적용 license, 증빙을 확보한다.
2. 실제 packaged dependency와 크레딧 대상을 대조하고 필요한 정확한 고지/전문을 포함한다.
3. Nanum 고지/OFL 전문과 Engine/실제 배포 third-party notices가 packaged 결과에 남는지 확인한다.
4. CREDIT_VERIFICATION_REQUIRED 항목은 미확정 표시를 그대로 출시 크레딧으로 보내지 않는다. 검증/대체/사용 제외를 결정하기 전 release sign-off를 완료하지 않는다.
5. 이번 문구/설계 Gate는 권리·라이선스 출시 적합성을 최종 승인하지 않는다.

## 12. Title / New Game 설계

**APPROVED_DESIGN:** Credits 이후 Title, Title에서 New Game. **IMPLEMENTATION_REQUIRED:** 현재 Title UI/route는 없다.

현재 DefaultEngine.ini의 GameDefaultMap은 가게 맵이며, GFM BeginPlay 초기화 뒤 BeginPrologue로 바로 간다. 현재 UI registry에는 RecordSelect/Dialogue/Prologue/Result/Turntable/Touch UI만 있다. 문자열 검색에서 잡힌 SendingFax는 Ending 자산이 아니다. 기존 fresh-world History reset 테스트도 shipped New Game 버튼을 구현했다는 뜻이 아니다.

최소안은 **새 map 없이 같은 Shop 맵에 WBP_Title을 표시**하는 것이다.

- 최초 map boot: 기존 GFM 참조/이벤트 초기화는 유지하고 BeginPrologue 직접 호출 대신 Title 진입으로 gate한다. Tutorial spawn/Day1 시작은 아직 하지 않는다.
- Title: UI-only/cursor/focus는 “새 게임”. Continue/SaveGame은 추가하지 않는다.
- New Game: phase=Title에서 한 번만 수락 → 버튼 잠금/Title 제거 → phase=Playing → 기존 BeginPrologue. Prologue/Tutorial 내용과 Day 진입 조건은 그대로다.
- Credits Return: 오디오 정리 완료 뒤 기존 Shop map을 한 번 OpenLevel하여 새 world/GFM/actors를 만든다. 새 world는 다시 Title에서 시작한다.
- 기존 세션에서 ResetRecommendationHistory만 호출하며 CurrentDay/Queue/Tutorial을 억지로 되돌리는 in-place reset은 사용하지 않는다.
- 새 GFM/Title는 Day0, 초기 Queue/ActiveVisit/ActiveCustomer, History0, TutorialComplete=false, PrologueStage 초기값, Result/Dialogue context 없음, Turntable.HasRecord=false, BGM request/ID/sound/ref 없음 상태여야 한다.
- 새 persistent GameInstance에 History/선택 LP를 옮기지 않는다. 새 게임을 눌렀을 때 음악/다음 고객/timer/기억이 이전 실행에서 이어지지 않아야 한다.

WBP_Prologue의 시각 패턴은 참고하되 기존 Continue/AdvancePrologue binding을 Ending/Title에 재사용하지 않는다. 새 Title gate는 후속 regression의 새 진입 단계이며 자동 테스트도 “Title → New Game → 기존 opening”으로 갱신해야 한다.

## 13. 실제 적용 대상 Asset 계획

I/J 데이터6개·Day07·optional Result schema/UI는 이번 Production Gate 대상이다. 아래 Final/Audio/Title 흐름과 신규 Ending/Title UI는 다음 Gate의 **IMPLEMENTATION_REQUIRED**다. 실제 변경 목록은 Production 보고서를 따른다.

| 작업 | 경로 / 대상 |
|---|---|
| 신규 본문 DataTable2개 | /Game/RecordShop/Data/Narrative/DT_I_Dialogue, DT_J_Dialogue |
| 신규 Narrative2개 | /Game/RecordShop/Data/Narrative/DA_I1_Narrative, DA_J1_Narrative |
| 신규 Visit2개 | /Game/RecordShop/Data/Schedule/DA_Visit_I_1, DA_Visit_J_1 |
| Schedule 수정 | /Game/RecordShop/Data/Schedule/DA_Day07 의 Visits 참조2개. DA_TemporaryWeek와 Day01~06은 원칙적으로 그대로 |
| Result optional text schema | /Game/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition — empty-default FText4개 |
| Result 표시 수정 | /Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback — 기존 grade/neutral fallback 유지, data-driven 원문/퇴장 반응 |
| Final/Audio/Title 흐름 | /Game/RecordShop/Core/Flow/BP_GameFlowManager — presentation phase, 마지막 Day ownership, UI 진입/cleanup/boot Title |
| 신규 UI2개 | /Game/RecordShop/UI/Ending/WBP_Ending, /Game/RecordShop/UI/Title/WBP_Title (예정 경로) |
| 재사용 | 현재 Shop map/폰트/6 LP/catalogue/DialogueManager/기존 customer presentation |
| 원칙적 변경 불필요 | BP_Turntable, /Game/CustomerDialogue, A~H Dialogue, RS001~006 metadata/Audio/Cover, Day01~06 data |

WBP_Ending 한 개에 연락/답장/완료/Credits phases를 넣어 별도 Credits manager/widget asset을 필수로 만들지 않는다. 세부 authoring/validation script 작업은 [구현 계획](Day7EndingImplementationPlan.md)에 정리한다. 정확한 변경 manifest는 실제 구현 시작 전 현재 baseline과 다시 대조한다.

## 14. History와 중복 안전성

- History는 현재 recommendation authority만 저장한다. I/J 각각 한 건, scheduled16, Tutorial 제외.
- 새 문구/Result 반응/퇴장/부모님 연락/Credits는 History를 쓰지 않는다.
- Ending은 Score/Result 합산·BEST 수·고객 성공 상태를 읽지 않는다. All BEST/All POOR여도 같은 내용이다.
- J1 RecordID는 마지막 BGM 검증/lookup에만 쓰며 grade를 이유로 음악을 바꾸지 않는다. Runtime cache와 catalogue resolve를 동일 GFM이 소유한다.
- FinalStoryEventTriggered는 hook 발생 사실, presentation phase는 UI 전달/완료 진행을 구분한다. 같은 hook이 두 번 와도 text/UI/audio/credits가 새로 시작되지 않는다.
- Credits/Title Return과 New Game에는 phase guard를 먼저 세워 double-click/keypress repeat에 한 번만 반응한다.
- abort/back/예상치 못한 UI 제거에서 gameplay를 다시 열지 않는다. 중앙 Return-to-Title cleanup을 통해서만 종료한다. 최소안에 새 skip 시스템은 추가하지 않는다.
- 자연 EOF는 새 component로 반복할 수 있다. “같은 component가 끝까지 살아야 한다”는 잘못된 검사 대신 source/RecordID/voice count와 실제 natural completion을 관찰한다.

## 15. MANUAL_REVIEW와 아직 미구현인 것

- I/J 원문은 CONTENT_LOCK 승인 완료. 실제 줄바꿈·가독성·한국어 말맛은 MANUAL_REVIEW를 유지한다. Ending UI/출처 표시의 세부 문구는 별도 검토 대상이다.
- I/J body/result/exit와 TEMP 교체는 이번 Gate 대상이다. Ending/Title/Credits와 Day7 오디오 예외는 계속 미구현이며 IMPLEMENTATION_REQUIRED다.
- 이전 설계 Gate의 Editor 감사는 data/graph 조회였다. 이번 실제 구현의 compile/runtime/7일 회귀/Cook 결과는 Production 보고서에만 근거와 함께 기록하며 packaged PASS와 구분한다.
- 실제 3-card readability, I→J profile/context leak, Result 직전/직후 대사 타이밍, 기존 placeholder 외형의 나이 표현 한계 확인.
- 마지막 LP가 RS003처럼 Restless Electronic이어도 같은 Ending이 성립하는지, Dialogue/Completion/Credits 동안 volume/fade/반복 경계/피로도 청취.
- 실제 mouse/gamepad, focus/cursor, 긴 대기/자연 EOF 여러 번, 빠른 Continue/Return/New Game, abort/Title audio0/새 History0 확인.
- Credits에 실제 확정 이름/역할이 정확히 보이고 required notices가 누락되지 않는지, 미검증 외부 항목이 출시용 placeholder로 남지 않는지 확인.
- 기존 permission warning은 보존하고 이번에 repo/라이선스 설정을 광범위하게 변경하지 않는다.

## 16. 다음 검토와 이전 설계 Gate 변경 이력

**이미 결정된 것을 다시 승인 요청하지 않는다:** I/J의 나이대/방문 이유/profile/BEST/단발 구조, A 채택/B·C 제외, 단일 Ending, Credits→Title→New Game, 마지막 LP 유지 방향, 팀원6명은 APPROVED_DESIGN이다.

I/J 원문·같은 Result panel의 퇴장 반응 표시는 후속 사용자 승인으로 확정했다. 다음 검토 대상은 Ending UI 세부 문구와 Credits의 표시 구성/출처 문구다. 외부 CREDIT_VERIFICATION_REQUIRED 자료는 별도의 출시 전 근거 확인 대상으로 남는다. 이 문구들을 아직 최종 승인된 Content Lock이라고 표시하지 않는다.

이전 설계 Gate에서 수정/생성한 deliverable은 이 문서와 Day7EndingImplementationPlan.md뿐이었다. Saved의 read-only 감사 script/result/log는 검증 근거이며 Production 콘텐츠가 아니다. Production .uasset/.umap, Blueprint, DataTable, Schedule, Audio, UI asset과 기존 authoring script/config는 수정하지 않는다. staging/commit/push도 하지 않는다.

### 이전 설계 Gate 비변경 확인

시작/종료 SHA 집계에서 Content 파일550개, ArtSource65개, 기존 Scripts96개, Config5개와 이 두 문서 외 기존 Docs33개의 digest가 동일했다. Branch/HEAD도 동일하고 staged 파일은 없다. Git에서 나타나는 deliverable은 기존 ContentPlan 갱신과 새 ImplementationPlan 두 문서뿐이며 Saved에는 read-only 감사 근거만 남겼다. 기존 접근 불가 임시 폴더 warning은 별도로 보존한다.

문서의 16개 콘텐츠 절/8개 구현 계획 절, 본문8행, 현행6LP의 I/J 점수, 로컬 근거 링크를 확인했다. 독립 계획 검토의 무음 Return/복귀 중 timer 경계 보완 후 남은 중대 설계 모순은 없었다. 이전 설계 Gate 종료 당시 원문 승인과 구현은 남아 있었다. 후속 I/J 원문은 CONTENT_LOCK 승인됐으며 실제 구현·runtime 결과는 새 Production 보고서에 기록한다. Ending 후속 구현, packaged 검증과 미확정 외부 권리 확인은 계속 남아 있다.
