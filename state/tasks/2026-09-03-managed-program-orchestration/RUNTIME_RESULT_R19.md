I read all six files in scope. Bash was denied, so all findings below are from static analysis (I attempted a runtime repro of finding 1 and could not run it — noted where that matters).

## Verification results

| Claim | Result |
|---|---|
| Exit 0 alone is never SUCCEEDED | **Holds** in `run()` — `execution-supervisor.py:208-211` requires nonce-validated terminal evidence, and `:209` demotes `SUCCEEDED`+nonzero to `CRASHED`. |
| Terminal capability not plaintext / not inherited | **Holds at the file and env layer.** Only `terminalNonceHash` is persisted in state (`:187`); the nonce moves over an inherited pipe fd (`:193-198`), is consumed and `closeSync`'d before any model spawn (`managed-agent-runner.mjs:129`), and `childEnv` strips the fd var (`:136`). `RESULT.json` does carry the nonce in cleartext, but it is only written after the last model invocation of that run and the nonce is per-run and single-use. See MEDIUM note below. |
| Terminal evidence read only after runner exit | **Holds** — `execution-supervisor.py:206-208` reads only after `poll()` returns; `recover` reads only after `managed_runner_alive()` is false (`:259`, `:270`). |
| Finalization/outbox race-safe | **Fails** — see findings 1 and 3. |
| Admission idempotent / RU+EN large objectives / high thinking / no arbitrary-command start | **Hold.** Disk-backed `admission.json` with `wx` + EEXIST-reread (`index.js:165-172`), deterministic ingress id (`:43`), RU and EN patterns (`:10-36`), `?? "high"` at `:231` plus hardcoded `"high"` for planner/reviewers, and dispatch takes `Type.Object({})` with the argv built internally (`:218-232`). |
| Owner delivery reconciled | **Fails** — see finding 2. |

---

## CRITICAL — every successful managed run is rewritten to CRASHED before the owner is told

`scripts/execution-supervisor.py:254` and `:274`

`recover` re-opens an already-finalized `SUCCEEDED` state back to `RUNNING` and clears the notification intent:

```python
if state.get("status") == "SUCCEEDED":
    state.update(status="RUNNING", notificationId=None, notificationDelivered=False)
```

It then falls through to `managed_runner_alive(state)` (`:259`), which is false because the runner already exited, and reaches `:274`:

```python
if observed == "SUCCEEDED": observed = "CRASHED"
```

`observed` is the *validated* `SUCCEEDED` from `RESULT.json`, so it is unconditionally demoted and `finalize(..., "CRASHED", 0)` runs at `:276`. There is no path by which `recover` can ever confirm `SUCCEEDED`.

This is not a cold-start-only path. The plugin's recovery service calls `recover` on the *normal* completion path: `index.js:343` skips only states that are already `notificationDelivered`, and `:344` skips only `RUNNING` states — a freshly finalized `SUCCEEDED` state matches neither, so `reconcileState` runs `python3 … recover` at `index.js:294` **before** it reads status for the flow mutation and the owner message.

Failure scenario: the managed agent completes, both independent terminal reviews PASS, `managed-agent-runner.mjs:254` writes `terminalStatus: "SUCCEEDED"` with a valid nonce, the supervisor finalizes `SUCCEEDED` and exits 0. Within one 5s tick the owner receives *"Execution supervisor: CRASHED"* (`index.js:319`), the TaskFlow is closed with `runtime.fail(...)` and `blockedSummary: "execution supervisor: CRASHED"` (`index.js:309`) instead of `finish()`, and `EVIDENCE.md` is rewritten to `Status: CRASHED`. The entire execution-truth chain reports the exact inverse of what happened.

I could not execute the repro (Bash denied), but the control flow is unconditional — there is no branch between `:254` and `:274` that can be taken for a live-runner-absent `SUCCEEDED` state.

## HIGH — outbox exactly-once is per (run, status), not per run

`scripts/execution-supervisor.py:137`

```python
event_id = f"exec-{state['runId']}-{state['status'].lower()}"
```

The dedup scan at `:142-148` matches on this id, so it only suppresses a *repeat of the same status*. Combined with `recover` clearing `notificationId` at `:255`, a run whose status changes after its first notification emits a second event. Concretely, under finding 1: `outbox.jsonl` ends up with both `exec-<runId>-succeeded` (pending forever, never acked) and `exec-<runId>-crashed`. The same hole is reachable independently — `finalize` at `:163` treats a persisted terminal status as authoritative only when it is *identical* to the incoming one, so a differing persisted terminal status is silently overwritten and re-notified rather than rejected.

