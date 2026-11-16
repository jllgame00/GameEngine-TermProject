# Seven-Day Customer Narrative / Content Production Plan

작성일: 2026-11-09 · 상태: **CONTENT DESIGN / REVIEW_REQUIRED**

이 문서는 7일 콘텐츠의 검토안과 Production 데이터 연결 계획이다. 확정된 Schedule과 A Visit 1은 보존한다. A 재방문 Beat, 신규 인물, LP, 합석은 아래 상태에 따라 검토하며, 최종 대사·Character Data·Audio로 확정 적용하지 않았다. Ending은 **TBD**다.

## 0. 기준과 실제 Production 감사

- Branch: `feature/day-system-customer-queue`.
- 시작 HEAD: `c2cbdf89d4a775c8abc73a0c46700d3cd0dd5d45`; 시작 worktree clean.
- Fresh Editor read-only 감사: [seven-day-content-audit](../../Saved/MVPCompletion/20261109T072956Z-seven-day-content-audit.json).
- 현재 소유권: 기존 BP_GameFlowManager의 Day / Queue / History, 기존 DialogueManager, 기존 RecordSelect → Shelf → GameFlowManager → Turntable 경로를 유지한다.
- Schedule의 A1/A2/A3는 기존 BP_Customer01을 참조한다. 모든 임시 방문은 아직 같은 class를 사용하고 `IsPlaceholderContent=True`, `StoryEventID=None`이다. 새로운 캐릭터의 콘텐츠가 연결됐다는 뜻이 아니다.
- A의 원본 프로필은 CustomerID `C01`, 표시명 `중년 손님`, Quiet / Jazz / Traditional이다. Queue에서는 ActiveVisit의 stable ID `A`로 runtime profile ID를 바꾼다. 원본 class의 C01을 A로 영구 치환하지 않는다.
- `/Game/CustomerDialogue`의 `C01_Quiet_01`~`C01_Quiet_05`를 수정·재명명·삭제하지 않는다. 첫 방문의 세대 불만과 불쾌함을 씻어낼 음악 요청을 그대로 둔다.
- 현재 DialogueManager.StartDialogue는 **CustomerID/VisitNumber가 아니라 Mood 일치 행을 수집하고 이름순으로 정렬**한다. 같은 테이블에 Quiet 대사를 추가하면 A 원문까지 섞일 수 있다. 신규 대사를 단순 append하는 작업은 안전하지 않다.
- Visit의 CustomerData row handle은 아직 runtime 소비자가 없는 예약 필드다. StoryEventID 역시 대사 라우터가 아니다. 필드에 값을 적는 것만으로 구현 완료로 취급하지 않는다.
- History는 세션 메모리다. SaveGame/Continue는 미연결이며 실제 Story delivery 완료 상태도 아직 없다.

### 상태 표기

| 상태 | 의미 |
|---|---|
| LOCKED_EXISTING | 이미 확정되어 유지할 Production 동작/데이터 |
| CONNECTED_EXISTING | 현재 자산 연결을 감사로 확인; 이번에 새로 구현한 연결은 아님 |
| REVIEW_REQUIRED | 사용자 검토용 후보; runtime 데이터에 영구 적용 금지 |
| IMPLEMENTATION_REQUIRED | 승인 이후 필요한 코드/데이터 경로; 현재 동작한다고 주장하지 않음 |
| TBD | 내용·선택을 아직 정하지 않음 |

범위는 부모님 대신 가게를 맡은 한 주의 작은 방문 경험이다. 음악은 일상에 잠시 공간을 만든다. 손님의 고민을 치료하거나 인생을 해결하는 장치로 쓰지 않는다. RecommendationResult는 음악 적합도이며 호감도·도덕 점수·엔딩 점수가 아니다.

## 1. 7일 전체 Timeline — 방문 순서 LOCKED_EXISTING

Prologue / Tutorial은 Queue 이전의 별도 cycle이며 A의 Visit 1이나 History로 합산하지 않는다.

| Day | 확정 방문 순서 | 그날의 중심 Beat 후보 | 보조 방문 / 무게 조절 | 이전 추천 반영 | Story 목적 |
|---|---|---|---|---|---|
| 1 | A1 → E1 | 기존 중년 손님의 불만 속에서 음악 요청을 읽는다 | E: 친구를 기다리는 짧은 쉼 | 둘 다 이전 기록 없음 | 기존 추천 방식과 가게의 일상성을 익힌다 |
| 2 | B1 → C1 | B: 수많은 시도 중 오늘 시작할 리듬 하나를 고른다 | C: 새 동네 첫 초대의 어색함을 짧게 소개 | 둘 다 첫 방문 | A와 다른 연령·취향·말의 속도를 소개한다 |
| 3 | A2 → F1 → D1 | A: 남의 태도에 대한 불만에서, 자신이 다음 말을 고를 시간으로 이동 | F는 가벼운 대기 에피소드; D는 자기 시간을 다루는 첫 소개만 | A는 V1; F/D는 없음 | 같은 사람의 새로운 현재 상황을 들을 수 있음을 보여준다 |
| 4 | B2 → C2 | B: 외부 피드백과 자기 작업의 속도를 구분한다 | C는 거창한 모임 대신 소수의 초대로 작은 마무리 | B/C 각각 V1 | 지난 추천을 기억하되 같은 부탁을 반복하지 않는다 |
| 5 | A3 → G1 | A: 구체적인 취향을 함께 알아온 과정의 작은 payoff | G는 엽서 한 장에 맞는 짧은 음악 | A는 V1+V2; G는 없음 | 큰 화해 선언 없이 반복 방문의 누적을 느끼게 한다 |
| 6 | B3 → D2 → H1 | B: 공개 평가와 별개로 자신이 정한 다음 작업을 시작한다 | D는 작은 생활 리듬 선택으로 마무리; H는 가벼운 퍼즐 휴식 | B는 V1+V2, D는 V1; H는 없음 | 주요 Arc를 닫되 세 방문 모두 큰 사건으로 만들지 않는다 |
| 7 | TEMP_D7_01 → TEMP_D7_02 → FinalStoryEvent | 일반 방문 cycle을 끝내고 한 주의 사실 정보를 모은다 | 두 일반 고객의 신원·에피소드·취향은 TBD | 현재 ID는 첫 방문; 과거 인물로 교체 시 별도 검토 | 운영 완료와 Story 전달 상태를 후속 Hook에 제공; Ending TBD |

