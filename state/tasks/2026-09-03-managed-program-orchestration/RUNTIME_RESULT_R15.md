Static review only — test execution was denied by the permission mode, so all findings below are from reading the five files.

## CRITICAL

**1. The supervisor state file is trusted as an authority on terminal status, and the supervised model can write it.**

`scripts/execution-supervisor.py:213-221` — every 5 s the running supervisor re-reads its own state file and, if `status` is terminal, kills the runner and exits with that verdict:

```python
persisted = load_json(args.state)
if persisted.get("status") in TERMINAL:
    os.killpg(...)
    return 0 if persisted["status"] == "SUCCEEDED" else 4
```

`scripts/execution-supervisor.py:221` then does `state = persisted`, so the supervisor also adopts the file's `requireValidatedTerminal` and `terminalNonceHash` — which are exactly the fields the nonce contract at `:207` depends on. `recover()` at `:243-247` likewise trusts `state["status"]` unconditionally, and `projects/execution-supervisor-taskflow/index.js:288-296` then delivers "Execution supervisor: SUCCEEDED" to the owner off that value.

The state file is written by `atomic_json` → `tempfile.mkstemp` (mode 0600) under `taskRoot`, and the runner/model runs as the same uid in that same tree — `:190`'s `PR_SET_DUMPABLE` comment ("protect supervisor memory from same-uid inspection") is an in-file acknowledgement of that threat model. Two forgeries follow: write `{"status":"SUCCEEDED"}` into the state file (accepted within 5 s, supervisor exits 0, owner notified), or rewrite `terminalNonceHash` to the hash of a nonce of your choosing and write a matching `RESULT.json`. The nonce protects `RESULT.json` but nothing protects the file that holds the nonce hash. The RESULT.json path is hardened; the state path is the unguarded way around it.

## HIGH

**2. `index.js:111-116` — the 60 s ADMITTED expiry silently disables the pre-dispatch gate.**

```js
if (admission?.status === "ADMITTED" && Date.now() - Date.parse(admission.createdAt) > 60000) { ...delete...; return undefined; }
```

`before_prompt_build` (`:251-255`) and `before_tool_call` (`:257-263`) both key off `admissionForContext`. A high-thinking turn that takes over 60 s to reach its first tool call loses the block entirely and proceeds to do the work in the foreground unmanaged — the exact outcome the admission gate exists to prevent. `execution_supervisor_dispatch` then throws `no managed admission for this turn` (`:339`). The same applies immediately after a plugin restart, since a persisted admission is reloaded with its original `createdAt` and is expired on first lookup.

**3. `index.js:162` — `createAdmission` overwrites `admission.json` unconditionally, breaking dispatch idempotency.**

`writeFile(resolve(taskRoot, "admission.json"), ...)` has no `wx` flag and no status guard, unlike the three writes above it. A duplicate ingress that interleaves past the in-memory cache (both handlers reach `createAdmission` before either populates `admissionsBySession`) rewrites a `DISPATCHED` record back to `ADMITTED` and drops `flowId`/`supervisorPid`/`deliveryContext`. Consequences: the dispatch lock at `:182` succeeds because the winner already unlinked it at `:220`, producing a second supervisor and runner on the same task root and state file; and `reconcileState`'s integrity check at `:274-275` (`admission.flowId !== state.flowId`) then throws `untrusted supervisor state` forever, permanently blocking owner delivery for that task. The `stat` at `:185` also races to ENOENT against that same unlink.

**4. `execution-supervisor.py:259-265` — the recovery path never observes a real exit code, and downgrades genuine success to CRASHED.**

```python
recovered_exit = terminal_exit_code(...)
if observed == "SUCCEEDED" and recovered_exit != 0: observed = "CRASHED"
```

`recovered_exit` is `None` when `RESULT.json` has no `exitCode`, and `None != 0`, so a validated SUCCEEDED becomes CRASHED. The two test suites disagree on whether that field is part of the runner contract: `test_execution_supervisor.py:81` adds `"exitCode": 0` specifically to make recovery pass, while the plugin's runner at `index.test.mjs:25` writes `terminalStatus`/`contractValidated`/`terminalNonce` and no `exitCode`. If the real runner matches the latter, every managed task that succeeds across a supervisor restart is reported to the owner as CRASHED.

