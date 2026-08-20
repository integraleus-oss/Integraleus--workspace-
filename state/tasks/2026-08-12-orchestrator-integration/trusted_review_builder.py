#!/usr/bin/env python3
"""Build immutable review inputs from observed Git state and gate executions."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path, PurePosixPath
from typing import Any

import requirements_traceability


class BuilderError(RuntimeError):
    pass


ALLOWED_GATE_PROGRAMS = {"bash", "git", "python", "python3"}
WORKSPACE = Path(__file__).resolve().parents[3]
REVIEW_VERDICT_SCHEMA = (
    WORKSPACE / "state/tasks/2026-08-11-codex-claude-orchestrator/implementation/review-verdict.schema.json"
)
PRIOR_DETAIL_BASE_REQUIRED = {
    "occurrence_id", "finding_id", "fingerprint", "title", "severity", "category",
    "criterion_id", "confidence", "proposed_disposition", "status",
}
PRIOR_DETAIL_MAJOR_REQUIRED = {
    "rationale", "failure_scenario", "reproduction", "evidence",
}


def _prior_detail_complete(value: Any, finding_id: str) -> bool:
    if not isinstance(value, dict) or value.get("finding_id") != finding_id:
        return False
    if not PRIOR_DETAIL_BASE_REQUIRED.issubset(value):
        return False
    if not all(isinstance(value.get(key), str) and value[key].strip()
               for key in ("occurrence_id", "finding_id", "title", "severity", "category",
                           "confidence", "proposed_disposition")):
        return False
    if not isinstance(value.get("fingerprint"), dict):
        return False
    if value.get("severity") in {"blocker", "major"}:
        return (PRIOR_DETAIL_MAJOR_REQUIRED.issubset(value)
                and isinstance(value.get("rationale"), str) and bool(value["rationale"].strip())
                and isinstance(value.get("failure_scenario"), str) and bool(value["failure_scenario"].strip())
                and isinstance(value.get("reproduction"), list) and bool(value["reproduction"])
                and isinstance(value.get("evidence"), list) and bool(value["evidence"])
                and (isinstance(value.get("location"), dict)
                     or isinstance(value.get("location_absent_reason"), str)))
    return value.get("severity") == "nit"


def _digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _digest(path: Path) -> str:
    return _digest_bytes(path.read_bytes())


def _canonical_digest(value: Any) -> str:
    return _digest_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
    if check and result.returncode != 0:
        raise BuilderError(f"git {' '.join(args)} failed")
    return result


def _head(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD").stdout.decode().strip()


def _status(root: Path) -> bytes:
    return _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout


def _ignored_state(root: Path) -> dict[str, str]:
    raw = _git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").stdout
    state = {}
    for item in raw.split(b"\0"):
        if not item:
            continue
        name = item.decode("utf-8")
        path = root / name
        if path.is_file() and not path.is_symlink():
            state[name] = _digest(path)
        else:
            state[name] = "special"
    return state


def capture_clean_baseline(project_root: Path) -> dict[str, str]:
    root = project_root.resolve()
    if not root.is_dir() or not (root / ".git").exists():
        raise BuilderError("project root is not a Git repository or worktree")
    status = _status(root)
    if status:
        raise BuilderError("project baseline is not clean")
    return {"head": _head(root), "status_digest": _digest_bytes(status), "ignored": _ignored_state(root)}


def _changed_paths(root: Path, baseline_head: str) -> list[str]:
    committed = _git(root, "diff", "--name-only", "-z", baseline_head).stdout
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "-z").stdout
    paths = {item.decode("utf-8") for item in (committed + untracked).split(b"\0") if item}
    return sorted(paths)


def _validate_scope(root: Path, paths: list[str], allowed: list[str]) -> None:
    if not paths:
        raise BuilderError("Codex attempt produced no observable change")
    prefixes = [PurePosixPath(item) for item in allowed]
    if not prefixes or any(item.is_absolute() or ".." in item.parts for item in prefixes):
        raise BuilderError("allowed paths are invalid")
    for raw in paths:
        path = PurePosixPath(raw)
        if path.is_absolute() or ".." in path.parts:
            raise BuilderError("changed path escapes repository")
        if not any(path == prefix or prefix in path.parents for prefix in prefixes):
            raise BuilderError(f"changed path is outside allowed scope: {raw}")
        candidate = root / raw
        if candidate.is_symlink():
            raise BuilderError(f"changed path is a symlink: {raw}")


def _tree_digest(root: Path, paths: list[str]) -> str:
    digest = hashlib.sha256()
    for raw in paths:
        path = root / raw
        digest.update(raw.encode("utf-8") + b"\0")
        if path.is_file():
            digest.update(path.read_bytes())
        else:
            digest.update(b"<deleted>")
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def _run_gate(root: Path, gate: dict[str, Any], out: Path, timeout: int) -> dict[str, Any]:
    if (not isinstance(gate, dict)
            or set(gate) not in ({"id", "argv"}, {"id", "argv", "expected_test_count"})):
        raise BuilderError("gate definition is invalid")
    gate_id, argv = gate["id"], gate["argv"]
    has_expected_test_count = "expected_test_count" in gate
    expected_test_count = gate.get("expected_test_count")
    if not isinstance(gate_id, str) or not gate_id or not gate_id.replace("-", "").replace("_", "").isalnum():
        raise BuilderError("gate id is invalid")
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
        raise BuilderError("gate argv is invalid")
    if has_expected_test_count and (
        not isinstance(expected_test_count, int) or isinstance(expected_test_count, bool)
        or expected_test_count < 1
    ):
        raise BuilderError("gate expected test count is invalid")
    if Path(argv[0]).name not in ALLOWED_GATE_PROGRAMS:
        raise BuilderError("gate program is not allowlisted")
    started = time.monotonic_ns()
    try:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(argv, cwd=root, capture_output=True, timeout=timeout, check=False, env=env)
        timed_out = False
        exit_code = result.returncode
        stdout, stderr = result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out, exit_code = True, 124
        stdout, stderr = exc.stdout or b"", exc.stderr or b""
    gate_dir = out / "gates" / gate_id
    gate_dir.mkdir(parents=True)
    (gate_dir / "stdout.log").write_bytes(stdout)
    (gate_dir / "stderr.log").write_bytes(stderr)
    record = {
        "gate_id": gate_id, "argv": argv, "exit_code": exit_code, "timed_out": timed_out,
        "duration_ms": (time.monotonic_ns() - started) // 1_000_000,
        "stdout_digest": _digest(gate_dir / "stdout.log"),
        "stderr_digest": _digest(gate_dir / "stderr.log"),
    }
    if has_expected_test_count:
        observed = re.findall(rb"(?m)^# tests ([0-9]+)\r?$", stdout)
        observed_test_count = int(observed[0]) if len(observed) == 1 else None
        record.update({
            "expected_test_count": expected_test_count,
            "observed_test_count": observed_test_count,
        })
    _write_json(gate_dir / "result.json", record)
    if exit_code != 0 or timed_out:
        raise BuilderError(f"required gate failed: {gate_id}")
    if has_expected_test_count and observed_test_count != expected_test_count:
        raise BuilderError(f"required gate test count mismatch: {gate_id}")
    return record


def build_review_inputs(
    project_root: Path, output_dir: Path, baseline: dict[str, Any], config: dict[str, Any], attempt: int,
    prior_context: dict[str, Any] | None = None, proof_chain: dict[str, Any] | None = None,
) -> dict[str, Path]:
    root, out = project_root.resolve(), output_dir.resolve()
    if out.exists():
        raise BuilderError("review input directory already exists")
    if _head(root) != baseline.get("head"):
        raise BuilderError("HEAD changed since baseline capture")
    required = {"task_id", "repo_id", "allowed_paths", "gates", "gate_timeout_seconds",
                "acceptance_criteria", "review_instructions", "policy_fixture", "review_verdict"}
    if not isinstance(config, dict) or set(config) != required:
        raise BuilderError("builder configuration fields are invalid")
    slug = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
    if not isinstance(config["task_id"], str) or not slug.fullmatch(config["task_id"]):
        raise BuilderError("task id is not reviewer-contract compatible")
    if not isinstance(config["repo_id"], str) or not slug.fullmatch(config["repo_id"]):
        raise BuilderError("repo id is not reviewer-contract compatible")
    if not isinstance(config["gates"], list) or not config["gates"]:
        raise BuilderError("at least one required gate is required")
    gate_ids = [gate.get("id") for gate in config["gates"] if isinstance(gate, dict)]
    if len(gate_ids) != len(config["gates"]) or len(set(gate_ids)) != len(gate_ids):
        raise BuilderError("gate ids must be unique")
    if not isinstance(config["gate_timeout_seconds"], int) or not 1 <= config["gate_timeout_seconds"] <= 1800:
        raise BuilderError("gate timeout is invalid")
    if _ignored_state(root) != baseline.get("ignored"):
        raise BuilderError("ignored files changed since baseline capture")
    out.mkdir(parents=True)
    paths = _changed_paths(root, baseline["head"])
    _validate_scope(root, paths, config["allowed_paths"])
    pre_gate_tree = _tree_digest(root, paths)
    gates = [_run_gate(root, gate, out, config["gate_timeout_seconds"]) for gate in config["gates"]]
    after_paths = _changed_paths(root, baseline["head"])
    if (_head(root) != baseline["head"] or after_paths != paths or _ignored_state(root) != baseline.get("ignored")
            or _tree_digest(root, after_paths) != pre_gate_tree):
        raise BuilderError("required gate mutated the reviewed subject")
    diff = _git(root, "diff", "--binary", "--no-ext-diff", "--no-textconv", "--no-renames", baseline["head"]).stdout
    untracked_parts = []
    for raw in paths:
        path = root / raw
        if path.is_file() and not _git(root, "ls-files", "--error-unmatch", "--", raw, check=False).returncode == 0:
            untracked_parts.append(raw.encode() + b"\0" + path.read_bytes() + b"\0")
    (out / "observed.diff").write_bytes(diff + b"".join(untracked_parts))
    _write_json(out / "changed-paths.json", paths)
    instructions = Path(config["review_instructions"])
    policy = Path(config["policy_fixture"])
    if not instructions.is_file() or not policy.is_file():
        raise BuilderError("trusted builder input is missing")
    criteria = config["acceptance_criteria"]
    if (not isinstance(criteria, list) or not criteria
            or not all(isinstance(x, dict) and set(x) in ({"id", "statement"}, {"id", "statement", "requirement_ids"})
                       and isinstance(x["id"], str) and re.fullmatch(r"AC-[0-9]{1,3}", x["id"])
                       and isinstance(x["statement"], str) and x["statement"]
                       and ("requirement_ids" not in x or isinstance(x["requirement_ids"], list)) for x in criteria)):
        raise BuilderError("acceptance criteria are invalid")
    spec_bytes = b"\n".join((x["id"] + "\0" + x["statement"]).encode() for x in criteria)
    frozen_digest = _digest_bytes(spec_bytes)
    if (attempt > 1 and isinstance(prior_context, dict)
            and "frozen_acceptance_criteria_digest" in prior_context
            and prior_context["frozen_acceptance_criteria_digest"] != frozen_digest):
        raise BuilderError("acceptance criteria changed after the initial review")
    criteria_document = {
        "document_type": "trusted_acceptance_criteria", "schema_version": "1.0.0",
        "criteria": [{"criterion_id": x["id"], "statement": x["statement"],
                     "statement_digest": _digest_bytes(x["statement"].encode()),
                     **({"requirement_ids": x["requirement_ids"]} if "requirement_ids" in x else {})}
                    for x in criteria],
    }
    _write_json(out / "acceptance-criteria.json", criteria_document)
    if not REVIEW_VERDICT_SCHEMA.is_file():
        raise BuilderError("accepted review verdict schema is missing")
    (out / "review-verdict.schema.json").write_bytes(REVIEW_VERDICT_SCHEMA.read_bytes())
    tree_digest = pre_gate_tree
    run_id = f"run_{config['task_id']}.attempt-{attempt}"
    if len(run_id.removeprefix("run_")) > 64:
        raise BuilderError("generated run id is not reviewer-contract compatible")
    review_mode = "initial_full" if attempt == 1 else "targeted_verification" if attempt == 2 else "final_full"
    manifest = {
        "document_type": "trusted_review_manifest", "schema_version": "1.0.0",
        "subject": {"task_id": config["task_id"], "run_id": run_id, "attempt": attempt,
                    "repo_id": config["repo_id"], "base_commit": baseline["head"],
                    "head_commit": baseline["head"], "diff_digest": _digest(out / "observed.diff"),
                    "changed_files_digest": _digest(out / "changed-paths.json"),
                    "gate_run_id_pre": "run_builder-baseline", "gate_run_id_post": run_id},
        "expected_review_mode": review_mode,
        "expected_coverage_scope": "targeted" if review_mode == "targeted_verification" else "full",
        "acceptance_criteria_digest": frozen_digest,
        "review_instructions_digest": _digest(instructions),
        "criteria": [{"criterion_id": x["id"], "statement_digest": _digest_bytes(x["statement"].encode())} for x in criteria],
    }
    binding = {
        "document_type": "review_projection_binding", "schema_version": "1.0.0",
        "task_id": config["task_id"], "spec_digest": frozen_digest, "run_id": run_id,
        "attempt_epoch": attempt, "reviewed_tree_digest": tree_digest, "covered_paths": paths,
    }
    evidence = {
        "document_type": "trusted_review_evidence", "schema_version": "1.0.0", "run_id": run_id,
        "baseline": baseline, "reviewed_tree_digest": tree_digest, "changed_paths": paths,
        "artifacts": {"diff": manifest["subject"]["diff_digest"],
                      "changed_paths": manifest["subject"]["changed_files_digest"],
                      "review_instructions": manifest["review_instructions_digest"],
                      "acceptance_criteria": _digest(out / "acceptance-criteria.json"),
                      "review_verdict_schema": _digest(out / "review-verdict.schema.json")},
        "gates": gates,
    }
    proof_artifacts: dict[str, str] = {}
    if proof_chain is not None:
        try:
            requirements_traceability.validate_preflight(
                proof_chain["manifest"], proof_chain["specification"], proof_chain["task_map"]
            )
        except (KeyError, requirements_traceability.TraceabilityError) as exc:
            raise BuilderError(f"requirements proof-chain is invalid: {exc}") from exc
        for name, key in (("requirements-manifest.json", "manifest"),
                          ("requirements-specification.json", "specification"),
                          ("requirements-task-map.json", "task_map")):
            _write_json(out / name, proof_chain[key])
            proof_artifacts[name] = _digest(out / name)
        evidence["requirements_manifest_digest"] = proof_chain["manifest"]["immutable_core_digest"]
        evidence["artifacts"].update(proof_artifacts)
    for name, value in (("manifest.json", manifest), ("binding.json", binding), ("evidence.json", evidence)):
        _write_json(out / name, value)
    try:
        template = json.loads(policy.read_text(encoding="utf-8"))
        budgets = template["task_policy"]["budgets"]
        infra = template["task_policy"].get("infra_signature_allowlist", [])
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise BuilderError("policy template is invalid") from exc
    evidence_artifacts = []
    requirements = []
    for gate in gates:
        result_path = out / "gates" / gate["gate_id"] / "result.json"
        req_id = "gate-" + gate["gate_id"]
        digest = _digest(result_path)
        requirements.append({"req_id": req_id, "digest": digest, "digest_required": True})
        evidence_artifacts.append({"req_id": req_id, "digest": digest, "bytes": result_path.stat().st_size})
    task_policy = {"document_type": "orchestrator_task_policy", "schema_version": "1.0.0",
                   "task_id": config["task_id"], "spec_digest": binding["spec_digest"], "run_id": run_id,
                   "mandatory_gates": gate_ids, "required_evidence": requirements,
                   "infra_signature_allowlist": infra, "budgets": budgets}
    previous = prior_context or {}
    counters = previous.get("budgets_after", {"rework_used": 0, "infra_total_used": 0,
        "infra_used_by_signature": {}, "final_full_used": 0, "no_progress_streak": 0})
    prior_attempts = list(previous.get("prior_attempts", []))
    if previous.get("last_decision"):
        prior_attempts.append({"attempt_epoch": attempt - 1, **previous["last_decision"]})
    ledger = {"document_type": "orchestrator_ledger", "schema_version": "1.0.0",
              "task_id": config["task_id"], "spec_digest": binding["spec_digest"], "run_id": run_id,
              "current_epoch": attempt, "last_epoch": attempt - 1,
              "seen_nonces": previous.get("seen_nonces", []),
              "expected_subject": {"tree_digest": tree_digest, "changed_paths": paths},
              "counters": counters,
              "finding_registry": previous.get("finding_registry", {
                  "document_type": "finding_registry", "schema_version": "1.0.0", "findings": []}),
              "prior_attempts": prior_attempts, "terminal_decision": None}
    execution = {"document_type": "execution_report", "schema_version": "1.0.0",
                 "task_id": config["task_id"], "spec_digest": binding["spec_digest"], "run_id": run_id,
                 "attempt_epoch": attempt, "nonce": f"{run_id}-nonce",
                 "subject": {"tree_digest": tree_digest, "changed_paths": paths}, "exit_status": "OK",
                 "failure_signatures": [], "gate_results": {gate_id: "PASS" for gate_id in gate_ids},
                 "evidence_artifacts": evidence_artifacts}
    _write_json(out / "policy.json", {"document_type": "policy_fixture", "schema_version": "1.0.0",
                                      "task_policy": task_policy, "ledger": ledger, "execution_report": execution})
    (out / "review-instructions.md").write_bytes(instructions.read_bytes())
    verdict = PurePosixPath(config["review_verdict"])
    if verdict.is_absolute() or ".." in verdict.parts:
        raise BuilderError("review verdict path is invalid")
    prior_findings_name = None
    if review_mode == "targeted_verification":
        registry_findings = previous.get("finding_registry", {}).get("findings", [])
        detail_by_id = previous.get("prior_finding_details", {})
        if not isinstance(detail_by_id, dict):
            raise BuilderError("prior finding details are invalid")
        open_ids = [item.get("finding_id") for item in registry_findings
                    if item.get("status") == "open" and isinstance(item.get("finding_id"), str)]
        if any(finding_id not in detail_by_id for finding_id in open_ids):
            raise BuilderError("targeted verification requires complete prior finding details")
        if any(not _prior_detail_complete(detail_by_id[finding_id], finding_id)
               for finding_id in open_ids):
            raise BuilderError("targeted verification prior finding details are incomplete")
        prior_findings = {"document_type": "prior_findings", "schema_version": "1.0.0",
                          "findings": [detail_by_id[finding_id] for finding_id in open_ids]}
        if not prior_findings["findings"]:
            raise BuilderError("targeted verification requires open prior findings")
        prior_findings_name = "prior-findings.json"
        _write_json(out / prior_findings_name, prior_findings)
    review_context = {
        "document_type": "trusted_review_context", "schema_version": "1.0.0",
        "review_verdict_schema_digest": _digest(out / "review-verdict.schema.json"),
        "prior_findings_canonical_digest": _canonical_digest(prior_findings) if prior_findings_name else None,
    }
    _write_json(out / "review-context.json", review_context)
    bundle = {"document_type": "local_orchestrator_run", "schema_version": "1.0.0",
              "run_name": run_id, "policy_fixture": "policy.json", "review_verdict": str(verdict),
              "trusted_manifest": "manifest.json", "projection_binding": "binding.json",
              "prior_findings": prior_findings_name}
    _write_json(out / "bundle.json", bundle)
    seal = {name: _digest(out / name) for name in ("observed.diff", "changed-paths.json",
                                                    "acceptance-criteria.json", "manifest.json",
                                                    "binding.json", "evidence.json", "policy.json", "bundle.json",
                                                    "review-instructions.md", "review-verdict.schema.json",
                                                    "review-context.json")}
    seal.update(proof_artifacts)
    if prior_findings_name:
        seal[prior_findings_name] = _digest(out / prior_findings_name)
    _write_json(out / "seal.json", seal)
    for path in out.rglob("*"):
        if path.is_file():
            path.chmod(0o444)
    return {"input_dir": out, "bundle": out / "bundle.json", "seal": out / "seal.json"}


def verify_seal(
    input_dir: Path, project_root: Path | None = None, *, expected_seal_digest: str | None = None,
) -> None:
    seal_path = input_dir / "seal.json"
    if expected_seal_digest is not None and _digest(seal_path) != expected_seal_digest:
        raise BuilderError("review input seal root digest mismatch")
    try:
        seal = json.loads(seal_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuilderError("review input seal is unreadable") from exc
    if not isinstance(seal, dict):
        raise BuilderError("review input seal is invalid")
    for name, expected in seal.items():
        path = input_dir / name
        if path.is_symlink() or not path.is_file() or _digest(path) != expected:
            raise BuilderError(f"review input digest mismatch: {name}")
    try:
        evidence = json.loads((input_dir / "evidence.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuilderError("review evidence is unreadable") from exc
    for gate in evidence.get("gates", []):
        gate_dir = input_dir / "gates" / gate["gate_id"]
        result_path = gate_dir / "result.json"
        try:
            if json.loads(result_path.read_text(encoding="utf-8")) != gate:
                raise BuilderError(f"gate result mismatch: {gate['gate_id']}")
        except (OSError, json.JSONDecodeError) as exc:
            raise BuilderError(f"gate result is unreadable: {gate['gate_id']}") from exc
        for name in ("stdout", "stderr"):
            path = gate_dir / f"{name}.log"
            if path.is_symlink() or not path.is_file() or _digest(path) != gate[f"{name}_digest"]:
                raise BuilderError(f"gate evidence digest mismatch: {gate['gate_id']}/{name}")
    expected_files = {"seal.json", *seal}
    for gate in evidence.get("gates", []):
        expected_files.update({f"gates/{gate['gate_id']}/result.json", f"gates/{gate['gate_id']}/stdout.log",
                               f"gates/{gate['gate_id']}/stderr.log"})
    actual_files = {str(path.relative_to(input_dir)) for path in input_dir.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        raise BuilderError("review input file set mismatch")
    if project_root is not None:
        paths = evidence.get("changed_paths")
        if not isinstance(paths, list) or _tree_digest(project_root.resolve(), paths) != evidence.get("reviewed_tree_digest"):
            raise BuilderError("reviewed tree changed after evidence capture")