A1 외의 중심 Beat와 모든 보조 인물 내용은 REVIEW_REQUIRED다. Day 7에 부모님의 귀환, 감사 편지, 폐점, 공연, 화해 장면 등을 임의로 배치하지 않는다.

## 2. A — 기존 중년 손님 / Visit 1·2·3

### 고정점과 제안 경계

- **LOCKED_EXISTING:** 기존 중년 남성 설정, 첫 방문 5행, Quiet / Jazz / Traditional, A의 Day 1/3/5 방문.
- **REVIEW_REQUIRED:** V2/V3의 구체 상황과 아래 Beat. 직업·가족·자녀·과거 상실 경험을 새로 확정하지 않는다.
- 세대 불만을 음악 적합도와 분리한다. 플레이어가 불만에 동의해야 좋은 추천이 되는 구조를 만들지 않는다.
- V2/V3의 제안 preference는 계속 Quiet / Jazz / Traditional이다. 달라지는 현재 상황을 같은 취향 안에서도 다르게 들을 수 있게 한다. 이는 고정 적용된 신규 방문 프로필이 아니다.

| 방문 | 시작 상태 / Narrative Beat | 현재 요청과 추론 Hint | 기억 사용 | 마무리의 역할 |
|---|---|---|---|---|
| V1 · Day 1 | 기존 세대 불만을 말하고 불쾌함을 씻어낼 음악을 요구 | 기존 원문 보존. Quiet/Jazz/Traditional은 기존 프로필 기준 | 없음 | 최초 추천의 기준점을 만든다 |
| V2 · Day 3 | 지난 곡을 짧게 짚은 뒤, 가까운 젊은 지인과 대화가 어긋나 다음 말을 고르기 망설이는 현재 상황으로 이동 | 자극을 더하기보다 말을 정리할 공간=Quiet; 익숙한 작은 재즈 합주를 선호=Jazz; 낯선 해석보다 익숙한 형식=Traditional | 정확히 A V1을 조회. Result별 도입 1개 → 공통 현재 Beat로 합류 | 비난을 반복하는 장면 대신 자신의 말과 속도를 생각할 여지를 남긴다 |
| V3 · Day 5 | 다시 이야기할 평범한 약속을 앞두고, 가게에서 들었던 두 번의 경험을 비교한다 | 감정을 더 크게 만들지 않는 소리, 익숙한 장르와 형식을 구체적으로 지목. 취향을 플레이어가 추론할 단서가 누적됨 | A V1과 V2를 각각 조회. V2 반응을 중심으로 V1 대비 1개를 덧붙임 | 잘 맞았으면 이해받았다는 구체적인 인식, 안 맞았으면 취향을 더 정확히 설명하는 기회. 화해 성공·성격 교정·Ending으로 이어진다고 확정하지 않음 |

위 Hint는 대사 작성 지침이며 신규 영구 Dialogue 문구가 아니다. 기존 V1에 Jazz/Traditional 단서가 직접 충분히 드러난다고 가정하지 않는다. 나이·성별로 장르를 추측하게 하지 말고, 필요하면 이후 onboarding/프로필 표시로 단서를 보강할지 검토한다. 오늘 원문을 고치지 않는다.

### A V2 분기 정의

| 조건 | 도입 Beat | RecordID 사용 | 공통 구간 |
|---|---|---|---|
| V1 BEST | 그날 들은 곡의 익숙함과 차분함이 잘 맞았다는 구체적 회상 | 확인된 레코드 제목 또는 안전한 일반 지칭 | 오늘은 대화 전 마음을 정리하고 싶은 상황 → 같은 3요소 Hint |
| V1 GOOD | 전체 방향은 맞았지만 자신의 취향을 조금 더 설명할 필요가 있었다는 회상 | 실제 V1 RecordID만 사용 | 동일 |
| V1 POOR | 지난 추천은 그날의 요청과 거리가 있었다는 담담한 피드백 | 곡/플레이어를 열등하다고 평가하지 않음 | 동일; 새 추천 기회를 정상 제공 |
| 기록 없음/조회 실패 | 이전 추천의 결과를 단정하지 않고 현재 요청부터 시작 | 가짜 제목이나 POOR 기본값 생성 금지 | 동일 |

GOOD 점수만으로 어떤 요소가 어긋났는지 단정하지 않는다. 현재 History에는 당시 preference snapshot이나 요소별 채점 내역이 없다. 세부 불일치를 말하려면 검증된 당시 방문 프로필과 canonical RecordID 해석이 먼저 필요하다.

### A V3 누적 방식 — 9개 전체 대본을 만들지 않음

V2 결과 도입 모듈 3개, V1 대비 모듈 3개, 현재 상황/취향 Hint/마무리 공통 모듈을 조합한다. V1 또는 V2 누락은 별도 중립 fallback이다.

| V1 → V2 | 비교 Beat 방향 |
|---|---|
| BEST → BEST | 일관되게 맞았던 요소가 자신의 취향임을 구체화 |
| BEST → GOOD | 익숙한 기준은 있으나 두 번째 선택에서 미묘한 차이를 발견 |
| BEST → POOR | 첫 경험과 달랐음을 말하고 오늘 필요한 조건을 다시 분명히 함 |
| GOOD → BEST | 첫 단서가 두 번째에서 더 정확해졌음을 인식 |
| GOOD → GOOD | 큰 방향은 맞지만 남은 취향 차이를 구체적으로 설명 |
| GOOD → POOR | 지난 두 경험을 동일하게 좋았다고 포장하지 않고 요청을 정리 |
| POOR → BEST | 잘 맞지 않았던 경험 뒤에 맞는 방향을 찾았다는 대비 |
| POOR → GOOD | 일부 맞아가는 변화만 인정; 과장된 성공 선언 없음 |
| POOR → POOR | 실패 기록을 지우지 않음. 더 명확한 Hint를 주고 세 번째 추천을 정상 진행 |

