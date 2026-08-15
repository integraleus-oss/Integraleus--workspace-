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


OLD_RUN = Path("/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t02-instance-path-run")
PROJECT = Path("/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t02-instance-path")
OUTPUT = Path("/home/stanislav/agent-runs/orchestrator-worktrees/pilot-t02-targeted-replay-r5")
TASK = WORKSPACE / "state/tasks/2026-08-15-orchestrator-manual-pilot/trials/T02-instance-path"
PROMPT = Path(__file__).with_name("REVIEW_PROMPT.md")


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("targeted replay output already exists")
    attempt1 = OLD_RUN / "attempt-1/claude/live-review/policy-runs/run_home-agent-factory-pilot-t02.attempt-1"
    baseline = read(OLD_RUN / "attempt-1/claude/review-inputs/evidence.json")["baseline"]
    decision = read(attempt1 / "decision.json")
    registry = read(attempt1 / "registry-after.json")
    verdict = review_projection.normalize_derived_review_ids(read(attempt1 / "input-review_verdict.json"))
    details = {item["finding_id"]: {**item, "status": "open"} for item in verdict["findings"]}
    prior_context = {
        "budgets_after": decision["budgets_after"],
        "seen_nonces": ["run_home-agent-factory-pilot-t02.attempt-1-nonce"],
        "finding_registry": registry,
        "prior_finding_details": details,
        "prior_attempts": [],
        "last_decision": {key: decision[key] for key in
                          ("progress_identity", "decision_digest", "outcome", "rule_id")},
    }
    packet = read(TASK / "PRODUCTION_TASK.json")
    config = dict(packet["builder"])
    config["task_id"] = "home-agent-factory-t02-targeted-r1"
    config["repo_id"] = "home-agent-factory-t02-targeted-r1"
    config["review_instructions"] = str(TASK / "REVIEW_INSTRUCTIONS.md")
    config["policy_fixture"] = str(TASK / "POLICY.json")
    built = trusted_review_builder.build_review_inputs(
        PROJECT, OUTPUT / "review-inputs", baseline, config, 2, prior_context
    )
    review_prompt = OUTPUT / "review-prompt.md"
    review_prompt.write_text(
        PROMPT.read_text(encoding="utf-8")
        + "\n\nTrusted review inputs (read every sealed artifact):\n"
        + str(built["input_dir"])
        + "\nUse review-instructions.md and the exact review-verdict.schema.json there. "
          "Include every required property, including null-valued required fields.\n",
        encoding="utf-8",
    )
    prior = read(built["input_dir"] / "prior-findings.json")
    required = {"finding_id", "status", "title", "severity", "location", "rationale", "evidence"}
    if len(prior["findings"]) != len(registry["findings"]):
        raise RuntimeError("prior finding count mismatch")
    if any(not required.issubset(item) for item in prior["findings"]):
        raise RuntimeError("prior finding details are incomplete")
    anchored = sha256(built["seal"])
    result = live_review_cycle.run_cycle(
        PROJECT,
        review_prompt,
        built["bundle"],
        OUTPUT / "live-review",
        timeout_seconds=600,
        pre_admission_verify=lambda: trusted_review_builder.verify_seal(
            built["input_dir"], PROJECT, expected_seal_digest=anchored
        ),
        allow_format_retry=True,
        allow_contract_retry=True,
    )
    admitted = managed_policy_review.admit_live_review(result, OUTPUT / "live-review")
    summary = {
        "document_type": "t02_targeted_replay_result",
        "schema_version": "1.0.0",
        "prior_findings_count": len(prior["findings"]),
        "prior_findings_complete": True,
        "outcome": admitted.get("outcome"),
        "rule_id": admitted.get("rule_id"),
        "decision_dir": result.get("decision_dir"),
    }
    (OUTPUT / "replay-result.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
