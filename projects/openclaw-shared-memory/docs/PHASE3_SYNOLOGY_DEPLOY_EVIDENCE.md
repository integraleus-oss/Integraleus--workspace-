# Evidence: Phase 3 Synology Pilot Deployment

Status: blocked at preflight
Date: 2026-07-23
Approval: Telegram topic `HOME:1751`, message at 2026-07-23 14:31 MSK

## Approved Scope

- Deploy OpenClaw Shared Memory pilot to Synology NAS.
- Bind Postgres to LAN IP `192.168.68.103`, port `55432`.
- Use disposable smoke records only.
- Run role, mirror, backup, restore, and connectivity checks.

## Explicitly Not Approved

- WAN/public exposure.
- Wildcard bind `0.0.0.0`.
- OpenClaw runtime/MCP changes.
- Real memory import.
- External review/send.
- Deleting Synology data.

## Files Created Or Changed

- `docs/PHASE3_SYNOLOGY_DEPLOY_EVIDENCE.md` - this deployment evidence.
- `docs/PHASE3_APPROVAL_REQUEST.md` - pending update with approval record.
- `deploy/synology/CHECKLIST.md` - pending update with pilot results.
- `TODO.md` - pending update after pilot verification.

## Commands Run

```bash
sed -n '1,260p' projects/openclaw-shared-memory/docs/PHASE3_APPROVAL_REQUEST.md
sed -n '1,260p' projects/openclaw-shared-memory/deploy/synology/RUNBOOK.md
git status --short --branch -- projects/openclaw-shared-memory DECISIONS.md STATE.md
ls -l projects/openclaw-shared-memory/dist/synology-openclaw-shared-memory.tar.gz projects/openclaw-shared-memory/dist/synology-openclaw-shared-memory.tar.gz.sha256
ping -c 3 -W 2 192.168.68.103
ssh -i ~/.ssh/id_ed25519_synology_openclaw -p 2222 -o BatchMode=yes -o ConnectTimeout=8 openclaw-admin@192.168.68.103 'hostname; id; uname -a; docker --version; docker compose version'
ssh -i ~/.ssh/id_ed25519_synology_openclaw -p 2222 -o BatchMode=yes -o ConnectTimeout=8 openclaw-admin@192.168.68.103 'test -e /volume1/docker/openclaw-shared-memory && ls -la /volume1/docker/openclaw-shared-memory || echo TARGET_MISSING'
ssh -i ~/.ssh/id_ed25519_synology_openclaw -p 2222 -o BatchMode=yes -o ConnectTimeout=8 openclaw-admin@192.168.68.103 'ss -ltnp 2>/dev/null | grep :55432 || true'
ssh -i ~/.ssh/id_ed25519_synology_openclaw -p 2222 -o BatchMode=yes -o ConnectTimeout=8 openclaw-admin@192.168.68.103 'command -v docker || true; command -v containerd || true; ls -l /usr/local/bin/docker /usr/bin/docker /var/packages/ContainerManager/target/usr/bin/docker /var/packages/Docker/target/usr/bin/docker 2>/dev/null || true'
ssh -i ~/.ssh/id_ed25519_synology_openclaw -p 2222 -o BatchMode=yes -o ConnectTimeout=8 openclaw-admin@192.168.68.103 'sudo -n true && echo SUDO_OK || echo SUDO_NEEDS_PASSWORD'
ssh -i ~/.ssh/id_ed25519_synology_openclaw -p 2222 -o BatchMode=yes -o ConnectTimeout=8 openclaw-admin@192.168.68.103 'sudo synopkg list --name 2>/dev/null | grep -Ei "Docker|Container|Virtual" || true'
ssh -i ~/.ssh/id_ed25519_synology_openclaw -p 2222 -o BatchMode=yes -o ConnectTimeout=8 openclaw-admin@192.168.68.103 'sudo synopkg status ContainerManager 2>/dev/null || true; sudo synopkg status Docker 2>/dev/null || true'
ssh -i ~/.ssh/id_ed25519_synology_openclaw -p 2222 -o BatchMode=yes -o ConnectTimeout=8 openclaw-admin@192.168.68.103 'sudo /usr/syno/bin/synopkg list 2>/dev/null | grep -Ei "Docker|Container|Virtual" || true'
curl -fsSL 'https://www.synology.com/api/support/findDownloadInfo?lang=en-us&product=DS218play&major=7&minor=3' | python3 -c '<package-list check>'
curl -fsSL 'https://archive.synology.com/download/Package/ContainerManager/24.0.2-1606/' | sed -n '1,80p'
```

Result:

- Approval packet and runbook reviewed.
- Package archive exists locally.
- Scoped project/memory state was clean before deployment.
- Synology `192.168.68.103` is reachable over LAN; ping 3/3 passed.
- SSH as `openclaw-admin` works; user is in `administrators`; passwordless sudo works.
- Host identifies as `S218`, Linux `synology_rtd1296_ds218play`.
- Target path `/volume1/docker/openclaw-shared-memory` does not exist yet.
- Port `55432` was not listening before deployment.
- `docker`, `docker compose`, and `containerd` were not found in the SSH shell or expected package paths.
- `synopkg` checks did not show Docker or Container Manager installed; only unrelated packages were returned by the filtered query.
- Synology Download Center API for `DS218play` / DSM 7.3 returned 64 packages; `ContainerManager` and `Docker` were not listed.
- Synology Archive contains a generic `ContainerManager-armv8-24.0.2-1606.spk`, but the official DS218play package list does not offer it for this model/DSM combination.
- A third-party workaround exists for installing Container Manager on excluded armv8 models, but using it would be an unsupported root/package-level change and is outside the approved Phase 3 deployment scope.
- No package was copied, no directory was created, no `.env` was written, and no container was started.

## Checks

- [x] Synology SSH reachable
- [ ] package copied: blocked
- [ ] package checksum verified on Synology: blocked
- [ ] `.env` created on Synology with LAN bind: blocked
- [ ] compose project started: blocked
- [ ] container healthy: blocked
- [ ] bind verified as LAN-only, no wildcard: blocked
- [ ] migrations/schema present: blocked
- [ ] LOGIN roles provisioned: blocked
- [ ] backup LOGIN has `BYPASSRLS`, other app LOGIN roles do not: blocked
- [ ] role-scoped smoke passed: blocked
- [ ] mirror allowlist passed: blocked
- [ ] backup passed: blocked
- [ ] restore drill passed against disposable DB: blocked
- [x] OpenClaw runtime/MCP unchanged
- [x] no real memory import
- [x] rollback path documented

## Residual Risks

- Synology deployment cannot proceed until an approved container runtime path exists.
- Official package data does not list Docker/Container Manager for DS218play on DSM 7.3.2.
- Installing Docker/Container Manager, including any manual SPK or third-party workaround, is a separate Synology package/root-level change and was not included in this approval.
- Because the deployment did not start, there is no running DB pilot yet.

## Handoff

- Current state is a documented blocker, not a partial deployment.
- Next step is to decide whether to approve installing/enabling a supported container runtime on Synology, choose another LAN host that already has Docker, or keep the project paused.
- Do not proceed to MCP/runtime wiring without separate approval.
