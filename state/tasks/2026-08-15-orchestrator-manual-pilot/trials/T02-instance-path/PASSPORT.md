# T02 — instance path boundary

- Source: `/home/stanislav/projects/home-agent-factory`
- Commit: `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`
- Worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t02-instance-path`
- Allowed: `src/cli/factory.js`, `test/cli-instance.test.js`.
- Forbidden: all other paths and all external/system changes.
- Result: `--instance` must resolve inside the project and reject traversal,
  absolute, malformed, missing-value and symlink escape cases before reading.
- Checks: `npm test`; valid local run; `git diff --check`.
- Time: 600 s per agent; 60 s per gate. Attempts: 2 Codex maximum plus one
  review-only final-full Claude leg.
- Stop: standard pilot fail-closed conditions.
- Commit/push/deploy: forbidden.
