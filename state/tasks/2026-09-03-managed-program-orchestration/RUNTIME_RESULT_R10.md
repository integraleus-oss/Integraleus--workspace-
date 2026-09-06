I reviewed all five files statically (no edits, no execution).

## CRITICAL

**C1 — The recovery service trusts unauthenticated state files; a managed agent can turn them into arbitrary file overwrite, arbitrary process kill, and arbitrary outbound messages.**

`index.js:284` walks `state/tasks/**` for *any* file named `execution-supervisor-state.json` and reconciles it. There is no provenance check (no admission linkage, no signature, no allowlist of task roots). Every dangerous parameter is then read out of that file:

- `execution-supervisor.py:205` — `evidence = Path(state["evidencePath"]); outbox = Path(state["outboxPath"])`, unvalidated.
- `execution-supervisor.py:207` — with `status` already terminal, `notify_once()` appends to `outboxPath` (creating parent dirs, `:108`) and `update_evidence()` (`:76-99`) reads, rewrites and `os.replace()`s `evidencePath`. **Arbitrary file overwrite anywhere the uid can write.**
- `execution-supervisor.py:211` — non-terminal branch: `os.killpg(int(state["pid"]), SIGTERM)` after only a liveness check; `pidStartTicks` is optional (`:208`), so a planted file omits it. **Arbitrary process-group kill.**
- `index.js:255-262` — `adapterTarget(state.deliveryContext)` → `adapter.sendText({ to, threadId, text: ... Flow ${state.flowId}; run ${state.runId} ... })`. Channel, recipient **and** payload substrings are all attacker-chosen. **Outbound exfiltration to an arbitrary recipient**, and it happens *before* the ack (`:263`), so it fires even when ack fails.

The managed agent is explicitly exempted from admission and tool blocking (`index.js:117`), so it runs with full tools inside the workspace and can write such a file. `safePath()` (`index.js:60-65`, used at `:322`) validates only the `statePath` *argument* of the recover tool — never the paths *inside* the state document, and the background service bypasses it entirely. Minimal payload: `{"status":"SUCCEEDED","evidencePath":"<victim>","outboxPath":"<victim2>","notificationId":"x","notificationDelivered":false,"deliveryContext":{"channel":"telegram","to":"telegram:<attacker>"},"runId":"<text>","flowId":"<text>"}`.

## HIGH

**H1 — `recover` mutates durable state outside the finalize lock; terminal status can be rolled back and the outbox double-appended.**
`finalize()` serializes on `*.finalize.lock` (`execution-supervisor.py:124-134`), but `recover()` never takes it: it loads state at `:204` and writes at `:207` (`notify_once` + `update_evidence`) and `:214` (`atomic_json` + `update_evidence`). The recovery service spawns `recover` every `pollMs` against live runs (`index.js:240`, default 5 s tick at `:292`). Interleaving: recover loads `RUNNING` → supervisor's child exits and `finalize()` writes `TIMED_OUT`/`SUCCEEDED` + outbox event + EVIDENCE.md → recover's `atomic_json` lands last and **restores `status: RUNNING`, `notificationId: null`, and rewrites EVIDENCE.md back to RUNNING** while the supervisor process is already gone. The next tick re-derives status from `RESULT.json`, so a validated SUCCEEDED self-heals — but a `TIMED_OUT` or `INTERRUPTED` run has no `RESULT.json` and is re-finalized as `CRASHED` (`:218`), and a rolled-back `notificationDelivered` re-delivers. Same window makes `notify_once`'s outbox scan (`:109-115`) a TOCTOU: two processes can both see an empty outbox and both append the same event id. `acknowledge()` (`:221-225`) is likewise unlocked. This directly contradicts the race-safety and exactly-once requirements.

**H2 — Admission is not idempotent under concurrency: the same prompt can dispatch two supervisors onto the same state/outbox/RESULT.json.**
`createAdmission` reads `admission.json` at `index.js:123` and writes it at `:157` with a plain `writeFile` — deliberately *not* `{flag:"wx"}`, unlike CONTEXT/TASK/EVIDENCE (`:148,151,154`). The in-memory maps are only populated at `:158-159`, after several awaits. Two ingress events with identical `(sessionKey, prompt)` hash to the same id (`:43`), both miss the persisted check, both fall through to `dispatchAdmission` (`:212`), and each spawns a supervisor with the same `--state`, `--outbox`, `--terminal-evidence` (`:182-189`). The second launch also unlinks the first's terminal evidence (`execution-supervisor.py:140`). The tests only exercise the strictly sequential case (`index.test.mjs:73-83`), so this is uncovered.

