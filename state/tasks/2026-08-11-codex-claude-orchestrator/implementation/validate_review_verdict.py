#!/usr/bin/env python3
"""Validate reviewer output without producing an acceptance decision."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError:  # pragma: no cover - exercised only on missing dependency.
    jsonschema = None


DEFAULT_SCHEMA = Path(__file__).with_name("review-verdict.schema.json")
MAX_BYTES = 4 * 1024 * 1024
MAX_DEPTH = 32
REQUIRED_MANIFEST_SUBJECT_KEYS = (
    "task_id",
    "run_id",
    "attempt",
    "repo_id",
    "base_commit",
    "head_commit",
    "diff_digest",
    "changed_files_digest",
    "gate_run_id_pre",
    "gate_run_id_post",
)
REVIEW_MODES = {"initial_full", "targeted_verification", "final_full"}
COVERAGE_SCOPES = {"full", "targeted"}
PRIOR_FINDING_STATUSES = {"open", "fixed", "superseded", "not_verifiable", "no_longer_applicable"}


class TransportError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        pointer: str = "",
        failure_kind: str = "contract_failure",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.pointer = pointer
        self.failure_kind = failure_kind


def _reject_constant(value: str) -> None:
    raise TransportError("invalid_json_constant", f"non-standard JSON constant {value!r}")


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TransportError("duplicate_key", f"duplicate object key {key!r}")
        result[key] = value
    return result


def _json_pointer(parts: list[Any]) -> str:
    if not parts:
        return ""
    escaped = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(escaped)


def _canonical_digest(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _safe_json_int(value: str) -> int:
    digits = value[1:] if value.startswith("-") else value
    if len(digits) > 1000:
        raise TransportError("huge_number", "integer literal exceeds 1000 digits")
    return int(value)


def _max_depth(value: Any, depth: int = 1) -> int:
    if isinstance(value, dict):
        if not value:
            return depth
        return max(_max_depth(item, depth + 1) for item in value.values())
    if isinstance(value, list):
        if not value:
            return depth
        return max(_max_depth(item, depth + 1) for item in value)
    return depth


def _walk_strings(value: Any, parts: list[Any] | None = None) -> None:
    if parts is None:
        parts = []
    if isinstance(value, str):
        for index, char in enumerate(value):
            codepoint = ord(char)
            if 0xD800 <= codepoint <= 0xDFFF:
                raise TransportError(
                    "invalid_utf8",
                    "decoded JSON string contains a lone surrogate",
                    _json_pointer(parts + [f"char:{index}"]),
                )
            if codepoint < 0x20:
                raise TransportError(
                    "disallowed_control_character",
                    f"decoded JSON string contains U+{codepoint:04X}",
                    _json_pointer(parts + [f"char:{index}"]),
                )
        value.encode("utf-8", "strict")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _walk_strings(key, parts + [key])
            _walk_strings(item, parts + [key])
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_strings(item, parts + [index])


def parse_strict_json_bytes(data: bytes) -> dict[str, Any]:
    if not data:
        raise TransportError("empty_input", "input is empty")
    if len(data) > MAX_BYTES:
        raise TransportError("oversized_input", f"input exceeds {MAX_BYTES} bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TransportError("invalid_utf8", str(exc)) from exc
    if text.startswith("\ufeff"):
        raise TransportError("utf8_bom", "UTF-8 BOM is not allowed")
    if not text.strip():
        raise TransportError("empty_input", "input contains only whitespace")

    decoder = json.JSONDecoder(
        object_pairs_hook=_no_duplicate_object,
        parse_constant=_reject_constant,
        parse_int=_safe_json_int,
    )
    try:
        start = json.decoder.WHITESPACE.match(text, 0).end()
        parsed, end = decoder.raw_decode(text, start)
    except TransportError:
        raise
    except json.JSONDecodeError as exc:
        raise TransportError("json_parse_error", exc.msg, f"/char/{exc.pos}") from exc
    except RecursionError as exc:
        raise TransportError("too_deep", f"document nesting exceeds {MAX_DEPTH}") from exc
    except ValueError as exc:
        raise TransportError("json_parse_error", str(exc)) from exc
    if text[end:].strip():
        raise TransportError("trailing_json", "input contains trailing data after first JSON value")
    if not isinstance(parsed, dict):
        raise TransportError("non_object_root", "root JSON value must be an object")
    try:
        depth = _max_depth(parsed)
    except RecursionError as exc:
        raise TransportError("too_deep", f"document nesting exceeds {MAX_DEPTH}") from exc
    if depth > MAX_DEPTH:
        raise TransportError("too_deep", f"document nesting depth {depth} exceeds {MAX_DEPTH}")
    _walk_strings(parsed)
    return parsed


def load_json_file(path: Path) -> dict[str, Any]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise TransportError("io_error", str(exc), "", "tool_input_failure") from exc
    return parse_strict_json_bytes(data)


def schema_errors(document: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, str]]:
    if jsonschema is None:
        return [
            {
                "layer": "schema",
                "code": "missing_dependency",
                "message": "Python package jsonschema with Draft202012Validator is required",
                "pointer": "",
            }
        ]
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        pointer = _json_pointer(list(error.path))
        code = "schema_validation"
        message = f"{error.message} (schema keyword: {error.validator})"
        if error.validator == "not":
            message = "forbidden authority-shaped field is present (schema keyword: not)"
        elif error.validator in ("pattern", "minLength") and pointer.endswith("/excerpt"):
            code = "empty_evidence_excerpt"
            message = "evidence excerpt must contain non-whitespace text"
        errors.append(
            {
                "layer": "schema",
                "code": code,
                "message": message,
                "pointer": pointer,
                "schema_pointer": _json_pointer(list(error.schema_path)),
            }
        )
    return errors


def check_schema(schema: dict[str, Any]) -> list[dict[str, str]]:
    if jsonschema is None:
        return [
            {
                "layer": "schema",
                "code": "missing_dependency",
                "message": "Python package jsonschema with Draft202012Validator is required",
                "pointer": "",
            }
        ]
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        return [
            {
                "layer": "schema",
                "code": "invalid_schema",
                "message": exc.message,
                "pointer": _json_pointer(list(exc.path)),
            }
        ]
    return []


def _parse_timestamp(value: str, pointer: str, errors: list[dict[str, str]]) -> dt.datetime | None:
    try:
        if int(value[17:19]) > 59:
            raise ValueError
    except (ValueError, IndexError):
        errors.append(
            {
                "layer": "semantic",
                "code": "invalid_timestamp",
                "message": f"invalid UTC timestamp {value!r}",
                "pointer": pointer,
            }
        )
        return None
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        try:
            return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            errors.append(
                {
                    "layer": "semantic",
                    "code": "invalid_timestamp",
                    "message": f"invalid UTC timestamp {value!r}",
                    "pointer": pointer,
                }
            )
            return None


def _semantic_error(errors: list[dict[str, str]], code: str, message: str, pointer: str) -> None:
    errors.append({"layer": "semantic", "code": code, "message": message, "pointer": pointer})


def _tool_error(errors: list[dict[str, str]], code: str, message: str, pointer: str) -> None:
    errors.append({"layer": "tool", "code": code, "message": message, "pointer": pointer})


def _is_sha256_digest(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 71 and value.startswith("sha256:") and all(
        char in "0123456789abcdef" for char in value[7:]
    )


def _is_finding_id(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 36 and value.startswith("fnd_") and all(
        char in "0123456789abcdef" for char in value[4:]
    )


def expected_finding_id(fingerprint: dict[str, Any]) -> str:
    canonical = json.dumps(fingerprint, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "fnd_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]


def expected_occurrence_id(review_id: str, finding_id: str, ordinal: int) -> str:
    material = f"{review_id}\0{finding_id}\0{ordinal:06d}"
    return "occ_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def _collect_evidence_from_items(
    items: list[dict[str, Any]],
    found: dict[str, dict[str, Any]],
    errors: list[dict[str, str]],
    pointer: str,
) -> None:
    for index, item in enumerate(items):
        evidence_id = item.get("evidence_id")
        if isinstance(evidence_id, str):
            item_pointer = f"{pointer}/{index}"
            if evidence_id in found:
                _semantic_error(errors, "duplicate_evidence_id", f"duplicate evidence_id {evidence_id}", f"{item_pointer}/evidence_id")
            else:
                found[evidence_id] = item
            _validate_evidence_item(item, errors, item_pointer)


def _validate_evidence_item(item: dict[str, Any], errors: list[dict[str, str]], pointer: str) -> None:
    kind = item.get("kind")
    excerpt = item.get("excerpt")
    has_excerpt = isinstance(excerpt, str) and bool(excerpt.strip())
    artifact_ref = item.get("artifact_ref")
    digest = item.get("content_digest")
    has_digest_artifact = isinstance(artifact_ref, str) and isinstance(digest, str)
    command = item.get("command")

    if "excerpt" in item and not has_excerpt:
        _semantic_error(errors, "empty_evidence_excerpt", "evidence excerpt must contain non-whitespace text", f"{pointer}/excerpt")
    if "artifact_ref" in item and not isinstance(digest, str):
        _semantic_error(errors, "evidence_digest_required", "artifact evidence requires a non-null content_digest", f"{pointer}/content_digest")
    if kind in ("command_output", "test_result", "build_log") and not isinstance(command, dict):
        _semantic_error(errors, "kind_inconsistent_evidence", f"{kind} evidence requires a command block", f"{pointer}/command")
    if kind in ("gate_artifact", "artifact_reference") and not has_digest_artifact:
        _semantic_error(errors, "kind_inconsistent_evidence", f"{kind} evidence requires artifact_ref and content_digest", pointer)
    if not has_excerpt and not has_digest_artifact and not isinstance(command, dict):
        _semantic_error(errors, "insubstantial_evidence", "evidence requires excerpt, digest-bound artifact, or command output", pointer)


def _prior_open_ids(prior_findings: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for item in prior_findings["findings"]:
        if item["status"] == "open":
            result.add(item["finding_id"])
    return result


def _validate_prior_findings_structure(prior_findings: dict[str, Any], errors: list[dict[str, str]]) -> bool:
    start_count = len(errors)
    if prior_findings.get("document_type") != "prior_findings":
        _tool_error(errors, "prior_findings_invalid", "prior findings document_type must be prior_findings", "/document_type")
    if prior_findings.get("schema_version") != "1.0.0":
        _tool_error(errors, "prior_findings_invalid", "prior findings schema_version must be 1.0.0", "/schema_version")

    findings = prior_findings.get("findings")
    if not isinstance(findings, list):
        _tool_error(errors, "prior_findings_invalid", "prior findings findings must be an array", "/findings")
        return False

    seen: set[str] = set()
    for index, item in enumerate(findings):
        pointer = f"/findings/{index}"
        if not isinstance(item, dict):
            _tool_error(errors, "prior_findings_invalid", "prior findings entries must be objects", pointer)
            continue
        extra_keys = set(item) - {"finding_id", "status"}
        if extra_keys:
            _tool_error(errors, "prior_findings_invalid", "prior findings entries contain unsupported keys", pointer)
        finding_id = item.get("finding_id")
        if not _is_finding_id(finding_id):
            _tool_error(errors, "prior_findings_invalid", "prior findings entries require a valid finding_id", f"{pointer}/finding_id")
        elif finding_id in seen:
            _tool_error(errors, "prior_findings_invalid", f"duplicate prior finding_id {finding_id}", f"{pointer}/finding_id")
        else:
            seen.add(finding_id)
        status = item.get("status")
        if not isinstance(status, str) or status not in PRIOR_FINDING_STATUSES:
            _tool_error(errors, "prior_findings_invalid", "prior findings status is not an allowed value", f"{pointer}/status")
    return len(errors) == start_count


def _validate_trusted_manifest(
    document: dict[str, Any],
    trusted_manifest: dict[str, Any] | None,
    errors: list[dict[str, str]],
) -> tuple[set[str], str | None]:
    if trusted_manifest is None:
        _semantic_error(errors, "trusted_manifest_missing", "document validation requires coordinator-supplied --trusted-manifest", "")
        return set(), None
    if trusted_manifest.get("document_type") != "trusted_review_manifest":
        _tool_error(errors, "trusted_manifest_invalid", "trusted manifest document_type must be trusted_review_manifest", "/document_type")
        return set(), None

    manifest_subject = trusted_manifest.get("subject")
    document_subject = document.get("subject", {})
    if not isinstance(manifest_subject, dict):
        _tool_error(errors, "trusted_manifest_invalid", "trusted manifest subject must be an object", "/subject")
    else:
        for key in REQUIRED_MANIFEST_SUBJECT_KEYS:
            if key not in manifest_subject:
                _tool_error(errors, "trusted_manifest_invalid", f"trusted manifest subject is missing {key}", f"/subject/{key}")
        for key in manifest_subject:
            if key not in REQUIRED_MANIFEST_SUBJECT_KEYS:
                _tool_error(errors, "trusted_manifest_invalid", f"trusted manifest subject contains unsupported key {key}", f"/subject/{key}")
        for key, expected in manifest_subject.items():
            if document_subject.get(key) != expected:
                _semantic_error(errors, "trusted_binding_mismatch", f"subject.{key} differs from trusted manifest", f"/subject/{key}")

    inputs = document.get("review", {}).get("inputs_digest", {})
    for manifest_key, input_key in (
        ("acceptance_criteria_digest", "acceptance_criteria_digest"),
        ("review_instructions_digest", "review_instructions_digest"),
    ):
        expected = trusted_manifest.get(manifest_key)
        if not _is_sha256_digest(expected):
            _tool_error(errors, "trusted_manifest_invalid", f"trusted manifest {manifest_key} must be a sha256 digest", f"/{manifest_key}")
        elif inputs.get(input_key) != expected:
            _semantic_error(errors, "trusted_binding_mismatch", f"{input_key} differs from trusted manifest", f"/review/inputs_digest/{input_key}")

    expected_review_mode = trusted_manifest.get("expected_review_mode")
    if not isinstance(expected_review_mode, str) or expected_review_mode not in REVIEW_MODES:
        _tool_error(errors, "trusted_manifest_invalid", "trusted manifest expected_review_mode is missing or invalid", "/expected_review_mode")
        expected_review_mode = None
    elif document.get("review", {}).get("review_mode") != expected_review_mode:
        _semantic_error(errors, "trusted_binding_mismatch", "review_mode differs from trusted manifest", "/review/review_mode")

    expected_coverage_scope = trusted_manifest.get("expected_coverage_scope")
    if not isinstance(expected_coverage_scope, str) or expected_coverage_scope not in COVERAGE_SCOPES:
        _tool_error(errors, "trusted_manifest_invalid", "trusted manifest expected_coverage_scope is missing or invalid", "/expected_coverage_scope")
    elif document.get("coverage_scope") != expected_coverage_scope:
        _semantic_error(errors, "trusted_binding_mismatch", "coverage_scope differs from trusted manifest", "/coverage_scope")

    criteria = trusted_manifest.get("criteria")
    if not isinstance(criteria, list):
        _tool_error(errors, "trusted_manifest_invalid", "trusted manifest criteria must be an array", "/criteria")
        return set(), expected_review_mode
    if not criteria:
        _tool_error(errors, "trusted_manifest_invalid", "trusted manifest criteria must contain at least one criterion", "/criteria")
    criterion_ids: set[str] = set()
    trusted_statements: dict[str, str] = {}
    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            _tool_error(errors, "trusted_manifest_invalid", "trusted criterion entries must be objects", f"/criteria/{index}")
            continue
        extra_keys = set(criterion) - {"criterion_id", "statement_digest"}
        if extra_keys:
            _tool_error(errors, "trusted_manifest_invalid", "trusted criterion entries contain unsupported keys", f"/criteria/{index}")
        if not isinstance(criterion.get("criterion_id"), str) or not criterion["criterion_id"].strip():
            _tool_error(errors, "trusted_manifest_invalid", "trusted criterion entries require a non-empty criterion_id", f"/criteria/{index}/criterion_id")
            continue
        criterion_id = criterion["criterion_id"]
        if criterion_id in criterion_ids:
            _tool_error(errors, "trusted_manifest_invalid", f"duplicate trusted criterion_id {criterion_id}", f"/criteria/{index}/criterion_id")
        criterion_ids.add(criterion_id)
        if not _is_sha256_digest(criterion.get("statement_digest")):
            _tool_error(errors, "trusted_manifest_invalid", "trusted criterion entries require a statement_digest", f"/criteria/{index}/statement_digest")
        else:
            trusted_statements[criterion_id] = criterion["statement_digest"]

    coverage_by_id = {coverage.get("criterion_id"): coverage for coverage in document.get("criteria_coverage", []) if isinstance(coverage, dict)}
    for criterion_id, statement_digest in trusted_statements.items():
        coverage = coverage_by_id.get(criterion_id)
        if coverage is None:
            _semantic_error(errors, "missing_criteria_coverage", f"missing coverage for trusted criterion {criterion_id}", "/criteria_coverage")
        elif coverage.get("statement_digest") != statement_digest:
            _semantic_error(errors, "trusted_binding_mismatch", f"statement_digest differs for {criterion_id}", "/criteria_coverage")

    if document.get("review", {}).get("review_mode") in ("initial_full", "final_full") and criterion_ids:
        if set(coverage_by_id) != criterion_ids:
            _semantic_error(errors, "criteria_coverage_mismatch", "full review coverage must exactly match trusted criteria", "/criteria_coverage")
    return criterion_ids, expected_review_mode


def _validate_prior_findings(
    document: dict[str, Any],
    prior_findings: dict[str, Any] | None,
    errors: list[dict[str, str]],
    expected_review_mode: str | None = None,
) -> tuple[set[str], bool]:
    review_mode = document.get("review", {}).get("review_mode")
    requires_prior = (
        review_mode == "targeted_verification"
        or expected_review_mode == "targeted_verification"
        or isinstance(document.get("verification"), dict)
    )
    if not requires_prior:
        return set(), True
    if prior_findings is None:
        _semantic_error(errors, "prior_findings_missing", "verification requires coordinator-supplied --prior-findings", "")
        return set(), False
    if not _validate_prior_findings_structure(prior_findings, errors):
        return set(), False
    digest = _canonical_digest(prior_findings)
    review_digest = document.get("review", {}).get("inputs_digest", {}).get("prior_findings_digest")
    verification_digest = document.get("verification", {}).get("prior_findings_digest")
    if review_digest != digest:
        _semantic_error(errors, "prior_digest_mismatch", "review prior_findings_digest differs from canonical prior-findings digest", "/review/inputs_digest/prior_findings_digest")
    if verification_digest != digest:
        _semantic_error(errors, "prior_digest_mismatch", "verification prior_findings_digest differs from canonical prior-findings digest", "/verification/prior_findings_digest")
    return _prior_open_ids(prior_findings), True


def _parse_all_timestamps(
    value: Any,
    errors: list[dict[str, str]],
    pointer: str = "",
    review_window: tuple[dt.datetime | None, dt.datetime | None] = (None, None),
) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            child_pointer = f"{pointer}/{key}" if pointer else f"/{key}"
            if key in ("started_at", "completed_at", "collected_at", "observed_at") and isinstance(item, str):
                parsed = _parse_timestamp(item, child_pointer, errors)
                if key in ("collected_at", "observed_at") and parsed is not None:
                    started_at, completed_at = review_window
                    if started_at and completed_at and not (started_at <= parsed <= completed_at):
                        _semantic_error(errors, "timestamp_out_of_review_window", "per-run evidence timestamp is outside review window", child_pointer)
            else:
                _parse_all_timestamps(item, errors, child_pointer, review_window)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child_pointer = f"{pointer}/{index}" if pointer else f"/{index}"
            _parse_all_timestamps(item, errors, child_pointer, review_window)


def semantic_errors(
    document: dict[str, Any],
    trusted_manifest: dict[str, Any] | None = None,
    prior_findings: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    findings = document.get("findings", [])
    counts = document.get("counts", {})
    review = document.get("review", {})
    review_id = review.get("review_id", "")
    occurrence_ids: set[str] = set()
    finding_ids: set[str] = set()
    evidence_ids: dict[str, dict[str, Any]] = {}
    trusted_criteria, expected_review_mode = _validate_trusted_manifest(document, trusted_manifest, errors)
    open_prior_ids, prior_findings_valid = _validate_prior_findings(document, prior_findings, errors, expected_review_mode)

    actual_counts = {"blocker": 0, "major": 0, "nit": 0, "total": len(findings)}
    for index, finding in enumerate(findings, 1):
        pointer = f"/findings/{index - 1}"
        severity = finding.get("severity")
        if severity in ("blocker", "major", "nit"):
            actual_counts[severity] += 1

        occurrence_id = finding.get("occurrence_id")
        finding_id = finding.get("finding_id")
        if occurrence_id in occurrence_ids:
            _semantic_error(errors, "duplicate_occurrence_id", f"duplicate occurrence_id {occurrence_id}", f"{pointer}/occurrence_id")
        occurrence_ids.add(occurrence_id)
        if finding_id in finding_ids:
            _semantic_error(errors, "duplicate_finding_id", f"duplicate finding_id {finding_id}", f"{pointer}/finding_id")
        finding_ids.add(finding_id)

        fingerprint = finding.get("fingerprint", {})
        if fingerprint.get("category") != finding.get("category"):
            _semantic_error(errors, "fingerprint_mismatch", "fingerprint category does not match finding category", f"{pointer}/fingerprint/category")
        if fingerprint.get("criterion_id") != finding.get("criterion_id"):
            _semantic_error(errors, "fingerprint_mismatch", "fingerprint criterion_id does not match finding criterion_id", f"{pointer}/fingerprint/criterion_id")
        if isinstance(fingerprint, dict) and isinstance(finding_id, str):
            expected = expected_finding_id(fingerprint)
            if finding_id != expected:
                _semantic_error(errors, "finding_id_mismatch", f"expected {expected}", f"{pointer}/finding_id")
        if isinstance(review_id, str) and isinstance(finding_id, str) and isinstance(occurrence_id, str):
            expected = expected_occurrence_id(review_id, finding_id, index)
            if occurrence_id != expected:
                _semantic_error(errors, "occurrence_id_mismatch", f"expected {expected}", f"{pointer}/occurrence_id")

        location = finding.get("location")
        if isinstance(location, dict):
            start = location.get("start_line")
            end = location.get("end_line")
            if isinstance(start, int) and isinstance(end, int) and end < start:
                _semantic_error(errors, "bad_line_order", "end_line precedes start_line", f"{pointer}/location/end_line")
        if isinstance(location, dict) and "location_absent_reason" in finding:
            _semantic_error(errors, "location_conflict", "location and location_absent_reason are mutually exclusive", f"{pointer}/location_absent_reason")
        if finding.get("criterion_id") is None:
            if finding.get("category") == "acceptance_criterion_violation":
                _semantic_error(errors, "null_criterion_category_conflict", "acceptance_criterion_violation requires a criterion_id", f"{pointer}/category")
            rationale = finding.get("rationale", "")
            if not isinstance(rationale, str) or len(rationale.strip()) < 40:
                _semantic_error(errors, "null_criterion_reason_too_short", "null criterion_id requires a meaningful rationale", f"{pointer}/rationale")
        if finding.get("proposed_disposition") == "propose_superseded":
            supersedes = finding.get("supersedes_finding_id")
            if not isinstance(supersedes, str):
                _semantic_error(errors, "missing_supersession_reference", "propose_superseded requires supersedes_finding_id", f"{pointer}/supersedes_finding_id")
            elif supersedes == finding_id:
                _semantic_error(errors, "bad_supersession_reference", "finding cannot supersede itself", f"{pointer}/supersedes_finding_id")

        _collect_evidence_from_items(finding.get("evidence", []), evidence_ids, errors, f"{pointer}/evidence")

    verification = document.get("verification")
    result_ids: list[str] = []
    if isinstance(verification, dict):
        for index, result in enumerate(verification.get("results", [])):
            pointer = f"/verification/results/{index}"
            result_finding_id = result.get("finding_id")
            if isinstance(result_finding_id, str):
                result_ids.append(result_finding_id)
            _collect_evidence_from_items(result.get("evidence", []), evidence_ids, errors, f"{pointer}/evidence")
            if result.get("observed_status") == "appears_fixed":
                for ev_index, evidence in enumerate(result.get("evidence", [])):
                    if not (
                        isinstance(evidence.get("command"), dict)
                        or (isinstance(evidence.get("artifact_ref"), str) and isinstance(evidence.get("content_digest"), str))
                    ):
                        _semantic_error(errors, "weak_appears_fixed_evidence", "appears_fixed evidence requires command output or digest-bound artifact", f"{pointer}/evidence/{ev_index}")

    for index, symptom in enumerate(document.get("infra_symptoms", [])):
        _collect_evidence_from_items(symptom.get("evidence", []), evidence_ids, errors, f"/infra_symptoms/{index}/evidence")

    if counts != actual_counts:
        _semantic_error(errors, "count_mismatch", f"declared counts {counts!r} do not match {actual_counts!r}", "/counts")

    criteria_ids: set[str] = set()
    for index, coverage in enumerate(document.get("criteria_coverage", [])):
        pointer = f"/criteria_coverage/{index}"
        criterion_id = coverage.get("criterion_id")
        if criterion_id in criteria_ids:
            _semantic_error(errors, "duplicate_criterion_coverage", f"duplicate criterion_id {criterion_id}", f"{pointer}/criterion_id")
        criteria_ids.add(criterion_id)
        for evidence_id in coverage.get("evidence_ids", []):
            if evidence_id not in evidence_ids:
                _semantic_error(errors, "bad_evidence_reference", f"unknown evidence_id {evidence_id}", f"{pointer}/evidence_ids")
        for occurrence_id in coverage.get("linked_occurrence_ids", []):
            if occurrence_id not in occurrence_ids:
                _semantic_error(errors, "bad_occurrence_reference", f"unknown occurrence_id {occurrence_id}", f"{pointer}/linked_occurrence_ids")
        if trusted_criteria and criterion_id not in trusted_criteria:
            _semantic_error(errors, "criteria_coverage_mismatch", f"criterion {criterion_id} is not in trusted manifest", f"{pointer}/criterion_id")

    for index, limitation in enumerate(document.get("limitations", [])):
        for evidence_id in limitation.get("evidence_ids", []):
            if evidence_id not in evidence_ids:
                _semantic_error(errors, "bad_evidence_reference", f"unknown evidence_id {evidence_id}", f"/limitations/{index}/evidence_ids")

    if isinstance(verification, dict):
        prior_digest = review.get("inputs_digest", {}).get("prior_findings_digest")
        if prior_digest != verification.get("prior_findings_digest"):
            _semantic_error(errors, "prior_digest_mismatch", "verification digest differs from review input digest", "/verification/prior_findings_digest")
        if len(result_ids) != len(set(result_ids)):
            _semantic_error(errors, "duplicate_verification_finding_id", "verification results must contain each finding_id at most once", "/verification/results")
        if prior_findings is not None and prior_findings_valid and set(result_ids) != open_prior_ids:
            _semantic_error(errors, "prior_findings_coverage_mismatch", "verification results must exactly cover open prior finding IDs", "/verification/results")
        for index, result in enumerate(verification.get("results", [])):
            pointer = f"/verification/results/{index}"
            new_occurrence_id = result.get("new_occurrence_id")
            if result.get("observed_status") == "still_open":
                if new_occurrence_id not in occurrence_ids:
                    _semantic_error(errors, "bad_occurrence_reference", f"unknown new_occurrence_id {new_occurrence_id}", f"{pointer}/new_occurrence_id")
                else:
                    matching = [item for item in findings if item.get("occurrence_id") == new_occurrence_id]
                    if matching and matching[0].get("finding_id") != result.get("finding_id"):
                        _semantic_error(errors, "bad_occurrence_reference", "new occurrence finding_id mismatch", f"{pointer}/new_occurrence_id")

    started_at = _parse_timestamp(review.get("started_at", ""), "/review/started_at", errors)
    completed_at = _parse_timestamp(review.get("completed_at", ""), "/review/completed_at", errors)
    if started_at and completed_at and completed_at < started_at:
        _semantic_error(errors, "bad_timestamp_order", "completed_at precedes started_at", "/review/completed_at")
    _parse_all_timestamps(document, errors, review_window=(started_at, completed_at))

    finding_criteria = {
        finding.get("criterion_id"): finding.get("severity")
        for finding in findings
        if finding.get("criterion_id") is not None and finding.get("severity") in ("blocker", "major")
    }
    coverage_by_id = {coverage.get("criterion_id"): coverage for coverage in document.get("criteria_coverage", [])}
    for criterion_id in finding_criteria:
        status = coverage_by_id.get(criterion_id, {}).get("status")
        if status not in ("violated", "partially_satisfied"):
            _semantic_error(errors, "criterion_finding_contradiction", f"{criterion_id} has blocker/major finding but coverage is not violated", "/criteria_coverage")

    for index, finding in enumerate(findings):
        supersedes = finding.get("supersedes_finding_id")
        if isinstance(supersedes, str) and supersedes not in finding_ids and supersedes not in open_prior_ids:
            _semantic_error(errors, "bad_supersession_reference", f"unknown supersedes_finding_id {supersedes}", f"/findings/{index}/supersedes_finding_id")

    conclusion = document.get("conclusion", {})
    if conclusion.get("status") == "no_findings":
        coverage = document.get("criteria_coverage", [])
        if not coverage:
            _semantic_error(errors, "empty_clean_coverage", "no_findings requires reviewed criteria coverage", "/criteria_coverage")
        for index, item in enumerate(coverage):
            if item.get("status") in ("not_reviewed", "not_verifiable"):
                _semantic_error(errors, "unreviewed_clean_coverage", "no_findings cannot rely on unreviewed or unverifiable coverage", f"/criteria_coverage/{index}/status")
            if item.get("status") != "satisfied":
                _semantic_error(errors, "unclean_conclusion", "no_findings requires all covered criteria to be satisfied", f"/criteria_coverage/{index}/status")

    return errors


def _failure_result(
    mode: str,
    layers: dict[str, bool | None],
    errors: list[dict[str, str]],
    failure_kind: str = "contract_failure",
) -> dict[str, Any]:
    return {
        "mode": mode,
        "contract_valid": False,
        "failure_kind": failure_kind,
        "layers": layers,
        "errors": errors,
    }


def validate_document(
    document_path: Path,
    schema_path: Path = DEFAULT_SCHEMA,
    trusted_manifest_path: Path | None = None,
    prior_findings_path: Path | None = None,
) -> dict[str, Any]:
    try:
        schema = load_json_file(schema_path)
    except TransportError as exc:
        return _failure_result(
            "document",
            {"transport": None, "schema": False, "semantic": False},
            [{"layer": "tool", "code": exc.code, "message": str(exc), "pointer": exc.pointer}],
            exc.failure_kind,
        )
    schema_check = check_schema(schema)
    if schema_check:
        return _failure_result("document", {"transport": None, "schema": False, "semantic": False}, schema_check, "tool_input_failure")

    try:
        document = load_json_file(document_path)
    except TransportError as exc:
        layer = "tool" if exc.failure_kind == "tool_input_failure" else "transport"
        return _failure_result(
            "document",
            {"transport": False, "schema": False, "semantic": False},
            [{"layer": layer, "code": exc.code, "message": str(exc), "pointer": exc.pointer}],
            exc.failure_kind,
        )

    trusted_manifest = None
    if trusted_manifest_path is not None:
        try:
            trusted_manifest = load_json_file(trusted_manifest_path)
        except TransportError as exc:
            return _failure_result(
                "document",
                {"transport": True, "schema": True, "semantic": False},
                [{"layer": "tool", "code": exc.code, "message": str(exc), "pointer": exc.pointer}],
                exc.failure_kind,
            )

    prior_findings = None
    if prior_findings_path is not None:
        try:
            prior_findings = load_json_file(prior_findings_path)
        except TransportError as exc:
            return _failure_result(
                "document",
                {"transport": True, "schema": True, "semantic": False},
                [{"layer": "tool", "code": exc.code, "message": str(exc), "pointer": exc.pointer}],
                exc.failure_kind,
            )

    schema_failures = schema_errors(document, schema)
    if schema_failures:
        return _failure_result("document", {"transport": True, "schema": False, "semantic": False}, schema_failures)

    semantic_failures = semantic_errors(document, trusted_manifest, prior_findings)
    if semantic_failures:
        failure_kind = "tool_input_failure" if any(error.get("layer") == "tool" for error in semantic_failures) else "contract_failure"
        return _failure_result("document", {"transport": True, "schema": True, "semantic": False}, semantic_failures, failure_kind)
    return {
        "mode": "document",
        "contract_valid": not semantic_failures,
        "failure_kind": None,
        "layers": {"transport": True, "schema": True, "semantic": not semantic_failures},
        "errors": semantic_failures,
    }


def check_schema_file(schema_path: Path = DEFAULT_SCHEMA) -> dict[str, Any]:
    try:
        schema = load_json_file(schema_path)
    except TransportError as exc:
        return _failure_result(
            "schema_self_check",
            {"transport": False, "schema": False, "semantic": None},
            [{"layer": "tool", "code": exc.code, "message": str(exc), "pointer": exc.pointer}],
            exc.failure_kind,
        )
    failures = check_schema(schema)
    if failures:
        return _failure_result("schema_self_check", {"transport": True, "schema": False, "semantic": None}, failures, "tool_input_failure")
    return {
        "mode": "schema_self_check",
        "contract_valid": True,
        "failure_kind": None,
        "layers": {"transport": True, "schema": True, "semantic": None},
        "errors": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", nargs="?", type=Path, help="review verdict JSON document")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="schema path")
    parser.add_argument("--check-schema", action="store_true", help="validate the schema itself")
    parser.add_argument("--trusted-manifest", type=Path, help="coordinator-supplied subject and criteria bindings")
    parser.add_argument("--prior-findings", type=Path, help="coordinator-supplied prior findings for targeted verification")
    args = parser.parse_args(argv)

    if args.check_schema and args.document is not None:
        result = _failure_result(
            "schema_self_check",
            {"transport": None, "schema": None, "semantic": None},
            [{"layer": "tool", "code": "invalid_cli_usage", "message": "--check-schema cannot be combined with a document path", "pointer": ""}],
            "tool_input_failure",
        )
    elif args.check_schema:
        result = check_schema_file(args.schema)
    elif args.document is None:
        result = _failure_result(
            "document",
            {"transport": False, "schema": False, "semantic": False},
            [{"layer": "tool", "code": "missing_input", "message": "document path is required", "pointer": ""}],
            "tool_input_failure",
        )
    else:
        result = validate_document(args.document, args.schema, args.trusted_manifest, args.prior_findings)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    if result["contract_valid"]:
        return 0
    return 2 if result.get("failure_kind") == "tool_input_failure" else 1


if __name__ == "__main__":
    raise SystemExit(main())
