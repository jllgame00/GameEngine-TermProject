param(
    [string]$RepoRoot = "D:\univ\3-1\GameEngine\Termproject\RecordShop_overnight",
    [string]$WorkerModel = "gpt-6-astra",
    [ValidateSet("low","medium","high","xhigh","max")]
    [string]$WorkerEffort = "high",
    [string]$AuditorModel = "gpt-6.1-sol",
    [ValidateSet("low","medium","high","xhigh","max")]
    [string]$AuditorEffort = "high",
    [ValidateRange(1,10)]
    [int]$MaxRounds = 3,
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "=== $Message ===" -ForegroundColor Cyan
}

function Invoke-Git {
    param([Parameter(Mandatory=$true)][string[]]$Args)
    & git -C $RepoRoot @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Get-GitText {
    param([Parameter(Mandatory=$true)][string[]]$Args)
    $out = & git -C $RepoRoot @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed"
    }
    return (($out | Out-String).Trim())
}

function Get-ChangedPaths {
    $tracked = @(& git -C $RepoRoot diff --name-only HEAD)
    if ($LASTEXITCODE -ne 0) { throw "git diff --name-only failed" }
    $untracked = @(& git -C $RepoRoot ls-files --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) { throw "git ls-files --others failed" }
    return @($tracked + $untracked | Where-Object { $_ -and $_.Trim() } | Sort-Object -Unique)
}

function Assert-SafeBranch {
    $branch = Get-GitText @("branch","--show-current")
    if (-not $branch) { throw "Detached HEAD is not allowed." }
    if ($branch -in @("main","develop")) {
        throw "Refusing to run on protected branch '$branch'. Use a feature integration branch/worktree."
    }
    return $branch
}

function Assert-CleanWorktree {
    $dirty = Get-GitText @("status","--porcelain")
    if ($dirty) {
        Write-Host $dirty
        throw "Worktree is not clean. Commit/stash deliberate work before running the harness."
    }
}

