# Evidence

Status: REWORK — ADMITTED REVIEW HAS OPEN FINDINGS

- Authorization: Telegram topic 2922, message 3356.
- Canonical project root: `/home/stanislav/workspace/alpha-presale`.
- Expected fixed source commit: `52ea3ba`.
- Commit/transfer/push/deploy: forbidden.
- Attempt 1 project root: `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-presale-doctor-pilot-002`.
- Attempt 1 outcome: `ESCALATED` before gates/review because
  `alpha_presale/__pycache__/` changed after baseline capture.
- Attempt 1 Codex changed exactly the three allowed files; its focused doctor
  checks passed. Full-suite failures inside the Codex sandbox were caused by
  the worktree location hiding the read-only licensing corpus and by denied
  loopback socket binding. No review was run and no diff was transferred.
- Retry uses a fresh clean worktree at
  `/home/stanislav/workspace/alpha-presale-doctor-pilot-002`, still based on
  `52ea3ba`; Codex starts from source rather than receiving the attempt-1 diff.
- Retry redirects Python cache outside the project worktree.
- The initially proposed retry root under `/home/stanislav/workspace` was
  rejected by packet admission because it is outside approved orchestrator
  worktree bases; no implementation ran there.
- Fresh retry root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-presale-doctor-pilot-002-r3`.
- Fresh retry run root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-presale-doctor-pilot-002-run-r4`.
- Retry changed exactly `alpha_presale/cli.py`, `tests/test_core.py`, and
  `README.md`.
- Retry diff SHA-256:
  `df5a9865959f8dcd62b2cb09ff2eb2dfeaa2d82f34f31d3bfb2bca653a2eac3e`.
- `DoctorCliTests`: PASS, 11/11.
- Read-only Python source compilation: PASS.
- `git diff --check`: PASS.
- Ignored-file boundary: PASS; no ignored files changed in the fresh retry.
- Claude review launch: FAILED_INFRA before review with HTTP 429 session limit;
  provider message says reset at 22:30 Europe/Moscow.
- Review-only retry after the reset did not rerun Codex or modify the fixed
  diff. The seal and diff digest were reverified before review and admission.
- The initial retry verdict required the single allowed contract-only repair.
  The repaired verdict was admitted by policy as `REWORK / R11_OPEN_FINDINGS`.
- Admitted review findings: 4 major and 2 nit. The major findings are missing
  aggregation for unreadable/non-UTF-8 inputs, no baseline local configuration
  readiness check, silent omission of shell-variable verification commands,
  and non-hermetic success tests coupled to host `node`/`rg` availability.
- The two nits cover the untested non-executable local-command branch and a
  fragile shell-keyword tokenizer.
- Repeated `DoctorCliTests`: PASS, 11/11; `git diff --check`: PASS; diff digest
  remained `df5a9865959f8dcd62b2cb09ff2eb2dfeaa2d82f34f31d3bfb2bca653a2eac3e`.
- Policy decision digest:
  `sha256:847235ad7b7b40a07dc951177ef37a9f22fc4576468125b32729ce5ef6bdef70`.
- Transfer remains forbidden pending bounded rework, repeated checks, and a
  fresh admitted review.
- Canonical Alpha-Presale remains at `52ea3ba`; its pre-existing untracked
  `docs/reviews/` and `memory/` are unchanged.
- Commit/transfer/push/deploy/system service/Web/API/customer action: none.
