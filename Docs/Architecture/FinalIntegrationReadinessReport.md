# Final Integration Readiness Report

작성: 2026-11-11 KST. **보존 감사 PASS / 현재 Production checkpoint 이미 커밋됨 / 1080p Front-end 새 검증 PASS / 팀원 binary 통합·최종 Release는 보류.** 이번 Gate는 기능을 추가하지 않았다. staging/commit/push/merge/fetch/checkout/reset/clean/LFS 복구·prune, Engine/ACL/디스플레이 설정 변경을 하지 않았다. 기존 보고서와 Production 자산을 수정하지 않았다.

## 1. Git Baseline

| 항목 | 실제 시작 상태 |
|---|---|
| 경로 | D:/univ/3-1/GameEngine/Termproject/RecordShop |
| Branch | feature/customer-narrative-content |
| HEAD | 75b3a077c3030f319f42147a8a1d5d020303c634 |
| Commit | feat(recordshop): complete seven-day gameplay, narrative, and ending |
| Commit 시각/저자 | 2026-11-11 14:40:19 +0900 / 정우빈 — 기존 commit의 metadata |
| Modified / staged / deleted / untracked | 시작 시 모두0 |
| origin/develop 대비 | 현재 branch9 ahead /0 behind,234경로. origin/develop=2ed3fa0 |
| 원격 branch | GitHub connector가 현재 feature branch75b3a07과 로컬 origin snapshot 일치를 별도로 확인 |
| Worktrees | 현재 외에 roadmap_audit와 ui_integration2개. 조회만 수행 |

이전 Ending 보고서의 HEAD6c848a34·미커밋60개는 **과거 실행 기록**이다. 이번 시작 시에는 그60개가 기존 HEAD75b3a07에 이미 커밋돼 있었다. 이 commit을 이번 agent가 만들거나 push한 것이 아니며, 분할하기 위해 기존 이력을 되돌리지 않는다. [시작 status·tracked791 SHA·ignored inventory](../../Saved/IntegrationReadiness/20261111T054221Z-baseline/baseline.json), [commit 원문](../../Saved/IntegrationReadiness/20261111T054221Z-baseline/recent-commit.txt), [refs/worktrees](../../Saved/IntegrationReadiness/20261111T054221Z-baseline/branches.txt).

일반 git status는 exit0/clean이며 `ArtSource/Audio/Music/recordshop-expansion-fiqbw4uv` 열거 권한 경고는 남았다. 해당 디렉터리가 현재 비어 있다고 재확정하지 않는다. tracked791개는 전부 읽을 수 있었다. [이전 증거와 현재 파일 대조](../../Saved/IntegrationReadiness/prior-evidence-current-source-match.json): 이전788개 중787개 동일, 유일한 Ending 보고서 변경은 최신 재감사 증거의 report SHA와 일치한다. 따라서 기존 runtime 성공과 같은 Production/source 내용임을 확인했지만, 그 테스트를 이번에 새 실행한 것으로 표시하지 않는다.

## 2. 전체 파일 분류 / 보존

분류는 이번 감사의 주된 목적 기준이며 독점 소유권이나 삭제 허용 목록이 아니다. A는 기존 dependency 검사에서 실제 Shop/GameMode closure에 포함된 프로젝트249 package, 배포 고지2개와 프로젝트/config/LFS 설정이다. 미사용 prototype·예약 .gitkeep112개는 B로 분리했다. [실제 runtime 파일 목록](../../Saved/IntegrationReadiness/inventory/production-dependency-files.json).

| 분류 | 의미 | 시작 tracked791 | 기존 HEAD60경로 | develop 대비234경로 | 시작 ignored118834 |
|---|---|---:|---:|---:|---:|
| A | Production 필수 |258|14|77|0|
| B | Production 관련 Source / 보존할 비활성 자산 |405|9|45|0|
| C | Validation / Evidence |91|33|87|15979|
| D | Documentation |37|4|25|0|
| E | Generated / Temporary |0|0|0|102841|
| F | 출처 불명 또는 검토 필요 |0|0|0|14|

정확한 **모든 파일별** 경로·상태·분류·소유 영역·bytes·SHA256·LFS 여부는 [tracked791 CSV](../../Saved/IntegrationReadiness/inventory/all-tracked-v2.csv), [기존 HEAD60 CSV](../../Saved/IntegrationReadiness/inventory/recent-commit-v2.csv), [develop 대비234 CSV](../../Saved/IntegrationReadiness/inventory/feature-vs-develop-v2.csv)에 있다. Saved 포함 ignored는 [전체118834경로 CSV](../../Saved/IntegrationReadiness/inventory/ignored-manifest-v2.csv)에 분류했다. 숫자는 **감사 시작 스냅샷**이며 이후 이번 Gate의 새 Saved evidence는 증가분이다. 비교 CSV의 A/M은 이미 커밋된 과거 변경이지 현재 unstaged/staged 상태가 아니다. 이 범위에 삭제 경로는 없다.

