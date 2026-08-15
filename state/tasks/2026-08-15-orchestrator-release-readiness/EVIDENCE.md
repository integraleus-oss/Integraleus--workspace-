# Release checkpoint evidence

Status: complete

## Planned checkpoint

- Branch: `main`
- Pre-release baseline: `73592bf`
- Release tag: `orchestrator-local-cli-r1-2026-08-15`
- Activation state: not activated

## Verification record

- Integration suite: 86/86 PASS (`7.549s`).
- Python compile: PASS after correcting the command's initial nonexistent
  filename from `production_cycle.py` to the real `production_cycle_cli.py`.
- `git diff --check`: PASS.
- Release checkpoint commit: `b300207cf33a7dfbf7de9312e38f67b39f9d4c67`.
- Annotated tag `orchestrator-local-cli-r1-2026-08-15` resolves exactly to the
  release checkpoint commit.
- Encrypted backup:
  `/mnt/synology/Documents/openclaw-backups/encrypted/openclaw-orchestrator-b300207-2026-08-15.tar.gpg`.
- Backup size: `604921096` bytes; file mode: `600`.
- Adjacent external SHA-256 file exists with mode `600`; checksum verification:
  PASS.
- Encryption: GPG symmetric AES-256; the recovery passphrase is stored locally
  at `/home/stanislav/.openclaw/secrets/orchestrator-release-backup.passphrase`
  with mode `600` and is not committed or copied into the backup.
- Independent temporary restore: GPG decryption PASS; archive contained only
  relative `workspace.bundle`, `INTERNAL_SHA256`, and `RELEASE_COMMIT` entries.
- Internal bundle SHA-256: PASS.
- `git bundle verify`: PASS; complete history with `refs/heads/main` and the
  annotated release tag.
- Restored `refs/heads/main` and recorded `RELEASE_COMMIT` both resolved exactly
  to `b300207cf33a7dfbf7de9312e38f67b39f9d4c67`.
- Temporary build/restore directories were removed by guarded cleanup traps.
- No Gateway, OpenClaw runtime/config, systemd, cron, deploy, push, or source
  `home-agent-factory` change was performed.

## Operational result

The release is ready only for the controlled manual pilot defined in
`ACTIVATION_READINESS.md`. It is not activated, installed as a service, wired
to Gateway, or authorized for unattended execution.
