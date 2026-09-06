I inspected the eight requirement areas against the implementation, plus a live artifact from a prior managed run. Findings below; no files were edited.

## CRITICAL

**C1 — Supervisor still converts exit code 0 into SUCCEEDED.** `scripts/execution-supervisor.py:126-129`
```python
observed = terminal_from_evidence(args.terminal_evidence)
if code is not None:
    return finalize(..., observed or ("SUCCEEDED" if code == 0 else "CRASHED"), code)
```
This is the exact line that produced the original ZSR incident (`state/tasks/2026-09-03-managed-program-orchestration/EVIDENCE.md:9-10`), and `git diff scripts/execution-supervisor.py` shows the scoped change touched only `TERMINAL`/`EVIDENCE_MAP` (adding `BLOCKED`). The rule "exit 0 ⇒ SUCCEEDED" is untouched. Whenever terminal evidence is absent, unreadable (`terminal_from_evidence` swallows `JSONDecodeError`/`OSError` at :59-60), or carries an unmapped status, a zero exit is still recorded as objective success. `projects/execution-supervisor-taskflow/index.js:302,311` makes `--terminal-evidence` optional for `execution_supervisor_start`, so that tool path is *always* governed by exit code alone. Requirement 1 is not met at the layer that persists the terminal state.

**C2 — Terminal evidence is agent-writable and unauthenticated.** `index.js:124,166` + `index.js:45` + `execution-supervisor.py:126,130-132`
The supervisor polls `RESULT.json` and treats any `{"status":"SUCCESS"|"ACCEPTED"|"SUCCEEDED"}` as terminal, kills the runner's process group, and finalizes SUCCEEDED. `RESULT.json` lives in the task dir the managed agent works in, carries no run id/nonce, and `evidenceMarkdown` (`index.js:45`) advertises it to the agent as `Expected output`. That advertisement survives every supervisor rewrite — see `state/tasks/managed-admission/8989af44-.../EVIDENCE.md:9`, which the agent demonstrably read and appended to. A single file write by the very agent whose self-report is untrusted terminates the run as SUCCEEDED and bypasses `MANAGED_OUTCOME.json`, the slice loop, and the whole contract. This reproduces process-success/objective-failure divergence in one step.

**C3 — The completion gate is pure self-attestation; nothing is verified.** `scripts/managed-outcome-contract.mjs:19,25,29-34`; `scripts/managed-agent-runner.mjs:66-80`
`evidence` is validated only as "array of non-empty strings" (`nonEmpty`, contract:5-7). No path is resolved, no gate command is executed, no external checker runs. Packages and gates are proposed, executed, evidenced, and marked PASSED by the same agent, then accepted by the runner. The project's own test encodes the minimal bypass: `scripts/managed-agent-runner.test.mjs:15-18` reaches valid SUCCEEDED with one package and one gate whose evidence is the literal string `"test"`. Requirement 4 ("PASSED with evidence") is satisfied syntactically, not semantically — the bar moved from "exit 0" to "well-formed JSON asserting success", which is still a process-level self-report.

**C4 — No cross-slice contract monotonicity; the objective is not restated on continuation.** `managed-agent-runner.mjs:62-63,82`
Slice 2+ receives only `Continue the same managed objective. Your previous contract was: <JSON>` — the TASK_PACKET text is never re-sent (only slice 1 gets `${task}`), and `previous` is never compared against the new outcome. A slice that declared 10 packages can return a 1-package contract with everything PASSED and `objectiveComplete=true`, and `terminalStatus()` accepts it. Silent objective narrowing across slices → SUCCEEDED on partial work. This is the same divergence the packet claims to prevent (`TASK_PACKET.md:26`).

## HIGH

**H1 — Stale/foreign `RESULT.json` makes the runner exit 0 with no terminal contract.** `managed-agent-runner.mjs:50` vs `:85-90`
The runner unlinks `args.outcome` each slice but never unlinks `args.result` at startup. The final guard is `if (!(await loadJson(args.result)))` — if any prior or agent-written `RESULT.json` exists, the FAILED fallback is skipped, `process.exitCode` stays unset, and node exits 0. Feeding into C1/C2 the supervisor then reports the stale status (or SUCCEEDED on exit 0). Reachable whenever a task dir is reused: `admissionId(ctx.runId)` (`index.js:36-37,114`) makes the dir deterministic for a given run id. `managed-agent-runner.test.mjs:46` removes `RESULT.json` before every scenario, so this path is untested.

**H2 — BLOCKED externality is asserted, not evidenced, and is never cross-checked.** `managed-outcome-contract.mjs:35-40`
The only requirement is `blocker.external === true` plus three non-empty fields. Nothing correlates the blocker with package/gate state: an outcome whose packages are all `FAILED` for internal reasons (failed tests, unfixed defects) is accepted as terminal BLOCKED, delivered to the owner, and marked `runtime.fail(...)` in TaskFlow (`index.js:245`). Requirement 6 ("internal defects, failed tests, task size, remaining work cannot be BLOCKED") is enforced only by prompt text at `managed-agent-runner.mjs:60`, i.e. by the same untrusted narrator.

**H3 — Terminal notification can be delivered twice.** `execution-supervisor.py:125` vs `:150-157,160-164`; `index.js:222-235,256-261`
The recovery service runs `recover` against *live* RUNNING states every `pollMs` (`index.js:258` only skips already-delivered terminals). If `recover` observes terminal evidence first (`supervisor:152-153`) it finalizes, writes `notificationId`, and the plugin sends. The still-running supervisor's next poll unconditionally rewrites the state file from its in-memory dict (`supervisor:125`, status `RUNNING`, `notificationId: None`), destroying that bookkeeping; its own `finalize` then passes the `:100` guard and `notify_once` appends a second outbox line, which the recovery tick delivers again. `notify_once` deduplicates on in-memory state only — it never scans the outbox ledger for the event id. Separately, `index.js:227-233`: if `sendText` succeeds and the `ack` spawn fails or the Gateway dies before it, the next tick re-sends (only the adapter's `deliveryQueueId` handling stands between that and a duplicate). Requirement 7 ("delivered once") is not structurally guaranteed.

