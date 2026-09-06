I reviewed the scoped diff statically. **Bash execution is denied in this session, so I could not run the three test suites** — all findings below are from reading the code, and the "tests PASS" claims in `state/tasks/2026-09-03-managed-program-orchestration/EVIDENCE.md:19-26` are unverified by me.

---

# HIGH

### H1 — The evidence-existence gate is silently skipped on any status casing other than exact uppercase
`scripts/managed-agent-runner.mjs:49-50` vs `scripts/managed-outcome-contract.mjs:18-19,27-28`

The validator normalizes case (`String(item?.status || "").toUpperCase()`), but the evidence checker compares raw: `.filter(item => item.status === "PASSED")` and `outcome?.status === "BLOCKED"`.

An outcome with `"status":"succeeded"` and packages/gates at `"status":"passed"` passes `validateManagedOutcome` in full (line 18 uppercases, line 19 only requires non-empty *strings*, line 27-28 uppercase the open-item filter), `terminalStatus()` returns `SUCCEEDED` — and `evidenceErrors()` matches nothing, so **no evidence file is ever stat'ed**. The run is accepted as SUCCEEDED with entirely fabricated evidence paths. Same hole for a lowercase `"blocked"`: `blocker.evidence` is never checked.

This is not adversarial-only; lowercase or title-case enum values are ordinary model output. It defeats acceptance criterion "Partial work cannot produce `SUCCEEDED`" (`TASK_PACKET.md:26`), which is the entire point of the change.

### H2 — One non-zero slice exit aborts the whole objective, and the 600 s slice cap makes that likely
`scripts/managed-agent-runner.mjs:94,106-110`

`sliceSeconds = Math.max(2, Math.min(600, remainingSeconds - 10))` hard-caps every slice at 10 minutes regardless of the 3600 s budget, and there is no knob for it. Line 106 then treats *any* non-zero child exit as terminal `CRASHED` and breaks out, discarding all remaining slices and time.

The originating incident recorded in `EVIDENCE.md:8` is a slice that ran **458 405 ms (≈7.6 min)** — within a factor of 1.3 of the cap. A slice that needs longer hits `openclaw agent --timeout`, which will almost certainly exit non-zero, and the entire managed program is reported `CRASHED` with ~50 minutes of budget and 11 slices unused. There is no distinction between "this slice timed out, retry with the remaining budget" and "the agent binary is broken."

### H3 — `evidenceErrors` throws on malformed model output, killing the runner before any diagnostics are written
`scripts/managed-agent-runner.mjs:49-52`

Unlike the validator, this function uses `item.status` (no optional chaining) and passes `item` straight to `isAbsolute()`. Concrete inputs that crash it:

- `"packages":[null]` → `TypeError: Cannot read properties of null (reading 'status')`
- `"packages":[{"id":"P1","title":"t","status":"PASSED","evidence":[123]}]` → `isAbsolute(123)` → `TypeError: path must be of type string`

Line 102 awaits `evidenceErrors(outcome)` **before** line 104-105 push the attempt and write `agent-output.json`. So the rejection is unhandled at top level, node exits non-zero, `RESULT.json` is never written, and the slice's stdout/stderr/outcome are never persisted. The supervisor reports `FAILED` with zero forensics. Malformed JSON from the agent is precisely the input class this module exists to survive.

---

# MEDIUM

### M1 — Time-budget tail spawns degenerate 2-second slices
`scripts/managed-agent-runner.mjs:76-77,94`

The loop only breaks at `remainingSeconds <= 1`, but `sliceSeconds` is floored at `2` via `Math.max(2, …)`. When `remainingSeconds` drops below 12, the 10-second reserve is violated and the runner keeps launching 2-second agent invocations that cannot do useful work, each consuming one of the 12 slices and each likely exiting non-zero → H2 fires and the result is `CRASHED` rather than the intended budget-exhaustion `FAILED`. With the schema-minimum `managedAgentTimeoutSeconds: 60` (`index.js:20`) the runner gets 30 s total and enters this regime on slice 2.

### M2 — The plan baseline is locked from the first *structurally non-empty* outcome, valid or not
`scripts/managed-agent-runner.mjs:99-101`

