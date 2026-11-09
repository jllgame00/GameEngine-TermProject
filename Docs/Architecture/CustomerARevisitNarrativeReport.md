# Customer A Revisit Narrative Production Gate

## 1. 시작 branch / HEAD / status

- 경로: `D:/univ/3-1/GameEngine/Termproject/RecordShop`.
- Branch: `feature/customer-a-revisit-narrative`.
- HEAD: `3c73df226eda9d7b6bfe1ae27b5509dc5cf442b4`; 시작 worktree clean.
- READ-ONLY Editor 감사 / RED: `Saved/MVPCompletion/20261109T093855Z-customer-a-audit-red.json`.
- 최초 RED는 A2 Production Narrative 부재를 정확히 검출했다. 원본 A1은 별도 source로 복사하지 않았다.

## 2. A2 / A3 Narrative 구조

A2: V1 Result Intro 0~1행 + 공통 현재 상황/취향/요청 5행. NO_MEMORY는 회상을 생략하고 현재 상황으로 바로 간다.

A3: V2 Result Intro 1행 + V1 회상 1행 + 공통 현재 상황/취향 3행 + 짧은 payoff 1행. 9개 전체 대본을 만들지 않고 이 모듈들을 조합한다. V1/V2 중 하나라도 missing/unknown이면 neutral 1행 + 공통 3행 + 설명형 payoff 1행으로 간다.

가까운 젊은 지인과 대화가 어긋났다는 A2 상황, 다시 이야기할 평범한 약속이라는 A3 상황만 사용한다. 새 가족사/직업/상실/화해 성공/개과천선/Ending을 추가하지 않았다. Quiet/Jazz/Traditional을 유지한다.

## 3. 실제 작성 대사

아래 20행이 신규 Production text 전체다. A1 5행은 원본에서만 읽는다. Authoring source는 `Scripts/Unreal/customer_a_dialogue.json`, runtime source는 `DT_A_RevisitDialogue`다. 새 text는 `CustomerARevisit` localization namespace와 row/field 기반 key를 사용한다.

| Row | Dialogue |
|---|---|
| A2_Memory_BEST | 지난번 골라준 음반은 차분하고 익숙해서 좋았네. 그날 내 기분에는 잘 맞더군. |
| A2_Memory_GOOD | 지난번 것도 대체로 괜찮았네. 다만 내가 바라는 느낌을 조금 더 설명했어야겠더군. |
| A2_Memory_POOR | 지난 음반은 내가 원했던 느낌과는 좀 달랐네. 오늘은 조금 더 이야기해 보지. |
| A2_Current_01 | 며칠 전에 가까이 지내는 젊은 사람과 이야기를 했네. 말이 자꾸 어긋나는 것 같더군. |
| A2_Current_02 | 그 사람 얘기를 또 하려는 건 아니야. 다음에 무슨 말부터 할지, 잠깐 생각이나 정리하고 싶어서 왔네. |
| A2_Current_03 | 오늘은 말소리를 덮지 않을 만큼 차분한 소리면 좋겠네. |
| A2_Current_04 | 작은 재즈 합주처럼 익숙한 흐름 말이야. 너무 낯선 해석보다는 오래 듣던 형식이 편하더군. |
| A2_Current_05 | 그런 쪽으로 한 장 골라주게. |
| A3_Memory_BEST | 두 번째로 골라준 음반은 편하게 들었네. 차분하고 익숙한 느낌이 잘 맞더군. |
| A3_Memory_GOOD | 두 번째 음반도 대체로 괜찮았네. 그래도 내가 찾는 느낌을 좀 더 분명히 말할 필요는 있더군. |
| A3_Memory_POOR | 두 번째 음반은 내가 기대한 느낌과는 조금 달랐네. |
| A3_Memory_NEUTRAL | 오늘은 내가 편하게 듣는 소리를 좀 더 정확히 말해 보겠네. |
| A3_Earlier_BEST | 처음 골라준 음반의 편안한 느낌도 기억하네. 두 번을 떠올리니 내가 좋아하는 쪽이 좀 보이는군. |
| A3_Earlier_GOOD | 처음 것도 대체로 괜찮았지. 두 번을 떠올려 보니 내가 더 바라는 게 무엇인지 조금 알겠네. |
| A3_Earlier_POOR | 처음 것도 원했던 느낌과는 거리가 있었지. 두 번을 떠올리니 내 쪽에서도 설명을 더 해야겠더군. |
| A3_Current_01 | 조만간 아는 사람과 다시 이야기할 약속이 있네. 그 전에 여기서 잠깐 쉬었다 가려고. |
| A3_Current_02 | 소리가 빈틈없이 몰아치기보다는, 생각이 머물 여백이 있는 쪽이 좋겠네. |
| A3_Current_03 | 작은 재즈 합주가 익숙한 박자로 흘러가는 느낌 말이야. 색다른 해석보다 전통적인 흐름이 내겐 편하더군. |
| A3_Payoff_Aligned | 자네가 내 취향을 조금 알아가는 것 같군. 오늘도 그런 쪽으로 한 장 부탁하네. |
| A3_Payoff_Clarify | 내가 뭘 원하는지 이제는 좀 더 설명할 수 있겠군. 오늘은 그쪽으로 한 장 부탁하네. |

