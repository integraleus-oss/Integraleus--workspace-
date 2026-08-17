#!/usr/bin/env python3
"""Validate a review verdict and build the narrow policy projection."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import tempfile
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[3]
CORE = WORKSPACE / "state/tasks/2026-08-11-codex-claude-orchestrator/implementation"
if not (CORE / "orchestrator_policy.py").is_file():
    raise RuntimeError(f"accepted policy core not found: {CORE}")


class ProjectionError(ValueError):
    pass


class ContractValidationError(ProjectionError):
    """Contract failure carrying the deterministic validator report."""

    def __init__(self, validation: dict[str, Any]) -> None:
        self.validation = validation
        super().__init__(
            "review verdict is not contract-valid: "
            + json.dumps(validation, sort_keys=True, separators=(",", ":"))
        )


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ProjectionError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_module("review_contract_validator", CORE / "validate_review_verdict.py")
EVIDENCE_ID_RE = re.compile(r"^ev_[0-9a-f]{32}$")
COMMAND_EVIDENCE_KINDS = frozenset({"command_output", "test_result", "build_log"})
PRESERVED_VERIFICATION_STATUSES = frozenset({"still_open", "not_verifiable"})
POSITIVE_VERIFICATION_STATUSES = frozenset({"appears_fixed", "no_longer_applicable"})
EXPECTED_VERIFICATION_STATUSES = (
    PRESERVED_VERIFICATION_STATUSES | POSITIVE_VERIFICATION_STATUSES
)
EXPECTED_CRITERIA_STATUSES = frozenset({
    "satisfied", "violated", "partially_satisfied", "not_verifiable", "not_reviewed"
})
EVIDENCE_DEPENDENT_CRITERIA_STATUSES = frozenset({
    "satisfied", "partially_satisfied"
})
EXPECTED_VERIFICATION_METHODS = frozenset({
    "executed_test", "manual_execution", "code_inspection", "static_analysis",
    "gate_artifact_review", "not_attempted",
})


def _derive_fingerprint_keys(schema: dict[str, Any]) -> frozenset[str]:
    try:
        fingerprint = schema["$defs"]["fingerprint"]
        if not isinstance(fingerprint, dict):
            raise TypeError("fingerprint schema must be an object")
        properties = fingerprint["properties"]
        required = fingerprint["required"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("accepted fingerprint schema is unreadable") from exc
    allowed_schema_keys = {"type", "properties", "required", "additionalProperties"}
    if (
        set(fingerprint) != allowed_schema_keys
        or fingerprint.get("type") != "object"
        or not isinstance(properties, dict)
        or not isinstance(required, list)
        or fingerprint.get("additionalProperties") is not False
        or len(required) != len(set(required))
        or set(required) != set(properties)
    ):
        raise RuntimeError("accepted fingerprint schema is not a flat closed object")
    return frozenset(properties)


def _load_accepted_schema() -> dict[str, Any]:
    try:
        schema = json.loads(VALIDATOR.DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("accepted review schema is unreadable") from exc
    if not isinstance(schema, dict):
        raise RuntimeError("accepted review schema is unreadable")
    return schema


def _derive_positive_verification_statuses(schema: dict[str, Any]) -> frozenset[str]:
    try:
        statuses = schema["$defs"]["verification"]["properties"]["results"][
            "items"
        ]["properties"]["observed_status"]["enum"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("accepted verification status schema is unreadable") from exc
    if (
        not isinstance(statuses, list)
        or any(not isinstance(item, str) for item in statuses)
        or len(statuses) != len(set(statuses))
        or set(statuses) != EXPECTED_VERIFICATION_STATUSES
    ):
        raise RuntimeError("accepted verification status schema is unsupported")
    return POSITIVE_VERIFICATION_STATUSES


def _assert_criteria_contract_enums(schema: dict[str, Any]) -> None:
    try:
        properties = schema["$defs"]["criterion_coverage"]["properties"]
        statuses = properties["status"]["enum"]
        methods = properties["verification_method"]["enum"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("accepted criteria schema is unreadable") from exc
    if (
        not isinstance(statuses, list)
        or not isinstance(methods, list)
        or set(statuses) != EXPECTED_CRITERIA_STATUSES
        or len(statuses) != len(set(statuses))
        or set(methods) != EXPECTED_VERIFICATION_METHODS
        or len(methods) != len(set(methods))
    ):
        raise RuntimeError("accepted criteria schema is unsupported")


ACCEPTED_SCHEMA = _load_accepted_schema()
FINGERPRINT_KEYS = _derive_fingerprint_keys(ACCEPTED_SCHEMA)
SCHEMA_POSITIVE_VERIFICATION_STATUSES = _derive_positive_verification_statuses(
    ACCEPTED_SCHEMA
)
_assert_criteria_contract_enums(ACCEPTED_SCHEMA)


def _load_json(path: Path) -> dict[str, Any]:
    value = VALIDATOR.load_json_file(path)
    if not isinstance(value, dict):
        raise ProjectionError(f"JSON root must be an object: {path}")
    return value


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _list_items(value: Any) -> list[Any]:
    """Return list members without masking a malformed value from validation."""
    return value if isinstance(value, list) else []


def normalize_derived_review_ids(verdict: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize contract-derived IDs without changing review substance."""
    normalized = copy.deepcopy(verdict)
    review_id = normalized.get("review", {}).get("review_id")
    findings = normalized.get("findings")
    if not isinstance(review_id, str) or not isinstance(findings, list):
        return normalized
    occurrence_map: dict[str, str] = {}
    finding_map: dict[str, str] = {}
    for ordinal, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict) or not isinstance(finding.get("fingerprint"), dict):
            continue
        old_finding = finding.get("finding_id")
        old_occurrence = finding.get("occurrence_id")
        new_finding = VALIDATOR.expected_finding_id(finding["fingerprint"])
        new_occurrence = VALIDATOR.expected_occurrence_id(review_id, new_finding, ordinal)
        if isinstance(old_finding, str):
            finding_map[old_finding] = new_finding
        if isinstance(old_occurrence, str):
            occurrence_map[old_occurrence] = new_occurrence
        finding["finding_id"] = new_finding
        finding["occurrence_id"] = new_occurrence
    for coverage in _list_items(normalized.get("criteria_coverage", [])):
        if isinstance(coverage, dict) and isinstance(coverage.get("linked_occurrence_ids"), list):
            coverage["linked_occurrence_ids"] = [occurrence_map.get(item, item)
                                                   for item in coverage["linked_occurrence_ids"]]
    verification = normalized.get("verification")
    if isinstance(verification, dict):
        for result in _list_items(verification.get("results", [])):
            if not isinstance(result, dict):
                continue
            if isinstance(result.get("finding_id"), str):
                result["finding_id"] = finding_map.get(result["finding_id"], result["finding_id"])
            if isinstance(result.get("new_occurrence_id"), str):
                result["new_occurrence_id"] = occurrence_map.get(
                    result["new_occurrence_id"], result["new_occurrence_id"])
    return normalized


