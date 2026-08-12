## Closure review — local orchestrator live launch

Scope read: the two live-launch documents, the four integration files under review, plus `local_orchestrator_runner.py` and `tests/test_integration.py` as accepted dependencies. I did **not** inspect the wrappers (`codex-local-run.sh`, `claude-review`), stdout/stderr content, memory, config, or the wider worktree.

**I could not execute the test suites** — Bash `python3` invocations were denied in this session. Every claim below about test coverage is from reading the test files; claims about suite results are therefore unverified, which is itself part of finding MAJ‑5.

---

## BLOCKERS

**BLK-1 — The dry run never exercised `live_review_cycle.run_cycle`; EVIDENCE presents it as if it did.**
`EVIDENCE.md:8-30` describes `live_review_cycle.py` admitting exact JSON and lists "Durable evidence: `runs/codex-smoke-01/`, `runs/claude-smoke-01/`, `dry-run/policy-runs/real-claude-contract-smoke/`". The artifact tree contradicts an end-to-end cycle run:

- no `cycle-result.json` and no `*/claude-launch/` directory exists anywhere in the task folder — `run_cycle` writes the former unconditionally on both `DECIDED` and `FAILED_LAUNCH` (`live_review_cycle.py:45`, `:73`) and creates the latter (`:34`);
- `dry-run/inputs/verdict.json` is still present, whereas `run_cycle` generates that file and deletes it (`live_review_cycle.py:58`, `:64`);
- `dry-run/policy-runs/` sits directly under `dry-run/`, not under a `cycle_root` as `run_cycle` requires (`live_review_cycle.py:60`).

The launcher ran live and the runner ran live, but the composed admission path — the actual deliverable of this slice — has only ever run against stub shell wrappers (`tests/test_live_review_cycle.py:23-33`). TASK_PACKET acceptance "The dry run demonstrates a deterministic terminal/intermediate decision" (`TASK_PACKET.md:49`) is satisfied piecewise, not for the integrated entry point.
*Remediation (pick one):* run `live_review_cycle.py` once against the real `claude-review` wrapper with a fresh bundle and commit the resulting `cycle-result.json` + `claude-launch/`; or rewrite `EVIDENCE.md:18-30` to state plainly that the launcher and runner were exercised live **separately** and that `run_cycle` is covered only by stubbed tests.

**BLK-2 — The timeout bound is not enforceable against the wrapper's children, and can itself hang.**
`agent_launcher.py:71` uses `subprocess.run(..., timeout=timeout_seconds + 15)` with no `start_new_session`/process-group handling. On expiry Python kills only the direct child (the wrapper shell); a `codex`/`claude` process spawned without `exec` survives and keeps inheriting the stdout/stderr pipes, so the post-kill `communicate()` in `subprocess.run` blocks with no timeout — `launch()` never returns, and the live external model call keeps running unbounded. This defeats the "bounded timeout" claim (`EVIDENCE.md:9`) and acceptance criterion `TASK_PACKET.md:47`. The timeout branch (`agent_launcher.py:75-79`) also has **zero** test coverage, so the `timed_out=True` / `exit_code=124` path has never executed.
*Remediation:* replace `subprocess.run` with `Popen(..., start_new_session=True)`; on `TimeoutExpired` call `os.killpg(os.getpgid(p.pid), SIGTERM)`, then `SIGKILL` after a short grace, and bound the final `communicate()`. Add a test with a wrapper that backgrounds a long-lived child and asserts `status=="FAILED"`, `timed_out is True`, and that `launch()` returns within the bound.

---

## MAJOR

**MAJ-1 — Failures after a successful launch leave no durable cycle record.** `live_review_cycle.py:58-63`: if `extract_claude_verdict` raises, or the validator/projection/policy rejects the verdict, the exception propagates and `cycle-result.json` is never written (`:73` is unreachable). The only cycle-level record is the JSON printed to stdout by `main()` (`:89-91`), which is not durable. This is the single most likely real-world outcome — a Claude reply that parses as JSON but fails the contract. Fail-closed holds; "remains auditable" (`TASK_PACKET.md:47`) does not at the cycle layer.
*Remediation:* wrap `:48-64` and write `cycle-result.json` with `status: "FAILED_ADMISSION"` plus the error type/message before re-raising.

**MAJ-2 — `extract_claude_verdict` accepts an arbitrary envelope as the verdict.** `agent_launcher.py:110`: when the envelope is a dict **without** a `result` key, `payload` becomes the envelope itself and is written out as the verdict (`:118`). A wrapper error document such as `{"error":"timeout","code":124}` is admitted as a verdict rather than rejected. The envelope's own `is_error`/error-subtype fields are likewise never checked, so an aborted run that still exits 0 passes admission. The downstream validator is the only thing that stops it — which is exactly the fail-closed layering "exact JSON admission" is supposed to add.
*Remediation:* require the documented envelope shape — reject when the top-level object lacks `result`, and raise `LaunchError` when a truthy `is_error` is present. Add tests for both.

**MAJ-3 — The "fixed/allowlisted argv" property is only a default.** `agent_launcher.py:40` `wrapper_override` accepts any executable path with no allowlist check (`:59-61` validates only that it is executable), and `live_review_cycle.py:27` re-exports the same seam. `project_root` (`:44-46`) is likewise unbounded — the live Claude run used the entire workspace root as its scope. Any in-process caller can therefore launch an arbitrary binary against an arbitrary tree through the audited launcher, and the resulting `launch-result.json` looks identical to an approved run.
*Remediation:* validate the resolved override against an explicit `ALLOWED_WRAPPERS` set (or gate it behind a tests-only sentinel), and require `project_root` to resolve under an approved root; record in `launch-result.json` whether the wrapper was the default or an override.