Ignored 중 현재 Content의 누락 파일은 찾지 못했다. ignored Asset 총36535개 중 Cook/Stage/Archive 산출물이36522개이고, 나머지 **13개는 원본형 Asset snapshot**이다: Saved/Autosaves의 GFM/Turntable/Shelf/Interaction/Player/Map 등11개와 Saved/ArmPosePolish/CoverReach.baseline.uasset, Saved/TurntableBlocker/BP_Turntable.baseline.uasset. 또 Saved의 GFM .tmp1개를 F로 보존한다. 자동 복원하지 않았으며 현재 Content와 혼동하지 않는다. [13개 snapshot 및 기존 ignored Binaries14개의 SHA](../../Saved/IntegrationReadiness/inventory/important-ignored.json). Binaries의 RecordShop.exe/UnrealEditor-RecordShop.dll/target/PDB는 Generated E이며, 현재 프로젝트 uproject에는 Modules/Source가 없다. 이 exe가 완성된 배포물이라는 증거로 사용하지 않는다.

추가 F 디렉터리2개는 파일 수에 포함하지 않는다: 위 접근 불가 ArtSource 임시 폴더와 파일이 없는 `%SystemDrive%/ProgramData/Microsoft/Windows` 경로다. 생성자를 확인하지 못했고 삭제하지 않았다. .gitignore의 Saved/Binaries/DDC/Intermediate/pycache 정책을 유지했다. 중요한 Saved validation은 Git에 들어 있지 않으므로 로컬 증거를 지우면 새 checkout에서 보고서 링크만으로 재현되지 않는다. 이번 감사와 주요 이전 증거를 [선택적 evidence bundle](../../Saved/IntegrationReadiness/evidence-bundle-v2.zip), [SHA manifest](../../Saved/IntegrationReadiness/evidence-bundle-v2-manifest.json)에 별도 보존한다. 이 bundle은 전체 프로젝트/LFS 백업이 아니며 원본 Saved도 그대로 남는다. 외부 업로드는 하지 않았다.

### 기존 HEAD75b3a07의60경로 — 현재 미커밋 목록 아님

소유 영역 코드: CORE=정우빈 Integration/Core Flow/Camera, TT=전찬 Interaction/Recommendation/Turntable, NPC=주정은 NPC/AI/Animation, UI=조현우 UI/2D/Audio/Presentation, ENV=김민서 Environment/3D/Lighting, DATA=박준혁 Dialogue/Data/Narrative. 코드별 역할은 승인 명단 기준이고 경로의 예상 검토 책임을 나타낸다. Git alias와 실명을 새로 매핑하지 않았다. 공유 자산의 최종 연결은 Integration이 함께 검토한다.

| 과거 상태 | 분류 | 검토 영역 | 경로 |
|---|---|---|---|
| M | A | CORE | `Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset` |
| M | A | DATA+CORE | `Content/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition.uasset` |
| A | A | DATA+CORE | `Content/RecordShop/Data/Narrative/DA_I1_Narrative.uasset` |
| A | A | DATA+CORE | `Content/RecordShop/Data/Narrative/DA_J1_Narrative.uasset` |
| A | A | DATA+CORE | `Content/RecordShop/Data/Narrative/DT_I_Dialogue.uasset` |
| A | A | DATA+CORE | `Content/RecordShop/Data/Narrative/DT_J_Dialogue.uasset` |
| M | A | CORE | `Content/RecordShop/Data/Schedule/DA_Day07.uasset` |
| A | A | CORE | `Content/RecordShop/Data/Schedule/DA_Visit_I_1.uasset` |
| A | A | CORE | `Content/RecordShop/Data/Schedule/DA_Visit_J_1.uasset` |
| M | A | TT+CORE | `Content/RecordShop/Interaction/Components/BPC_Interaction.uasset` |
| A | A | UI | `Content/RecordShop/Licenses/NanumGothic_OFL_Full.txt` |
| A | A | UI | `Content/RecordShop/UI/Ending/WBP_Ending.uasset` |
| M | A | UI | `Content/RecordShop/UI/Result/WBP_Result_IntegrationFallback.uasset` |
| A | A | UI | `Content/RecordShop/UI/Title/WBP_Title.uasset` |
| A | D | CORE | `Docs/Architecture/Day7CustomerProductionReport.md` |
| A | D | CORE | `Docs/Architecture/Day7EndingContentPlan.md` |
| A | D | CORE | `Docs/Architecture/Day7EndingImplementationPlan.md` |
| A | D | CORE | `Docs/Architecture/EndingProductionReport.md` |
| M | C | CORE | `Scripts/Unreal/audio_handoff_validation_support.py` |
| A | C | DATA+CORE | `Scripts/Unreal/audit_customer_ij.py` |
| A | C | CORE | `Scripts/Unreal/audit_ending.py` |
| M | C | CORE | `Scripts/Unreal/cook_mvp.py` |
| M | C | DATA+CORE | `Scripts/Unreal/customer_b_validation_support.py` |
| A | B | DATA+CORE | `Scripts/Unreal/customer_ij_dialogue.json` |
| A | C | DATA+CORE | `Scripts/Unreal/customer_ij_reference.json` |
| A | C | DATA+CORE | `Scripts/Unreal/customer_ij_validation_support.py` |
| A | B | CORE | `Scripts/Unreal/ending_content.json` |
| A | C | CORE | `Scripts/Unreal/ending_reference.json` |
| A | C | CORE | `Scripts/Unreal/ending_runtime_support.py` |
| A | C | CORE | `Scripts/Unreal/ending_validation_support.py` |
| A | B | CORE | `Scripts/Unreal/fix_ending_quit_tick.py` |
| A | B | CORE | `Scripts/Unreal/fix_ending_stale_day.py` |
| A | B | CORE | `Scripts/Unreal/fix_ending_validation_boot.py` |
| M | C | CORE | `Scripts/Unreal/history_validation_support.py` |
| A | B | DATA+CORE | `Scripts/Unreal/install_customer_ij.py` |
| A | B | CORE | `Scripts/Unreal/install_ending.py` |
| A | C | CORE | `Scripts/Unreal/package_ending.py` |
| A | B | CORE | `Scripts/Unreal/polish_ending_title.py` |
| M | B | CORE | `Scripts/Unreal/record_expansion.json` |
| M | C | CORE | `Scripts/Unreal/record_expansion_support.py` |
| A | C | DATA+CORE | `Scripts/Unreal/run_customer_ij_gate.py` |
| M | C | CORE | `Scripts/Unreal/run_mvp_validation.py` |
| M | C | DATA+CORE | `Scripts/Unreal/run_narrative_gate.py` |
| A | C | DATA+CORE | `Scripts/Unreal/test_customer_ij_source.py` |
| A | C | CORE | `Scripts/Unreal/test_ending_source.py` |
| M | C | CORE | `Scripts/Unreal/validate_audio_handoff_contract.py` |
| M | C | DATA+CORE | `Scripts/Unreal/validate_customer_b_contract.py` |
| M | C | DATA+CORE | `Scripts/Unreal/validate_customer_cd_contract.py` |
| M | C | DATA+CORE | `Scripts/Unreal/validate_customer_efgh_sequences.py` |
| A | C | DATA+CORE | `Scripts/Unreal/validate_customer_ij_contract.py` |
| A | C | DATA+CORE | `Scripts/Unreal/validate_customer_ij_cycles.py` |
| A | C | DATA+CORE | `Scripts/Unreal/validate_customer_ij_sequences.py` |
| M | C | CORE | `Scripts/Unreal/validate_day_schedule.py` |
| M | C | CORE | `Scripts/Unreal/validate_day_week.py` |
| A | C | CORE | `Scripts/Unreal/validate_ending_contract.py` |
| A | C | CORE | `Scripts/Unreal/validate_ending_quit.py` |
| A | C | CORE | `Scripts/Unreal/validate_ending_runtime.py` |
| A | C | CORE | `Scripts/Unreal/validate_ending_week.py` |
| M | C | DATA+CORE | `Scripts/Unreal/validate_narrative_contract.py` |
| M | C | CORE | `Scripts/Unreal/validate_record_expansion_runtime.py` |

