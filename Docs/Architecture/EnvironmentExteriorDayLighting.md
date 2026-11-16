# 가게 외부 + 요일별 조명 (Environment)

## 상태: 테스트맵에서 검토 중
- 메인 맵 `L_RecordShop_Greybox`는 **변경 없음**. 확인용 테스트맵 `Maps/Test/L_Env_ExteriorLighting_Test` (메인 맵 복사본 + 아래 서브레벨)
- 팀 확인 후 메인 맵에 같은 변경을 적용 (스크립트 재실행)

## 테스트맵에서 바뀐 것
- 테스트맵 (메인 맵 대비)
  - `GB_Wall_Front_L/R`, `Shop_Vestibule` 제거 → 쇼윈도 2개 + 유리 양문(닫힘, 충돌 있음)으로 교체
  - `TEST_DirectionalLight`, `TEST_SkyLight` 제거 (요일 프리셋으로 이동), `TEST_SkyAtmosphere` → `Shop_SkyAtmosphere`
- 새 서브레벨 (모두 `Maps/Greybox/`)
  - `L_RecordShop_Greybox_Exterior` (Always Loaded): 거리, 맞은편 건물, 간판, 차양, 가로등, 벤치 등. 액터 이름 `EXT_*`
  - `L_RecordShop_Light_Morning` (Initially Loaded/Visible) / `_Rain` / `_Sunset` / `_Closing` (Blueprint 스트리밍)
  - 문 팻말 글자도 조명 레벨에 들어 있음: 낮 프리셋은 밖 OPEN / 안 THANK YOU, Closing은 밖 CLOSED / 안 SEE YOU TOMORROW
  - Closing (엔딩 전용): 밤하늘, 가로등, 턴테이블 위 따뜻한 스포트 하나, 노출 하한 고정(밤이 다시 밝아지지 않게), 비네트
    - 각 레벨: 해(Directional), SkyLight, Height Fog, 색보정 PPV(우선순위 1, 노출은 건드리지 않음), 가로등 불빛(비/노을만). 액터 이름 `LGT_*`
- 머티리얼: `Art/Environment/Exterior/Materials` (`M_Ext_Base` + `MI_Ext_*`, `M_Ext_WindowGlass`)
- 재생성 스크립트: `Scripts/Unreal/build_shop_exterior.py`, `build_day_lighting_presets.py`, 에디터 미리보기 `preview_day_lighting.py`

## 요청: 날짜 시작 시 조명 바꾸기 (BP_GameFlowManager, BeginDay 쪽에 노드 몇 개)
연결 전에도 게임은 Morning으로 정상 표시됩니다.

1. Day → 프리셋: 1 Morning, 2 Morning, 3 Rain, 4 Sunset, 5 Rain, 6 Morning, 7 Sunset
2. 다른 두 레벨 `Unload Stream Level`, 해당 레벨 `Load Stream Level` (Make Visible After Load = true)
   - 레벨 이름: `L_RecordShop_Light_Morning` / `L_RecordShop_Light_Rain` / `L_RecordShop_Light_Sunset`
3. 날짜 전환 페이드(검은 화면) 중에 바꾸면 깜빡임이 안 보입니다.

## 요청: 엔딩 마감 연출 (BeginEnding 시작 부분)
1. 다른 조명 레벨 Unload → `L_RecordShop_Light_Closing` Load
2. `Shop_AreaLight00/01/10/11` 밝기 950 → 200 (매장 조명을 거의 끈 느낌)
3. (선택) 0.5초 정도 페이드 아웃/인으로 감싸기

조명 값이나 매핑은 바꾸고 싶으면 말해주세요. (김민서)