## 4. Result 분기 구조

- 기존 확정 RecommendationResult의 BEST/GOOD/POOR만 소비한다. 점수 계산/History 기록 시점은 바꾸지 않았다.
- GOOD를 보고 특정 Mood/Genre/Theme가 틀렸다고 단정하지 않는다.
- A3에서 둘 다 BEST 또는 GOOD이면 `A3_Payoff_Aligned`; POOR 또는 누락/unknown이 있으면 `A3_Payoff_Clarify`다. 이 조건은 범주형 회상 선택이며 새 score/호감도/Ending 조건이 아니다.
- 현재 Result 화면은 기존 generic feedback을 유지한다. 별도 A reaction popup을 얹지 않았으며, 다음 방문의 Intro가 이전 추천 반응을 맡는다.

## 5. Sequence / Row 구성과 ownership

- A1: `/Game/CustomerDialogue`, `A_Visit1`, 기존 C01_Quiet_01~05 그대로.
- A2: `A_Visit2`, 새 source의 A2_Memory_{BEST/GOOD/POOR} + A2_Current_01~05, MemoryVisitNumbers=[1].
- A3: `A_Visit3`, 새 source의 A3_Memory_{BEST/GOOD/POOR}, A3_Earlier_{BEST/GOOD/POOR}, A3_Current_01~03, A3_Payoff_{Aligned/Clarify}, MemoryVisitNumbers=[1,2]. 누락 시 A3_Memory_NEUTRAL 사용.
- 기존 BP_VisitNarrativeDefinition에 optional RequireAllMemories, EarlierMemoryVisitNumber, EarlierBest/Good/PoorRows, AllPositiveOutroRows, OtherMemoryOutroRows를 추가했다. 기본 false/0/empty는 이전 계약 동작을 유지한다.
- GFM의 기존 ConfigureActiveNarrative만 확장한다. GetRecommendationForVisit(ActiveVisit.CustomerID, 요청 방문 번호)로 읽고, pending을 구성한 뒤 기존 OnRevisitMemoryReady가 발생한다. Dialogue는 History 배열을 직접 탐색하지 않는다.
- MemoryVisitNumbers는 현재 방문보다 작은 양의 번호만 조회한다. earlier module은 해당 번호의 confirmed result만 사용한다. local flag/row 배열은 매 configure마다 초기화한다.
- 기존 pending/active/finish/cancel/duplicate Start는 그대로 사용한다. DialogueManager 자산 변경 없음.
- ID/VisitNumber/Day는 기존 Day Schedule authority다. A2는 Day3/Visit2, A3는 Day5/Visit3 reference만 연결했다.
- A2/A3 profile override와 CandidateRecordIDs는 unset이다. 기본 preference와 shared catalogue default 후보 3개를 유지하며 다른 방문의 후보 세트를 확정하지 않는다.

## 6. 정확한 변경 파일

```text
Content/RecordShop/Data/Narrative/DA_A2_Narrative.uasset
Content/RecordShop/Data/Narrative/DA_A3_Narrative.uasset
Content/RecordShop/Data/Narrative/DT_A_RevisitDialogue.uasset
Docs/Architecture/CustomerARevisitNarrativePlan.md
Docs/Architecture/CustomerARevisitNarrativeReport.md
Scripts/Unreal/customer_a_dialogue.json
Scripts/Unreal/customer_a_reference_baseline.json
Scripts/Unreal/customer_a_validation_support.py
Scripts/Unreal/install_customer_a_narrative.py
Scripts/Unreal/run_customer_a_gate.py
Scripts/Unreal/validate_customer_a_contract.py
Scripts/Unreal/validate_customer_a_sequences.py
Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset
Content/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition.uasset
Content/RecordShop/Data/Schedule/DA_Visit_A_2.uasset
Content/RecordShop/Data/Schedule/DA_Visit_A_3.uasset
Scripts/Unreal/cook_mvp.py
Scripts/Unreal/validate_day_week.py
Scripts/Unreal/validate_narrative_contract.py
```

