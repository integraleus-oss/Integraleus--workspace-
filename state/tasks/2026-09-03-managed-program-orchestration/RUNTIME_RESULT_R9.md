I read all five files. Here's the review.

## CRITICAL

**1. `before_dispatch` re-dispatches an already-DISPATCHED admission → two supervisors on one task**
`projects/execution-supervisor-taskflow/index.js:200-204`

`createAdmission` deliberately returns an existing record when its status is `"ADMITTED"` **or** `"DISPATCHED"` (index.js:117-118), but the ingress hook then calls `dispatchAdmission` unconditionally. The tool path guards this (`index.js:296` throws on `DISPATCHED`); the ingress path has no equivalent check.

Failure: owner sends "Выполни задачу и сообщи по завершении" twice (retry, duplicate Telegram delivery, or edited resend) in the same session. Second call → `admissionsBySession` hit, `known.prompt === prompt`, status `DISPATCHED` → record returned → `dispatchAdmission` runs again. That creates a second TaskFlow and spawns a second `execution-supervisor.py` against the *same* `--state`, `--outbox` and `--terminal-evidence` paths. The second supervisor immediately unlinks `RESULT.json` (`scripts/execution-supervisor.py:135`) — destroying the first run's in-flight terminal evidence — and both processes then rewrite the same state file with different `runId`s. Two runners execute the same objective; the outbox gets two events with different ids (dedupe is keyed on `exec-{runId}-{status}`, so `notify_once` cannot suppress them). Idempotency requirement fails.

**2. Admission identity is random when `ctx.runId` is absent — the ingress path is not idempotent across restarts**
`index.js:39-41`, `index.js:116-125`

`admissionId(runId)` falls back to `randomUUID()`. The disk-dedupe read at index.js:120 looks up `state/tasks/managed-admission/<id>/admission.json` using that freshly random id, so it can never match. The in-memory maps are the only dedupe, and they die with the process. The in-scope test's own ingress context (`index.test.mjs:71-72`) has no `runId` — i.e. the ingress path is exactly the case with no stable identity. After a plugin/host restart mid-run, the same request produces a new admission directory and a second dispatch of a task already running detached.

## HIGH

**3. Post-dispatch tool gate is dead code — all foreground work tools are allowed after dispatch**
`index.js:220-226`

Line 222 returns early when `admission.status === "DISPATCHED"`, so the ternary at 223-224 (`"...is already detached; foreground work is blocked."`) is unreachable. The intent is stated in the message and in the injected prompt ("After dispatch… stop", index.js:217) but nothing enforces it — only the model's compliance does. `index.test.mjs:105-106` and `:120-121` lock in the permissive behavior (`bash` and `sessions_spawn` both return `undefined` after dispatch). The foreground turn can therefore redo, or interfere with, the objective already running detached.

**4. `recover` reads terminal evidence before checking whether the runner is alive**
`scripts/execution-supervisor.py:191-194`

The stated invariant is that terminal evidence is read only after runner exit. `run()` honors it (evidence is read at py:167 only once `process.poll()` is non-`None`). `recover()` does not: `terminal_from_evidence` at py:191 executes before the `pid_alive` check at py:194. The recovery service polls **every** state file every 5 s, including live ones (`index.js:273-277`), so this path runs continuously during normal execution. A runner that writes a nonce-signed `RESULT.json` and keeps working (or dies afterward) is finalized and reported to the owner while still running.

This compounds with a lost-update race: `run()`'s poll loop rewrites the entire state file from its stale in-memory dict every `--poll` interval (`py:165`) without re-reading. Any concurrent mutation is silently reverted — `recover`'s terminal finalization, and `ack`'s `notificationDelivered = true` (py:203-204). When the child eventually exits, `finalize` sees its own clobbered `RUNNING` state, passes the guard at py:125, and finalizes a second time; if the recover-derived status differs from the exit-derived status (e.g. `SUCCEEDED` vs `CRASHED`), `notify_once` computes a different `event_id` and emits a **second, contradictory** outbox event. Finalization is lock-safe only against other `finalize` callers, not against the polling writer.

**5. Delivery failure aborts reconciliation before the TaskFlow is finalized, and there is no configured fallback**
`index.js:237-239` (throw), `index.js:255-259` (unreached), `index.js:27-28`

