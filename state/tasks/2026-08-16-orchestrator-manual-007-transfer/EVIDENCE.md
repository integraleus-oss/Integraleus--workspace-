# Manual-007 source-transfer evidence

Status: COMPLETE

## Result

- Source baseline was clean at
  `f25e00150258eba2ea89146dfe114c758d462309`.
- Accepted `observed.diff` SHA-256 was rechecked as
  `797e4e7406f3dae3c6134275881fd3ee512906e40c0921b3b3c7e4ae58142295`.
- Exactly `schemas/run-log.schema.json`, `src/core/run-log.js`, and
  `test/run-log.test.js` were transferred.
- All three target files matched their accepted detached-worktree versions
  byte-for-byte before commit and again after commit.
- Target file SHA-256 values:
  - `schemas/run-log.schema.json`:
    `7379c15c942cc57fad4f55677d34136f503ddb1aaaa5b304539025c8e8c15f3e`;
  - `src/core/run-log.js`:
    `2bf6d160897f02744e52474fb409c4b0e884cc0790c80cd348315f7c3de9d162`;
  - `test/run-log.test.js`:
    `b92d8fff01511b2d7b69ac2bfd72bfff04f1a193a7f3fe8ef2747e8b70031168`.
- `npm test`: 33/33 passed.
- `git diff --cached --check`: PASS. Staging exactly the three allowed paths
  ensured the new test file was included in the whitespace check.
- Local source commit:
  `8985b8e95427c471662562afa1b89a9e5b17a6a0` (`fix: harden run log contract`).
- Source worktree was clean after commit.
- No push, deploy, Gateway/runtime/config, cron, systemd/daemon, unattended,
  dependency, network, Synology, or external-system change was performed.