19 files: 7 assets, 8 Python scripts, 2 JSON sources/baselines, 2 docs.

## 7. A1 hash regression

Original package / row / display golden hashes PASS. New reference audit also freezes ten original packages (A1 definition/reference, Tutorial and catalogue included).

```text
CustomerDialogue package: 872dbd16f39cbc4b61da81dbd9dfa6bcbc0ad4dd9379136300894d0850f3eed5
A1 five rows: 7bfa933b1b612309e476b6ceaaa155ec1fc36a9419c98debbc715534e7f5a363
A1 displayed text: c7e2623244f103ed721207ac59e01a66747b6578b80f05e442353aed55a59070
```

Legacy sequence diagnostics still emit exactly C01_Quiet_01~05; the current full-week natural A1 display check is included in section 10.

## 8. A2 분기 검증

7 cases PASS (four required branches plus unknown/foreign/future guards). Every configured row list and emitted text was exact; NO_MEMORY begins at the current situation.

| V1 | V2 | Input mode | Intro | Earlier module | Payoff | Lines | Result |
|---|---|---|---|---|---|---:|---|
| BEST | - | normal | A2_Memory_BEST | none | common request | 6 | PASS |
| GOOD | - | normal | A2_Memory_GOOD | none | common request | 6 | PASS |
| POOR | - | normal | A2_Memory_POOR | none | common request | 6 | PASS |
| MISSING | - | normal | none | none | common request | 5 | PASS |
| BEST | - | foreign | none | none | common request | 5 | PASS |
| BEST | - | future | none | none | common request | 5 | PASS |
| UNKNOWN | - | normal | none | none | common request | 5 | PASS |

## 9. A3 조합 검증

16 cases PASS: all nine combinations, V1 missing/V2 missing/both missing, either unknown, foreign/future histories. Actual pending and emitted rows match the modular contract; every sequence ends with cleared source/rows and late Next produces no second finish.

| V1 | V2 | Input mode | Intro | Earlier module | Payoff | Lines | Result |
|---|---|---|---|---|---|---:|---|
| BEST | BEST | normal | A3_Memory_BEST | A3_Earlier_BEST | A3_Payoff_Aligned | 6 | PASS |
| BEST | GOOD | normal | A3_Memory_GOOD | A3_Earlier_BEST | A3_Payoff_Aligned | 6 | PASS |
| BEST | POOR | normal | A3_Memory_POOR | A3_Earlier_BEST | A3_Payoff_Clarify | 6 | PASS |
| GOOD | BEST | normal | A3_Memory_BEST | A3_Earlier_GOOD | A3_Payoff_Aligned | 6 | PASS |
| GOOD | GOOD | normal | A3_Memory_GOOD | A3_Earlier_GOOD | A3_Payoff_Aligned | 6 | PASS |
| GOOD | POOR | normal | A3_Memory_POOR | A3_Earlier_GOOD | A3_Payoff_Clarify | 6 | PASS |
| POOR | BEST | normal | A3_Memory_BEST | A3_Earlier_POOR | A3_Payoff_Clarify | 6 | PASS |
| POOR | GOOD | normal | A3_Memory_GOOD | A3_Earlier_POOR | A3_Payoff_Clarify | 6 | PASS |
| POOR | POOR | normal | A3_Memory_POOR | A3_Earlier_POOR | A3_Payoff_Clarify | 6 | PASS |
| MISSING | BEST | normal | A3_Memory_NEUTRAL | none | A3_Payoff_Clarify | 5 | PASS |
| BEST | - | normal | A3_Memory_NEUTRAL | none | A3_Payoff_Clarify | 5 | PASS |
| MISSING | - | normal | A3_Memory_NEUTRAL | none | A3_Payoff_Clarify | 5 | PASS |
| UNKNOWN | BEST | normal | A3_Memory_NEUTRAL | none | A3_Payoff_Clarify | 5 | PASS |
| BEST | UNKNOWN | normal | A3_Memory_NEUTRAL | none | A3_Payoff_Clarify | 5 | PASS |
| BEST | GOOD | foreign | A3_Memory_NEUTRAL | none | A3_Payoff_Clarify | 5 | PASS |
| BEST | GOOD | future | A3_Memory_NEUTRAL | none | A3_Payoff_Clarify | 5 | PASS |

