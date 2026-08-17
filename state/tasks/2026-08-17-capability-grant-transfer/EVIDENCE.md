# Evidence

Status: COMPLETE

- Authorization: Telegram topic 2922, message 3343, `Переносим.`
- Source worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/manual-pilot-001-capability-grant`
- Target repository: `/home/stanislav/projects/home-agent-factory`
- Allowed files: `src/core/policy.js`, `schemas/capability-grant.schema.json`, `test/policy.test.js`
- Accepted diff digest: `5b29fb1e2a91f34c9a1c01c8ae04734a4f289ab4dcc29ecaff07e8e8dcf17fa2`
- Target pre-transfer HEAD: `8985b8e95427c471662562afa1b89a9e5b17a6a0`
- Target pre-transfer status: clean
- Target changed paths before commit: exactly the three allowed files
- Target transferred diff digest: `5b29fb1e2a91f34c9a1c01c8ae04734a4f289ab4dcc29ecaff07e8e8dcf17fa2` — exact match
- `git diff --check`: PASS
- `npm test`: PASS, 48/48
- Target commit: `3b21d0d` (`feat: align capability grant runtime and schema`)
- Target post-commit status: clean
- Push/deploy/Gateway/systemd/plugin/background activity: none
- Unrelated household-block files in the workspace were not touched.
