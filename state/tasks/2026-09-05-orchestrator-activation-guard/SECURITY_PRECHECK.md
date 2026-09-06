# Security precheck

- Risk: HIGH (Gateway/runtime/config activation).
- Human approval: present in Telegram topic 2922.
- Private/external data: no external review or external send planned.
- Secrets: do not print or commit tokens, auth profiles, `.env`, or protected signing material.
- Trust boundary: managed model stays in Docker with network disabled, read-only root, dropped capabilities, and no access to protected runtime state.
- Dirty worktree: unrelated changes exist and must remain untouched.
- Stop conditions: unexpected diff overlap, Telegram failure, recovery-loop, false terminal transition, sandbox escape, or inability to prove rollback.