def normalize_transport_defects(
    verdict: dict[str, Any],
    validation_errors: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Repair only bounded, meaning-preserving reviewer transport defects."""
    normalized = copy.deepcopy(verdict)
    changes: list[dict[str, Any]] = []
    raw_errors = validation_errors
    verification = normalized.get("verification")

    for index, finding in enumerate(_list_items(normalized.get("findings", []))):
        if not isinstance(finding, dict):
            continue
        fingerprint = finding.get("fingerprint")
        if isinstance(fingerprint, dict):
            unknown_keys = sorted(set(fingerprint) - FINGERPRINT_KEYS)
            if unknown_keys:
                for key in unknown_keys:
                    del fingerprint[key]
                changes.append({
                    "operation": "remove_unknown_fingerprint_properties",
                    "pointer": f"/findings/{index}/fingerprint",
                    "removed": unknown_keys,
                })
        title = finding.get("title")
        if isinstance(title, str) and len(title) > 160:
            finding["title"] = title[:160]
            changes.append({
                "operation": "truncate_finding_title",
                "pointer": f"/findings/{index}/title",
                "original_length": len(title),
                "normalized_length": 160,
            })

    def discard_commandless_evidence(owner: dict[str, Any], pointer: str) -> bool:
        evidence = owner.get("evidence")
        if not isinstance(evidence, list):
            return False
        retained: list[Any] = []
        pending_changes: list[dict[str, Any]] = []
        for evidence_index, item in enumerate(evidence):
            item_pointer = f"{pointer}/{evidence_index}"
            item_errors = [
                error for error in raw_errors
                if isinstance(error.get("pointer"), str)
                and (
                    error["pointer"] == item_pointer
                    or error["pointer"].startswith(item_pointer + "/")
                )
            ]
            missing_command_errors = [
                error for error in item_errors
                if error.get("layer") == "semantic"
                and error.get("code") == "kind_inconsistent_evidence"
                and error.get("pointer") == item_pointer + "/command"
            ]
            secondary_missing_command_errors = [
                error for error in item_errors
                if error.get("layer") == "semantic"
                and error.get("code") == "weak_appears_fixed_evidence"
                and error.get("pointer") == item_pointer
            ]
            only_missing_command = (
                isinstance(item, dict)
                and item.get("kind") in COMMAND_EVIDENCE_KINDS
                and "command" not in item
                and len(missing_command_errors) == 1
                and len(secondary_missing_command_errors) <= 1
                and len(item_errors) == (
                    len(missing_command_errors) + len(secondary_missing_command_errors)
                )
            )
            if only_missing_command:
                pending_changes.append({
                    "operation": "discard_evidence_without_required_command",
                    "pointer": f"{pointer}/{evidence_index}",
                    "evidence_id": item.get("evidence_id"),
                    "kind": item.get("kind"),
                })
                continue
            retained.append(item)
        removed_any = bool(pending_changes) and bool(retained)
        if removed_any:
            owner["evidence"] = retained
            changes.extend(pending_changes)
        return removed_any

    for index, finding in enumerate(_list_items(normalized.get("findings", []))):
        if isinstance(finding, dict):
            discard_commandless_evidence(finding, f"/findings/{index}/evidence")
    if isinstance(verification, dict):
        for index, result in enumerate(_list_items(verification.get("results", []))):
            if isinstance(result, dict):
                removed = discard_commandless_evidence(
                    result, f"/verification/results/{index}/evidence"
                )
                if (
                    removed
                    and result.get("observed_status")
                    in SCHEMA_POSITIVE_VERIFICATION_STATUSES
                ):
                    result["observed_status"] = "not_verifiable"
                    changes.append({
                        "operation": "mark_verification_not_verifiable",
                        "pointer": f"/verification/results/{index}",
                        "reason": "invalid_command_evidence_discarded",
                    })
    for index, symptom in enumerate(_list_items(normalized.get("infra_symptoms", []))):
        if isinstance(symptom, dict):
            discard_commandless_evidence(symptom, f"/infra_symptoms/{index}/evidence")

    defined_evidence: set[str] = set()
    carriers: list[Any] = []
    for finding in _list_items(normalized.get("findings", [])):
        if isinstance(finding, dict) and isinstance(finding.get("evidence"), list):
            carriers.extend(finding["evidence"])
    if isinstance(verification, dict):
        for result in _list_items(verification.get("results", [])):
            if isinstance(result, dict) and isinstance(result.get("evidence"), list):
                carriers.extend(result["evidence"])
    for symptom in _list_items(normalized.get("infra_symptoms", [])):
        if isinstance(symptom, dict) and isinstance(symptom.get("evidence"), list):
            carriers.extend(symptom["evidence"])
    for evidence in carriers:
        if isinstance(evidence, dict) and isinstance(evidence.get("evidence_id"), str):
            defined_evidence.add(evidence["evidence_id"])

    for collection_name in ("criteria_coverage", "limitations"):
        for index, item in enumerate(_list_items(normalized.get(collection_name, []))):
            if not isinstance(item, dict) or not isinstance(item.get("evidence_ids"), list):
                continue
            original = item["evidence_ids"]
            if any(
                not isinstance(value, str) or EVIDENCE_ID_RE.fullmatch(value) is None
                for value in original
            ):
                continue
            retained = [value for value in original if value in defined_evidence]
            removed = [value for value in original if value not in defined_evidence]
            if not removed:
                continue
            item["evidence_ids"] = retained
            changes.append({
                "operation": "remove_undefined_evidence_ids",
                "pointer": f"/{collection_name}/{index}/evidence_ids",
                "removed": removed,
            })
            if (
                collection_name == "criteria_coverage"
                and item.get("status") in EVIDENCE_DEPENDENT_CRITERIA_STATUSES
            ):
                item["status"] = "not_verifiable"
                item["verification_method"] = "not_attempted"
                normalization_note = (
                    "Evidence references were undefined; criterion is not verifiable."
                )
                prior_notes = item.get("notes")
                if not isinstance(prior_notes, str) or not prior_notes:
                    item["notes"] = normalization_note
                changes.append({
                    "operation": "mark_criterion_not_verifiable",
                    "pointer": f"/criteria_coverage/{index}/status",
                    "reason": "undefined_evidence_reference_removed",
                })
    return normalized, changes


def build_projection(
    verdict_path: Path,
    trusted_manifest_path: Path,
    projection_binding_path: Path,
    prior_findings_path: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    transport_validation = VALIDATOR.validate_document(
        verdict_path,
        trusted_manifest_path=trusted_manifest_path,
        prior_findings_path=prior_findings_path,
    )
    if transport_validation.get("layers", {}).get("transport") is False:
        raise ContractValidationError(transport_validation)
    raw_verdict = _load_json(verdict_path)
    transport_normalized, transport_normalizations = normalize_transport_defects(
        raw_verdict, transport_validation.get("errors", [])
    )
    normalized_verdict = normalize_derived_review_ids(transport_normalized)
    validation_path = verdict_path
    temporary_path: Path | None = None
    try:
        if normalized_verdict != raw_verdict:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".json", delete=False) as handle:
                json.dump(normalized_verdict, handle, sort_keys=True, separators=(",", ":"))
                handle.write("\n")
                temporary_path = Path(handle.name)
            validation_path = temporary_path
        validation = VALIDATOR.validate_document(
            validation_path,
            trusted_manifest_path=trusted_manifest_path,
            prior_findings_path=prior_findings_path,
        )
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    if not validation.get("contract_valid"):
        raise ContractValidationError(validation)
    validation["transport_normalizations"] = transport_normalizations

    verdict = normalized_verdict
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