## MEDIUM

**M1 — "Bounded slices" bounds count, not time.** `managed-agent-runner.mjs:48` gives each slice the *entire* remaining budget, so slice 1 can consume all 3600s; `:49` then breaks and the run ends FAILED with no continuation ever happening — the original 458s single-shot shape is still permitted. The runner also enforces no deadline of its own (it trusts the child's `--timeout`), and `index.js:167,171` gives the supervisor and the runner the identical deadline, so the supervisor's SIGTERM can land before the runner writes its own terminal contract.

**M2 — Validation errors are not returned to the next slice.** `managed-agent-runner.mjs:82`: `previous = outcome || {...validationErrors}` — the errors are attached only when the file is missing. An outcome present but invalid (e.g. SUCCEEDED without evidence) is echoed back verbatim with no reason, so the agent repeats it and burns all 12 slices.

**M3 — Admissions are never cleared, deadlocking a session.** `index.js:100-107,141-142,174-175,207-213`. `admissionsBySession` is written on admission and dispatch and removed nowhere. For any hook context lacking `runId` (which is how `before_dispatch` itself creates admissions — `index.js:187`, and the ingress test ctx at `index.test.mjs:96-97` has no `runId`), `admissionForContext` returns the old DISPATCHED record forever: every tool call is blocked with "already detached" (`:211`) and `execution_supervisor_dispatch` throws "already dispatched" (`:279`). Only contexts that carry a fresh `runId` escape (`index.test.mjs:168-171`).

**M4 — Admission→dispatch gap has no durable recovery.** The maps are in-memory only; a Gateway restart after `createAdmission` but before `dispatchAdmission` leaves a task dir with no `execution-supervisor-state.json`, which `findStateFiles` (`index.js:66-80,256`) cannot see. The owner's request ends with no run, no terminal state, and no notification at all.

**M5 — Evidence file grows without bound and is rewritten every poll.** `execution-supervisor.py:73-82`: `lines = lines[:lines.index(marker)]` retains the blank line preceding the marker, then `:76` appends another `""` — one blank line per poll, with a full read-modify-write + `fsync` at 0.25 s. Observed in the artifact: `state/tasks/managed-admission/8989af44-.../EVIDENCE.md` is 453 lines, ~430 of them blank, from a 90-second run. A 3600 s managed run yields ~14k lines and O(n²) I/O, and the loop clobbers concurrent agent edits to the file the agent is instructed to update (`managed-agent-runner.mjs:61`).

## LOW

- **L1** `index.js:21-23` and `openclaw.plugin.json` allow `adaptive`, which can resolve below `high` for a complex slice; the runner accepts any `--thinking` value unvalidated (`managed-agent-runner.mjs:65`). Requirement 8 holds only by config discipline — `low` is at least excluded from the schema and both defaults are `high`.
- **L2** `schemaVersion` is emitted in the instruction (`managed-agent-runner.mjs:56`) but never validated (`managed-outcome-contract.mjs:9-43`) — silent schema drift.
- **L3** `managed-agent-runner.mjs:31` resolves on `exit`, not `close`, so captured `stdout`/`stderr` can be truncated; `:69` rewrites the whole growing `attempts` array (with full transcripts) once per slice.
- **L4** `Number(args.timeout)`/`MANAGED_MAX_SLICES` are unvalidated (`:41,43,48`): a non-numeric timeout propagates `NaN` to the child's `--timeout`; a non-numeric slice count silently yields zero slices.
- **L5** Test gaps for every path above: no stale-`RESULT.json` case, no agent-written-terminal-evidence case, no contract-shrinkage case, no supervisor test for "exit 0 with no terminal evidence", and `test_execution_supervisor.py:29` actually *asserts* the exit-0⇒SUCCEEDED behavior as correct.

## Requirement verdict

| # | Requirement | Result |
|---|---|---|
| 1 | exit 0 alone cannot prove completion | **FAIL** (C1, C2, H1) |
| 2 | decomposition into packages + gates | Partial — durable but unconstrained (C3, C4) |
| 3 | partial work continues in bounded slices | Partial — continuation works (test:55-56); slice bounding is count-only (M1) |
| 4 | SUCCEEDED requires all PASSED with evidence | **FAIL** — evidence unverified, contract mutable (C3, C4) |
| 5 | BLOCKED requires evidenced external dep + owner action | Partial — shape only (H2) |
| 6 | internal defects/tests/size cannot be BLOCKED | **FAIL** — prompt-only (H2) |
| 7 | reconciled through supervisor/TaskFlow, delivered once | **FAIL** (H3); reconciliation path itself is wired correctly |
| 8 | complex slices do not inherit low thinking | **PASS** with caveat (L1) |

The change is a real improvement over the previous runner — the outcome contract, the continuation loop, and preserving `BLOCKED` as terminal all work as described. But the trust boundary was never closed: the decision "objective complete" is still made entirely inside the agent process, and the two mechanisms that carry it out of that process (`RESULT.json` and the supervisor's exit-code fallback) remain unauthenticated and unchanged. C1 through C4 are each independently sufficient to reproduce process-success/objective-failure divergence.

**FAIL**
