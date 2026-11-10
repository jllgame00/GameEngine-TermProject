# Customer E/F/G/H Narrative Production Gate

**최종: 20/20 성공 근거 확인, RS002 strict retry 포함. 초회 aggregate 실패와 manual 제한은 아래에 명시한다.**

## 1. 시작 branch / HEAD / status

Branch **feature/customer-narrative-content**, HEAD **9a7d8813f37d0558c0bcb7510220dd36e3fa6424**, 시작 worktree clean. 현재 branch를 유지했다. 새 branch, staging, commit, push는 수행하지 않았다.

READ-ONLY Editor audit **Saved/MVPCompletion/20261110T020234Z-customer-efgh-audit-process.json** PASS. 시작 상태와 기존 Content 536개 SHA256은 **Saved/MVPCompletion/customer-efgh-start-state.json**에 보존했다. E/F/G/H Visit은 각각 한 건이며 Narrative=None, CustomerClass=C01, IsPlaceholderContent=True였다. A/B/C/D Narrative, sequence/profile override, catalogue, schedule, history, neutral Result graph를 확인한 뒤 데이터만 추가했다.

## 2. E final interpretation + 실제 Dialogue

20대 카페 직원. 교대 후 친구를 기다리는 짧은 시간을 편하게 보내려는 손님이다. 직업을 Jazz 취향의 원인으로 쓰지 않고 작은 합주와 악기 사이의 대화를 직접 말한다. 과한 명랑함이나 추가 관계 이야기는 없다. **E appearance = PLACEHOLDER**. Speaker: 카페 직원 손님.

| Row | Dialogue |
|---|---|
| E1_Current_01 | 카페 교대가 끝났어요. 친구를 만나기까지 시간이 좀 남아서 잠깐 들렀어요. |
| E1_Current_02 | 잠깐 쉬면서 듣고 싶어요. 대화나 생각을 덮지 않을 만큼 작은 소리면 좋겠어요. |
| E1_Current_03 | 작은 재즈 합주를 좋아해요. 악기끼리 말을 주고받듯 리듬이 자연스럽게 이어지는 곡이요. |
| E1_Current_04 | 혼자 깊이 잠기기보다는, 누군가를 기다리며 편하게 들을 음반을 골라 주시겠어요? |

## 3. F final interpretation + 실제 Dialogue

대학생. 우산 없이 비를 만나 버스 한 대를 더 기다리는 상황을 짧은 소리 탐색으로 바꾼다. 비를 우울함과 연결하지 않는다. 반복 리듬, 신스/전자음, 낯선 질감에 대한 호기심으로 세 취향을 표현한다. **F appearance = PLACEHOLDER**. Speaker: 대학생 손님.

| Row | Dialogue |
|---|---|
| F1_Current_01 | 수업 끝나고 나왔는데 비가 오네요. 우산도 없고, 버스 한 대 더 기다리는 동안 구경하려고요. |
| F1_Current_02 | 가만히 가라앉는 곡보다는 반복되는 리듬에 몸이 조금 움직이는 곡을 듣고 싶어요. |
| F1_Current_03 | 신스나 전자음으로 만든 낯선 질감이 궁금해요. 평소 안 듣던 소리도 들어보고 싶고요. |
| F1_Current_04 | 기다리는 동안 짧게 탐색해 볼 만한 음반이 있을까요? 익숙하지 않은 소리여도 괜찮아요. |

## 4. G final interpretation + 실제 Dialogue

40대 수리 기사. 외근 후 멀리 있는 친구에게 엽서를 쓰는 동안 들을 음악만 요청한다. 직업/친구의 사연, 엽서 UI/발송, 퀘스트를 확장하지 않는다. 작은 소리, 어쿠스틱 현과 담백한 목소리, 누군가에게 말 거는 분위기가 단서다. **G appearance = PLACEHOLDER**. Speaker: 수리 기사 손님.