## 3. Production 필수 자산 / authority

[249개 실제 project dependency](../../Saved/IntegrationReadiness/inventory/production-dependency-files.json)와 Config/고지를 포함한 A258개를 보존한다. 기반 dependency344/Blueprint30은 이전20261111T052518Z 검사이며 이번에 다시 compile하지 않았다.

| 역할 | 보존하는 canonical 자산 / 소유 영역 |
|---|---|
| Flow/Queue/History/Ending/Title | Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset — CORE |
| Interaction gate | Content/RecordShop/Interaction/Components/BPC_Interaction.uasset — TT+CORE |
| SelectedRecord 전달 / Listening | BP_RecordShelf / BP_Turntable — TT+CORE, 새 GameInstance authority 없음 |
| NPC Spawn/Exit/Animation | Characters/Customers/Common/BP_Customer, Customer01/Blueprints/BP_Customer01 및 기존 montage/ABP — NPC |
| Dialogue | 루트 Content/DialogueData, CustomerData, CustomerDialogue, DialogueManager와 RecordShop/Data/Narrative의 A~J/Tutorial 정의·DT — DATA+CORE |
| Record Catalogue | RecordShop/Data/Records/DA_RecordCatalogue, DT_RecordCatalogue, ST_RecordData — DATA+TT+UI |
| Day/Visit | 기존 Week/Day01~07/16 scheduled Visits — CORE+DATA |
| UI | RecordSelect, Dialogue, Turntable, Result_IntegrationFallback, Prologue, Ending/WBP_Ending, Title/WBP_Title, Nanum font — UI+CORE |
| 실제 통합 Map | Content/RecordShop/Maps/Greybox/L_RecordShop_Greybox.umap — ENV+CORE |
| Audio | RecordShop/Audio/Music의 RS001~006 및 기존 SFX — UI+TT+CORE |
| Release 고지/설정 | Licenses/NanumGothic_License.txt, NanumGothic_OFL_Full.txt, Config5개, RecordShop.uproject, .gitattributes |

AssetOwnership/MapPolicy의 L_RecordShop_Main은 과거 계획명이다. 현재 Main/Test 폴더는 예약 .gitkeep이고 실제 IntegrationMap이라는 asset은 없다. 새 map을 만들어 맞추지 않는다. 공유 binary 소유권은 기존 [AssetOwnership](../AssetGuide/AssetOwnership.md)에 따라 명시적으로 인계한 뒤 편집해야 한다.

## 4. Git LFS 상태와 오류

### 현재 읽기 전용 검사

Git2.51.0.windows.1 / git-lfs3.7.0. .gitattributes는 uasset/umap/blend/fbx/glb/gltf/psd에 filter=lfs/diff=lfs/merge=lfs/-text를 적용한다. 실제 현재454경로는 uasset442 +umap3 +fbx7 +blend2다. [pointer/object 무결성](../../Saved/IntegrationReadiness/lfs/pointer-object-integrity.json): **454개 모두 HEAD의 canonical pointer 형식, 예상 size/SHA256, Working Tree의 실체, 로컬 .git/lfs/objects 실체가 일치**한다. Working Tree가 LFS pointer만 남은 Production asset은0개다. 현재 필수 자산 손상·누락을 찾지 못했다.

