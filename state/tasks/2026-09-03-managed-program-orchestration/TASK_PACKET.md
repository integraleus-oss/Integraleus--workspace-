# Managed Program Orchestration

Status: BLOCKED_EXTERNAL_REVIEW_TIMEOUT
Owner: main
Started: 2026-09-03T21:47:00+03:00
Execution: no live process; R20 reviewers timed out after 300 seconds
Expected output: strict multi-slice managed runner and terminal acceptance gate

## Goal

Prevent a large managed objective from being reported as successful merely
because one agent process exited with code 0. Continue bounded work slices until
the objective is verified complete or a genuine external blocker is recorded.

## Boundaries

- Allowed: `scripts/managed-agent-runner.mjs`, `scripts/managed-outcome-contract.mjs`, their tests,
  `scripts/execution-supervisor.py`, supervisor tests, and the TaskFlow plugin.
- Forbidden: Gateway restart/activation, production/customer/Synology changes,
  unrelated dirty files, and external publication.
- Runtime activation requires a separate explicit approval after code review.
- No commit until checks and independent review are complete.

## Acceptance

- [x] Partial work cannot produce `SUCCEEDED`.
- [x] Exit code 0 alone cannot produce `SUCCEEDED`.
- [x] A large task persists packages and acceptance gates in a durable contract.
- [x] `CONTINUE` automatically launches another bounded agent slice.
- [x] `BLOCKED` requires a concrete external blocker with evidence and owner action.
- [x] Terminal status is derived from the contract and reconciled by supervisor.
- [x] Tests cover success, continuation, malformed/stale evidence, invalid success,
  valid/invalid blocker, capability isolation, and crash.
- [x] Existing supervisor/plugin tests remain green.
- [ ] Independent Standards and Spec reviews complete before activation.

## Activation gate

Code is prepared but not active in the live Gateway. Activation requires owner
approval for independent external review and a Gateway restart/live drill.

Current gate: R18/R19 findings are remediated and local checks pass. R20 core
and runtime reviewers both timed out without verdicts. Activation remains
forbidden until fresh core and runtime reviews return PASS on this revision.
