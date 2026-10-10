param(
    [string]$RepoRoot = "D:\univ\3-1\GameEngine\Termproject\RecordShop_overnight",
    [string]$ExpectedBranch = "feature/overnight-integration-2026-10-09",
    [string]$WorkerModel = "gpt-6-astra",
    [ValidateSet("low","medium","high","xhigh","max")][string]$WorkerEffort = "high",
    [string]$AuditorModel = "gpt-6.1-sol",
    [ValidateSet("low","medium","high","xhigh","max")][string]$AuditorEffort = "high",
    [ValidateRange(1,100)][int]$MaxRounds = 5,
    [ValidateRange(0,10)][int]$MaxRepairAttemptsPerRound = 2,
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $utf8NoBom
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "=== $Message ===" -ForegroundColor Cyan
}

function Invoke-Git {
    param([Parameter(Mandatory=$true)][string[]]$Args)
    & git --literal-pathspecs -C $RepoRoot @Args | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE" }
}

function Get-GitText {
    param([Parameter(Mandatory=$true)][string[]]$Args)
    $out = & git --literal-pathspecs -C $RepoRoot -c core.quotepath=false @Args
    if ($LASTEXITCODE -ne 0) { throw "git $($Args -join ' ') failed" }
    return (($out | Out-String).Trim())
}

function Get-ChangedPaths {
    # Include BOTH sides of renames so exact staging also covers deletions.
    $tracked = @(& git -C $RepoRoot -c core.quotepath=false diff --no-renames --name-only HEAD)
    if ($LASTEXITCODE -ne 0) { throw "git diff --name-only failed" }
    $untracked = @(& git -C $RepoRoot -c core.quotepath=false ls-files --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) { throw "git ls-files --others failed" }
    return @($tracked + $untracked | Where-Object { $_ } | Sort-Object -Unique)
}

function Assert-SafeBranch {
    $current = Get-GitText @("branch","--show-current")
    if (-not $current -or $current -in @("main","develop")) { throw "Detached/protected branch is not allowed." }
    if ($current -cne $ExpectedBranch) { throw "Expected integration branch '$ExpectedBranch', found '$current'." }
    return $current
}

function Assert-CleanWorktree {
    $dirty = Get-GitText @("status","--porcelain")
    if ($dirty) { throw "Worktree must be clean before a new round. Existing work is preserved.`n$dirty" }
}

function Assert-CheckpointIdentity([string]$Head) {
    $null = Assert-SafeBranch
    if ((Get-GitText @("rev-parse","HEAD")) -cne $Head) {
        throw "HEAD changed inside a worker/auditor session. No automatic staging, commit or push."
    }
}