이 비교는 합산 호감도나 상승/하락 수치가 아니다. 현재 세 번째 추천의 Result는 기존 cycle에서 별도로 확정된다. 과거 결과만으로 세 번째 성공을 미리 선언하지 않는다.

**승인 후 필요한 대사 단위 예산:** V2는 도입 1~2행 + 현재 상황/3요소 Hint 3~4행; V3는 도입 1행 + 대비 최대 1행 + 현재 요청/Hint 2~3행 + 짧은 payoff 1행을 목표로 검토한다. 원문 V1의 행 수와 종료 표시는 그대로 둔다.

## 3. B 후보 — 자기 작업의 속도를 찾는 20대 후반 프리랜서 영상 디자이너

**REVIEW_REQUIRED — 이름, 성별, 구체 직업, 문구, tag 변화 모두 미확정.**

| 항목 | 제안 |
|---|---|
| 생활 배경 / 고민 | 짧은 의뢰 작업을 여러 개 하며 첫 개인 작업 공개도 준비. 선택지가 많아 시작·수정·종료를 남의 반응에 맡기는 경향 |
| 말투 / 첫 인상 | 빠르게 말했다가 스스로 고쳐 말함. 자신만만한 표현 사이로 작업 방식의 망설임이 보임 |
| 음악 취향 / 성격 | Electronic / Adventurous. 낯선 질감에 관심이 있으며 도전적인 취향이 항상 큰 음량을 뜻하지는 않음 |
| A와의 차이 | 세대 판단/익숙함이 아니라 자기 표현과 외부 평가의 경계; Traditional/Jazz와 구분 |

| 방문 | 현재 변화 | target Mood / Genre / Theme | 플레이어가 읽을 Hint | 이전 추천 사용 |
|---|---|---|---|---|
| B1 · Day 2 | 오늘 시작할 작업 하나를 골라 첫 시도를 하고 싶음 | Restless / Electronic / Adventurous | 움직이는 반복 리듬, 전자적 질감, 새 소리를 시도하려는 의향 | 없음. 기존 RS003도 이 요청에는 BEST일 수 있음 |
| B2 · Day 4 | 공개 뒤 서로 다른 의견을 받아, 바로 고치기보다 자기 속도를 되찾을 공간이 필요 | Quiet / Electronic / Adventurous | 장르는 유지하되 리듬 밀도/자극은 낮추고 싶음; 새로운 음색은 포기하지 않음 | B1의 BEST/GOOD/POOR로 작업을 시작할 때의 음악 경험만 회상. 작품 평가가 좋아졌다는 인과관계는 만들지 않음 |
| B3 · Day 6 | 모두의 평가를 맞추는 대신 본인이 정한 작은 수정 또는 다음 시도를 선택 | Quiet / Electronic / Adventurous | 조용한 전자음도 자신의 취향임을 구체적으로 말할 수 있음 | B1과 B2를 비교해 목표 음악의 변화가 전달됨. 음악 취향 변화와 사람의 성장 점수를 합치지 않음 |

B의 payoff는 성공·취업·수상 소식이 아니라 자기 작업의 다음 단계를 자신이 정하는 작은 선택이다. 다른 고객과 비밀리에 가족/연인/사제 관계로 연결하지 않는다.

## 4. C 후보 — 새 동네에서 작은 목공 모임을 준비하는 30대 공유공방 강사

**REVIEW_REQUIRED.** 가게 밖 공방 맵·제작·매출 시스템을 만들자는 제안이 아니다.

| 항목 | 제안 |
|---|---|
| 배경 / 현재 고민 | 새 동네에서 처음 사람들을 초대하려다 준비만 커짐. 거창한 개장 행사보다 같이 앉을 작은 자리를 만들고 싶음 |
| 말투 / 첫 인상 | 구체적인 생활 물건과 인원수를 들어 이야기함. 상대를 챙기느라 자기 부담을 뒤늦게 말하는 친근한 사람 |
| 취향 | Quiet / Folk / Sociable. 목소리를 덮지 않는 어쿠스틱 질감과 함께 있는 분위기 |
| A/B와 차이 | 판단을 누그러뜨리거나 개인 창작의 평가를 다루는 역할이 아니라 첫 관계를 시작하는 실용적 소심함 |

| 방문 | Narrative 변화 | Hint | 기억 사용 |
|---|---|---|---|
| C1 · Day 2 | 많은 사람을 위한 완벽한 준비 대신 첫 초대 한 번을 생각 | 작은 대화가 들릴 정도=Quiet; 손으로 튕기는 현과 담백한 목소리=Folk; 혼자 몰입하기보다 함께 앉는 분위기=Sociable | 이전 기록 없음 |
| C2 · Day 4 | 큰 행사 계획을 줄이고 두세 명에게 먼저 연락하는 선택 | 같은 3요소를 새로운 현재 장면에 연결. 새 취향 시험을 억지로 넣지 않음 | C1 결과별로 그날 가게에서 느낀 분위기만 회상. 아직 구현되지 않은 구매/대여/집에서 재생을 사실처럼 말하지 않음 |

두 번의 방문으로 끝나는 작은 초대의 Arc다. 방문객 수 증가, 수익, 모임 성공 여부를 gameplay 상태로 요구하지 않는다.

## 5. D 후보 — 야간에서 주간 근무로 옮긴 40대 시설관리 기사

**REVIEW_REQUIRED.** 직업 전문 지식이나 건강·치료 서사는 추가하지 않는다.

