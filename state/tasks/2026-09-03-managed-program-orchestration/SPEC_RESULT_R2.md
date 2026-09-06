Bash was denied in this session, so I verified the validator edge cases by reading the code paths rather than executing probes. All line references below are from direct reads of the files.

## Findings

### HIGH

**H1 — `execution_supervisor_start` never passes `--require-validated-terminal`; exit code 0 still becomes `SUCCEEDED`.**
`projects/execution-supervisor-taskflow/index.js:313-318` builds the supervisor argv for the v1 tool without the strict flag (compare the managed path at `index.js:169`, which does pass it). In `scripts/execution-supervisor.py:137-141`, when `require_validated_terminal` is false the supervisor falls back to `observed or ("SUCCEEDED" if code == 0 else "CRASHED")`. `terminalEvidencePath` is optional in that tool's schema (`index.js:298`), and even when supplied the strict check is never armed.

This is not theoretical — the project's own integration test demonstrates it: `index.test.mjs:63-73` runs `["python3","-c","pass"]`, produces no evidence at all, and asserts `terminal.status === "SUCCEEDED"`, with the flow then driven to `succeeded` (`index.test.mjs:91`). The tool is registered and contract-declared (`openclaw.plugin.json` `contracts.tools`), reachable by any trusted-owner session, and `before_tool_call` (`index.js:209-215`) only blocks it while an admission is pending — i.e. it is freely callable in exactly the turns the regex gate did not admit. The ZSR failure mode is fully reachable through this path.

**H2 — Case-normalization mismatch lets an outcome skip filesystem evidence verification entirely.**
`managed-outcome-contract.mjs` normalizes case everywhere (`:12`, `:18-19`, `:24-25`, `:27-28`), so `"status":"passed"` / `"succeeded"` validates as PASSED/SUCCEEDED. But `managed-agent-runner.mjs:49` filters with a raw strict comparison, `item.status === "PASSED"`, and `:50` with `outcome?.status === "BLOCKED"`. A lowercase-cased outcome therefore yields an empty `items` list, `evidenceErrors()` returns `[]`, `validationErrors` is empty, and `terminalStatus()` returns `SUCCEEDED` (`:111-116`) — with the evidence array containing arbitrary prose strings that were never resolved to files. The slice-1 guard at `:103` is also raw-compared, so this is reachable from slice 2 onward. Process success, objective unverified.

**H3 — Evidence verification is existence + non-zero size only, so any pre-existing file satisfies a gate.**
`managed-agent-runner.mjs:51-55` only `stat()`s the path and checks `isFile() && size !== 0`. The instruction that evidence "independently contain the claimed check/result" (`:87`) is never enforced. The runner's own test bakes this in: `managed-agent-runner.test.mjs:49` substitutes `__EVIDENCE__` with the **task packet file itself**, and that is the passing `SUCCEEDED` scenario (`:55`). An agent can point every package and gate at `TASK_PACKET.md`, `CONTEXT.json`, or any file it just wrote, and reach `SUCCEEDED`. "PASSED with evidence" is currently "PASSED with a filename".

### MEDIUM

**M1 — `BLOCKED` accepts FAILED acceptance gates: failed tests are laundered into an external blocker.**
`managed-outcome-contract.mjs:41` rejects FAILED *packages* under BLOCKED, but the equivalent check for *gates* does not exist. `FAILED` is a legal gate state (`:2`) and carries no evidence requirement (`:25`). An outcome with `gates:[{status:"FAILED"}]`, one BLOCKED package, and a plausible external blocker validates. The spec requirement "failed tests … cannot be used as BLOCKED" is not enforced on the gate axis.

**M2 — `external: true` is pure self-attestation.**
`managed-outcome-contract.mjs:37-39` requires the boolean flag, a reason string, non-empty evidence, and an owner action — none of which distinguish an external dependency from an internal defect. Combined with H3 (evidence = any file) and M1, `BLOCKED` (supervisor exit 4, terminal, notification delivered) is reachable at the agent's discretion. Nothing checks that non-blocked packages made progress either — `PENDING` siblings are accepted (`:40` only requires *some* package BLOCKED).

**M3 — Terminal evidence has no run identity, and the supervisor reads it before the runner clears it.**
`execution-supervisor.py:129-136` polls `terminal_from_evidence` on the *first* loop iteration, milliseconds after `Popen`, with no pre-sleep; the runner only unlinks the result file at `managed-agent-runner.mjs:73`, after Node startup, ESM imports and `readFile(prompt)`. Because `taskRoot` is deterministic in `runId` (`index.js:113-114`) and the seed files are written `wx` (preserved), a re-dispatch over an existing task root will deterministically read the *previous* run's `RESULT.json`, kill the fresh runner (`:142-146`) and finalize with the stale status. `RESULT.json` carries no `runId`/nonce for the supervisor to check, and it sits in a directory the managed agent can write. Freshness should be owned by the supervisor (or the file bound to the run id), not by the child it supervises.

