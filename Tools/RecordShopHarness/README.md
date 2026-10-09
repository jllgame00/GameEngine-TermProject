# RecordShop Autonomous Integration Harness

Worker → independent auditor → exact-file commit → push loop for the RecordShop UE project.

## Default models
- Worker: `gpt-6-astra`, reasoning `high`
- Auditor: `gpt-6.1-sol`, reasoning `high`

## Safety
- refuses `main` / `develop`
- requires clean worktree per round
- refreshes origin + UI teammate fork
- prefetches relevant LFS objects outside Codex when possible
- Codex only implements/tests; it does not commit/push
- second Codex pass independently audits the changes
- stages exact auditor-approved files only
- refuses commit if audit file list != actual changed files
- blocks known stale/dangerous paths
- commits/pushes using normal PowerShell permissions
- never merges to develop
- up to 3 autonomous repair rounds by default

## Install
Copy this `Tools\RecordShopHarness` directory to:

`D:\univ\3-1\GameEngine\Termproject\RecordShop_overnight\Tools\RecordShopHarness`

Before running:
1. Close Unreal Editor.
2. Worktree must be clean and on a feature branch.
3. `codex` must be installed/authenticated.

## Run

```powershell
cd "D:\univ\3-1\GameEngine\Termproject\RecordShop_overnight"
powershell -ExecutionPolicy Bypass -File ".\Tools\RecordShopHarness\Invoke-RecordShopHarness.ps1"
```

## One round

```powershell
powershell -ExecutionPolicy Bypass -File ".\Tools\RecordShopHarness\Invoke-RecordShopHarness.ps1" -MaxRounds 1
```

## No remote push

```powershell
powershell -ExecutionPolicy Bypass -File ".\Tools\RecordShopHarness\Invoke-RecordShopHarness.ps1" -NoPush
```

`-NoPush` still allows a local audited commit; it only skips the remote push.
