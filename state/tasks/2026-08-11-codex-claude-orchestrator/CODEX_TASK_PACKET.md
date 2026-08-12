# Codex Task Packet: Reviewer Contract Executable Slice

Status: COMPLETED — sandbox repaired, implementation and checks passed
Owner: Stanislav
Coordinator: OpenClaw main
Implementer: local Codex
Risk: MEDIUM, local files only

## Goal

Turn Claude's reviewer-contract design into an executable, tested first slice.

## Source inputs

- `TASK_PACKET.md`
- `reviews/claude-contract-design.md`
- `reviews/CLAUDE_ASSESSMENT.md`
- approved architecture `D-2026-08-11-01` in workspace `DECISIONS.md`

## Allowed files

Create or edit only under:

- `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`
- checklist status lines in this task folder's `TASK_PACKET.md` and
  `CODEX_TASK_PACKET.md` if useful

Do not edit wrappers, Gateway config, shared skills, DECISIONS, STATE, or any
other project.

## Deliverables

1. `implementation/review-verdict.schema.json`
2. `implementation/validate_review_verdict.py`
3. `implementation/fixtures/valid/*.json`
4. `implementation/fixtures/invalid/*.json`
5. `implementation/tests/test_review_verdict.py`
6. `implementation/README.md` with exact commands and boundary notes
7. `implementation/EVIDENCE.md` with test results and residual gaps

## Required behavior

- Draft 2020-12 schema; strict unknown-field rejection.
- No authoritative acceptance, state transition, merge, or human approval
  field may be represented.
- Strict transport parser rejects empty input, duplicate keys, trailing JSON,
  non-object root, invalid UTF-8, and oversized/deep documents.
- Validator distinguishes transport, schema, and semantic failures.
- Enforce severity floors and blocker/major evidence obligations.
- `criterion_id=null` requires category and rationale.
- Separate stable `finding_id` and per-run `occurrence_id`.
- Review modes: initial_full, targeted_verification, final_full.
- Targeted mode requires prior-findings digest and verification data.
- Reviewer may report infra symptoms but cannot classify `FAILED_INFRA`.
- Reviewer may propose disposition but cannot set resolution or approval.
- Counts, uniqueness, references, time ordering, and ID/hash consistency that
  JSON Schema cannot express must be checked in Python where feasible in this
  slice.
- Missing/schema-invalid output must exit non-zero and never produce a success
  state.

## Acceptance criteria

- AC-C01: Schema validates itself with the installed Draft 2020-12 validator.
- AC-C02: At least two valid fixtures pass.
- AC-C03: At least twelve invalid fixtures fail for the intended reason,
  including acceptance field, severity-floor bypass, missing evidence,
  null-criterion omission, bad targeted mode, reviewer infra classification,
  duplicate key, trailing JSON, count mismatch, bad reference, bad timestamps,
  and fingerprint mismatch.
- AC-C04: Test command exits zero and reports every fixture expectation.
- AC-C05: Validator output is machine-readable JSON and contains no acceptance
  decision; success means only `contract_valid: true`.
- AC-C06: `python3 -m unittest discover` and `git diff --check` pass for the
  implementation slice.
- AC-C07: No file outside allowed paths is changed by Codex.

## Non-goals

- No orchestration loop.
- No worktree creation.
- No policy state machine.
- No Claude wrapper changes.
- No background service, Redis, Gateway, cron, deployment, or commit.

## Blocker behavior

If a required Python package is missing, do not install system packages and do
not change global environments. Record the blocker and provide a standard-
library fallback plan or local dependency declaration.

## Commit rule

Do not commit. Preserve the dirty workspace and report only files in scope.

## Checklist

- [x] Implementation files created
- [x] Schema self-check passed
- [x] Valid fixtures passed
- [x] Invalid fixtures failed as expected
- [x] Unit tests passed
- [x] `git diff --check` passed
- [x] Scope audit passed

## Run outcome

Two initial workspace-write attempts failed with the same AppArmor/bubblewrap
infrastructure signature and correctly exhausted the retry budget. After the
owner explicitly approved a narrow AppArmor repair, the sandbox probe passed
without `--danger`. A fresh local Codex run then produced the bounded
implementation slice. Schema self-check, 2 valid fixtures, 15 invalid fixtures,
5 unit tests, whitespace checks, and the scope audit passed. No commit was made.
