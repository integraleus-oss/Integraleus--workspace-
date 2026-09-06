I reviewed all four files inline (no subagents, no edits, no prior review files read).

## What actually holds up

- **Malformed output fails safely.** `loadJson` returns `null` on parse failure (`managed-agent-runner.mjs:23`), validation is wrapped in try/catch (`:141-145`), stale/forged outcomes are rejected by `sliceToken` (`:146`), and the fall-through always writes a `FAILED` result (`:179-184`). Non-`CONTINUE` on slice 1 is rejected (`:147`).
- **The terminal nonce is genuinely kept from the model.** It is read from fd 3 and the fd is closed *before* any spawn (`:93`), `MANAGED_TERMINAL_FD` is stripped from both `process.env` and `childEnv` (`:93`, `:98`), and it never appears in any prompt. Result files carrying it are unlinked at start (`:95`) and only written at exit.
- **Evidence verification is real when it runs.** `evidenceErrors` (`:50-73`) enforces workspace containment, one-artifact-per-claim via `used` (`:63`), non-empty, `mtime >= started`, and sha256 match — and it is unconditionally applied to any `SUCCEEDED`/`BLOCKED` candidate (`:143-144`), with `terminalStatus` gated on zero errors (`:157`).
- **Continuation is bounded** by `maxSlices`, the deadline, and 3 consecutive process failures (`:150-155`).

That is the good half. The gate itself has holes.

## CRITICAL

**1. The "independent locked plan" is reused unvalidated, and the executing model is handed its path.** — `scripts/managed-agent-runner.mjs:90`

`baseline = await loadJson(planPath)` accepts whatever is on disk, and `:99 if (!baseline)` then skips planning entirely. None of the token/shape checks at `:105-108` apply to the reuse path. Meanwhile `:124` explicitly tells the execution agent the plan lives at `${args.outcome}.locked-plan.json`, and nothing prevents it writing there.

Failure scenario: the runner is killed mid-run (the packet's own status is `REVIEW_R7_TIMED_OUT_RETRY_R8`, so this is the observed mode). The exec agent had written `{"packages":[],"gates":[]}` to `planPath`. On restart, planning is skipped, `planErrors` (`:42`) iterates two empty arrays and returns `[]`, so the plan imposes **no constraint at all**. The model now self-selects one package + one gate, writes two junk files, and `validateManagedOutcome` is satisfied. This is the original ZSR shape — success declared over a silently narrowed objective — reachable with one file write.

**2. The terminal review is best-of-N sampling with no cost for failure.** — `scripts/managed-agent-runner.mjs:166-168`

On a review `FAIL`, the runner does `previous = {...outcome, validationErrors:[reason]}; continue;`. `consecutiveFailures` is not incremented, no record of the rejected claim is retained, and the identical claim may be resubmitted with a fresh `sliceToken`. With `MANAGED_MAX_SLICES` defaulting to 12 (`:81`), the model gets up to ~11 independent draws from a stochastic reviewer and needs exactly one `PASS` to make `SUCCEEDED` terminal. The reviewer's `reason` is fed straight back to the executor, handing it the precise objection to route around each round. Compounding this, every review runs under the *same* session key `${session-key}:review` (`:163`), so untrusted evidence text the reviewer ingests in round N persists into rounds N+1…N+k — the one gate that carries the entire semantic guarantee is both resamplable and cumulatively influenceable.

## HIGH

**3. Plan and review tokens are passed on the command line.** — `:102-103`, `:161-164`

`planToken` and `reviewToken` are embedded in `--message` argv, world-readable via `/proc/<pid>/cmdline`. The runner spawns children `detached: true` (`:27`) and never reaps anything the model itself backgrounds. A poller left by an earlier slice can lift `reviewToken` while the review is in flight and write `${result}.review.json` with `verdict: "PASS"` — the runner reads the file only after the review process closes (`:165`), so last-writer wins. The unlink at `:160` does not help. Contrast with the terminal nonce, which is correctly kept off argv and env.

**4. Nothing constrains the planner to a non-trivial plan.** — `:105-108`

The acceptance test is only "≥1 package, ≥1 gate, string ids/titles". A single-package/single-gate plan passes, after which "every package PASSED" (`managed-outcome-contract.mjs:42-43`) is trivially reachable with two artifacts. There is no minimum decomposition, no cross-check against `TASK_PACKET.md` acceptance items, and no second opinion on coverage — so "do not silently narrow it" (`:101`) is an unenforced instruction to a single LLM.

**5. `BLOCKED` is an early escape hatch that requires no attempted work.** — `scripts/managed-outcome-contract.mjs:47-55`

`BLOCKED` requires one package in state `BLOCKED` and no `FAILED` packages/gates. Packages left `PENDING` are unconstrained. So on slice 2 the model can declare `BLOCKED` with 11 of 12 locked packages never touched, one self-written evidence file, and a self-asserted `external: true` (`:49`). Every structural check passes; only the reviewer — see defect 2 — stands in the way. The requirement "BLOCKED only for a genuine external dependency" is not structurally enforced.

**6. Workspace containment fails open.** — `scripts/managed-agent-runner.mjs:85`

`resolve(process.env.MANAGED_WORKSPACE_ROOT || process.cwd())`. Unlike `MANAGED_TERMINAL_FD` (`:92`), this is never required or sanity-checked. If the supervisor launches the runner without it from `/`, the containment check at `:62` accepts every path on the filesystem. Additionally `:61-62` resolves relative paths against `process.cwd()` rather than `workspaceRoot`, and `stat` follows symlinks — an in-workspace symlink to an outside file passes containment while `mtime`/hash are read from the target.

**7. Every evidence guard and the review-rejection path are untested.** — `scripts/managed-agent-runner.test.mjs:74-82`

The fake CLI returns `verdict: "PASS"` unconditionally (`:49`), so `:166-168` never executes in the suite. There is no test for duplicate evidence paths, out-of-workspace evidence, stale `mtime`, hash mismatch, missing evidence file, plan-tampering (removed/renamed package via `planErrors`), planner failure (`:110-113`), or malformed JSON outcome. The suite covers the packet's literal list (`TASK_PACKET.md:32`) while leaving 100% of the anti-false-success machinery unexercised.

**8. The implementation violates its own declared boundary and no acceptance item is marked verified.** — `TASK_PACKET.md:17-19`, `:26-34`

`Allowed:` names `managed-agent-runner.mjs`, its tests, `execution-supervisor.py`, supervisor tests, and the TaskFlow plugin. `scripts/managed-outcome-contract.mjs` — a new untracked file holding the entire contract — is outside that list. All nine acceptance boxes remain `[ ]`. Separately, acceptance item `:31` ("reconciled by supervisor") is not verifiable within the four files I was scoped to, so objective completeness cannot be established from this set alone.

## Verdict

The scaffolding is sound — fd-based secret handling, evidence hashing/freshness/distinctness, and safe failure are correctly built. But the two properties the design leans on hardest do not hold: independent planning is bypassable via unvalidated plan reuse on any restart (defect 1), and the terminal review is a resamplable gate the model can retry until it passes (defect 2). Both reopen the original false-success class directly.

**FAIL**
