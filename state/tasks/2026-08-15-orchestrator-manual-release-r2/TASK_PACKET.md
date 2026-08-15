# Controlled-manual-use release checkpoint r2

Status: COMPLETE; CHECKPOINT BACKED UP; FIRST TASK PREPARED, NOT STARTED

## Goal

Freeze the approved `READY FOR CONTROLLED MANUAL USE; NOT ACTIVATED` state at
commit `3b01190`, protect it with a verified encrypted Git bundle on Synology,
and prepare (but do not silently activate) the first ordinary manual-use task.

## Authorized scope

- Create an annotated local tag resolving exactly to `3b01190`.
- Create a Git bundle containing complete history and the annotated tag.
- Encrypt it symmetrically with GPG AES-256 using the existing local recovery
  passphrase file; write only the encrypted artifact and checksum to the
  approved Synology backup directory.
- Decrypt into a guarded temporary local directory and verify checksums,
  archive paths, bundle integrity, refs, and exact commit.
- Create local evidence and first-task preparation documents.

## Forbidden scope

- No push, deploy, Gateway/runtime/config, cron, systemd, daemon, unattended
  execution, network configuration, package, authentication, or root-level
  Synology changes.
- No modification of source project repositories.
- No raw Synology data may leave the home network.
- Do not start a production cycle until its repository, commit, paths, gates,
  budgets, and stop conditions are recorded and checked.

## Checklist

- [x] Task packet created before release actions.
- [x] Workspace clean and checkpoint commit verified.
- [x] Annotated r2 tag created and verified.
- [x] Git bundle created with complete history and tag.
- [x] AES-256 encrypted backup and external checksum written with mode `600`.
- [x] Independent temporary decrypt and archive-path audit passed.
- [x] Internal checksum, `git bundle verify`, refs, and exact commit passed.
- [x] Temporary plaintext artifacts removed.
- [x] Evidence report completed and prepared for local commit.
- [x] First ordinary manual task packet prepared; execution remains manual.