`reconcileState` throws on missing delivery context or unavailable adapter *before* the `runtime.finish`/`runtime.fail` block. Any delivery problem leaves the managed flow permanently in `running` while the tick retries every `pollMs` forever with no backoff. The tool dispatch path sources delivery solely from `ctx.deliveryContext` (`index.js:298`) — unlike the ingress path, which derives it defensively from the session key (`deliveryFromDispatch`, index.js:157-167). The `delivery` block declared in both config schemas (index.js:27-28, `openclaw.plugin.json:23-33`) is never read anywhere in the plugin, so the configured owner target cannot serve as the fallback it appears to be. Owner-delivery reconciliation is one missing `ctx` field away from a permanent stall.

## MEDIUM (not blocking, but load-bearing)

- **`--require-validated-terminal` is never read.** `py:214` defines it; `py:146` overrides with `bool(args.terminal_evidence)`. The flag fails safe (validation is always on when evidence is configured), but `test_exit_zero_without_objective_contract_fails` and `test_strict_exit_zero_without_validated_terminal_fails` (`test_execution_supervisor.py:30-32`) are therefore the same test — the `strict` parameter adds no coverage anywhere it is used.
- **Nonzero exit is ignored when evidence says SUCCEEDED** (`py:167-168`). A runner that writes valid terminal evidence and then crashes is reported `SUCCEEDED` with a nonzero `exitCode` recorded. The inverse invariant (exit 0 alone ≠ SUCCEEDED) holds; this direction is unguarded and untested.
- **`notify_once` runs outside the finalize lock** in `recover`'s already-terminal branch (`py:189-190`). Its read-scan-then-append dedupe is not atomic, so two concurrent `recover` processes in the window between `atomic_json` and `notify_once` inside a crashed `finalize` can both append.
- **Recovery exits non-zero on non-SUCCEEDED finalization.** `finalize` returns 4/124 (`py:130`), which `index.js:233` treats as a recovery failure and rejects — so the tick that *performs* a `CRASHED`/`TIMED_OUT` finalization never sends the notification. It self-heals on the following tick (recover then returns 0 via `py:189`), so this is delay plus a spurious error, not lost delivery.
- **No timeout enforcement after supervisor death.** If the supervisor is SIGKILLed, the child survives (`start_new_session=True`); `recover` reports `RUNNING` indefinitely and never re-applies `timeoutSeconds`.

## Criteria that hold up

- Exit code 0 alone is never `SUCCEEDED` — `py:169` maps `code == 0` without validated evidence to `FAILED`; covered by tests at `test_execution_supervisor.py:30`, `:32`, `:43`.
- Terminal capability is not persisted in plaintext: only `sha256` is stored (`py:148`), the nonce travels over a one-shot pipe (`py:154-159`), `PR_SET_DUMPABLE(0)` is set (`py:152`), and `test_execution_supervisor.py:36` asserts the nonce is absent from state. Forged nonces are rejected (`:37-40`) and stale evidence is unlinked pre-launch (`py:135`, `:41-43`). Caveat: `pass_fds` clears `FD_CLOEXEC` and `MANAGED_TERMINAL_FD` is placed in the child's inherited environment, so non-inheritance by the model depends entirely on `managed-agent-runner.mjs` draining the pipe before the first model tool runs. That file is out of scope and no in-scope test covers it.
- Arbitrary-command start is removed: no `execution_supervisor_start` (asserted at `index.test.mjs:65`), the dispatch tool takes `Type.Object({})` with `additionalProperties: false` (`index.js:291`), and argv is fully constructed in-plugin (`index.js:176-183`).
- High thinking is used: `config.managedAgentThinkingLevel ?? "high"` (`index.js:183`), schema-defaulted in both manifests, and the fake runner hard-fails on anything else (`index.test.mjs:22`).
- Russian and English large-objective detection works (`index.js:32-37`, asserted `index.test.mjs:7-10`); nested managed sessions are correctly exempt (`index.js:114`, `index.test.mjs:139-141`). Minor gap: the ≥600-char rule still requires an imperative verb, so a long declarative objective is not admitted.

**Test-coverage gaps that let CRITICAL 1–2 through:** `index.test.mjs` never sends the same ingress content twice, never restarts the plugin with an existing admission on disk, and every path uses a runner that succeeds — no non-SUCCEEDED reconciliation, no concurrent `run`/`recover`, and no assertion that a live runner's evidence is ignored.

**FAIL**
