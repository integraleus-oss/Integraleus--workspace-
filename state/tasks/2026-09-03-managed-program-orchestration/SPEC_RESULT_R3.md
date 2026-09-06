I could not execute anything this session (Bash `node -e` was denied), so every finding below is from direct reads; I flag the two places where that limits me. Line references are to the current working-tree files.

---

# Specification review — managed program orchestration vs. the ZSR failure mode

## Verified fixed since the R2 round

Confirmed by reading: status case-normalization in `managed-agent-runner.mjs:50-51` (R2-SPEC-H2), sha256 binding + gate command execution in `:56-57,61-62` (R2-SPEC-H3), `--require-validated-terminal` now pushed by `execution_supervisor_start` (`index.js:317`, R2-SPEC-H1), supervisor pre-unlink of stale terminal evidence (`execution-supervisor.py:117-118`, R2-SPEC-M3/L2), FAILED **gates** rejected under BLOCKED (`managed-outcome-contract.mjs:51`, R2-SPEC-M1), and thinking level asserted end to end (`index.test.mjs:21`).

---

# HIGH

### H1 — Terminal evidence is a self-declared flag in a file the supervised agent can write, and the supervisor acts on it mid-run
`execution-supervisor.py:57-63`, `:138`, `:144-148`; `index.js:166`; `managed-agent-runner.mjs:117,123`

`terminal_from_evidence` treats `contractValidated is True` (`:61`) as proof — a plain boolean, with no run id, nonce, signature, or writer authentication. `RESULT.json` lives in the task root (`index.js:124,166`), the same directory the managed slice works in; the managed session gets no admission (`index.js:112`) so `before_tool_call` never blocks its tools. The supervisor polls that file every 0.25 s **while the child is alive** (`:138`), and on any terminal value kills the process group and finalizes (`:144-148`).

So a slice that writes `{"terminalStatus":"SUCCEEDED","contractValidated":true}` to `RESULT.json` terminates the objective as SUCCEEDED, notifies the owner, and drives the TaskFlow to `succeeded` (`index.js:246`) — with zero packages, gates, or evidence ever evaluated. This is not hypothetical: **both** tests do exactly this and assert SUCCEEDED (`index.test.mjs:22` in the fake runner, `:65` in the integration command, asserted `:75`). Nor is it adversarial-only — `RESULT.json` is the established name for "the file the managed run produces" in this repo (twelve prior `state/tasks/managed-admission/*/EVIDENCE.md:9` say `Expected output: …/RESULT.json`), and the slice is instructed to atomically write a JSON result file into that very directory (`managed-agent-runner.mjs:94`). Exit code 0 has been replaced by a one-line JSON file the same untrusted process can author.

### H2 — `execution_supervisor_start` runs an arbitrary command and accepts its self-declared terminal file; the contract never applies
`index.js:292-325` (esp. `:299` arbitrary `command`, `:313-318`)

R2-H1 was closed by adding `--require-validated-terminal` at `:317`, but that flag only checks the boolean of H1. This tool creates a managed TaskFlow, runs any argv, and reports SUCCEEDED when that argv writes `contractValidated:true` — no runner, no packages, no gates, no continuation. It is contract-declared (`openclaw.plugin.json:9`), callable by any trusted-owner session (`index.js:302,48-53`), and `before_tool_call` (`:209-215`) only guards turns that already have a pending admission — i.e. it is freely callable in exactly the turns the regex gate did not admit. `index.test.mjs:63-66` is a working demonstration of process-success with an unproven objective.

### H3 — `validateManagedOutcome` throws on a SUCCEEDED outcome whose gate has no `evidence`, killing the run instead of rejecting it
`managed-outcome-contract.mjs:41`; `managed-agent-runner.mjs:108`

```js
value.gates.some(x => !x.evidence.some(e => e.kind === "command"))
```
This is unguarded (contrast `:27,:33`, which use `Array.isArray`) and runs over **every** gate whenever `status === "SUCCEEDED"`, including gates legitimately carrying no evidence. A gate `{"id":"G2","title":"…","status":"PENDING"}` yields `TypeError: Cannot read properties of undefined (reading 'some')`. `managed-agent-runner.mjs:108` calls the validator at module top level with no `try`, so the rejection is unhandled: node exits non-zero, `RESULT.json` is never written (it was unlinked at `:83`), the attempt is never appended to `agent-output.json` (`:114-115` are past the throw), and the supervisor finalizes FAILED (`execution-supervisor.py:140-141`) with no forensics and no continuation.

The trigger is the single most likely overclaim in this system — "SUCCEEDED while one gate is still PENDING" — which is precisely the input the validator exists to reject and the loop exists to continue from. Introduced by the R2 fix for gate-command evidence.

### H4 — `evidenceErrors` still crashes on malformed model output (R2-STANDARDS-H3, unfixed)
`managed-agent-runner.mjs:50`, `:54`

