# Targeted Closure Review: Local Orchestrator Integration

Status: REWORK FIXED; TARGETED CLOSURE REQUIRED

Review only the bounded fixes for findings BLOCKER-1 and MAJOR/MINOR-2..6 in
`claude-review.md`. Do not broaden this into a fresh architecture review.

## Files in scope

- `claude-review.md` — original findings
- `review_projection.py` — adapter fixes
- `local_orchestrator_runner.py` — runner fixes
- `tests/test_integration.py` — exact regressions
- `README.md` — trust and audit-boundary wording
- `TASK_PACKET.md` and `EVIDENCE.md` — acceptance and evidence context

The accepted policy core under
`state/tasks/2026-08-11-codex-claude-orchestrator/implementation/` is read-only
context. It was not changed by this integration rework.

## Closure questions

1. Can an `unable_to_complete` review, a review with a blocking limitation, or
   a full review with incomplete criterion coverage still reach a policy
   decision?
2. Are locationless contract-valid findings retained deterministically?
3. Does every failure after run-directory creation leave `run-error.json` and
   no false acceptance artifact?
4. Does the success manifest include exit status and the run-bundle digest?
5. Are absolute/traversing/escaping bundle paths rejected before copying?
6. Does targeted `still_open` remain excluded from `verified_finding_ids`?
7. Did any fix weaken or duplicate the accepted policy core?

Report only remaining blocker or major findings caused by these bounded fixes.
For each finding give file/line, minimal failure scenario, and bounded remedy.
Minor or informational observations may be listed separately but do not block
closure. End with exactly one token on its own line:

- `TARGETED_PASS` if all original blocker/major findings are closed and no new
  blocker/major regression exists;
- `TARGETED_REWORK` otherwise.
