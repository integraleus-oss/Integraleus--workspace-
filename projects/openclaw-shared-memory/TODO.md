# OpenClaw Shared Memory TODO

Status date: 2026-07-24

## Checklist

- [x] Project folder created
- [x] Architecture README created
- [x] Postgres + pgvector docker-compose added
- [x] Canonical schema migration added
- [x] App config and env example added
- [x] MCP-style server skeleton added
- [x] Memory proposal/promote/search/supersede workflows added
- [x] Markdown mirror export script added
- [x] Backup and restore drill scripts added
- [x] Basic validation script added
- [x] Implementation plan created
- [x] Claude plan audit completed
- [x] Implementation plan v2 created
- [x] Visual architecture/data-flow diagram created
- [x] First local Postgres instance started
- [x] Migration applied to a disposable local database
- [x] Phase 0 hardening patch implemented
- [x] Phase 0 DB-backed safety tests implemented
- [x] Phase 0 hardening evidence note created
- [x] Phase 1 disposable local DB pilot implemented
- [x] Phase 1 role-scoped login user pilot verified
- [x] Phase 1 local pilot evidence note created
- [x] Unified Agent Workflow / Shared Memory development plan created
- [x] Claude audit for unified plan completed
- [x] Unified plan fixes from Claude audit applied
- [x] MCP tool contract updated after Phase 0/1 hardening
- [x] Before Phase 2: make backup login BYPASSRLS provisioning explicit in Synology/deploy runbook
- [x] Before Phase 2: tighten Phase 1 negative tests to assert expected error types
- [x] Before Phase 2: fold mirror/backup/restore/container-stop checks into an automated pilot runner
- [x] Phase 1.5: create project-specific Agent Workflow brief
- [x] Phase 1.5: create Phase 2 task packet, security precheck, audit packet, and evidence note
- [x] Phase 1.5: keep Skill Workshop proposal pending unless explicitly approved
- [x] Phase 2: add Synology rollback artifact to deploy package
- [x] Phase 2: generate and inspect Synology deploy package archive
- [x] Phase 2: prepare exact Phase 3 approval request
- [x] Phase 2: record local-network-only boundary with VPN as private LAN route only
- [ ] Phase 3: Synology pilot deployment blocked because Docker/Container Manager is unavailable on Synology SSH preflight and not listed for DS218play in official DSM 7.3 package data
- [x] Phase 3: openclaw-home LAN pilot deployment
- [x] Phase 4 prep: read-only MCP/API gateway task packet, precheck, approval request, and preflight script prepared without runtime changes
- [x] Phase 4 runtime: read-only MCP/API gateway wiring approved and registered in OpenClaw `mcp.servers`
- [x] OpenClaw MCP registration wired into runtime config for read-only smoke tools
- [x] Phase 4 runtime: verify tool availability from a fresh agent turn after MCP reload
- [x] Phase 5 prep: controlled memory candidate import task packet, precheck, approval request, synthetic fixture, and dry-run planner
- [x] Phase 5 tiny candidate-write pilot: import max 3 approved `DECISIONS.md` Shared Memory entries as candidates only
- [x] Phase 5 manual promotion pilot: promote the 3 approved imported Shared Memory candidates
- [ ] Phase 5 candidate review/promotion decision: continue broader review only after separate approval
- [x] Phase 6 prep: inspect pending Agent Workflow skill proposal and prepare recommendation
- [ ] Phase 6 lifecycle action: revise/apply/reject/leave pending only after separate approval
- [ ] Existing MEMORY.md/STATE.md/DECISIONS.md imported after owner review
- [x] Restore drill run against a disposable database
- [ ] Owner approval recorded before replacing current memory workflow

## Boundaries

- This project is infrastructure only. It does not change current OpenClaw runtime config.
- Current markdown memory remains the source used by agents until migration is explicitly approved.
- No Synology data is imported or exported by default.
- No memory entry is promoted to shared canon without an explicit reason, source, scope, and privacy class.
- Phase 4 prep is documentation and read-only smoke verification only; it does not approve runtime wiring.
- Phase 4 runtime exposes only read-only MCP tools; write tools and real memory import remain blocked.
- Phase 5 prep is documentation and dry-run planning only; it does not approve write MCP exposure, DB candidate writes, real memory import, or promotion.
