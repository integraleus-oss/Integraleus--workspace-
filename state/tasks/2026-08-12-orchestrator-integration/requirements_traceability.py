#!/usr/bin/env python3
"""Generate and validate immutable requirements and their proof-chain links."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable


class TraceabilityError(RuntimeError):
    pass


ACTIVE_STATES = {"accepted", "implementing", "implemented"}
ALL_STATES = ACTIVE_STATES | {"deferred_by_user", "removed_by_user"}
ACCEPTANCE_OUTCOMES = {"pass", "fail", "deferred", "removed", "unable_to_verify"}
REQ_ID = re.compile(r"^R[0-9]{2,3}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")


def digest_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def generate_manifest(manifest_id: str, original_brief: str, requirement_texts: Iterable[str]) -> dict[str, Any]:
    """Create stable IDs from ordered requirement texts without rewriting the brief."""
    texts = list(requirement_texts)
    if not isinstance(manifest_id, str) or not SLUG.fullmatch(manifest_id):
        raise TraceabilityError("manifest_id is invalid")
    if not isinstance(original_brief, str) or not original_brief or len(original_brief) > 65536:
        raise TraceabilityError("original brief is invalid")
    if not texts or len(texts) > 999 or any(not isinstance(text, str) or not text or len(text) > 8192 for text in texts):
        raise TraceabilityError("requirement texts are invalid")
    width = max(2, len(str(len(texts))))
    manifest = {
        "document_type": "requirements_manifest",
        "schema_version": "1.0.0",
        "manifest_id": manifest_id,
        "original_brief": original_brief,
        "original_brief_digest": digest_text(original_brief),
        "requirements": [
            {
                "requirement_id": f"R{index:0{width}d}",
                "original_text": text,
                "original_text_digest": digest_text(text),
                "state": "accepted",
                "owner_disposition": None,
            }
            for index, text in enumerate(texts, 1)
        ],
    }
    validate_manifest(manifest)
    return manifest


def validate_manifest(manifest: Any) -> dict[str, dict[str, Any]]:
    required = {"document_type", "schema_version", "manifest_id", "original_brief",
                "original_brief_digest", "requirements"}
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise TraceabilityError("requirements manifest fields are invalid")
    if manifest["document_type"] != "requirements_manifest" or manifest["schema_version"] != "1.0.0":
        raise TraceabilityError("requirements manifest contract is unsupported")
    if not isinstance(manifest["manifest_id"], str) or not SLUG.fullmatch(manifest["manifest_id"]):
        raise TraceabilityError("manifest_id is invalid")
    brief = manifest["original_brief"]
    if not isinstance(brief, str) or not brief or len(brief) > 65536 or manifest["original_brief_digest"] != digest_text(brief):
        raise TraceabilityError("original brief digest mismatch")
    requirements = manifest["requirements"]
    if not isinstance(requirements, list) or not 1 <= len(requirements) <= 999:
        raise TraceabilityError("requirements list is invalid")
    by_id: dict[str, dict[str, Any]] = {}
    width = max(2, len(str(len(requirements))))
    for index, item in enumerate(requirements, 1):
        fields = {"requirement_id", "original_text", "original_text_digest", "state", "owner_disposition"}
        expected_id = f"R{index:0{width}d}"
        if not isinstance(item, dict) or set(item) != fields or item.get("requirement_id") != expected_id:
            raise TraceabilityError("requirement IDs must be unique, stable, and contiguous")
        text = item["original_text"]
        if not isinstance(text, str) or not text or len(text) > 8192 or item["original_text_digest"] != digest_text(text):
            raise TraceabilityError(f"requirement text digest mismatch: {expected_id}")
        state, disposition = item["state"], item["owner_disposition"]
        if state not in ALL_STATES:
            raise TraceabilityError(f"requirement state is invalid: {expected_id}")
        if state in {"deferred_by_user", "removed_by_user"}:
            if (not isinstance(disposition, dict) or set(disposition) != {"decision_id", "reason"}
                    or not all(isinstance(disposition[key], str) and disposition[key].strip()
                               for key in ("decision_id", "reason"))):
                raise TraceabilityError(f"owner disposition is required: {expected_id}")
        elif disposition is not None:
            raise TraceabilityError(f"owner disposition is forbidden for active requirement: {expected_id}")
        by_id[expected_id] = item
    return by_id


def _active_ids(manifest: dict[str, Any]) -> set[str]:
    return {item["requirement_id"] for item in manifest["requirements"] if item["state"] in ACTIVE_STATES}


def validate_spec_completeness(manifest: dict[str, Any], specification: Any) -> None:
    by_id = validate_manifest(manifest)
    if (not isinstance(specification, dict)
            or set(specification) != {"document_type", "schema_version", "manifest_digest", "requirements"}
            or specification["document_type"] != "requirements_specification"
            or specification["schema_version"] != "1.0.0"
            or specification["manifest_digest"] != canonical_digest(manifest)
            or not isinstance(specification["requirements"], list)):
        raise TraceabilityError("requirements specification contract is invalid")
    seen: set[str] = set()
    for item in specification["requirements"]:
        if (not isinstance(item, dict) or set(item) != {"requirement_id", "specification"}
                or item.get("requirement_id") not in by_id or item["requirement_id"] in seen
                or not isinstance(item.get("specification"), str) or not item["specification"].strip()):
            raise TraceabilityError("requirements specification entry is invalid")
        seen.add(item["requirement_id"])
    missing = _active_ids(manifest) - seen
    if missing:
        raise TraceabilityError("active requirements lack specification: " + ",".join(sorted(missing)))


def validate_task_traceability(manifest: dict[str, Any], tasks: Any) -> None:
    by_id = validate_manifest(manifest)
    if (not isinstance(tasks, dict) or set(tasks) != {"document_type", "schema_version", "manifest_digest", "tasks"}
            or tasks["document_type"] != "requirements_task_map" or tasks["schema_version"] != "1.0.0"
            or tasks["manifest_digest"] != canonical_digest(manifest) or not isinstance(tasks["tasks"], list)):
        raise TraceabilityError("requirements task map contract is invalid")
    covered: set[str] = set()
    task_ids: set[str] = set()
    for task in tasks["tasks"]:
        if (not isinstance(task, dict) or set(task) != {"task_id", "requirement_ids"}
                or not isinstance(task.get("task_id"), str) or not SLUG.fullmatch(task["task_id"])
                or task["task_id"] in task_ids or not isinstance(task.get("requirement_ids"), list)
                or not task["requirement_ids"] or len(task["requirement_ids"]) != len(set(task["requirement_ids"]))
                or any(req_id not in by_id for req_id in task["requirement_ids"])):
            raise TraceabilityError("task traceability entry is invalid")
        task_ids.add(task["task_id"])
        covered.update(task["requirement_ids"])
    implementing = {req_id for req_id, item in by_id.items() if item["state"] in {"implementing", "implemented"}}
    missing = implementing - covered
    if missing:
        raise TraceabilityError("implementing requirements lack tasks: " + ",".join(sorted(missing)))


def validate_acceptance_completeness(manifest: dict[str, Any], acceptance: Any) -> None:
    by_id = validate_manifest(manifest)
    if (not isinstance(acceptance, dict)
            or set(acceptance) != {"document_type", "schema_version", "manifest_digest", "results"}
            or acceptance["document_type"] != "requirements_acceptance"
            or acceptance["schema_version"] != "1.0.0"
            or acceptance["manifest_digest"] != canonical_digest(manifest)
            or not isinstance(acceptance["results"], list)):
        raise TraceabilityError("requirements acceptance contract is invalid")
    seen: set[str] = set()
    for result in acceptance["results"]:
        if (not isinstance(result, dict) or set(result) != {"requirement_id", "outcome", "evidence"}
                or result.get("requirement_id") not in by_id or result["requirement_id"] in seen
                or result.get("outcome") not in ACCEPTANCE_OUTCOMES
                or not isinstance(result.get("evidence"), str) or not result["evidence"].strip()):
            raise TraceabilityError("requirements acceptance result is invalid")
        seen.add(result["requirement_id"])
    missing = _active_ids(manifest) - seen
    if missing:
        raise TraceabilityError("active requirements lack acceptance: " + ",".join(sorted(missing)))


def validate_preflight(manifest: dict[str, Any], specification: Any, tasks: Any) -> None:
    validate_spec_completeness(manifest, specification)
    validate_task_traceability(manifest, tasks)