function Test-ForbiddenPath([string]$Path) {
    $p = $Path.Replace("\","/")
    $forbiddenPrefixes = @(
        "Saved/",
        "Intermediate/",
        "DerivedDataCache/",
        "Binaries/",
        ".vs/",
        "Content/RecordShop/Maps/Test/_GENERATED/"
    )
    foreach ($prefix in $forbiddenPrefixes) {
        if ($p.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    }

    $forbiddenExact = @(
        "Content/RecordShop/Core/GameInstance/BP_RecordGameInstance.uasset",
        "Content/ThirdPerson/Blueprints/WBP_RecordSelection.uasset",
        "Content/ThirdPerson/Blueprints/WBP_RecordSelection2.uasset"
    )
    foreach ($exact in $forbiddenExact) {
        if ($p.Equals($exact, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    return $false
}

function Ensure-Remote {
    param([string]$Name, [string]$Url)
    $remotes = @(& git -C $RepoRoot remote)
    if ($remotes -notcontains $Name) {
        Write-Host "Adding remote $Name -> $Url"
        Invoke-Git @("remote","add",$Name,$Url)
    }
}

function Invoke-CodexRun {
    param(
        [Parameter(Mandatory=$true)][string]$Prompt,
        [Parameter(Mandatory=$true)][string]$Model,
        [Parameter(Mandatory=$true)][string]$Effort,
        [Parameter(Mandatory=$true)][string]$LastMessagePath,
        [string]$SchemaPath = ""
    )

    $args = @(
        "exec",
        "--model", $Model,
        "--sandbox", "workspace-write",
        "--ask-for-approval", "never",
        "--config", "model_reasoning_effort=$Effort",
        "--output-last-message", $LastMessagePath
    )
    if ($SchemaPath) { $args += @("--output-schema", $SchemaPath) }

    Push-Location $RepoRoot
    try {
        $Prompt | & codex @args -
        $code = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    return $code
}

Write-Step "Preflight"

if (-not (Test-Path $RepoRoot)) { throw "RepoRoot does not exist: $RepoRoot" }
$gitRoot = Get-GitText @("rev-parse","--show-toplevel")
if (-not $gitRoot) { throw "Not a Git worktree: $RepoRoot" }

$branch = Assert-SafeBranch
Assert-CleanWorktree

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    throw "codex CLI is not available on PATH."
}

if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) {
    throw "UnrealEditor is running. Close it before an unattended harness run."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workerPromptPath = Join-Path $scriptDir "worker_prompt.md"
$auditPromptPath = Join-Path $scriptDir "audit_prompt.md"
$auditSchemaPath = Join-Path $scriptDir "audit_schema.json"
foreach ($required in @($workerPromptPath,$auditPromptPath,$auditSchemaPath)) {
    if (-not (Test-Path $required)) { throw "Missing harness file: $required" }
}

Ensure-Remote -Name "hyeon-fork" -Url "https://github.com/kkkwwwqqqeqwdc/GameEngine-TermProject.git"

Write-Host "Repo:   $RepoRoot"
Write-Host "Branch: $branch"
Write-Host "Worker: $WorkerModel / $WorkerEffort"
Write-Host "Audit:  $AuditorModel / $AuditorEffort"

Write-Step "Refresh remotes"
Invoke-Git @("fetch","origin","--prune")
Invoke-Git @("fetch","hyeon-fork","--prune")

& git lfs version *> $null
if ($LASTEXITCODE -eq 0) {
    $lfsRefs = @(
        @("origin","feature/environment-art"),
        @("origin","feature/turntable-recommendation"),
        @("origin","feature/customer-ai"),
        @("origin","feature/dialogue-data"),
        @("hyeon-fork","feature/ui-presentation")
    )
    foreach ($pair in $lfsRefs) {
        Write-Host "LFS prefetch (best effort): $($pair[0]) $($pair[1])"
        & git -C $RepoRoot lfs fetch $pair[0] $pair[1]
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "LFS prefetch failed for $($pair[0])/$($pair[1]); continuing."
        }
    }
}

$runStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runRoot = Join-Path $env:TEMP "RecordShopHarness\$runStamp"
New-Item -ItemType Directory -Force -Path $runRoot | Out-Null

$baseDevelop = Get-GitText @("rev-parse","origin/develop")
$startingHead = Get-GitText @("rev-parse","HEAD")
$knownHeads = [ordered]@{
    "origin/develop" = $baseDevelop
    "origin/feature/environment-art" = (Get-GitText @("rev-parse","origin/feature/environment-art"))
    "origin/feature/turntable-recommendation" = (Get-GitText @("rev-parse","origin/feature/turntable-recommendation"))
    "origin/feature/customer-ai" = (Get-GitText @("rev-parse","origin/feature/customer-ai"))
    "origin/feature/dialogue-data" = (Get-GitText @("rev-parse","origin/feature/dialogue-data"))
    "hyeon-fork/feature/ui-presentation" = (Get-GitText @("rev-parse","hyeon-fork/feature/ui-presentation"))
}

$previousAuditSummary = "No previous round in this harness invocation."

for ($round = 1; $round -le $MaxRounds; $round++) {
    Write-Step "Round $round / $MaxRounds - worker"
    Assert-CleanWorktree

    $roundStartHead = Get-GitText @("rev-parse","HEAD")
    $workerOut = Join-Path $runRoot "round-$round-worker.txt"
    $auditOut = Join-Path $runRoot "round-$round-audit.json"

    $workerBase = Get-Content $workerPromptPath -Raw
    $headsJson = $knownHeads | ConvertTo-Json -Depth 4
    $dynamic = @"

==================================================
HARNESS RUNTIME CONTEXT
==================================================
Repository worktree:
$RepoRoot

Current branch:
$branch

Current round:
$round / $MaxRounds

Round start HEAD:
$roundStartHead

origin/develop:
$baseDevelop

Latest fetched contributor heads:
$headsJson

Previous independent audit summary:
$previousAuditSummary

IMPORTANT HARNESS CONTRACT:
- Do NOT commit.
- Do NOT push.
- Do NOT merge directly to develop.
- Git commit/push are handled outside your sandbox by the PowerShell harness.
- You own implementation + Unreal validation + human-readable report updates.
- Keep working through independent tasks until a terminal condition is reached.
"@

    $workerCode = Invoke-CodexRun -Prompt ($workerBase + $dynamic) -Model $WorkerModel -Effort $WorkerEffort -LastMessagePath $workerOut
    if ($workerCode -ne 0) {
        Write-Warning "Worker Codex exited with code $workerCode. Continuing to safety inspection if changes exist."
    }

    $changed = @(Get-ChangedPaths)
    if ($changed.Count -eq 0) {
        Write-Host "Worker produced no repository changes."
        if (Test-Path $workerOut) {
            Write-Host "--- Worker last message ---"
            Get-Content $workerOut
        }
        break
    }

    Write-Host "Changed paths:"
    $changed | ForEach-Object { Write-Host "  $_" }

    $forbidden = @($changed | Where-Object { Test-ForbiddenPath $_ })
    if ($forbidden.Count -gt 0) {
        Write-Host "FORBIDDEN CHANGES DETECTED:" -ForegroundColor Red
        $forbidden | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        Write-Host "No stage/commit/push. Changes are left for human review."
        exit 20
    }

    Write-Step "Static Git safety checks"
    & git -C $RepoRoot diff --check
    if ($LASTEXITCODE -ne 0) { Write-Host "git diff --check failed. No commit/push." -ForegroundColor Red; exit 21 }

    $diffStat = Get-GitText @("diff","--stat","HEAD")
    $statusText = Get-GitText @("status","--short")

    Write-Step "Round $round - independent auditor"
    $auditBase = Get-Content $auditPromptPath -Raw
    $workerLast = if (Test-Path $workerOut) { Get-Content $workerOut -Raw } else { "" }

    $auditDynamic = @"

==================================================
AUDIT RUNTIME CONTEXT
==================================================
Repo:
$RepoRoot

Branch:
$branch

Round start HEAD:
$roundStartHead

Current HEAD before harness commit:
$(Get-GitText @("rev-parse","HEAD"))

origin/develop:
$baseDevelop

Git status:
$statusText

Changed files:
$($changed -join "`n")

Diff stat:
$diffStat

Worker last message:
$workerLast

Audit the ACTUAL repository state and runtime evidence yourself.
Do not trust the worker's claims without verification.
Return JSON matching the supplied schema.
"@

    $auditCode = Invoke-CodexRun -Prompt ($auditBase + $auditDynamic) -Model $AuditorModel -Effort $AuditorEffort -LastMessagePath $auditOut -SchemaPath $auditSchemaPath
    if ($auditCode -ne 0 -or -not (Test-Path $auditOut)) {
        Write-Host "Independent audit did not complete. No commit/push." -ForegroundColor Red
        exit 22
    }

    try { $audit = Get-Content $auditOut -Raw | ConvertFrom-Json }
    catch { Write-Host "Could not parse auditor JSON. No commit/push." -ForegroundColor Red; Get-Content $auditOut; exit 23 }

    Write-Host "AUDIT VERDICT: $($audit.verdict)"
    Write-Host "SAFE TO COMMIT: $($audit.safe_to_commit)"
    Write-Host "E2E: $($audit.e2e)"
    Write-Host "LAST NATURAL STAGE: $($audit.last_natural_stage)"
    Write-Host "FIRST BLOCKER: $($audit.first_blocker)"

    $previousAuditSummary = @"
Verdict: $($audit.verdict)
E2E: $($audit.e2e)
Last natural stage: $($audit.last_natural_stage)
First blocker: $($audit.first_blocker)
Summary: $($audit.summary)
Remaining blockers: $($audit.remaining_blockers -join '; ')
"@

    if (-not [bool]$audit.safe_to_commit) {
        Write-Host "Auditor did not approve automatic commit. Changes left uncommitted." -ForegroundColor Yellow
        Write-Host "Audit JSON: $auditOut"
        exit 24
    }

    $filesToCommit = @($audit.files_to_commit | ForEach-Object { [string]$_ } | Where-Object { $_ })
    if ($filesToCommit.Count -eq 0) {
        Write-Host "Auditor approved commit but supplied no files_to_commit." -ForegroundColor Red
        exit 25
    }

    $currentChanged = @(Get-ChangedPaths)
    $changedNorm = @($currentChanged | ForEach-Object { $_.Replace("\","/") } | Sort-Object -Unique)
    $commitNorm = @($filesToCommit | ForEach-Object { $_.Replace("\","/") } | Sort-Object -Unique)

    $missingFromAudit = @($changedNorm | Where-Object { $commitNorm -notcontains $_ })
    $unknownFromAudit = @($commitNorm | Where-Object { $changedNorm -notcontains $_ })
    if ($missingFromAudit.Count -gt 0 -or $unknownFromAudit.Count -gt 0) {
        Write-Host "Auditor file set != actual repository changes. Refusing auto-commit." -ForegroundColor Red
        if ($missingFromAudit.Count -gt 0) { Write-Host "Changed but not approved:"; $missingFromAudit | ForEach-Object { Write-Host "  $_" } }
        if ($unknownFromAudit.Count -gt 0) { Write-Host "Approved but not changed:"; $unknownFromAudit | ForEach-Object { Write-Host "  $_" } }
        exit 26
    }

    foreach ($f in $commitNorm) {
        if (Test-ForbiddenPath $f) { throw "Auditor attempted to approve forbidden path: $f" }
    }

    Write-Step "Stage exact audited files"
    foreach ($f in $commitNorm) {
        & git -C $RepoRoot add -- $f
        if ($LASTEXITCODE -ne 0) { throw "git add failed: $f" }
    }

    & git -C $RepoRoot diff --cached --check
    if ($LASTEXITCODE -ne 0) { Write-Host "git diff --cached --check failed. No commit." -ForegroundColor Red; exit 27 }

    $staged = Get-GitText @("diff","--cached","--name-only")
    if (-not $staged) { Write-Host "Nothing staged." -ForegroundColor Yellow; break }

    $commitMessage = [string]$audit.commit_message
    if (-not $commitMessage.Trim()) { $commitMessage = "feat: advance record shop integration" }

    Write-Step "Commit audited changes"
    & git -C $RepoRoot commit -m $commitMessage
    if ($LASTEXITCODE -ne 0) { throw "git commit failed." }

    $newHead = Get-GitText @("rev-parse","HEAD")
    Write-Host "Committed: $newHead"

    if (-not $NoPush) {
        Write-Step "Push feature branch"
        & git -C $RepoRoot push -u origin $branch
        if ($LASTEXITCODE -ne 0) { throw "git push failed. Local commit is preserved." }

        $remoteLine = (& git -C $RepoRoot ls-remote --heads origin "refs/heads/$branch" | Out-String).Trim()
        if (-not $remoteLine) { throw "Could not verify remote branch after push." }
        $remoteSha = ($remoteLine -split "\s+")[0]
        if ($remoteSha -ne $newHead) { throw "Remote verification mismatch. Local=$newHead Remote=$remoteSha" }
        Write-Host "Remote verification PASS: $remoteSha"
    } else {
        Write-Host "NoPush enabled; local commit retained without push."
    }

    $afterStatus = Get-GitText @("status","--porcelain")
    if ($afterStatus) {
        Write-Host "Worktree is not clean after commit:" -ForegroundColor Yellow
        Write-Host $afterStatus
        exit 28
    }

    if ($audit.e2e -eq "PASS") { Write-Step "Terminal condition: E2E PASS"; break }
    if (-not [bool]$audit.continue_recommended) { Write-Step "Terminal condition: auditor recommends stop"; break }
    if ($round -lt $MaxRounds) { Write-Host "Auditor recommends another autonomous repair round." }
}

Write-Step "Final summary"
$finalHead = Get-GitText @("rev-parse","HEAD")
$finalStatus = Get-GitText @("status","--porcelain")
Write-Host "BRANCH:        $branch"
Write-Host "START HEAD:    $startingHead"
Write-Host "FINAL HEAD:    $finalHead"
Write-Host "BASE DEVELOP:  $baseDevelop"
Write-Host "WORKTREE:      $(if ($finalStatus) { 'DIRTY' } else { 'CLEAN' })"
Write-Host "RUN LOGS:      $runRoot"
Write-Host "Harness finished. It never merges to develop automatically." -ForegroundColor Green
