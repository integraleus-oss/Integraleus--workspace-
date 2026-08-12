I reviewed the seven in-scope files plus the accepted `local_orchestrator_runner.py` / `review_projection.py` / `tests/test_integration.py` as dependencies. I did not run the suites: Bash was denied in this session, so every "tests green" claim below is assessed statically only.

## Blockers

**B1 — `EVIDENCE.md:33-34`: verification numbers don't describe the delivered tree.**
Evidence records "35/35 passed (included 14 inherited duplicate tests; cleanup removes that duplicate execution)" and no post-cleanup run. The delivered suite is 21 tests: `test_integration.py` 14 (lines 49, 62, 147, 154, 162, 168, 176, 187, 199, 208, 222, 232, 250, 259), `test_agent_launcher.py` 5, `test_live_review_cycle.py` 2. `test_live_review_cycle.py:15` composes `LocalIntegrationTests` rather than subclassing it, so nothing is re-executed and 35 cannot be reproduced. The closure gate ("existing 14 integration and 84 core tests remain green", `TASK_PACKET.md:50`) therefore has no evidence for the code as shipped.
*Remediation:* re-run both suites against the current tree and replace lines 33-34 with the actual counts (expected 21 integration + 84 core) and the commands used.

**B2 — `agent_launcher.py:68-80`: the timeout does not bound the real agent process.**
`subprocess.run(..., timeout=...)` kills only the direct child (the wrapper shell). Without `start_new_session=True` plus a process-group kill, the `claude`/`codex` grandchild is orphaned and keeps running the external call after `launch()` has already written `launch-result.json` with `timed_out: true` — and it can still write `wrapper-output.json` into the "single-use, immutable" run dir after the digests at lines 94-96 were computed. No test exercises the timeout path at all (`test_agent_launcher.py:44` covers only *invalid* timeout values), so the acceptance criterion "timeout … fails closed and remains auditable" (`TASK_PACKET.md:47`) is neither implemented nor demonstrated.
*Remediation:* pass `start_new_session=True`, and on `TimeoutExpired` `os.killpg(os.getpgid(proc.pid), SIGKILL)` before recording the result; add a test with a wrapper that spawns a sleeping grandchild and assert `timed_out`, `status == "FAILED"`, and that no file appears in the run dir afterwards.

## Major

**M1 — `agent_launcher.py:40,59-61` (propagated at `live_review_cycle.py:27,35`): `wrapper_override` defeats the allowlist.**
`ROLES` is validated, but any in-process caller can point `wrapper_override` at an arbitrary executable; the only check is "exists and is executable." The CLI (`live_review_cycle.py:77-84`) never exposes it, so the breach is at the library API the coordinator will call, not at the command line — but "argv is fixed/allowlisted" (`TASK_PACKET.md:45`) is then a convention, not an enforced invariant.
*Remediation:* keep an `ALLOWED_WRAPPERS = {CODEX_WRAPPER, CLAUDE_WRAPPER}` set and reject any resolved wrapper not in it; give tests a separate, explicitly test-only injection point (e.g. module-level `_TEST_WRAPPERS` populated by the test setUp).

**M2 — `live_review_cycle.py:52-58`: verdict write path is symlink-unsafe and lands outside the single-use cycle dir.**
The check rejects absolute paths and `..` parts, but never resolves the result nor confirms containment. A bundle whose directory contains a symlinked subdir (`"review_verdict": "link/verdict.json"`) writes the generated verdict outside the bundle tree. The accepted runner already does this correctly at `local_orchestrator_runner.py:62-66` (`source.resolve()` + `is_relative_to(base)`), so this slice is strictly weaker than the code it feeds.
*Remediation:* mirror the runner — `verdict_path = (base / verdict_relative).resolve()`, then `if not verdict_path.is_relative_to(base): raise ProjectionError(...)`, and use `open(..., "x")` instead of an `exists()` pre-check.