| Row | Dialogue |
|---|---|
| G1_Current_01 | 수리 외근을 마치고 왔어요. 멀리 사는 친구에게 엽서 한 장 쓰면서 들을 음악을 찾고 있어요. |
| G1_Current_02 | 글 쓰는 흐름을 방해하지 않을 만큼 소리가 작고 차분했으면 해요. |
| G1_Current_03 | 어쿠스틱 기타 줄을 손으로 튕기는 소리나 담백한 목소리가 좋아요. 포크 음반 쪽을 보고 싶어요. |
| G1_Current_04 | 혼자 멀어지는 느낌보다는 누군가에게 말을 건네는 듯했으면 해요. 그런 음반 하나 골라 주실래요? |

## 5. H final interpretation + 실제 Dialogue

60대 동네 손님. 낱말퍼즐 마지막 한 칸을 잠시 내려놓고 듣는 시간을 원한다. 나이를 Classical 취향의 이유로 사용하지 않는다. 피아노/현과 긴 호흡, 고요한 여백, 혼자 생각할 공간을 직접 요청한다. 퍼즐 정답/미니게임/보상은 없다. **H appearance = PLACEHOLDER**. Speaker: 동네 손님.

| Row | Dialogue |
|---|---|
| H1_Current_01 | 신문 낱말퍼즐이 한 칸 남았어요. 답을 억지로 찾기보다 잠깐 앉아서 음악을 듣고 싶네요. |
| H1_Current_02 | 소리가 서두르지 않고, 중간중간 조용한 여백이 있으면 좋겠어요. |
| H1_Current_03 | 클래식 중에서도 피아노나 현이 긴 호흡으로 천천히 이어지는 곡을 좋아해요. |
| H1_Current_04 | 혼자 생각할 자리가 남는 음악이면 좋겠어요. 바로 결론을 내리지 않아도 되는 음반을 부탁해요. |

## 6. Profile / tag mapping

| ID | Visit | Day / Order | Mood | MusicPreference | Personality |
|---|---:|---|---|---|---|
| E | 1 | 1 / 2 | Quiet | Jazz | Sociable |
| F | 1 | 3 / 2 | Restless | Electronic | Adventurous |
| G | 1 | 5 / 2 | Quiet | Folk | Sociable |
| H | 1 | 6 / 3 | Quiet | Classical | Reflective |

기존 TargetMoodOverride / TargetGenreOverride / TargetThemeOverride → ApplyVisitProfileOverrides → active customer profile copy → DM CurrentCustomer/CurrentMood 경로를 사용한다. 실제 CalculateLPScore는 Mood/Genre/Theme와 Mood/MusicPreference/Personality의 정확한 문자열 일치를 각 1점으로 계산한다. Class default는 변경하지 않는다. Production queue는 매 Visit 새 actor를 생성한다.

## 7. Result reaction contract

고객별 전용 반응 대사는 추가하지 않고 기존 UsesVisitProfileOverrides / PreferenceAwareFeedback의 중립 반응을 그대로 사용한다. 요청의 선택 사항인 전용 문구를 생략하고 공유 graph와 기존 A/B/C/D 반응을 보존하는 결정이다. 결과는 현재 음악 적합도만 표현하며 인생 문제 해결, 성장, 다음 방문, 관계 결과를 만들지 않는다.

| Result | Score | ScoreStatus |
|---|---|---|
| BEST | 3 | 최고의 선택  \|  취향 3 / 3 일치<br>이번 방문에서 손님이 말한 세 가지 취향에 모두 맞는 추천입니다. |
| GOOD | 2 | 좋은 선택  \|  취향 2 / 3 일치<br>이번 방문의 취향과 대체로 맞는 추천입니다.<br>원하는 느낌을 조금 더 이야기해 볼 수 있겠습니다. |
| POOR | 0~1 | 아쉬운 선택  \|  취향 0~1 / 3 일치<br>이번 방문에서 찾던 느낌과는 다소 거리가 있는 추천입니다.<br>손님이 말한 단서를 다시 떠올려 보세요. |

Unavailable fallback과 Continue 동작도 기존 authority를 유지한다. G/H의 BEST, H의 GOOD 검증은 Result widget 입력 fixture로만 수행하며 실제 점수/History/Record를 위조하지 않는다.

## 8. Sequence architecture

