# OpenClaw Shared Memory TODO

Status date: 2026-07-22

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
- [ ] Before Phase 2: make backup login BYPASSRLS provisioning explicit in Synology/deploy runbook
- [ ] Before Phase 2: tighten Phase 1 negative tests to assert expected error types
- [ ] Before Phase 2: fold mirror/backup/restore/container-stop checks into an automated pilot runner
- [ ] Phase 1.5: create project-specific Agent Workflow brief
- [ ] Phase 1.5: create Phase 2 task packet, security precheck, audit packet, and evidence note
- [ ] Phase 1.5: keep Skill Workshop proposal pending unless explicitly approved
- [ ] OpenClaw MCP registration wired into runtime config
- [ ] Existing MEMORY.md/STATE.md/DECISIONS.md imported after owner review
- [x] Restore drill run against a disposable database
- [ ] Owner approval recorded before replacing current memory workflow

## Boundaries

- This project is infrastructure only. It does not change current OpenClaw runtime config.
- Current markdown memory remains the source used by agents until migration is explicitly approved.
- No Synology data is imported or exported by default.
- No memory entry is promoted to shared canon without an explicit reason, source, scope, and privacy class.
