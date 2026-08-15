# Reviewer evidence-reference discipline

## Goal

Eliminate the real-project `bad_evidence_reference` blocker without weakening
the strict verdict validator, then prove the fix with regression tests and a new
post-review real-project smoke.

## Boundaries

- Source of truth: the workspace orchestrator implementation under
  `state/tasks/2026-08-12-orchestrator-integration/` plus its bounded tests.
- Preserve strict schema and semantic referential-integrity checks.
- Prefer reviewer contract/guidance and bounded repair over output sanitizing.
- Do not modify or deploy `home-agent-factory`, Gateway, cron, or external state.
- Do not push.

## Acceptance criteria

- [x] Regression reproduces a reviewer inventing evidence IDs.
- [x] Reviewer receives an explicit allowlist/discipline for evidence IDs on the
  first attempt and every bounded retry.
- [x] Unknown IDs remain rejected by the validator.
- [x] Focused, integration, core, compile, and diff checks pass.
- [x] New real-project smoke reaches post-review terminal `ACCEPT`, or records a
  distinct honest blocker with complete evidence.
- [x] Changes are reviewed through real-project initial/full-review gates and
  committed as a narrow slice.

## Evidence log

- Initial worktree: clean after snapshot commit `a73b298`.
- Prior r4: transport/schema passed; terminal `ESCALATED` due to four reviewer
  evidence references absent from the verdict evidence carriers.
- Final r8: strict transport/schema/semantic validation passed twice; managed
  chain reached `R15_NEED_FULL_REVIEW` then review-only `R17_ACCEPT` without a
  second Codex implementation leg.
