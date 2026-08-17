# Evidence

Status: COMPLETE — R17_ACCEPT; TRANSFER NOT PERFORMED

- Source failure 1: unexpected fingerprint property `excerptless`.
- Source failure 2: `test_result` evidence without required `command`.
- Capability-grant subject digest before work:
  `5b29fb1e2a91f34c9a1c01c8ae04734a4f289ab4dcc29ecaff07e8e8dcf17fa2`.
- Capability-grant implementation baseline: 48/48 tests PASS.
- Red regressions: both focused tests failed before the transport change.
- Focused post-fix tests: 2/2 PASS.
- Integration suite: 127/127 PASS.
- Policy-core suite: 87/87 PASS.
- Implementation files changed:
  - `state/tasks/2026-08-12-orchestrator-integration/review_projection.py`
  - `state/tasks/2026-08-12-orchestrator-integration/tests/test_integration.py`
- Unknown fingerprint properties are removed through a fixed allowlist before
  derived-ID normalization.
- Command-required evidence without a structured `command` is discarded.
  Referencing satisfied criteria become `not_verifiable`; targeted
  `appears_fixed` claims become `not_verifiable`.
- Independent review 1: `VERDICT: REWORK` with 2 blocker, 3 major, 6 nit.
- Blocker/major remediation:
  - discard only when `command` is absent; a present malformed command remains
    a contract failure;
  - derive fingerprint keys from the canonical review schema;
  - assert derived IDs directly against the cleaned canonical fingerprint;
  - add targeted `appears_fixed`, infra-symptom, and empty-evidence regressions.
- Post-review focused regressions: 6/6 PASS.
- Post-review integration suite: 131/131 PASS.
- Post-review policy-core suite: 87/87 PASS.
- Post-review `git diff --check`: PASS.
- Independent review 2 contained 0 blocker but 3 major despite its textual
  `VERDICT: ACCEPT`; the gate was therefore rejected.
- Review-2 major remediation:
  - all targeted verification statuses are downgraded to `not_verifiable` when
    any command-required evidence is discarded;
  - an infra symptom left with no evidence is pinned as a contract failure;
  - fingerprint schema derivation now checks the canonical shape is a flat,
    closed object and the valid fixture corpus is covered by the derived keys.
- Review-2 focused regressions: 4/4 PASS.
- Review-2 integration suite: 133/133 PASS.
- Review-2 policy-core suite: 87/87 PASS.
- Review-2 `git diff --check`: PASS.
- Independent review 3: `VERDICT: REWORK` with 4 major and no confirmed
  blocker. The critical issue was fail-open handling of `still_open`: the
  normalizer erased a persisting-defect claim after discarding one malformed
  evidence item.
- Review-3 remediation:
  - preserve `still_open` and its occurrence while discarding only the invalid
    evidence item;
  - downgrade only positive `appears_fixed` / `no_longer_applicable` claims;
  - do not fabricate `reverification_method = not_attempted`;
  - factor and strictly validate the canonical flat fingerprint-schema shape;
  - add direct rejection tests plus `null` command and non-command evidence
    boundary tests.
- Review-3 post-fix integration suite: 137/137 PASS.
- Review-3 post-fix policy-core suite: 87/87 PASS.
- Review-3 post-fix `git diff --check`: PASS.
- Independent review 4 again had a contradictory `VERDICT: ACCEPT` with 3 major;
  the gate rejected it.
- Review-4 major remediation:
  - derive positive verification statuses from the canonical schema while
    explicitly preserving `still_open` and `not_verifiable`;
  - pin command-required evidence kinds against the accepted validator's
    behavior for every schema evidence kind;
  - prove a `still_open` result with only discarded evidence contract-fails;
  - prove fingerprint cleanup cannot silently merge two findings.
- Review-4 post-fix integration suite: 141/141 PASS.
- Independent review 5: `VERDICT: REWORK`, 2 major. It correctly rejected an
  unsafe future-schema default that treated every unknown status as positive.
- Review-5 major remediation:
  - pin the exact accepted verification-status enum and fail import on drift;
  - keep positive statuses as an explicit allowlist;
  - parse the accepted schema once for both derivations;
  - make the enum regression non-tautological and make the command-kind test
    assert the validator's exact command error.
