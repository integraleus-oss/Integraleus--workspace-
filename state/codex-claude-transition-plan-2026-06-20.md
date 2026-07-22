# Codex / Claude CLI Transition Plan - 2026-06-20

## Status

- Preparation started.
- Current Termius sessions must not be touched during preparation.
- No Codex/Claude process has been stopped, restarted, attached, or sent input by this plan.

## Installed / Available

- `tmux`: present at `/usr/bin/tmux`, version 3.4.
- `python3`: present at `/usr/bin/python3`, version 3.12.3.
- No package installation was needed for the safe preparation phase.

## Base Created

- `/home/stanislav/agent-runs/README.md`
- `/home/stanislav/agent-runs/_templates/TASK.md`
- `/home/stanislav/agent-runs/_templates/STATUS.md`
- `/home/stanislav/agent-runs/_templates/HANDOFF.md`
- `/home/stanislav/agent-runs/_templates/events.jsonl`
- `/home/stanislav/agent-runs/_locks/README.md`
- `/home/stanislav/agent-runs/_dashboard/README.md`
- `/home/stanislav/agent-runs/_dashboard/server.py`
- `/home/stanislav/agent-runs/_bin/agent-task`
- `/home/stanislav/agent-runs/2026-06-20-alpha-bpr-coordination/`
- `/home/stanislav/agent-runs/_locks/alpha-bpr.lock`

## Safe Transition Plan

1. Keep existing Termius sessions running until they reach a natural checkpoint.
2. Do not send keystrokes to current Codex/Claude sessions during preparation.
3. Create task ledger folders before launching any new supervised task.
4. Use `agent-task init <project-path> <slug>` to create a task folder.
5. Record current state in `TASK.md`, `STATUS.md`, and `HANDOFF.md`.
6. Add a writer lock in `_locks/` before allowing any agent to edit a project.
7. Start future Codex from the project root, for example:
   `codex -C /home/stanislav/projects/alpha-bpr`
8. Start future Claude from the project root, for example:
   `cd /home/stanislav/projects/alpha-bpr && claude`
9. Add internal tmux runner only after task ledgers and locks are proven useful.
10. Add read-only dashboard before adding any control buttons.

## Risk Controls

- Termius remains fallback/admin access.
- Existing direct Synology exchange remains valid, but important messages should be mirrored into `HANDOFF.md`.
- One project has one writer.
- The reviewer can inspect and propose, but not edit.
- Dashboard v1 is read-only.
- Pause/stop buttons are deferred until observation is reliable.

## Next Safe Step

Review the first task ledger for the current Alpha BPR coordination work:

```bash
/home/stanislav/agent-runs/_bin/agent-task status /home/stanislav/agent-runs/2026-06-20-alpha-bpr-coordination
```

Then decide when the current Termius sessions have reached a safe checkpoint. Only after that should the next Codex/Claude runs move into supervised mode.
