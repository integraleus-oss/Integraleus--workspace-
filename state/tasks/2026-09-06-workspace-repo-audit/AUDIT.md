# Workspace repository audit

Status: AUDIT_COMPLETE
Checked: 2026-09-06 11:43 MSK
Repository: `/home/stanislav/.openclaw/workspace/agents/main`
Branch: `main`

## Executive finding

The repository is structurally healthy (`git fsck` found only ordinary
unreachable objects), but the worktree mixed four different classes of data:

1. durable source/documentation changes that should be reviewed and committed;
2. generated runtime/evidence updates that need an explicit retention policy;
3. local exports and large handoff media that should not enter Git;
4. host-local migration, lock, backup, and infrastructure-note files that must
   remain local.

`main` is 172 commits ahead of `origin/main` and 0 behind. This is a publication
decision, not a worktree-cleanliness problem; no push was performed.

## Initial tracked changes

- 22 tracked paths changed: 20 modified and 2 deleted.
- Diff size before this audit: 385 insertions and 69 deletions.
- The two deleted paths are OpenClaw workspace-state files migrated by the
  2026.9.2 doctor. Their deletion should be committed only together with the
  corresponding local-state ignore policy.
- Durable candidate changes:
  - `AGENTS.md` plus local `docs/INFRA-NOTES.md` split;
  - `DECISIONS.md` and `STATE.md` approved cross-session state;
  - Codex account-limit probe fix and heartbeat log-filter fix;
  - dashboard/product-calculator skill compatibility notes;
  - ordered-hardening terminal evidence.
- Runtime-history changes:
  - September 1 supervisor evidence/state/outbox files were rewritten by later
    recovery/terminalization passes. These should not be mixed into feature
    commits; preserve them only in a dedicated audit-history commit if desired.

## Initial untracked data

- Large generated handoffs dominated the noise:
  - `out/alpha-bpr-rc2.1-testing/`: about 256 MiB;
  - `out/alpha-bpr-rc2.1-complete-testing/`: about 256 MiB;
  - `outbox/alpha-bpr-rc2.2/`: about 166 MiB;
  - other `out/`, `outbox/`, and `exports/` content: tens of MiB.
- `state/tasks/managed-admission/`: about 5.8 MiB / 153 runtime files.
- `projects/execution-supervisor-dashboard/`: about 904 KiB / 8 files; this is
  real source and remains visible for a separate review/commit.
- Numerous task evidence directories are plausible durable audit records and
  remain visible rather than being broadly ignored.
- Backup suffixes, finalize locks, workspace-state migration remnants, and the
  accidental empty `=22.22.3` file are disposable/local noise.

## Ignore-policy repair applied

`.gitignore` now excludes:

- root export/handoff trees: `exports/`, `out/`, `outbox/`;
- ephemeral supervisor admissions and topic state;
- workspace-state migration remnants and finalize locks;
- dated backup suffixes and the accidental `=22.22.3` file;
- `docs/INFRA-NOTES.md`, which is host-specific and may contain sensitive
  infrastructure context.

The rules do not untrack existing committed files and do not delete anything.

## Recommended commit sequence

1. **Repository hygiene:** `.gitignore`, removal of the two already-migrated
   tracked workspace-state files, and this audit artifact.
2. **OpenClaw 2026.9.2 maintenance:** account probe, heartbeat filter, tests,
   hardening evidence, and relevant task packets.
3. **Approved memory/state:** `DECISIONS.md` and `STATE.md`, after checking each
   entry against explicit approvals.
4. **Skill migrations:** dashboard, product calculator, and safe SQLite archive
   skill as one reviewed compatibility batch.
5. **Execution-supervisor history:** either a dedicated evidence-only commit or
   leave historical generated state local; do not mix with executable changes.
6. **Execution supervisor dashboard:** review/test as its own project commit.

## Actions intentionally not taken

- No file deletion or restoration.
- No staging or commit.
- No push or history rewrite.
- No large artifact movement.
- No secret values printed or copied.