`baseline` is captured whenever `packages` and `gates` are non-empty arrays — `checked.errors` is not consulted. If slice 1 emits a plan that fails validation for an unrelated reason (bad status enum, missing summary), its ids and titles are still frozen. Every later slice that corrects a title then fails `planErrors` with "title cannot change", and the feedback loop at line 92 actively instructs the agent to keep the bad title. The run cannot recover and burns all 12 slices to `FAILED`.

### M3 — Evidence paths resolve against an undefined cwd and are not confined to the workspace
`scripts/managed-agent-runner.mjs:52`

`resolve(process.cwd(), item)` — the runner's cwd is inherited from the detached supervisor, which inherits the gateway's cwd. Nothing in the contract instruction (`:84-91`) tells the agent what relative paths are relative *to*, so relative evidence is validated against an arbitrary directory. Conversely, absolute paths get no containment check: `"evidence":["/etc/hostname"]` is a non-empty file and satisfies the gate. The check proves "some non-empty file exists," not "this file contains the claimed result," which is weaker than what `README.md:31-36` advertises.

### M4 — `recover` now prefers PID liveness over terminal evidence, so a recycled PID pins a run at RUNNING forever
`scripts/execution-supervisor.py:166-171`

The reorder is correct for the common case (don't finalize on an intermediate result while the child still runs), but `state["pid"]` is the *supervised child's* pid and there is no identity check (start-time, cmdline, or a supervisor-owned lock). After a host reboot, any recycled pid makes `pid_alive()` true permanently; the previous ordering would have rescued the run from `RESULT.json`. The plugin's recovery service scans every `state/tasks/**/execution-supervisor-state.json` on a 5 s timer (`index.js:262-266`), so such a state file is re-polled forever, never finalized, and no owner notification is ever emitted.

### M5 — The three behaviours most changed here have no test coverage
- `scripts/execution-supervisor.py:94-100` (new outbox duplicate scan): `test_notification_exactly_once_after_recovery` (`test_execution_supervisor.py:44-47`) returns at line 88 because `notificationId` is already set in state. The new scan is never entered. The crash window it closes — outbox appended, state write lost — is not simulated.
- `scripts/execution-supervisor.py:166-171` (the recover reorder): no test at all.
- Strict mode with a terminal file that *exists* but lacks `contractValidated` (line 61): `test_strict_exit_zero_without_validated_terminal_fails` passes `terminal=False`, so it only covers the file-absent case.
- `planErrors` (`managed-agent-runner.mjs:35-44`) and the negative path of `evidenceErrors`: zero coverage. Every scenario in `managed-agent-runner.test.mjs:53` substitutes `__EVIDENCE__` with a real file, so a missing-evidence rejection is never exercised.
- No test drives the deadline path (all fake slices return instantly), so M1 is invisible to the suite.

### M6 — Killing the process group may not cancel the agent turn it started
`projects/execution-supervisor-taskflow/index.js:172`, `scripts/managed-agent-runner.mjs:95-96`

The runner correctly spawns `openclaw` non-detached, so it shares the supervised process group and `killpg` reaches it. But `openclaw agent --session-key agent:main:managed:<id>` is a session-keyed invocation; if the CLI is an RPC front-end to the gateway (which the `--session-key`/`--json` shape strongly suggests), SIGTERM kills the client while the gateway-side turn keeps running — writing `MANAGED_OUTCOME.json` and mutating the repo after the supervisor has already finalized `TIMED_OUT` and notified the owner. I could not verify the CLI's architecture in this session; if the turn is not cancelled on client death, the timeout path does not actually stop work.

---

# LOW

- **L1** `managed-agent-runner.mjs:107` — the `CRASHED` record is written with `contractValidated: true` when no contract was validated. It works only because the supervisor treats the field as a boolean gate, not a claim; it makes the persisted artifact misleading.
- **L2** `managed-agent-runner.mjs:73` vs `execution-supervisor.py:133-136` — the stale-`RESULT.json` unlink happens inside the runner, after the supervisor has already started polling. On a re-dispatch into an existing `state/tasks/managed-admission/<id>/` the supervisor can read the previous run's result (which always carries `contractValidated: true`) in its first poll and finalize on it. Narrow window and requires runId reuse, but the fix is to clear it in the plugin before spawn.
- **L3** `index.js:20-23` / `managed-agent-runner.mjs:65` — `managedAgentThinkingLevel` was added to both the TypeBox and JSON schemas, but `MANAGED_MAX_SLICES` and the 600 s slice cap remain env-only/hard-coded. Inconsistent config contract for two knobs of the same mechanism.
- **L4** `index.js:238-252` — the new admission cleanup sits behind the `!state.sessionKey || !state.flowId` and `!record` early returns, and only covers dispatched runs that reach terminal. Admissions created in `before_agent_run` that are never dispatched stay in `admissionsByRun` (with the full prompt) and on disk for the process lifetime; twelve such directories already exist under `state/tasks/managed-admission/`.
- **L5** `execution-supervisor.py:135` — `update_evidence` was dropped from the poll loop. The trailing-blank-line fix at line 77 makes that safe, but `EVIDENCE.md` now freezes "Last verified" for the whole run unless the plugin's recovery service is up. A human reading the evidence file can no longer tell a live run from a hung one.
- **L6** `managed-agent-runner.mjs:14-18` — `atomicJson` renames without `fsync` (the Python side does fsync at `execution-supervisor.py:36`), and a kill between write and rename leaks an unattributable `.<uuid>.tmp` in the task directory.
- **L7** `managed-outcome-contract.mjs:15-26` / `managed-agent-runner.mjs:39` — duplicate package/gate ids are not rejected, and `planErrors` uses `.find`, which matches only the first. An agent can emit `P1` twice and satisfy the lock with either copy.
- **L8** `managed-agent-runner.test.mjs:42` — the runner path is hardcoded to `/home/stanislav/.openclaw/…`. Pre-existing, but the rewrite was the moment to switch to `new URL("./managed-agent-runner.mjs", import.meta.url)`.
- **L9** `managed-outcome-contract.mjs:9-45` — the instructed shape includes `"schemaVersion":1` (`managed-agent-runner.mjs:85`) but nothing validates it, so there is no version handle for a future contract change.

---

# Positives

The `update_evidence` trailing-blank-line pop (`execution-supervisor.py:77`) is the correct fix for the unbounded EVIDENCE.md growth visible in the working tree. The SIGKILL escalation (`:144-145,149-150`) closes a real hang. The `notify_once` outbox scan (`:94-100`) closes a genuine exactly-once gap — the write→fsync→state-persist ordering means a crash in the window now converges to no duplicate. Awaiting `"spawn"` (`index.js:174,320`) replaces a previously *uncaught* `error` event on a listener-less ChildProcess. Poll order in the supervisor (`:134` then `:136`) reads terminal evidence after observing exit, which is the right direction. Versions are consistent across `package.json`/`package-lock.json`/`openclaw.plugin.json` at 0.2.0, and the two config schemas mirror each other.

# Design limitation (not a defect, but it bounds the claim)

The package/gate plan is authored by the same agent it constrains, and `objectiveComplete` is self-asserted. `planErrors` prevents removal and renaming but not a deliberately thin slice-1 plan, and nothing checks the plan against the owner objective. `SUCCEEDED` therefore means "the agent kept the promises it made in slice 1 and named files that exist" — meaningfully stronger than exit code 0, but weaker than `TASK_PACKET.md:26-31` implies. Worth stating plainly in `README.md` before activation.

# Rules alignment

Boundaries in `TASK_PACKET.md:17-22` are respected: the diff touches only the allowed files, unrelated dirty files are untouched, and nothing was committed or activated. `TECHNICAL-RULES.md:44-53` (checks chosen by risk, and say so when a check is impossible) — I am flagging that I could not execute any of the three suites here.

---

**FAIL**

H1 alone means the evidence gate — the central mechanism of this change — can be bypassed by ordinary case variation in model output, so the stated acceptance criteria are not met. H2 and H3 make the slice loop abort on inputs that will occur in normal operation. H1 and H3 are small, local fixes (normalize status once in the contract module and export the normalized view; guard `evidenceErrors` against non-string/non-object entries). H2 needs a decision on slice-timeout retry semantics before activation.
