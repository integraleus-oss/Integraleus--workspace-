#!/usr/bin/env python3
"""Run one isolated deterministic orchestrator evaluation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any

from review_projection import CORE, ProjectionError, build_projection


def _load_policy() -> Any:
    spec = importlib.util.spec_from_file_location("orchestrator_policy_core", CORE / "orchestrator_policy.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load accepted policy core")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


POLICY = _load_policy()


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def run(bundle_path: Path, runs_root: Path) -> tuple[Path, dict[str, Any]]:
    bundle = POLICY.parse_json_file(bundle_path)
    required = {
        "document_type", "schema_version", "run_name", "policy_fixture", "review_verdict",
        "trusted_manifest", "projection_binding", "prior_findings",
    }
    if not isinstance(bundle, dict) or set(bundle) != required:
        raise ProjectionError("run bundle has missing or unknown fields")
    if bundle["document_type"] != "local_orchestrator_run" or bundle["schema_version"] != "1.0.0":
        raise ProjectionError("unsupported run bundle")
    run_name = bundle["run_name"]
    if not isinstance(run_name, str) or not run_name or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for ch in run_name):
        raise ProjectionError("invalid run_name")
    run_dir = runs_root / run_name
    if run_dir.exists():
        raise ProjectionError("run directory already exists; replay must use a new run_name")
    run_dir.mkdir(parents=True)
    snapshots: dict[str, Path] = {}
    try:
        base = bundle_path.resolve().parent
        names = ["policy_fixture", "review_verdict", "trusted_manifest", "projection_binding"]
        if bundle["prior_findings"] is not None:
            names.append("prior_findings")
        for name in names:
            relative = Path(bundle[name])
            if relative.is_absolute() or ".." in relative.parts:
                raise ProjectionError(f"input path escapes bundle directory: {name}")
            source = (base / relative).resolve()
            if not source.is_relative_to(base) or not source.is_file():
                raise ProjectionError(f"missing or escaping input file: {name}")
            target = run_dir / f"input-{name}.json"
            shutil.copyfile(source, target)
            target.chmod(0o444)
            snapshots[name] = target
        bundle_snapshot = run_dir / "input-run-bundle.json"
        shutil.copyfile(bundle_path, bundle_snapshot)
        bundle_snapshot.chmod(0o444)

        prior = snapshots.get("prior_findings")
        projection, validation = build_projection(
            snapshots["review_verdict"], snapshots["trusted_manifest"], snapshots["projection_binding"], prior
        )
        fixture = POLICY.parse_json_file(snapshots["policy_fixture"])
        for key in ("task_policy", "ledger", "execution_report"):
            if key not in fixture:
                raise ProjectionError(f"policy fixture missing {key}")
        decision = POLICY.decide(fixture["task_policy"], fixture["ledger"], fixture["execution_report"], projection)
        if decision.get("outcome") == "ACCEPTED" and not validation.get("contract_valid"):
            raise ProjectionError("fail-closed invariant violated")
    except Exception as exc:
        error = {
            "document_type": "local_orchestrator_run_error",
            "schema_version": "1.0.0",
            "run_name": run_name,
            "error": {"type": type(exc).__name__, "message": str(exc)},
            "input_digests": {name: _sha256(path) for name, path in sorted(snapshots.items())},
        }
        _write_json(run_dir / "run-error.json", error)
        raise

    _write_json(run_dir / "review-validation.json", validation)
    _write_json(run_dir / "trusted-review-projection.json", projection)
    _write_json(run_dir / "decision.json", decision)
    manifest = {
        "document_type": "local_orchestrator_run_result",
        "schema_version": "1.0.0",
        "run_name": run_name,
        "outcome": decision["outcome"],
        "rule_id": decision["rule_id"],
        "exit_status": "OK",
        "run_bundle_digest": _sha256(run_dir / "input-run-bundle.json"),
        "input_digests": {name: _sha256(path) for name, path in sorted(snapshots.items())},
        "projection_digest": _sha256(run_dir / "trusted-review-projection.json"),
        "decision_digest_file": _sha256(run_dir / "decision.json"),
    }
    _write_json(run_dir / "run-result.json", manifest)
    return run_dir, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--runs-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        run_dir, result = run(args.bundle, args.runs_root)
        output = {"ok": True, "run_dir": str(run_dir), "result": result}
        code = 0
    except Exception as exc:
        output = {"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}
        code = 2
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
