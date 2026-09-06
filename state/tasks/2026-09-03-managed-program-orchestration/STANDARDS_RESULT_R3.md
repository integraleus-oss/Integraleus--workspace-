I reviewed all 11 files plus the diff against HEAD and the existing on-disk state artifacts. **I could not execute any test or verification command — Bash was denied in this session (don't-ask mode)**, so every finding below is from static analysis and reading. No files were edited.

---

# Findings

## Critical

### C1 — `validateManagedOutcome` throws on a gate without an `evidence` key, killing the runner
`scripts/managed-outcome-contract.mjs:41`

```js
if (Array.isArray(value.gates) && value.gates.some(x => !x.evidence.some(e => e.kind === "command")))
```

`x.evidence` is unguarded here, unlike every sibling check (`:27`, `:33`, `:47` all guard with `Array.isArray(...) ||` first). The per-gate loop at `:30–33` only requires `evidence` when that gate's own status is `PASSED`; it pushes errors but does not return.

Failure scenario: agent writes `{"status":"SUCCEEDED", …, "gates":[{"id":"G1","title":"g","status":"PENDING"}]}` — a premature-success claim, i.e. exactly the case this contract exists to catch. Line 41 dereferences `undefined.some` → `TypeError`. This is thrown from `managed-agent-runner.mjs:108`, at module top level, before `attempts.push`/`atomicJson` at `:114–115`. Result: unhandled rejection, runner exits nonzero, **no `RESULT.json`, no `agent-result.json` entry for that slice, no validation feedback, no retry**. The supervisor then sees exit≠0 with no validated terminal → `FAILED` (`execution-supervisor.py:140`). The owner gets a bare `FAILED` with zero diagnostics, and the multi-slice correction loop — the core value of this change — never engages.

### C2 — Exactly-once terminal delivery is defeated by an unlocked state-file race between the live supervisor and the recovery service
`projects/execution-supervisor-taskflow/index.js:262–266`, `scripts/execution-supervisor.py:168–170`, `:101–105`

The recovery tick skips only states that are *both* terminal and delivered (`index.js:264`), so it spawns `python3 … recover` against every **RUNNING** state every `pollMs` (default 5000). `recover` does a full read-modify-write of the state document (`execution-supervisor.py:168–169`) with no lock, concurrently with the supervisor's own full-document write every `--poll` (default 0.25s, `:137`).

Failure scenario: `recover` reads state at T0 (`RUNNING`) → supervisor finalizes at T0+ε, writing `status=TIMED_OUT`, `notificationId=exec-<run>-timed_out`, and appending the outbox line → `recover` writes its stale document back at T0+2ε, resetting `status` to `RUNNING` and `notificationId` to `null`. Next tick: pid is dead, no terminal-evidence file exists (timeout path never writes one) → `recover` finalizes as `CRASHED` → `notify_once` computes id `exec-<run>-crashed`, which does **not** match the `…-timed_out` line already in the outbox, so the new dedup scan at `:95–100` misses it and appends a second event. Two notifications, two owner messages, contradictory statuses.

The dedup block added in this diff only helps when the recomputed status happens to match; `TIMED_OUT`, `FAILED`, and `INTERRUPTED` all recompute to `CRASHED` after a state clobber. Separately, the read-then-append in `notify_once` (`:95–102`) is itself not atomic, so two concurrent `recover` invocations (recovery service + manual CLI, or two gateway processes) can both append the same id.

### C3 — A dispatched admission deadlocks its originating session
`projects/execution-supervisor-taskflow/index.js:203–215`, `:285`

Once an admission reaches `DISPATCHED`, `before_prompt_build` (`:206`) still injects *"call `execution_supervisor_dispatch` … Do not use bash, exec, apply_patch, Codex, subagents, or other work tools in this turn"*, while `before_tool_call` (`:211–214`) blocks every tool except `execution_supervisor_dispatch` — and `execution_supervisor_dispatch` itself throws `admission already dispatched` (`:285`). The session has no legal move.

Entries are only cleared in `reconcileState` (`:249–252`) once the supervisor state goes terminal, i.e. up to `managedAgentTimeoutSeconds` (default **3600s**) later. Whether this bites depends on whether `ctx.runId` is populated in `before_prompt_build`/`before_tool_call`: `admissionForContext` (`:104–107`) returns `admissionsByRun.get(ctx.runId)` and **falls through to no lookup at all** when `runId` is present but unmatched. So the deadlock is latent on the `runId` contract — any hook invocation lacking `runId` hits `admissionsBySession` and freezes the session for an hour. The plugin depends on an undocumented invariant it does not assert.

---

## High

### H1 — `contractValidated: true` is hardcoded on every result, so `--require-validated-terminal` validates nothing
`scripts/managed-agent-runner.mjs:117`, `:123`, `:132`; consumed at `scripts/execution-supervisor.py:61`

All three `RESULT.json` writers set `contractValidated: true` — including the `CRASHED` path (`:117`, where no outcome was ever validated) and the budget-exhaustion `FAILED` path (`:132`, where no valid outcome was ever produced). The supervisor's new strict gate (`:61`) therefore reduces to "a file exists at this path with a recognized status", which the pre-existing `path.exists()` check already covered. The field name asserts a property the code does not hold. If the intent is "the terminal status was derived from a validated outcome contract", only `:123` qualifies.

### H2 — Default owner trust admits any Telegram session routed to agent `main`, gating arbitrary command execution
`projects/execution-supervisor-taskflow/index.js:48–53`, `:302`, `:318`

`isTrustedOwnerContext` returns true for any `sessionKey` matching the default prefix `agent:main:telegram:` (`:50–52`). `execution_supervisor_start` checks only `isTrustedOwnerContext` (`:302`) and then executes a caller-supplied `command` array verbatim (`:318`). `config.authorizedSenderIds` is **not** consulted by `isTrustedOwnerContext` — it is only applied on the `before_dispatch` ingress path (`:186`).

Failure scenario: a non-owner participant in any Telegram group whose session routes to agent `main` induces the agent to call `execution_supervisor_start` with `command: ["bash","-c","…"]`. The `safePath` guard (`:55–60`) constrains only the three evidence/state paths, not `command`. This predates the diff, but the diff extends this path (now always `--require-validated-terminal`) without tightening it, and the README (`README.md:12–15`) describes the trust model as "an authenticated channel owner or a session key explicitly allowlisted", which the default wildcard prefix contradicts.

### H3 — No `SIGTERM` handler: gateway shutdown orphans the child and skips finalization
`scripts/execution-supervisor.py:155`

Only `KeyboardInterrupt` is caught. The child is spawned with `start_new_session=True` (`:131`), so a `SIGTERM` to the supervisor (systemd stop, `openclaw gateway restart`, OOM reaper) kills the supervisor without running `finalize` — leaving a live orphaned runner in its own session with **no timeout enforcement, no reaper, and no terminal write**. `recover` then sees `pid_alive` → prints `RUNNING` and returns 0 forever (`:168–170`), which as of this diff now takes priority over terminal-evidence inspection. The state's `disablePath` field claims "SIGINT or terminate foreground supervisor" (`:127`) — the second half is not implemented.

---

## Medium

### M1 — `recover` PID check now shadows terminal evidence; PID reuse wedges the run permanently
`scripts/execution-supervisor.py:168–173`

The diff moved `pid_alive` **above** `terminal_from_evidence` (previously evidence won). `state["pid"]` is the child's PID and is never revalidated against start time or cmdline. After a reboot or PID-space wrap, an unrelated process holding that PID makes `recover` report `RUNNING` indefinitely, and the valid `RESULT.json` sitting on disk is never read. Before this change, evidence would have rescued it. Also note `pid_alive` returns `True` on `PermissionError` (`:53`), so a recycled PID owned by another user also reads as alive.

### M2 — Evidence commands run unsandboxed, untimed, and re-run on every slice
`scripts/managed-agent-runner.mjs:59–63`, invoked from `:112`

`run(item.argv[0], item.argv.slice(1), item.cwd)` executes agent-authored argv with no allowlist and, critically, **no timeout** — `run()` at `:25–34` resolves only on `close`. A gate whose command blocks (a server, a `wait`, a network call with no timeout) hangs the runner past its own `deadline`; the only backstop is the outer supervisor killing the group at `timeoutSeconds`, which discards all slice progress and reports `TIMED_OUT`.

Additionally `evidenceErrors` is called on every slice (`:112`) over *all* PASSED packages and gates, so each gate command is re-executed once per remaining slice — up to 12× (`MANAGED_MAX_SLICES`). Non-idempotent evidence commands will have their side effects replayed.

### M3 — The prompt teaches a blocker-evidence shape the validator always rejects
`scripts/managed-agent-runner.mjs:99` vs `scripts/managed-outcome-contract.mjs:9–15`, `:46–48`

The instruction says `blocker must be {"external":true,"reason":"...","evidence":["..."],"ownerAction":"..."}` — an array of **strings**. `validEvidence` requires objects with `kind: "file"|"command"`; a string returns `false` at `:14`. Every `BLOCKED` outcome written to spec is rejected with "BLOCKED requires an external blocker with reason, evidence, and ownerAction", which does not hint at the shape mismatch. Legitimate external blockers will burn the entire slice budget and terminate as `FAILED` instead of `BLOCKED`.

### M4 — Stale terminal-evidence is only cleared on the strict path
`scripts/execution-supervisor.py:117–118`

`args.terminal_evidence.unlink(missing_ok=True)` is gated on `require_validated_terminal`. With `--terminal-evidence` but no `--require-validated-terminal`, a leftover `RESULT.json` from a previous run at the same path is read on the very first poll (`:138`), and the supervisor immediately SIGTERMs a child that has done no work, finalizing with the previous run's status. The unlink should be unconditional whenever `--terminal-evidence` is supplied.

### M5 — Breaking tool-contract change shipped as a minor version bump, undocumented
`projects/execution-supervisor-taskflow/index.js:298`, `:317`; `openclaw.plugin.json:5`; `README.md`

`terminalEvidencePath` went from `Type.Optional(Type.String())` to required `Type.String()`, and `--require-validated-terminal` is now always passed (`:317`). Any existing caller that supervises a plain command — one that does not write a `contractValidated` result — now gets `FAILED` on a clean exit 0 instead of `SUCCEEDED` (`execution-supervisor.py:140–141`). This is defensible hardening, but it is a contract break released as 0.1.0 → 0.2.0 with no note in the README and no migration guidance.

Related: `Type.String()` has no `minLength`, so `terminalEvidencePath: ""` makes `terminalPath` `null` at `:308` and `spawn` receives `null` in argv at `:317` → `TypeError`. Add `minLength: 1`.

### M6 — `update_evidence` silently deletes agent-written evidence below the marker
`scripts/execution-supervisor.py:76`

`lines = lines[:lines.index(marker)]` truncates everything after `## Execution Supervisor`. The managed runner explicitly instructs the agent to "Update task evidence as work progresses" (`managed-agent-runner.mjs:101`) against the same `EVIDENCE.md`. Anything the agent appends after the supervisor block is destroyed at finalize. Because this diff removed `update_evidence` from the poll loop (`:137`), the loss now happens once, at the end — i.e. precisely when the evidence matters.

### M7 — Undeliverable notifications retry forever with no backoff or dead-letter
`projects/execution-supervisor-taskflow/index.js:226`, `:264`

`deliveryFromDispatch` falls back to `to: ctx.conversationId` (`:155`), which may be `undefined`. `reconcileState` then throws `missing originating delivery context` (`:226`) on every tick. Since `notificationDelivered` never becomes true, the state is never skipped by `:264` — the loop retries and logs an error every 5s indefinitely, and the owner is never told the run finished.

### M8 — Recursive full-tree scan every 5 seconds, forever
`projects/execution-supervisor-taskflow/index.js:66–80`, `:262`

`findStateFiles` walks all of `state/tasks` recursively on each tick and `readState`s every match. This directory already holds 18 state files across a growing tree, and every historical task dir is re-walked forever with no age cutoff or completed-run pruning. Combined with the supervisor's own 4 Hz state writes (`execution-supervisor.py:137`, ~14k fsync+rename per hour-long run just to refresh `lastVerified`), this is a lot of steady-state disk churn for a mostly-idle system.

### M9 — Admitted-but-undispatched work is lost across a gateway restart
`projects/execution-supervisor-taskflow/index.js:100–102`, `:262`

`admissionsByRun` / `admissionsBySession` are in-memory only. The recovery service keys exclusively off `execution-supervisor-state.json`, which is created by the supervisor at `run` time. An admission that is written to disk (`admission.json`, status `ADMITTED`) but never dispatched — gateway restart, crash between `createAdmission` and `dispatchAdmission`, spawn failure — has no recovery path and is silently abandoned. The maps are also never pruned for such records, so they leak.

---

## Low

- **L1 — Tests hardcode absolute workspace paths.** `scripts/managed-agent-runner.test.mjs:46` and `projects/execution-supervisor-taskflow/index.test.mjs:47` embed `/home/stanislav/.openclaw/workspace/agents/main/...`. Both break in any worktree, clone, or CI checkout; use paths relative to `import.meta.url`.
- **L2 — The new outbox dedup branch is entirely untested and unreachable from the existing tests.** `execution-supervisor.py:95–100` is only reachable when `state["notificationId"]` is falsy while the outbox already holds the id. `test_notification_exactly_once_after_recovery` (`test_execution_supervisor.py:44–47`) cannot reach it — `notify_once` early-returns at `:88` because the id is set. The one piece of new exactly-once logic in this diff has zero coverage.
- **L3 — Other new behavior is untested.** No test covers: the strict-mode stale-file unlink (`execution-supervisor.py:118`), the reordered `recover` pid-vs-evidence precedence (`:168–173`), `BLOCKED` reaching `recover`'s TERMINAL branch, backward compat for old states lacking `requireValidatedTerminal`, or — on the runner side — evidence hash mismatch, missing evidence file, plan-lock violation (`planErrors`), or failing evidence commands. `index.test.mjs:157` asserts a magic `sends.length === 3` with no explanation of the expected event set.
- **L4 — `index.test.mjs:179` omits the now-required `terminalEvidencePath`.** The test calls `execute` directly, bypassing schema validation, so it asserts a `safePath` rejection that the real runtime would reject earlier on schema grounds. The assertion no longer tests what it appears to.
- **L5 — Runner `atomicJson` does not fsync and leaks temp files.** `managed-agent-runner.mjs:15–19` renames without fsync (the Python side does fsync at `:36`), and a crash between `writeFile` and `rename` strands a `.<uuid>.tmp` in the task dir permanently.
- **L6 — `argumentsMap` is strictly positional.** `managed-agent-runner.mjs:9–13` assumes perfect `--flag value` pairs; any bare flag silently corrupts every subsequent key. Callers are correct today, but the failure is silent.
- **L7 — `schemaVersion` is written but never read.** The `1 → 2` bump in `RESULT.json` (`managed-agent-runner.mjs:117/123/132`) has no consumer anywhere in the repo; nothing would reject a v1 document.
- **L8 — `MANAGED_MAX_SLICES` is env-only and undocumented.** `managed-agent-runner.mjs:75` reads it, but it is absent from both config schemas and the README, and the plugin never sets it — so it is effectively always 12.
- **L9 — `managedAgentThinkingLevel` is added to both schemas but not documented** in `README.md`.
- **L10 — `safePath` canonicalizes only the root.** `index.js:55–60` compares a resolved-but-not-canonical target against `realpath(root)`; a symlink inside the workspace pointing outward passes. Defense-in-depth only, given H2.

---

## What's done well

- Backward compat on the strict flag is handled correctly: `recover` reads `bool(state.get("requireValidatedTerminal"))` (`execution-supervisor.py:171–172`), so the 18 pre-existing on-disk states — which I confirmed lack both `requireValidatedTerminal` and `contractValidated` — reconcile in legacy non-strict mode rather than being misreported as `CRASHED`.
- The `SIGTERM` → `wait(timeout=5)` → `SIGKILL` escalation added at `:145–147` closes a real hang (the old code let `TimeoutExpired` propagate uncaught), and correctly matches the pattern already used on the timeout path.
- `killpg` on a `start_new_session=True` child is the right call for killing the whole runner tree, and leaving the child unreaped until after `killpg` keeps the process group alive so the signal lands.
- The slice loop's budget arithmetic is sound: the runner's deadline is `timeoutSeconds - 30` against the supervisor's `timeoutSeconds` (`index.js:172`), leaving real slack to write a terminal result before the supervisor kills the group.
- Version bump is consistent across `package.json`, `package-lock.json`, and `openclaw.plugin.json`, and the two config schemas (TypeBox and JSON Schema) are kept in sync.
- `createAdmission` uses `flag: "wx"` with `EEXIST` tolerance (`index.js:131–139`), correctly making context/task/evidence creation idempotent without clobbering.

---

**FAIL**

C1 is a crash on the exact input the contract exists to reject, and it disables the retry loop that is this change's central mechanism. C2 breaks the stated exactly-once guarantee under a race the diff's own recovery service makes likely, not rare. C3 can wedge an owner session for an hour with no recovery. H1 means the headline hardening (`--require-validated-terminal`) does not check what its name claims. These are fixable narrowly — C1 is a one-line guard — but the change should not ship as-is.

I did not run `scripts/test_execution_supervisor.py`, `scripts/managed-agent-runner.test.mjs`, or `projects/execution-supervisor-taskflow/index.test.mjs`; Bash was denied. If you re-run this with execution permitted, I'd start by confirming C1 with a `SUCCEEDED` outcome containing an evidence-less `PENDING` gate.
