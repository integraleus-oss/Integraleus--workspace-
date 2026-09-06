I reviewed the current working-tree implementation against the eight required behaviors. Note upfront: **I could not execute anything** — `node -e`, the test suites, and `openclaw agent --help` were all denied by the sandbox — so every finding below is from direct reads, and I flag the two places where that limits me (L6, L8).

---

# Specification review R4 — managed program orchestration vs. the ZSR failure mode

## Verified fixed since R3

- **R3-H3** closed: `managed-outcome-contract.mjs:41` now guards with `Array.isArray(x.evidence)`, and `managed-agent-runner.test.mjs:29` covers the "SUCCEEDED with a PENDING evidence-less gate" input.
- **R3-M8** closed: the instructed `blocker` shape (`managed-agent-runner.mjs:100`) now says evidence uses the same file/command objects, so a literal-compliant BLOCKED can validate.
- Stale terminal-evidence unlink is now unconditional (`execution-supervisor.py:122`), covered by `test_execution_supervisor.py:36-38`.
- Thinking level: `low` is excluded from both schemas (`index.js:21-23`, `openclaw.plugin.json:21`), `high` is passed explicitly (`index.js:171`), the runner defaults to `high` (`managed-agent-runner.mjs:107`), and the fake runner asserts it (`index.test.mjs:21`).

---

# HIGH

### H1 — Terminal proof is still a self-declared boolean in a file the supervised agent can write
`scripts/execution-supervisor.py:57-63`, `:144-149`, `:150-154`; `projects/execution-supervisor-taskflow/index.js:124,165-171`; `README.md:42-47`

`terminal_from_evidence` accepts `contractValidated is True` (`:61`) as proof of completion — a plain boolean with no run id, nonce, or writer authentication — then reads `terminalStatus`/`status`/`outcome` (`:62`) against a permissive map (`:19-23`, where `SUCCESS` and `ACCEPTED` also mean SUCCEEDED). `RESULT.json` sits in the task root (`index.js:124`), the directory the managed slice works in; that slice gets no admission (`index.js:111`), so `before_tool_call` (`:208-214`) never blocks its tools, and `admission.json` (`index.js:139`) publishes `resultPath` to it. The supervisor polls that file every 0.25 s **while the child is alive** (`:144`) and on any terminal value kills the process group and finalizes (`:150-154`).

A slice that writes `{"terminalStatus":"SUCCEEDED","contractValidated":true}` therefore ends the objective as SUCCEEDED, notifies the owner, and drives the TaskFlow to `succeeded` (`index.js:245`) with zero packages, gates, or evidence evaluated. This is not adversarial-only: both suites do exactly this and assert it as correct (`index.test.mjs:19-23`, `:63-66`, asserted `:75`), and `README.md:44-45` documents it as the contract ("must atomically write a JSON terminal envelope containing `contractValidated: true`"). Exit code 0 has been replaced by a one-line JSON file the same untrusted process authors. **Requirement 1 is not met at the layer that persists terminal state.**

### H2 — `execution_supervisor_start` supervises an arbitrary command and accepts its self-declared envelope; the package/gate contract never applies
`index.js:294-327` (esp. `:301` arbitrary `command`, `:315-320`)

The tool creates a managed TaskFlow, runs any argv, and reports SUCCEEDED on the H1 envelope — no runner, no packages, no gates, no continuation. `safePath` (`:54-59`) constrains only the three path arguments, not `command`. It is contract-declared (`openclaw.plugin.json:9`) and freely callable in exactly the turns the regex gate did not admit, because `before_tool_call` (`:210`) only guards turns that already carry a pending admission. `index.test.mjs:63-66,75` is a working demonstration of process-success with an unproven objective.

### H3 — Malformed model output still crashes the runner instead of being rejected and continued
`managed-agent-runner.mjs:51`, `:55`, `:113`; `managed-outcome-contract.mjs:41`

Three unguarded dereferences on inputs the validator is explicitly built to tolerate-and-reject (`contract:25-27` use `item?.`):

- `contract:41` — `value.gates.some(x => !Array.isArray(x.evidence) …)`: a null element in `gates` throws. The `Array.isArray` fix guarded the property, not the object.
- `runner:51` — `.filter(item => String(item.status)…)`: `"packages":[null]` throws.
- `runner:55` — `isAbsolute(item.path)` with a missing/non-string `path` throws, and it sits **outside** the `try` that opens at `:56`.