Two live triggers: `"packages":[null]` → `String(item.status)` on `null` at `:50`; and a PASSED item with `"evidence":[{"kind":"file","sha256":"…"}]` → `isAbsolute(item.path)` at `:54`, which sits **outside** the `try` that begins at `:55`. `validateManagedOutcome` tolerates both (`item?.id`, `:25-27`) and correctly returns "invalid — continue", but the runner dies before that verdict is used, because `:112` awaits `evidenceErrors` in the same expression. Same consequence as H3: a recoverable slice becomes a terminal FAILED with no record.

### H5 — One non-zero slice exit terminates the whole objective; the 600 s slice cap makes that likely
`managed-agent-runner.mjs:104`, `:116-119`

`sliceSeconds` is hard-capped at 600 s regardless of the 3600 s budget, then any non-zero child exit is terminal `CRASHED` with `break` — discarding remaining slices and time. The originating incident recorded in `EVIDENCE.md:8` ran **458 405 ms**, within 1.3× of that cap. A slice that overruns hits `openclaw agent --timeout` and will almost certainly exit non-zero, so the normal-operation case ("this slice ran long") is indistinguishable from "the binary is broken." This directly defeats the required behavior *partial work automatically continues in bounded slices*.

---

# MEDIUM

### M1 — SUCCEEDED still rests on a self-authored plan verified by self-authored evidence
`managed-agent-runner.mjs:109-111`, `:36-45`, `:56-57`, `:61-62`; `managed-outcome-contract.mjs:41`

The baseline plan is captured from the first structurally non-empty outcome, valid or not (`:109`), and `planErrors` only blocks removal and renaming — nothing requires more than one package/gate, and nothing ties either to the owner objective. File evidence proves "a file exists whose bytes hash to the value you claimed"; the agent can write that file. Gate evidence proves "a command you chose exited with the code you predicted" — `/usr/bin/true` satisfies `contract:41`, and the runner's own passing scenario uses `["/usr/bin/test","-s", TASK_PACKET.md]` against the task packet (`managed-agent-runner.test.mjs:20,52`). The mechanism is meaningfully stronger than exit 0, but `README.md:35-38` and the acceptance list overstate it: SUCCEEDED currently means "the agent kept the promises it made in slice 1 and named files that exist."

### M2 — The slice-1 plan lock is bypassable in slice 2 with no intervening work
`managed-agent-runner.mjs:113`, `:109-111`

The `CONTINUE` requirement is checked only for `slice === 1`, while the baseline is captured from slice 1 regardless of validity. An outcome rejected as "slice 1 must establish the locked plan" can be resubmitted byte-identical in slice 2 and is accepted. `managed-agent-runner.test.mjs:58` depends on this: the fake CLI returns the same `passed()` every time, so the "success" scenario is rejection-then-identical-resubmission.

### M3 — BLOCKED externality is unverifiable, and relabeling escapes the internal-defect rule
`managed-outcome-contract.mjs:44-52`

`external: true` is a self-asserted boolean; `reason`/`ownerAction` are free text; `evidence` is a file the agent wrote (M1). The FAILED-package/gate checks (`:50-51`) are defeated by marking the failing item `BLOCKED` instead of `FAILED`. So *internal defects, failed tests, task size, and remaining work cannot be used as BLOCKED* is enforced only against honest labeling — and BLOCKED is a fully terminal, owner-notified state (`:44`, `execution-supervisor.py:18`, `index.js:247`).

### M4 — `recover` prefers PID liveness over terminal evidence; a recycled PID pins a run at RUNNING forever
`execution-supervisor.py:168-174`; `index.js:262-270`

`pid_alive` has no identity check (start time, cmdline, supervisor-owned lock). After a reboot or PID wrap, `state["pid"]` matching an unrelated process makes the run permanently RUNNING; the 5 s recovery scan re-polls it forever, `terminal_from_evidence` at `:171` is never consulted, and no owner notification is ever emitted. Unchanged from R2.

### M5 — Delivery is at-least-once at the plugin layer
`index.js:229-236`

`adapter.sendText` succeeds, then `ack` is spawned as a separate process. A failure or Gateway death in that window leaves `notificationDelivered` false and the next 5 s tick (`:270`) re-sends. The supervisor's outbox ledger is genuinely exactly-once (`execution-supervisor.py:87-105`); the send is not — idempotence rests entirely on the adapter honoring `deliveryQueueId` (`:232`). *Delivered once* is not established end to end.

### M6 — Evidence paths resolve against the runner's inherited cwd, with no workspace containment
`managed-agent-runner.mjs:54`

`resolve(process.cwd(), item.path)` — the runner is spawned by a detached supervisor spawned by the Gateway (`index.js:173`), so cwd is unspecified and nothing in the contract instruction (`:89-101`) tells the agent what relative paths resolve against. Absolute paths get no containment check: `/etc/hostname` plus its correct sha256 is valid evidence.

### M7 — Degenerate tail slices convert budget exhaustion into CRASHED
`managed-agent-runner.mjs:86-87` vs `:104`

The loop breaks only at `remainingSeconds <= 1`, but `sliceSeconds` is floored at 2, so once remaining drops below 12 the 10 s reserve is violated and the runner keeps launching 2 s agent turns that cannot do work — each consuming a slice and each likely exiting non-zero, so H5 fires and the result is CRASHED rather than the intended `FAILED` at `:131-136`. With the schema-minimum `managedAgentTimeoutSeconds: 60` (`index.js:20`) the runner gets 30 s and enters this regime on slice 2.

