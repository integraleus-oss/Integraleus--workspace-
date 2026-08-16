# Manual-005 result

Status: `ESCALATED`; transfer prohibited

## Managed result

- One Codex implementation completed within the two-file write boundary.
- Managed gates passed: `npm test` reported 18/18 tests and
  `git diff --check` passed.
- The initial Claude review stated that AC-1 through AC-5 were satisfied and
  reported only non-blocking nits, but its output needed bounded verdict repair.
- The final contract-only repair remained semantically invalid:
  `command_output` evidence omitted its required `command` block at
  `/findings/0/evidence/3/command`.
- The orchestrator ended fail-closed with exit code 4 and terminal
  `ESCALATED`; it did not launch a second Codex implementation or accept the
  diff.

## Reviewer observations

The initial review recorded no blocker or major. Its nits concerned:

- exporting/pinning the accepted model-class grammar and later aligning the
  pack schema;
- pinning short-circuit precedence when a valid request class overrides an
  invalid pack default;
- reducing duplicated invalid-value corpora and documenting `undefined` as an
  absent source.

These observations are not an admitted verdict because the repaired document
failed the sealed evidence contract.

## Independent verification

- Repeated `npm test`: PASS — 18 tests, 0 failures.
- Repeated `git diff --check`: PASS.
- Changed paths are exactly `src/core/policy.js` and `test/policy.test.js`.
- No managed-cycle or Claude processes remained after termination.
- Source `/home/stanislav/projects/home-agent-factory` remains clean at
  `6e56761030812f0387dbbe570a199b37c3088ca5`.
- No commit, source transfer, push, deploy, Gateway, cron, systemd, daemon,
  unattended, dependency, network, or system change occurred.

## Next gate

Do not transfer this diff. A new bounded task must decide whether to widen the
scope to schema-pinning and then produce a fresh sealed review; it must not
reuse this failed verdict as acceptance evidence.

## Checklist

- [x] Managed cycle terminal result recorded.
- [x] Changed-path scope verified.
- [x] Tests and diff checks recorded.
- [x] Source repository unchanged.
- [x] Transfer prohibited after fail-closed escalation.