| SequenceID | Source | OrderedRows | Memory |
|---|---|---|---|
| E_V1 | DT_E_Dialogue | E1_Current_01~04 | none |
| F_V1 | DT_F_Dialogue | F1_Current_01~04 | none |
| G_V1 | DT_G_Dialogue | G1_Current_01~04 | none |
| H_V1 | DT_H_Dialogue | H1_Current_01~04 | none |

기존 BP_VisitNarrativeDefinition 네 인스턴스와 기존 Visit의 Narrative 참조만 추가한다. 총 16행, FText namespace CustomerE/F/G/H + row_field key. ReviewStatus=READY, ContentVersion=1은 narrative 데이터의 상태이며 3D 외형 완료를 뜻하지 않는다. MemoryVisitNumbers와 모든 memory intro/outro/earlier 배열은 비어 있고 RequireAllMemories=False, EarlierMemoryVisitNumber=0이다. CandidateRecordIDs=[]는 공유 catalogue의 기본 RS001/2/3으로 resolve한다.

기존 pending consume-once / source snapshot / same-source Next / finish·cancel clear / legacy fallback을 재사용한다. Mood-only CustomerDialogue에 행을 append하지 않는다. 단발 Visit1에 same-visit/foreign/future/unknown History가 있어도 previous memory를 만들지 않는다.

## 9. 정확한 변경 파일

29 files:

- `Content/RecordShop/Data/Narrative/DA_E1_Narrative.uasset`
- `Content/RecordShop/Data/Narrative/DA_F1_Narrative.uasset`
- `Content/RecordShop/Data/Narrative/DA_G1_Narrative.uasset`
- `Content/RecordShop/Data/Narrative/DA_H1_Narrative.uasset`
- `Content/RecordShop/Data/Narrative/DT_E_Dialogue.uasset`
- `Content/RecordShop/Data/Narrative/DT_F_Dialogue.uasset`
- `Content/RecordShop/Data/Narrative/DT_G_Dialogue.uasset`
- `Content/RecordShop/Data/Narrative/DT_H_Dialogue.uasset`
- `Content/RecordShop/Data/Schedule/DA_Visit_E_1.uasset`
- `Content/RecordShop/Data/Schedule/DA_Visit_F_1.uasset`
- `Content/RecordShop/Data/Schedule/DA_Visit_G_1.uasset`
- `Content/RecordShop/Data/Schedule/DA_Visit_H_1.uasset`
- `Docs/Architecture/CustomerEFGHNarrativePlan.md`
- `Docs/Architecture/CustomerEFGHNarrativeReport.md`
- `Scripts/Unreal/cook_mvp.py`
- `Scripts/Unreal/customer_b_validation_support.py`
- `Scripts/Unreal/customer_efgh_dialogue.json`
- `Scripts/Unreal/customer_efgh_reference_baseline.json`
- `Scripts/Unreal/customer_efgh_validation_support.py`
- `Scripts/Unreal/install_customer_efgh_narrative.py`
- `Scripts/Unreal/run_customer_efgh_gate.py`
- `Scripts/Unreal/validate_customer_b_contract.py`
- `Scripts/Unreal/validate_customer_b_sequences.py`
- `Scripts/Unreal/validate_customer_cd_contract.py`
- `Scripts/Unreal/validate_customer_cd_sequences.py`
- `Scripts/Unreal/validate_customer_efgh_contract.py`
- `Scripts/Unreal/validate_customer_efgh_sequences.py`
- `Scripts/Unreal/validate_day_week.py`
- `Scripts/Unreal/validate_narrative_contract.py`

모든 uasset 변경은 AssetTools / DataTableFunctionLibrary / EditorAssetLibrary로 수행했다. raw byte edit는 없다. 기존 공유 graph, A/B/C/D/Tutorial 자산, catalogue/RS001~3, class default, map, audio/input/turntable은 보호 해시로 검사한다.

## 10. E/F validation

Fresh contract 20261110T020910Z, runtime matrix 20261110T020948Z PASS. 각 고객별 empty / same-visit / foreign / future / unknown History 5사례에서 정확한 speaker·문장·순서 4행을 실제 GFM/DM이 출력했다. previous memory와 NarrativeMemoryVisits는 비어 있고 Dialogue가 History를 변경하지 않았다.

