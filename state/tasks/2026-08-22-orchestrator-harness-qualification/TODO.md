# Orchestrator Harness Qualification

Status: COMPLETE

## Fixed point

- Harness source: `state/tasks/2026-08-12-orchestrator-integration/`
- Qualification target: `/home/stanislav/projects/home-agent-factory`
- Historical replay baseline: `3d9c27e`
- Canonical target branch must remain unchanged during replay qualification.

## Scope

- [x] Audit current harness and tests against the agreed failure matrix.
- [x] Add missing fail-closed harness behavior and regression tests.
- [x] Prove PREPARE `red -> synthetic green -> clean restore` locally.
- [x] Prove controlled gate failure, infrastructure failure, unknown exception,
      malformed reviewer JSON, and interrupt handling.
- [x] Locate and bind the existing sealed replay packets for four historical
      security slices; do not duplicate already completed agent runs.
- [x] Verify the four historical replay results and their digests.
- [x] Record unified run evidence and independent review.
- [x] Verify canonical `home-agent-factory` remains clean and unchanged.

## Boundaries

- No Alpha BPR changes.
- No deploy, push, Synology write, gateway/config/auth change, or external send.
- No canonical `home-agent-factory` edits during qualification.
- No Codex or Claude launch before local red/green/restore qualification.
- Expected nonzero policy/fixture exits must be captured as evidence, not
  surfaced as generic shell failures.

## Acceptance

- Harness regression suite passes.
- Every terminal failure writes evidence and prevents automatic continuation.
- Scope checks include individual untracked files.
- Unknown failures stop fail-closed without implementation repair.
- Reviewer contract repair is bounded to one attempt.
- Interrupted runs are terminal and resumable only by explicit new command.
- Four replay runs remain isolated from canonical branches.

## Evidence checklist

- [x] Files changed
- [x] Test commands and counts
- [x] Red/green/restore transcript
- [x] Failure-matrix results
- [x] Replay digests and changed paths
- [x] Review verdict
- [x] Git status and commit state
