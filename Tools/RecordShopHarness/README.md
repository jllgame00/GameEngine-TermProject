# RecordShop MVP Completion Harness V4

One command runs substantial Astra integration work, independent Sol audits, bounded repairs of rejected checkpoints, exact-file outer commits/pushes, and further clean rounds toward the complete mechanical customer cycle.

```powershell
& ".\Tools\RecordShopHarness\Invoke-RecordShopHarness.ps1"
```

The defaults are `MaxRounds=5`, `MaxRepairAttemptsPerRound=2`, worker `gpt-6-astra` / reasoning `high`, and auditor `gpt-6.1-sol` / reasoning `high`. The Windows CLI order remains `codex --ask-for-approval never exec ...`. Compatible with Windows PowerShell 5.1; native input/output and prompt/log reads use UTF-8.

Before running, close Unreal Editor, install/authenticate `codex`, and start with a clean worktree on the expected integration branch, currently `feature/overnight-integration-2026-10-09`. Commit this harness upgrade through the normal outer review process first. A deliberate branch change requires `-ExpectedBranch <integration-branch>`; detached HEAD, main and develop are refused. Git and best-effort Git LFS must be available. Git refresh failures retain cached refs and are reported; they never discard local work.

## Global MVP completion mode

Every worker round inventories and advances the entire ordered target:

1. Live Customer/customer-mood/dialogue data mapping using existing unambiguous contracts and root DialogueManager authority.
2. Natural Ready/StartDialogue, UI update, Next, finish, close, input restoration and progression.
3. Explicit Turntable completion connected to GameFlow, real authored Audio completion where present, deterministic documented Audio=None behavior otherwise.
4. Existing recommendation scoring/fields, mechanical graph repairs, consumable established raw score/result where qualitative design is absent.
5. Canonical Result UI, or a clearly named minimal integration fallback under RecordShop/UI/Result displaying only established data and an explicit continue/completion action.
6. FinishResult, customer exit, CustomerExited, cleared ActiveCustomer/modals, restored input/cursor and Explore.
7. The complete naturally exercised startup-to-customer-exit cycle returning to Explore.
8. Blueprint compilation, production-map cook/dependencies, reference/redirector/missing-package checks, and packaging when useful and safe.

Blank authored dialogue, contributor LFS absence, missing art, an unresolved scoring rule, or one failed test environment blocks only dependent work. Continue all available independent implementation and validation. Do not invent narrative, tags, weights, thresholds, Good/Bad meanings or audible playback. Blank fixtures can establish mechanical-only behavior through normal gameplay, never authored-content completion. Distinguish physical input/UI, synthetic Enhanced Input and direct diagnostic injections; direct calls never prove natural stages.

The preserved selection authority is WBP_RecordSelect -> BP_RecordShelf.RecordSelected -> BP_GameFlowManager.HandleRecordSelected -> BP_Turntable.SetRecord. GameInstance must not regain selected-record authority. Production binaries may be changed only through supported Unreal Editor/Editor Python mechanisms and saved normally. No raw binary editing, generated/test production Content or wholesale contributor branch merges.

## Round and repair behavior

A round begins with exact branch/clean-worktree checks, outer remote refresh and best-effort contributor LFS prefetch/inventory. The worker makes substantial coherent progress, inspects the complete diff, compiles affected Blueprints, tests relevant behavior, observes natural progression where possible and updates the integration report. Sol then independently audits actual changes and evidence, including attempts that produce no changes.

For a rejected checkpoint with `safe_to_commit=false` and `continue_recommended=true`, a fresh Astra worker receives the EXACT auditor JSON and repairs the preserved dirty worktree. It must fix actual factual/code/test issues and validate again; it must not merely rewrite documentation to appease the auditor. A fresh Sol audit follows. The default permits the initial attempt plus two repair attempts per round. Repairs do not require a clean worktree and do not count as new rounds.

If the repair cap is exhausted or the auditor finds no safe repair, stop without staging/committing/pushing rejected work. Print the latest exact blocker and audit path. No automatic reset, restore, stash or discard occurs. Invalid/missing/contradictory audit JSON, forbidden paths or changed branch/HEAD also stop safely. A valid structured JSON result remains usable after a nonzero auditor process exit.

On approval, require EXACT equality of the entire changed file set and `files_to_commit`, including untracked files, deletions and both rename paths. Reject duplicate/invalid/forbidden paths. Run `diff --check`, stage only each explicitly approved literal path, check staged whitespace and exact staged file-set equality, and recheck branch/HEAD. Outer PowerShell commits the auditor-provided message, pushes only the current integration branch, verifies remote HEAD and requires a clean worktree. When `continue_recommended=true`, proceed to the next round. Never use `git add .` or force operations. Workers/auditors never write Git metadata.

## Audit schema and completion decisions

`audit_schema.json` is unchanged. Required field/type/enum checks are supplemented by case-sensitive validation entries in the existing `validations` array:

