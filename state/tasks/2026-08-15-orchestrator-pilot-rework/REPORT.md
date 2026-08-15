# Orchestrator pilot rework report

Status: TECHNICALLY COMPLETE; AWAITING READINESS DECISION; NOT ACTIVATED

## Outcome

Both blockers recorded by `D-2026-08-15-04` are closed in the local manual
orchestrator implementation. The fixes do not activate the orchestrator and do
not grant any new operational authority.

## Changes

### Complete prior-finding carry

- The production cycle now reconstructs carried findings from the admitted
  reviewer verdict, normalizes their canonical IDs, and carries the complete
  finding records into targeted re-review.
- The trusted review builder requires a complete record for every open registry
  ID and stops fail-closed if any detail is missing.
- The core verdict validator accepts the sealed detailed prior-finding contract
  with a strict key allowlist while retaining compatibility with the previous
  minimal contract.

### Structured operator interruption

- The launcher catches operator interruption, terminates the child process
  group, captures available stdout/stderr and preserves launch evidence, and records exit code
  `130` with status `INTERRUPTED`.
- The managed cycle records a terminal `INTERRUPTED` cycle result, does not run
  review, does not classify the interruption as an unknown failure, and does
  not continue automatically.
- The production CLI returns exit code `130` when the managed cycle reaches
  this terminal state.

## Verification

- Red test: the pre-fix launcher allowed `KeyboardInterrupt` to escape without
  a structured terminal result.
- Integration suite: `94/94` passed.
- Core verdict-validator suite: `87/87` passed.
- `python3 -m py_compile` passed for the changed Python modules.
- `git diff --check` passed.
- Original source repository remains clean at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.

## T02 rerun

- Fresh worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t02-instance-path-r2`
- Run evidence:
  `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t02-instance-path-r2-run`
- Result: `ACCEPTED / R17_ACCEPT` after one Codex implementation and the
  required review-only final-full pass.
- Cycle-result SHA-256:
  `a19c696d535ce78ca7e3e9811034f41426a4773a2da87bb1f697150c0648b018`.

Because the fresh T02 implementation went directly to final-full review, a
separate targeted replay was used to exercise the repaired carry contract
against the original three T02 findings.

## Targeted prior-finding replay

- Evidence root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t02-targeted-replay-r5`
- All three findings were supplied with title, severity, rationale, location,
  fingerprint, reproduction information, remediation, and sealed evidence.
- The reviewer reprocessed that complete input and policy returned
  `REWORK / R15_NEED_FULL_REVIEW`, the expected gate after targeted review. It
  did not manufacture acceptance or treat missing finding context as verified.
- Replay-result SHA-256:
  `987516706bb9fcd1e06ce4f2d9b95d08a4f9eb1a5dad3265bdf49dc9ab849882`.
- Prior-findings SHA-256:
  `19ef15d90d46f8c8dc58ad903ff96e0861109a27538ed0f1f3b35feb505c7bb9`.
- Policy decision SHA-256:
  `4de1b8faf2c59fddba24776014932459751a47b02149542b89ac2c9975597251`.

Earlier replay attempts stopped fail-closed while exposing two additional
contract mismatches: reviewer IDs needed canonical normalization, and the core
validator needed an explicit detailed-record contract. Both were fixed and
covered by regression tests before the successful replay.

## Interruption drill

- Worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-interrupt-r3`
- Run evidence:
  `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-interrupt-r3-run`
- Result: terminal `INTERRUPTED`, launcher exit `130`, review not started,
  no automatic continuation, no orphaned pilot process, and clean worktree.
- Cycle-result SHA-256:
  `8bdd460a64fce47fd70e0e07c322262b5f078edb143390f013b03046472edc0b`.
- Launch-result SHA-256:
  `a36cec5c2df043c861dbb4d197a32a5faa8ead7512aff4bd18dd676c17ddef13`.

A second live drill interrupted the Claude review leg itself, closing a gap
found by independent review:

- Evidence root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/pilot-interrupt-claude-r1`
- Result: terminal `INTERRUPTED`, exit `130`, policy not started, no automatic
  continuation, no orphaned review process, and the source repository remained
  clean.
- Cycle-result SHA-256:
  `cb0094e79e8a29612242bb30169b7c7949e464a0edab7a6d507735d3b0a5592b`.
- Launch-result SHA-256:
  `bc34b09ef29d60cd69c793ae46d0fe4d903eedfed6dc8afe5fd15c9436224c01`.

## Independent review

The first read-only review returned `REWORK` and identified three material
gaps: optional advisory findings were validated as if they were major,
interruption was not propagated from the Claude review leg, and repeated
operator interruption could break teardown evidence. The implementation was
reworked accordingly, negative regression tests were added, and the live
Claude-leg interruption drill above was completed. The final read-only review
is recorded in `CODE_REVIEW_R2.md`. That second review also returned bounded
`REWORK`; its medium findings were closed by enforcing completeness in the
builder itself, guaranteeing SIGINT-handler restoration with `finally`, making
the repeated-interrupt test deterministic, and adding negative fail-closed
tests. Its informational provenance concern was addressed by explicitly
labelling prior findings as reviewer-authored data rather than instructions.
The third independent review (`CODE_REVIEW_R3.md`) returned `ACCEPT`. Its one
remaining defense-in-depth medium finding was then closed by bringing the
detailed prior-finding validator to schema parity for mandatory fields and
category/severity rules. Its recommended bounded-wait and handler-entry
hardening were also applied before the final test run. The provenance concern
remains mitigated at prompt level; it is not treated as structurally eliminated.

## Boundaries confirmed

No push, deploy, Gateway, OpenClaw runtime/config, cron, systemd, daemon,
unattended mode, package, firewall, authentication, Synology, or source-project
commit changes were made.

## Recommendation

The two required technical repairs and their bounded rechecks are complete.
The orchestrator must remain `NOT ACTIVATED` until a separate durable readiness
decision is explicitly approved. The evidence supports returning it to
`READY FOR CONTROLLED MANUAL USE`; it does not support unattended operation or
automatic integration with OpenClaw.
