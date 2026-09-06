I read all four files in full. Analysis below.

## What holds up

**Independent locked planning before execution** — `managed-agent-runner.mjs:112-127`. A separate `openclaw agent` session (`:planner:<uuid>`) must write `planPath` with a matching `planToken` before any execution slice. Plan is then independently reviewed (`:138-144`) and digest-locked (`:128`), with integrity re-checked at every slice head (`:149`) and again inside the terminal slice (`:195`). `planErrors` (`:44-53`) blocks removal or retitling of any locked package/gate, and `:183` forbids slice 1 from being terminal. Silent narrowing is genuinely closed off.

**Bounded continuation** — `:186-191`. Nonzero exit never feeds `previous`, so a crashed slice cannot carry an outcome forward; retries cap at 3 consecutive, `maxSlices` ≥2 is enforced (`:94`), and the deadline gates each iteration (`:154`, `:172`).

**Evidence integrity** — `evidenceErrors` (`:55-83`) is solid. `realpath` containment (`:70`) defeats symlink escape; freshness against `evidenceStarted` (`:76`) plus mandatory in-content `evidenceToken` (`:77`) defeats stale-artifact reuse; the `used`/`usedHashes` pair (`:71`) enforces one *distinct artifact and distinct content* per PASSED claim — a duplicate cannot slip through by claiming a different hash, because the hash-vs-content check at `:78` catches the mismatch. Exit code 0 alone is inert: `terminalStatus` derives only from the validated contract.

**Secret handling** — the terminal nonce arrives on fd 3, is read and closed before any spawn (`:106`), scrubbed from `process.env` and `childEnv` (`:106`, `:111`), and `run()` gives children only fds 0–2. `RESULT.json` (the only file containing the nonce) is unlinked at startup (`:86`) and rewritten only after all children have exited, so no model process ever sees it on disk.

**Malformed output** — `loadJson` returns null on parse failure, validation is wrapped (`:177-181`), and the `sliceToken` check (`:182`) sits outside the try so it always runs. Covered by `FAKE_BAD_JSON`, `FAKE_SKIP_OUTCOME`, `FAKE_BAD_SLICE_TOKEN`.

## HIGH defects

**1. The terminal review prompt does not cover the BLOCKED case — `scripts/managed-agent-runner.mjs:205`**

Both terminal statuses route through the same reviewer message (`:193-216`), but that message asks only whether *"the complete owner objective is satisfied"* and says *"PASS only if fully justified."* For a BLOCKED candidate the objective is by definition **not** satisfied, so a compliant reviewer returns FAIL and a legitimate external blocker is converted to `terminalStatus: "FAILED"`, exit 5 (`:212-215`). The BLOCKED path is effectively unreachable in production.

The mirror-image risk is worse: nothing in the review prompt asks the reviewer to assess *externality*. `blocker.external === true` is a model self-assertion (`managed-outcome-contract.mjs:49`) and blocker "evidence" is satisfied by any fresh workspace file containing the run token. So if a reviewer resolves the prompt ambiguity toward "the outcome is well justified," BLOCKED becomes the cheapest escape from a hard objective — exactly the ZSR shape, relocated from SUCCEEDED to BLOCKED. The strong contract-level guards at `managed-outcome-contract.mjs:52-55` constrain the *shape* of the claim, not its truth.

This is masked by the test suite: the fake reviewer at `scripts/managed-agent-runner.test.mjs:52` returns PASS unconditionally, so `:91` (`[passed("CONTINUE"), blocked] → 4, "BLOCKED"`) passes without ever exercising a reviewer that reasons about the blocker. Contract branches `:53-55` (BLOCKED with PENDING/RUNNING, FAILED packages, FAILED gates) have no test at all, and there is no negative test for stale / out-of-workspace / token-less *blocker* evidence.

**2. Planning and plan review run outside the time budget — `scripts/managed-agent-runner.mjs:116` and `:138`, vs. deadline at `:98`**

`deadline` is computed from `runStarted` before planning, but neither the planner nor the plan reviewer consults it: both are hard-coded to `--timeout 300` with a 315 000 ms wall kill. That is up to **630 s consumed before the first execution slice**, while `:94` accepts any `totalSeconds >= 5`.

Concretely, with the suite's own `--timeout 240` (`test.mjs:70`) and a real planner: 200 s planning + 200 s review → the deadline has already passed when the loop starts, `remainingSeconds` clamps to 1 (`:153`), `<= 15` breaks immediately (`:154`), `attempts.length === 0`, and the runner emits `terminalStatus: "FAILED"` with the summary *"did not reach a valid terminal contract within the slice/time budget"* (`:227-229`). Two failures at once: **no execution slice can ever run** for any budget under roughly 640 s + slice minimum, and the runner **overruns its declared `--timeout` by ~2.6×**, which will collide with any external supervisor kill. The failure summary is also misleading — it names the slice budget when the budget was spent entirely on planning. The test suite cannot catch this because the fake `openclaw` returns instantly.

## Lower-severity, worth noting

- `run()` rejects on spawn error (`child.on("error", reject)`), and every call site (`:115`, `:137`, `:173`, `:204`) awaits at top level with no catch. A missing `OPENCLAW_BIN` or a transient `EAGAIN` during the terminal review kills the process with exit 1 and **no `RESULT.json` at all** (it was unlinked at `:86`). Safe against false success, but it shifts the burden onto the supervisor to treat an absent result as failure.
- No test asserts the child cannot read fd 3 directly. The fake only checks the `MANAGED_TERMINAL_FD` env var (`test.mjs:49`), so the fd-isolation property is correct by construction but unverified.
- `if (!baseline)` at `:112` is vacuous (`baseline` is `null` from `:103` and never assigned before it) — dead conditional, harmless.
- `args.outcome` is not unlinked at startup, unlike `args.result` (`:86`) and `planPath` (`:101`), so a stale prior-run contract is loaded into `previous` (`:102`) and embedded in slice 1's prompt. Benign — the fresh `sliceToken` check rejects it — but inconsistent with the other reset paths.

## Verdict

**FAIL**

The anti-false-SUCCEEDED machinery — locked independent plan, distinct fresh workspace-contained token-bound artifacts, dual injection-aware terminal review, exit-code-independent terminal derivation — is objectively sound and I found no path to a fabricated SUCCEEDED. It fails on the other two required properties: BLOCKED is not independently validated as a genuine external dependency (and is simultaneously unreachable for legitimate blockers), and the time budget is not honored across the planning phase, which can deterministically prevent any execution slice from running.
