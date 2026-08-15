# SCADA Engineer Prompt Alpha Review

- [x] Receive and inspect original Markdown prompt.
- [x] Check current Alpha product naming against `docs/alpha_platform/PRODUCT_CHEATSHEET.md`.
- [x] Check HMI guidance against live `asu-tp-hmi-checklist`.
- [x] Write corrected prompt Markdown.
- [x] Verify corrected prompt for forbidden/outdated terms.
- [x] Send corrected Markdown back to Stanislav.
- [x] Accepted by Stanislav in Telegram.

Original inbound file:
`/home/stanislav/.openclaw/media/inbound/scada-engineer-prompt-alpha---57bc32ea-f771-4b78-99da-f01d946b140b.md`

Corrected file:
`/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-scada-engineer-prompt-alpha-review/scada-engineer-prompt-alpha-corrected.md`

Verification:
- `rg` check found deprecated names only inside the explicit "do not use as current component" warning.
- Confirmed current names: `Alpha.DevStudio`, `Alpha.HMI.WebViewer`, `Alpha.HMI.Alarms`, `alpha.hmi.charts`, `Alpha.Security`, `Alpha.Imitator`.
