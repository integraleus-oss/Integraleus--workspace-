# Controlled-manual-use checkpoint r2 evidence

Status: COMPLETE

## Release identity

- Approved commit: `3b01190baafc783d8ac519eba40bf1f37960625d`.
- Annotated tag: `orchestrator-local-cli-r2-manual-2026-08-15`.
- The peeled annotated tag resolves exactly to the approved commit.
- Operational status: `READY FOR CONTROLLED MANUAL USE; NOT ACTIVATED`.

## Encrypted backup

- Artifact:
  `/mnt/synology/Documents/openclaw-backups/encrypted/openclaw-orchestrator-3b01190-2026-08-15-r2.tar.gpg`.
- Size: `604966834` bytes.
- Artifact and adjacent checksum file mode: `600` (NFS ownership is squashed by
  the approved share configuration).
- External SHA-256:
  `cef0f93545522ac63e6864f1e20ba814f48607e919c4d2e732831d2484adca80`.
- Encryption: GPG symmetric AES-256 using the existing local mode-`600`
  recovery passphrase file. The passphrase was not copied into the archive,
  repository, evidence, or chat.

## Independent restore verification

- Decryption into a fresh guarded local temporary directory: PASS.
- Archive allowlist: exactly `workspace.bundle`, `INTERNAL_SHA256`,
  `RELEASE_COMMIT`, and `RELEASE_TAG`; absolute and parent-traversal paths: none.
- Internal bundle SHA-256:
  `55a40fa1645fa4bee65c766d0c97e7c6f9a47e1fa95ddcfd47be3ca321ce401d` — PASS.
- `git bundle verify`: PASS; complete history recorded.
- Bundle refs: `refs/heads/main` at the approved commit and the annotated r2
  tag object.
- Bare restore: branch and peeled tag both resolve exactly to
  `3b01190baafc783d8ac519eba40bf1f37960625d`.
- Temporary plaintext build and restore directories were removed after
  verification.

## Boundaries

No push, deploy, Gateway/runtime/config, cron, systemd, daemon, unattended
execution, package, authentication, network, root-level Synology, or source
project change occurred.

The first ordinary controlled-manual-use task is prepared under `manual-001/`.
It is not activated by this checkpoint and requires a clean detached worktree
and foreground invocation.
