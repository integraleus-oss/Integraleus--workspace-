I inspected every file in `REVIEW_STANDARDS.md` plus `TASK_PACKET.md` and `EVIDENCE.md`, and cross-checked against the live admission records under `state/tasks/managed-admission/`. No files were edited.

## Verdict on the original trace

The exact ZSR trace is closed. A runner that exits 0 while reporting `PARTIAL_BLOCKED` now produces no validated envelope (`managed-outcome-contract.mjs:20` rejects the status), so `execution-supervisor.py:170-171` finalizes `FAILED`. The nonce binding (`execution-supervisor.py:149-161`, `managed-agent-runner.mjs:86-89`) and the post-exit-only read (`execution-supervisor.py:168-169`) are sound, and `test_execution_supervisor.py:32-44` covers forged/stale/exit-zero cases properly.

That is not the same as preventing the failure *mode*.

---

## HIGH

**H1 — "Evidence" proves file existence, not verification. `managed-agent-runner.mjs:58-67`, `managed-outcome-contract.mjs:9-13`**
`validEvidence` requires only `kind:"file"`, a non-empty path, and 64 hex chars. `evidenceErrors` checks the file exists, is non-empty, and its SHA-256 matches — but the hash is supplied by the same model that names the file. There is no requirement that the artifact was created during the run, lives under the task root, is unique per gate, or contains a machine-checkable result. Line 61 explicitly accepts any absolute path on the filesystem.

Failure scenario: slice 2 runs `printf ok > /tmp/g1.txt`, computes the hash, marks P1/G1 `PASSED` citing it. All of `managed-outcome-contract.mjs:26,32,44` pass. This is not hypothetical — the test suite does exactly this: `managed-agent-runner.test.mjs:41,61` uses the owner's own `TASK_PACKET.md` as the passing evidence artifact for both the package and the gate, and the suite goes green. `SUCCEEDED` is reachable with zero verification performed.

**H2 — The acceptance plan is self-authored and never bound to the objective. `managed-agent-runner.mjs:102,127-128`, `39-48`**
Slice 1 writes the plan; `baseline` freezes only `{id, title}` (line 128), and `planErrors` (39-48) checks only non-removal and non-rename. Nothing compares the plan to the owner objective, checks decomposition depth, or forbids adding packages later. A model that under-decomposes in slice 1 — one package "do the work", one gate "it works" — then legitimately completes that plan and emits a fully valid `SUCCEEDED`. The divergence simply moves one level up: process succeeds, plan succeeds, objective is unmet. The required behavior "a complete objective is decomposed into durable packages and acceptance gates" is durable and machine-checked, but not *complete* — completeness is asserted, not enforced.

**H3 — The entire invariant is opt-in by heuristic. `projects/execution-supervisor-taskflow/index.js:10-14,31-36,192-196`**
None of the above applies unless `requiresManagedExecution` fires. The English branch (line 13) requires `run|execute|complete` followed within 160 chars by `notify|tell me when|once done|complete`; lines 34-35 require Russian imperatives. "Implement the full migration plan and let me know when it's finished" matches nothing. Line 35's length fallback also requires a Russian imperative. On top of that, `before_dispatch:194-196` returns early for any sender outside `authorizedSenderIds` or failing `isTrustedOwnerContext`.

Failure scenario: a 5,000-word English objective from the owner over an untrusted-context channel runs as an ordinary agent turn, exits 0, and reports done. That is the original ZSR mode, fully intact, on a path that no test covers (`index.test.mjs:7-10` tests four short strings, all positive-framed).

**H4 — A failed first slice makes completion permanently unreachable. `managed-agent-runner.mjs:127` vs `131`**
`baseline` can only be locked under `slice === 1` (line 127). Line 131 adds a hard error for every `slice > 1` while `baseline` is null. If slice 1 exits non-zero (line 134-137 `continue`s, so the retry is *slice 2*) or writes anything invalid, `baseline` stays null forever and every later slice fails validation — including a perfect `CONTINUE` plan. The pushed message, "return a valid CONTINUE plan before terminal completion," is unsatisfiable by construction.

Failure scenario: one transient `openclaw agent` failure on the first invocation burns the full 3450 s / 12-slice budget and reports `FAILED` with the objective untouched. Fails safe on truth, but denies completion entirely. `managed-agent-runner.test.mjs:70,75` observe the `FAILED` exit and never test recovery after a bad slice 1.

---

## MEDIUM

**M1 — `BLOCKED` laundering via relabeling. `managed-outcome-contract.mjs:52-54`**
The rule "internal defects cannot be BLOCKED" is enforced only against the literal string `FAILED`. A model with a broken test marks that package `BLOCKED` (satisfying line 52), authors `blocker:{external:true, reason:"upstream API changed", evidence:[self-written file], ownerAction:"..."}` and passes. Nothing verifies externality; `managed-agent-runner.mjs:109` states the rule in prose to the model being constrained. The requirement "BLOCKED requires an evidenced external dependency" is enforced structurally, not substantively.