E 실제 HandleRecordSelected → EvaluateRecordScore / CalculateLPScore / ClassifyRecommendationScore 결과는 RS001=2 GOOD, RS002=3 BEST, RS003=0 POOR. F는 0 POOR / 0 POOR / 3 BEST다. 후보는 공유 RS001/2/3이며 selection 단계에 History를 남기지 않는다.

각 고객에 실제 Result widget으로 score0/1/2/3 및 unavailable 입력을 검사했다. duplicate Start/late Next가 중복 line/finish를 만들지 않고 pending·active 취소와 정상 완료가 source/rows/ID를 정리했다. F→D→E→A→legacy 전환의 profile/sequence 격리와 C01 class default 불변을 확인했다.

## 11. G/H validation

동일한 fresh matrix에서 G/H 각 5개 History fixture 사례 PASS. G 실제 score vector는 1/2/0, H는 1/1/0. 12개 실제 LP 선택 경로 모두 예상 score/result와 일치했다. 현재 후보에서 G 최대 GOOD, H 최대 POOR이며 runtime BEST를 생성하지 않는다.

BEST 및 H GOOD의 반응 branch는 Result widget SetRawScoreDisplay 입력에만 grade를 주입해 검증했다. catalogue에 Record를 추가하거나 추천 score/history를 바꾼 검증이 아니다. 단발 고객의 정상 완료·취소·중복 호출, no-memory, exact text/profile, 다음 고객 격리 계약은 E/F와 동일하게 PASS.

## 12. A/B/C/D regression

Fresh C/D contract + matrix22, B contract + matrix24, A contract + matrix23 PASS. 모두 이번 실행에서 생성한 결과다. A Visit1/2/3, B Visit1/2/3, C Visit1/2, D Visit1/2의 기존 대사/기억 분기/실제 profile과 score를 유지했다.

A1 원본 CustomerDialogue package SHA256: 872dbd16f39cbc4b61da81dbd9dfa6bcbc0ad4dd9379136300894d0850f3eed5. A1 row hash: 7bfa933b1b612309e476b6ceaaa155ec1fc36a9419c98debbc715534e7f5a363. 공유 graph와 기존 production narrative/record/UI 자산은 532개 보호 목록에 포함되어 byte-identical이다.

B/CD의 following legacy fixture만 E에서 TEMP_D7_01_1로 변경했다. E는 이제 explicit sequence를 가지므로 기존 legacy 회귀를 실제 남아 있는 placeholder로 계속 검증하기 위한 갱신이다. Day7 Narrative 자체는 추가하지 않았다.

## 13. Full Day / History regression

주간 검증 20261110T022455Z-narrative-week.json / process.json PASS. Tutorial=TUTORIAL 1회 + scheduled visits16 = 서로 다른 customer actor 17개 cycle. Day1~7 시작/종료 각 1회, FinalStoryEvent Hook 1회. Day7 기존 TEMP placeholder 두 건은 보존하고 Narrative를 추가하지 않았다.

검증한 큐: Day1 A1/E1, Day2 B1/C1, Day3 A2/F1/D1, Day4 B2/C2, Day5 A3/G1, Day6 B3/D2/H1, Day7 TEMP_D7_01/TEMP_D7_02.

History16, stable CustomerID/VisitNumber/Day/Sequence 일치, 각 E/F/G/H 정확히 한 건, 이전 기억 없음. Duplicate HandleTurntableCompleted/CommitRecommendationHistory 및 active reset 거부, copied query isolation, selection 시 미기록, 새 New Game History empty까지 PASS.

| ID | Day | Visit | Record | Score / Result | History Sequence |
|---|---:|---:|---|---|---:|
| E | 1 | 1 | RS002 | 3 / BEST | 2 |
| F | 3 | 1 | RS003 | 3 / BEST | 6 |
| G | 5 | 1 | RS002 | 2 / GOOD | 11 |
| H | 6 | 1 | RS001 | 1 / POOR | 14 |