Separately, that value is the runner's *self-reported* exit code, not an observed one — a runner cannot know its own exit status before exiting. So in `recover()` the "exit code 0 alone is never SUCCEEDED" invariant is not actually enforced by anything the supervisor observed; the verdict rests entirely on runner-controlled fields. The invariant holds properly only on the `run()` path (`:205-210`), where `code` comes from `process.poll()`.

**5. `index.js:317` — admitted-but-never-dispatched tasks are unrecoverable.**

`findStateFiles` matches only `execution-supervisor-state.json`, which does not exist until a supervisor is spawned. A task root left at ADMITTED (finding 2, or a crash between admission and dispatch) is never swept, never dispatched, and never produces a failure signal to the owner — it is silently dropped.

## Requirement-by-requirement

| Requirement | Result |
|---|---|
| Exit 0 alone never SUCCEEDED | Holds on the `run()` path (`py:205-210`, `:208`); defeated by findings 1 and 4 |
| Terminal capability not persisted in plaintext | Holds — nonce goes over a pipe (`py:191-197`), only `terminalNonceHash` is stored (`py:186`); asserted at `test_...py:37` |
| Terminal capability not inherited by the model | Not establishable from these five files — `MANAGED_TERMINAL_FD` and the read end are handed to the runner (`py:194-196`); whether the runner leaks either to the model lives in `managed-agent-runner.mjs`, outside the review scope |
| Terminal evidence read only after runner exit | Holds — `py:207` is downstream of `process.poll()`, stale file removed at `py:173`, covered by `test_...py:38-44` |
| Finalization/outbox race-safe | Partially — all outbox/state writes are under the `flock` (`py:159-167`, `:244`, `:254`, `:269`) and `finalize` re-checks persisted terminal at `:163`; but there is no concurrency test at all, and the lock does not protect against finding 1 |
| Admission idempotent | Fails under concurrent ingress (finding 3); the sequential and restart cases work |
| Russian/English large objectives | Holds — `index.js:10-15`, `:35-36`; note the ≥600-char fallback fires only on a leading imperative, so a large objective phrased as an infinitive or "нужно …" is not admitted |
| High thinking | Holds — `index.js:211` defaults to `"high"`, schema default matches (`index.js:22-24`, `openclaw.plugin.json:20`), enforced by the fake runner at `index.test.mjs:22` |
| Arbitrary-command start removed | Holds — only `execution_supervisor_dispatch` (no params) and `execution_supervisor_recover` (workspace-scoped path) are registered and declared (`index.js:331-362`, `openclaw.plugin.json:6-11`), asserted at `index.test.mjs:65`. `safePath` (`index.js:60-65`) resolves the root but not the target, so an in-workspace symlink escapes the prefix check; `validate_recovery_state` (`py:65-76`) contains the damage |
| Owner delivery reconciled | Holds in the happy path (`index.js:276`, `:288-296`, throws rather than falling back on a missing origin); broken permanently by finding 3, and at-least-once by the send-then-ack window at `:291-300` (mitigated by `deliveryQueueId`) |

## Lower-severity notes

- `py:283` defines `--require-validated-terminal`, but `py:184` overrides it from `bool(args.terminal_evidence)`. The flag is dead; it happens to fail strict, but it misleads.
- `index.js:260` — the ternary's `DISPATCHED` branch is unreachable; `:259` already returned.
- `py:163` returns 4 for a re-entered `TIMED_OUT` finalize where `:168` returns 124.
- `py:215` — an unhandled `load_json` failure in the heartbeat escapes `run()` past the `KeyboardInterrupt` handler, orphaning a live runner with no finalization.
- `py:200`'s initial `update_evidence` is the only evidence write not under the lock.
- `managed_runner_alive` (`py:85`) compares Python-resolved paths against a Node-`resolve`d cmdline; a symlinked workspace root makes them differ and the live runner reads as dead.

**FAIL**
