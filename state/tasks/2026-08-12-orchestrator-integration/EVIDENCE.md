# Evidence: Local Orchestrator Integration

## Baseline

- Core commit: `e95faa7`
- Core task status: `COMPLETED`
- Core mechanical result: `ACCEPTED / R17_ACCEPT`
- Core verification before commit: 84/84 tests, `py_compile`, whitespace check

## Work log

- Created the integration task packet before implementation.
- No network, GitHub, Gateway, Synology, root, or runtime changes authorized or
  performed for this slice.
- Implemented `review_projection.py`. It calls the accepted contract validator,
  requires explicit coordinator bindings, and maps only contract-valid fields.
- Implemented `local_orchestrator_runner.py`. It creates isolated single-use run
  directories, snapshots inputs read-only, and writes validator, projection,
  decision, and digest artifacts.
- First integration run exposed an incorrect validator API name
  (`parse_json_file` vs `load_json_file`); fixed locally before green status.
- Test expectation was corrected from a guessed blocker rule to the core's
  actual `R11_OPEN_FINDINGS` contract.
- A synthetic empty clean review was rejected correctly because satisfied
  criteria require evidence. The acceptance regression now uses a contract-valid
  evidence-backed advisory nit, which the policy correctly permits.

## Verification results

Integration suite before review rework:

```text
Ran 9 tests in 0.451s
OK
```

Covered behaviors:

- contract-valid blocker -> `REWORK / R11_OPEN_FINDINGS`
- contract-valid final-full advisory nit -> `ACCEPTED / R17_ACCEPT`
- allowlisted runner failure -> `FAILED_INFRA`
- malformed trusted policy input -> `ESCALATED / R01_BINDING`
- invalid reviewer authority field -> no decision emitted
- binding mismatch -> fail closed
- identical replay inputs -> byte-identical decision
- existing run directory -> refused, never overwritten

Post-rework targeted verification, executed locally on 2026-08-12:

```text
Ran 14 tests in 0.639s
OK
```

The five added regressions prove:

- blocking limitations cannot project;
- incomplete full-review criterion coverage cannot project;
- locationless findings remain visible through a deterministic sentinel path;
- escaping bundle paths are rejected and recorded in `run-error.json`;
- targeted `still_open` never enters `verified_finding_ids`.

Accepted core regression suite after integration rework:

```text
Ran 84 tests in 2.985s
OK
```

Additional checks:

- `py_compile`: pass
- `git diff --check`: pass

## Pending gate

- Fresh independent Claude review returned `INTEGRATION_REWORK`: 1 blocker,
  2 major, 3 minor, and informational notes. Bash was denied in that review,
  so its findings were source-based; coordinator reproduction/tests remain the
  execution evidence.
- Rework closes incomplete-review false acceptance, locationless findings,
  unaudited failure paths, missing bundle/exit manifest fields, and input path
  traversal. Exact regressions were added, including targeted `still_open`.
- Fresh targeted closure review inspected every bounded fix. It confirmed all
  six original findings closed by construction and found no new blocker/major
  code regression. Its advisory result was `TARGETED_REWORK` only because this
  evidence file and the task packet still reported the pre-rework 9-test run.
- The requested suites were then executed independently: integration 14/14,
  accepted core 84/84, and `py_compile` passed. This refresh closes the sole
  remaining review gate without changing implementation code.