F 다음 실제 D1의 Quiet/Classical/Reflective 복원, 명시적 dialogue routing/context clear, canonical shelf UI→SelectedRecord→Turntable 전달, 실제 listening/Result, Store BGM, camera/input/cursor/focus 복귀를 주간 내내 검사했다. A1 실제 표시 대사 hash c7e2623244f103ed721207ac59e01a66747b6578b80f05e442353aed55a59070도 유지했다.

Production map dependency closure332 packages, Blueprint28개 compile PASS / missing0 / redirectors0. Core/native/audio/cook 최종 결과는 아래 표에 기록한다.

최종 근거 Saved/MVPCompletion/customer-efgh-final-evidence.json: **20/20 atomic groups PASS (RS002 strict 재실행 포함)**. 초회 aggregate 20261110T020910Z-customer-efgh-gate.json 자체는 FAIL이며 덮어쓰지 않았다. 실패는 20261110T023627Z-narrative-rs002.json의 Player visibly snapped during alignment 한 건이었다.

실패 시 Walking/84cm/s, 관측 간 이동21.54cm, 기록된 sample interval0이었고 같은 정렬 경로의 RS001/RS003은 PASS였다. 프레임 타이밍에 따른 간헐적 실패 가능성은 남아 있다. Production 자산, validation 코드, 15cm 기준을 바꾸지 않고 동일한 native RS002/45RPM/front 조건으로 재실행했다. 20261110T024319Z-narrative-rs002.json은 PASS, 최대 관측 이동1.850cm/25 samples였다. 원본 실패와 retry command/host/result를 모두 보존했다.

기존 run_narrative_gate의 성공 report 재사용 기능으로 나머지 11개 Core 결과와 strict retry를 묶은 20261110T024319Z-narrative-gate.json은 12/12 PASS다. 최종 evidence collector는 이 Core와 같은 작업 상태에서 성공한 E/F/G/H·C/D·B·A 각 contract/matrix 8개를 다시 확인해 20개 성공 근거를 결합했다. 초회 aggregate의 실패 flag를 PASS로 수정한 것이 아니다.

| Group | Result | Evidence |
|---|---|---|
| E/F/G/H/contract | PASS | [20261110T020910Z-customer-efgh-contract.json](../../Saved/MVPCompletion/20261110T020910Z-customer-efgh-contract.json) |
| E/F/G/H/matrix | PASS | [20261110T020948Z-customer-efgh-sequences.json](../../Saved/MVPCompletion/20261110T020948Z-customer-efgh-sequences.json) |
| C/D/contract | PASS | [20261110T021122Z-customer-cd-contract.json](../../Saved/MVPCompletion/20261110T021122Z-customer-cd-contract.json) |
| C/D/matrix | PASS | [20261110T021153Z-customer-cd-sequences.json](../../Saved/MVPCompletion/20261110T021153Z-customer-cd-sequences.json) |
| B/contract | PASS | [20261110T021310Z-customer-b-contract.json](../../Saved/MVPCompletion/20261110T021310Z-customer-b-contract.json) |
| B/matrix | PASS | [20261110T021341Z-customer-b-sequences.json](../../Saved/MVPCompletion/20261110T021341Z-customer-b-sequences.json) |
| A/contract | PASS | [20261110T021520Z-customer-a-contract.json](../../Saved/MVPCompletion/20261110T021520Z-customer-a-contract.json) |
| A/matrix | PASS | [20261110T021551Z-customer-a-sequences.json](../../Saved/MVPCompletion/20261110T021551Z-customer-a-sequences.json) |
| Core/editor | PASS | [20261110T021714Z-narrative-editor.json](../../Saved/MVPCompletion/20261110T021714Z-narrative-editor.json) |
| Core/sequence | PASS | [20261110T021813Z-narrative-sequence.json](../../Saved/MVPCompletion/20261110T021813Z-narrative-sequence.json) |
| Core/integration | PASS | [20261110T021904Z-narrative-integration.json](../../Saved/MVPCompletion/20261110T021904Z-narrative-integration.json) |
| Core/guards | PASS | [20261110T022126Z-narrative-guards.json](../../Saved/MVPCompletion/20261110T022126Z-narrative-guards.json) |
| Core/week | PASS | [20261110T022455Z-narrative-week.json](../../Saved/MVPCompletion/20261110T022455Z-narrative-week.json) |
| Core/rs001 | PASS | [20261110T023453Z-narrative-rs001.json](../../Saved/MVPCompletion/20261110T023453Z-narrative-rs001.json) |
| Core/rs003 | PASS | [20261110T023724Z-narrative-rs003.json](../../Saved/MVPCompletion/20261110T023724Z-narrative-rs003.json) |
| Core/isolated | PASS | [20261110T023854Z-narrative-isolated.json](../../Saved/MVPCompletion/20261110T023854Z-narrative-isolated.json) |
| Core/audio | PASS | [20261110T024040Z-narrative-audio.json](../../Saved/MVPCompletion/20261110T024040Z-narrative-audio.json) |
| Core/startup | PASS | [20261110T024150Z-narrative-startup.json](../../Saved/MVPCompletion/20261110T024150Z-narrative-startup.json) |
| Core/cook | PASS | [20261110T024213Z-cook-final.log](../../Saved/MVPCompletion/20261110T024213Z-cook-final.log) |
| Core/rs002 | PASS | [20261110T024319Z-narrative-rs002.json](../../Saved/MVPCompletion/20261110T024319Z-narrative-rs002.json) |