`runner:109` and `:113` call the validator and `evidenceErrors` at module top level with no `try`. The rejection is unhandled: node exits non-zero, `RESULT.json` is never written (unlinked at `:84`), the attempt is never appended to `agent-output.json` (`:115-116` are past the throw), and the supervisor finalizes FAILED (`execution-supervisor.py:146-147`) with no forensics and no continuation. A recoverable slice becomes a terminal failure.

### H4 — One non-zero slice exit terminates the whole objective, and the 600 s slice cap makes that the normal case
`managed-agent-runner.mjs:105`, `:117-121`; `index.js:20`, `:171`

`sliceSeconds` is hard-capped at 600 s regardless of the up-to-3600 s budget (`:105`), then **any** non-zero child exit is terminal `CRASHED` with `break` (`:117-121`), discarding every remaining slice and second of budget. A slice that overruns hits `openclaw agent --timeout` and will almost certainly exit non-zero, so "this slice ran long" is indistinguishable from "the binary is broken." The originating incident ran 458 405 ms (`EVIDENCE.md:8`) — within 1.3× the cap. `managed-agent-runner.test.mjs:67` asserts this abort as correct. **Requirement 3 is not met.**

### H5 — One slice that omits `MANAGED_OUTCOME.json` poisons the run unrecoverably; the plan lock is not durable
`managed-agent-runner.mjs:89`, `:110-112`, `:129`, `:37-45`

The outcome file is deleted at the start of every slice (`:89`). If a slice exits 0 without rewriting it, `loadJson` returns null and `previous` collapses to a placeholder (`:129`), dropping every package and gate from the next slice's prompt — while the in-memory `baseline` (`:110-112`) still forbids removal and renaming. `planErrors` (`:43-44`) reports the missing **ids** but never the locked **titles**, so the agent cannot reconstruct a plan that validates: every subsequent slice is rejected until budget exhaustion → FAILED (`:132-136`).

Separately, this is where **requirement 2 fails on "durable"**: the plan lock lives only in a runner-process variable, and the only on-disk copy of the decomposition is deleted at each slice boundary. Nothing survives the runner process, so a supervisor-level recovery cannot resume a decomposed objective — `recover` (`execution-supervisor.py:171-182`) only finalizes; it never relaunches.

---

# MEDIUM

### M1 — SUCCEEDED still rests on a self-authored plan verified by self-authored evidence
`managed-outcome-contract.mjs:27,33,41`; `managed-agent-runner.mjs:56-58`, `:61-63`

File evidence proves "a file exists whose bytes hash to the value you claimed" — the agent writes the file. Gate evidence proves "a command you chose exited with the code you predicted" — `/bin/true` satisfies `contract:41`'s "independently executed command for every gate," and the suite's own passing scenario uses `["/usr/bin/test","-s",TASK_PACKET.md]` against the task packet (`managed-agent-runner.test.mjs:20`), which passes before any work happens. Nothing requires more than one package/gate, and nothing ties either to the owner objective in `TASK_PACKET.md`. The mechanism is meaningfully stronger than exit 0, but `README.md:35-38` and `EVIDENCE.md:34-35` overstate it: SUCCEEDED means "the agent kept the promises it made in slice 1."

### M2 — The slice-1 plan lock is bypassable in slice 2 with no intervening work
`managed-agent-runner.mjs:110-112`, `:114`

The CONTINUE requirement is checked only for `slice === 1`, while the baseline is captured from slice 1 regardless of validity. An outcome rejected as "slice 1 must establish the locked plan" can be resubmitted byte-identical in slice 2 and is accepted. `managed-agent-runner.test.mjs:59` depends on this — the fake CLI returns the same `passed()` every call, so the suite's canonical success scenario *is* rejection-then-identical-resubmission. With M1, a complete SUCCEEDED is reachable in two slices with zero objective work.

### M3 — BLOCKED externality is unverifiable, and relabeling escapes the internal-defect rule
`managed-outcome-contract.mjs:44-52`

`external: true` is a self-asserted boolean; `reason`/`ownerAction` are free text; `evidence` is a file the agent wrote (M1). The FAILED-package and FAILED-gate bans (`:50-51`) are defeated by marking the failing item `BLOCKED` instead of `FAILED`. BLOCKED is fully terminal and owner-notified (`execution-supervisor.py:18`, `index.js:246`). **Requirement 6 is enforced only against honest labeling.**

