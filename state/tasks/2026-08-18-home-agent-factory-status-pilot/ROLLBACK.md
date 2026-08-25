# Rollback

If the second-account login fails or must be reverted:

1. Stop any active local Codex process.
2. Restore `/home/stanislav/.codex/auth.json` from `/home/stanislav/.codex-backups/local-switch-20260818-2008/auth.json` without displaying its contents.
3. Run `/home/stanislav/.local/bin/codex-local login status`.
4. Do not modify OpenClaw auth order, Gateway, or agent Codex homes.
