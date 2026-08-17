# Reviewer transport normalization

Status: COMPLETE — transport ACCEPT; pilot REWORK
Risk: MEDIUM

## Goal

Admit reviewer verdicts with two narrowly defined transport defects without
changing substantive findings: overlong finding titles and references to
undefined evidence IDs.

## Boundaries

- Allowed: `review_projection.py`, its integration tests, and this task evidence.
- Forbidden: capability-grant pilot diff, Gateway, systemd, deploy, push, transfer.
- Preserve the original reviewer verdict as the immutable runner input snapshot.
- Normalize only a deep copy used for validation/projection.
- Any unsupported defect remains a hard contract failure.

## Acceptance

- Finding titles longer than the sealed 160-character limit are deterministically truncated.
- Undefined evidence IDs are removed from coverage/limitations.
- A `satisfied` criterion that loses evidence becomes `not_verifiable`, never accepted.
- Normalizations are recorded in validation evidence.
- Regression and full runtime tests pass; independent review reports no blocker/major.
- Only after transport ACCEPT: retry review of the unchanged capability-grant diff.

## Checklist

- [x] Packet created
- [x] Implementation
- [x] Regression tests
- [x] Full tests
- [x] Independent review
- [x] Unchanged capability-grant review retry
- [x] Final evidence and commit