Bounded Windows loose cook 20261110T024213Z-cook-final-process.json PASS: production map, Result/Prologue/history, narrative foundation26 packages(신규 E/F/G/H8 포함), day7개/visit16개 확인. Cook errors0, missing/redirector/compile failure0. SkipSaveAssetRegistry smoke 범위이며 packaging/staging/executable은 실행하지 않았다.

RS001/2/3 native 조작과 33/45/78RPM, SelectedRecord canonical flow, turntable full-arm/contact, Listening→Result, Store BGM, camera/input/cursor/focus 회복을 검사했다. Audio/isolated/startup도 PASS. Host Python unit tests11 PASS, 변경 Python13개 AST parse PASS.

최종 원본 Content536개 중532개 SHA가 그대로이며 기존 자산 변경은 E/F/G/H Visit의 Narrative 참조4개뿐이다. 신규 Content8개는 대사4개/정의4개다. 총 변경29파일, branch/HEAD 유지, staged0. staging/commit/push 없음.

## 14. Catalogue limitation

| Customer | RS001 | RS002 | RS003 | 현재 최고 |
|---|---|---|---|---|
| E | 2 GOOD | 3 BEST | 0 POOR | BEST, RS002 |
| F | 0 POOR | 0 POOR | 3 BEST | BEST, RS003 |
| G | 1 POOR | 2 GOOD | 0 POOR | GOOD, RS002 |
| H | 1 POOR | 1 POOR | 0 POOR | POOR |

**Known Limitation: G/H에게 현재 BEST가 없다.** G의 향후 RS005(Quiet/Folk/Sociable), H의 향후 RS006(Quiet/Classical/Reflective)은 콘텐츠 계획일 뿐이다. 이번 Gate에서 RS004/5/6 실제 Record, Audio, Cover 또는 가짜 production 후보를 추가하지 않았다. 자동 테스트의 grade fixture와 현재 catalogue의 실제 결과를 구분한다.

## 15. Known limitations

- E/F/G/H appearance = PLACEHOLDER. 기존 C01 mesh/animation과 class-default 이름/VisitReason presentation을 재사용한다. 대사 speaker와 runtime ID/profile은 고객별 데이터이며 외형 제작 완료를 주장하지 않는다.
- 고객별 전용 Result 문구 대신 기존 중립 반응을 적용한다.
- 단발 고객에 revisit/history branch/previous memory/다음 방문 암시는 없다. History에는 실제 추천 결과 한 건만 남긴다.
- 주간 자동화의 player 접근 위치와 virtual Slate activation은 fixture다. Production navigation/queue/recommendation/history/audio 흐름과 구분한다.
- 초회 RS002 native alignment 검사가21.54cm 이동으로 한 번 실패했다. 동일 strict 재실행은1.850cm로 PASS했지만 낮은 FPS/관측 타이밍의 간헐적 continuity 위험은 manual review에 남긴다. 원본 실패를 보존했다.
- 실제 gamepad 하드웨어 및 packaged executable은 미검증이다. Bounded loose cook는 packaging/staging/executable 검증이 아니다.
- 엔진 pre-init의 기존 UnifiedError smoke signature는 strict log classifier가 별도로 분류한다. 이를 globally error-free와 혼동하지 않으며 예상하지 않은 runtime error는 허용하지 않는다.