| 항목 | 제안 |
|---|---|
| 배경 / 현재 고민 | 근무 시간이 바뀌어 자기 시간이 낯설게 남음. 모든 빈 시간을 일로 채우지 않고 하루의 시작/끝을 구분해 보고 싶음 |
| 말투 / 첫 인상 | 시간과 순서를 정확하게 말하는 간결한 말투. 감정 대신 평소 동선을 먼저 설명 |
| 취향 | Quiet / Classical / Reflective. 천천히 이어지는 연주를 따라가며 자기 시간을 정리하고 싶음 |
| A/B/C와 차이 | 세대 갈등·창작 평가·사람 초대가 아닌 생활 리듬의 작은 전환. Classical은 나이/직업 때문에 추정하는 취향이 아님 |

| 방문 | Narrative 변화 | Hint | 기억 사용 |
|---|---|---|---|
| D1 · Day 3 | 남는 시간을 뭘 해야 하는 시간으로만 느끼고 있음 | 고요한 여백=Quiet; 악장처럼 이어지는 피아노/현의 연주=Classical; 생각을 정돈할 여유=Reflective | 없음 |
| D2 · Day 6 | 대단한 취미 대신 잠깐 앉아 듣는 시간을 하루에 남기는 선택 | 동일한 3요소를 반복 주문 대신 오늘의 구체적 여백으로 제시 | D1 결과별로 편했거나 어긋난 음악 경험을 회상. 생활 전환이 음악 한 곡으로 해결됐다고 단정하지 않음 |

짧은 휴식 하나를 선택하는 데서 닫는다. 퇴사·은퇴·질병·가족 상실을 새로 확정하지 않는다.

## 6. E / F / G / H — 단발 Episode 후보

**전원 REVIEW_REQUIRED.** 각 2~4행의 요청/Hint와 짧은 반응 방향을 목표로 한다. 이름·성별·외형·영구 Dialogue는 미확정이다. 다음 방문이나 별도 해결 퀘스트를 예고하지 않는다.

| ID / Day | 한 문장 concept / 방문 이유 | Mood / MusicPreference / Personality | Dialogue Hint 방향 | 추천 결과 Reaction 방향 |
|---|---|---|---|---|
| E / 1 | 교대를 마친 20대 카페 직원이 친구와 만나기 전 잠깐 앉을 음악을 찾음 | Quiet / Jazz / Sociable | 대화 전 쉬는 작은 공간, 작은 재즈 합주, 누군가를 기다리는 밝은 여유 | BEST: 기다리는 시간이 편안해짐; GOOD: 대체로 어울리지만 분위기 한 요소가 남음; POOR: 오늘 기다림에 필요한 느낌과 달랐다고 가볍게 마무리 |
| F / 3 | 우산 없이 버스 한 대를 더 기다리는 대학생이 짧은 대기를 작은 음악 탐색으로 바꿈 | Restless / Electronic / Adventurous | 움직이는 반복 리듬, 전자음, 평소 안 듣던 질감에 대한 호기심 | BEST: 대기가 짧은 탐색처럼 느껴짐; GOOD: 흥미로운 부분 하나를 짚음; POOR: 낯설어도 오늘 원한 낯섦은 아니었다는 취향 차이. 비 때문에 우울하다고 자동 설정하지 않음 |
| G / 5 | 외근을 마친 40대 수리 기사가 멀리 있는 친구에게 엽서 한 장을 쓸 동안의 음악을 찾음 | Quiet / Folk / Sociable | 작은 소리, 어쿠스틱 현/목소리, 누군가에게 말을 건네는 듯한 분위기 | BEST: 엽서의 첫 문장을 고를 여유; GOOD: 소리는 편하지만 분위기가 조금 다름; POOR: 글쓰기와 어울리지 않았음을 담담히 말함. 엽서 UI/발송 기능은 만들지 않음 |
| H / 6 | 신문 낱말퍼즐 한 칸을 남겨 둔 60대 동네 손님이 답을 서두르지 않을 음악을 찾음 | Quiet / Classical / Reflective | 서두르지 않는 흐름, 피아노/현의 긴 호흡, 혼자 생각할 여백 | BEST: 답보다 듣는 시간을 즐김; GOOD: 차분함 일부는 맞음; POOR: 생각을 흩뜨렸다는 짧은 반응. 실제 퍼즐 정답·미니게임·보상은 없음 |

Theme는 성격 전체의 진단이 아니라 이번 음악 선택에 쓰이는 기존 3요소 계약이다. 인물별 취향은 나이/직업의 고정관념에서 추론시키지 말고 요청 안에 단서를 제공한다.

## 7. Customer preference와 태그 사전

이 표는 **후보 데이터**다. Production CustomerData/Visit/Dialogue에 import하지 않는다. A V1 외의 적용은 승인 후다.

| Customer / Visit | Mood | MusicPreference → LP Genre | Personality → LP Theme | 상태 |
|---|---|---|---|---|
| A1 | Quiet | Jazz | Traditional | LOCKED_EXISTING |
| A2 / A3 | Quiet | Jazz | Traditional | 기존 취향 유지 제안 / REVIEW_REQUIRED |
| B1 | Restless | Electronic | Adventurous | REVIEW_REQUIRED |
| B2 / B3 | Quiet | Electronic | Adventurous | REVIEW_REQUIRED; 방문별 Mood override 경로 필요 |
| C1 / C2 | Quiet | Folk | Sociable | REVIEW_REQUIRED |
| D1 / D2 | Quiet | Classical | Reflective | REVIEW_REQUIRED |
| E1 | Quiet | Jazz | Sociable | REVIEW_REQUIRED |
| F1 | Restless | Electronic | Adventurous | REVIEW_REQUIRED |
| G1 | Quiet | Folk | Sociable | REVIEW_REQUIRED |
| H1 | Quiet | Classical | Reflective | REVIEW_REQUIRED |
| TEMP_D7_01 / TEMP_D7_02 | TBD | TBD | TBD | 현재 C01 mechanical placeholder 유지; 신규 취향 미확정 |

