# Harness qualification evidence

## Outcome so far

Local qualification is PASS. Independent review is ACCEPTED.

The agreed four historical security slices were already executed from the
clean `3d9c27e` baseline on 2026-08-15. Re-running them would spend model limits
without adding independent evidence, so this qualification binds their sealed
results instead of launching duplicate Codex/Claude work.

## Harness changes

- `trusted_review_builder.py`
  - rejects review attempts outside `{1, 2}` before creating evidence;
  - requires the frozen acceptance-criteria digest on attempt 2;
  - exposes one digest function shared by builder-repair setup;
  - removes the unreachable third `final_full` builder mode.
- `production_cycle_cli.py`
  - carries the frozen criteria digest into authenticated builder repair.
- `tests/test_trusted_review_builder.py`
  - proves attempt 3 is rejected;
  - proves missing frozen digest is rejected;
  - proves a file inside a new untracked directory is resolved as the exact
    allowed file rather than the directory summary;
  - updates the initial-review policy expectation to prevent a removed third
    review from being impersonated.

Observed patch digest before review:
`sha256:08afd978df5b351f496930f737432ad6eec6db7ce01aadd26e1e1f9cff97a8a0`.

Final patch digest after review closure:
`sha256:93f3afe9bd9b881ba59a66efd96ed1a046e5aa12b4785358ce990ff25915be78`.

## Local qualification

Command, from the harness directory:

`python3 -m unittest discover -s tests`

Result: `177 tests`, `OK`, runtime `20.770s`.

Closure after reviewer nit: `177 tests`, `OK`, runtime `19.754s`;
`git diff --check` PASS.

The suite proves the requested matrix through deterministic fixtures:

- red: exit `1` with bounded diagnostic is classified
  `IMPLEMENTATION_FAILURE`;
- synthetic green: exact untracked `docs/evidence/report.md` is admitted and
  its content gate passes;
- clean restore: every fixture uses a temporary Git repository and teardown;
  the canonical target remains clean;
- infrastructure: timeout, exit `127`, and signal exits are
  `INFRASTRUCTURE_FAILURE` with no repair packet;
- unknown/exception: terminal records are written and no hidden continuation
  is admitted;
- malformed reviewer JSON: format/contract repair is bounded to one retry and
  the second malformed response fails closed;
- interrupt: launch and managed-cycle tests preserve `INTERRUPTED`, exit `130`,
  evidence, and no policy continuation;
- review ceiling: direct builder attempt 3 is now rejected.

The earlier root-level discovery command was intentionally not treated as a
product failure: running discovery from the wrong working directory produced
`ModuleNotFoundError: test_integration`. The canonical README command, executed
from the harness directory, passes.

## Bound historical replay results

- T01 pack slug: `ACCEPTED / R17_ACCEPT`, one Codex implementation, exact
  allowed paths. RESULT digest
  `sha256:9ed5529bef2d326891b4d3af70db5f33ff58c1ece72ce04ea1db1407ddca67f3`.
- T02 instance path: `ESCALATED / R12_FINDINGS_EXHAUSTED`, two bounded
  implementations. This run correctly exposed the old evidence-carry defect;
  no transfer was allowed. RESULT digest
  `sha256:1b9d4b528b15ca39ba353b3436262da0b54799c3794a7559211a6e5461a304c6`.
- T03 external methods: `ACCEPTED / R17_ACCEPT`, one implementation plus one
  bounded reviewer-contract repair. RESULT digest
  `sha256:d9668ebe005070b80920955134dc6205a5a3ad71e878c4beaef4fc05acb651b6`.
- T04 run-log ID: `ACCEPTED / R17_ACCEPT`, one implementation, exact allowed
  paths. RESULT digest
  `sha256:cebead3a0c0c6770bb7eee82ba6ae7c994a4d5c7f2c8c053151f85e74fa103e0`.

These are qualification evidence, not authorization to transfer their old
detached diffs. The relevant accepted product work has since been integrated
through later controlled tasks and the canonical repository is now clean at
`f93b744d65036cc6dc02a679b8b2cda3b8606ac8`.

## Current boundaries

- Canonical `/home/stanislav/projects/home-agent-factory`: clean on `main` at
  `f93b744`.
- Alpha BPR: untouched.
- Claude's diff and read-only wrappers both produced empty output and were
  rejected as invalid review transport. A bounded read-only Codex review was
  then completed and accepted: 0 blocker, 0 major, 1 nit. The nit (three dead
  normalized review slots) was fixed to two and closure-tested.
- No commit, push, deploy, Synology, Gateway, auth, config, cron, or system
  change.
