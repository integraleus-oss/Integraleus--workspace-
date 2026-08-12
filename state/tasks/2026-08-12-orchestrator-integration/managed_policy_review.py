#!/usr/bin/env python3
"""Admit one live-review result into the bounded managed-cycle controller."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ManagedReviewError(RuntimeError):
    pass


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def admit_live_review(result: dict[str, Any], cycle_root: Path) -> dict[str, Any]:
    """Return a policy-authenticated controller result, or fail closed."""
    if result.get("document_type") != "local_live_review_cycle_result" or result.get("status") != "DECIDED":
        raise ManagedReviewError("live review did not produce a decision")
    manifest = result.get("decision")
    if not isinstance(manifest, dict) or manifest.get("document_type") != "local_orchestrator_run_result":
        raise ManagedReviewError("live review has no policy result manifest")

    cycle_root = cycle_root.resolve()
    decision_dir_raw = result.get("decision_dir")
    if not isinstance(decision_dir_raw, str):
        raise ManagedReviewError("live review has no decision directory")
    decision_dir = Path(decision_dir_raw).resolve()
    if not decision_dir.is_relative_to(cycle_root) or not decision_dir.is_dir():
        raise ManagedReviewError("decision directory escapes live-review root")

    run_result_path = decision_dir / "run-result.json"
    decision_path = decision_dir / "decision.json"
    projection_path = decision_dir / "trusted-review-projection.json"
    if _read_json(run_result_path) != manifest:
        raise ManagedReviewError("policy result manifest does not match durable artifact")
    if manifest.get("decision_digest_file") != _sha256(decision_path):
        raise ManagedReviewError("policy decision digest mismatch")
    if manifest.get("projection_digest") != _sha256(projection_path):
        raise ManagedReviewError("review projection digest mismatch")

    decision = _read_json(decision_path)
    projection = _read_json(projection_path)
    if decision.get("outcome") != manifest.get("outcome") or decision.get("rule_id") != manifest.get("rule_id"):
        raise ManagedReviewError("manifest does not match policy decision")

    admitted = dict(manifest)
    if decision.get("outcome") == "REWORK":
        finding_by_id = {
            finding.get("finding_id"): finding
            for finding in projection.get("findings", [])
            if isinstance(finding, dict) and isinstance(finding.get("finding_id"), str)
        }
        requested_ids = []
        packet_lines: list[str] = []
        for directive in decision.get("directives", []):
            if not isinstance(directive, dict):
                continue
            if directive.get("type") == "FIX_FINDINGS":
                ids = directive.get("finding_ids")
                if isinstance(ids, list):
                    requested_ids.extend(item for item in ids if isinstance(item, str))
            elif directive.get("type") == "FIX_GATES" and isinstance(directive.get("gate_ids"), list):
                packet_lines.append("Fix and rerun only these failed mandatory gates: " + ", ".join(directive["gate_ids"]))
            elif directive.get("type") == "PROVIDE_EVIDENCE" and isinstance(directive.get("req_ids"), list):
                packet_lines.append("Provide only these required evidence artifacts: " + ", ".join(directive["req_ids"]))
            elif directive.get("type") == "REVIEW_ONLY_FULL":
                packet_lines.append("Run the required final full review only; do not change implementation files.")
        if requested_ids:
            if any(item not in finding_by_id for item in requested_ids):
                raise ManagedReviewError("REWORK decision references an unprojected finding")
            packet_lines.append("Fix only these policy-selected findings:")
            for finding_id in dict.fromkeys(requested_ids):
                finding = finding_by_id[finding_id]
                packet_lines.append(f"- {finding_id} [{finding.get('severity')}]: {finding.get('message')} ({finding.get('path')})")
        if not packet_lines:
            raise ManagedReviewError("REWORK decision has no supported bounded directive")
        packet = "\n".join(packet_lines)
        if len(packet.encode("utf-8")) > 8192:
            raise ManagedReviewError("derived rework packet exceeds controller limit")
        admitted["rework_packet"] = packet
    return admitted