`test_execution_supervisor.py:53-62` only exercises this for a run that stays `FAILED`, which is the one case where the id happens not to change.

## HIGH — model agents survive the supervisor's kill path

`scripts/managed-agent-runner.mjs:36`, `:43-44`

Every `openclaw agent` invocation is spawned `detached: true`, placing it in its own session. The supervisor kills only its direct child's group — `os.killpg(process.pid, SIGTERM)` at `execution-supervisor.py:228` (timeout), `:235` (SIGINT/SIGTERM) and `:220`/`:230`/`:237` (SIGKILL escalation) — where `process.pid` is the runner, itself isolated by `start_new_session=True` at `:196`. The grandchildren are in different groups and are not signalled.

The runner installs no `SIGTERM` handler, so it dies immediately and its `child.on("close")` group-cleanup at `:44` and the timeout timer at `:43` never run.

Failure scenario: a managed run hits its wall-clock timeout. The supervisor kills the runner, finalizes `TIMED_OUT`, notifies the owner, and exits — while the in-flight model agent keeps running with full write access to the workspace, now with no supervisor, no timeout enforcement, and no terminal-evidence consumer. The state file advertises `"disablePath": "SIGINT or terminate foreground supervisor"` (`execution-supervisor.py:183`), but that documented kill switch stops the bookkeeping, not the work.

## HIGH — reconciliation discards the persisted originating delivery context

`projects/execution-supervisor-taskflow/index.js:297-300`

```js
const derivedDelivery = deliveryFromDispatch({}, { sessionKey: state.sessionKey });
state.deliveryContext = derivedDelivery?.channel && derivedDelivery?.to ? {...} : config.delivery;
```

`state.deliveryContext` — persisted durably by the supervisor from `--delivery-json` (`execution-supervisor.py:188`) precisely so delivery survives a restart — is overwritten, never read. The replacement is re-derived from the session key alone, and because the synthetic event/ctx are empty, `deliveryFromDispatch` falls to its literal default `"telegram"` at `index.js:181` and `:184`.

Failure scenario: an owner request arrives on a non-Telegram channel whose session key ends in `:direct:<digits>`. The `:direct:` branch at `:184` matches, `ctx.channelId` and `event.channel` are both undefined, so the completion notice is routed with `channel: "telegram"` and `to: "telegram:<digits>"` — `adapterTarget` strips the prefix (`:98`) and `loadAdapter("telegram")` sends the owner's completion notice to whatever Telegram account owns that numeric id. For a session key matching neither branch (e.g. `agent:main:main`, used at `index.test.mjs:139`), `to` is `undefined` and `:314` throws `missing originating delivery context` on every 5s tick forever — the correct target was sitting in `state.deliveryContext` the whole time.

## HIGH — the test suites cannot observe the CRITICAL defect

`scripts/test_execution_supervisor.py:53`, `projects/execution-supervisor-taskflow/index.test.mjs:133`

`test_notification_exactly_once_after_recovery` and `test_outbox_deduplicates_after_state_intent_loss` both launch `"pass"`, which finalizes `FAILED` — the single status for which `recover`'s `SUCCEEDED` branch and the status-keyed event id are both inert. No test drives a `SUCCEEDED` state through `recover`. On the plugin side, `index.test.mjs:133` asserts `sends.length === 2` (one per admission) but never asserts the message text, the post-reconcile `state.status`, the outbox line count, or whether `runtime.finish` vs `runtime.fail` was called — so the succeeded→crashed inversion and the resulting duplicate outbox event pass the suite silently.

---

**MEDIUM (not blocking, for the record):** the supervisor hardens its own memory with `PR_SET_DUMPABLE=0` (`execution-supervisor.py:191`), but `dumpable` resets on `execve`, so the runner — which holds the nonce in memory for the entire run and writes it in cleartext to `RESULT.json` (mode 0644) — has no equivalent protection. Exploitation requires `ptrace_scope=0`, since the model agents are descendants rather than ancestors of the runner. Also minor: `--require-validated-terminal` (`:294`) is dead — `:185` unconditionally overwrites it with `bool(args.terminal_evidence)`; and `admission.sessionKey` may be `null` at `index.js:227`, which makes `spawn` throw `ERR_INVALID_ARG_TYPE` (fails closed, lock released at `:243`).

**FAIL**