현재 git lfs status/env/ls-files --all --long/logs last는 모두 exit0이다. status는 push/commit/not-staged 목록이 비었다. [전체 stdout/stderr·trace/trace2와 명령](../../Saved/IntegrationReadiness/lfs/20261111T054313Z-commands.json)을 보존했다. git lfs status 성공은 원격 LFS 서버의 모든 객체 존재를 검사한 결과가 아니다. WAV/PNG/SVG는 현재 일반 Git 추적이며6개 음악 WAV는 각 약5.5~6.3MB다. 현재 tracked50MiB 초과 파일은 없다. 이번에 LFS 정책·history migration을 바꾸지 않는다.

### 과거 오류와 이번 재현 한계

기존 보고서의 `couldn't create signal pipe, Win32 error5`는 Git for Windows/MSYS subprocess 생성·권한 계층 오류 서명이다. 이번 clean tree의 동일 조회에서는 재현되지 않았다. 현재 trace가 성공했다고 과거 원인을 해결했다고 표시하지 않는다. 과거 raw signal-pipe 전체 로그는 지정 snapshot JSON에서 찾지 못했고 문서 기록을 근거로 남긴다. 정확한 당시 OS/token 조건은 재확정하지 못했다. 오류를 만들기 위해 asset/mtime를 건드리거나 clean filter를 강제 실행하지 않았다.

