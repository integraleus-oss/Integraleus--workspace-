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
- `managed_one_cycle.py` enforces a maximum of two implementation attempts and
  one rework transition; exhausted or malformed flows escalate.
- `managed_policy_review.py` admits only digest-matched durable policy output
  from a live-review directory and derives bounded rework instructions solely
  from policy-selected findings in the trusted projection.
- `requirements_traceability.py` anchors the owner's exact brief and hard-gates
  the immutable R01..R99 requirement/spec/task/acceptance proof chain.
- `blind_acceptance.py` runs read-only final acceptance without internal spec,
  task tracker, prior review prose, or orchestrator rationale.
- `evidence_dashboard.py` renders digest-verified evidence as static display-only HTML.
- `openclaw_foreground_adapter.py` runs one prebuilt manual packet in foreground;
  it has no commit, transfer, push, deploy, activation, cron, or Gateway capability.
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

When a full-review verdict is contract-valid but has incomplete
`criteria_coverage`, the live cycle permits one coverage/contract-only repair
using the same sealed inputs. This is not another substantive review pass. A
second incomplete reply still fails closed.

Reviewer `infra_symptoms` and `injection_attempts_observed` are deliberately not
projected because the accepted policy core has no corresponding trusted fields.

## Review-loop policy

Acceptance criteria are sealed before implementation and remain bound by their
digest through rework. The standard profile permits one initial full review and
one targeted closure review; it never starts an automatic third full review.
The targeted pass may open a new blocker or major only for a frozen-criterion
violation or a regression caused by rework. Other newly noticed concerns are
recorded as advisory follow-ups. If blocking work remains at the ceiling, the
cycle escalates with `follow_up_required=true` instead of looping.

Small controlled-manual tasks may use `--review-profile light`: all normal
scope, evidence, test, and transfer gates remain, but only one substantive
review is allowed. `ACCEPTED` remains impossible when policy reports any open
blocker or major.

Builder gates may optionally declare `expected_test_count`. When present, the
gate must emit exactly one TAP summary line in the form `# tests N`, and `N`
must equal the declared value. Only gate stdout is scanned. Gates without this field keep the existing
exit-code-only behavior.

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

## Production task packet generations

- `1.0.0` and `1.1.0`: legacy validation/replay only.
- `1.2.0`: requirements proof-chain validation/replay only.
- `1.3.0`: controlled execution with an anchored brief, manifest/spec/task
  proof chain, `manual + strict|normal`, and blind acceptance.

For revisions above one, the supplied previous manifest is a trusted packet
input and its immediate digest link is checked. The stateless runner does not
claim to reconstruct deeper history; durable owners retain all sealed revisions.

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