- Mood는 인물의 모든 감정이 아니라 **찾는 음악의 목표 분위기**로 작성한다. 화가 난 A도 Quiet를 원할 수 있다.
- 이미 확인된 값: Quiet, Restless / Jazz, Electronic / Traditional, Sociable, Adventurous.
- 신규 제안 값: **Folk, Classical, Reflective**. 명칭·번역·카탈로그 사용을 검토해야 한다. 현재 코드의 비교가 문자열 정확 일치이므로 대소문자/공백을 포함한 작성 규칙을 통일한다.
- Energy는 현재 채점 요소가 아니다. High/Low나 추가 세부 감정을 채점에 몰래 추가하지 않는다.
- 방문별 Mood를 바꿀 때 class default를 덮어쓰지 않는다. 승인된 Visit profile override를 runtime CurrentCustomer/CurrentMood에 함께 적용해야 한다. 현재는 그 콘텐츠 경로가 없다.

## 8. Revisit Result branching / Dialogue data contract

### 8.1 기존 Runtime API를 소비하는 순서

1. 기존 GFM의 accepted Dialogue setup에서 `OnRevisitMemoryReady(CustomerID, VisitNumber, HasPrevious)`가 발생한다.
2. 해당 이벤트의 ID/번호가 ActiveVisit과 일치하는지 확인하고 `GetActiveVisitMemory()` 사본을 한 번 받아 이번 대화 context로 고정한다. 이벤트 시점에는 DialogueManager.StartDialogue 전이다.
3. V2는 `GetRecommendationForVisit(CustomerID, 1)`, V3는 번호 1과 2를 각각 조회한다. 서로 다른 CustomerID를 fallback으로 사용하지 않는다.
4. Entry의 ID, VisitNumber, RecordID, Result와 유효성을 검사한다. current visit 결과나 future visit은 이전 기억에 포함하지 않는다.
5. Memory intro → 공통 현재 상황 → preference Hint → 기존 추천 cycle로 합류한다. 음악 선택·계산·Result·History 확정 경로는 그대로 둔다.
6. Dialogue 종료/취소 시 context를 해제한다. History는 수정·삭제하거나 매 조회마다 다시 기록하지 않는다. 같은 Dialogue 시작 이벤트 반복으로 도입을 두 번 재생하지 않는다.

`HasPreviousVisit(CustomerID)`는 해당 ID의 확정 기록 존재 여부다. Result 이후에는 현재 방문도 기록돼 있으므로, 현재 방문을 제외해야 하는 Narrative 판단에는 `GetActiveVisitMemory` 또는 번호가 지정된 query를 사용한다. `GetLatestRecommendation`만 무조건 호출해 V2 기록이라고 가정하지 않는다.

### 8.2 Result 의미와 안전한 표현

| 분기 | Data 의미 | Narrative 사용 | 금지할 가정 |
|---|---|---|---|
| BEST | Score 3 | 요청한 음악 방향이 잘 맞았던 구체적 경험 | 호감도 증가, 인생 문제 해결, 다음 추천 자동 성공 |
| GOOD | Score 2 | 전체 방향은 맞지만 취향 차이를 더 설명할 여지 | History만으로 어느 태그가 틀렸는지 단정 |
| POOR | Score 0~1 | 이전 추천과 당시 요청의 거리 | 손님/음악/플레이어의 우열, Queue 탈락, 재방문 차단 |
| NO_MEMORY | Entry 없음/유효성 실패/알 수 없는 Result | 현재 요청부터 자연스럽게 시작 | POOR 치환, 가짜 이전 방문 생성 |

RecordID만 저장돼 있다. 현재 catalogue는 WBP_RecordSelect의 MakeStruct 데이터이며 공용 ID resolver가 없다. 새 RecordID→Title 목록을 Narrative 안에 복제하지 않는다. 승인 후 기존 catalogue를 단일 공유 data source로 옮기고 현재 선택 widget도 그 source를 읽도록 하거나, 같은 authority를 조회할 수 있는 resolver를 마련한다. 그전에는 레코드 제목 없이 그날 들었던 곡을 지칭하는 중립 fallback을 사용한다. 구매·대여·집에서 재생한 사실은 현재 History로 입증되지 않는다.

### 8.3 제안 Narrative visit row 계약 — 아직 asset/struct가 아님

| 필드 | 의미 / 권한 |
|---|---|
| CustomerID + VisitNumber | 기존 Schedule key를 참조; 여기서 새 번호를 생성하지 않음 |
| SequenceID | 승인된 대사 sequence의 명시적 ID |
| SourceTable + OrderedRowNames | 해당 sequence의 원본 테이블과 순서가 정해진 행 참조 |
| LegacySequenceRef | A1은 기존 CustomerDialogue의 C01_Quiet_01~05를 참조; 원문 복사 없음 |
| MemoryVisitNumbers | V2=[1], V3=[1,2]; 없는 번호는 NO_MEMORY |
| MemoryIntroKeys | BEST / GOOD / POOR / NO_MEMORY의 text key. Result 자체를 편집하지 않음 |
| CurrentBeatKey / HintKeys | 공통 현재 상황과 3요소 단서의 text key |
| TargetMoodOverride | 승인된 방문에만 설정; 프로필/CurrentMood 동기화 필요 |
| ReactionKeys | 기존 Result 확정 후 소비할 고객별 반응 후보; score authority와 분리 |
| ReviewStatus / ContentVersion | 미승인 행을 Production loader가 채택하지 않도록 하는 authoring 조건 |

**권장 source 분리:** 원본 CustomerDialogue에는 새 Quiet 행을 넣지 않는다. 신규 대사는 승인 후 별도 `DT_CustomerVisitNarrative` 후보 테이블에 기존 DialogueData row 형식을 재사용하는 방향을 우선한다. 별도 테이블은 신규 대사의 유일한 source이며 A1 원문은 복사하지 않는다. A1/Tutorial은 원본 테이블 5행을 계속 사용하므로 legacy Mood-only fallback에서도 새 대사와 섞이지 않는다.

**작은 진입점 제안:** 기존 DialogueManager가 `SetPendingDialogueSequence(SourceTable, OrderedRowNames)`를 받고, 직후 기존 StartDialogue가 pending 값을 한 번 소비하도록 확장한다. 승인된 sequence와 모든 행을 검증한 뒤 active source와 순서 배열로 고정한다. StartDialogue뿐 아니라 Next/종료까지 같은 active source를 사용해야 한다. 현재 hardcoded DataTable 조회를 그대로 두고 SourceTable 필드만 추가하면 구현된 것이 아니다.