### M8 — The instructed BLOCKED shape can never validate
`managed-agent-runner.mjs:99` vs `managed-outcome-contract.mjs:9-15,46-48`

The prompt tells the agent `blocker` is `{"external":true,…,"evidence":["..."],…}` — an array of **strings**. `validEvidence` requires objects with `kind`, so every literal-compliant BLOCKED is rejected (and the strings are silently skipped by `evidenceErrors:53,59`, so they are never even checked). A genuine external blocker reported in the documented form loops until budget exhaustion → FAILED.

---

# LOW

- **L1** `managed-agent-runner.mjs:117` — the CRASHED record is written with `contractValidated: true` when nothing was validated. It matters because `execution-supervisor.py:61` treats that field as the gate: every runner-written result is "validated" by construction.
- **L2** `index.js:308,317` — an empty-string `terminalEvidencePath` yields `argv.push("--terminal-evidence", null)` → spawn `TypeError`. The schema requires the field but not `minLength`.
- **L3** `managed-outcome-contract.mjs:24-34` / `managed-agent-runner.mjs:40` — duplicate package/gate ids are not rejected and `planErrors` uses `.find`, so `P1` twice satisfies the lock via either copy.
- **L4** `managed-agent-runner.mjs:15-19` — `atomicJson` renames without `fsync` (the Python side fsyncs at `execution-supervisor.py:36`); a kill between write and rename leaks an unattributable `.<uuid>.tmp` in the task directory.
- **L5** `managed-outcome-contract.mjs` — `schemaVersion` is emitted in the instructed shape (`runner:95`) but never validated; no version handle for a future contract change.
- **L6** `index.js:22` / `openclaw.plugin.json:21` — `adaptive` can resolve below `high` for a complex slice. Separately, I could **not** verify that `openclaw agent --thinking` exists (`runner:106`); if the flag is unsupported the CLI exits non-zero and H5 turns every slice into CRASHED. Worth confirming before activation.
- **L7** `managed-agent-runner.test.mjs:46` — runner path hardcoded to `/home/stanislav/…`; `new URL("./managed-agent-runner.mjs", import.meta.url)` is the portable form.
- **L8** `EVIDENCE.md:19-26` asserts all three suites PASS. Bash was denied here, so those claims are unverified by me. No test covers: an agent-written `RESULT.json` (H1), a bare-exit-0 `execution_supervisor_start` without contract (H2 — `index.test.mjs:63-66` asserts the opposite as correct), the H3/H4 crash inputs, the deadline/tail path (M7), or a rejected-evidence path (every scenario substitutes a real file).

---

## Requirement-by-requirement

| Required behavior | Status |
|---|---|
| Exit code 0 alone cannot prove completion | **Not met** — replaced by an unauthenticated self-declared file (H1) and an arbitrary-command tool (H2) |
| Objective decomposed into durable packages and gates | Met structurally; plan is self-authored with no floor or objective linkage (M1, M2) |
| Partial work continues in bounded slices | **Not met** — H3/H4 crash the loop, H5 aborts it on any non-zero slice exit, M7 burns the tail |
| SUCCEEDED requires all packages/gates PASSED with evidence | Met in the contract; evidence is self-produced and gate commands are agent-chosen (M1) |
| BLOCKED requires evidenced external dependency + owner action | Structurally enforced, semantically unverifiable (M3); documented shape is invalid (M8) |
| Internal defects/tests/size/remaining work cannot be BLOCKED | **Not met** — defeated by relabeling FAILED → BLOCKED (M3) |
| Terminal state reconciled via supervisor/TaskFlow, delivered once | Reconciliation met; delivery is at-least-once (M5); M4 can strand a run permanently |
| Complex managed slices do not inherit low thinking | Met — `low` excluded from both schemas, `high` default at `index.js:172` and `runner:106`, asserted at `index.test.mjs:21`; caveats L6 |

---

## Verdict

**FAIL.**

Two paths reproduce process-success/objective-failure divergence outright. H1 is the original ZSR defect one layer up: the supervisor's proof of completion is a boolean in a file the supervised agent can write, accepted mid-run, with no run identity — and the project's own two tests fabricate exactly that file to assert SUCCEEDED. H2 leaves a registered tool that reports SUCCEEDED for an arbitrary command with no contract at all. H3, H4 and H5 then break the continuation guarantee in the opposite direction: the most likely overclaim, malformed model output, and an over-long slice each end the objective terminally instead of rejecting and continuing.

The minimum to re-review: bind `RESULT.json` to the run (nonce/run-id written by the supervisor before `Popen` and required on read) and treat it as untrusted otherwise; make `execution_supervisor_start` either route through the contract or stop reporting SUCCEEDED; guard `contract:41` and `runner:50,54` against absent/non-string fields inside the rejection path; and decide slice-timeout retry semantics before H5 meets a real 600 s slice.
