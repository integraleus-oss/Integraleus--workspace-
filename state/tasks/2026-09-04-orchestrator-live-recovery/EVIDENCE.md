# Evidence

Status: SUCCEEDED
Last verified: 2026-09-04T14:02:06+03:00

## Checklist

- [x] Isolated worktree and R20 preservation verified.
- [x] Pre-change backups verified.
- [x] Stable source restore verified.
- [x] Gateway and Telegram verified.
- [x] Legacy records repaired and recovery logs quiet.

## Result

- R20 preserved in `/home/stanislav/agent-runs/managed-program-r20-isolated` on branch `managed-program-r20-isolated`; its worktree contains the full uncommitted R20 patch.
- Pre-repair legacy files are preserved under `backup/`; state backups use the `.json.bak` suffix so the live recovery scanner cannot execute them.
- Live `execution-supervisor.py`, `managed-agent-runner.mjs`, plugin `index.js`, and plugin manifest match commit `92ee5436` byte-for-byte. The live orchestrator path has no Git diff.
- Gateway restarted cleanly at 2026-09-04T13:59:19+03:00 and is running as systemd user service PID 49766.
- `openclaw status --deep`: Gateway reachable, event loop healthy, Telegram `OK` for 2/2 accounts.
- The last recovery failure was at 2026-09-04T14:00:57+03:00 and targeted a backup filename. After renaming backup state files, the log remained unchanged through 2026-09-04T14:02:06+03:00.
- `drill-current` restored to `SUCCEEDED`, exit code `0`, original success notification ID; false `CRASHED` outbox event removed.
- `drill-alpha-bpr` restored to `SUCCEEDED`, exit code `0`, success notification marked delivered; false `CRASHED` outbox event removed and evidence corrected.
- JSON assertions passed for both states/outboxes; neither outbox contains a `CRASHED` event.
- No standalone `execution-supervisor.py` or `managed-agent-runner.mjs` process is active; recovery is performed by the Gateway plugin.
- Repository HEAD remains `92ee5436`; no commit was created during containment.