function Test-ForbiddenPath([string]$Path) {
    $p = $Path.Replace("\","/")
    if (-not $p -or $p -match '^(?:/|[A-Za-z]:)' -or $p -match '[\x00-\x1f\x7f]' -or
        @($p.Split('/') | Where-Object { $_ -in @('', '.', '..', '.git') }).Count -gt 0) { return $true }
    foreach ($prefix in @("Saved/","Intermediate/","DerivedDataCache/","Binaries/",".vs/","Content/RecordShop/Maps/Test/_GENERATED/")) {
        if ($p.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    foreach ($exact in @(
        "Content/RecordShop/Core/GameInstance/BP_RecordGameInstance.uasset",
        "Content/ThirdPerson/Blueprints/WBP_RecordSelection.uasset",
        "Content/ThirdPerson/Blueprints/WBP_RecordSelection2.uasset"
    )) {
        if ($p.Equals($exact, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    return $false
}

function Assert-ExactFileSet {
    param([AllowEmptyCollection()][string[]]$Actual, [AllowEmptyCollection()][string[]]$Approved)
    # Ordinal comparison: no case folding, aliases, empty entries or duplicate approval paths.
    $actualSet = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
    $approvedSet = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
    foreach ($path in $Actual) { $null = $actualSet.Add($path.Replace("\","/")) }
    foreach ($path in $Approved) {
        if (Test-ForbiddenPath $path) { throw "Forbidden/invalid approved path: $path" }
        if (-not $approvedSet.Add($path.Replace("\","/"))) { throw "Duplicate approved path: $path" }
    }
    if (-not $actualSet.SetEquals($approvedSet)) { throw "Auditor file set != actual repository changes. No automatic commit." }
}

function Ensure-Remote {
    param([string]$Name, [string]$Url)
    $remotes = @(& git -C $RepoRoot remote)
    if ($LASTEXITCODE -ne 0) { throw "Cannot inspect remotes." }
    if ($remotes -notcontains $Name) { Invoke-Git @("remote","add",$Name,$Url) }
}

function Update-ContributorInventory {
    # Network/LFS failures are evidence, never permission to discard local work.
    # PS 5.1 may turn native stderr into ErrorRecords; inspect exit codes explicitly.
    $ErrorActionPreference = "Continue"
    foreach ($remote in @("origin","hyeon-fork")) {
        & git -C $RepoRoot fetch $remote --prune 2>&1 | Out-Host
        if ($LASTEXITCODE -ne 0) {
            $message = "Fetch failed for $remote; cached refs may be stale."
            Write-Warning $message
            $null = $externalEvents.Add($message)
        }
    }
    $lfsRefs = @(
        @("origin","feature/environment-art"), @("origin","feature/turntable-recommendation"),
        @("origin","feature/customer-ai"), @("origin","feature/dialogue-data"),
        @("hyeon-fork","feature/ui-presentation")
    )
    & git lfs version *> $null
    if ($LASTEXITCODE -eq 0) {
        foreach ($pair in $lfsRefs) {
            Write-Host "LFS prefetch (best effort): $($pair[0]) $($pair[1])"
            & git -C $RepoRoot lfs fetch $pair[0] $pair[1] 2>&1 | Out-Host
            if ($LASTEXITCODE -ne 0) {
                $message = "LFS prefetch failed for $($pair[0])/$($pair[1]); inventory must distinguish missing binaries."
                Write-Warning $message
                $null = $externalEvents.Add($message)
            }
        }
    } else { $null = $externalEvents.Add("Git LFS unavailable; inspect pointer/binary availability locally.") }
    $inventory = [ordered]@{}
    foreach ($ref in @("origin/develop") + @($lfsRefs | ForEach-Object { "$($_[0])/$($_[1])" })) {
        $sha = @(& git -C $RepoRoot rev-parse --verify $ref 2>$null)
        if ($LASTEXITCODE -eq 0) { $inventory[$ref] = ($sha -join '') }
        else {
            $inventory[$ref] = "UNAVAILABLE"
            $null = $externalEvents.Add("Contributor ref unavailable: $ref")
        }
    }
    return $inventory
}

function Invoke-CodexRun {
    param(
        [Parameter(Mandatory=$true)][string]$Prompt,
        [Parameter(Mandatory=$true)][string]$Model,
        [Parameter(Mandatory=$true)][string]$Effort,
        [Parameter(Mandatory=$true)][string]$LastMessagePath,
        [string]$SchemaPath = ""
    )
    $cliArgs = @("--ask-for-approval", "never", "exec", "--model", $Model,
        "--sandbox", "workspace-write", "--config", "model_reasoning_effort=$Effort",
        "--output-last-message", $LastMessagePath)
    if ($SchemaPath) { $cliArgs += @("--output-schema", $SchemaPath) }
    Push-Location $RepoRoot
    try {
        # Keep native output out of the return value, and retain JSON after nonzero exits.
        $ErrorActionPreference = "Continue"
        $Prompt | & codex @cliArgs - 2>&1 | Out-Host
        $code = $LASTEXITCODE
    }
    finally { Pop-Location }
    return $code
}

function Get-AuditValidation($Audit, [string]$Name) {
    $matches = @($Audit.validations | Where-Object { $_.name -ceq $Name })
    if ($matches.Count -ne 1) { throw "Audit must contain exactly one '$Name' validation." }
    return $matches[0]
}

function Read-StructuredAudit([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Independent audit produced no JSON. No commit/push." }
    $raw = [System.IO.File]::ReadAllText($Path, $utf8NoBom)
    $audit = $raw | ConvertFrom-Json -ErrorAction Stop
    if ($audit -isnot [System.Management.Automation.PSCustomObject]) { throw "Auditor JSON must be a top-level object." }
    $required = @("verdict","safe_to_commit","summary","files_to_commit","commit_message","e2e",
        "last_natural_stage","first_blocker","validations","remaining_blockers","continue_recommended")
    $fields = @($audit.PSObject.Properties.Name)
    if (@($required | Where-Object { $fields -cnotcontains $_ }).Count -gt 0 -or
        @($fields | Where-Object { $required -cnotcontains $_ }).Count -gt 0) { throw "Audit fields do not match the required schema." }
    foreach ($name in @("safe_to_commit","continue_recommended")) {
        if ($audit.$name -isnot [bool]) { throw "Audit '$name' must be a JSON boolean." }
    }
    foreach ($name in @("verdict","summary","commit_message","e2e","last_natural_stage","first_blocker")) {
        if ($audit.$name -isnot [string]) { throw "Audit '$name' must be a string." }
    }
    if ($audit.verdict -cnotin @("PASS","PARTIAL_SAFE","BLOCKED","FAIL") -or $audit.e2e -cnotin @("PASS","FAIL","NOT_RUN")) {
        throw "Invalid audit verdict/E2E enum."
    }
    foreach ($name in @("files_to_commit","remaining_blockers","validations")) {
        if ($audit.$name -isnot [array]) { throw "Audit '$name' must be an array." }
    }
    foreach ($entry in @($audit.files_to_commit) + @($audit.remaining_blockers)) {
        if ($entry -isnot [string] -or -not $entry.Trim()) { throw "Audit paths/blockers must be nonempty strings." }
    }
    foreach ($validation in $audit.validations) {
        if ($validation -isnot [System.Management.Automation.PSCustomObject]) { throw "Invalid validation object." }
        $names = @($validation.PSObject.Properties.Name)
        if ($names.Count -ne 3 -or @(@("name","status","evidence") | Where-Object { $names -cnotcontains $_ }).Count -gt 0) {
            throw "Invalid validation fields."
        }
        foreach ($name in @("name","status","evidence")) {
            if ($validation.$name -isnot [string] -or -not $validation.$name.Trim()) { throw "Empty/invalid validation '$name'." }
        }
        if ($validation.status -cnotin @("PASS","PARTIAL","FAIL","UNVERIFIED")) { throw "Invalid validation status." }
    }
    $mechanical = Get-AuditValidation $audit "Mechanical MVP"
    $independent = Get-AuditValidation $audit "Independent work"
    $null = Get-AuditValidation $audit "Rendered validation"
    $null = Get-AuditValidation $audit "Packaging"
    if ($mechanical.status -ceq "PASS" -and $audit.e2e -cne "PASS") { throw "Mechanical MVP PASS requires natural E2E PASS." }
    if ($independent.status -cnotin @("PASS","PARTIAL")) { throw "Independent work must be PASS (none) or PARTIAL (available)." }
    if ($audit.continue_recommended -ne ($independent.status -ceq "PARTIAL")) { throw "Continuation contradicts independent-work inventory." }
    if ($independent.status -ceq "PASS" -and $independent.evidence -cne "NONE") { throw "No independent work must use evidence NONE." }
    if ($independent.status -ceq "PARTIAL" -and $independent.evidence -ceq "NONE") { throw "Available independent work requires concrete tasks." }
    foreach ($blocker in $audit.remaining_blockers) {
        if ($blocker -cnotmatch '^(PRODUCT|EXTERNAL|CONTENT/DESIGN): .+') { throw "Unclassified remaining blocker: $blocker" }
    }
    if ($mechanical.status -ceq "PASS" -and @($audit.remaining_blockers | Where-Object { $_ -cmatch '^PRODUCT: ' }).Count -gt 0) {
        throw "Mechanical MVP PASS cannot leave unresolved product blockers."
    }
    if (-not $audit.continue_recommended -and $mechanical.status -cne "PASS" -and @($audit.remaining_blockers).Count -eq 0) {
        throw "Incomplete terminal checkpoint must identify its human/external dependency."
    }
    if ($audit.safe_to_commit) {
        if ($audit.verdict -cnotin @("PASS","PARTIAL_SAFE")) { throw "Unsafe verdict cannot authorize commit." }
        if (@($audit.files_to_commit).Count -gt 0 -and -not $audit.commit_message.Trim()) { throw "Approved changes require an auditor commit message." }
    } elseif (@($audit.files_to_commit).Count -gt 0) { throw "Rejected checkpoint must approve no files." }
    # Preserve EXACT JSON, including formatting, for a fresh repair worker.
    return [pscustomobject]@{ Audit = $audit; Raw = $raw }
}

function Invoke-MvpRound {
    param([int]$Round, [string]$RoundStartHead, [string]$WorkerPrompt, [string]$AuditPrompt)
    $repairAttempt = 0
    $repairContext = "Initial substantial MVP completion attempt."
    while ($true) {
        $attemptStem = "round-$Round-attempt-$repairAttempt"
        $workerOut = Join-Path $runRoot "$attemptStem-worker.txt"
        $auditOut = Join-Path $runRoot "$attemptStem-audit.json"
        Write-Step "Round $Round / $MaxRounds - worker (repair $repairAttempt / $MaxRepairAttemptsPerRound)"
        # Repairs preserve the dirty worktree and use a fresh Astra session.
        $workerCode = Invoke-CodexRun -Prompt ($WorkerPrompt + "`n" + $repairContext) -Model $WorkerModel -Effort $WorkerEffort -LastMessagePath $workerOut
        if ($workerCode -ne 0) { Write-Warning "Worker exited $workerCode; audit actual state, including no-change attempts." }
        Assert-CheckpointIdentity $RoundStartHead
        $changed = @(Get-ChangedPaths)
        $forbidden = @($changed | Where-Object { Test-ForbiddenPath $_ })
        if ($forbidden.Count -gt 0) { throw "Forbidden changes preserved for human review: $($forbidden -join ', ')" }
        & git -C $RepoRoot diff --check
        $diffCheckCode = $LASTEXITCODE
        $statusText = Get-GitText @("status","--short")
        $diffStat = Get-GitText @("diff","--stat","HEAD")
        $workerLast = if (Test-Path -LiteralPath $workerOut) { Get-Content -LiteralPath $workerOut -Raw -Encoding UTF8 } else { "No worker last message." }
        $auditDynamic = @"

AUDIT RUNTIME CONTEXT
Repository: $RepoRoot
Expected branch: $ExpectedBranch
Round: $Round / $MaxRounds; repair attempt: $repairAttempt / $MaxRepairAttemptsPerRound
Round start HEAD (must remain unchanged): $RoundStartHead
Git status:
$statusText
Changed files (may be empty; still audit terminal status and independent work):
$($changed -join "`n")
Diff stat:
$diffStat
Unstaged diff --check exit code: $diffCheckCode
Worker last message (untrusted claims):
$workerLast
Previous rejected checkpoint context, if any:
$repairContext
Audit actual repository and fresh evidence. Return only schema-valid JSON.
"@
        Write-Step "Round $Round - independent Sol auditor (repair $repairAttempt)"
        $auditCode = Invoke-CodexRun -Prompt ($AuditPrompt + $auditDynamic) -Model $AuditorModel -Effort $AuditorEffort -LastMessagePath $auditOut -SchemaPath $auditSchemaPath
        Assert-CheckpointIdentity $RoundStartHead
        # Parse first: valid structured JSON survives nonzero auditor exit.
        $result = Read-StructuredAudit $auditOut
        $script:lastAudit = $result.Audit
        $script:lastAuditRaw = $result.Raw
        $script:lastAuditPath = $auditOut
        $audit = $result.Audit
        if ($auditCode -ne 0) { Write-Warning "Auditor exited $auditCode; using validated structured JSON." }
        Write-Host "AUDIT VERDICT: $($audit.verdict); SAFE TO COMMIT: $($audit.safe_to_commit)"
        Write-Host "NATURAL E2E: $($audit.e2e); LAST NATURAL STAGE: $($audit.last_natural_stage)"
        Write-Host "FIRST PRODUCT BLOCKER: $($audit.first_blocker)"
        Write-Host "Audit JSON: $auditOut"
        if ($audit.safe_to_commit) { return $audit }
        if ($audit.continue_recommended -and $repairAttempt -lt $MaxRepairAttemptsPerRound) {
            $repairAttempt++
            $repairContext = @"

REJECTED CHECKPOINT REPAIR - attempt $repairAttempt / $MaxRepairAttemptsPerRound
The dirty worktree is preserved. This is a fresh worker, not a new clean round.
Fix factual/code/test issues identified by the independent auditor in the ACTUAL implementation
and validation. Do not merely rewrite documentation to appease the auditor. Inspect all changes,
compile affected Blueprints, test and update the report. Do not reset/discard rejected work.
Continue independent MVP work when safe; rejection is not permission to bypass any gate.
EXACT STRUCTURED AUDITOR JSON BEGIN
$($result.Raw)
EXACT STRUCTURED AUDITOR JSON END
"@
            continue
        }
        if ($audit.continue_recommended) { $reason = "Repair attempts exhausted ($MaxRepairAttemptsPerRound)." }
        else { $reason = "Auditor rejected checkpoint and no safe independent repair remains." }
        throw "$reason Dirty worktree untouched. Latest exact blocker: $($audit.first_blocker) Audit: $auditOut"
    }
}

function Publish-AuditedCheckpoint {
    param($Audit, [string]$RoundStartHead)
    Assert-CheckpointIdentity $RoundStartHead
    $currentChanged = @(Get-ChangedPaths)
    $approved = @($Audit.files_to_commit)
    Assert-ExactFileSet -Actual $currentChanged -Approved $approved
    & git -C $RepoRoot diff --check
    if ($LASTEXITCODE -ne 0) { throw "git diff --check failed. No commit/push." }
    if ($currentChanged.Count -eq 0) { Assert-CleanWorktree; return }
    Write-Step "Stage exact audited files"
    foreach ($file in $approved) { Invoke-Git @("add","--",$file.Replace("\","/")) }
    Invoke-Git @("diff","--cached","--check")
    $staged = @(& git -C $RepoRoot -c core.quotepath=false diff --cached --no-renames --name-only)
    if ($LASTEXITCODE -ne 0) { throw "Cannot inspect staged file set." }
    Assert-ExactFileSet -Actual $staged -Approved $approved
    Assert-ExactFileSet -Actual @(Get-ChangedPaths) -Approved $approved
    Assert-CheckpointIdentity $RoundStartHead
    Write-Step "Commit audited changes"
    Invoke-Git @("commit","-m",[string]$Audit.commit_message)
    $script:commitsCreated++
    $script:lastCommit = Get-GitText @("rev-parse","HEAD")
    Assert-CleanWorktree
    $null = Assert-SafeBranch
    if (-not $NoPush) {
        Write-Step "Push current integration branch"
        Invoke-Git @("push","-u","origin","HEAD:refs/heads/$ExpectedBranch")
        $remoteLine = Get-GitText @("ls-remote","--heads","origin","refs/heads/$ExpectedBranch")
        if (-not $remoteLine -or ($remoteLine -split '\s+')[0] -cne $script:lastCommit) {
            throw "Remote verification failed; local commit preserved."
        }
    } else { Write-Host "NoPush enabled; audited local commit retained without push." }
    Assert-CleanWorktree
}

function Write-MvpSummary {
    $clean = "NO"
    try { if (-not (Get-GitText @("status","--porcelain"))) { $clean = "YES" } }
    catch { Write-Warning "Cannot inspect final worktree: $($_.Exception.Message)" }
    $natural = "FAIL"
    $stage = "UNVERIFIED"
    $product = "UNVERIFIED"
    $content = @()
    $external = @($externalEvents | Sort-Object -Unique)
    $remaining = "UNVERIFIED"
    $mechanicalComplete = $false
    if ($null -ne $lastAudit) {
        if ($lastAudit.e2e -ceq "PASS") { $natural = "PASS" }
        $stage = $lastAudit.last_natural_stage
        $product = $lastAudit.first_blocker
        $content = @($lastAudit.remaining_blockers | Where-Object { $_ -cmatch '^CONTENT/DESIGN: ' })
        $external += @($lastAudit.remaining_blockers | Where-Object { $_ -cmatch '^EXTERNAL: ' })
        $remaining = (Get-AuditValidation $lastAudit "Independent work").evidence
        $mechanicalComplete = (Get-AuditValidation $lastAudit "Mechanical MVP").status -ceq "PASS"
    }
    if ($stopReason) { $external += "HARNESS: $stopReason" }
    Write-Step "Final summary"
    Write-Host "MVP COMPLETION HARNESS: $completionStatus"
    Write-Host "ROUNDS COMPLETED: $roundsCompleted"
    Write-Host "COMMITS CREATED: $commitsCreated"
    Write-Host "LAST COMMIT: $lastCommit"
    Write-Host "NATURAL E2E: $natural"
    Write-Host "LAST NATURAL STAGE: $stage"
    Write-Host "FIRST PRODUCT BLOCKER: $product"
    Write-Host "EXTERNAL BLOCKERS: $(if ($external.Count) { $external -join '; ' } else { 'NONE' })"
    Write-Host "CONTENT/DESIGN BLOCKERS: $(if ($content.Count) { $content -join '; ' } else { 'NONE' })"
    Write-Host "REMAINING INDEPENDENT WORK: $remaining"
    Write-Host "WORKTREE CLEAN: $clean"
    if ($completionStatus -ceq "COMPLETE" -and $mechanicalComplete) {
        Write-Host "MECHANICAL MVP COMPLETE"
        if ($content.Count -gt 0) { Write-Host "CONTENT/POLISH REMAINS" }
    }
    Write-Host "RUN LOGS: $runRoot"
    if ($lastAuditPath) { Write-Host "LATEST EXACT AUDIT: $lastAuditPath" }
}

$roundsCompleted = 0
$commitsCreated = 0
$lastCommit = "NONE"
$lastAudit = $null
$lastAuditRaw = "No previous round in this harness invocation."
$lastAuditPath = ""
$externalEvents = New-Object 'System.Collections.Generic.List[string]'
$completionStatus = "PARTIAL"
$stopReason = ""
$exitCode = 0
$runRoot = "NOT CREATED"

try {
    Write-Step "Preflight"
    if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) { throw "RepoRoot does not exist: $RepoRoot" }
    $gitRoot = Get-GitText @("rev-parse","--show-toplevel")
    if ([System.IO.Path]::GetFullPath($gitRoot) -ine [System.IO.Path]::GetFullPath($RepoRoot)) { throw "RepoRoot must be the Git worktree root." }
    $null = Assert-SafeBranch
    Assert-CleanWorktree
    if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "codex CLI is not available on PATH." }
    if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) { throw "Close UnrealEditor before an unattended run." }
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $workerPromptPath = Join-Path $scriptDir "worker_prompt.md"
    $auditPromptPath = Join-Path $scriptDir "audit_prompt.md"
    $auditSchemaPath = Join-Path $scriptDir "audit_schema.json"
    foreach ($required in @($workerPromptPath,$auditPromptPath,$auditSchemaPath)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Missing harness file: $required" }
    }
    $runRoot = Join-Path $env:TEMP ("RecordShopHarness\" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $runRoot | Out-Null
    Ensure-Remote -Name "hyeon-fork" -Url "https://github.com/kkkwwwqqqeqwdc/GameEngine-TermProject.git"
    Write-Host "Repo: $RepoRoot; Branch: $ExpectedBranch"
    Write-Host "Worker: $WorkerModel / $WorkerEffort; Auditor: $AuditorModel / $AuditorEffort"
    for ($round = 1; $round -le $MaxRounds; $round++) {
        $null = Assert-SafeBranch
        Assert-CleanWorktree
        $roundStartHead = Get-GitText @("rev-parse","HEAD")
        $externalEvents.Clear()
        Write-Step "Round $round - refresh remotes / best-effort LFS inventory"
        $knownHeads = Update-ContributorInventory
        Assert-CheckpointIdentity $roundStartHead
        Assert-CleanWorktree
        $headsJson = $knownHeads | ConvertTo-Json -Depth 4
        $dynamic = @"

HARNESS RUNTIME CONTEXT
Repository: $RepoRoot
Expected integration branch: $ExpectedBranch
Round: $round / $MaxRounds; MaxRepairAttemptsPerRound: $MaxRepairAttemptsPerRound
Round start HEAD: $roundStartHead
Contributor refs (UNAVAILABLE/cached refs block only dependent tasks):
$headsJson
Fetch/LFS observations:
$($externalEvents -join "`n")
Previous EXACT independent audit JSON, or initial status:
$lastAuditRaw
Do not commit/push/fetch, modify Git metadata, reset, stash, destructively restore,
merge main/develop/contributor branches or force any Git operation. The outer harness owns Git writes.
This round is a substantial attempt across the GLOBAL ORDERED MVP TARGET. Keep working through
safe independent tasks after individual blockers. Update the integration report and all evidence.
"@
        $workerPrompt = (Get-Content -LiteralPath $workerPromptPath -Raw -Encoding UTF8) + $dynamic
        $auditPrompt = (Get-Content -LiteralPath $auditPromptPath -Raw -Encoding UTF8) + $dynamic
        $audit = Invoke-MvpRound -Round $round -RoundStartHead $roundStartHead -WorkerPrompt $workerPrompt -AuditPrompt $auditPrompt
        Publish-AuditedCheckpoint -Audit $audit -RoundStartHead $roundStartHead
        $roundsCompleted++
        # E2E alone is not terminal while independent readiness work remains.
        if (-not $audit.continue_recommended) {
            if ((Get-AuditValidation $audit "Mechanical MVP").status -ceq "PASS") { $completionStatus = "COMPLETE" }
            else { $completionStatus = "BLOCKED" }
            break
        }
        if ($round -lt $MaxRounds) { Write-Host "Approved checkpoint published; continuing independent MVP work in the next clean round." }
        else { $stopReason = "MaxRounds reached ($MaxRounds); safe independent work remains. Resume with another invocation." }
    }
}
catch {
    $completionStatus = "BLOCKED"
    $stopReason = $_.Exception.Message
    $exitCode = 1
    Write-Host "STOPPED SAFELY: $stopReason" -ForegroundColor Yellow
    Write-Host "Existing work and commits are preserved; no automatic discard."
}
finally { Write-MvpSummary }
exit $exitCode
