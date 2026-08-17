#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


WORKSPACE = Path("/home/stanislav/.openclaw/workspace/agents/main")
INTEGRATION = WORKSPACE / "state/tasks/2026-08-12-orchestrator-integration"
sys.path.insert(0, str(INTEGRATION))

import live_review_cycle
import managed_policy_review
import review_projection
import trusted_review_builder


PROJECT = Path("/home/stanislav/agent-runs/orchestrator-worktrees/manual-pilot-001-capability-grant")
ATTEMPT_ONE = Path(
    "/home/stanislav/agent-runs/orchestrator-worktrees/"
    "manual-pilot-001-capability-grant-rework-review/live-review/policy-runs/"
    "run_home-agent-factory-manual-pilot-001.attempt-1"
)
ATTEMPT_ONE_INPUTS = Path(
    "/home/stanislav/agent-runs/orchestrator-worktrees/"
    "manual-pilot-001-capability-grant-rework-review/inputs"
)
OUTPUT = Path(
    "/home/stanislav/agent-runs/orchestrator-worktrees/"
    "manual-pilot-001-capability-grant-rework-targeted-review"
)
TASK = WORKSPACE / "state/tasks/2026-08-17-orchestrator-manual-pilot-001"
LOCAL_TASK = WORKSPACE / "state/tasks/2026-08-17-capability-grant-model-policy-rework"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("targeted review output already exists")

    decision = read(ATTEMPT_ONE / "decision.json")
    registry = read(ATTEMPT_ONE / "registry-after.json")
    verdict = review_projection.normalize_derived_review_ids(
        read(ATTEMPT_ONE / "input-review_verdict.json")
    )
    details = {item["finding_id"]: {**item, "status": "open"} for item in verdict["findings"]}
    prior_context = {
        "budgets_after": decision["budgets_after"],
        "seen_nonces": ["run_home-agent-factory-manual-pilot-001.attempt-1-nonce"],
        "finding_registry": registry,
        "prior_finding_details": details,
        "prior_attempts": [],
        "last_decision": {
            key: decision[key]
            for key in ("progress_identity", "decision_digest", "outcome", "rule_id")
        },
    }

    packet = read(TASK / "PRODUCTION_TASK.json")
    config = dict(packet["builder"])
    config["review_instructions"] = str(TASK / "REVIEW_INSTRUCTIONS.md")
    config["policy_fixture"] = str(TASK / "POLICY.json")
    baseline = read(ATTEMPT_ONE_INPUTS / "evidence.json")["baseline"]
    proof_chain = {
        "manifest": read(TASK / "REQUIREMENTS_MANIFEST.json"),
        "specification": read(TASK / "REQUIREMENTS_SPECIFICATION.json"),
        "task_map": read(TASK / "REQUIREMENTS_TASK_MAP.json"),
    }
    built = trusted_review_builder.build_review_inputs(
        PROJECT, OUTPUT / "inputs", baseline, config, 2, prior_context, proof_chain
    )
    anchored = digest(built["seal"])

    prompt = OUTPUT / "review-prompt.md"
    prompt.write_text(
        (LOCAL_TASK / "TARGETED_REVIEW_PROMPT.md").read_text(encoding="utf-8")
        + "\n\nTrusted sealed input directory:\n"
        + str(built["input_dir"])
        + "\n",
        encoding="utf-8",
    )
    result = live_review_cycle.run_cycle(
        PROJECT,
        prompt,
        built["bundle"],
        OUTPUT / "live-review",
        timeout_seconds=900,
        pre_admission_verify=lambda: trusted_review_builder.verify_seal(
            built["input_dir"], PROJECT, expected_seal_digest=anchored
        ),
        allow_format_retry=True,
        allow_contract_retry=True,
    )
    admitted = managed_policy_review.admit_live_review(result, OUTPUT / "live-review")
    summary = {
        "document_type": "capability_grant_targeted_review_result",
        "schema_version": "1.0.0",
        "outcome": admitted.get("outcome"),
        "rule_id": admitted.get("rule_id"),
        "decision_dir": result.get("decision_dir"),
        "seal_digest": anchored,
    }
    (OUTPUT / "result.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
