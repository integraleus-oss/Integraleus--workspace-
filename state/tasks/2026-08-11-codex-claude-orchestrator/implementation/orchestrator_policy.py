#!/usr/bin/env python3
"""Deterministic orchestrator policy engine.

The public decision function is pure: it reads no files, calls no subprocesses,
uses no clock, and depends only on its explicit JSON-compatible inputs.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError:  # pragma: no cover - only exercised if dependency is absent.
    jsonschema = None


SCHEMA_VERSION = "1.0.0"
STATE_SCHEMA = Path(__file__).with_name("orchestrator-state-machine.schema.json")
REGISTRY_SCHEMA = Path(__file__).with_name("finding-registry.schema.json")
MAX_BYTES = 3 * 1024 * 1024
MAX_DEPTH = 32
MAX_LIST_ITEMS = 2000
MAX_MAPPING_KEYS = 500

OUTCOMES = {"REWORK", "ACCEPTED", "FAILED_INFRA", "ESCALATED"}
GATE_STATES = {"PASS", "FAIL", "MISSING", "SKIPPED", "TIMEOUT"}
SEVERITY_RANK = {"info": 0, "nit": 1, "minor": 1, "major": 2, "blocker": 3}
RANK_SEVERITY = {0: "info", 1: "nit", 2: "major", 3: "blocker"}
BLOCKING_RANK = SEVERITY_RANK["major"]
REGISTRY_STATUSES = {"open", "resolved_verified"}
REGISTRY_SEVERITIES = {"info", "nit", "major", "blocker"}
DECISION_REQUIRED_KEYS = {
    "document_type",
    "schema_version",
    "outcome",
    "rule_id",
    "reason_codes",
    "directives",
    "progress_identity",
    "budgets_after",
    "input_digests",
    "registry_digest_after",
    "decision_digest",
}
FORBIDDEN_REVIEW_AUTHORITY_KEYS = {
    "accept",
    "accepted",
    "approval",
    "approved",
    "decision",
    "downgraded",
    "resolved",
    "reviewer_verdict",
    "verdict",
    "waived",
}


class PolicyInputError(ValueError):
    def __init__(self, code: str, message: str, pointer: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.pointer = pointer


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


UNORDERED_DIGEST_LIST_PATHS = {
    ("execution_report", "evidence_artifacts"),
    ("execution_report", "failure_signatures"),
    ("execution_report", "subject", "changed_paths"),
    ("ledger", "expected_subject", "changed_paths"),
    ("ledger", "finding_registry", "findings"),
    ("ledger", "finding_registry", "findings", "*", "history"),
    ("ledger", "seen_nonces"),
    ("reviewer_report", "covered_paths"),
    ("reviewer_report", "findings"),
    ("reviewer_report", "verified_finding_ids"),
    ("task_policy", "infra_signature_allowlist"),
    ("task_policy", "required_evidence"),
}


def _path_matches(pattern: tuple[str, ...], path: tuple[str, ...]) -> bool:
    return len(pattern) == len(path) and all(expected == "*" or expected == actual for expected, actual in zip(pattern, path))


def _is_unordered_digest_list(path: tuple[str, ...]) -> bool:
    return any(_path_matches(pattern, path) for pattern in UNORDERED_DIGEST_LIST_PATHS)


def _json_safe_shape(value: Any, depth: int = 0) -> Any:
    if depth > MAX_DEPTH:
        return {"__type__": "too_deep"}
    if isinstance(value, dict):
        if len(value) > MAX_MAPPING_KEYS:
            return {"__type__": "too_many_keys", "count": len(value)}
        items = [[_json_safe_shape(key, depth + 1), _json_safe_shape(item, depth + 1)] for key, item in value.items()]
        return {"__type__": "dict", "items": sorted(items, key=lambda item: _canonical_bytes(item))}
    if isinstance(value, list):
        if len(value) > MAX_LIST_ITEMS:
            return {"__type__": "too_many_items", "count": len(value)}
        return {"__type__": "list", "items": [_json_safe_shape(item, depth + 1) for item in value]}
    if isinstance(value, tuple):
        if len(value) > MAX_LIST_ITEMS:
            return {"__type__": "too_many_items", "count": len(value)}
        return {"__type__": "tuple", "items": [_json_safe_shape(item, depth + 1) for item in value]}
    if isinstance(value, str) or value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value == value and value not in (float("inf"), float("-inf")):
            return value
        return {"__type__": "non_json_float"}
    return {"__type__": type(value).__name__}


def _canonical_sort_key(value: Any) -> bytes:
    try:
        return _canonical_bytes(value)
    except (TypeError, ValueError):
        return _canonical_bytes(_json_safe_shape(value))


def _safe_canonical_digest(value: Any) -> str:
    try:
        return canonical_digest(value)
    except (RecursionError, TypeError, ValueError):
        return canonical_digest({"invalid_json_shape": _json_safe_shape(value)})


def _normalized_for_digest(value: Any, path: tuple[str, ...] = ()) -> Any:
    if isinstance(value, dict):
        return {key: _normalized_for_digest(item, path + (str(key),)) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, list):
        item_path = path + ("*",)
        normalized = [_normalized_for_digest(item, item_path) for item in value]
        if _is_unordered_digest_list(path):
            return sorted(normalized, key=_canonical_sort_key)
        return normalized
    return value


def _json_pointer(parts: list[Any]) -> str:
    if not parts:
        return ""
    return "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def _reject_constant(value: str) -> None:
    raise PolicyInputError("invalid_json_constant", f"non-standard JSON constant {value!r}")


def _safe_json_int(value: str) -> int:
    digits = value[1:] if value.startswith("-") else value
    if len(digits) > 1000:
        raise PolicyInputError("huge_number", "integer literal exceeds 1000 digits")
    return int(value)


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PolicyInputError("duplicate_key", f"duplicate object key {key!r}")
        result[key] = value
    return result


def _walk_limits(value: Any, parts: list[Any] | None = None, depth: int = 1) -> None:
    if parts is None:
        parts = []
    if depth > MAX_DEPTH:
        raise PolicyInputError("too_deep", f"document nesting exceeds {MAX_DEPTH}", _json_pointer(parts))
    if isinstance(value, dict):
        if len(value) > MAX_MAPPING_KEYS:
            raise PolicyInputError("too_many_keys", f"object exceeds {MAX_MAPPING_KEYS} keys", _json_pointer(parts))
        for key, item in value.items():
            _walk_limits(key, parts + [key], depth + 1)
            _walk_limits(item, parts + [key], depth + 1)
    elif isinstance(value, list):
        if len(value) > MAX_LIST_ITEMS:
            raise PolicyInputError("too_many_items", f"array exceeds {MAX_LIST_ITEMS} items", _json_pointer(parts))
        for index, item in enumerate(value):
            _walk_limits(item, parts + [index], depth + 1)
    elif isinstance(value, str):
        for index, char in enumerate(value):
            codepoint = ord(char)
            if 0xD800 <= codepoint <= 0xDFFF:
                raise PolicyInputError("invalid_utf8", "decoded string contains lone surrogate", _json_pointer(parts + [f"char:{index}"]))
            if codepoint < 0x20:
                raise PolicyInputError(
                    "disallowed_control_character",
                    f"decoded string contains U+{codepoint:04X}",
                    _json_pointer(parts + [f"char:{index}"]),
                )
        value.encode("utf-8", "strict")


def parse_json_file(path: Path) -> dict[str, Any]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise PolicyInputError("io_error", str(exc)) from exc
    if not data:
        raise PolicyInputError("empty_input", "input is empty")
    if len(data) > MAX_BYTES:
        raise PolicyInputError("oversized_input", f"input exceeds {MAX_BYTES} bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PolicyInputError("invalid_utf8", str(exc)) from exc
    if text.startswith("\ufeff"):
        raise PolicyInputError("utf8_bom", "UTF-8 BOM is not allowed")
    decoder = json.JSONDecoder(
        object_pairs_hook=_no_duplicate_object,
        parse_constant=_reject_constant,
        parse_int=_safe_json_int,
    )
    try:
        start = json.decoder.WHITESPACE.match(text, 0).end()
        value, end = decoder.raw_decode(text, start)
    except PolicyInputError:
        raise
    except json.JSONDecodeError as exc:
        raise PolicyInputError("json_parse_error", exc.msg, f"/char/{exc.pos}") from exc
    if text[end:].strip():
        raise PolicyInputError("trailing_json", "input contains trailing JSON data")
    if not isinstance(value, dict):
        raise PolicyInputError("non_object_root", "root JSON value must be an object")
    _walk_limits(value)
    return value


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_sha256_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 71
        and value.startswith("sha256:")
        and all(char in "0123456789abcdef" for char in value[7:])
    )


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _unique_sorted_strings(value: Any) -> list[str]:
    return sorted({item for item in _as_list(value) if isinstance(item, str)})


def _has_duplicate_strings(value: list[Any]) -> bool:
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        if item in seen:
            return True
        seen.add(item)
    return False


def _ledger_for_digest(ledger: dict[str, Any]) -> dict[str, Any]:
    stripped = copy.deepcopy(ledger)
    if isinstance(stripped, dict):
        stripped.pop("terminal_decision", None)
    return stripped


def _input_digests(
    task_policy: dict[str, Any],
    ledger: dict[str, Any],
    execution_report: dict[str, Any],
    reviewer_report: dict[str, Any],
) -> dict[str, str]:
    return {
        "execution_report": _safe_canonical_digest(_normalized_for_digest(execution_report, ("execution_report",))),
        "ledger_pre": _safe_canonical_digest(_normalized_for_digest(_ledger_for_digest(ledger), ("ledger",))),
        "reviewer_report": _safe_canonical_digest(_normalized_for_digest(reviewer_report, ("reviewer_report",))),
        "task_policy": _safe_canonical_digest(_normalized_for_digest(task_policy, ("task_policy",))),
    }


def _rejected_input_digests(
    task_policy: Any,
    ledger: Any,
    execution_report: Any,
    reviewer_report: Any,
) -> dict[str, str]:
    return {
        "execution_report": canonical_digest({"rejected_input": _json_safe_shape(execution_report)}),
        "ledger_pre": canonical_digest({"rejected_input": _json_safe_shape(ledger)}),
        "reviewer_report": canonical_digest({"rejected_input": _json_safe_shape(reviewer_report)}),
        "task_policy": canonical_digest({"rejected_input": _json_safe_shape(task_policy)}),
    }


def _placeholder_input_digests() -> dict[str, str]:
    return {
        "execution_report": canonical_digest({"input_digest": "unavailable", "document": "execution_report"}),
        "ledger_pre": canonical_digest({"input_digest": "unavailable", "document": "ledger"}),
        "reviewer_report": canonical_digest({"input_digest": "unavailable", "document": "reviewer_report"}),
        "task_policy": canonical_digest({"input_digest": "unavailable", "document": "task_policy"}),
    }


def _enforce_decide_input_limits(
    task_policy: Any,
    ledger: Any,
    execution_report: Any,
    reviewer_report: Any,
) -> None:
    for name, value in (
        ("task_policy", task_policy),
        ("ledger", ledger),
        ("execution_report", execution_report),
        ("reviewer_report", reviewer_report),
    ):
        _walk_limits(value, [name])


def _empty_budget_state() -> dict[str, Any]:
    return {
        "rework_used": 0,
        "infra_total_used": 0,
        "infra_used_by_signature": {},
        "final_full_used": 0,
        "no_progress_streak": 0,
    }


def _safe_budget_state(ledger: Any) -> dict[str, Any]:
    result = _empty_budget_state()
    if not isinstance(ledger, dict):
        return result
    counters = ledger.get("counters")
    if not isinstance(counters, dict):
        return result
    for key in ("rework_used", "infra_total_used", "final_full_used", "no_progress_streak"):
        value = counters.get(key)
        if _is_nonnegative_int(value):
            result[key] = value
    by_sig = counters.get("infra_used_by_signature")
    if isinstance(by_sig, dict) and len(by_sig) <= MAX_MAPPING_KEYS:
        result["infra_used_by_signature"] = dict(
            sorted((key, value) for key, value in by_sig.items() if isinstance(key, str) and _is_nonnegative_int(value))
        )
    return result


def _budget_state(ledger: dict[str, Any]) -> dict[str, Any]:
    counters = _as_mapping(_as_mapping(ledger).get("counters"))
    return {
        "rework_used": counters.get("rework_used", 0),
        "infra_total_used": counters.get("infra_total_used", 0),
        "infra_used_by_signature": copy.deepcopy(counters.get("infra_used_by_signature", {})),
        "final_full_used": counters.get("final_full_used", 0),
        "no_progress_streak": counters.get("no_progress_streak", 0),
    }


def _with_decision_digest(decision: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(decision)
    result["decision_digest"] = canonical_digest({key: value for key, value in result.items() if key != "decision_digest"})
    return result


def _make_decision(
    outcome: str,
    rule_id: str,
    reason_codes: list[str],
    directives: list[dict[str, Any]],
    budgets_after: dict[str, Any],
    input_digests: dict[str, str],
    registry_after: dict[str, Any] | None = None,
    progress_identity: str | None = None,
) -> dict[str, Any]:
    decision: dict[str, Any] = {
        "document_type": "orchestrator_decision",
        "schema_version": SCHEMA_VERSION,
        "outcome": outcome,
        "rule_id": rule_id,
        "reason_codes": reason_codes,
        "directives": directives,
        "progress_identity": progress_identity,
        "budgets_after": budgets_after,
        "input_digests": input_digests,
        "registry_digest_after": canonical_digest(registry_after) if registry_after is not None else None,
    }
    return _with_decision_digest(decision)


def _escalated(
    rule_id: str,
    reason_codes: list[str],
    input_digests: dict[str, str],
    budgets_after: dict[str, Any],
    progress_identity: str | None = None,
) -> dict[str, Any]:
    return _make_decision(
        "ESCALATED",
        rule_id,
        reason_codes,
        [{"type": "ESCALATE_TO_HUMAN"}],
        budgets_after,
        input_digests,
        progress_identity=progress_identity,
    )


def _schema_issue(code: str, pointer: str = "") -> dict[str, str]:
    return {"code": code, "pointer": pointer}


def _validate_task_policy(task_policy: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(task_policy, dict):
        return [_schema_issue("task_policy_not_object")]
    allowed = {
        "document_type",
        "schema_version",
        "task_id",
        "spec_digest",
        "run_id",
        "mandatory_gates",
        "required_evidence",
        "infra_signature_allowlist",
        "budgets",
    }
    if set(task_policy) - allowed:
        errors.append(_schema_issue("unknown_task_policy_field"))
    for key in ("document_type", "schema_version", "task_id", "spec_digest", "run_id"):
        if not isinstance(task_policy.get(key), str) or not task_policy[key]:
            errors.append(_schema_issue("task_policy_missing_identity", f"/{key}"))
    if task_policy.get("document_type") != "orchestrator_task_policy":
        errors.append(_schema_issue("bad_task_policy_document_type", "/document_type"))
    if task_policy.get("schema_version") != SCHEMA_VERSION:
        errors.append(_schema_issue("bad_task_policy_schema_version", "/schema_version"))
    gates = task_policy.get("mandatory_gates")
    if not isinstance(gates, list) or not gates or any(not isinstance(item, str) or not item for item in gates):
        errors.append(_schema_issue("bad_mandatory_gates", "/mandatory_gates"))
    elif _has_duplicate_strings(gates):
        errors.append(_schema_issue("duplicate_mandatory_gate", "/mandatory_gates"))
    allowlist = task_policy.get("infra_signature_allowlist")
    if not isinstance(allowlist, list) or any(not isinstance(item, str) or not item for item in allowlist):
        errors.append(_schema_issue("bad_infra_allowlist", "/infra_signature_allowlist"))
    elif _has_duplicate_strings(allowlist):
        errors.append(_schema_issue("duplicate_infra_signature", "/infra_signature_allowlist"))
    required_evidence = task_policy.get("required_evidence")
    if not isinstance(required_evidence, list):
        errors.append(_schema_issue("bad_required_evidence", "/required_evidence"))
    else:
        seen: set[str] = set()
        for index, item in enumerate(required_evidence):
            if not isinstance(item, dict):
                errors.append(_schema_issue("bad_evidence_requirement", f"/required_evidence/{index}"))
                continue
            extra = set(item) - {"req_id", "digest", "digest_required"}
            if extra:
                errors.append(_schema_issue("unknown_evidence_requirement_field", f"/required_evidence/{index}"))
            req_id = item.get("req_id")
            if not isinstance(req_id, str) or not req_id:
                errors.append(_schema_issue("bad_evidence_req_id", f"/required_evidence/{index}/req_id"))
            elif req_id in seen:
                errors.append(_schema_issue("duplicate_evidence_req_id", f"/required_evidence/{index}/req_id"))
            else:
                seen.add(req_id)
            if item.get("digest_required", True) is not False and not isinstance(item.get("digest"), str):
                errors.append(_schema_issue("bad_evidence_digest", f"/required_evidence/{index}/digest"))
            if "digest_required" in item and not isinstance(item.get("digest_required"), bool):
                errors.append(_schema_issue("bad_digest_required", f"/required_evidence/{index}/digest_required"))
    budgets = task_policy.get("budgets")
    if not isinstance(budgets, dict):
        errors.append(_schema_issue("bad_budgets", "/budgets"))
    else:
        if set(budgets) - {"rework", "infra_total", "infra_per_signature", "final_full", "no_progress"}:
            errors.append(_schema_issue("unknown_budget_field", "/budgets"))
        for key in ("rework", "infra_total", "final_full", "no_progress"):
            if not _is_nonnegative_int(budgets.get(key)):
                errors.append(_schema_issue("bad_budget_counter", f"/budgets/{key}"))
        per_sig = budgets.get("infra_per_signature")
        if not isinstance(per_sig, dict) or any(not isinstance(key, str) or not _is_nonnegative_int(value) for key, value in _as_mapping(per_sig).items()):
            errors.append(_schema_issue("bad_per_signature_budget", "/budgets/infra_per_signature"))
    return errors


def _validate_registry_record(record: Any, pointer: str, seen_finding_ids: set[str]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(record, dict):
        return [_schema_issue("bad_registry_finding", pointer)]
    allowed = {"finding_id", "status", "effective_severity", "occurrence_count", "resolved_at", "history"}
    if set(record) - allowed:
        errors.append(_schema_issue("unknown_registry_finding_field", pointer))
    finding_id = record.get("finding_id")
    if not isinstance(finding_id, str) or not finding_id:
        errors.append(_schema_issue("bad_registry_finding_id", f"{pointer}/finding_id"))
    elif finding_id in seen_finding_ids:
        errors.append(_schema_issue("duplicate_registry_finding_id", f"{pointer}/finding_id"))
    else:
        seen_finding_ids.add(finding_id)
    status = record.get("status")
    if not isinstance(status, str) or status not in REGISTRY_STATUSES:
        errors.append(_schema_issue("bad_registry_status", f"{pointer}/status"))
    severity = record.get("effective_severity")
    if not isinstance(severity, str) or severity not in REGISTRY_SEVERITIES:
        errors.append(_schema_issue("bad_registry_effective_severity", f"{pointer}/effective_severity"))
    occurrence_count = record.get("occurrence_count")
    if not _is_nonnegative_int(occurrence_count):
        errors.append(_schema_issue("bad_registry_occurrence_count", f"{pointer}/occurrence_count"))
    resolved_at = record.get("resolved_at")
    if status == "open" and resolved_at is not None:
        errors.append(_schema_issue("bad_registry_resolved_at", f"{pointer}/resolved_at"))
    elif status == "resolved_verified":
        if not isinstance(resolved_at, dict):
            errors.append(_schema_issue("bad_registry_resolved_at", f"{pointer}/resolved_at"))
        else:
            if set(resolved_at) - {"review_id", "tree_digest"}:
                errors.append(_schema_issue("unknown_registry_resolved_at_field", f"{pointer}/resolved_at"))
            if not isinstance(resolved_at.get("review_id"), str) or not resolved_at["review_id"]:
                errors.append(_schema_issue("bad_registry_resolved_review_id", f"{pointer}/resolved_at/review_id"))
            if not isinstance(resolved_at.get("tree_digest"), str) or not resolved_at["tree_digest"]:
                errors.append(_schema_issue("bad_registry_resolved_tree_digest", f"{pointer}/resolved_at/tree_digest"))
    history = record.get("history")
    if not isinstance(history, list):
        errors.append(_schema_issue("bad_registry_history", f"{pointer}/history"))
        return errors
    if _is_nonnegative_int(occurrence_count) and occurrence_count != len(history):
        errors.append(_schema_issue("bad_registry_occurrence_count", f"{pointer}/occurrence_count"))
    seen_history_keys: set[tuple[str, str]] = set()
    for index, entry in enumerate(history):
        entry_pointer = f"{pointer}/history/{index}"
        if not isinstance(entry, dict):
            errors.append(_schema_issue("bad_registry_history_entry", entry_pointer))
            continue
        allowed_entry = {"review_id", "occurrence_id", "severity", "path", "tree_digest"}
        if set(entry) - allowed_entry:
            errors.append(_schema_issue("unknown_registry_history_field", entry_pointer))
        review_id = entry.get("review_id")
        occurrence_id = entry.get("occurrence_id")
        if not isinstance(review_id, str) or not review_id:
            errors.append(_schema_issue("bad_registry_history_review_id", f"{entry_pointer}/review_id"))
        if not isinstance(occurrence_id, str) or not occurrence_id:
            errors.append(_schema_issue("bad_registry_history_occurrence_id", f"{entry_pointer}/occurrence_id"))
        if isinstance(review_id, str) and isinstance(occurrence_id, str):
            history_key = (review_id, occurrence_id)
            if history_key in seen_history_keys:
                errors.append(_schema_issue("duplicate_registry_history_entry", entry_pointer))
            seen_history_keys.add(history_key)
        if not isinstance(entry.get("severity"), str) or entry["severity"] not in REGISTRY_SEVERITIES:
            errors.append(_schema_issue("bad_registry_history_severity", f"{entry_pointer}/severity"))
        if not isinstance(entry.get("path"), str) or not entry["path"]:
            errors.append(_schema_issue("bad_registry_history_path", f"{entry_pointer}/path"))
        if not isinstance(entry.get("tree_digest"), str) or not entry["tree_digest"]:
            errors.append(_schema_issue("bad_registry_history_tree_digest", f"{entry_pointer}/tree_digest"))
    return errors


def _validate_finding_registry(registry: Any, pointer: str = "/finding_registry") -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(registry, dict):
        return [_schema_issue("bad_finding_registry", pointer)]
    if set(registry) - {"document_type", "schema_version", "findings"}:
        errors.append(_schema_issue("unknown_finding_registry_field", pointer))
    if registry.get("document_type") != "finding_registry":
        errors.append(_schema_issue("bad_finding_registry_document_type", f"{pointer}/document_type"))
    if registry.get("schema_version") != SCHEMA_VERSION:
        errors.append(_schema_issue("bad_finding_registry_schema_version", f"{pointer}/schema_version"))
    findings = registry.get("findings")
    if not isinstance(findings, list):
        errors.append(_schema_issue("bad_finding_registry_findings", f"{pointer}/findings"))
        return errors
    seen_finding_ids: set[str] = set()
    for index, record in enumerate(findings):
        errors.extend(_validate_registry_record(record, f"{pointer}/findings/{index}", seen_finding_ids))
    return errors


def _validate_ledger(ledger: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(ledger, dict):
        return [_schema_issue("ledger_not_object")]
    allowed = {
        "document_type",
        "schema_version",
        "task_id",
        "spec_digest",
        "run_id",
        "current_epoch",
        "last_epoch",
        "seen_nonces",
        "expected_subject",
        "counters",
        "finding_registry",
        "prior_attempts",
        "terminal_decision",
    }
    if set(ledger) - allowed:
        errors.append(_schema_issue("unknown_ledger_field"))
    if ledger.get("document_type") != "orchestrator_ledger":
        errors.append(_schema_issue("bad_ledger_document_type", "/document_type"))
    if ledger.get("schema_version") != SCHEMA_VERSION:
        errors.append(_schema_issue("bad_ledger_schema_version", "/schema_version"))
    for key in ("task_id", "spec_digest", "run_id"):
        if not isinstance(ledger.get(key), str) or not ledger[key]:
            errors.append(_schema_issue("ledger_missing_binding", f"/{key}"))
    for key in ("current_epoch", "last_epoch"):
        if not _is_nonnegative_int(ledger.get(key)):
            errors.append(_schema_issue("bad_ledger_epoch", f"/{key}"))
    if not isinstance(ledger.get("seen_nonces"), list) or any(not isinstance(item, str) for item in _as_list(ledger.get("seen_nonces"))):
        errors.append(_schema_issue("bad_seen_nonces", "/seen_nonces"))
    expected = ledger.get("expected_subject")
    if not isinstance(expected, dict):
        errors.append(_schema_issue("bad_expected_subject", "/expected_subject"))
    else:
        if set(expected) - {"tree_digest", "changed_paths"}:
            errors.append(_schema_issue("unknown_expected_subject_field", "/expected_subject"))
        if not isinstance(expected.get("tree_digest"), str) or not expected["tree_digest"]:
            errors.append(_schema_issue("bad_expected_tree_digest", "/expected_subject/tree_digest"))
        if not isinstance(expected.get("changed_paths"), list) or any(not isinstance(item, str) for item in _as_list(expected.get("changed_paths"))):
            errors.append(_schema_issue("bad_expected_changed_paths", "/expected_subject/changed_paths"))
    counters = ledger.get("counters")
    if not isinstance(counters, dict):
        errors.append(_schema_issue("bad_ledger_counters", "/counters"))
    else:
        if set(counters) - {"rework_used", "infra_total_used", "infra_used_by_signature", "final_full_used", "no_progress_streak"}:
            errors.append(_schema_issue("unknown_counter_field", "/counters"))
        for key in ("rework_used", "infra_total_used", "final_full_used", "no_progress_streak"):
            if not _is_nonnegative_int(counters.get(key)):
                errors.append(_schema_issue("bad_ledger_counter", f"/counters/{key}"))
        by_sig = counters.get("infra_used_by_signature")
        if not isinstance(by_sig, dict) or any(not isinstance(key, str) or not _is_nonnegative_int(value) for key, value in _as_mapping(by_sig).items()):
            errors.append(_schema_issue("bad_infra_used_by_signature", "/counters/infra_used_by_signature"))
    errors.extend(_validate_finding_registry(ledger.get("finding_registry")))
    if not isinstance(ledger.get("prior_attempts"), list):
        errors.append(_schema_issue("bad_prior_attempts", "/prior_attempts"))
    else:
        seen_attempt_epochs: set[int] = set()
        for index, attempt in enumerate(ledger["prior_attempts"]):
            pointer = f"/prior_attempts/{index}"
            if not isinstance(attempt, dict):
                errors.append(_schema_issue("bad_prior_attempt", pointer))
                continue
            allowed_attempt = {"attempt_epoch", "progress_identity", "decision_digest", "outcome", "rule_id"}
            if set(attempt) - allowed_attempt:
                errors.append(_schema_issue("unknown_prior_attempt_field", pointer))
            attempt_epoch = attempt.get("attempt_epoch")
            if not _is_nonnegative_int(attempt_epoch):
                errors.append(_schema_issue("bad_prior_attempt_epoch", f"{pointer}/attempt_epoch"))
            elif attempt_epoch in seen_attempt_epochs:
                errors.append(_schema_issue("duplicate_prior_attempt_epoch", f"{pointer}/attempt_epoch"))
            else:
                seen_attempt_epochs.add(attempt_epoch)
            for digest_key in ("progress_identity", "decision_digest"):
                if not _is_sha256_digest(attempt.get(digest_key)):
                    errors.append(_schema_issue("bad_prior_attempt_digest", f"{pointer}/{digest_key}"))
            if not isinstance(attempt.get("outcome"), str) or attempt["outcome"] not in OUTCOMES:
                errors.append(_schema_issue("bad_prior_attempt_outcome", f"{pointer}/outcome"))
            if not isinstance(attempt.get("rule_id"), str) or not attempt["rule_id"].startswith("R"):
                errors.append(_schema_issue("bad_prior_attempt_rule_id", f"{pointer}/rule_id"))
    terminal = ledger.get("terminal_decision")
    if terminal is not None and not isinstance(terminal, dict):
        errors.append(_schema_issue("bad_terminal_decision", "/terminal_decision"))
    return errors


def _validate_execution_report(execution_report: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(execution_report, dict):
        return [_schema_issue("execution_report_not_object")]
    allowed = {
        "document_type",
        "schema_version",
        "task_id",
        "spec_digest",
        "run_id",
        "attempt_epoch",
        "nonce",
        "subject",
        "exit_status",
        "failure_signatures",
        "gate_results",
        "evidence_artifacts",
        "payload",
        "payload_digest",
    }
    if set(execution_report) - allowed:
        errors.append(_schema_issue("unknown_execution_report_field"))
    if execution_report.get("document_type") != "execution_report":
        errors.append(_schema_issue("bad_execution_document_type", "/document_type"))
    if execution_report.get("schema_version") != SCHEMA_VERSION:
        errors.append(_schema_issue("bad_execution_schema_version", "/schema_version"))
    for key in ("task_id", "spec_digest", "run_id", "nonce"):
        if not isinstance(execution_report.get(key), str) or not execution_report[key]:
            errors.append(_schema_issue("execution_missing_binding", f"/{key}"))
    if not _is_nonnegative_int(execution_report.get("attempt_epoch")):
        errors.append(_schema_issue("bad_attempt_epoch", "/attempt_epoch"))
    if execution_report.get("exit_status") not in ("OK", "FAILED"):
        errors.append(_schema_issue("bad_exit_status", "/exit_status"))
    subject = execution_report.get("subject")
    if not isinstance(subject, dict):
        errors.append(_schema_issue("bad_execution_subject", "/subject"))
    else:
        if set(subject) - {"tree_digest", "changed_paths"}:
            errors.append(_schema_issue("unknown_execution_subject_field", "/subject"))
        if not isinstance(subject.get("tree_digest"), str) or not subject["tree_digest"]:
            errors.append(_schema_issue("bad_execution_tree_digest", "/subject/tree_digest"))
        if not isinstance(subject.get("changed_paths"), list) or any(not isinstance(item, str) for item in _as_list(subject.get("changed_paths"))):
            errors.append(_schema_issue("bad_execution_changed_paths", "/subject/changed_paths"))
    signatures = execution_report.get("failure_signatures")
    if not isinstance(signatures, list) or any(not isinstance(item, str) for item in _as_list(signatures)):
        errors.append(_schema_issue("bad_failure_signatures", "/failure_signatures"))
    elif _has_duplicate_strings(signatures):
        errors.append(_schema_issue("duplicate_failure_signature", "/failure_signatures"))
    gates = execution_report.get("gate_results")
    if not isinstance(gates, dict) or any(not isinstance(key, str) or not isinstance(value, str) or value not in GATE_STATES for key, value in _as_mapping(gates).items()):
        errors.append(_schema_issue("bad_gate_results", "/gate_results"))
    artifacts = execution_report.get("evidence_artifacts")
    if not isinstance(artifacts, list):
        errors.append(_schema_issue("bad_evidence_artifacts", "/evidence_artifacts"))
    else:
        seen_req_ids: set[str] = set()
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                errors.append(_schema_issue("bad_evidence_artifact", f"/evidence_artifacts/{index}"))
                continue
            if set(artifact) - {"req_id", "digest", "bytes"}:
                errors.append(_schema_issue("unknown_evidence_artifact_field", f"/evidence_artifacts/{index}"))
            if not isinstance(artifact.get("req_id"), str) or not artifact["req_id"]:
                errors.append(_schema_issue("bad_artifact_req_id", f"/evidence_artifacts/{index}/req_id"))
            elif artifact["req_id"] in seen_req_ids:
                errors.append(_schema_issue("duplicate_artifact_req_id", f"/evidence_artifacts/{index}/req_id"))
            else:
                seen_req_ids.add(artifact["req_id"])
            if not isinstance(artifact.get("digest"), str) or not artifact["digest"]:
                errors.append(_schema_issue("bad_artifact_digest", f"/evidence_artifacts/{index}/digest"))
            if not _is_nonnegative_int(artifact.get("bytes")):
                errors.append(_schema_issue("bad_artifact_bytes", f"/evidence_artifacts/{index}/bytes"))
    if ("payload" in execution_report) != ("payload_digest" in execution_report):
        errors.append(_schema_issue("bad_execution_payload_binding", "/payload_digest"))
    if "payload_digest" in execution_report and (not isinstance(execution_report.get("payload_digest"), str) or not execution_report["payload_digest"]):
        errors.append(_schema_issue("bad_execution_payload_digest", "/payload_digest"))
    return errors


def _find_forbidden_review_keys(value: Any, parts: list[Any] | None = None) -> list[str]:
    if parts is None:
        parts = []
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and key.lower() in FORBIDDEN_REVIEW_AUTHORITY_KEYS:
                found.append(_json_pointer(parts + [key]))
            found.extend(_find_forbidden_review_keys(item, parts + [key]))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_find_forbidden_review_keys(item, parts + [index]))
    return found


def _validate_reviewer_report(reviewer_report: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(reviewer_report, dict):
        return [_schema_issue("reviewer_report_not_object")]
    forbidden = _find_forbidden_review_keys(reviewer_report)
    if forbidden:
        for pointer in forbidden:
            errors.append(_schema_issue("review_authority_field_present", pointer))
        return errors
    if reviewer_report.get("document_type") != "trusted_review_projection":
        errors.append(_schema_issue("unsupported_review_document_type", "/document_type"))
        return errors
    if reviewer_report.get("schema_version") != SCHEMA_VERSION:
        errors.append(_schema_issue("bad_review_schema_version", "/schema_version"))
    allowed = {
        "document_type",
        "schema_version",
        "task_id",
        "spec_digest",
        "run_id",
        "attempt_epoch",
        "review_id",
        "review_digest",
        "review_mode",
        "coverage_scope",
        "reviewed_tree_digest",
        "covered_paths",
        "findings",
        "verified_finding_ids",
    }
    if set(reviewer_report) - allowed:
        errors.append(_schema_issue("unknown_review_projection_field"))
    for key in ("task_id", "spec_digest", "run_id", "review_id", "review_digest", "reviewed_tree_digest"):
        if not isinstance(reviewer_report.get(key), str) or not reviewer_report[key]:
            errors.append(_schema_issue("review_missing_binding", f"/{key}"))
    if not _is_nonnegative_int(reviewer_report.get("attempt_epoch")):
        errors.append(_schema_issue("bad_review_attempt_epoch", "/attempt_epoch"))
    if reviewer_report.get("review_mode") not in ("initial_full", "targeted_verification", "final_full"):
        errors.append(_schema_issue("bad_review_mode", "/review_mode"))
    if reviewer_report.get("coverage_scope") not in ("full", "targeted"):
        errors.append(_schema_issue("bad_coverage_scope", "/coverage_scope"))
    if not isinstance(reviewer_report.get("covered_paths"), list) or any(not isinstance(item, str) for item in _as_list(reviewer_report.get("covered_paths"))):
        errors.append(_schema_issue("bad_covered_paths", "/covered_paths"))
    verified_ids = reviewer_report.get("verified_finding_ids")
    if not isinstance(verified_ids, list) or any(not isinstance(item, str) for item in _as_list(verified_ids)):
        errors.append(_schema_issue("bad_verified_finding_ids", "/verified_finding_ids"))
    elif _has_duplicate_strings(verified_ids):
        errors.append(_schema_issue("duplicate_verified_finding_id", "/verified_finding_ids"))
    findings = reviewer_report.get("findings")
    if not isinstance(findings, list):
        errors.append(_schema_issue("bad_review_findings", "/findings"))
    else:
        seen_occurrences: set[tuple[str, str]] = set()
        seen_occurrence_ids: set[str] = set()
        for index, finding in enumerate(findings):
            pointer = f"/findings/{index}"
            if not isinstance(finding, dict):
                errors.append(_schema_issue("bad_review_finding", pointer))
                continue
            allowed_finding = {"finding_id", "occurrence_id", "severity", "path", "message"}
            if set(finding) - allowed_finding:
                errors.append(_schema_issue("unknown_review_finding_field", pointer))
            finding_id = finding.get("finding_id")
            occurrence_id = finding.get("occurrence_id")
            if not isinstance(finding_id, str) or not finding_id:
                errors.append(_schema_issue("bad_finding_id", f"{pointer}/finding_id"))
            if not isinstance(occurrence_id, str) or not occurrence_id:
                errors.append(_schema_issue("bad_occurrence_id", f"{pointer}/occurrence_id"))
            else:
                if occurrence_id in seen_occurrence_ids:
                    errors.append(_schema_issue("duplicate_occurrence_id", f"{pointer}/occurrence_id"))
                seen_occurrence_ids.add(occurrence_id)
            if isinstance(finding_id, str) and isinstance(occurrence_id, str):
                key = (finding_id, occurrence_id)
                if key in seen_occurrences:
                    errors.append(_schema_issue("duplicate_finding_occurrence", f"{pointer}/occurrence_id"))
                seen_occurrences.add(key)
            if not isinstance(finding.get("severity"), str) or finding["severity"].lower() not in SEVERITY_RANK:
                errors.append(_schema_issue("bad_finding_severity", f"{pointer}/severity"))
            if not isinstance(finding.get("path"), str) or not finding["path"]:
                errors.append(_schema_issue("bad_finding_path", f"{pointer}/path"))
            if "message" in finding and not isinstance(finding.get("message"), str):
                errors.append(_schema_issue("bad_finding_message", f"{pointer}/message"))
    return errors


def _binding_errors(task_policy: dict[str, Any], ledger: dict[str, Any], execution_report: dict[str, Any], reviewer_report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("task_id", "spec_digest", "run_id"):
        values = {
            str(task_policy.get(field)),
            str(ledger.get(field)),
            str(execution_report.get(field)),
            str(reviewer_report.get(field)),
        }
        if len(values) != 1:
            errors.append(f"BINDING_MISMATCH:{field}")
    if execution_report.get("attempt_epoch") != reviewer_report.get("attempt_epoch"):
        errors.append("BINDING_MISMATCH:attempt_epoch")
    return sorted(errors)


def _matched_infra(task_policy: dict[str, Any], execution_report: dict[str, Any]) -> tuple[list[str], list[str]]:
    allowlist = set(_unique_sorted_strings(task_policy.get("infra_signature_allowlist")))
    signatures = _unique_sorted_strings(execution_report.get("failure_signatures"))
    matched = [sig for sig in signatures if sig in allowlist]
    unknown = [sig for sig in signatures if sig not in allowlist]
    return matched, unknown


def _infra_budget_available(task_policy: dict[str, Any], ledger: dict[str, Any], matched: list[str]) -> bool:
    budgets = _as_mapping(task_policy.get("budgets"))
    counters = _as_mapping(ledger.get("counters"))
    per_cap = _as_mapping(budgets.get("infra_per_signature"))
    used_by_sig = _as_mapping(counters.get("infra_used_by_signature"))
    if counters.get("infra_total_used", 0) >= budgets.get("infra_total", 0):
        return False
    return all(used_by_sig.get(sig, 0) < per_cap.get(sig, 0) for sig in matched)


def _increment_infra(budgets_after: dict[str, Any], matched: list[str]) -> None:
    budgets_after["infra_total_used"] = budgets_after.get("infra_total_used", 0) + 1
    by_sig = dict(budgets_after.get("infra_used_by_signature", {}))
    for sig in matched:
        by_sig[sig] = by_sig.get(sig, 0) + 1
    budgets_after["infra_used_by_signature"] = dict(sorted(by_sig.items()))


def _rework_available(task_policy: dict[str, Any], ledger: dict[str, Any]) -> bool:
    return _as_mapping(ledger.get("counters")).get("rework_used", 0) < _as_mapping(task_policy.get("budgets")).get("rework", 0)


def progress_identity(execution_report: dict[str, Any]) -> str:
    """Return the public progress identity for an execution report subject."""

    subject = execution_report["subject"]
    return canonical_digest(
        {
            "subject": {
                "tree_digest": subject["tree_digest"],
                "changed_paths": sorted(subject["changed_paths"]),
            }
        }
    )


def _safe_progress_identity(execution_report: Any) -> str | None:
    try:
        if not isinstance(execution_report, dict):
            return None
        subject = execution_report.get("subject")
        if not isinstance(subject, dict):
            return None
        tree_digest = subject.get("tree_digest")
        changed_paths = subject.get("changed_paths")
        if not isinstance(tree_digest, str) or not tree_digest:
            return None
        if not isinstance(changed_paths, list) or any(not isinstance(item, str) for item in changed_paths):
            return None
        return progress_identity(execution_report)
    except Exception:
        return None


def _latest_prior_attempt(ledger: dict[str, Any]) -> dict[str, Any] | None:
    attempts = _as_list(ledger.get("prior_attempts"))
    if not attempts:
        return None
    return max(attempts, key=lambda attempt: attempt["attempt_epoch"])


def _no_progress_transition(
    task_policy: dict[str, Any],
    ledger: dict[str, Any],
    execution_report: dict[str, Any],
) -> tuple[int, bool]:
    limit = _as_mapping(task_policy.get("budgets")).get("no_progress", 0)
    current_streak = _as_mapping(ledger.get("counters")).get("no_progress_streak", 0)
    if current_streak >= limit:
        return current_streak, True
    prior_attempt = _latest_prior_attempt(ledger)
    current_identity = progress_identity(execution_report)
    next_streak = current_streak + 1 if prior_attempt and prior_attempt.get("progress_identity") == current_identity else 0
    return next_streak, next_streak >= limit


def _apply_no_progress_transition(
    task_policy: dict[str, Any],
    ledger: dict[str, Any],
    execution_report: dict[str, Any],
    budgets_after: dict[str, Any],
) -> bool:
    next_streak, tripped = _no_progress_transition(task_policy, ledger, execution_report)
    budgets_after["no_progress_streak"] = next_streak
    return tripped


def _full_review_available(task_policy: dict[str, Any], ledger: dict[str, Any]) -> bool:
    return _as_mapping(ledger.get("counters")).get("final_full_used", 0) < _as_mapping(task_policy.get("budgets")).get("final_full", 0)


def _failed_gates(task_policy: dict[str, Any], execution_report: dict[str, Any]) -> list[tuple[str, str]]:
    gates = _as_mapping(execution_report.get("gate_results"))
    failures: list[tuple[str, str]] = []
    for gate in _as_list(task_policy.get("mandatory_gates")):
        state = gates.get(gate, "MISSING")
        if state != "PASS":
            failures.append((gate, state))
    return failures


def _registry_records(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for item in _as_list(registry.get("findings")):
        if isinstance(item, dict) and isinstance(item.get("finding_id"), str):
            records[item["finding_id"]] = copy.deepcopy(item)
    return records


def merge_finding_registry(
    finding_registry: dict[str, Any],
    reviewer_report: dict[str, Any],
    current_tree_digest: str,
) -> dict[str, Any]:
    """Merge observations using ``(review_id, occurrence_id)`` identity.

    History entries are append-only: an existing identity is retained without
    overwrite, and identifiers may be reused by a different review.
    """

    result = {
        "document_type": "finding_registry",
        "schema_version": SCHEMA_VERSION,
        "findings": [],
    }
    records = _registry_records(finding_registry)
    current_finding_ids: set[str] = set()

    for finding in sorted(
        _as_list(reviewer_report.get("findings")),
        key=lambda item: (str(_as_mapping(item).get("finding_id")), str(_as_mapping(item).get("occurrence_id"))),
    ):
        if not isinstance(finding, dict) or not isinstance(finding.get("finding_id"), str):
            continue
        finding_id = finding["finding_id"]
        current_finding_ids.add(finding_id)
        severity = str(finding.get("severity", "info")).lower()
        observed_rank = SEVERITY_RANK.get(severity, 0)
        record = records.get(
            finding_id,
            {
                "finding_id": finding_id,
                "status": "open",
                "effective_severity": RANK_SEVERITY[observed_rank],
                "occurrence_count": 0,
                "resolved_at": None,
                "history": [],
            },
        )
        effective_rank = max(SEVERITY_RANK.get(str(record.get("effective_severity", "info")).lower(), 0), observed_rank)
        record["effective_severity"] = RANK_SEVERITY[effective_rank]
        record["status"] = "open"
        record["resolved_at"] = None
        history = _as_list(record.get("history"))
        occurrence = {
            "review_id": reviewer_report.get("review_id"),
            "occurrence_id": finding.get("occurrence_id"),
            "severity": RANK_SEVERITY[observed_rank],
            "path": finding.get("path"),
            "tree_digest": current_tree_digest,
        }
        occurrence_key = (occurrence["review_id"], occurrence["occurrence_id"])
        history_keys = {
            (_as_mapping(item).get("review_id"), _as_mapping(item).get("occurrence_id"))
            for item in history
        }
        if occurrence_key not in history_keys:
            history.append(occurrence)
        record["history"] = sorted(history, key=_canonical_sort_key)
        record["occurrence_count"] = len(record["history"])
        records[finding_id] = record

    verified_ids = set(_unique_sorted_strings(reviewer_report.get("verified_finding_ids")))
    if (
        reviewer_report.get("review_mode") == "targeted_verification"
        and reviewer_report.get("reviewed_tree_digest") == current_tree_digest
    ):
        for finding_id in verified_ids - current_finding_ids:
            record = records.get(finding_id)
            if record is not None and record.get("status") == "open":
                record["status"] = "resolved_verified"
                record["resolved_at"] = {
                    "review_id": reviewer_report.get("review_id"),
                    "tree_digest": current_tree_digest,
                }

    for record in records.values():
        record["history"] = sorted(_as_list(record.get("history")), key=_canonical_sort_key)
        record["occurrence_count"] = len(record["history"])
    result["findings"] = [records[key] for key in sorted(records)]
    return result


def _open_blocking_findings(registry: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for item in _as_list(registry.get("findings")):
        if not isinstance(item, dict):
            continue
        rank = SEVERITY_RANK.get(str(item.get("effective_severity", "info")).lower(), 0)
        if item.get("status") == "open" and rank >= BLOCKING_RANK and isinstance(item.get("finding_id"), str):
            findings.append(item["finding_id"])
    return sorted(set(findings))


def _evidence_failures(task_policy: dict[str, Any], execution_report: dict[str, Any]) -> list[str]:
    artifacts: dict[str, dict[str, Any]] = {}
    for artifact in _as_list(execution_report.get("evidence_artifacts")):
        if isinstance(artifact, dict) and isinstance(artifact.get("req_id"), str):
            artifacts[artifact["req_id"]] = artifact
    failures: list[str] = []
    requirements = sorted(
        [requirement for requirement in _as_list(task_policy.get("required_evidence")) if isinstance(requirement, dict)],
        key=lambda requirement: str(requirement.get("req_id")),
    )
    for requirement in requirements:
        if not isinstance(requirement, dict):
            continue
        req_id = requirement.get("req_id")
        artifact = artifacts.get(req_id)
        if not isinstance(req_id, str) or artifact is None:
            failures.append(str(req_id))
            continue
        if artifact.get("bytes", 0) <= 0:
            failures.append(req_id)
            continue
        if requirement.get("digest_required", True) is not False and artifact.get("digest") != requirement.get("digest"):
            failures.append(req_id)
    return sorted(set(failures))


def _final_full_ok(execution_report: dict[str, Any], reviewer_report: dict[str, Any]) -> bool:
    if reviewer_report.get("review_mode") != "final_full":
        return False
    if reviewer_report.get("coverage_scope") != "full":
        return False
    subject = _as_mapping(execution_report.get("subject"))
    if reviewer_report.get("reviewed_tree_digest") != subject.get("tree_digest"):
        return False
    return set(_as_list(reviewer_report.get("covered_paths"))) >= set(_as_list(subject.get("changed_paths")))


def _validate_terminal_decision(terminal: Any, input_digests: dict[str, str]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(terminal, dict):
        return [_schema_issue("bad_terminal_decision", "/terminal_decision")]
    if set(terminal) != DECISION_REQUIRED_KEYS:
        errors.append(_schema_issue("bad_terminal_decision_shape", "/terminal_decision"))
    if terminal.get("document_type") != "orchestrator_decision":
        errors.append(_schema_issue("bad_terminal_document_type", "/terminal_decision/document_type"))
    if terminal.get("schema_version") != SCHEMA_VERSION:
        errors.append(_schema_issue("bad_terminal_schema_version", "/terminal_decision/schema_version"))
    if not isinstance(terminal.get("outcome"), str) or terminal["outcome"] not in OUTCOMES:
        errors.append(_schema_issue("bad_terminal_outcome", "/terminal_decision/outcome"))
    if not isinstance(terminal.get("rule_id"), str) or not terminal["rule_id"].startswith("R"):
        errors.append(_schema_issue("bad_terminal_rule_id", "/terminal_decision/rule_id"))
    if not isinstance(terminal.get("reason_codes"), list) or any(not isinstance(item, str) for item in _as_list(terminal.get("reason_codes"))):
        errors.append(_schema_issue("bad_terminal_reason_codes", "/terminal_decision/reason_codes"))
    if not isinstance(terminal.get("directives"), list) or any(not isinstance(item, dict) for item in _as_list(terminal.get("directives"))):
        errors.append(_schema_issue("bad_terminal_directives", "/terminal_decision/directives"))
    terminal_progress_identity = terminal.get("progress_identity")
    if terminal_progress_identity is not None and not _is_sha256_digest(terminal_progress_identity):
        errors.append(_schema_issue("bad_terminal_progress_identity", "/terminal_decision/progress_identity"))
    if not isinstance(terminal.get("budgets_after"), dict):
        errors.append(_schema_issue("bad_terminal_budgets", "/terminal_decision/budgets_after"))
    if terminal.get("input_digests") != input_digests:
        errors.append(_schema_issue("bad_terminal_input_digests", "/terminal_decision/input_digests"))
    registry_digest = terminal.get("registry_digest_after")
    if registry_digest is not None and not isinstance(registry_digest, str):
        errors.append(_schema_issue("bad_terminal_registry_digest", "/terminal_decision/registry_digest_after"))
    if not isinstance(terminal.get("decision_digest"), str) or not terminal["decision_digest"]:
        errors.append(_schema_issue("bad_terminal_decision_digest", "/terminal_decision/decision_digest"))
    else:
        recomputed = _with_decision_digest({key: value for key, value in terminal.items() if key != "decision_digest"})
        if recomputed.get("decision_digest") != terminal.get("decision_digest"):
            errors.append(_schema_issue("bad_terminal_decision_digest", "/terminal_decision/decision_digest"))
    return errors


def _decide_policy(
    task_policy: dict[str, Any],
    ledger: dict[str, Any],
    execution_report: dict[str, Any],
    reviewer_report: dict[str, Any],
    input_digests: dict[str, str],
    budgets_after: dict[str, Any],
) -> dict[str, Any]:
    attempt_epoch = execution_report["attempt_epoch"]
    current_progress_identity = progress_identity(execution_report)
    if execution_report["nonce"] in set(ledger["seen_nonces"]) or attempt_epoch <= ledger["last_epoch"]:
        return _escalated("R02_REPLAY", ["FAIL_CLOSED", "INPUT_REPLAY"], input_digests, budgets_after, current_progress_identity)

    expected_subject = ledger["expected_subject"]
    exec_subject = execution_report["subject"]
    if (
        attempt_epoch < ledger["current_epoch"]
        or exec_subject["tree_digest"] != expected_subject["tree_digest"]
        or sorted(exec_subject["changed_paths"]) != sorted(expected_subject["changed_paths"])
        or reviewer_report["reviewed_tree_digest"] != exec_subject["tree_digest"]
    ):
        return _escalated("R03_STALE", ["FAIL_CLOSED", "INPUT_STALE_OR_MISMATCHED"], input_digests, budgets_after, current_progress_identity)

    if ("payload" in execution_report) != ("payload_digest" in execution_report):
        return _escalated("R04_INCOMPLETE", ["FAIL_CLOSED", "INPUT_INCOMPLETE"], input_digests, budgets_after, current_progress_identity)
    if "payload" in execution_report and canonical_digest(execution_report["payload"]) != execution_report.get("payload_digest"):
        return _escalated("R04_INCOMPLETE", ["FAIL_CLOSED", "INPUT_INCOMPLETE"], input_digests, budgets_after, current_progress_identity)

    matched_infra, unknown_infra = _matched_infra(task_policy, execution_report)
    if execution_report["exit_status"] != "OK" and matched_infra and not unknown_infra:
        if _infra_budget_available(task_policy, ledger, matched_infra):
            _increment_infra(budgets_after, matched_infra)
            return _make_decision(
                "FAILED_INFRA",
                "R05_INFRA_RETRY",
                [*(f"INFRA_CLASSIFIED:{sig}" for sig in matched_infra), "RETRY_SCHEDULED"],
                [{"type": "RETRY_INFRA", "signature_ids": matched_infra}],
                budgets_after,
                input_digests,
                progress_identity=current_progress_identity,
            )
        return _make_decision(
            "ESCALATED",
            "R06_INFRA_EXHAUSTED",
            [f"INFRA_BUDGET_EXHAUSTED:{sig}" for sig in matched_infra],
            [{"type": "ESCALATE_TO_HUMAN"}],
            budgets_after,
            input_digests,
            progress_identity=current_progress_identity,
        )

    if execution_report["exit_status"] != "OK":
        return _escalated("R07_UNKNOWN_FAILURE", ["FAIL_CLOSED", "UNCLASSIFIED_FAILURE"], input_digests, budgets_after, current_progress_identity)

    merged_registry = merge_finding_registry(ledger["finding_registry"], reviewer_report, exec_subject["tree_digest"])

    gate_failures = _failed_gates(task_policy, execution_report)
    if gate_failures:
        reason_codes = [f"GATE_FAILED:{gate}" for gate, _state in gate_failures]
        no_progress_tripped = _apply_no_progress_transition(task_policy, ledger, execution_report, budgets_after)
        if _rework_available(task_policy, ledger) and not no_progress_tripped:
            budgets_after["rework_used"] += 1
            return _make_decision(
                "REWORK",
                "R09_GATE_FAIL",
                reason_codes,
                [{"type": "FIX_GATES", "gate_ids": [gate for gate, _state in gate_failures]}],
                budgets_after,
                input_digests,
                merged_registry,
                current_progress_identity,
            )
        reason = "NO_PROGRESS" if no_progress_tripped else "REWORK_BUDGET_EXHAUSTED"
        return _make_decision(
            "ESCALATED",
            "R10_GATE_FAIL_EXHAUSTED",
            [reason],
            [{"type": "ESCALATE_TO_HUMAN"}],
            budgets_after,
            input_digests,
            merged_registry,
            current_progress_identity,
        )

    open_blocking = _open_blocking_findings(merged_registry)
    if open_blocking:
        reasons = [f"OPEN_FINDING:{finding_id}" for finding_id in open_blocking[:20]]
        if len(open_blocking) > 20:
            reasons.append(f"+{len(open_blocking) - 20}_MORE")
        no_progress_tripped = _apply_no_progress_transition(task_policy, ledger, execution_report, budgets_after)
        if _rework_available(task_policy, ledger) and not no_progress_tripped:
            budgets_after["rework_used"] += 1
            return _make_decision(
                "REWORK",
                "R11_OPEN_FINDINGS",
                reasons,
                [{"type": "FIX_FINDINGS", "finding_ids": open_blocking}],
                budgets_after,
                input_digests,
                merged_registry,
                current_progress_identity,
            )
        reason = "NO_PROGRESS" if no_progress_tripped else "REWORK_BUDGET_EXHAUSTED"
        return _make_decision(
            "ESCALATED",
            "R12_FINDINGS_EXHAUSTED",
            [reason],
            [{"type": "ESCALATE_TO_HUMAN"}],
            budgets_after,
            input_digests,
            merged_registry,
            current_progress_identity,
        )

    evidence_failures = _evidence_failures(task_policy, execution_report)
    if evidence_failures:
        reasons = [f"EVIDENCE_MISSING:{req_id}" for req_id in evidence_failures]
        no_progress_tripped = _apply_no_progress_transition(task_policy, ledger, execution_report, budgets_after)
        if _rework_available(task_policy, ledger) and not no_progress_tripped:
            budgets_after["rework_used"] += 1
            return _make_decision(
                "REWORK",
                "R13_EVIDENCE",
                reasons,
                [{"type": "PROVIDE_EVIDENCE", "req_ids": evidence_failures}],
                budgets_after,
                input_digests,
                merged_registry,
                current_progress_identity,
            )
        reason = "NO_PROGRESS" if no_progress_tripped else "REWORK_BUDGET_EXHAUSTED"
        return _make_decision(
            "ESCALATED",
            "R14_EVIDENCE_EXHAUSTED",
            [reason],
            [{"type": "ESCALATE_TO_HUMAN"}],
            budgets_after,
            input_digests,
            merged_registry,
            current_progress_identity,
        )

    if not _final_full_ok(execution_report, reviewer_report):
        if _full_review_available(task_policy, ledger):
            budgets_after["final_full_used"] += 1
            return _make_decision(
                "REWORK",
                "R15_NEED_FULL_REVIEW",
                ["FINAL_FULL_REVIEW_REQUIRED"],
                [{"type": "REVIEW_ONLY_FULL"}],
                budgets_after,
                input_digests,
                merged_registry,
                current_progress_identity,
            )
        return _make_decision(
            "ESCALATED",
            "R16_FULL_REVIEW_EXHAUSTED",
            ["FULL_REVIEW_CAP_EXHAUSTED"],
            [{"type": "ESCALATE_TO_HUMAN"}],
            budgets_after,
            input_digests,
            merged_registry,
            current_progress_identity,
        )

    return _make_decision(
        "ACCEPTED",
        "R17_ACCEPT",
        ["ALL_GATES_PASSED", "NO_OPEN_BLOCKER_MAJOR", "EVIDENCE_SATISFIED", "FINAL_FULL_REVIEW_OK"],
        [{"type": "RECORD_TERMINAL_DECISION"}],
        budgets_after,
        input_digests,
        merged_registry,
        current_progress_identity,
    )


def _invalid_terminal_decision(
    input_digests: dict[str, str],
    budgets_after: dict[str, Any],
    progress_identity: str | None,
) -> dict[str, Any]:
    return _escalated("R01_BINDING", ["FAIL_CLOSED", "TERMINAL_DECISION_INVALID"], input_digests, budgets_after, progress_identity)


def decide(
    task_policy: dict[str, Any],
    ledger: dict[str, Any],
    execution_report: dict[str, Any],
    reviewer_report: dict[str, Any],
) -> dict[str, Any]:
    """Return the deterministic policy decision for trusted JSON inputs."""

    input_digests = _placeholder_input_digests()
    budgets_after = _safe_budget_state(ledger)
    decision_progress_identity = _safe_progress_identity(execution_report)

    try:
        _enforce_decide_input_limits(task_policy, ledger, execution_report, reviewer_report)
        input_digests = _input_digests(task_policy, ledger, execution_report, reviewer_report)
        budgets_after = _budget_state(ledger)
        schema_errors = _validate_task_policy(task_policy) + _validate_ledger(ledger) + _validate_execution_report(execution_report)
        if schema_errors:
            return _escalated("R01_BINDING", ["FAIL_CLOSED", "INPUT_BINDING_VIOLATION"], input_digests, budgets_after, decision_progress_identity)
        review_errors = _validate_reviewer_report(reviewer_report)
        if review_errors:
            return _escalated("R08_REVIEW_CONTRACT", ["FAIL_CLOSED", "REVIEW_CONTRACT_INVALID"], input_digests, budgets_after, decision_progress_identity)

        binding_errors = _binding_errors(task_policy, ledger, execution_report, reviewer_report)
        if binding_errors:
            return _escalated(
                "R01_BINDING",
                ["FAIL_CLOSED", "INPUT_BINDING_VIOLATION", *binding_errors],
                input_digests,
                budgets_after,
                decision_progress_identity,
            )

        derived = _decide_policy(task_policy, ledger, execution_report, reviewer_report, input_digests, copy.deepcopy(budgets_after))
        if derived["outcome"] == "ESCALATED" and derived["rule_id"] in {"R02_REPLAY", "R03_STALE", "R04_INCOMPLETE"}:
            return derived
        terminal = ledger.get("terminal_decision") if isinstance(ledger, dict) else None
        if terminal is not None:
            if _validate_terminal_decision(terminal, input_digests):
                return _invalid_terminal_decision(input_digests, budgets_after, decision_progress_identity)
            if terminal != derived:
                return _invalid_terminal_decision(input_digests, budgets_after, decision_progress_identity)
            return copy.deepcopy(terminal)
        return derived
    except PolicyInputError:
        input_digests = _rejected_input_digests(task_policy, ledger, execution_report, reviewer_report)
        return _escalated("R01_BINDING", ["FAIL_CLOSED", "INPUT_BINDING_VIOLATION"], input_digests, budgets_after, decision_progress_identity)
    except Exception:
        return _escalated("R01_BINDING", ["FAIL_CLOSED", "INPUT_BINDING_VIOLATION"], input_digests, budgets_after, decision_progress_identity)


def _load_schema(path: Path) -> dict[str, Any]:
    return parse_json_file(path)


def _schema_check(path: Path) -> list[dict[str, str]]:
    if jsonschema is None:
        return [{"code": "missing_dependency", "message": "jsonschema is required", "path": str(path)}]
    try:
        schema = _load_schema(path)
        jsonschema.Draft202012Validator.check_schema(schema)
    except (PolicyInputError, jsonschema.SchemaError) as exc:
        return [{"code": "invalid_schema", "message": str(exc), "path": str(path)}]
    return []


def _validate_against_state_schema(document: dict[str, Any]) -> list[str]:
    if jsonschema is None:
        return ["jsonschema is required"]
    schema = _load_schema(STATE_SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path))]


def evaluate_fixture(path: Path) -> dict[str, Any]:
    fixture = parse_json_file(path)
    schema_errors = _validate_against_state_schema(fixture)
    if schema_errors:
        return {
            "fixture": path.name,
            "valid": False,
            "schema_errors": schema_errors,
        }
    decision = decide(fixture["task_policy"], fixture["ledger"], fixture["execution_report"], fixture["reviewer_report"])
    expected_outcome = fixture.get("expected_outcome")
    expected_rule_id = fixture.get("expected_rule_id")
    matches = decision["outcome"] == expected_outcome and decision["rule_id"] == expected_rule_id
    return {
        "fixture": path.name,
        "valid": matches,
        "outcome": decision["outcome"],
        "rule_id": decision["rule_id"],
        "expected_outcome": expected_outcome,
        "expected_rule_id": expected_rule_id,
    }


def check_fixture_tree(root: Path) -> dict[str, Any]:
    valid_dir = root / "valid"
    invalid_dir = root / "invalid"
    valid_results = [evaluate_fixture(path) for path in sorted(valid_dir.glob("*.json"))]
    invalid_results = []
    for path in sorted(invalid_dir.glob("*.json")):
        try:
            fixture = parse_json_file(path)
            schema_errors = _validate_against_state_schema(fixture)
            invalid_results.append({"fixture": path.name, "rejected": bool(schema_errors), "schema_errors": schema_errors})
        except PolicyInputError as exc:
            invalid_results.append({"fixture": path.name, "rejected": True, "schema_errors": [exc.code]})
    return {
        "mode": "fixture_check",
        "valid_count": len(valid_results),
        "invalid_count": len(invalid_results),
        "valid_results": valid_results,
        "invalid_results": invalid_results,
        "passed": all(item.get("valid") for item in valid_results) and all(item.get("rejected") for item in invalid_results),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-schema", action="store_true", help="self-validate both policy schemas")
    parser.add_argument("--fixture", type=Path, help="evaluate one policy fixture")
    parser.add_argument("--check-fixtures", type=Path, help="validate fixtures under a policy fixture root")
    args = parser.parse_args(argv)

    try:
        if args.check_schema:
            errors = _schema_check(STATE_SCHEMA) + _schema_check(REGISTRY_SCHEMA)
            result = {"mode": "schema_self_check", "schemas_valid": not errors, "errors": errors}
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0 if not errors else 2
        if args.fixture is not None:
            result = evaluate_fixture(args.fixture)
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0 if result["valid"] else 1
        if args.check_fixtures is not None:
            result = check_fixture_tree(args.check_fixtures)
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0 if result["passed"] else 1
    except PolicyInputError as exc:
        result = {"mode": "tool_input_failure", "valid": False, "error": {"code": exc.code, "message": str(exc), "pointer": exc.pointer}}
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 2

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
