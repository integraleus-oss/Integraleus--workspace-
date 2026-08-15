# T03 — external-read method validation

- Source commit: `home-agent-factory` at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- Worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t03-external-methods`.
- Allowed: `src/core/policy.js`, `test/policy.test.js`.
- Result: malformed method values are rejected through a stable `PolicyError`;
  only GET remains allowed; valid behavior is preserved.
- Checks: `npm test`; `git diff --check`.
- Limits: 600 s agents, 60 s gates, maximum two Codex implementations plus one
  review-only final-full Claude leg.
- Standard stop conditions. Commit/push/deploy/external/system changes forbidden.
