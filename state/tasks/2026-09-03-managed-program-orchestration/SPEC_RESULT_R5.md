Confirmed: `index.js:113` skips admission for `agent:main:managed:*`, so `before_tool_call` (`index.js:211-212`) never engages for the worker slice — the managed agent has unrestricted shell.

# Spec Review R5 — Managed Program Orchestration

## Verdict summary

The contract layer is genuinely well-built: `validateManagedOutcome` structurally enforces every requirement you listed, slice-1 plan locking is durable, `CONTINUE` loops are bounded, and `--require-validated-terminal` closes the original ZSR path. But the whole scheme rests on one secret — `terminalNonce` — and **that secret is written to a file in the directory the managed agent works in.** Everything above it is bypassable.

---

## CRITICAL

### C1 — The terminal nonce is stored in the managed agent's own task directory

`scripts/execution-supervisor.py:143` mints the nonce; `:150` writes the entire `state` dict — nonce included — to `args.state`, and `:155` rewrites it on every poll tick. That path is `projects/execution-supervisor-taskflow/index.js:123`, i.e. `<taskRoot>/execution-supervisor-state.json` — the same directory as `MANAGED_OUTCOME.json` (`index.js:126`), whose absolute path is handed to the agent at `scripts/managed-agent-runner.mjs:108`.

The state file also contains `command` (the full runner argv, including `--result <RESULT.json>`) and `terminalEvidencePath` — confirmed in the on-disk sample `state/tasks/managed-admission/e4799e79-.../execution-supervisor-state.json:10-27`. So one file read yields **both the nonce and the exact target path**.

The managed agent has unrestricted bash: `index.js:113` returns `null` for `agent:main:managed:*`, so `before_tool_call` (`index.js:211-212`) never engages.

Failure scenario: slice 2 agent runs `cat <taskRoot>/execution-supervisor-state.json`, then writes `RESULT.json` = `{"contractValidated":true,"terminalNonce":"<leaked>","terminalStatus":"SUCCEEDED"}`. Supervisor `:156` accepts it, `:162` kills the runner group, `finalize` persists `SUCCEEDED`. Zero packages, zero gates, zero evidence, no independent review. **This is the ZSR failure mode reproduced exactly**, with strictly less work than the original.

`EVIDENCE.md:42-43` claims the nonce "is not exposed to the managed model process." That claim is false as written.

### C2 — The nonce leaks into agent-controlled evidence commands

`managed-agent-runner.mjs:25` defaults `env = process.env`. `:70` invokes evidence commands without passing `childEnv`, so `MANAGED_TERMINAL_NONCE` (present per `:93`) is in their environment. `argv` and `cwd` are fully agent-authored (`managed-outcome-contract.mjs:12-13`).

The `delete childEnv.MANAGED_TERMINAL_NONCE` at `:120` protects only the agent and review spawns (`:122`, `:153`). A gate declaring `argv: ["/bin/sh","-c","env > /tmp/x"], expectedExit: 0` exfiltrates the nonce during validation of a candidate terminal outcome — before the review runs, and regardless of whether the review later rejects.

### C1/C2 architectural note

Both are instances of a deeper problem: the runner and the agent run as the **same user**, so `/proc/<runner-pid>/environ` is readable too. Withholding an env var (`:120`) is not a boundary against a same-user process with shell access. A nonce can prevent *accidental* stale-file pickup; it cannot be the authorization mechanism for terminal state. Sealing C1 and C2 narrows the aperture but does not close the class.

---

## HIGH

### H1 — Gate "command evidence" proves nothing

`managed-outcome-contract.mjs:46` requires every gate to carry a `kind:"command"` evidence entry on `SUCCEEDED` — the strongest structural check in the design. But `:12-13` accepts any `argv`/`cwd` with any integer `expectedExit`, and `managed-agent-runner.mjs:70-71` compares **only the exit code**, discarding stdout.

`argv:["/bin/true"], expectedExit:0` passes. So does `argv:["/bin/false"], expectedExit:1`. The agent authors both the assertion and the oracle. Nothing links a gate command to the owner objective.

Same for file evidence: `:62-63` verifies existence, non-emptiness, and hash — but the agent wrote the file, so the hash only proves it didn't change between slices.

Net: "SUCCEEDED requires all packages/gates PASSED with evidence" is structurally enforced but semantically empty. The only real check is the independent reviewer (`:148-158`) — a genuine mitigation, but it is LLM judgment, not a gate.

### H2 — Internal defects can be laundered into BLOCKED

Requirement: internal defects, failed tests, task size, and remaining work *cannot* be used as BLOCKED. `managed-outcome-contract.mjs:55-56` blocks the honest route (`FAILED` packages/gates are rejected), but `:51` accepts `blocker.external === true` as a **self-asserted boolean**.

