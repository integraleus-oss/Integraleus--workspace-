# Task Packet: Deterministic State Machine Slice

Status: COMPLETED
Owner: Stanislav
Coordinator: OpenClaw main
Risk: MEDIUM, local artifact work only

## Goal

Specify and implement a deterministic policy engine that consumes trusted task,
gate, reviewer-contract, and finding-registry inputs and emits only mechanical
state transitions. No LLM may accept work, downgrade findings, or classify
unknown failures as infrastructure.

## Deliverables

- `implementation/orchestrator-state-machine.schema.json`
- `implementation/finding-registry.schema.json`
- `implementation/orchestrator_policy.py`
- valid and invalid fixtures
- unit tests, including transition-table and budget-boundary coverage
- `implementation/STATE_MACHINE.md`
- updated `implementation/EVIDENCE.md`

## Required states

- `REWORK`
- `ACCEPTED`
- `FAILED_INFRA`
- `ESCALATED`

Intermediate execution phases may be represented separately, but they must not
weaken the four policy outcomes.

## Deterministic requirements

- Acceptance requires all mandatory gates green, a contract-valid final review,
  zero open blocker/major findings, required evidence manifest satisfied, and a
  final-full review after targeted closure.
- Known infrastructure classification is allowlist-only. Unknown runner/test
  failures escalate; they never become `FAILED_INFRA` by free-text similarity.
- Infrastructure retries have a separate budget; repeated exhaustion escalates.
- Rework iterations have a bounded budget; exhaustion escalates.
- Finding identity is stable and deterministic. Repeated occurrences are
  deduplicated without losing history.
- Claude cannot close, suppress, downgrade, or accept a finding. Reviewer output
  is observation data; registry transitions require policy-valid evidence.
- Targeted verification may close previously open findings, but acceptance still
  requires one final full review.
- Nits do not block acceptance unless task policy explicitly promotes them.
- Every transition records reason codes and immutable input digests.
- Malformed, incomplete, stale, mismatched, or replayed trusted inputs fail
  closed to `ESCALATED` or a typed tool-input error; never to `ACCEPTED`.

## Boundaries

Allowed edits are limited to this task folder. The completed reviewer-contract
slice may be imported or read, but its schema/validator/tests must not be changed
without a separately documented blocker.

Forbidden: commits, Gateway/config/runtime changes, root changes, network sends,
`--danger`, unrelated worktree cleanup, and LLM-authored acceptance decisions.

## Execution plan

- [x] Artifact/task packet created
- [x] Fresh Claude design review: broad attempt timed out; bounded core retry completed
- [x] Coordinator converts accepted design into bounded Codex packet
- [x] Fresh local Codex implements in workspace-write sandbox
- [x] Coordinator runs deterministic gates: schemas, fixtures, 63 tests, py_compile
- [x] Fresh Claude adversarial review: broad attempt timed out; bounded core review found 3 blocker + 4 major
- [x] Codex fixes confirmed blocker/major findings: R1 completed with exact regressions
- [x] Gates rerun: schemas, fixtures, 77 tests, py_compile
- [x] Targeted verification of SM-01 through SM-07: six fixed, SM-07 residue reproduced locally
- [x] Codex R2 closes registry-history canonicalization mismatch
- [x] Independent R2 gates: 57 focused, 79 total, schemas, fixtures, compile, whitespace
- [x] Fresh targeted closure of R2 returned `TARGETED_PASS`
- [x] Final-full review found FF-01 through FF-04 (0 blocker, 4 major)
- [x] Fresh Codex R3 fixed FF-01 through FF-04 and added exact regressions
- [x] Independent R3 gates: 61 focused, 83 total, schemas, fixtures, compile, whitespace
- [x] Fresh targeted closure of FF-01 through FF-04: R3 found two follow-up majors; bounded R4 fixed both; fresh R4 closure returned `TARGETED_PASS`
- [x] Current-tree final-full closure review returned `FINAL_FULL_PASS`
- [x] Policy engine mechanically reached `ACCEPTED/R17_ACCEPT` on the accepted fixture; final independent gates passed with 84/84 tests

## Commit rule

Do not commit automatically. Preserve unrelated dirty-worktree changes.
