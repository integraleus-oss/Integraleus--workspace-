# Supervisor stale-admission repair evidence

Status: SUCCEEDED

- Owner: main
- Foreground mechanism: current Codex session
- Defect 1: a live `DISPATCHED` admission could keep blocking tools after its persisted supervisor state became terminal.
- Fix 1: `admissionForContext` now checks the trusted persisted state and evicts terminal admissions before applying the hook gate.
- Defect 2: trusted-context traversal aborted the runner when a directory disappeared between recursive scan steps.
- Fix 2: missing directories (`ENOENT`) are treated as an empty traversal step; other filesystem errors still fail closed.

## Verification

- `python3 scripts/test_execution_supervisor.py`: PASS, 22 tests.
- `node projects/execution-supervisor-taskflow/index.test.mjs`: PASS.
- `node scripts/managed-runner-fs.test.mjs`: PASS.
- `node scripts/managed-agent-runner.test.mjs`: PASS.
- `git diff --check`: PASS.
- `python3 scripts/test_execution_supervisor_recovery.py`: pre-existing FAIL because its fixture launches the supervisor without the now-required signed terminal result; unrelated to this patch.

## Live activation

- Runtime runner files match the workspace source, including `managed-runner-fs.mjs`.
- Gateway restarted cleanly at `2026-09-05T09:21:35+03:00` using `openclaw gateway restart`.
- New Gateway process: PID `793189`, systemd user service `active`.
- Startup log confirms `execution-supervisor-taskflow` among the five loaded plugins and `gateway ready`.
- Restart recovery resumed the interrupted main session: `recovered=1 failed=0 skipped=0`.
- `openclaw status --deep`: Gateway reachable, event loop healthy, Telegram `2/2` OK, plugin compatibility issues `none`.
- No `ERR_MODULE_NOT_FOUND` or Telegram `409 Conflict` appears in the post-restart log excerpt.

## Commit boundary

- Intended source patch: `projects/execution-supervisor-taskflow/index.js`, `projects/execution-supervisor-taskflow/index.test.mjs`, `scripts/managed-agent-runner.mjs`, `scripts/managed-runner-fs.mjs`, and `scripts/managed-runner-fs.test.mjs`.
- Evidence/checklist: this directory.
- The workspace contains unrelated pre-existing modifications and generated artifacts; none were reverted or included in a commit.
- Commit: not created in this recovery turn.
