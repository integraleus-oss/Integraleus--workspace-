# T04 — run-log identifier boundary

- Source commit: `home-agent-factory` at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- Worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t04-run-log-id`.
- Allowed: `src/core/run-log.js`, `test/run-log.test.js`.
- Result: attacker-controlled run IDs cannot escape or alias files outside the
  dated audit directory; valid append-first JSONL behavior remains.
- Checks: `npm test`; `git diff --check`.
- Limits: 600 s agents, 60 s gates, maximum two Codex implementations plus one
  review-only final-full Claude leg.
- Standard stop conditions. Commit/push/deploy/external/system changes forbidden.