**MAJ-4 — The audit chain from launch to admitted verdict is not digest-linked.** `agent_launcher.py:94-96` digests the prompt, stdout, and stderr — but not `wrapper-output.json`, the file that actually carries the verdict for the Claude role (`:66`). `extract_claude_verdict` (`:102-119`) writes the extracted verdict with no record of source path, source digest, or output digest. Nothing ties the runner's `input-review_verdict` digest back to the launch evidence.
*Remediation:* add `wrapper_output_digest` to the result when the file exists, and have `extract_claude_verdict` emit a `verdict-extraction.json` recording source path/digest and output digest.

**MAJ-5 — Verification claims are stale and do not describe the shipped tree.** `EVIDENCE.md:33-34` reports "35/35 passed" for a state explicitly labelled *before final cleanup*, and no post-cleanup result is recorded; `py_compile` (`:35`) does not say which files. `TASK_PACKET.md:50` expects "14 integration and 84 core tests". The shipped tree contains 14 methods in `test_integration.py`, 5 in `test_agent_launcher.py`, and 2 in `test_live_review_cycle.py` (21), so no reported number corresponds to the delivered code. Separately, `TASK_PACKET.md:33-41` still shows every checklist item after the first unchecked while `EVIDENCE.md:3` claims `IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW`.
*Remediation:* re-run `python3 -m unittest discover -s tests` and the core suite on the final tree, record exact counts and the `py_compile` file list, and sync the checklist.

**MAJ-6 — Sandbox-scope claim is broader than what was proven.** `EVIDENCE.md:23-24` states "No Synology, memory, config, secrets, customer data … was involved." `runs/claude-smoke-01/launch-result.json` shows `project_root` was `/home/stanislav/.openclaw/workspace/agents/main` — the whole workspace, read-only. The evidence can honestly assert only that the *prompt inputs* were synthetic; the reviewer's read scope included memory and config directories.
*Remediation:* narrow the sentence to prompt inputs and state the actual project scope, or re-run the smoke with a narrowed `project_root`.

**MAJ-7 — Test gaps beyond BLK-2.** No test asserts the Claude argv shape (only codex, `tests/test_agent_launcher.py:34`), so the five-positional wrapper contract at `agent_launcher.py:66` is unverified by anything except the un-inspectable wrapper. Also untested: unsupported `role` (`:42`), non-directory `project_root` (`:45`), missing `wrapper-output.json` (`:105`), the MAJ-2 envelope case, and `run_cycle`'s path-escape rejection (`live_review_cycle.py:52`).
*Remediation:* add the argv assertion plus one test per rejection branch.

---

## NITS

- **N-1** `live_review_cycle.py:51-54` checks `is_absolute()`/`".."` but never resolves and re-checks containment, unlike `local_orchestrator_runner.py:64-66`. A symlinked input dir lets the generated verdict be written outside the bundle directory before the runner's stricter check aborts the run. Mirror the `is_relative_to(base)` check.
- **N-2** `agent_launcher.py:71` — an `OSError` from `subprocess.run` (`E2BIG` on a large codex prompt, ENOENT race) escapes uncaught after `run_dir` and the prompt exist, leaving a run directory with no `launch-result.json`. Catch it and write a `FAILED` result.
- **N-3** `live_review_cycle.py:57` creates parent directories outside `cycle_root` that are never removed, and `:64` deletes a file in the caller's bundle tree. Side effects outside the single-use directory should at least be listed in `cycle-result.json`.
- **N-4** `README.md:74-76` — the `py_compile` line omits `agent_launcher.py` and `live_review_cycle.py`; `README.md:19-20` mentions only `tests/test_integration.py`; there is no CLI usage block for `live_review_cycle.py` although one exists for the runner (`:61-65`).
- **N-5** `agent_launcher.py:64` passes the codex prompt as an argv element, making it visible in `ps` to any local process and subject to `ARG_MAX`. The Claude role already uses a file (`:66`); consider the same for codex if the wrapper supports it.
- **N-6** `tests/test_live_review_cycle.py:15` constructs `test_integration.LocalIntegrationTests` with a hardcoded `methodName` as a fixture helper, and depends on that module's import side effect for `sys.path`. Extract the fixture builders instead.
- **N-7** `agent_launcher.py:81-82`, `:98` — `stdout.log`, `stderr.log`, and `launch-result.json` are left writable while `input-prompt.md` is `0o444` (`:56`); immutability is applied inconsistently. Also `:68`/`:80` use `time.time_ns()` (wall clock) for `duration_ms`; `time.monotonic_ns()` is the right source.

---

The spec axis holds in its core shape — no shell-string evaluation of task content, single-use run and cycle directories, failed launch yields `decision: None` with no policy invocation (`live_review_cycle.py:37-46`, covered by `tests/test_live_review_cycle.py:50-61`), and the accepted validator/projection/policy remains the only decision authority (`local_orchestrator_runner.py:76-85`, reached unchanged via `:60`). The blockers are that the integrated path was never proven live despite evidence implying otherwise, and that the execution bound protecting the live call is unenforced and untested.

LIVE_LAUNCH_REWORK
