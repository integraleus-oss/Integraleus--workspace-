# Task packet

- Goal: complete the five ordered OpenClaw reliability and hardening steps.
- Owner: main.
- Allowed files: heartbeat scripts/instructions, task evidence, archived delivery metadata, OpenClaw configuration through supported SecretRef tooling, and scoped source patches required by verified findings.
- Forbidden: replaying inbound dead letters, deleting outbound deduplication fences, printing or committing secrets, or sweeping unrelated dirty-worktree changes into commits.
- Checks: bounded heartbeat smoke, SQLite integrity/count checks, config validation, Gateway/Telegram deep health, doctor/security audit, and scoped Git review.
- Commit rule: separate scoped commits by concern; no unrelated files.
