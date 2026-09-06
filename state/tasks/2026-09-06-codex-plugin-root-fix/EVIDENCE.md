# Evidence: Codex plugin root fix

Status: SUCCEEDED

## Installed plugin

- Version: `2026.9.2`
- Status: `loaded`
- Discovery source: `openclaw plugins list --json`, field `rootDir`
- Resolved root: `/home/stanislav/.openclaw/npm/projects/openclaw-codex-8902d781d4__openclaw-generation__g-e2e0de3303206c53/node_modules/@openclaw/codex`

## Change

- `scripts/codex-account-limit-switch.mjs` now resolves the active Codex plugin from the OpenClaw plugin registry.
- Legacy project-directory scanning remains as a compatibility fallback.
- The script registers the resolved plugin root before starting the managed Codex app-server, as required by 2026.9.2.

## Verification

- `node --check scripts/codex-account-limit-switch.mjs`: PASS.
- Focused limit probe: PASS for both configured OAuth profiles.
- Probe with `OPENCLAW_NPM_PROJECTS_DIR=/nonexistent/legacy-codex-projects`: PASS, proving registry discovery is primary.
- Primary profile: 5h remaining 85%; weekly value not exposed.
- Secondary profile: 5h remaining 100%; weekly remaining 84%.
- Active order first: primary profile; no switch needed.
- Full `scripts/heartbeat-token-limits.sh` reached and passed the two-profile Codex probe. Its final exit was 1 only because the separate historical log matcher classified `agent-turn-timing` lines as new `model_fallback` events.
- `git diff --check -- scripts/codex-account-limit-switch.mjs`: PASS.

## Safety and archive

- Pre-change snapshot: `codex-account-limit-switch.mjs.before`.
- Full heartbeat output: `heartbeat-token-limits.log`.
- No outbound queue rows were changed, deleted, replayed, or delivered.
- No OAuth order was changed; auto-switch remained disabled.
