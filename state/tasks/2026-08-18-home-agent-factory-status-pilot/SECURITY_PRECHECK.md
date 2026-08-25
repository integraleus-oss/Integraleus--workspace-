# Local Codex account switch precheck

- Owner authorization: Telegram message 3387, "Переключи на другой аккаунт".
- Scope: local/default Codex CLI under `/home/stanislav/.codex` only.
- OpenClaw agent auth profiles and Gateway configuration: out of scope and unchanged.
- Secrets: never print or copy into task artifacts/chat.
- Backup target: `/home/stanislav/.codex-backups/local-switch-20260818-2008/`.
- Verification: `codex-local login status` plus a one-word read-only smoke.
- Pilot continuation: new single-use run root; no reuse of the failed run directory.
