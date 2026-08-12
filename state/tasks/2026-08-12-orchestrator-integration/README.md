# Local Orchestrator Integration

This slice connects the accepted reviewer contract and deterministic policy core
to bounded local agent launches without changing OpenClaw runtime configuration.

## Components

- `review_projection.py` validates a full `review_verdict` against the accepted
  contract and trusted manifest, then produces the narrow
  `trusted_review_projection` consumed by the policy core.
- `local_orchestrator_runner.py` snapshots explicit inputs into a new isolated
  run directory, invokes the adapter and policy, and writes deterministic JSON
  artifacts for audit and replay.
- `agent_launcher.py` invokes only the approved local Codex/Claude wrappers via
  fixed argv, bounds execution time, and preserves prompt/output/error digests.
- `live_review_cycle.py` admits exact JSON from a successful fresh Claude
  launch into the existing validator/projection/policy path. Failed launches
  never produce a policy decision.
- `tests/test_integration.py` covers all four policy outcomes and fail-closed
  integration boundaries.

## Trust boundary

The adapter does not infer bindings from reviewer prose. The coordinator must
provide a `review_projection_binding` containing the task/spec/run/epoch/tree
bindings and covered paths. The adapter cross-checks task, run, and attempt
against the contract-valid verdict. A mismatch produces no decision.

For targeted verification, only results whose exact status is `appears_fixed`
enter `verified_finding_ids`. `still_open`, `not_verifiable`, and
`no_longer_applicable` do not close registry findings.

Incomplete reviews are never projected: `unable_to_complete`, any blocking
limitation, or incomplete criterion coverage in a full review fails closed
before the policy call. Findings without a source location receive a stable
`_no_location/<reason>` sentinel and remain visible to policy.

Reviewer `infra_symptoms` and `injection_attempts_observed` are deliberately not
projected because the accepted policy core has no corresponding trusted fields.

## Run bundle

The runner accepts one JSON object:

```json
{
  "document_type": "local_orchestrator_run",
  "schema_version": "1.0.0",
  "run_name": "unique-run-name",
  "policy_fixture": "inputs/policy.json",
  "review_verdict": "inputs/review-verdict.json",
  "trusted_manifest": "inputs/trusted-manifest.json",
  "projection_binding": "inputs/projection-binding.json",
  "prior_findings": null
}
```

Paths are resolved relative to the run-bundle file. For targeted review,
`prior_findings` must point to the trusted prior-findings document.

Run locally:

```sh
python3 local_orchestrator_runner.py run-bundle.json --runs-root runs
```

Every `run_name` is single-use. Existing run directories are never overwritten.
Input snapshots are marked read-only for the local single-user workflow, and the directory contains validator output,
the projection, policy decision, and content digests.

## Verification

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile agent_launcher.py live_review_cycle.py review_projection.py local_orchestrator_runner.py tests/*.py
```

The accepted core regression suite must also remain green:

```sh
cd ../2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest discover -s tests
```
