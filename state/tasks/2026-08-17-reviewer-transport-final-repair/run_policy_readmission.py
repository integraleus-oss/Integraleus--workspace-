#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


WORKSPACE = Path("/home/stanislav/.openclaw/workspace/agents/main")
INTEGRATION = WORKSPACE / "state/tasks/2026-08-12-orchestrator-integration"
sys.path.insert(0, str(INTEGRATION))

import local_orchestrator_runner


SOURCE = Path(
    "/home/stanislav/agent-runs/orchestrator-worktrees/"
    "manual-pilot-001-capability-grant-rework-final-review-transport-replay/"
    "live-review/policy-runs/run_home-agent-factory-manual-pilot-001.attempt-3"
)
INPUTS = WORKSPACE / (
    "state/tasks/2026-08-17-reviewer-transport-final-repair/"
    "policy-readmission-inputs"
)
RUNS = Path(
    "/home/stanislav/agent-runs/orchestrator-worktrees/"
    "manual-pilot-001-capability-grant-final-policy-readmission"
)
RUN_NAME = "run_home-agent-factory-manual-pilot-001.attempt-3-readmission"


def write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if INPUTS.exists() or RUNS.exists():
        raise RuntimeError("policy readmission output already exists")
    INPUTS.mkdir(parents=True)

    fixture = json.loads((SOURCE / "input-policy_fixture.json").read_text())
    prior_attempts = fixture["ledger"]["prior_attempts"]
    if len(prior_attempts) != 2 or prior_attempts[0].get("attempt_epoch") is not None:
        raise RuntimeError("unexpected source ledger shape")
    prior_attempts[0]["attempt_epoch"] = 1
    write(INPUTS / "policy.json", fixture)

    copies = {
        "verdict.json": "input-review_verdict.json",
        "manifest.json": "input-trusted_manifest.json",
        "binding.json": "input-projection_binding.json",
    }
    for target, source in copies.items():
        shutil.copyfile(SOURCE / source, INPUTS / target)

    bundle = {
        "document_type": "local_orchestrator_run",
        "schema_version": "1.0.0",
        "run_name": RUN_NAME,
        "policy_fixture": "policy.json",
        "review_verdict": "verdict.json",
        "trusted_manifest": "manifest.json",
        "projection_binding": "binding.json",
        "prior_findings": None,
    }
    write(INPUTS / "bundle.json", bundle)
    run_dir, result = local_orchestrator_runner.run(INPUTS / "bundle.json", RUNS)
    summary = {
        "document_type": "capability_grant_policy_readmission_result",
        "schema_version": "1.0.0",
        "outcome": result["outcome"],
        "rule_id": result["rule_id"],
        "run_dir": str(run_dir),
    }
    write(INPUTS / "result.json", summary)
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
