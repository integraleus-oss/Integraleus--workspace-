#!/usr/bin/env python3
"""Run one bounded local Codex/Claude cycle from a strict task packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import agent_launcher
import live_review_cycle
import trusted_review_builder
from managed_one_cycle import run_managed_cycle
from managed_policy_review import admit_live_review


class PacketError(RuntimeError):
    pass


SAFE_PROJECT_BASES = (
    Path("/home/stanislav/projects"),
    Path("/home/stanislav/agent-runs/orchestrator-worktrees"),
)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PacketError(f"cannot read JSON packet: {path}") from exc


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _bounded_text(path: Path, limit: int = 131072) -> str:
    if not path.is_file() or path.is_symlink():
        raise PacketError(f"required regular file is missing: {path}")
    data = path.read_bytes()
    if not data or len(data) > limit:
        raise PacketError(f"file size is outside allowed bounds: {path}")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PacketError(f"file is not valid UTF-8: {path}") from exc


def _inside(base: Path, raw: Any, *, directory: bool = False) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise PacketError("packet path must be a non-empty string")
    try:
        relative = Path(raw)
    except (ValueError, OSError) as exc:
        raise PacketError("packet path is invalid") from exc
    if relative.is_absolute() or ".." in relative.parts:
        raise PacketError("packet path escapes packet directory")
    candidate = base / relative
    if candidate.is_symlink():
        raise PacketError("packet path must not be a symlink")
    try:
        resolved = candidate.resolve()
    except (ValueError, OSError) as exc:
        raise PacketError("packet path cannot be resolved") from exc
    if not resolved.is_relative_to(base):
        raise PacketError("packet path escapes packet directory")
    if (directory and not resolved.is_dir()) or (not directory and not resolved.is_file()):
        raise PacketError("packet path has wrong type or is missing")
    return resolved


def load_packet(packet_path: Path) -> dict[str, Any]:
    try:
        packet_path = packet_path.resolve()
    except (ValueError, OSError) as exc:
        raise PacketError("packet path cannot be resolved") from exc
    packet = _read_json(packet_path)
    if not isinstance(packet, dict) or packet.get("document_type") != "production_cycle_task":
        raise PacketError("unsupported task packet")
    schema_version = packet.get("schema_version")
    legacy_fields = {
        "document_type", "schema_version", "project_root", "task_note", "run_root",
        "codex_timeout_seconds", "claude_timeout_seconds", "reviews",
    }
    builder_fields = (legacy_fields - {"reviews"}) | {"builder"}
    if schema_version not in {"1.0.0", "1.1.0"} or set(packet) != (
        legacy_fields if schema_version == "1.0.0" else builder_fields
    ):
        raise PacketError("task packet fields or schema version are invalid")
    base = packet_path.parent
    if not isinstance(packet["project_root"], str) or not packet["project_root"].strip():
        raise PacketError("project_root must be a non-empty string")
    if not isinstance(packet["run_root"], str) or not packet["run_root"].strip():
        raise PacketError("run_root must be a non-empty string")
    project_root = Path(packet["project_root"]).resolve()
    run_root = Path(packet["run_root"]).resolve()
    if not project_root.is_dir() or project_root == Path("/"):
        raise PacketError("project_root is not a valid directory")
    if not any(project_root.is_relative_to(base.resolve()) for base in SAFE_PROJECT_BASES):
        raise PacketError("project_root is outside approved local worktree bases")
    git_marker = project_root / ".git"
    if git_marker.is_symlink() or not (git_marker.is_file() or git_marker.is_dir()):
        raise PacketError("project_root must be the root of a Git repository or worktree")
    if run_root.exists() or run_root == Path("/") or run_root.is_relative_to(project_root):
        raise PacketError("run_root must be new and outside project_root")
    for key in ("codex_timeout_seconds", "claude_timeout_seconds"):
        if not isinstance(packet[key], int) or not 1 <= packet[key] <= 1800:
            raise PacketError(f"{key} must be between 1 and 1800")
    task_note = _inside(base, packet["task_note"])
    _bounded_text(task_note, 65536)
    normalized_reviews = []
    builder = None
    if schema_version == "1.0.0":
        reviews = packet["reviews"]
        if not isinstance(reviews, list) or len(reviews) != 2:
            raise PacketError("exactly two review legs are required")
        for review in reviews:
            if not isinstance(review, dict) or set(review) != {"prompt", "input_dir", "bundle"}:
                raise PacketError("review leg fields are invalid")
            prompt = _inside(base, review["prompt"])
            input_dir = _inside(base, review["input_dir"], directory=True)
            bundle_path = _inside(input_dir, review["bundle"])
            prompt_text = _bounded_text(prompt)
            _bounded_text(bundle_path)
            if any(path.is_symlink() for path in input_dir.rglob("*")):
                raise PacketError("review input directory contains a symlink")
            normalized_reviews.append({"prompt_text": prompt_text, "input_dir": input_dir, "bundle": bundle_path})
    else:
        builder = packet["builder"]
        required = {"task_id", "repo_id", "allowed_paths", "gates", "gate_timeout_seconds",
                    "acceptance_criteria", "review_instructions", "policy_fixture", "review_verdict"}
        if not isinstance(builder, dict) or set(builder) != required:
            raise PacketError("builder configuration fields are invalid")
        if not isinstance(builder["gate_timeout_seconds"], int) or not 1 <= builder["gate_timeout_seconds"] <= 1800:
            raise PacketError("builder gate timeout is invalid")
        builder = dict(builder)
        builder["review_instructions"] = str(_inside(base, builder["review_instructions"]))
        builder["policy_fixture"] = str(_inside(base, builder["policy_fixture"]))
        normalized_reviews = [{"prompt_text": _bounded_text(Path(builder["review_instructions"]))} for _ in range(3)]
    return {
        **packet,
        "packet_path": packet_path,
        "project_root": project_root,
        "run_root": run_root,
        "task_note": task_note,
        "reviews": normalized_reviews,
        "builder": builder,
    }


def _run_loaded_packet(packet: dict[str, Any]) -> dict[str, Any]:
    task_text = _bounded_text(packet["task_note"], 65536)
    baseline = trusted_review_builder.capture_clean_baseline(packet["project_root"]) if packet["builder"] else None
    prior_context: dict[str, Any] | None = None

    def implement(attempt: int, rework: str | None, run_dir: Path) -> dict[str, Any]:
        if attempt == 1:
            prompt = task_text
        else:
            if not isinstance(rework, str) or not rework.strip():
                raise PacketError("attempt 2 requires a policy-authenticated rework packet")
            prompt = ("This is a policy-authenticated rework attempt. The directive below is the sole "
                      "authoritative implementation instruction for this attempt. Do not repeat or preserve "
                      "the prior attempt merely because earlier task prose conflicts with this directive.\n\n"
                      "Policy-authenticated rework:\n" + rework)
        result = agent_launcher.launch(
            "codex", packet["project_root"], prompt, run_dir,
            timeout_seconds=packet["codex_timeout_seconds"], codex_write=True,
        )
        if result["status"] != "OK":
            result = dict(result)
            result["classification"] = "UNKNOWN"
        return result

    def review(attempt: int, run_dir: Path) -> dict[str, Any]:
        nonlocal prior_context
        leg = packet["reviews"][attempt - 1]
        if packet["builder"]:
            built = trusted_review_builder.build_review_inputs(
                packet["project_root"], run_dir / "review-inputs", baseline, packet["builder"], attempt, prior_context
            )
            trusted_review_builder.verify_seal(built["input_dir"], packet["project_root"])
            copied_inputs, bundle = built["input_dir"], built["bundle"]
            anchored_seal_digest = _sha256(built["seal"])
        else:
            copied_inputs = run_dir / "review-inputs"
            anchored_seal_digest = None
            shutil.copytree(leg["input_dir"], copied_inputs, symlinks=True)
            if any(path.is_symlink() for path in copied_inputs.rglob("*")):
                raise PacketError("copied review inputs contain a symlink")
            bundle = copied_inputs / leg["bundle"].relative_to(leg["input_dir"])
        prompt = run_dir / "review-prompt.md"
        prompt_text = leg["prompt_text"]
        if packet["builder"]:
            prompt_text += ("\n\nTrusted review inputs (read every sealed artifact before returning the verdict):\n"
                            f"{copied_inputs}\nThe manifest digest binds review-instructions.md; use that file as the "
                            "review instruction input. The only allowed output contract is the sealed "
                            "review-verdict.schema.json in that directory: read it and conform to it exactly. "
                            "Its root document_type must be review_verdict. Do not use any other remembered or "
                            "inferred review schema. Include every schema-required property even when its value "
                            "is null (including conclusion.unable_to_complete_reason when applicable). Return "
                            "only the exact JSON document as your final response.\n")
        prompt.write_text(prompt_text, encoding="utf-8")
        prompt.chmod(0o444)
        live_root = run_dir / "live-review"
        result = live_review_cycle.run_cycle(
            packet["project_root"], prompt, bundle, live_root,
            timeout_seconds=packet["claude_timeout_seconds"],
            pre_admission_verify=(lambda: trusted_review_builder.verify_seal(
                copied_inputs, packet["project_root"], expected_seal_digest=anchored_seal_digest
            ))
            if packet["builder"] else None,
            allow_format_retry=bool(packet["builder"]),
            allow_contract_retry=bool(packet["builder"]),
        )
        admitted = admit_live_review(result, live_root)
        if packet["builder"] and result.get("status") == "DECIDED" and admitted.get("outcome") == "REWORK":
            decision_dir = Path(result["decision_dir"])
            decision = _read_json(decision_dir / "decision.json")
            registry = _read_json(decision_dir / "registry-after.json")
            manifest = result.get("decision", {})
            if (manifest.get("registry_digest_file") != _sha256(decision_dir / "registry-after.json")
                    or decision.get("registry_digest_after") != _canonical_digest(registry)):
                raise PacketError("carried finding registry digest mismatch")
            carried_attempts = [] if prior_context is None else list(prior_context.get("prior_attempts", []))
            if prior_context and prior_context.get("last_decision"):
                carried_attempts.append({"attempt_epoch": attempt - 1, **prior_context["last_decision"]})
            seen_nonces = [] if prior_context is None else list(prior_context.get("seen_nonces", []))
            seen_nonces.append(f"run_{packet['builder']['task_id']}.attempt-{attempt}-nonce")
            prior_context = {
                "budgets_after": decision.get("budgets_after", {}),
                "progress_identity": decision.get("progress_identity"),
                "finding_registry": registry,
                "seen_nonces": seen_nonces,
                "prior_attempts": carried_attempts,
                "last_decision": {key: decision[key] for key in
                                  ("progress_identity", "decision_digest", "outcome", "rule_id")},
            }
        return admitted

    return run_managed_cycle(packet["run_root"], implement, review)


def run_packet(packet_path: Path) -> dict[str, Any]:
    return _run_loaded_packet(load_packet(packet_path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        packet = load_packet(args.packet)
        result = {"status": "VALID", "run_root": str(packet["run_root"])} if args.validate_only else _run_loaded_packet(packet)
        code = 0 if result["status"] in {"VALID", "ACCEPTED"} else 3 if result["status"] == "FAILED_INFRA" else 4
    except Exception as exc:
        result = {"status": "ERROR", "error": {"type": type(exc).__name__, "message": str(exc)}}
        code = 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
