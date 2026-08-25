# R4 Universal Integration Closure — Prepare Packet

## Goal

Prepare one bounded closure repair for the isolated R4 implementation. Close
only the three findings preserved by the independent review after the previous
builder repair.

## Fixed point

- Product source of truth: canonical Alpha BPR remains `b9e6377` and must not
  be changed during PREPARE or RUN.
- Input implementation: the isolated R4 repair worktree after the successful
  25-focused / 365-full gate run.
- Findings source: the sealed attempt-2 review projection and registry from the
  previous R4 repair cycle.

## Required closure

1. Preserve exact `Int64` values for identity transforms, including values
   above 2^53 and `long.MaxValue`; retain fail-closed overflow handling for
   genuine transforms. Add deterministic boundary tests.
2. Remove duplicated fixture JSON loading while preserving the name guard.
3. Extend ADR-009 consequences with the fail-closed behaviours introduced by
   R4 repair.

## Boundaries

- Allowed product paths: the existing integration validator, fixture store,
  integration tests, and ADR-009 only.
- No new product scope, modules, endpoints, write APIs, Alpha.Link, live Alpha
  Platform compatibility claims, credentials, VMs, services, Gateway access,
  commit to canonical Alpha BPR, transfer, push, or deploy.
- Build outputs remain in the external artifact root; no `bin/obj` in worktree.

## Acceptance

- The two exact identity-transform boundary tests are red on the pinned input
  baseline and green after implementation.
- Focused tests >= 27 and full tests >= 367.
- Restore, build, focused, full, and diff-check gates pass.
- Independent closure review reports 0 blocker and 0 major, with all six
  criteria satisfied.
- Implementation remains isolated until a later explicit transfer gate.

## Operator flow

`PREPARE -> explicit RUN -> closure verdict -> separate transfer decision`
