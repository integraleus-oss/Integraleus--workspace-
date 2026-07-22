# Claude Review Prompt: OpenClaw Shared Memory Phase 1

Review the current diff for `projects/openclaw-shared-memory`.

Focus on bugs, security regressions, missing Phase 1 proof, and test gaps.

Expected Phase 1 boundaries:

- Local/disposable DB only.
- Distinct role-scoped login users for reader/writer/promoter/backup.
- No Synology changes.
- No OpenClaw runtime config changes.
- No import or promotion of real memory.

Expected proof:

- Full repository lifecycle runs through distinct DB URLs.
- Reader cannot write.
- Writer can propose but cannot promote/update.
- Promoter can promote/reject/supersede/archive only with actor gate and confirmation checks.
- Forbidden/private records remain denied to reader/repository reads.
- Backup role can perform full recovery backup despite forced RLS.
- Mirror exports only `shared_safe`.
- Backup/restore drill succeeds on disposable DB.
- Real-data plaintext backup and same-target restore are refused.
- Container is stopped after tests.

Return concise JSON with verdict `GO` or `NO_GO`, findings, test_gaps, and summary.
