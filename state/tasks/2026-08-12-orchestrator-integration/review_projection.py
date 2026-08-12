#!/usr/bin/env python3
"""Validate a review verdict and build the narrow policy projection."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[3]
CORE = WORKSPACE / "state/tasks/2026-08-11-codex-claude-orchestrator/implementation"
if not (CORE / "orchestrator_policy.py").is_file():
    raise RuntimeError(f"accepted policy core not found: {CORE}")


class ProjectionError(ValueError):
    pass


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ProjectionError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_module("review_contract_validator", CORE / "validate_review_verdict.py")


def _load_json(path: Path) -> dict[str, Any]:
    value = VALIDATOR.load_json_file(path)
    if not isinstance(value, dict):
        raise ProjectionError(f"JSON root must be an object: {path}")
    return value


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def build_projection(
    verdict_path: Path,
    trusted_manifest_path: Path,
    projection_binding_path: Path,
    prior_findings_path: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validation = VALIDATOR.validate_document(
        verdict_path,
        trusted_manifest_path=trusted_manifest_path,
        prior_findings_path=prior_findings_path,
    )
    if not validation.get("contract_valid"):
        raise ProjectionError("review verdict is not contract-valid")

    verdict = _load_json(verdict_path)
    binding = _load_json(projection_binding_path)
    allowed = {
        "document_type", "schema_version", "task_id", "spec_digest", "run_id",
        "attempt_epoch", "reviewed_tree_digest", "covered_paths",
    }
    if set(binding) != allowed:
        raise ProjectionError("projection binding has missing or unknown fields")
    if binding.get("document_type") != "review_projection_binding" or binding.get("schema_version") != "1.0.0":
        raise ProjectionError("unsupported projection binding")

    review = verdict.get("review", {})
    subject = verdict.get("subject", {})
    conclusion = verdict.get("conclusion", {})
    if conclusion.get("status") == "unable_to_complete":
        raise ProjectionError("incomplete review cannot be projected")
    if any(item.get("blocking") is True for item in verdict.get("limitations", [])):
        raise ProjectionError("review has a blocking limitation")
    if review.get("review_mode") in ("initial_full", "final_full"):
        complete_statuses = {"satisfied", "violated", "partially_satisfied"}
        if any(item.get("status") not in complete_statuses for item in verdict.get("criteria_coverage", [])):
            raise ProjectionError("full review has incomplete criteria coverage")
    checks = (
        (binding["task_id"], subject.get("task_id"), "task_id"),
        (binding["run_id"], subject.get("run_id"), "run_id"),
        (binding["attempt_epoch"], subject.get("attempt"), "attempt_epoch"),
    )
    for expected, actual, name in checks:
        if expected != actual:
            raise ProjectionError(f"projection binding mismatch: {name}")
    if not isinstance(binding["covered_paths"], list) or not binding["covered_paths"]:
        raise ProjectionError("covered_paths must be a non-empty array")
    if any(not isinstance(item, str) or not item for item in binding["covered_paths"]):
        raise ProjectionError("covered_paths contains an invalid path")

    findings = []
    for finding in verdict.get("findings", []):
        location = finding.get("location") or {}
        path = location.get("path") or finding.get("fingerprint", {}).get("normalized_path")
        if path is None:
            reason = finding.get("location_absent_reason") or "unspecified"
            path = f"_no_location/{reason}"
        if not isinstance(path, str) or not path:
            raise ProjectionError("review finding has an invalid path")
        findings.append({
            "finding_id": finding["finding_id"],
            "occurrence_id": finding["occurrence_id"],
            "severity": finding["severity"],
            "path": path,
            "message": finding["title"],
        })

    verified_ids: list[str] = []
    verification = verdict.get("verification")
    if review.get("review_mode") == "targeted_verification":
        if not isinstance(verification, dict):
            raise ProjectionError("targeted verdict has no verification object")
        verified_ids = sorted(
            item["finding_id"]
            for item in verification.get("results", [])
            if item.get("observed_status") == "appears_fixed"
        )

    projection = {
        "document_type": "trusted_review_projection",
        "schema_version": "1.0.0",
        "task_id": binding["task_id"],
        "spec_digest": binding["spec_digest"],
        "run_id": binding["run_id"],
        "attempt_epoch": binding["attempt_epoch"],
        "review_id": review["review_id"],
        "review_digest": _digest(verdict),
        "review_mode": review["review_mode"],
        "coverage_scope": verdict["coverage_scope"],
        "reviewed_tree_digest": binding["reviewed_tree_digest"],
        "covered_paths": sorted(set(binding["covered_paths"])),
        "findings": sorted(findings, key=lambda item: (item["finding_id"], item["occurrence_id"])),
        "verified_finding_ids": verified_ids,
    }
    return projection, validation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("verdict", type=Path)
    parser.add_argument("--trusted-manifest", type=Path, required=True)
    parser.add_argument("--projection-binding", type=Path, required=True)
    parser.add_argument("--prior-findings", type=Path)
    args = parser.parse_args()
    try:
        projection, validation = build_projection(
            args.verdict, args.trusted_manifest, args.projection_binding, args.prior_findings
        )
        result = {"ok": True, "validation": validation, "projection": projection}
        code = 0
    except Exception as exc:
        result = {"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}
        code = 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