**M3 — `live_review_cycle.py:59-63`: post-launch failures leave no durable cycle record.**
On a successful launch followed by an extraction, projection, or policy failure, the exception propagates and `cycle-result.json` is never written; `main()` (lines 88-92) prints an `ERROR` object to stdout only. So the one outcome most in need of audit — Claude ran, budget was spent, no decision resulted — has no artifact in `cycle_root`. `test_live_review_cycle.py` covers `DECIDED` and `FAILED_LAUNCH` but not this third path.
*Remediation:* wrap lines 48-64 in `try/except`, write a `status: "FAILED_ADMISSION"` cycle result (including `launch`, `decision: null`, and the error type/message) before re-raising; add a test with a wrapper emitting contract-invalid JSON asserting the file exists and `decision` is null.

**M4 — `agent_launcher.py:15` vs `TASK_PACKET.md:20` / `EVIDENCE.md:20`: the Codex wrapper is outside the packet's declared dependency set.**
The packet allows "existing local wrappers under `/home/stanislav/agent-runs/_bin/`" as read-only dependencies. `CODEX_WRAPPER` hardcodes `main/scripts/codex-local-run.sh`, and evidence calls it "approved" without pointing at the approval. Either the boundary or the claim is wrong.
*Remediation:* amend `TASK_PACKET.md:20` to name `scripts/codex-local-run.sh` explicitly, or move/point the constant at the approved `_bin/` wrapper; drop the bare word "approved" in favour of the boundary line it derives from.

**M5 — `test_live_review_cycle.py:23-33`: the Claude argv contract is untested.**
The Codex test pins the exact argv (`test_agent_launcher.py:34`), but the Claude fake wrapper only touches `$3`. Nothing asserts that `$1` is the project root, `$2` the read-only prompt *file* (not inline text), or `$5` the timeout — i.e. the fixed-argv guarantee is unverified for the only role the live cycle actually launches. Also absent: missing/non-executable wrapper, unknown role, missing `wrapper-output.json`, and non-dict payload.
*Remediation:* have the fake wrapper `printf '%s\n' "$@" > "$4".argv` (or write argv to a file in the run dir) and assert the five positional arguments; add the four negative `LaunchError` cases.

## Nits

- `agent_launcher.py:53-56` vs `:60` — `run_dir` and the 0444 prompt are created *before* the wrapper is validated, so a bad wrapper leaves an orphan directory that permanently blocks retry at that path. Move the wrapper check above `run_dir.mkdir`.
- `agent_launcher.py:64` — the Codex prompt travels in argv and is visible in the process table; the Claude role already uses a file. Pass a prompt file for both if the wrapper supports it, or note the accepted exposure in `EVIDENCE.md`.
- `agent_launcher.py:78-79` — on timeout `exc.stdout` is `bytes` (POSIX `_communicate` returns undecoded partial data even with `text=True`), so the guard silently discards all partial output and writes empty logs for exactly the case needing forensics. Decode with `errors="replace"` instead.
- `agent_launcher.py:71` — `capture_output=True` buffers unbounded reviewer output in memory; the packet's "budget limits" checklist item (`TASK_PACKET.md:37`) has no corresponding output cap. Consider streaming straight to the log files with a byte ceiling.
- `agent_launcher.py:87,93` — synthetic `exit_code: 124` collides with a wrapper's genuine 124 (disambiguated only by `timed_out`); and the `codex_write` / `workspace-write` branch is reachable, untested, and unguarded despite `EVIDENCE.md:43-45` stating mutation is not enabled.
- `agent_launcher.py:110` — an envelope carrying `is_error: true` alongside a well-formed `result` is admitted; downstream validation catches malformed content, but an explicit rejection of errored envelopes is cheaper and clearer.
- `agent_launcher.py:94-96` — `launch-result.json` digests prompt/stdout/stderr but not `wrapper-output.json`, the file the decision is actually derived from. It is digested later by the runner snapshot, so the chain closes, but not at launch time.
- `README.md:3-4` still says the slice works "without launching agents", contradicting lines 14-18 and the whole slice; `README.md:74-76` omits `agent_launcher.py`, `live_review_cycle.py`, and the two new test modules from the `py_compile` line.
- `TASK_PACKET.md:3,33-41` — `Status: IN_PROGRESS` and eight unchecked boxes for work `EVIDENCE.md` reports as complete.

LIVE_LAUNCH_REWORK