### M4 — `exit 0 ⇒ SUCCEEDED` is still the supervisor default, and a test asserts it
`execution-supervisor.py:149`; `test_execution_supervisor.py:30`

Without `--require-validated-terminal` the supervisor falls back to `observed or ("SUCCEEDED" if code == 0 else "CRASHED")`. Both current plugin call sites pass the flag (`index.js:168`, `:319`), but the CLI is a documented manual/heartbeat entry point (`HEARTBEAT.md:26`) and `test_success` codifies the ZSR mapping as correct behavior. Strictness should be implied by `--terminal-evidence`, or default-on with an explicit opt-out.

### M5 — `recover` prefers PID liveness over terminal evidence; a recycled PID pins a run at RUNNING forever
`execution-supervisor.py:50-54`, `:176-182`; `index.js:262-269`

`pid_alive` has no identity check (start time, cmdline, owned lock). After a reboot or PID wrap, a `state["pid"]` matching an unrelated process makes the run permanently RUNNING: the recovery scan `continue`s every tick (`index.js:264-265`), `terminal_from_evidence` at `:179` is never consulted, and no owner notification is ever emitted. Unchanged since R2.

### M6 — Delivery is at-least-once at the plugin layer
`index.js:228-235`

`adapter.sendText` succeeds, then `ack` is spawned as a separate process (`:232`). A failure or Gateway death in that window leaves `notificationDelivered` false and the next 5 s tick (`:272`) re-sends; the outbox event's `delivery.status: "pending"` (`execution-supervisor.py:97`) is never updated, so the ledger cannot dedupe the send. The supervisor's outbox is genuinely exactly-once (`:92-110`); the send is not — idempotence rests entirely on the adapter honoring `deliveryQueueId`. **"Delivered once" is not established end to end.**

### M7 — The whole contract is regex-gated
`index.js:10-14`, `:32-34`, `:183`, `:197-198`

Managed admission fires only for prompts matching three patterns ("сообщи по завершении" / "notify me when done"). The identical objective phrased any other way gets no packages, no gates, no supervisor, and no continuation — the ordinary agent path, where exit-0-equivalent self-report is the only signal. The anti-ZSR guarantee holds for a phrasing, not for a class of work.

### M8 — Evidence paths are uncontained and evidence commands are unsandboxed
`managed-agent-runner.mjs:55`, `:62`

`resolve(process.cwd(), item.path)` — the runner is spawned by a detached supervisor spawned by the Gateway (`index.js:172`), so cwd is unspecified, and nothing in the contract instruction (`:90-102`) tells the agent what relative paths resolve against. Absolute paths get no workspace containment: `/etc/hostname` plus its correct sha256 is valid evidence. Separately, `:62` executes model-chosen `argv` in a model-chosen `cwd` with the runner's privileges — the validator itself is an arbitrary-execution sink.

### M9 — Degenerate tail slices convert budget exhaustion into CRASHED
`managed-agent-runner.mjs:87-88` vs `:105`

The loop breaks only at `remainingSeconds <= 1`, but `sliceSeconds` is floored at 2, so once remaining drops below 12 the 10 s reserve is violated and the runner keeps launching 2 s agent turns that cannot do work — each burning a slice and each likely exiting non-zero, so H4 fires and the terminal state is CRASHED rather than the intended FAILED at `:132-136`. With the schema minimum `managedAgentTimeoutSeconds: 60` (`index.js:20`) the runner gets 30 s and enters this regime on slice 2.

---

# LOW

