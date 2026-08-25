# Evidence Backlog Cleanup Manifest

Status before execution: approved by Stanislav on 2026-08-25.

Scope: the 21 untracked evidence directories inventoried in `REPORT.md`.

Rule: keep exactly the files listed below. Remove every other pre-existing file in each listed directory. No path outside these directories is in scope. Empty directories may disappear. Removed files go to the system trash; the trash is not emptied by this task.

Planned result: keep 99 of the original 220 files and remove 121. The audit's own `TODO.md`, `REPORT.md`, and this manifest are additional retained files.

## Exact keep list

- `2026-08-17-alpha-presale-doctor-pilot`: `EVIDENCE.md`, `RESULT.md`, `TASK_PACKET.md`
- `2026-08-18-alpha-presale-doctor-manifest`: `RESULT.md`, `REVIEW_INSTRUCTIONS.md`, `TASK_PACKET.md`, `TODO.md`
- `2026-08-18-alpha-presale-doctor-rework`: `CLAUDE_REVIEW_R2.md`, `RESULT.md`, `REVIEW_INSTRUCTIONS.md`, `TODO.md`
- `2026-08-18-alpha-presale-doctor-transfer`: all 3 files
- `2026-08-18-home-agent-factory-status-pilot`: `FINAL_REVIEW_ONLY_R5.md`, `RESULT.md`, `ROLLBACK.md`, `SECURITY_PRECHECK.md`, `TASK_PACKET.md`, `TRANSFER_EVIDENCE.md`
- `2026-08-18-orchestrator-review-loop-reduction`: `RESULT.md`, `REVIEW_INSTRUCTIONS.md`, `TASK_PACKET.md`, `TODO.md`, `claude-review-final.md`
- `2026-08-20-alpha-bpr-track-f-release-audit-closure`: all 5 files
- `2026-08-20-alpha-bpr-track-f-release-audit-r2`: `AUDIT_HARNESS.sh`, `PREPARE_RESULT.md`, `RESULT.md`, `TASK_PACKET.md`
- `2026-08-20-alpha-bpr-track-f-release-audit`: `AUDIT_HARNESS.sh`, `PREPARE_RESULT.md`, `RESULT.md`, `TASK_PACKET.md`
- `2026-08-20-alpha-bpr-universal-integration-r2`: `DOTNET_HARNESS.sh`, `IMPLEMENTATION_TASK.md`, `PREPARE_RESULT.md`, `RESULT.md`, `TASK_PACKET.md`
- `2026-08-20-alpha-bpr-universal-integration-v1`: `FOCUSED_TEST_HARNESS.sh`, `IMPLEMENTATION_TASK.md`, `PREPARE_RESULT.md`, `RESULT.md`
- `2026-08-20-orchestrator-pilot3-hardening`: `RESULT.md`, `TASK_PACKET.md`, `TRANSFER_EVIDENCE.md`, `claude-review-followup.md`
- `2026-08-20-orchestrator-regression-pilot`: all 4 files
- `2026-08-21-alpha-bpr-triz-p3-proof-summary`: `MANUAL_CLOSURE_REVIEW.md`, `MANUAL_CLOSURE_REVIEW_RESULT.md`, `PREPARE_RESULT.md`, `PROOF_HARNESS.sh`, `RESULT.md`, `TASK_PACKET.md`, `TODO.md`
- `2026-08-21-alpha-bpr-universal-integration-r3`: `DOTNET_HARNESS.sh`, `IMPLEMENTATION_TASK.md`, `PREPARE_RESULT.md`, `RESULT.md`, `TASK_PACKET.md`
- `2026-08-21-alpha-bpr-universal-integration-r4-closure`: `DOTNET_HARNESS.sh`, `FINAL_REVIEW.md`, `FINAL_REVIEW_INSTRUCTIONS.md`, `FINAL_REVIEW_PACKET.md`, `PREPARE_RESULT.md`, `RESULT.md`, `TASK_PACKET.md`, `TODO.md`, `TRANSFER_PACKET.md`, `TRANSFER_RESULT.md`
- `2026-08-21-alpha-bpr-universal-integration-r4-repair`: `DOTNET_HARNESS.sh`, `IMPLEMENTATION_TASK.md`, `PREPARE_RESULT.md`, `RESULT.md`, `TASK_PACKET.md`, `TODO.md`
- `2026-08-21-alpha-bpr-universal-integration-r4`: `DOTNET_HARNESS.sh`, `IMPLEMENTATION_TASK.md`, `PREPARE_RESULT.md`, `RESULT.md`, `TASK_PACKET.md`, `TODO.md`
- `2026-08-21-orchestrator-dotnet-sandbox-regression`: all 6 files, including the three files under `fixture/`
- `2026-08-23-orchestrator-architecture-visual`: all 3 files
- `2026-08-23-store-generator-audit`: its single `REPORT.md`

## Exact removal rule by package

For packages marked `all`, remove nothing. For every other package, remove exactly the files not named in its keep entry above. The frozen pre-clean inventory is the 220-file inventory used by `REPORT.md`; therefore the keep list plus its complement uniquely identifies all 121 removal targets.

Material removals include all raw `CLAUDE_REVIEW*.json` envelopes, superseded generated policy/specification/task-map variants, repeated review transcripts, and `2026-08-21-alpha-bpr-universal-integration-r4-closure/TRANSFER.patch`.

## Commit groups

1. Alpha-Presale doctor: packages 1–4.
2. Home Agent Factory status: package 5.
3. Orchestrator hardening: packages 6, 12, 13, 19, plus this audit package.
4. Alpha BPR Track F: packages 7–9.
5. Universal Integration: packages 10, 11, 15–18.
6. TRIZ P3 rejected orchestrator attempt: package 14.
7. Orchestrator architecture visual: package 20.
8. Store Generator safety audit: package 21.
