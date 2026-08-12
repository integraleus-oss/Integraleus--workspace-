## Targeted closure review — live-launch rework

Scope read: the four integration files, the two live-launch documents, plus `runs/live-cycle-r3/`, `runs/{codex,claude}-smoke-01/launch-result.json`, and `tests/test_integration.py` helpers as accepted context. Nothing else was opened. **I could not execute the suites — `python3` under Bash is denied in this session**, so all test-result claims below are read-verified, not run-verified.

### Blockers

**BLK-1 — CLOSED.** `runs/live-cycle-r3/` contains a real composed run: `claude-launch/{input-prompt.md,stdout.log,stderr.log,wrapper-output.json,launch-result.json,verdict-extraction.json}`, `policy-runs/real-claude-contract-smoke/`, and `cycle-result.json` with `status:"DECIDED"`, `outcome:"REWORK"`, `rule_id:"R11_OPEN_FINDINGS"`, `wrapper:/home/stanislav/agent-runs/_bin/claude-review`, `duration_ms:21721`. The generated verdict was unlinked as designed. `EVIDENCE.md:28-32` now describes this accurately and no longer implies the earlier smokes were end-to-end.

**BLK-2 — CLOSED.** `agent_launcher.py:73` uses `Popen(..., start_new_session=True)`; on `TimeoutExpired` it `killpg(SIGTERM)` → bounded `communicate(2)` → `killpg(SIGKILL)` → bounded `communicate(2)`, sets `timed_out=True`/`exit_code=124`, and re-attaches partial output without duplication (`:86-93`). `tests/test_agent_launcher.py:60-69` is a genuine regression: wrapper backgrounds a 3 s child, asserts return under 4 s, `("FAILED", True)`, and that the child's marker never appears. `duration_ms` now uses `monotonic_ns`.

### Majors

- **MAJ-1 — CLOSED.** `live_review_cycle.py:60-73` writes `cycle-result.json` with `status:"FAILED_ADMISSION"` plus error type/message before re-raising; `tests/test_live_review_cycle.py:61-71` asserts the durable record.
- **MAJ-2 — CLOSED.** `agent_launcher.py:131-134` rejects envelopes lacking `result` and any truthy `is_error`; both cases tested (`test_agent_launcher.py:87-93`).
- **MAJ-3 — CLOSED.** The `wrapper_override` seam is gone from both `agent_launcher.launch` and `live_review_cycle`; only the two module constants can be selected (`:52`). Residual (not blocking): `project_root` is still unrestricted to an approved root.
- **MAJ-4 — CLOSED and verified end-to-end.** `wrapper_output_digest` is recorded (`:116-118`) and `verdict-extraction.json` carries source path/digest and verdict digest (`:144-151`). In the live run the chain links: extraction `verdict_digest e8af5a78…` equals the runner's `input_digests.review_verdict e8af5a78…`.
- **MAJ-5 — CLOSED on counts, unverified on results.** `EVIDENCE.md:36-39` now states 26/26 integration and 84/84 core. 26 matches the shipped tree exactly (14 `test_integration` + 9 `test_agent_launcher` + 3 `test_live_review_cycle`), and the `TASK_PACKET.md` checklist is synced to the current gate. I could not run either suite, and the `py_compile` line still omits the file list (nit).
- **MAJ-6 — OPEN.** `EVIDENCE.md:19-24` still describes the two smokes without their model-visible scope and keeps the unqualified sentence "No Synology, memory, config, secrets, customer data, Gateway, systemd, GitHub, or push was involved." Both smokes ran with `project_root:/home/stanislav/.openclaw/workspace/agents/main` — the entire workspace repo, read-only — which is what the prior review asked to be disclosed or narrowed. Also `EVIDENCE.md:49` calls the r3 root "a narrow synthetic fixture root"; it was `state/tasks/2026-08-11-codex-claude-orchestrator/implementation`, real accepted code (narrow, but not a synthetic fixture). Fix is one edit: state the two smoke roots and the r3 root explicitly, and scope the categorical sentence to prompt inputs.
- **MAJ-7 — PARTIALLY CLOSED, not blocking on its own.** The key gap is fixed: `test_claude_argv_contract` pins the five-positional wrapper contract, plus a new absolute-path-across-`cd` test. Still untested: unsupported `role` (`:42`), non-directory `project_root` (`:45`), missing `wrapper-output.json` (`:125`), and `run_cycle`'s path-escape rejection (`live_review_cycle.py:51-56`, now correctly symlink-safe via `resolve()` + `is_relative_to`).

### One residual worth noting (minor)

`agent_launcher.py:84` — if the post-`SIGKILL` `communicate(timeout=2)` raises `TimeoutExpired`, it escapes uncaught (the outer handler catches only `OSError`), leaving a run directory with no `launch-result.json`. Same class as the earlier N-2; requires a grandchild that escaped the process group.

Only MAJ-6 remains open, and it is a documentation-accuracy fix, not a code change.

TARGETED_REWORK
