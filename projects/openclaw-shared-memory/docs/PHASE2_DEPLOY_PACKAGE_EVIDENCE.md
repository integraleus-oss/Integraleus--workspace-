# Evidence: Phase 2 Deploy Package

Status: ready
Date: 2026-07-23
Task packet: `docs/PHASE2_PREP_TASK_PACKET.md`

## Summary

- Phase 2 preparation builds and verifies a self-contained Synology deploy
  package without changing Synology, OpenClaw runtime, MCP config, or real
  memory state.

## Files Created Or Changed

- `deploy/synology/ROLLBACK.md` - rollback procedure for the future approval-gated Synology pilot.
- `scripts/package_synology_deploy.sh` - includes rollback, archive, checksum, explicit bind guard, and wildcard bind rejection.
- `docs/PHASE2_DEPLOY_PACKAGE_EVIDENCE.md` - this evidence file.
- `docs/PHASE3_APPROVAL_REQUEST.md` - exact approval request for future Synology deployment.
- `TODO.md` - updated Phase 2 prep checklist.
- `deploy/synology/README.md`, `deploy/synology/RUNBOOK.md`, and `docs/PHASE3_APPROVAL_REQUEST.md` - clarified local-network-only boundary: LAN-first, VPN only as a private route into the home LAN.

## Commands Run

```bash
git status --short --branch -- projects/openclaw-shared-memory DECISIONS.md STATE.md
sed -n '1,260p' projects/openclaw-shared-memory/scripts/package_synology_deploy.sh
sed -n '1,260p' projects/openclaw-shared-memory/deploy/synology/CHECKLIST.md
sed -n '1,260p' projects/openclaw-shared-memory/deploy/synology/README.md
scripts/package_synology_deploy.sh
find dist/synology-openclaw-shared-memory -maxdepth 3 -type f -printf '%P\n' | sort
tar -tzf dist/synology-openclaw-shared-memory.tar.gz | sort
cd dist && sha256sum -c synology-openclaw-shared-memory.tar.gz.sha256
rg -n "POSTGRES_PASSWORD=.*[^<>]$|OPENCLAW_MEMORY_BIND_HOST=0\.0\.0\.0|sk-[A-Za-z0-9]|BEGIN (RSA|OPENSSH|PRIVATE)|api[_-]?key\s*=|token\s*=" dist/synology-openclaw-shared-memory deploy/synology docs/PHASE3_APPROVAL_REQUEST.md
tar -tzf dist/synology-openclaw-shared-memory.tar.gz | rg '(^|/)\.env$|\.dump|\.age|\.db|session|secret|token|key'
.venv/bin/python -m pytest
.venv/bin/python -m compileall src scripts
bash -n scripts/package_synology_deploy.sh scripts/run_phase1_pilot_checks.sh
git diff --check -- projects/openclaw-shared-memory
```

Result:

- Phase 1.5 project commit exists as `4bee741`.
- `DECISIONS.md` and `STATE.md` contain approved memory updates and are dirty outside the project commit.
- No Synology/runtime/MCP/real-memory action was performed.
- Package folder: `dist/synology-openclaw-shared-memory/`.
- Archive: `dist/synology-openclaw-shared-memory.tar.gz`.
- Checksum: `dist/synology-openclaw-shared-memory.tar.gz.sha256`.
- Package files: `.env.synology.example`, `CHECKLIST.md`, `README.md`, `ROLLBACK.md`, `RUNBOOK.md`, `docker-compose.yml`, `migrations/001_initial_schema.sql`, `migrations/002_hardening.sql`.
- Archive also contains empty runtime directories: `backups/`, `data/`, `mirror/`.
- Checksum verification passed: `synology-openclaw-shared-memory.tar.gz: OK`.
- Secret scan found no actual `.env`, dumps, encrypted backups, db files, sessions, secrets, tokens, API keys, private keys, wildcard bind values, or non-placeholder password assignments in the package/archive.
- Network boundary is recorded as local-network-only. Default bind remains LAN `192.168.68.103`; VPN may be enabled only as a private route into the home LAN and does not imply public exposure.
- `pytest`: 2 passed.
- `compileall`: passed for `src` and `scripts`.
- `bash -n`: passed for package and Phase 1 pilot runner scripts.
- `git diff --check -- projects/openclaw-shared-memory`: passed.

## Checks

- [x] package generated
- [x] package contents inspected
- [x] archive generated
- [x] checksum generated
- [x] no secrets in package/archive listing
- [x] no wildcard bind in compose
- [x] rollback included
- [x] `pytest`
- [x] `compileall`
- [x] `bash -n`
- [x] `git diff --check`

## Review

- Reviewer: main self-review
- Review artifact: `docs/PHASE2_AUDIT_PACKET.md`
- Verdict: GO

## Approval Evidence

- Approval source: Telegram topic `HOME:1751`, 2026-07-23 14:10 MSK
- Approved action: Phase 2 prep package and approval request only
- Explicitly blocked: Synology deployment until Stanislav says "разворачивай на Synology"

## Residual Risks

- Phase 3 deployment commands have not been executed.
- Runtime/MCP registration remains future work and requires explicit approval.

## Handoff

- Use `docs/PHASE3_APPROVAL_REQUEST.md` as the exact approval packet for deployment.
