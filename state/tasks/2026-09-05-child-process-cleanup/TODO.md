# Child process cleanup

- Owner: main
- Started: 2026-09-05T16:22:10+03:00
- Execution: current foreground Telegram turn
- Expected output: classify Codex/Claude children, terminate only proven-orphaned processes, verify memory and recurrence
- Failure mode: stop without killing if ownership/activity cannot be proven

## Checklist

- [x] Capture Gateway/cgroup/process baseline
- [x] Map app-server processes to live turns/sessions
- [x] Gracefully stop proven orphans
- [x] Verify Gateway, Telegram, process count, and memory
- [x] Correct invalid heartbeat model override and legacy failover instruction
- [x] Record evidence and remaining product fix

## Baseline

- Gateway PID: 3293285
- Gateway cgroup memory: 1,211,949,056 bytes
- Codex app-server parents: 5 (started 16:12:54–16:12:59)
- Standalone Claude CLI PID: 3257075 (outside Gateway cgroup; possibly user-owned interactive terminal)

## Findings

- Only `agent:main:main` was active; no subagents/background runs were active.
- Current turn tree: `3369882 -> 3369896 -> 3405159`.
- Orphan app-server parents terminated gracefully: `3369531`, `3369888`,
  `3370651`, `3370657`.
- Trigger: heartbeat override selected unsupported `openai/gpt-5.4`, causing
  profile rotation/fallback; the run was then superseded by a new inbound turn
  without cleaning its app-server trees.
- Config changed live to `agents.entries.main.heartbeat.model =
  openai/gpt-5.6-sol`; `openclaw config validate` passed.
