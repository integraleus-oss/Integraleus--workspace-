#!/usr/bin/env python3
"""Build and admit a blind final acceptance independent of internal planning."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import agent_launcher
import requirements_traceability


class BlindAcceptanceError(RuntimeError):
    pass


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
                    encoding="utf-8")


def project_state(project_root: Path) -> str:
    status = subprocess.run(["git", "-C", str(project_root), "status", "--porcelain=v1", "-z",
                            "--untracked-files=all"], capture_output=True, check=False)
    diff = subprocess.run(["git", "-C", str(project_root), "diff", "--binary", "HEAD"],
                          capture_output=True, check=False)
    if status.returncode or diff.returncode:
        raise BlindAcceptanceError("cannot capture blind acceptance worktree state")
    digest = hashlib.sha256(status.stdout + b"\0" + diff.stdout)
    for raw in status.stdout.split(b"\0"):
        if len(raw) < 4 or raw[:2] != b"??":
            continue
        path = project_root / raw[3:].decode("utf-8")
        if path.is_file() and not path.is_symlink():
            digest.update(raw + b"\0" + path.read_bytes())
    return "sha256:" + digest.hexdigest()


def run_verification_commands(project_root: Path, run_dir: Path, commands: list[list[str]],
                              timeout_seconds: int) -> list[dict[str, Any]]:
    records = []
    before = project_state(project_root)
    gates = run_dir / "verification"
    gates.mkdir(parents=True)
    for index, argv in enumerate(commands, 1):
        try:
            result = subprocess.run(argv, cwd=project_root, capture_output=True, timeout=timeout_seconds, check=False)
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            result = None
            timed_out = True
            stdout, stderr, exit_code = exc.stdout or b"", exc.stderr or b"", 124
        else:
            stdout, stderr, exit_code = result.stdout, result.stderr, result.returncode
        gate = gates / f"gate-{index}"
        gate.mkdir()
        (gate / "stdout.log").write_bytes(stdout)
        (gate / "stderr.log").write_bytes(stderr)
        record = {"gate_id": f"blind-{index}", "argv": argv, "exit_code": exit_code, "timed_out": timed_out,
                  "stdout_digest": _digest(gate / "stdout.log"), "stderr_digest": _digest(gate / "stderr.log")}
        _write(gate / "result.json", record)
        records.append(record)
        if timed_out or exit_code != 0:
            raise BlindAcceptanceError(f"blind verification command failed: blind-{index}")
    if project_state(project_root) != before:
        raise BlindAcceptanceError("blind verification commands mutated the worktree")
    return records


def build_prompt(manifest: dict[str, Any], verification_commands: list[list[str]]) -> str:
    requirements_traceability.validate_manifest(manifest)
    active = [item for item in manifest["requirements"] if item["state"] in requirements_traceability.ACTIVE_STATES]
    commands = "\n".join("- " + json.dumps(command, ensure_ascii=False) for command in verification_commands)
    result_shape = [{"requirement_id": item["requirement_id"], "outcome": "pass|fail|unable_to_verify",
                     "evidence": "observable evidence"} for item in active]
    return (
        "You are the blind final acceptance agent. Independently inspect the current worktree and test the result "
        "against the owner's exact original brief below. You have not been given internal specifications, task "
        "tracking, prior reviews, or orchestrator explanations. Do not infer that work is correct from file names.\n\n"
        "ORIGINAL BRIEF (exact):\n---\n" + manifest["original_brief"] + "\n---\n\n"
        "Requirement labels and exact source excerpts (not internal specifications):\n" +
        "\n".join(f"- {item['requirement_id']}: {item['original_text']}" for item in active) +
        "\n\nVerification commands you may run read-only:\n" + commands +
        "\n\nReturn exact JSON only with document_type=blind_acceptance_verdict, schema_version=1.0.0, "
        "manifest_digest set to " + manifest["immutable_core_digest"] + ", and results shaped like:\n" +
        json.dumps(result_shape, ensure_ascii=False) + "\nNo additional root fields are allowed."
    )


def validate_blind_verdict(manifest: dict[str, Any], verdict: Any) -> None:
    requirements_traceability.validate_acceptance_completeness(manifest, verdict)
    if verdict["document_type"] != "requirements_acceptance":
        raise BlindAcceptanceError("blind verdict document type is invalid")
    active = {item["requirement_id"] for item in manifest["requirements"]
              if item["state"] in requirements_traceability.ACTIVE_STATES}
    for result in verdict["results"]:
        if result["requirement_id"] in active and result["outcome"] not in {"pass", "fail", "unable_to_verify"}:
            raise BlindAcceptanceError("blind verdict uses an invalid active outcome")


def compare_acceptance(manifest: dict[str, Any], internal: dict[str, Any], blind: dict[str, Any]) -> None:
    requirements_traceability.validate_acceptance_completeness(manifest, internal)
    validate_blind_verdict(manifest, blind)
    internal_by_id = {item["requirement_id"]: item["outcome"] for item in internal["results"]}
    blind_by_id = {item["requirement_id"]: item["outcome"] for item in blind["results"]}
    disagreements = sorted(req_id for req_id in internal_by_id if internal_by_id[req_id] != blind_by_id[req_id])
    if disagreements:
        raise BlindAcceptanceError("internal/blind acceptance disagreement: " + ",".join(disagreements))
    non_pass = sorted(req_id for req_id, outcome in blind_by_id.items() if outcome != "pass")
    if non_pass:
        raise BlindAcceptanceError("blind acceptance did not pass: " + ",".join(non_pass))


def run_blind_acceptance(project_root: Path, run_dir: Path, manifest: dict[str, Any],
                         internal: dict[str, Any], verification_commands: list[list[str]],
                         timeout_seconds: int) -> dict[str, Any]:
    run_dir.mkdir(parents=True)
    before = project_state(project_root)
    gates = run_verification_commands(project_root, run_dir, verification_commands, timeout_seconds)
    prompt = build_prompt(manifest, verification_commands)
    launch_dir = run_dir / "agent"
    launch = agent_launcher.launch("claude", project_root, prompt, launch_dir,
                                   timeout_seconds=timeout_seconds, codex_write=False)
    if launch.get("status") == "INTERRUPTED":
        return {"status": "INTERRUPTED", "launch": launch}
    if launch.get("status") != "OK":
        raise BlindAcceptanceError("blind acceptance launch failed")
    raw = agent_launcher.extract_claude_verdict(launch_dir, run_dir / "blind-verdict.json")
    if raw.get("document_type") == "blind_acceptance_verdict":
        raw = {**raw, "document_type": "requirements_acceptance"}
        _write(run_dir / "blind-verdict.json", raw)
    try:
        persisted = json.loads((run_dir / "blind-verdict.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BlindAcceptanceError("persisted blind verdict is invalid") from exc
    if persisted != raw:
        raise BlindAcceptanceError("persisted blind verdict differs from admitted verdict")
    compare_acceptance(manifest, internal, raw)
    if project_state(project_root) != before:
        raise BlindAcceptanceError("blind acceptance mutated the worktree")
    record = {"document_type": "blind_acceptance_result", "schema_version": "1.0.0",
              "status": "ACCEPTED", "manifest_digest": manifest["immutable_core_digest"],
              "prompt_digest": _digest(launch_dir / "input-prompt.md"),
              "verdict_digest": _digest(run_dir / "blind-verdict.json"), "verification_gates": gates,
              "worktree_state": before}
    _write(run_dir / "result.json", record)
    return record
