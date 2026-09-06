# Evidence

Status: SUCCEEDED

## Baseline

- 2026-09-05 09:48 heartbeat ran inside a sandbox-only managed worker.
- The worker lacked host OpenClaw CLI, Node >=22.22.3, Python `cryptography`, and host session/config access.
- This produced a false host-regression diagnosis; supervisor code was not changed by that heartbeat.

## Worktree boundary

- Existing unrelated modifications and generated files were present before this task.
- In particular, current edits to supervisor/runner files belong to the preceding supervisor repair and will not be overwritten without inspection.

## Verification

- Root cause confirmed: `agents.defaults.heartbeat.every = 1h` was inherited by `managed-worker`, whose Docker sandbox lacks host CLI/module/session capabilities.
- Config schema confirms `agents.list[].heartbeat.every` is the supported per-agent override; OpenClaw documentation defines `0m` as disabled.
- Applied: `agents.list[3].heartbeat.every = 0m` for `managed-worker` only.
- `openclaw config validate`: PASS.
- Resolved config: `managed-worker.heartbeat.every = 0m`; default/main interval remains `1h`.
- The first restart exposed an OpenClaw scheduler-reconstruction edge case: with only the inherited default plus the new `managed-worker=0m` override, runtime logged `heartbeat: disabled` for all agents.
- Corrective config normalization applied: `agents.list[0].heartbeat.every = 1h` is now explicit for `main`; `agents.list[3].heartbeat.every = 0m` remains explicit for `managed-worker`.
- `openclaw config validate`: PASS after the final config change.
- Final clean restart completed at 2026-09-05 10:04:36 MSK. Gateway PID is `1064402` and the post-restart log records `gateway/heartbeat {"intervalMs":3600000} heartbeat: started`.
- `openclaw status --deep`: PASS for routing and health: `Heartbeat 1h (main), disabled (home-monitor), disabled (local), disabled (managed-worker)`; Gateway reachable; event loop healthy; Telegram 2/2 OK.
- Host-backed heartbeat command smoke: `execution-truth-watch.py` returned `EXECUTION_TRUTH_OK`; token/account checks read both Codex accounts and host sessions successfully; `openclaw status --deep` and `openclaw cron status` succeeded. This distinguishes the host-capable main environment from the 09:48 sandbox false positive.
- Recovery scan only repeated the three pre-existing 2026-09-01 fixture failures with `unsafe outboxPath`; these are unchanged historical test artifacts, not a regression from this fix.
- A manual `system event --mode now` wake was accepted (`{"ok":true}`), but `openclaw system heartbeat last` remained `null` while this foreground main-agent turn occupied the lane. Therefore evidence does not claim that a separate automatic tick completed during this turn; scheduler activation and routing are proven by resolved config, the post-restart startup log, `status --deep`, and the host-backed command smoke.

## Changed state

- Runtime config outside the repository: `~/.openclaw/openclaw.json`
  - `main.heartbeat.every = 1h`
  - `managed-worker.heartbeat.every = 0m`
- Task evidence only inside this repository: `state/tasks/2026-09-05-heartbeat-routing-fix/`.
- No unrelated dirty-worktree changes were overwritten or committed.

## Residual notes

- `Last heartbeat: none` is expected immediately after scheduler reconstruction until the first completed scheduled tick; next interval is one hour from the 10:04 startup.
- OpenClaw reports an available update and existing security warnings; both are outside this task.
