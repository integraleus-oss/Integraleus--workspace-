# Reviewer transport final repair

Status: COMPLETE — R17_ACCEPT; TRANSFER NOT PERFORMED
Risk: MEDIUM

## Goal

Normalize two purely formal Claude verdict defects without inventing evidence:

1. remove unknown properties from finding fingerprints;
2. discard `test_result` evidence that lacks its required structured `command`.

Any positive criterion or verification claim weakened by discarded evidence
must become unverified rather than satisfied or fixed. A `still_open` result
must remain open; transport repair must never erase a persisting-defect claim.

## Boundaries

- Allowed implementation files:
  - `state/tasks/2026-08-12-orchestrator-integration/review_projection.py`
  - relevant tests under `state/tasks/2026-08-12-orchestrator-integration/tests/`
- Do not change capability-grant business code or its detached diff.
- Do not transfer, push, deploy, restart Gateway, modify systemd, or start cron.
- Preserve strict schema and semantic admission after normalization.

## Acceptance

- Red-capable regressions cover the exact `excerptless` fingerprint property and
  a `test_result` without `command`.
- Normalization is deterministic and records each operation.
- Invalid evidence is removed together with dangling references; unsupported
  claims become `unverified`/`appears_unfixed` as required by the existing
  contract.
- Integration and policy-core suites pass; `git diff --check` passes.
- Independent review of the transport change has no blocker or major.
- A fresh final-full review is attempted against unchanged capability-grant
  digest `5b29fb1e2a91f34c9a1c01c8ae04734a4f289ab4dcc29ecaff07e8e8dcf17fa2`.

## Checklist

- [x] Task packet
- [x] Red regressions
- [x] Transport fix
- [x] Full tests
- [x] Independent transport review
- [x] Final-full capability-grant replay
- [x] Evidence and handoff