**M4 — The locked plan is captured from the agent's own slice-1 output, including a rejected one, with no floor.**
`managed-agent-runner.mjs:99-101` sets `baseline` from the first outcome that merely has non-empty arrays — before `validationErrors` is computed at `:102`, so a plan from an otherwise-rejected slice becomes the lock. `planErrors` (`:35-44`) only prevents removal and renaming. Nothing ties packages/gates back to the owner objective, and nothing requires more than one of each. A single package "P1: do the task" plus "G1: it works" is a valid decomposition that satisfies "every package and gate PASSED" — objective narrowing survives the whole mechanism.

**M5 — Relative evidence paths resolve against the runner's cwd.**
`managed-agent-runner.mjs:52` uses `resolve(process.cwd(), item)`. The runner is spawned by a detached supervisor which was itself spawned by the Gateway (`index.js:173`), so cwd is the Gateway's, not `workspaceRoot`. Repo-relative evidence paths will spuriously fail, burning slices until the budget-exhaustion `FAILED` at `:121-126`. Fail-safe in direction, but it makes honest completion unreachable in the live configuration.

**M6 — The entire protection is gated on three prompt regexes.**
`index.js:10-14`, `32-34`, `184`. Any objective not phrased as "сообщи по завершении" / "notify me when done" bypasses admission, the runner, the contract, and the strict supervisor flag — and lands on the unhardened path of H1. The fix is opt-in by phrasing, not by task size or duration.

**M7 — Delivery is at-least-once, not exactly-once, at the plugin layer.**
`index.js:229-235`: `adapter.sendText` succeeds, then `ack` is spawned as a separate process. If the ack fails or the Gateway dies between the two, `notificationDelivered` stays false and the next 5 s tick (`:270`) re-sends. Idempotence rests entirely on the adapter honoring `deliveryQueueId` (`:232`). The supervisor's outbox ledger is exactly-once (`execution-supervisor.py:87-105`); the send is not.

### LOW

**L1 —** Concurrent finalization: the recovery service polls every state file every 5 s (`index.js:261-270`) and `recover` finalizes when the child pid is dead (`execution-supervisor.py:166-172`), which can race the still-sleeping supervisor's own `finalize`. Both hold independent in-memory copies, so the `TERMINAL` guard at `:109` does not serialize them; `notify_once`'s read-then-append (`:94-102`) is not atomic and can duplicate outbox lines.

**L2 —** One non-zero child exit terminates the objective as `CRASHED` with no retry (`managed-agent-runner.mjs:106-110`); a transient CLI failure on slice 9 discards eight slices of work. Safe direction, but it converts recoverable faults into terminal ones.

**L3 —** `TASK_PACKET.md:26-33` pre-checks every acceptance box, including "Partial work cannot produce SUCCEEDED" and "Exit code 0 alone cannot produce SUCCEEDED", while `:34` (independent review) is open. H1–H3 contradict those checked boxes; the packet asserts the property the review was meant to establish.

## What the implementation does get right

`--require-validated-terminal` on the managed path (`index.js:169`) plus `execution-supervisor.py:138-139` genuinely closes exit-0-implies-success **for managed-runner dispatches** — `test_execution_supervisor.py:31-32` covers it. `PARTIAL_BLOCKED` and self-declared `FAILED` are correctly not terminal (`managed-outcome-contract.mjs:3`, verified by `managed-agent-runner.test.mjs:59`). Continuation is real and bounded (`managed-agent-runner.mjs:75-77`, `:121-126`). Thinking level is sound: the config schema excludes `low` (`index.js:21-23`), the plugin always passes it explicitly (`:172`), the runner defaults to `high` (`:96`), and the fake runner asserts it (`index.test.mjs:21`). `BLOCKED` survives as a distinct terminal state end to end (`execution-supervisor.py:18-22`, `index.js:244-247`).

## Verdict

**FAIL.**

Three paths still produce process-success with an unproven objective: a registered tool that reports `SUCCEEDED` on bare exit 0 (H1, demonstrated by the project's own test), a case-sensitivity gap that skips evidence verification wholesale (H2), and an evidence check that any existing file satisfies (H3). H1 alone reproduces the original ZSR divergence. The strict path is correct where it is armed; it is not armed everywhere, and the evidence layer beneath it does not yet distinguish a claim from a proof.
