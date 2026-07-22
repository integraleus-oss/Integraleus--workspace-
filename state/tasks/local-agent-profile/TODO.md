# Lightweight local OpenClaw agent - 2026-07-07

## Goal

Create a small local-agent profile for private/emergency local tasks using Ollama,
short bootstrap, `thinking off`, and minimal tools.

## Checklist

- [x] Inspect current OpenClaw agent/profile layout.
- [x] Choose the least invasive config path.
- [x] Create or configure a lightweight local agent.
- [x] Set local model to an Ollama model and disable thinking.
- [x] Limit tools/bootstrap where supported.
- [ ] Run smoke prompt through the local agent.
- [ ] Run one practical private/emergency prompt.
- [ ] Document exact usage command.

## Notes

- Do not remove or rewrite the existing `main` agent.
- Keep Synology/private-data guardrails intact.
- Prefer CLI-supported config changes over manual JSON edits.
