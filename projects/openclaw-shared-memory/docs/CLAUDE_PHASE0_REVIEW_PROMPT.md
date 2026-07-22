# Claude Review Prompt: OpenClaw Shared Memory Phase 0

Review the current uncommitted diff for `projects/openclaw-shared-memory`.

Focus on bugs, security regressions, missing hardening, and test gaps for Phase 0 only.

Expected Phase 0 boundaries:

- No Synology deployment.
- No OpenClaw runtime config changes.
- No import of real memory.
- Local/disposable DB tests only.

Expected hardening:

- `002_hardening.sql` adds role groups, RLS, `content_hash`, append-only audit protection, and security-invoker shared-canon view.
- Application config supports reader/writer/promoter/backup URLs.
- Repository/server enforce idempotent propose, allowlisted promotion, classification confirmation, privacy-filtered read/list/get, reject/archive/list candidates, and supersede only for shared records.
- Mirror export fails closed for private/forbidden classes.
- Real-data backup requires encryption.
- Restore drill requires checksum and refuses prod/same target.
- Synology package requires explicit bind host and avoids wildcard DB exposure.
- Evidence and tests prove the above locally.

Return concise JSON:

```json
{
  "verdict": "GO|NO_GO",
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "file": "path",
      "line": 0,
      "issue": "text",
      "recommendation": "text"
    }
  ],
  "test_gaps": ["text"],
  "summary": "text"
}
```