- **L1** `managed-agent-runner.mjs:118` — the CRASHED record carries `contractValidated: true` when nothing was validated. Every runner-written result is "validated" by construction, which is the exact field `execution-supervisor.py:61` uses as its gate.
- **L2** `index.js:310,319` — an empty-string `terminalEvidencePath` yields `argv.push("--terminal-evidence", null)` → spawn `TypeError`. The schema (`:300`) requires the field but sets no `minLength`.
- **L3** `managed-outcome-contract.mjs:24-34` / `managed-agent-runner.mjs:41` — duplicate package/gate ids are not rejected, and `planErrors` uses `.find`, so `P1` declared twice satisfies the lock via either copy.
- **L4** `managed-agent-runner.mjs:15-19` — `atomicJson` renames without `fsync` (the Python side fsyncs at `execution-supervisor.py:36`) and leaks an unattributable `.<uuid>.tmp` in the task directory if `rename` throws.
- **L5** `managed-outcome-contract.mjs` — `schemaVersion` is emitted in the instructed shape (`runner:96`) but never validated; no version handle for a future contract change.
- **L6** `index.js:21-23` / `openclaw.plugin.json:21` — `adaptive` remains an allowed override and can resolve below `high` for a complex slice; `runner:107` accepts any `--thinking` string unvalidated. Separately I could **not** verify that `openclaw agent --thinking/--json` exist (bash denied); if either flag is unsupported the CLI exits non-zero and H4 turns *every* managed run into CRASHED. Confirm before activation.
- **L7** `index.js:24-25` vs `:48-52` — `authorizedSessionPrefixes` is declared in both schemas (default `["agent:main:telegram:"]`) but never read by `isTrustedOwnerContext`. `README.md:12-15` describes an allowlist model the code does not implement.
- **L8** `EVIDENCE.md:19-26` asserts all three suites PASS; I could not execute them. No test covers: an agent-written `RESULT.json` (H1), the H3 crash inputs, an outcome-file-omitting slice (H5), the deadline tail (M9), or any rejected-evidence path — every scenario substitutes a file that already exists (`managed-agent-runner.test.mjs:53`). `index.test.mjs:63-66,75` asserts H2 as correct behavior.
- **L9** `managed-agent-runner.mjs:58` — a PASSED evidence item missing `sha256` throws inside the `try` and is reported as "evidence file does not exist," which will send the agent to fix the wrong thing.

---

## Requirement-by-requirement

| Required behavior | Status |
|---|---|
| Exit code 0 alone cannot prove completion | **Not met** — replaced by an unauthenticated self-declared envelope (H1) and an arbitrary-command tool (H2); the permissive default survives at `execution-supervisor.py:149` (M4) |
| Objective decomposed into **durable** packages and gates | **Not met** — structure exists, but the plan lock is process-memory only and the outcome file is deleted each slice (H5); plan is self-authored with no floor or objective linkage (M1, M2) |
| Partial work continues in bounded slices | **Not met** — H3 crashes the loop, H4 aborts it on any non-zero slice exit, H5 poisons it permanently, M9 burns the tail |
| SUCCEEDED requires all packages/gates PASSED with evidence | Met in the contract; evidence is self-produced and gate commands are agent-chosen (M1), and reachable in two slices with no work (M2) |
| BLOCKED requires evidenced external dependency + owner action | Structurally enforced, semantically unverifiable (M3) |
| Internal defects/tests/size/remaining work cannot be BLOCKED | **Not met** — defeated by relabeling FAILED → BLOCKED (M3) |
| Terminal state reconciled via supervisor/TaskFlow, delivered once | Reconciliation met; delivery is at-least-once (M6); M5 can strand a run permanently |
| Complex managed slices do not inherit low thinking | **Met** — `low` excluded from both schemas, `high` default at `index.js:171` and `runner:107`, asserted at `index.test.mjs:21`; caveat L6 |

---

## Verdict

**FAIL.**

Two paths reproduce process-success/objective-failure divergence outright, and both are currently asserted as correct by the test suite. H1 is the original ZSR defect moved one layer up: the supervisor's proof of completion is a boolean in a file the supervised agent can write, accepted mid-run, with no run identity — and `README.md:42-47` documents that as the contract rather than as a gap. H2 leaves a registered tool that reports SUCCEEDED for an arbitrary command with no packages or gates at all.

Three more break the continuation guarantee in the opposite direction: H3 (malformed output), H4 (one long slice), and H5 (one missing outcome file) each end the objective terminally instead of rejecting and continuing — H5 additionally showing that the "durable" decomposition is not durable.

Minimum to re-review: bind `RESULT.json` to the run (supervisor writes a nonce before `Popen` and requires it on read) and treat the file as untrusted otherwise; make `execution_supervisor_start` either route through the contract or stop reporting SUCCEEDED; move validation and evidence checking inside a rejection path that cannot throw (`contract:41`, `runner:51,55`); persist the locked plan outside the runner process and stop deleting the outcome file before a replacement exists; and decide slice-timeout retry semantics before H4 meets a real 600 s slice.