`git lfs logs last`가 반환한 별도 로그는 **2026-09-23 UTC의 과거 filter-process**에서 .git/lfs/tmp/3230474601 → objects/6d/9b/... rename Access denied다. November의 signal-pipe 오류나 이번 발생 오류로 혼동하지 않는다. 이번 managed 환경의 .git 쓰기 제한과 맞는 형태지만, 당시 토큰까지 증명한 것은 아니다. 이 로그도 원문 보존했다. 객체를 이동할 수 있는 git lfs fsck, fetch/pull/checkout/prune/repair를 실행하지 않았고, 필요한 검사는 파일 읽기와 SHA 대조로 수행했다. [공식 pointer spec](https://github.com/git-lfs/git-lfs/blob/main/docs/spec.md), [Git filter 설명](https://git-scm.com/docs/gitattributes), [fsck의 bad-object 이동 동작](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-fsck.adoc)을 구분 근거로 참조한다.

### 현재 HEAD 외 후보 객체5개 누락

전체 refs의786개 unique LFS OID 중5개 실체가 **로컬에 없다**. 전부 현재 Production454개 밖의 후보다. 나머지 과거 객체는 존재 여부를 조사했으며 현재454개처럼 전체 historical payload SHA까지 검사했다고 주장하지 않는다.

| 후보 head / 자산 | 로컬 누락 SHA256 |
|---|---|
| customer-ai136921b / BP_Customer |32bb1fdcd6b923255edf013e758a8542cc4b720741c65942d55359626c1b82a8|
| customer-ai136921b / BP_Customer01 |f0a0bbd5a82fc5972df387ad3bfe3d868bcf865b8c9c30334ccfb99fecef630f|
| dialogue-data798cee1 / CustomerData |c1bcc510c604dfd5ad2c82931c527fe7669148755856d59490309ad16007cd3a|
| dialogue-data798cee1 / CustomerDialogue |a60ab3e9c98608704613485c1745db464778df5b3c8d6121d7f437cd4e495091|
| dialogue-data798cee1 / DialogueManager |40aeb1fe2dd1b6217355b54a005c3b591ade7013172f964146903f31d46d5e94|

이5개는 실제 팀원 branch head pointer와 일치한다. 원격에도 없다는 뜻은 아니지만 현재 checkout에서 binary 검토/import를 진행할 수 없다. 원격 인증·LFS download/upload·push 검증은 수행하지 않았다. 직접 git ls-remote 읽기는 SEC_E_NO_CREDENTIALS였고 GitHub connector metadata 조회는 성공했다. **현재 Production 보존 PASS**, 후보 binary 검토/원격 객체 가용성은 **BLOCKED**로 분리한다. 현재 push-pending 목록0을 전체 remote LFS 검증 PASS로 확대하지 않는다.

## 5. Packaging 실패 원인

[정확한 조사 결과](../../Saved/IntegrationReadiness/packaging/20261111T054345Z/triage.json), [설치 UAT source 발췌](../../Saved/IntegrationReadiness/packaging/20261111T054345Z/installed-uat-source-excerpts.txt). 마지막 실행은 [20261110T162441Z result](../../Saved/MVPCompletion/20261110T162441Z-ending-package/result.json), [원문 stdout](../../Saved/MVPCompletion/20261110T162441Z-ending-package/stdout.txt)이며 전체 exit1이다. Cook는 exit0 뒤 Stage에서 아래 파일 쓰기가 거부됐다.

`C:/Program Files/Epic Games/UE_5.8/Engine/Intermediate/Build/BuildCookRun/StagedBuild_RecordShop.ini`

설치 CopyBuildToStagingDirectory.Automation.cs:1860~1865가 SC.EngineRoot 아래 임시 source marker를 만들고 최종 Stage의 Engine/Config로 복사한다. -stagingdirectory는 최종 StageDirectory, -archivedirectory는 Archive를 지정할 뿐 이 marker를 옮기지 않는다. 마지막 명령은 이미 project-local의 분리된 Stage/Archive였다. EngineSaved/log/cooker UserDir도 이 쓰기에 관여하지 않는다. 지원되는 marker-only project-local override는 찾지 못했다. skipstage/prestaged는 완성된 Stage가 필요하고 cook-on-the-fly는 self-contained release와 다른 검사이므로 대체 PASS로 쓰지 않는다.

읽기 전용 ACL 검사상 해당 폴더와 기존0-byte marker에 Users/surlw FullControl이 있고 read-only도 아니다. 따라서 **일반 Windows 사용자 ACL이 고장났다고 단정하지 않는다.** 이번 managed session은 Engine 설치 경로 쓰기를 허용하지 않으며 이것만으로 실행 차단을 설명할 수 있다. 정확한 과거 프로세스 토큰의 모든 제한을 재현한 것은 아니다. Engine/ACL/관리자 권한 변경·쓰기 probe·Engine 복제·UAT patch 없이 안전하게 수행할 새 packaging 경로는 확인되지 않아 **이번 재실행은 BLOCKED**로 유지했다.

ArtSource 임시 폴더의 별도 열거 거부는 이 Stage stack에 없고, 직전 Cook도 성공했다. 이를 packaging 원인으로 연결하지 않는다. [최신 같은 자산 Cook](../../Saved/MVPCompletion/20261111T052534Z-cook-final-process.json)은 exit0/errors0, 이전20261110T162035Z와 모든 cooked_* 목록이 동일하다.733 cooked +7 skipped이며 기존 LogSsl root-store warning1개는 남는다. SkipSaveAssetRegistry loose Cook는 Stage/Archive/배포 exe/고지 포함을 검사하지 않는다. 이번 Gate에서 새 Cook를 실행한 것은 아니다.

다음 실행은 managed agent 밖의 **일반 비관리자 PowerShell**에서 repo root의 `python Scripts/Unreal/package_ending.py`다. 매번 새 timestamp 출력 폴더를 쓰므로 기존 build를 덮어쓰지 않는다. 성공을 보장하지는 않지만 현재 보이는 일반 사용자 ACL상 관리자/ACL 수정을 선행할 이유는 없다. command/stdout/result/실제 Archive/생성 FileOpenOrder를 보존하고 exit0 +실제 RecordShop.exe +Nanum 고지/전문을 확인해야 한다. 정상 사용자에서도 실패하면 원문과 함께 이미 권한이 허용된 build 환경으로 넘긴다.

## 6. 1080p 차단 원인 / 이번 해결된 검증

**이번 PRE-MERGE의 새 PASS:** [process-result](../../Saved/IntegrationReadiness/20261111T055000Z-viewport-1080-before-pie/process-result.json), [runtime-result](../../Saved/IntegrationReadiness/20261111T055000Z-viewport-1080-before-pie/runtime-result.json), [viewport observer](../../Saved/IntegrationReadiness/20261111T055000Z-viewport-1080-before-pie/viewport-observer.json), [원본 Title PNG](../../Saved/IntegrationReadiness/20261111T055000Z-viewport-1080-before-pie/runtime-result-cold-title.png), [상세 triage](../../Saved/IntegrationReadiness/20261111T055000Z-viewport-1080-before-pie/triage-summary.json). 실제 실행 UTC05:48:31~05:49:26, exit0, complete/pass=true, unexpected gameplay errors0. 알려진 pre-init smoke15개는 분류해 원문을 유지했다.

- 물리 display2개는 각각1920×1080(165/144Hz)다. DPI-unaware 프로세스가 관찰한 system/window DPI96, logical virtual screen은2677×2160, 원점(0,-1080)이다. 이96 값을 Windows 설정이 무조건100%라는 뜻으로 해석하지 않는다. [실측 display inventory](../../Saved/IntegrationReadiness/20261111T055000Z-viewport-1080-before-pie/display_inventory.json).
- 설치 LevelEditorSubsystem.editor_request_begin_play는 active embedded PIE를 선택한다. NewWindowWidth/Height 또는 일반 -ResX/-ResY만 주어도 이 API가 Standalone/New PIE Window로 바뀌지는 않는다. 별도 Standalone에는 독립 game viewport를 지정할 수 있지만 이번 성공은 Standalone/packaged launch가 아니다.
- 기존 helper는 game viewport 대신 **Editor 전체 HWND**를 확대했다. 같은1644×1080을 다시 재현했을 때 outer/client는2697×1256이었고2697은 Win32 max-track width와 같았다. Editor panels1053px/chrome176px 때문에 필요한 viewport를 확보하지 못한 것이다. raw WM_GETMINMAXINFO의 max_track=[0,0]은 초기값 없는 diagnostic이므로 실제 limit으로 사용하지 않는다.
- 지원되는 `LevelEditor.ToggleImmersive`를 **PIE/Title 생성 전** editor world에서 실행하고 animation 후 기존 exact-size helper를 호출했다. 패널을 숨겨 실제 PlayerController viewport1920×1080을 확보했다. OS 해상도/DPI·프로젝트 Config·Production Asset 변경은 없다.
- 기존 focus assertion을 유지했다. Title 생성 뒤 Immersive를 켰던 중간 시도는 focus를 빼앗아 FAIL했고 그대로 보존했다. 성공 실행은 Title의 production focus가 자연스럽게 설정된 후 가상 Enter로 진행하며 테스트가 focus를 강제로 복구하지 않는다.
- Title1장+Ending/Credits9장 **원본 PNG10개가 모두1920×1080**이다. resize/crop 이미지를 증거로 사용하지 않았다. Observer는9면과 Title 복귀까지 실제 PC viewport를 검사했다. Agent가10장을 확인했고 한글·팀원 역할·긴 고지·버튼의 잘림/겹침은 보이지 않았다.

검증 범위는 기존 **RS003 완료 Day7/accepted Result unsaved fixture1개**의 Cold Title/New Game/Ending/Credits/Title/audio0/fresh New Game이다. 고객17 Cycle, 모든 플레이 UI의1080p 또는 packaged1080p 검증을 이번 PASS로 주장하지 않는다. 고객/Turntable UI와 실제 장치1080p QA는 남는다. 기존20261110T153010Z의1080p PASS 및20261111T052325Z의 FAIL은 별도로 보존했다.

시도4개도 구분했다: 새 DDC setup62초 중단=BLOCKED, readonly-only DDC fallback34초 중단=BLOCKED, 실제1080 Title 확보 뒤 focus assertion=FAIL, PIE 이전 Immersive 최종 실행=PASS. 새 setup의 Zen fallback은 AppData metadata 쓰기를 로그에 시도했지만 기존 파일 timestamp는 과거 날짜 그대로였고 실제 변경 증거는 없었다. 성공 명령은 memory+readonly DDC와 -DDC-NoDefaultGraph, fresh UserDir, -nowrite/-NoAssetRegistryCacheWrite로 fallback·설정 저장을 방지했다. [정확한 명령](../../Saved/IntegrationReadiness/20261111T055000Z-viewport-1080-before-pie/command.json). 재실행 시 기존 evidence 폴더를 덮어쓰지 말고 두 Saved script를 새 고유 폴더에 복사해 run_viewport.py를 실행한다.

## 7. 팀원 Feature/PR 통합 위험

[전체16개 PR·소유 영역·파일별 blob/OID·ancestry 보고서](../../Saved/IntegrationReadiness/pr/pr-triage.md), [실시간 GitHub snapshot](../../Saved/IntegrationReadiness/pr/github-pr-snapshot.json), [branch audit](../../Saved/IntegrationReadiness/pr/local-branch-audit.json). GitHub connector로 원격12개 origin head와 fork UI head를 별도 조회했고 로컬 snapshot과 일치했다. Git fetch/PR 수정/댓글/merge는 하지 않았다.

열린 PR은0개다. 총16개 중14개 merged, [#4](https://github.com/jllgame00/GameEngine-TermProject/pull/4)/[#9](https://github.com/jllgame00/GameEngine-TermProject/pull/9)는 closed unmerged다. 다만 #4의 과거 head는 후속 통합으로 이미 현재 ancestry에 들어 있으므로 pending으로 세지 않는다. #9는 ancestry 밖이지만 shelf/counter 등 선택 통합돼 있다. [#14](https://github.com/jllgame00/GameEngine-TermProject/pull/14)의 NPC/Animation 작업도 이미 통합됐다. [#16](https://github.com/jllgame00/GameEngine-TermProject/pull/16)의 develop head는 현재 ancestry에 있고 main-only release merge가 별도인 것은 예상된 상태다. branch가 존재하는 것과 열린 PR/미통합 기능은 구분한다.

| 영역 | 현재 후보 tip | 현재 Production 대비 ahead/behind | branch-introduced files: same/different/absent | 판단 |
|---|---|---|---|---|
| TT / Recommendation | origin/feature/turntable-recommendation bc8c7b7 |7/55|26/19/73|현재 TT/Shelf/선택 UI/map과 충돌. 과거 GameInstance/RPM prototype을 통째로 복원하지 않음 |
| NPC / AI / Animation | origin/feature/customer-ai136921b |1/9|0/2/0|공통base2ed3fa0 이후 신규 shared-talking-montage 변경2개. Production은 그2개를 base 이후 수정하지 않았지만 후보 LFS2개 누락으로 binary 검토 BLOCKED |
| UI / 2D / Audio | fork/feature/ui-presentation32d909c |5/55|0/0/6|ThirdPerson prototype6 Widget. 현재 UI와 경로는 달라도 기능 중복. origin UI9df85c7는 오래된 scaffold이며 Audio 신규 변경 없음 |
| ENV / 3D / Lighting | origin/feature/environment-art9927497 |3/55|25/12/69|테스트맵/생성 assets54개 포함. 이미 선택 통합된 content와 구분 |
| DATA / Narrative | origin/feature/dialogue-data798cee1 |5/55|1/3/4|루트 authoritative3개가 현재와 다르고 후보 LFS3개 누락. organized old copies4개를 추가하면 경쟁 authority 위험 |
| CORE | 현재 feature/customer-narrative-content75b3a07 |develop 대비9/0|234경로|현재 GFM/History/6LP/A~J/Ending/Title authority 보존 |

**ENV106개 변경이 모두 TT branch에도 있으며 branch blob이106개 전부 동일하다.** 두 branch를 별도 기능으로 세어 중복 도입하면 안 된다. same/different는 같은 경로의 Git blob(자산은 LFS pointer) 비교이며 payload SHA도 별도 기록했다. absent는 해당 경로에 없다는 뜻일 뿐 Production에 반드시 필요하다는 뜻이 아니다. 경로를 바꿔 이미 변형 통합한 semantic duplication 가능성은 byte 비교만으로 배제하지 못한다.

핵심 충돌: BP_Turntable/Shelf/RecordSelect/Greybox는 TT·ENV·CORE가 겹치며, root CustomerDialogue/Data/DialogueManager는 DATA·현재 Narrative가 겹친다. GFM/RecordCatalogue/Ending UI는 현재 canonical version을 기준으로 연결한다. 전체 옛 branch를 ours/theirs 또는 폴더 checkout으로 덮는 방식은 승인된17Cycle/History16/6LP/audio cleanup을 잃을 수 있다. 현재 없는 prototype manager/widget/test map을 일괄 도입하지 않는다. 신규 NPC refactor는 작은 검토 후보지만 현재 Release에 반드시 필요한 기능으로 판단하지 않으며, asset payload와 회귀 검토 전에는 승인하지 않는다.

## 8. 권장 Commit 분할 계획 — 실행 안 함

1. **현재 baseline은 이미 commit75b3a07**이다. 이를 다시 분할하거나 amend/reset/rebase하지 않는다. 현재 기능 snapshot과 evidence를 기준점으로 유지한다.
2. 이번 새 FinalIntegrationReadinessReport.md만 별도 `docs: audit integration readiness and release QA blockers` commit 후보로 검토한다. Saved bundle/CSV/log는 자동 staging하지 않고 별도 artifact로 보존한다. 이 Gate에서는 문서도 staging하지 않았다.
3. 이후 명시적으로 승인된 QA tooling의 수정이 필요하다면 Production 변경과 분리한 `test: ...` 단위를 쓴다. 이번1080 해결은 Saved observer/command만으로 됐으므로 현재 Production patch를 만들 이유가 없다.
4. 향후 선택된 팀원 변경은 dependency-complete owner 단위로 검토한다. NPC2개와 대응 회귀는 한 단위, 필요한 ENV/UI 시각 asset은 선택 의존성 단위, shared map/GFM 최종 연결은 통합 소유자 단위다. 이미 integrated된 기능을 다시 가져오는 commit은 만들지 않는다.
5. 같은 binary를 여러 commit에서 반복 교체해 순서에 의존하게 만들지 않는다. 각 단위가 compile/dependency/focused regression을 통과한 뒤 최종17Cycle/History16와 package QA를 수행한다. 파일 경로만으로 기존 schema/widget/caller를 나누면 중간 commit이 깨질 수 있으므로 authoring source/검증 fixture도 함께 검토한다.

현재 판정: **작업물 보존과 현재 commit checkpoint는 준비됨. 무조건적인 team merge 또는 release 승인은 준비되지 않음.** 신규 Production commit이 필요한 상태가 아니다. 원격 LFS 가용성과 후보 binary를 확보하지 않은 채 통합을 진행하지 않는다.

## 9. Release QA Matrix

PASS=해당 근거/범위 통과, FAIL=실제 검사 실패, BLOCKED=실행/검토에 필요한 조건 미충족, MANUAL_REVIEW=사람의 판단·물리 장치 확인 필요. 아래의 이전 PASS는 이번 실행과 분리하며 현재 source hash 일치를 근거로 유지한다.

| 대상 | 판정 | 근거 / 새 실행 여부 / 남은 범위 |
|---|---|---|
| Cold Launch | PASS | 이번1080 Cold Title +이전 week. Editor/PIE 범위; packaged cold launch는 BLOCKED |
| Prologue / Tutorial | PASS | 이전 [20261111T051225Z week](../../Saved/MVPCompletion/20261111T051225Z-ending-reaudit-week-process.json), 재Tutorial→Day1 A 포함. 이번 full rerun 없음 |
| Day1~7 Full E2E /17Cycle /History16 | PASS | 위 동일 source 이전 week. 실제 customer navigation/queue, player geometry·가상 입력 fixture 포함 |
| Customer A~J / I·J 등급 | PASS | 위 week 및 이전30그룹 [aggregate](../../Saved/MVPCompletion/20261110T154617Z-customer-ij-gate.json). 이번 matrix 재실행 아님 |
| LP6종 / authored candidates | PASS | 이전 record/score/order/playback·fullweek, [기존 통합 evidence](../../Saved/MVPCompletion/ending-final-evidence.json). 이번 새 LP 추가/검사 아님 |
| Listening / Selected LP BGM | PASS | 이전 [Ending10사례](../../Saved/MVPCompletion/20261111T050959Z-ending-reaudit-recovered-720-process.json), 같은 track/voice/무음/0fade/EOF2회. 이번 RS003 UI flow에서도 유지·Title0 확인 |
| Ending / Credits / Title / fresh New Game | PASS | 이번1920×1080 single-case fixture 및 위 이전 fullweek. GFM canonical owner/단일 Ending |
| 720p Front-end | PASS | 이전1280×720 Ending10사례. 이번720p 재실행 없음 |
| 1080p Title/Ending/Credits | PASS | **이번 실제1920×1080/원본10PNG/production focus/exit0**. 모든 gameplay UI/packaged1080p 전체 검증은 아님 |
| 이전1080 실패/중간 focus 실패 | FAIL | 20261111T052325Z target-size 실패, 이번054800Z focus assertion 실패 그대로 보존. 최종 성공으로 원문 덮지 않음 |
| Keyboard 자동 UI | PASS | 실제 production focus+가상 Slate Enter, 이전 native input regression. 실제 사람 입력 승인 아님 |
| Mouse / Gamepad 실제 장치 | MANUAL_REVIEW | 미실행. 가상 Enter를 mouse/gamepad PASS로 표시하지 않음 |
| Audio Balance / 체감 Fade | MANUAL_REVIEW | 실제 청취·LP간 loudness·대화 balance·반복 피로도 필요 |
| Fade / Voice Leak 기술 상태 | PASS | 이전10사례 +이번RS003 Title voice0. 장시간/다기기 subjective QA는 별도 |
| Blueprint30 / Dependency344 | PASS | 이전 [20261111T052518Z](../../Saved/MVPCompletion/20261111T052518Z-ending-reaudit-dependencies-process.json), same source. 이번 재compile30 아님 |
| Host tests20개 | PASS | 이전 [통합 증거](../../Saved/MVPCompletion/ending-reaudit-final-evidence.json)의 실제20개 성공. 이번 host suite 재실행 없음 |
| Windows Cook | PASS | 이전 [20261111T052534Z](../../Saved/MVPCompletion/20261111T052534Z-cook-final-process.json), loose-cook 한정. 이번 새 실행 없음 |
| Windows Packaging | BLOCKED | 이전 UAT 전체 exit1, Stage Engine marker 쓰기 제한. 이번 retry 없음 |
| Packaged Launch / exe Quit / shipped notices | BLOCKED | 완성 Archive/exe 근거 없음. Binaries exe 또는 Editor Quit는 대체 증거가 아님 |
| 외부 Asset / Music License | BLOCKED | 로컬 합성 음악·커버 provenance/폰트 고지는 확인됨. Cigar_room/Fab Stereo/모델·외부 animation 취득 증빙과 shipped 고지 확인 필요 |
| 현재 Production LFS | PASS | 이번454개 pointer/실체/size/SHA 대조. 원격 저장소 전체 PASS 아님 |
| 팀원 후보 LFS / 원격 availability | BLOCKED | 이번 후보5개 로컬 미보유, 원격 payload 존재/전송 미검증 |

## 10. 미검증 / 남은 Release 차단

출시를 막는 항목은 정상 권한 환경의 complete package/packaged launch, 실제 입력·오디오 수동 승인, 외부 asset 권리 증빙 및 배포 고지다. 현재의1080p **Front-end** 차단은 이번 새 증거로 해소했으나 모든 gameplay UI·standalone·packaged1080p까지 완료된 것은 아니다. 장시간 플레이/여러 장치/다회차 전주 완주, 모든 BEST/모든 POOR 전주 별도2회는 추가 실행하지 않았다.

현재 Production payload와 source는 보존됐지만 후보5개 LFS 미보유가 새 NPC/Dialogue 통합 검토를 막는다. 이는 현재 Production asset 누락 또는 현재 package 실패 원인과 별개이며, 선택적 신규 refactor를 이번 release에 넣어야 한다는 의미도 아니다. 기존 Git/MSYS 오류의 정확한 당시 OS 조건과 원격 LFS 서버 상태는 미확정이다.

## 11. 다음 통합 단계의 안전한 순서

1. 현재75b3a07 baseline과 이 문서/evidence bundle을 검토·보존한다. old Saved 보고서 링크만 믿고 clean/일괄 삭제하지 않는다. 이번 Gate 종료 후 새 문서1개만 untracked이고 기존791개와 중요 ignored snapshot은 그대로여야 한다.
2. 추가 팀원 변경을 넣기 전에 현 baseline의 release blockers를 분리한다. 일반 비관리자 사용자 환경에서 `python Scripts/Unreal/package_ending.py`를 새 출력 폴더에 실행해 command/stdout/result/Archive를 확보한다. Engine·ACL 수정이나 관리자 강제 실행을 선행하지 않는다.
3. 실제 package의 Cold Title/New Game/Prologue/Tutorial/Day1~7/Ending/Credits/Title/restart/Quit,1920×1080, 물리 keyboard/mouse/gamepad, LP balance/fade/voice0와 notices를 확인한다. 외부 asset URL·권리자·취득 license 증빙을 owner와 확보한다. 미확정 rights는 출시 승인하지 않는다.
4. 이후 통합할 필요가 승인된 경우에만, 별도 허가된 retrieval 환경에서 **후보 head를 고정한5개 OID**의 LFS 실체를 확보하고 SHA 검증한다. 현재 checkout을 자동 복구/checkout하지 않는다. 현 baseline과 분리된 integration workspace 및 명시적 binary 소유권을 사용한다.
5. 가장 작은 신규 NPC136921b의2개 asset부터 base2ed3fa0/current와 inherited montage/dispatcher/function API를 검토하고 Tutorial/A~J spawn/dialogue/exit 회귀를 수행한다. 꼭 필요하지 않으면 release 이후로 미룬다.
6. ENV/TT 중복106개는 한 번만 검토하고 필요한 의존성만 선택한다. DATA의 root authority와 UI prototypes를 일괄 교체하지 않는다. shared GFM/map/catalogue 최종 wiring은 Integration owner가 현재 API 기준으로 수행한다.
7. 각 검토 단위 compile/dependency/redirector/map/focused regression 후17Cycle/History16/6LP/audio/Ending→Title→fresh New Game 전체와 Cook/package를 확인한다. 그 결과를 갖춘 뒤에만 별도 승인된 PR/commit/merge 절차로 이동한다. 이번 Gate는 그 절차를 실행하지 않았다.

보존 최종 증거: [final-preservation.json](../../Saved/IntegrationReadiness/final-preservation.json). Production 기능 변경0, 기존 파일 삭제/덮어쓰기0, staging/commit/push/merge0이다. release PASS는 부여하지 않는다.