## 16. MANUAL REVIEW

| 항목 | 검토 / 남은 확인 |
|---|---|
| E stereotype / 취향 | 직업은 입장 상황 1행에 한정. 합주·악기 대화·작은 소리·편한 기다림으로 취향 제시. 과한 명랑함 없음. |
| F caricature / 비=우울 / Electronic | 수업·버스 상황만 사용. 우울한 감정 부여 없음. 반복 리듬·신스·전자음·새 질감이 음악 요청과 연결됨. |
| G 설명량 / Folk·Sociable | 직업·엽서는 첫 행에서 끝냄. 어쿠스틱 현·담백한 목소리와 누군가에게 말 건네는 느낌을 각각 제시. |
| H 나이=Classical / 퍼즐 | 나이 언급 없이 실제 악기·흐름 선호를 말함. 퍼즐은 쉬는 계기 1행이며 정답/보상 없음. |
| 한국어 / 줄바꿈 / UI | Agent visual inspection: 실제 대사 16장과 Result 4장 모두 확인. 1714×1386 Editor 캡처의 현재 viewport에서 대사는 각 2줄로 표시되며 글자 잘림·버튼 겹침 없음. 다른 해상도는 별도 확인 필요. |
| Listening pacing | 설정 10초 Listening의 실제 주간 E/F/G/H 측정은 E 11.161초, F 11.164초, G 11.182초, H 11.171초. 자동 timing/재생 종료/BGM 복귀 PASS. 주관적인 청취 길이·음악 감상은 human manual review 필요. |
| Gamepad focus | 자동화는 owning-user keyboard focus와 virtual Slate Enter를 검사. 실제 gamepad 하드웨어 manual review 필요. |
| Packaged executable | 실행하지 않음. 별도 Windows package smoke 필요. |

## 17. RS004~006 Content Phase 진입 가능 여부

**기술적으로 RS004~006 Content Phase의 선행 narrative/profile 조건을 충족했다.** E/F/G/H가 현재 catalogue 범위에서 정상 동작하고, A/B/C/D/Core의 성공 검증 근거가 확보됐다. G/H BEST 부재는 실제 RS005/6 콘텐츠로 해결할 다음 단계의 알려진 제한이다.

이번 작업은 해당 제작 단계에 진입하지 않는다. 정식 배포 판정 전에는 실제 gamepad, packaged executable, 주관적 Listening pacing, 낮은 FPS에서의 기존 player alignment 간헐 실패를 manual review해야 한다.

이번 작업은 E/F/G/H에서 종료한다. 합석 Event, Day7 Narrative, Ending, Relationship, 경제/재고, 신규 mesh, world expansion은 범위 밖이다.

## 18. 추천 commit plan

실제로 staging/commit/push하지 않았다. 사용자가 검토 후 선택적으로 나눌 수 있는 계획:

1. feat(narrative): add single-visit E F G H production content — 8개 신규 narrative/table uasset, 4개 Visit 참조, authoring JSON/installer.
2. test(narrative): validate single visits and preserve week regressions — contract/matrix/runner/reference hashes와 기존 regression/cook 갱신.
3. docs(narrative): record E F G H gate evidence and limitations — plan/report.

git add .를 사용하지 말고 최종 목록에서 필요한 파일만 개별 검토한다.

UI 검토 evidence: Saved/MVPCompletion/customer-efgh-ui-review.json. 원본 20장과 고객별 contact sheet를 보존했다: [E](../../Saved/MVPCompletion/customer-efgh-E-ui-review.png), [F](../../Saved/MVPCompletion/customer-efgh-F-ui-review.png), [G](../../Saved/MVPCompletion/customer-efgh-G-ui-review.png), [H](../../Saved/MVPCompletion/customer-efgh-H-ui-review.png).
