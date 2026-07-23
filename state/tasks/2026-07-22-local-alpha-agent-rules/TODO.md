# Task Note: Local Alpha Agent Rules

Status: draft
Risk: MEDIUM
Owner: main agent
Date: 2026-07-22

## Use When

Create concise operating rules for a local weak model agent (`qwen3.5:4b` or `qwen3:8b`) that answers about Alpha Platform, tariff, licensing, presale inputs, and safe handoff boundaries.

Risk is MEDIUM because the document touches licensing, pricing boundaries, and product naming. It does not perform a customer calculation or send anything externally.

## Goal

- Produce a local-agent rules document that minimizes hallucinations and unsafe commercial answers.
- Ground rules in Alpha product and licensing sources.
- Keep the output usable as a system/developer prompt for a small local model.

## Scope

Allowed:

- Read Alpha product and licensing guardrail documents.
- Create draft files under this task folder.
- Create a pending Skill Workshop proposal for durable reuse.

Forbidden:

- final customer-facing TKP or pricing calculation;
- external sending;
- editing canonical `AGENTS.md`, `TOOLS.md`, `SOUL.md`, `MEMORY.md`, `STATE.md`;
- secrets, `.env`, credentials;
- production deploy/access/config changes;
- Synology root-level or DSM changes.

## Touched Files

- `state/tasks/2026-07-22-local-alpha-agent-rules/TODO.md`
- `state/tasks/2026-07-22-local-alpha-agent-rules/LOCAL_ALPHA_AGENT_RULES.md`
- `state/tasks/2026-07-22-local-alpha-agent-rules/LOCAL_ALPHA_AGENT_RULES_RU.md`
- `state/tasks/2026-07-22-local-alpha-agent-rules/EVIDENCE.md`

## Checks

- [x] Read `docs/alpha_platform/PRODUCT_CHEATSHEET.md`
- [x] Read `playbooks/PRESELL_FASTLANE.md`
- [x] Read `playbooks/EDGE_CASES.md`
- [x] Read `data/licensing_automiq/rules_hard_checks.md`
- [x] Create pending Skill Workshop proposal: `local-alpha-agent-rules-20260722-ff2d621a7b`
- [x] Run `git diff --check`

## Result

- Draft local-agent rules created.
- Russian canonical file created after user feedback.
- Pending Skill Workshop proposal created: `local-alpha-agent-rules-20260722-ff2d621a7b`.

## Next

- Optionally adapt the rules into the exact prompt/config format used by the local agent runtime.
