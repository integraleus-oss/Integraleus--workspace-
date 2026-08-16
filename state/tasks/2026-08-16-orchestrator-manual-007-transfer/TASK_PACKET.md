# Manual-007 controlled source transfer

Status: COMPLETE

## Goal

Transfer the accepted manual-007 run-log hardening from its detached worktree
to the clean `home-agent-factory` source, verify exact file identity and repeat
the accepted checks, then create one local source commit and scoped evidence.

## Fixed points

- Source root: `/home/stanislav/projects/home-agent-factory`.
- Source baseline: `f25e00150258eba2ea89146dfe114c758d462309`.
- Accepted worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-007-run-log`.
- Accepted observed-diff SHA-256:
  `797e4e7406f3dae3c6134275881fd3ee512906e40c0921b3b3c7e4ae58142295`.
- Durable authorization: `D-2026-08-16-04` plus Stanislav's explicit
  instruction on 2026-08-16 to do the required next work.

## Allowed files

- `schemas/run-log.schema.json`
- `src/core/run-log.js`
- `test/run-log.test.js`

## Boundaries and stop conditions

- No other source paths may change.
- Stop on source drift, accepted-subject drift, file mismatch, failed test,
  whitespace error, unexpected process, or commit-scope mismatch.
- No push, deploy, Gateway/runtime/config, cron, systemd/daemon, unattended,
  dependency, network, Synology, or external-system change.

## Checks

- [x] Source baseline and cleanliness verified.
- [x] Accepted subject digest verified.
- [x] Exactly three files transferred.
- [x] Transferred files match accepted files byte-for-byte.
- [x] `npm test` passes 33/33.
- [x] Staged `git diff --check` passes, including the new test file.
- [x] Local source commit created and target tree clean.
- [x] Evidence committed separately in the orchestrator workspace.