Matrix evidence: `Saved/MVPCompletion/20261109T095219Z-customer-a-sequences-5-process.json`. Inputs are unsaved history fixtures; production GFM/DM/profile/scoring are real. The isolated shots are NOT UI approval: this fixture calls DM directly after tutorial closure, so it does not reopen the production dialogue widget. Natural-week UI captures provide that evidence separately. Independent source review found no remaining concrete Critical/Important issue; the initial validation blocker and minor defensive coverage gap are resolved.

## 10. 기존 Day / History / E2E regression

Final Customer A gate: `Saved/MVPCompletion/20261109T102222Z-customer-a-gate.json` — complete=true / pass=true. 2 A-specific checks + 12 foundation groups = **14/14 PASS**.

| Group | Result | Accepted evidence under Saved/MVPCompletion |
|---|---|---|
| contract | PASS | 20261109T102222Z-customer-a-contract-process.json |
| matrix | PASS | 20261109T095219Z-customer-a-sequences-5-process.json |
| editor | PASS | 20261109T095502Z-narrative-editor-process.json |
| sequence | PASS | 20261109T095541Z-narrative-sequence-process.json |
| integration | PASS | 20261109T095615Z-narrative-integration-process.json |
| guards | PASS | 20261109T095725Z-narrative-guards-process.json |
| week | PASS | 20261109T095812Z-narrative-week-process.json |
| rs001 | PASS | 20261109T100825Z-narrative-rs001-process.json |
| rs002 | PASS | 20261109T101003Z-narrative-rs002-process.json |
| rs003 | PASS | 20261109T101151Z-narrative-rs003-process.json |
| audio | PASS | 20261109T101543Z-narrative-audio-process.json |
| startup | PASS | 20261109T101707Z-narrative-startup-process.json |
| cook | PASS | 20261109T101740Z-cook-final-process.json |
| isolated | PASS | 20261109T101900Z-narrative-isolated-process.json |

Blueprint compile: 28 PASS. Dependency closure: 314 packages; missing / redirector / compile failures: 0. Current schema, A1/Tutorial/catalogue hashes and frozen original data pass.

연속 live week는 Tutorial + 16 customers / 17 unique actors를 완료했다. Day starts/ends=[1..7], completed visits=16, FinalStoryEvent=1. History는 16 entries이며 A/B 3회, C/D 2회 기록과 per-customer 분리가 유지된다. Duplicate/copy isolation, selection 시 미기록, active reset 거부, 새 PIE session의 빈 History가 모두 PASS다. Queue 접근 geometry만 명시된 fixture이며 UI/추천/10초 timer/물리 Turntable return/exit/다음 고객은 기존 Production 경로다.

실제 연속 A 경로:

```text
A1: RS002 / GOOD -> History A Visit1
A2: V1 GOOD Intro + Current 01~05 -> RS003 / POOR -> History A Visit2
A3: V2 POOR Intro + V1 GOOD recollection + Current 01~03 + Clarify payoff
```

Natural RS001/2/3는 각각 3/BEST, 2/GOOD, 0/POOR로 PASS했다. SelectedRecord canonical handoff, RPM33/45/78와 cover/record/tonearm, Listening/Result/Store BGM, camera/cursor/focus/movement recovery를 확인했다. Listening timer는 기존 10초이고 Result 진입은 물리 return 시간을 포함한다.

실제 A2/A3 UMG 캡처 12장: `20261109T095812Z-narrative-week-A2-line1.png`~`line6.png`, `A3-line1.png`~`line6.png`. 관측한 A2 긴 상황/Hint, A3 payoff는 기존 패널에서 2줄로 읽히며 Next 버튼과 겹치지 않았다. 전체 해상도·말투·Hint 강도 판단은 MANUAL REVIEW다.

Windows cook PASS: exit 0 / cook errors 0; A2/A3 DataTable + 두 Narrative refs, 기존 catalogue/tutorial/history, 7 days / 16 visits 산출물을 확인했다. Scope는 SkipSaveAssetRegistry를 사용한 bounded loose cook이다. Packaging/staging/executable 확인은 NOT RUN.

최초 전체 실행 `20261109T095432Z-customer-a-gate.json` / `20261109T095502Z-narrative-gate.json`에서는 isolated LP reset/full-playback만 40초 timeout으로 실패했다. 나머지 11개 foundation groups는 PASS했다. Production audio/turntable은 변경하지 않았다. 동일한 40초 제한 fresh-Editor 재검증 `20261109T101900Z-narrative-isolated-process.json`은 early fade 1.219초, reset 후 full natural completion 34.203초로 PASS했다. 최종 집계는 변경 없는 Production의 성공 보고서 11개와 이 재검증을 합쳤다. 최초 실패를 폐기하거나 timeout 원인이 해결됐다고 주장하지 않는다.