- `Mechanical MVP`: PASS requires natural E2E PASS back to Explore. Content/polish may remain; independent readiness work may still need finishing.
- `Independent work`: PARTIAL with concrete tasks means `continue_recommended=true`; PASS with evidence exactly `NONE` means `continue_recommended=false` after the full target inventory is exhausted.
- `Rendered validation`: records current pre-shutdown observation and shutdown limitations separately.
- `Packaging`: PASS only for an actual successful package, never inferred from cook smoke.

`remaining_blockers` entries use `PRODUCT: `, `EXTERNAL: ` or `CONTENT/DESIGN: ` prefixes. `first_blocker` is the first product blocker or `NONE`. These conventions keep the schema stable while supplying the console summary. The auditor must not mark completion or stop merely because the first subsystem is blocked.

Successful terminal decisions are mechanical MVP complete with only content/polish/external asset dependencies, or a real human dependency after no safe independent work remains. E2E PASS alone is not terminal while readiness work remains. Reaching MaxRounds prints PARTIAL with the remaining tasks; another invocation can continue the clean committed checkpoint. `ROUNDS COMPLETED` counts approved rounds finished after publication (or an approved no-change checkpoint); rejected attempts are retained in logs.

## Known external engine shutdown

The investigated 0xC0000005 / -1073741819 rendered crash occurs during late editor Slate/ICU shutdown and has an editor-only reproduction without gameplay. Future crashes are never blindly waived. Fresh/current control evidence, production compile PASS, focused functional PASS and natural rendered feature observation before shutdown, absence of related project runtime errors/assertions/ensures, and unrelated cook/dependency results are all required for EXTERNAL ENGINE BLOCKER classification.

Such a checkpoint may be PARTIAL_SAFE and safe to commit. The affected rendered run remains PARTIAL/FAIL. Package PASS needs an actual successful package; E2E PASS needs the complete natural cycle. Changed crash timing or gameplay-related errors require diagnosis/repair.

## Options and outputs

```powershell
& ".\Tools\RecordShopHarness\Invoke-RecordShopHarness.ps1" -MaxRounds 5 -MaxRepairAttemptsPerRound 2
& ".\Tools\RecordShopHarness\Invoke-RecordShopHarness.ps1" -MaxRounds 1
& ".\Tools\RecordShopHarness\Invoke-RecordShopHarness.ps1" -NoPush
```

`-NoPush` still permits audited local commits; it skips remote push/verification only. Fetch/LFS inventory still runs. A zero repair cap disables automatic rejected-checkpoint repair. Model and reasoning parameters remain configurable.

Each worker/repair last message and exact audit JSON is retained under a unique `%TEMP%\RecordShopHarness\<timestamp-guid>` directory. Durable implementation/runtime evidence belongs in the integration report under Docs.

Every exit through the harness control flow prints:

```text
MVP COMPLETION HARNESS: COMPLETE / PARTIAL / BLOCKED
ROUNDS COMPLETED:
COMMITS CREATED:
LAST COMMIT:
NATURAL E2E: PASS / FAIL
LAST NATURAL STAGE:
FIRST PRODUCT BLOCKER:
EXTERNAL BLOCKERS:
CONTENT/DESIGN BLOCKERS:
REMAINING INDEPENDENT WORK:
WORKTREE CLEAN: YES / NO
```

Audit `NOT_RUN` is rendered as console FAIL (not verified), with `last_natural_stage` and evidence preserving the distinction. LAST COMMIT means the latest commit created by this invocation, or NONE. A complete mechanical cycle with content/polish dependencies also prints `MECHANICAL MVP COMPLETE` and `CONTENT/POLISH REMAINS`.

Safe human-dependency termination has status BLOCKED and exit code 0 when its coherent checkpoint is approved. Operational/safety/rejection failures use exit code 1 and preserve work. A round-limit PARTIAL also uses exit code 0 and reports unfinished independent work. After a push failure, the local commit is preserved and no further round starts.

## Upgrade self-validation

Do not execute the real harness to test this upgrade. Parse the script with the Windows PowerShell parser and strict UTF-8 decoding. Extract its function/loop AST for isolated tests with mocked Codex/Git/refresh calls: rejected-continuable audit enters repair with exact JSON, two-repair cap holds, valid JSON survives nonzero auditor exit, approved exact files commit/push before the next round, no-change attempts still audit, and unsafe file sets/branches are rejected. Check forbidden operations and prompt policies statically. Do not write production assets or Git metadata during upgrade validation.

The V4 upgrade was checked with Windows PowerShell 5.1: zero parser errors and strict UTF-8 reads passed. Isolated function/loop tests passed for rejection repair and exact JSON feedback, the two-repair cap, approved commit/push before another round, continuation after E2E PASS while readiness work remains, no-change auditing, exact/staged file sets, protected/unexpected branches, changed HEAD, invalid audit types/fields and contradictory terminal decisions. A harmless native-process stand-in returned stdout/stderr and exit 7; valid exact JSON remained usable. Mock fetch/LFS failures retained cached contributor inventory. The real harness, production assets and Git writes were not exercised during upgrade validation.