**M2 — Exit-code-0-as-success still ships in the CLI. `execution-supervisor.py:146-148,172-173,219`**
With `--allow-exit-code-terminal` and no `--terminal-evidence`, `requireValidatedTerminal` is False and line 173 maps exit 0 to `SUCCEEDED`. The plugin never does this, and the arbitrary-command tool was removed (`index.test.mjs:65` asserts it), but the mechanism remains reachable from any shell and is exercised by `test_execution_supervisor.py:24,31,72`. The stated invariant "exit code 0 alone cannot prove objective completion" holds for the plugin path only, by caller discipline.

**M3 — Duplicate admissions and duplicate deliveries per objective. `index.js:38-40,115,192-203`**
`before_dispatch` supplies no `runId`, so `admissionId(undefined)` generates a fresh UUID each call (line 39). Line 115's dedup compares `known.admissionId === id` against that new random id and always misses. Every repeat of the same message spawns another admission directory, supervisor, runner, and terminal notification. The 12 UUID-named directories under `state/tasks/managed-admission/` confirm this keying is already live. Per-run delivery is exactly-once; per-objective it is not.

**M4 — Send-then-ack is not atomic. `index.js:238-244`**
`adapter.sendText` completes, then `ack` is spawned separately. A crash or non-zero ack between them leaves `notificationDelivered=false`, and the 5 s tick (line 279) re-sends. `deliveryQueueId: state.notificationId` is passed, so dedup depends entirely on the outbound adapter honoring it — untested here (`index.test.mjs:129,133` only checks the happy path). The JSONL outbox ledger is exactly-once; the *delivery* is at-least-once.

**M5 — The independent reviewer is neither isolated nor injection-safe. `managed-agent-runner.mjs:143-153`**
The reviewer is `--agent main`, same model, on a session key derived from the work session, and its verdict is an unstructured LLM judgment — it is the only real barrier behind H1 and H2. Its prompt (line 145) directs it to read `args.outcome` and the evidence files, all authored by the slice it is reviewing. A `summary` or evidence file containing reviewer-directed text is a direct injection path to `verdict:"PASS"`. The token/unlink handling (143-144, 150) is correct; the trust model is not.

**M6 — The rejection loop coaches the model toward the validator. `managed-agent-runner.mjs:111-112`**
Rejected slices are fed the exact validator messages ("SUCCEEDED requires a durable verification artifact for every gate"). Combined with H1, this is an explicit gradient toward producing validator-satisfying artifacts rather than toward completing the objective.

---

## LOW

- **L1** `managed-agent-runner.mjs:164` — the budget-exhaustion envelope sets `contractValidated: true` when no contract was validated. Harmless today (status `FAILED`), but that flag is the security-relevant one at `execution-supervisor.py:65`.
- **L2** `execution-supervisor.py:195-198` — `recover()` reads terminal evidence *before* the `pid_alive` check, unlike `run()` at 168-169. Weaker than the invariant `test_execution_supervisor.py:38-41` was written to protect.
- **L3** `execution-supervisor.py:154` — `PR_SET_DUMPABLE` protects the Python supervisor, but the nonce also lives in the Node runner's memory, which stays dumpable. Mitigated by Yama `ptrace_scope=1` (descendants cannot trace ancestors); the comment overstates the coverage.
- **L4** `managed-agent-runner.mjs:50` — `budgetMs` and `evidenceStarted` are dead; evidence hashing has no time bound.
- **L5** `managed-agent-runner.mjs:117` — `--thinking` is passed through unvalidated; a direct invocation can pass `low`. The plugin path is safe (`openclaw.plugin.json:20` excludes it).
- **L6** `managed-agent-runner.mjs:16-20` — `atomicJson` renames without fsync, unlike `atomic_text` at `execution-supervisor.py:39`.
- **L7** `index.js:221-223` — the `DISPATCHED` ternary branch is unreachable; line 220 already returned.
- **L8** `index.js:198` — `before_dispatch` passes `messages: []`, so `CONTEXT.json` is empty while `taskMarkdown` (line 43) tells the runner to read it for context.

---

## Requirement-by-requirement

| Required behavior | Status |
|---|---|
| exit 0 alone cannot prove completion | Met on the plugin path; M2 leaves the mechanism in the CLI |
| decomposed into durable packages and gates | Durable and frozen; completeness unenforced (H2) |
| partial work continues in bounded slices | Met; bounded correctly by deadline and `maxSlices` |
| SUCCEEDED requires all PASSED with evidence | Structurally met; "evidence" is not evidence (H1) |
| BLOCKED requires evidenced external dependency | Structurally met; evadable by relabeling (M1) |
| defects/tests/size/remaining work ≠ BLOCKED | Enforced only against the literal `FAILED` label (M1) |
| reconciled through supervisor/TaskFlow, delivered once | Once per run; not per objective (M3), at-least-once delivery (M4) |
| complex slices do not inherit low thinking | Met (`index.js:181`, `openclaw.plugin.json:20`, runner `:117,148`) |

The implementation converts an unconditional false `SUCCEEDED` into one that requires the model to author a plan, author artifacts, and pass an LLM reviewer. That is a real reduction in failure rate. It is not a structural prevention: H1 and H2 are mechanically reachable paths to `SUCCEEDED` with the objective unmet, H3 leaves the whole contract unapplied to objectives the regexes miss, and H4 is a live logic defect that can strand any run.

**FAIL**