이 진입점은 OnRevisitMemoryReady 소비자가 구성한 짧은 memory intro와 공통 Beat를 하나의 sequence로 전달하기 위한 **IMPLEMENTATION_REQUIRED 제안**이다. 현재 API로 존재하지 않는다. 별도 Dialogue/Result manager를 만들지 않는다. legacy 진입 시 pending/active context를 비워 원본 테이블로 돌아가고, 종료/취소 후에도 다음 방문으로 새 source가 새지 않도록 해제한다. Mood는 음악 요청 값으로 유지하며 신규 대사 선택 key로 재사용하지 않는다.

`A_V2_MemoryIntro`, `A_V3_Accumulation` 같은 이름은 문서상의 제안 식별자다. 현재 StoryEventID에 저장하거나 연결하지 않았다. A1의 원문을 새 행으로 복사해 두 개의 authority로 만들지 않는다.


### 8.4 승인 후 branch 검증 Gate

- A1은 원문 5행/순서/종료 표시가 같음. Tutorial과 Day 1 A1의 mechanical 중복도 유지 여부를 별도 검토한다. 현재 Tutorial 역시 C01을 사용하므로 동일 인물 소개가 반복될 수 있다. 이를 숨기기 위해 Tutorial을 A1로 합치거나 History 방문 번호를 바꾸지 않는다.
- A2의 BEST/GOOD/POOR/NO_MEMORY 각 1회; A3의 9개 결과 조합과 V1/V2 일부 누락을 검사한다.
- B/C/D의 고객 ID, 목표 방문, 이전 결과가 섞이지 않음. 승인된 B의 Mood 변경이 scoring에도 반영됨.
- 분기는 달라도 한 번의 기존 Customer Cycle로 합류. SelectedRecord, listening, Result, History의 idempotence, exit/cleanup은 기존 Gate를 회귀 검사한다.
- 미승인 row, 제목 resolve 실패, 알 수 없는 Result는 중립 fallback. 임의의 POOR/호감도/Ending을 만들지 않는다.

## 9. 합석 / 겹침 Event 후보 — 최대 두 개, 구현하지 않음

| 후보 | 의미 있는 조합 / 시점 | 짧은 Beat | 다음 손님의 상태 | 독립성 |
|---|---|---|---|---|
| OVERLAP_D3_A2_F | Day 3 A2 Result Continue 뒤, F의 정식 cycle 전 | 잠깐 비를 피하는 F와 A가 같은 공간의 다른 속도를 알아차리는 짧은 침묵/일상 정보 교환 | F는 음악을 요구하지 않고 기다림; A 종료 후 자기 요청 시작 | A의 세대관을 교정하는 필수 사건으로 만들지 않음. 생략해도 A3 정상 |
| OVERLAP_D6_D2_H | Day 6 D2 Result Continue 뒤, H의 정식 cycle 전 | 남는 시간을 바로 채우지 않아도 된다는 D의 선택 옆에 H의 느긋한 퍼즐 대기 장면 | H는 Store BGM을 들으며 대기. D cleanup 후 정식 요청 | 퍼즐 gameplay/공동 추천/추가 결과 기록 없음. 생략해도 Day 6 정상 |

**현재의 구현 경계:** Queue는 CustomerExited/cleanup 뒤 다음 고객을 spawn하므로 두 active customer가 겹치는 기능이 없다. Store BGM은 현재 기본 RS001을 재생하며 마지막 추천 LP가 그대로 계속되는 시스템이 아니다. 합석 Beat에서 방금 선택한 LP가 배경에서 계속 들린다고 쓰지 않는다.

**향후 Hook 제안만:** `OnPostResultInterludeRequested(CurrentVisit, NextVisit, InterludeID)` → 선택적 presentation → `InterludeFinished/Cancelled` → 기존 current customer Exit/cleanup → 기존 next spawn. 필요하면 arrival presentation을 별도로 설계하되, 두 번째 Customer Cycle/ActiveCustomer/spawn authority로 만들지 않는다.

Interlude 중 기존 Store BGM은 유지하고 새 LP 선택이나 History를 만들지 않는다. 다음 정식 Listening에서는 기존 StopStoreBGM을 사용한다. 승인 시 명시적 completion/cancel과 제한 시간 fallback으로 release를 보장해야 한다. 지금은 actor 대기/승격, 카메라, 입력, exit 지연, timeout 어느 것도 구현하지 않았다.

## 10. LP Content Requirement — 후보 기준 최소 추가 3장

### 실제 기존 catalogue

| RecordID | Mood | Genre | Theme | 현재 의미 |
|---|---|---|---|---|
| RS001 | Quiet | Jazz | Traditional | A에 3점 |
| RS002 | Quiet | Jazz | Sociable | A에 2점; E 후보에는 3점 가능 |
| RS003 | Restless | Electronic | Adventurous | A에 0점; B1/F 후보에는 3점 가능 |

파일명 `RS003_Poor` 등은 현재 A fixture 기준의 이름이다. 레코드의 전역 품질/모든 손님의 Result가 아니다. 음악 자산·RecordID·기존 태그를 이름 때문에 변경하지 않는다.

### 신규 LP 후보 — REVIEW_REQUIRED / Audio 미제작

| RecordID 후보 | Mood | Genre | Theme | Narrative role |
|---|---|---|---|---|
| RS004 | Quiet | Electronic | Adventurous | B2/B3에 조용하면서도 새로운 질감이라는 선택지를 제공. Electronic=항상 시끄러움이라는 고정을 피함 |
| RS005 | Quiet | Folk | Sociable | C/G의 작은 초대·말 걸기에 맞는 담백한 어쿠스틱 선택지 |
| RS006 | Quiet | Classical | Reflective | D/H의 혼자 생각할 여백과 긴 호흡을 받치는 선택지 |