Failure scenario: agent cannot fix a failing test. It marks the package `BLOCKED` (never `FAILED`), sets `external:true`, `reason:"upstream API returns 500"`, writes a log file it authored as blocker evidence (passes `:62-63`), and supplies `ownerAction`. Validation passes; terminal `BLOCKED` is delivered. The prompt at `managed-agent-runner.mjs:114` forbids this in prose only.

---

## MEDIUM

### M1 — Fail-safe behavior is opt-in, not default
`execution-supervisor.py:142` derives `requireValidatedTerminal` from caller flags; `:160-161` still falls back to `observed or ("SUCCEEDED" if code == 0 else "CRASHED")`. The plugin always passes the flag (`index.js:167,170`), so the live path is safe — but the supervisor's *default* remains "exit 0 ⇒ SUCCEEDED". Any future caller that forgets the flag silently restores ZSR. The default should be strict with an explicit `--allow-exit-code-terminal` escape.

### M2 — `createAdmission` is not idempotent
`index.js:110-145` never checks `admissionsByRun` for an existing record. A second call with the same `ctx.runId` overwrites the map entry with a fresh `status:"ADMITTED"`, defeating the `DISPATCHED` guard at `:286` and permitting a second supervisor + runner against the same `taskRoot` — two processes writing the same `execution-supervisor-state.json`, `MANAGED_OUTCOME.json`, and `RESULT.json`, plus duplicate notifications. The `wx` flags at `:132-140` also mean a reused `runId` silently re-runs the **old** `TASK_PACKET.md`.

### M3 — Stale contract artifacts are not cleared at run start
`execution-supervisor.py:131` unlinks only `terminal_evidence`. `managed-agent-runner.mjs:91-92` then loads a pre-existing `MANAGED_OUTCOME.json` and `.locked-plan.json` from disk. `sliceToken` (`:130`) neutralizes a stale outcome, but a stale **locked plan** is adopted verbatim and `:132` (`!baseline && slice === 1`) prevents re-locking — so a reused directory binds a new objective to an old plan. Reachable via M2.

---

## LOW

- **L1** — `managed-agent-runner.mjs:132` locks the plan only at `slice === 1`; `:136` then rejects every later slice when `baseline` is null. An invalid slice-1 output dooms the entire run to `FAILED` even if slices 2–12 would have succeeded. Fails closed (correct), but burns the full budget.
- **L2** — `managed-agent-runner.mjs:122` passes `args.thinking` through unvalidated (it is not in the required-args list at `:79`). The plugin schema forbids `low` (`index.js:21-23`, `openclaw.plugin.json:20`), so the live path is safe, but the runner enforces no floor of its own. Separately, `adaptive` is the one configurable value that can resolve below `medium` for a slice the runtime misjudges as simple.
- **L3** — `index.js:213-215`: the `admission.status === "DISPATCHED"` ternary branch is unreachable; `:212` already returned for that case.
- **L4** — `index.js:230-236`: if `sendText` succeeds but the `ack` spawn fails, `notificationDelivered` stays false and the next 5 s tick re-sends. Exactly-once then depends entirely on the adapter honoring `deliveryQueueId`.

---

## Requirement-by-requirement

| Requirement | Status |
|---|---|
| Exit code 0 alone cannot prove completion | ✅ on the plugin path; ⚠️ M1 default |
| Objective decomposed into durable packages/gates | ✅ (`:132-134`, `.locked-plan.json`) |
| Partial work continues in bounded slices | ✅ (`:99-166`) |
| SUCCEEDED requires all PASSED with evidence | ⚠️ structurally yes, semantically vacuous (H1) |
| BLOCKED requires evidenced external dependency | ⚠️ self-asserted (H2) |
| Internal defects/tests/size cannot be BLOCKED | ❌ (H2) |
| Terminal state reconciled and delivered once | ✅ (flock `:117-126`, outbox dedupe `:100-108`); ⚠️ L4 |
| Complex slices do not inherit low thinking | ✅ (`index.js:21-23`, runner `:122` default `high`, review `:153` hardcoded `high`) |

---

## FAIL

C1 alone is disqualifying: the managed agent can read its own supervisor state file, obtain the terminal nonce and the result path, and forge a `SUCCEEDED` envelope that bypasses the package/gate contract, evidence verification, and independent review in their entirety — process-success/objective-failure divergence, unchanged. C2 is a second independent leak of the same secret, and the same-user process boundary means nonce-based binding cannot carry this weight on its own.

H1 and H2 are the follow-on: with the nonce sealed, the structural gates still reduce to agent-authored assertions checked by an agent-chosen oracle, leaving one LLM reviewer as the sole substantive control.

Minimum to re-review: move the nonce out of agent-reachable state (kernel-level separation — separate uid, or an fd/pipe handshake the agent cannot open), pass `childEnv` at `managed-agent-runner.mjs:70`, and constrain gate commands to a supervisor-defined set rather than agent-supplied `argv`/`expectedExit`.

I did not edit any files.
