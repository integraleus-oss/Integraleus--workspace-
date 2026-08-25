# Independent review — Alpha-Presale doctor rework

Review the uncommitted diff against the controlled-manual pilot requirements.
The only allowed files are `alpha_presale/cli.py`, `tests/test_core.py`, and
`README.md`. No commit, transfer, push, deploy, licensing calculation, price
read, Web/API change, or customer-facing change is allowed.

Confirm whether the previous findings are closed:

1. Unreadable/non-UTF-8 schema, fixture, directory, and verify-script inputs
   must be represented in the single JSON report with exit 2, not crash.
2. `pyproject.toml` baseline configuration must be checked.
3. Commands declared through known shell variables must not be silently lost.
4. Success tests must not depend on host `node` or `rg` availability.
5. Non-executable local commands need regression coverage.
6. Shell control keywords must not be classified as PATH executables.

Also perform fresh Standards and Spec review for regressions, unsafe execution,
scope violations, and test gaps. Report findings by severity (blocker, major,
nit), with file and line. End with exactly one verdict: ACCEPT or REWORK.

The latest retry must also verify closure of: missing common shell builtins,
untested module-path root discovery, lack of a real `scripts/verify.sh` parser
smoke check, and lack of Python 3.10 fallback-parser coverage.

Known environment limitation: the full suite in this detached worktree fails
because the repository expects the sibling `data/licensing_automiq` corpus at
the canonical workspace layout. The focused doctor suite is the relevant
behavioral gate; do not treat unrelated missing-corpus failures as introduced
by this three-file diff unless the diff caused them.
