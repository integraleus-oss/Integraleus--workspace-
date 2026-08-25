# Evidence

Status: PASS

## Orchestrator baseline

- Canonical HEAD: `0ebd3fe51882d683da9c633ce9349205dd318acd`.
- Target orchestrator paths clean before and after verification.
- Initial focused invocation: 4 TAP tests passed; 3 coverage tests had an
  import-path invocation error (`test_integration` absent from `PYTHONPATH`).
- Corrected invocation changed only `PYTHONPATH`, not code.

## Regression scenarios

- Focused safeguards: 7/7 PASS.
- Coverage repair: incomplete full coverage receives one contract-only retry;
  a second incomplete result fails closed; unrelated projection errors do not
  receive this retry.
- TAP integrity: matching count passes; mismatched, missing, ambiguous, and
  invalid expected counts fail closed; undeclared count preserves old shape.
- Integration: 159/159 PASS.
- Policy core: 87/87 PASS.
- Python compilation and `git diff --check`: PASS.
- Verdict: safeguards are effective; stop further orchestrator hardening.

## Track F

- Project baseline: `f0ea11426063e96ef51d7db313579f6863ab038e`.
- Inventory: six modified tracked paths plus the appliance directory, export
  script, and appliance regression test as untracked paths.
- Appliance tests: 4/4 PASS.
- Shell syntax for appliance export, complete build, and first boot: PASS.
- Verification-pack ZIP checksum: PASS.
- OVA checksum: PASS; OVA contains OVF, manifest, and one VMDK.
- Complete offline archive checksum: PASS; archive contains OVA, checksum,
  appliance README, and compatibility matrix.
- `git diff --check`: PASS.
- No product/runtime/VM/service changes were made by this audit.

## Final state

- Orchestrator commit unchanged; push/deploy/runtime actions: none.
- Track F local commit: `b9e6377 feat: add portable Track F appliance`.
- Alpha BPR worktree is clean after commit; push/deploy/runtime actions: none.
- Pilot #4 was not launched because no approved implementation task packet or
  acceptance criteria exist. The next unchecked Track F item is an external
  integration pilot requiring named customer/test inputs and authorization.
