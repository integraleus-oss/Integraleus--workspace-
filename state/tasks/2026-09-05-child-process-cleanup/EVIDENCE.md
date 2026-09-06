# Evidence — child process cleanup

## Result

Completed at 2026-09-05T16:24:15+03:00.

- Four orphan Codex app-server trees were terminated with `SIGTERM` by exact
  process-group ID: `3369531`, `3369888`, `3370651`, `3370657`.
- The active turn tree was preserved: `3369882 -> 3369896 -> 3405159`.
- The standalone, user-owned interactive Claude CLI (`3257075`) was preserved.
- App-server parent count fell from 5 to 1 and did not respawn during the
  verification interval.
- Gateway remained active (`MainPID=3293285`) throughout; no restart occurred.
- Deep health check after cleanup: Gateway reachable, event loop OK, Telegram
  OK. The pre-existing dead-letter warning is unrelated.
- Gateway cgroup memory fell immediately from 1,211,949,056 to 1,084,653,568
  bytes. Later measurements during this active tool-heavy turn are not a valid
  idle baseline because its MCP processes remain live until turn completion.

## Root cause and prevention

Journal evidence showed heartbeat selecting unsupported `openai/gpt-5.4`,
rotating both profiles, attempting fallback, and then being superseded by a new
session writer. The superseded run did not reap four app-server trees.

Applied live configuration:

`agents.entries.main.heartbeat.model = openai/gpt-5.6-sol`

`openclaw config validate` passed and OpenClaw reported that no Gateway restart
was required. The stale auto-failover instruction in `HEARTBEAT.md` was updated
to the same supported model.

## Remaining product defect

OpenClaw still needs a lifecycle regression test/fix ensuring a superseded or
aborted Codex run closes its app-server process tree. The operational trigger
seen here is removed, but forced interruption could expose the generic cleanup
defect again. No public issue or upstream push was made.