RecordID는 예약 제안이며 이번 실행에서 실제 레코드나 audio 없는 placeholder를 추가하지 않는다. 제목/Artist/Cover/Audio/RPM·길이 등 최종 콘텐츠도 미확정이다. 새 audio가 없는데 기존 곡을 붙이고 신규 장르 콘텐츠가 완성됐다고 처리하지 않는다.

### 점수 검산

Formula는 그대로 `Mood 일치 + Genre 일치 + Theme 일치` 각 1점이다. 3=BEST, 2=GOOD, 0~1=POOR. 아래 숫자는 후보 preference에 대한 정확 일치 계산이며 실제 청취 품질 판정은 아니다.

| Target visit | RS001 | RS002 | RS003 | RS004* | RS005* | RS006* |
|---|---:|---:|---:|---:|---:|---:|
| A1/A2/A3 | 3 | 2 | 0 | 1 | 1 | 1 |
| B1/F | 0 | 0 | 3 | 2 | 0 | 0 |
| B2/B3 | 1 | 1 | 2 | 3 | 1 | 1 |
| C1/C2/G | 1 | 2 | 0 | 1 | 3 | 1 |
| D1/D2/H | 1 | 1 | 0 | 1 | 1 | 3 |
| E | 2 | 3 | 0 | 1 | 2 | 1 |

* RS004~RS006 are proposals only; no production audio/data added.

**최소 수량의 전제와 근거:** 승인된 각 목표 취향에 최소 한 장의 BEST가 있어야 한다는 콘텐츠 기준을 채택할 경우 신규 3장이 최소다. B2/B3, C/G, D/H의 새로운 완전일치 3요소 조합은 서로 다르며 기존 LP 어느 것도 3점이 아니다. 각 LP는 Mood/Genre/Theme 한 값씩 가지므로 한 장이 이 세 조합의 BEST를 동시에 담당할 수 없다. RS004/005/006 세 장으로 각각을 충족한다.

기존 3장만 쓰면 B2/B3·C/G는 최대 GOOD, D/H는 최대 POOR다. 이를 플레이어에게 완전한 정답이 있는 추천 과제로 제시하면 부당하다. 후보 취향을 바꾸거나 BEST 없는 설계를 명시적으로 승인한다면 수량은 줄일 수 있지만, 이는 다른 콘텐츠안이다. Day 7 두 고객의 취향까지 TBD이므로 **전체 최종본의 절대 최소가 3장이라고 확정하지 않는다**. Day 7을 승인된 기존 6장 안의 취향으로 정할 경우 추가분을 늘릴 필요는 없다.

**Production 전제:** 현재 선택 UI는 3개 버튼/3개 authored MakeStruct catalogue다. 3장 추가는 CSV에 행만 넣는 작업이 아니다. 승인 후 단일 catalogue 데이터와 가변 개수 선택 UI를 마련하고 canonical SelectedRecord 이벤트 경로, cursor/focus, turntable audio를 보존해야 한다. Mood별 대사 라우팅 문제도 함께 해결해야 한다. 오늘 UI나 계산식은 변경하지 않았다.

## 11. Production Data에 바로 유지/연결할 수 있는 항목

| 항목 | 현재 상태 / 이번 실행 처리 | 후속 작업 |
|---|---|---|
| 7일 Schedule의 CustomerID/VisitNumber/Day/OrderInDay | LOCKED_EXISTING; 정확한 16개 방문을 감사로 확인 | 그대로 참조. 후보 인물명을 ID 대신 key로 쓰지 않음 |
| A1 → BP_Customer01 / 기존 C01 5행 | CONNECTED_EXISTING; 원본 프로필과 asset hash 확인, 수정 없음 | 새 대사로 대체하거나 복사하지 않음 |
| A2/A3 → 기존 BP_Customer01 presentation | CONNECTED_EXISTING; 현재는 아직 C01 placeholder dialogue | 승인된 명시적 Narrative sequence를 붙인 뒤에만 Story 구현 완료로 표시 |
| Revisit Memory API / OnRevisitMemoryReady | CONNECTED_EXISTING; 고객/방문별 snapshot 사용 계약을 이 문서에 정의 | query/라우팅 소비자만 후속 구현. 내부 History 직접 순회 금지 |
| Day 7 → FinalStoryEvent | CONNECTED_EXISTING; 기존 hook ID 유지 | Ending을 붙이지 않고 아래 facts contract 사용을 검토 |
| RS001~RS003 / A 점수 3·2·0 | LOCKED_EXISTING; 기존 실제 catalogue 태그를 사용해 제안만 검산 | 기존 LP를 다른 ID나 전역 BEST/POOR 등급으로 재분류하지 않음 |

**이번 실행은 문서만 추가했다.** 기존 안전한 연결은 이미 존재한다. 새로운 A 재방문 sequence는 아직 승인된 대사가 없고, 현재 Mood-only selector에 새 행을 추가하는 방식도 안전하지 않아 `.uasset/.umap`을 변경하지 않았다. 이것은 신규 콘텐츠 연결 완료라는 보고가 아니다. import용 production JSON/CSV, 비활성 StoryEventID, audio 없는 LP도 추가하지 않았다.

## 12. 사용자 확정이 필요한 항목 / 제작 순서

| 결정 항목 | 검토 제안 | 승인 전 금지 |
|---|---|---|
| A2/A3 상황·payoff | 말 고르기 → 평범한 약속, 취향 이해의 누적 | 영구 대사 작성/적용, 가족·직업·화해 사건 확정 |
| B/C/D 인물과 Arc | 위 각 한 안을 출발점으로 검토 | 이름·외형·프로필·Dialogue 자산 적용 |
| E/F/G/H Episode | 짧은 요청과 반응 방향만 검토 | 추가 Arc/퀘스트/다음 방문 약속 |
| 취향과 신규 tag | Folk/Classical/Reflective, B 방문별 Quiet 전환 | 현재 Customer profile 덮어쓰기 |
| LP 3장 후보 | 모든 승인 취향에 BEST를 제공하는 기준 | RecordID 예약 확정, audio/cover 대체 투입 |
| Dialogue 길이/정보량 | 주요 재방문에 짧은 기억 + 하나의 현재 Beat | 조합별 전체 대본 대량 생성 |
| Tutorial과 A1 반복 소개 | 기존 mechanical 반복을 유지할지 추후 연출 검토 | Tutorial을 A1로 합치거나 History 번호 변경 |
| 합석 두 후보 | 선택적 짧은 interlude; 없어도 진행 가능 | 겹침 actor/camera/input/queue 시스템 구현 |
| Day 7 두 고객 | 일반 고객 2명 유지, 내용/취향 TBD | A~H 재방문으로 임의 치환, 최종 사건 작성 |
| Ending | TBD 유지 | 엔딩 내용·분기·호감도 총합·멀티엔딩 구현 |