**H3 — The terminal capability is handed to the entire child process tree, and is persisted in plaintext in `RESULT.json`.**
State correctly stores only `terminalNonceHash` (`execution-supervisor.py:153`, asserted at `test_execution_supervisor.py:36`). But the nonce is delivered via `MANAGED_TERMINAL_FD` in `child_env` plus a `pass_fds` pipe (`:158-163`). `pass_fds` clears `FD_CLOEXEC`, and neither the env var nor the fd is scrubbed by anything in scope, so every descendant of the runner — including whatever process the runner gives the model's `bash`/exec tools — inherits both `/proc/self/environ` and the open fd. Any such descendant that reads the fd first can write `{"terminalStatus":"SUCCEEDED","contractValidated":true,"terminalNonce":…}` and forge SUCCEEDED, which is exactly the forgery `test_forged_terminal_is_not_accepted_while_child_is_running` (`:37-40`) claims to prevent (that test only proves an *unknown* nonce fails). By contract the nonce is also written back to `RESULT.json` in cleartext (`terminal_from_evidence:70-71`; `index.test.mjs:25`) and never removed after finalize. The only possible mitigation lives in `managed-agent-runner.mjs`, which is outside the inspection scope — so within the reviewed surface this requirement is **not met**.

**H4 — Tool-path dispatch can permanently lose owner delivery and spin the recovery loop forever.**
`execution_supervisor_dispatch` passes `ctx.deliveryContext ?? config.delivery` (`index.js:309`); when both are absent, `:185` serializes `{}` and the supervisor persists `deliveryContext: {}` (`execution-supervisor.py:154`). `reconcileState` then throws `missing originating delivery context` (`index.js:256`) on every 5 s tick, forever, with no fallback to the `sessionKey`-derived target that the ingress path computes via `deliveryFromDispatch` (`:163-173`) and no give-up/escalation. The task completes and the owner is never told. `before_prompt_build` (`:225`) makes this tool path the *primary* one, and the test injects `deliveryContext` by hand (`index.test.mjs:64`), so the gap is invisible to the suite.

## MEDIUM (noted, not gating)

- `execution-supervisor.py:216-218` — recovery accepts a validated `SUCCEEDED` without the `code != 0 → CRASHED` cross-check that `run()` applies at `:174`.
- `index.js:36` — any prompt ≥600 chars containing `build`/`fix`/`выполни`… is captured as managed; combined with the blanket `before_tool_call` block (`:228-234`) an ordinary long owner request is hijacked and its tools disabled.
- `execution-supervisor.py:151` overrides `--require-validated-terminal` (`:235`) with `bool(args.terminal_evidence)`; the flag is dead. Fail-safe direction, but the CLI contract is misleading.
- `index.js:184-188` — `admission.sessionKey` may be `null`, which makes `spawn` throw `TypeError` on argv.
- `execution-supervisor.py:165-166` — `pid` is persisted one write before `pidStartTicks`; a crash in that window leaves recovery relying on bare `os.kill(pid,0)` (pid-reuse ambiguity).

## Criterion results

| Requirement | Verdict |
|---|---|
| exit 0 alone never SUCCEEDED | **Pass** — `:174`/`:176` force FAILED on `code==0` without validated evidence; covered by tests `:30-43` |
| terminal evidence read only after runner exit | **Pass** — `:171-175` gated on `poll()`; recovery gated on pid death `:208` |
| terminal capability not plaintext / not inherited | **Fail** (H3) |
| finalization + outbox race-safe | **Fail** (H1) |
| admission idempotent | **Fail** under concurrency (H2); sequential/restart idempotency is correct |
| RU/EN large objectives | **Pass** with over-capture risk (M2) |
| high thinking | **Pass** — default `"high"` (`index.js:189`, plugin.json:20); config may downgrade to `medium` |
| arbitrary-command start removed | **Pass** — `execution_supervisor_start` gone, dispatch takes no params, argv fixed and non-shell |
| owner delivery reconciled | **Fail** on the tool path (H4); ingress path is correct |

**FAIL** — 1 CRITICAL (C1) and 4 HIGH (H1–H4).
