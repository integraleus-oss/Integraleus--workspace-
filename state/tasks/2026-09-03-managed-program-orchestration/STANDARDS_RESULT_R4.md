I reviewed all 11 files, the diff against HEAD, and the three prior review rounds in `state/tasks/2026-09-03-managed-program-orchestration/`. **I could not execute any test — Bash is denied in this session (don't-ask mode)**, so everything below is static analysis. No files were edited.

Several R3 findings were genuinely fixed (C3 deadlock, H2 trust model, H3 SIGTERM, M3 blocker shape, M4 stale unlink, M6 evidence truncation, L2/L9). The findings below are what survives or is newly introduced.

---

# Findings

## Critical

### C1 — Malformed outcome JSON crashes the runner with no `RESULT.json`; the retry loop never engages
`scripts/managed-agent-runner.mjs:50-51`, `:42`; `scripts/managed-outcome-contract.mjs:41`

R3's C1 was fixed narrowly (`:41` now guards `!Array.isArray(x.evidence) ||`), but the *class* of unguarded dereference remains in three places on the hot path:

- `managed-outcome-contract.mjs:41` — `value.gates.some(x => !Array.isArray(x.evidence) ...)`. `x` itself is unguarded, unlike every sibling (`:33`, `:36`, `:49` all use `x?.`). Reached only when `status === "SUCCEEDED"`.
- `managed-agent-runner.mjs:50-51` — `[...(outcome?.packages || []), ...]` requires an *iterable*; `||` only catches null/undefined. Then `.filter(item => String(item.status)...)` derefs `item` unguarded.
- `managed-agent-runner.mjs:42` — `outcome?.[kind]?.find(item => item.id === ...)`; `?.` does not protect against `find` being `undefined` on a non-array, nor `item` being null.

Failure scenario: the managed agent writes `{"status":"SUCCEEDED","summary":"x","objectiveComplete":true,"packages":{"P1":{...}},"gates":[...]}` — `packages` as an object instead of an array, a routine model formatting slip. `validateManagedOutcome` survives it (`:23` guards), then `evidenceErrors` at `:113` throws `TypeError: outcome?.packages is not iterable`. This is a top-level `await` in a module, so it becomes an unhandled rejection: the process dies before `attempts.push` (`:115`) and before any `atomicJson` write. Result: no `RESULT.json`, no `agent-result.json` slice entry, no validation feedback, no next slice. Same for `"gates":[null]` (hits contract `:41`) and for a non-array `packages` on slice ≥2 (hits `planErrors:42`).

The supervisor then reports a bare `FAILED` (`execution-supervisor.py:146-147`) with zero diagnostics. This kills the multi-slice correction loop, which is the entire point of D-2026-09-03-01 — on exactly the input the contract exists to reject.

Fix: wrap the whole per-slice validation block (`managed-agent-runner.mjs:109-114`) in try/catch and convert a thrown error into a `validationErrors` entry, so malformed output feeds the correction loop instead of terminating it.

---

## High

### H1 — Exactly-once terminal delivery is still breakable: `finalize` guards on in-memory state only
`scripts/execution-supervisor.py:114`, `:92-110`; `projects/execution-supervisor-taskflow/index.js:264-266`

The new pid-alive skip (`index.js:264-266`) narrows R3's C2 substantially, and the outbox dedup scan (`:99-105`) catches the crash-between-append-and-id-write case. But `finalize:114` checks `state.get("status")` on the **in-memory dict**, never re-reading the file, so two processes finalizing the same run cannot see each other.

Failure scenario (timeout path): supervisor hits `--timeout` and `killpg`s the child (`:156`). The child dies. Within the next ≤0.25s the supervisor is still in `process.wait()` / `finalize`. A recovery tick fires, reads state (`RUNNING`), sees `state.pid` dead, and no `RESULT.json` exists (the timeout path never writes one) → `recover` finalizes `CRASHED`, appends `exec-<run>-crashed`. The supervisor's `finalize` then runs with in-memory status still `RUNNING`, writes `TIMED_OUT` over it, and `notify_once` computes `exec-<run>-timed_out` — a different id, so the dedup scan at `:102` misses it and appends a second event. **Two outbox events, two owner messages, contradictory statuses**, violating D-2026-09-01-01's "at most one alert".

The window is small (5s tick vs. a sub-second race), which makes this a rare production incident rather than a test failure — the worst kind. Fix: re-read the state file at the top of `finalize` and abort if it is already terminal, plus an `O_EXCL` lock file per `statePath`.

### H2 — Timeout budget regression: the 30 s headroom no longer covers evidence verification
`projects/execution-supervisor-taskflow/index.js:171`; `scripts/managed-agent-runner.mjs:62`, `:105`, `:113`

R3 praised this arithmetic as sound, and it was — before the M2 fix added a **120 s** per-command evidence timeout at `:62`. The headroom was not widened to match.

The runner's deadline is `timeoutSeconds - 30` (`index.js:171`); the supervisor kills the group at `timeoutSeconds`. Per slice, the agent gets `min(600, remaining - 10)` (`:105`), so it can legitimately return with ~10 s of runner budget left. `evidenceErrors` (`:113`) then runs *every* PASSED package/gate command sequentially, each up to 120 s. Total post-agent time available before the supervisor SIGKILLs: 10 + 30 = **40 s**. A single slow gate command exceeds it.

Failure scenario: final slice returns a valid `SUCCEEDED` outcome with three gates whose verification commands take 20 s each. The runner is killed mid-verification, never writes `RESULT.json`, and the owner is told `TIMED_OUT` for a run that actually succeeded — with all slice progress discarded.

Compounding: `evidenceErrors` runs on every slice over all PASSED items, so a 12-slice run with 5 gates executes up to 60 gate commands, and any non-idempotent one replays its side effects each time. R3's M2 flagged this; only the timeout half was fixed.

### H3 — Evidence-command timeout kills the child but not its process group; the runner can hang past its own budget
`scripts/managed-agent-runner.mjs:26`, `:32`, `:106`

Two related defects in `run()`:

1. `spawn` is called without `detached: true` (`:26`) and the timer does `child.kill("SIGKILL")` (`:32`) on the direct child only. The promise resolves on `"close"`, which requires the stdio pipes to close — a grandchild that inherited stdout keeps them open. So a gate command like `["bash","-c","some-daemon &"]` leaves the runner blocked forever despite the 120 s timer having fired.
2. The `openclaw agent` invocation at `:106` passes **no** `timeoutMs` at all, so slice budgeting is entirely advisory — it depends on the `openclaw` CLI honouring its own `--timeout`. `run()` supports a watchdog; this call site declines to use it.

In both cases the only backstop is the outer supervisor, which converts the situation into `TIMED_OUT` and discards all slice progress. Fix: `detached: true` + `process.kill(-child.pid, "SIGKILL")`, and pass `sliceSeconds * 1000 + grace` at `:106`.

---

## Medium

### M1 — `authorizedSessionPrefixes` is now dead config, and the README documents the removed behaviour
`projects/execution-supervisor-taskflow/index.js:25`, `:48-52`; `openclaw.plugin.json:23`; `README.md:24-25`

The H2 fix removed prefix matching and the `agent:main:main` special case from `isTrustedOwnerContext`, but left `authorizedSessionPrefixes` declared in **both** schemas with `default: ["agent:main:telegram:"]`. It is now read nowhere (verified by grep). Any deployment whose `config.json` relies on it silently loses all admission the moment 0.3.0 is enabled — no error, no warning, the config key still validates.

`README.md:24-25` still asserts "Owner admission covers every Telegram topic/direct session routed to agent `main`, plus its canonical direct session `agent:main:main`", which is now false. The 0.3 migration note (`:40-47`) covers `terminalEvidencePath` and `thinking` but not this, which is the more consequential break.

Fix: delete the key from both schemas and correct `README.md:24-25`, or restore prefix support behind an explicit opt-in.

### M2 — `contractValidated: true` is still hardcoded on every result path (R3 H1, unaddressed)
`scripts/managed-agent-runner.mjs:118`, `:124`, `:133`; consumed at `scripts/execution-supervisor.py:61`

All three `RESULT.json` writers assert `contractValidated: true`, including the `CRASHED` path (`:118`, where no outcome was ever validated) and the budget-exhaustion `FAILED` path (`:133`, where no valid outcome was ever produced). Only `:124` genuinely qualifies. The supervisor's strict gate therefore reduces to "a file exists here with a recognized status" — useful (it does catch exit-0-without-envelope, which is the real-world failure mode) but not what the flag name, the README (`:42-45`), or `execution-supervisor.py:61` claim. Set the field from `terminal !== null` rather than as a literal.

### M3 — A failed slice destroys the durable plan handed to the next slice
`scripts/managed-agent-runner.mjs:89`, `:129`

`:89` unlinks `MANAGED_OUTCOME.json` at the start of every slice, and `:129` sets `previous` to a bare `{status:"CONTINUE", summary:"Missing or invalid managed outcome"}` when the slice produced no outcome.

Failure scenario: slice 4 of 12 times out inside `openclaw agent` without writing the outcome. The file is already deleted, so the last-known-good package/gate list is gone from disk, and slice 5's prompt receives `Previous contract: {"status":"CONTINUE","summary":"Missing or invalid managed outcome",...}` — no packages, no gates, no evidence, no progress. The agent must reconstruct the whole plan from session memory while `planErrors` (`:37-46`) still enforces the in-memory baseline, so any reconstruction drift is rejected as "cannot be removed" / "title cannot change". The run can deadlock on its own plan lock.

Fix: retain the last *valid* outcome in `previous` and only overlay the new `validationErrors`; don't unlink until a replacement is written.

### M4 — Unbounded stdout/stderr buffering in `run()`
`scripts/managed-agent-runner.mjs:28-30`

`stdout += chunk` accumulates without limit. The `.slice(-20000)` at `:115` truncates only for *storage*, after the full string is already resident. An agent-authored evidence command that streams output (`["yes"]`, `["cat","/dev/urandom"]`, a verbose test suite) OOMs the runner within its 120 s window. Cap the accumulator at ~64 KB with a ring/head-tail buffer.

### M5 — Test coverage regression: `safePath` traversal rejection is no longer tested
`projects/execution-supervisor-taskflow/index.test.mjs:176-182`

The assertion was changed from `/path outside workspace root/` to `/trusted owner required/`. Because `prefixCtx` sets `senderIsOwner: false`, the auth check at `index.js:304` now short-circuits before `safePath` is ever called — so the `evidencePath: "/outside/EVIDENCE.md"` argument is inert and **no test in the repo exercises `safePath` at all** (grep-confirmed). A security control lost its only coverage as a side effect of the auth change. Add a separate trusted-context case that still passes an out-of-root path.

### M6 — New enforcement logic is largely untested
`scripts/managed-agent-runner.test.mjs:59-67`

The three mechanisms this change is *for* have no coverage: `planErrors` (package/gate removal or rename after slice 1), evidence hash mismatch, missing evidence file, and failing/non-zero evidence commands. All seven scenarios exercise only status/blocker shape. Positively, `index.test.mjs:21` does now assert the `--outcome`/`--thinking` argv contract, closing an R3 gap.

### M7 — Undeliverable notifications retry forever with no backoff or dead-letter (R3 M7, unaddressed)
`projects/execution-supervisor-taskflow/index.js:155`, `:225`, `:263`

`deliveryFromDispatch` falls back to `to: ctx.conversationId` (`:154`), which may be `undefined`. `reconcileState` then throws `missing originating delivery context` (`:225`) on every tick. `notificationDelivered` never becomes true, so `:263` never skips the state — the loop spawns `python3 recover` and logs an error every 5 s indefinitely, and the owner is never told the run finished.

### M8 — `recover`'s pid check shadows terminal evidence; pid reuse wedges the run permanently (R3 M1, unaddressed)
`scripts/execution-supervisor.py:176-181`

`pid_alive` still precedes `terminal_from_evidence`, and `state["pid"]` (the *child's* pid, not the supervisor's) is never revalidated against start time or cmdline. After a reboot or pid-space wrap, an unrelated process holding that pid makes `recover` print `RUNNING` forever while a valid `RESULT.json` sits unread on disk. `pid_alive` also returns `True` on `PermissionError` (`:53`), so a recycled pid owned by another user reads as alive.

---

## Low

- **L1 — `terminalEvidencePath` lacks `minLength: 1`.** `index.js:300` → `""` makes `terminalPath` `null` at `:310`, and `spawn` receives `null` in argv at `:319` → `TypeError`. R3 M5's second half, unaddressed.
- **L2 — No guard against `terminalEvidencePath` aliasing `evidencePath`.** `execution-supervisor.py:122` unconditionally unlinks the caller-supplied path before launch. `index.js:307-310` validates all four paths independently but never checks they differ, so a caller can delete their own `EVIDENCE.md` by passing it twice.
- **L3 — SIGTERM handler installation race.** `execution-supervisor.py:136-137` installs the handler after `Popen` (`:135`) but the `try` block starts at `:140`. A SIGTERM landing in that window raises an uncaught `KeyboardInterrupt`, orphaning the child with no finalize. Install the handler before `Popen`.
- **L4 — Dead branch in `before_tool_call`.** `index.js:210` returns early on `status === "DISPATCHED"`, so the ternary's "already detached" arm at `:211-212` is unreachable. Note this also means post-dispatch foreground work is now entirely unguarded (`index.test.mjs:133-134`, `:148-149` were changed to assert `undefined`) — defensible given the C3 deadlock, but it is a real loosening of the "managed work must not also run in the foreground" property.
- **L5 — One-time evidence loss on migration.** `execution-supervisor.py:78-81` preserves content after `## /Execution Supervisor`, but pre-0.3 `EVIDENCE.md` files have the start marker and no end marker, so `lines = lines[:start]` still truncates everything below it on the first 0.3 write. 18 on-disk state dirs are affected.
- **L6 — Runner `atomicJson` does not fsync and leaks temp files.** `managed-agent-runner.mjs:15-19` renames without fsync (the Python side fsyncs at `:36`); `RESULT.json` is the exactly-once terminal evidence and deserves matching durability. A crash between `writeFile` and `rename` strands `.<uuid>.tmp` permanently.
- **L7 — Agent-authored evidence commands are executed with the runner's full environment and no allowlist.** `managed-agent-runner.mjs:62`. `validEvidence` (`managed-outcome-contract.mjs:12-13`) accepts any non-empty argv, so `["/bin/true"]` satisfies "SUCCEEDED requires an independently executed command for every gate" (`:41`). Not a privilege escalation — the agent already has shell access — but the word *independently* overstates the guarantee.
- **L8 — Unresolved R3 lows.** L1 hardcoded absolute paths (`managed-agent-runner.test.mjs:47`, `index.test.mjs:47`); L5 no fsync; L6 positional `argumentsMap` (`:9-13`) silently corrupts every subsequent key after a bare flag; L7 `schemaVersion: 2` has no reader; L8 `MANAGED_MAX_SLICES` is env-only and absent from both config schemas and the README; M8 full-tree rescan every 5 s; M9 admitted-but-undispatched work lost across gateway restart.
- **L9 — `spawn("python3", …)`** (`index.js:172`, `:321`, `:220`, `:232`) relies on `PATH` in a gateway service context; `TECHNICAL-RULES.md:132-136` calls for absolute paths in non-login shells. `OPENCLAW_BIN` correctly defaults to `/usr/bin/openclaw`.
- **L10 — `--thinking` is an unverified CLI assumption.** `managed-agent-runner.mjs:107` passes it unconditionally with no capability check. If the installed `openclaw` build lacks the flag, every slice exits non-zero and slice 1 terminates the run as `CRASHED`. Flagged in `SPEC_RESULT_R3.md:100` and still unverified; I could not run the CLI.

---

## What's done well

- The R3 C3 session deadlock is properly fixed at `index.js:204` and `:210`, and the terminal cleanup of both admission maps (`:248-251`) prevents the map leak for completed runs.
- The trust model tightening (`index.js:48-52`) is the right call — dropping wildcard prefix trust in front of `execution_supervisor_start`'s verbatim `command` execution closes a genuine privilege hole.
- `update_evidence`'s end-marker + suffix preservation (`execution-supervisor.py:76-88`) correctly stops the supervisor from eating agent-written evidence, and removing `update_evidence` from the poll loop (`:143`) is a sound I/O reduction.
- Backward compatibility is handled deliberately: `recover` reads `bool(state.get("requireValidatedTerminal"))` (`:179-180`), so the pre-existing on-disk states reconcile in legacy mode rather than being misreported.
- The SIGTERM → `wait(timeout=5)` → SIGKILL escalation (`:151-153`) closes a real hang, and `killpg` on a `start_new_session=True` child is the correct primitive.
- Version bump is consistent across `package.json`, `package-lock.json`, and `openclaw.plugin.json`; the TypeBox and JSON schemas are kept in sync; `flag: "wx"` with `EEXIST` tolerance (`index.js:130-138`) makes admission creation idempotent.

---

**FAIL**

C1 is the blocker: a routine JSON shape error from the managed agent kills the runner outright, producing a diagnostic-free `FAILED` and disabling the multi-slice correction loop that D-2026-09-03-01 mandates — and it survives in three places after R3 fixed one of them. H2 is a regression introduced by this round's own M2 fix: adding a 120 s evidence-command timeout without widening the 30 s supervisor headroom means successful runs get reported as `TIMED_OUT`. H1 leaves the exactly-once guarantee breakable on the timeout path, against an explicit "at most one alert" decision. H3 lets the runner hang past every budget it owns. M1 silently breaks a live config contract while the README documents the old behaviour.

C1, H2, and M1 are narrow fixes (a try/catch, a constant, a schema deletion plus two README lines). H1 needs `finalize` to re-read persisted state before deciding, which is slightly more involved but well-scoped.

I did not run `scripts/test_execution_supervisor.py`, `scripts/managed-agent-runner.test.mjs`, or `projects/execution-supervisor-taskflow/index.test.mjs` — Bash was denied. If you re-run this with execution permitted, start by confirming C1 with an outcome whose `packages` is a JSON object instead of an array, and H2 with a gate whose evidence command sleeps 45 s.