승인 후 제작 순서는 (1) 인물/취향/Beat 확정 → (2) 명시적 Dialogue sequence 진입과 shared catalogue/ID resolve 계획 확정 → (3) A1 보존 regression을 둔 A2 소량 적용 → (4) A3와 B/C/D 단계 적용 → (5) 단발 인물과 신규 LP의 실제 audio/UI 통합 → (6) 필요할 때만 합석을 별도 Gate로 진행하는 것을 권한다. A1 원문, Schedule, scoring, History 저장 authority를 별도로 복제하지 않는다.

## 13. Day 7 FinalStoryEvent와 Ending TBD

Hook의 위치는 기존 그대로 `Day 7 Customers Complete → FinalStoryEvent`다. 이 시점에는 cleanup 뒤여서 ActiveVisit이 없으므로 GetActiveVisitMemory로 마지막 손님의 맥락을 추정하지 말고 고객 ID/방문 번호 기반 History API를 사용한다. 다음은 이후 소비할 **사실 정보 제안**이며 Ending selector/새 저장 시스템이 아니다.

| Narrative 정보 | 조회 source / 의미 | 주의 |
|---|---|---|
| Day progression | CurrentDay=7, FinalStoryEventTriggered, 실제 Day/Queue completion | 다시 Day를 시작하거나 FinalStoryEvent를 두 번 발생시키지 않음 |
| 완료 방문 | WeekSchedule와 현재 Day/Queue 완료 상태; 필요 시 기존 OnCustomerVisitCompleted event 소비 | 최종 Queue 완료로 예정 방문의 cycle 종료를 확인할 수 있으나 별도 방문 완료 history 배열은 현재 없음. 개별 기록이 필요하면 기존 event를 소비해야 함. 게임 진행 완료와 Story 전달 완료는 별개 |
| Recommendation History | 고객별 GetRecommendationHistory/GetRecommendationForVisit의 사본 | ID·방문·Day·LP·Score·Result·Sequence를 그대로 읽음. 총합을 호감도/엔딩 점수로 만들지 않음 |
| 주요 Arc 전달 여부 | 후속 명시적 sequence의 delivery 완료가 source여야 함 | 현재 구현 없음. placeholder C01 대화와 History 16개만으로 A/B/C/D Story 완료라고 표시하면 안 됨 |
| 누락·fallback 여부 | 후속 Narrative 소비자의 content validation/NO_MEMORY 경로 | missing을 POOR나 실패 Ending으로 치환하지 않음 |
| Optional overlap | 후속 interlude의 완료/생략 상태, 필요할 때만 | Arc 완료나 FinalStoryEvent의 필수 조건으로 삼지 않음 |

Story delivery 추적이 필요해지면 기존 세션 owner 안에서 `(CustomerID, VisitNumber, SequenceID)`의 전달 완료를 받는 작은 `NarrativeVisitFinished` Hook을 검토한다. 현재 존재하는 기능으로 표시하거나 새 Story manager/Relationship manager를 만들지 않는다. Ending이 확정되기 전에는 이 정보가 없어도 기존 FinalStoryEvent를 막거나 자동 엔딩을 선택하지 않는다.

A/B/C/D의 이야기 내용은 종료 지점 이전에 작게 마무리하는 후보이지만, 그 마무리가 부모님의 귀환/가게의 미래/플레이어의 진로에 어떤 의미인지 정하지 않는다. **FinalStoryEvent 이후의 장면·텍스트·엔딩 수·조건은 전부 TBD.**

## 14. 이번 실행 결과와 검증

- 새 작업 파일: 이 문서 한 개(unstaged).
- Production asset, canonical Dialogue, Record catalogue, Schedule, History 구현은 변경하지 않음.
- Fresh Editor 감사는 read-only이며 compile/cook/E2E 회귀 검증을 이번 문서 작업에서 새로 수행한 것으로 보고하지 않는다. 기존 History Gate의 결과와 구분한다.
- 문서 내 score matrix, 16개 Schedule, A1 원본 hash, local reference 및 git 상태를 검증한다. 상세 결과는 아래 검증 기록에 기재한다.
- staging / commit / push는 수행하지 않는다.

검증 기록:

- Editor read-only 감사 PASS: `20261109T072956Z-seven-day-content-audit-process.json` (exit 0; gameplay unexpected error 0; 알려진 engine startup smoke error는 별도 분류).
- Schedule 16개 / A 기존 Dialogue 행 5개 일치.
- 주요 Production asset 8개 SHA-256 동일; git에서 기존 tracked 파일 변경 없음.
- 실제 catalogue와 제안 태그의 score matrix 검산 PASS. 후보별 BEST coverage 조건에서 신규 LP 최소 3장; Day 7 내용에 따른 추가 가능성은 미정.
- 설계 독립 리뷰: 중요한 미해결 질문/충돌 없음. 이 결과는 후보 콘텐츠의 사용자 확정 또는 runtime 제작 승인을 의미하지 않음.
- 검증 상세: `Saved/MVPCompletion/seven-day-content-plan-validation.json`; LP 분석: `Saved/MVPCompletion/seven-day-lp-analysis.json`.
- 이번 실행에서 compile / cook / E2E를 재수행하지 않음(문서 전용 변경).
- staging / commit / push 없음. Branch / HEAD 유지.


