# T01 — pack slug boundary

- Source: `/home/stanislav/projects/home-agent-factory`
- Commit: `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`
- Worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t01-pack-slug`
- Allowed: `src/cli/factory.js`, `test/cli.test.js`
- Forbidden: every other project path; source worktree; secrets; dependencies;
  commit, push, deploy, Gateway, cron, services, system state.
- Result: reject traversal/absolute/separator/empty/malformed pack slugs before
  reading outside `agent-packs`; preserve valid list/show.
- Checks: `npm test`; pack list; valid pack show; `git diff --check`.
- Time: 600 s per agent, 60 s per gate.
- Attempts: at most 2 Codex implementation legs and 1 Claude final-full
  review-only leg; bounded reviewer repair as implemented by release.
- Stop: boundary breach, unknown/repeated infra, timeout, invalid evidence,
  digest/seal failure, exhausted repair, or operator interrupt.
- Commit: forbidden. Push/deploy: forbidden.
