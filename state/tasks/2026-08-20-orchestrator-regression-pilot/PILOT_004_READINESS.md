# Pilot 004 Readiness

Status: INPUT REQUIRED — NOT LAUNCHED

## Ready

- canonical orchestrator: `0ebd3fe5`;
- regression safeguards: 7/7 focused, 159/159 integration, 87/87 policy core;
- Alpha BPR: clean at `b9e6377`;
- Codex limits: primary 94% of the five-hour window, reserve 67%;
- Claude authenticated, five-hour usage 0% at preflight.

## Missing launch input

No Pilot 004 implementation task, frozen acceptance criteria, allowed-path
boundary, or product test command has been approved. The first unchecked Track
F TODO is the real external read-only integration pilot. It requires a named
customer/test environment, endpoint/tag mapping, access approval, owners, and
fresh sanitized observation; these inputs cannot be invented or substituted
with Home evidence.

## Safe next decision

Choose one:

1. Pilot 004 targets the external Track F integration after the required
   customer/test inputs are supplied; or
2. approve a separately defined internal Alpha BPR implementation slice.

Until that choice, launching Codex would create scope rather than execute an
approved task, so the orchestrator remains fail-closed.