- Review-5 post-fix integration suite: 141/141 PASS.
- Review-5 post-fix policy-core suite: 87/87 PASS.
- Review-5 post-fix `git diff --check`: PASS.
- Independent review 6: `VERDICT: REWORK`, 3 major.
- Review-6 major remediation:
  - never clear `new_occurrence_id` while downgrading a positive claim;
  - make the fingerprint-collision test use distinct evidence IDs and assert
    the exact `duplicate_finding_id` failure;
  - pin the complete criteria-status and verification-method enums and fail on
    schema drift;
  - bind the validated positive-status set to the runtime branch.
- Review-6 post-fix integration suite: 143/143 PASS.
- Independent review 7 again reported 2 major despite textual `ACCEPT`; the
  gate rejected it.
- Review-7 major remediation:
  - downgrade `partially_satisfied` criteria when their cited evidence is
    discarded;
  - discard commandless evidence only when a schema and semantic probe proves
    the missing command is its sole defect;
  - retain co-defective items (including duplicate evidence IDs or missing
    descriptions) so the verdict remains a contract failure.
- Review-7 post-fix integration suite: 145/145 PASS.
- Independent review 8: `VERDICT: REWORK` with 1 blocker and 2 major. The
  blocker identified that a local placeholder probe could miss document-level
  validation errors.
- Review-8 remediation:
  - derive discard eligibility exclusively from the accepted validator's raw
    error report;
  - discard only when all errors under that evidence pointer are the exact
    missing-command error (plus its known `weak_appears_fixed_evidence`
    consequence);
  - never discard the sole evidence item, preserving an explicit contract
    failure instead of leaving an unsupported carrier;
  - cover retained occurrences end to end after positive-status downgrade.
- Review-8 post-fix integration suite: 145/145 PASS.
- Review-8 post-fix policy-core suite: 87/87 PASS.
- Review-8 post-fix `git diff --check`: PASS.
- Independent review 9 had 2 major despite textual `ACCEPT`; the gate rejected
  it.
- Review-9 major remediation:
  - cap the known `weak_appears_fixed_evidence` consequence at one exact,
    pointer-bound error and assert the raw validator error set;
  - add repeat-build determinism checks for fingerprint cleanup and evidence
    discard, including ordered normalization records.
- Review-9 post-fix integration suite: 145/145 PASS.
- Independent review 10: `VERDICT: REWORK`, 3 major focused on test proof.
- Review-10 remediation:
  - generate finding and occurrence IDs only through canonical validator
    functions;
  - prove end to end that `not_verifiable` may retain a schema-valid occurrence
    without becoming a verified finding;
  - add a semantic co-defect (`evidence_digest_required`) and assert that it is
    co-reported with missing-command before confirming the item is retained.
- Review-10 post-fix integration suite: 145/145 PASS.
- Independent review 11: `VERDICT: REWORK`, 2 major.
- Review-11 major remediation:
  - make raw-error validation mandatory at every normalizer call site;
  - let test helpers use the exact trusted manifest and prior-findings inputs;
  - exercise `partially_satisfied` with a real linked occurrence end to end and
    prove the final-full gate stops it as incomplete after downgrade.
- Review-11 post-fix integration suite: 145/145 PASS.
- Independent review 12: `VERDICT: ACCEPT`, 0 blocker, 0 major, advisory nits
  only. Transport repair accepted.
- Capability preflight after transport acceptance:
  - implementation tests: 48/48 PASS;
  - `git diff --check`: PASS;
  - diff SHA-256 unchanged:
    `5b29fb1e2a91f34c9a1c01c8ae04734a4f289ab4dcc29ecaff07e8e8dcf17fa2`.
- First final-full replay produced a contract-valid final-full verdict with
  0 blocker, 0 major and 3 nits, but policy returned
  `ESCALATED / R01_BINDING` because the replay wrapper omitted
  `attempt_epoch=1` from the first prior-attempt ledger record.
- Corrected external replay then failed before policy because Claude and its
  format-only retry did not return exact JSON; it produced no new verdict.
- Deterministic policy readmission reused the first replay's immutable,
  contract-valid verdict and corrected only the missing ledger epoch.
- Final policy result: `ACCEPTED / R17_ACCEPT`.
- Policy readmission directory:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-pilot-001-capability-grant-final-policy-readmission/run_home-agent-factory-manual-pilot-001.attempt-3-readmission`.
- Capability-grant files were not transferred to the source repository. Commit,
  push, deploy, Gateway and systemd changes remain forbidden/not performed.
