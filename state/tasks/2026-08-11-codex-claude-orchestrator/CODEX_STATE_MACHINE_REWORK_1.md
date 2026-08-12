# Codex Rework Packet: Policy Engine Adversarial Findings R1

Status: READY
Implementer: fresh local Codex
Scope: only policy-engine files under `implementation/`
Commit: forbidden

## Confirmed review input

Claude report: `reviews/claude-state-machine-core-review.md`.

Coordinator directly reproduced SM-01, SM-02, SM-03, SM-06, and SM-07. SM-04
and SM-05 are source-confirmed validation/replay gaps. Fix all seven without
changing the completed reviewer-contract schema, validator, or tests.

## Required fixes

- SM-01: terminal replay must not precede validation/binding/payload-digest
  checks and must not rely on lossy recursive key-name normalization.
- SM-02: reject duplicate `evidence_artifacts.req_id`; never last-wins.
- SM-03: fully validate finding-registry structure and reject duplicate
  `finding_id`; never last-wins or delete history.
- SM-04: validate terminal decision schema/content, recompute its decision
  digest, and only replay a verified terminal record after all current input
  validation/binding/replay/staleness checks. Invalid terminal data must
  deterministically `ESCALATED`, never be echoed.
- SM-05: unknown registry status/severity/type must fail closed; never default
  to info/non-open or allow severity downgrade.
- SM-06: malformed/unhashable nested values in any supposedly scalar list/map
  must return a machine `ESCALATED` decision, not raise an uncaught exception.
- SM-07: canonicalization and decision traversal must agree. Either preserve
  ordered semantics in digests or sort decision reasons/directives consistently;
  semantically equivalent permutations must yield identical decision JSON.
- Apply no-progress policy consistently to evidence rework as well.

## Regression requirements

Add exact tests for all seven Claude repros, plus:

- terminal decision with forged digest/outcome/budgets;
- invalid ledger registry status, severity, count, history entry, and bool count;
- duplicate occurrence IDs/history entries;
- duplicate gate results/evidence/required evidence identifiers;
- nested occurrences of keys named `findings`/`required_evidence` inside opaque
  payloads do not alter outer canonicalization semantics;
- public `decide()` is total for representative malformed dict/list/scalar
  containers and never throws outside process-fatal exceptions.

Keep reason codes deterministic and schemas strict. Run all existing and new
tests, schema/fixture checks, py_compile, and whitespace checks. Append exact
evidence and do not commit.