프로세스별 unexpected gameplay errors는 0이다. 기존 engine startup smoke의 `Condition failed` 메시지는 별도로 분류되며, 모든 Editor 로그가 globally error-free라는 뜻은 아니다. 초기 probe crash 로그와 RED audit도 Saved 아래 보존했다.

## 11. Known limitations

- 이번 신규 text는 A2/A3의 20행뿐이다. B~H는 기존 mechanical placeholder이며 final story를 적용하지 않았다.
- 과거 LP의 RecordID는 History API/context에 유지하지만 이번 text에 제목을 동적 삽입하지 않는다. 회상은 확정 Result와 방문 번호에 기반한다.
- 현재 Result의 A 전용 추가 문구는 만들지 않았다. Generic authority/UI를 유지하고 다음 방문에서 반영한다.
- 새 optional memory fields의 authoring 규약은 MemoryVisitNumbers의 오름차순/중복 없음과 EarlierMemoryVisitNumber가 그 목록에 포함됨이다. A3는 [1,2]/1로 명시한다.
- SaveGame/Continue, affinity, 합석, 신규 LP/audio/cover, Ending은 추가하지 않았다. Day7 FinalStoryEvent 이후는 TBD다.
- 초기 테스트용 probe의 추가 Memory observer 구성에서 native Editor crash가 발생했다. 이 중복 observer를 제거하고 기존 Foundation event 관측 검증과 신규 실제 line/finish/UI 검증을 나누었다. raw 실패 로그를 보존하며 plugin crash 원인이 확정됐다고 주장하지 않는다.
- 기존 isolated LP replay의 간헐적 40초 timeout은 원인이 미확정이다. 동일 조건 재검증은 통과했지만 실제 장치 청취와 별도 audio 안정성 확인이 필요하다.
- Cook은 bounded loose smoke이며 packaged executable/staging 검증과 다르다.

## 12. MANUAL REVIEW

- 한국어 자연스러움, A1의 거친 하게체와 A2/A3의 연결. A2의 “아니야” 같은 구어적 어미를 어느 정도 유지할지.
- 5~6행 길이, 한 행의 호흡과 Hint의 노골성. 현재 Jazz/Traditional 단서를 의도적으로 읽을 수 있게 썼다.
- GOOD/POOR 회상과 두 방문 비교가 실제 플레이 순서에서 자연스러운지.
- 화면 줄바꿈/가독성, mouse/gamepad focus와 camera/input 감각.
- 실제 기기의 10초 Listening / Store BGM 음량 및 fade 청취.
- packaged executable 실행. 최종 Ending 내용은 계속 TBD.

## 13. 다음 B Narrative Phase 진입 가능 여부

자동 Gate 14/14 PASS로 B Narrative Phase에 진입할 기술적 기반은 준비됐다. 다만 B의 실제 대사/방문별 preference와 candidate set은 다음 범위에서 확정해야 한다. 이번 실행은 A2/A3에서 멈추며, B~H/추가 LP/합석/Ending을 구현하지 않는다. 한국어 tone·Hint 강도와 inherited audio timeout은 위 review/limitation에 남긴다.

## 14. 추천 commit plan

- `feat: add modular revisit memory composition for narratives` — definition/GFM optional contract와 재생 검증을 함께 검토.
- `content: add customer A second and third visit dialogue` — DT/DA/visit references와 authoring source.
- `test: verify customer A branches and week regressions` — matrix/full-week/cook/report.
- 실제 binary는 dependency가 있는 단위로 묶어 검토하고, BP_GameFlowManager를 텍스트처럼 부분 staging하지 않는다.
- staging / commit / push는 수행하지 않았다.

최종 Git 상태: 시작 branch/HEAD 유지, staging 0. 변경은 section 6의 19 files만이며 unrelated change가 없다. 8개 변경 Python AST, JSON authoring, 원본 10 packages hash, diff whitespace 검증이 통과했다. 모든 자산 변경은 Unreal Editor Python / BlueprintGraphEditor / AssetTools / EditorAssetLibrary로 수행했고 raw .uasset/.umap edit는 하지 않았다. 마지막 Production 자산 변경은 성공 installer(09:43:18 UTC 실행)이며 이후에는 검증/문서만 수정했다. No staging / commit / push.
