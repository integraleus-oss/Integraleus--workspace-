#!/usr/bin/env python3
"""Launch one fresh Claude review and evaluate it with the accepted policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import agent_launcher
import local_orchestrator_runner
from review_projection import ProjectionError


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def run_cycle(
    project_root: Path,
    prompt_path: Path,
    bundle_path: Path,
    cycle_root: Path,
    *,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    if cycle_root.exists():
        raise ProjectionError("cycle directory already exists")
    cycle_root.mkdir(parents=True)
    prompt = prompt_path.read_text(encoding="utf-8")
    launch_result = agent_launcher.launch(
        "claude", project_root, prompt, cycle_root / "claude-launch",
        timeout_seconds=timeout_seconds,
    )
    if launch_result["status"] != "OK":
        result = {
            "document_type": "local_live_review_cycle_result",
            "schema_version": "1.0.0",
            "status": "FAILED_LAUNCH",
            "launch": launch_result,
            "decision": None,
        }
        _write_json(cycle_root / "cycle-result.json", result)
        return result

    bundle = local_orchestrator_runner.POLICY.parse_json_file(bundle_path)
    if not isinstance(bundle, dict) or not isinstance(bundle.get("review_verdict"), str):
        raise ProjectionError("bundle has no review_verdict path")
    verdict_relative = Path(bundle["review_verdict"])
    if verdict_relative.is_absolute() or ".." in verdict_relative.parts:
        raise ProjectionError("review_verdict path escapes bundle directory")
    bundle_base = bundle_path.resolve().parent
    verdict_path = (bundle_base / verdict_relative).resolve()
    if not verdict_path.is_relative_to(bundle_base):
        raise ProjectionError("review_verdict path escapes bundle directory")
    if verdict_path.exists():
        raise ProjectionError("generated review verdict already exists")
    verdict_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        agent_launcher.extract_claude_verdict(cycle_root / "claude-launch", verdict_path)
        decision_dir, manifest = local_orchestrator_runner.run(bundle_path, cycle_root / "policy-runs")
    except Exception as exc:
        verdict_path.unlink(missing_ok=True)
        _write_json(cycle_root / "cycle-result.json", {
            "document_type": "local_live_review_cycle_result",
            "schema_version": "1.0.0",
            "status": "FAILED_ADMISSION",
            "launch": launch_result,
            "decision": None,
            "error": {"type": type(exc).__name__, "message": str(exc)},
        })
        raise
    verdict_path.unlink(missing_ok=True)
    result = {
        "document_type": "local_live_review_cycle_result",
        "schema_version": "1.0.0",
        "status": "DECIDED",
        "launch": launch_result,
        "decision": manifest,
        "decision_dir": str(decision_dir),
    }
    _write_json(cycle_root / "cycle-result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--cycle-root", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    try:
        result = run_cycle(args.project_root, args.prompt, args.bundle, args.cycle_root, timeout_seconds=args.timeout)
        code = 0 if result["status"] == "DECIDED" else 3
    except Exception as exc:
        result = {"status": "ERROR", "error": {"type": type(exc).__name__, "message": str(exc)}}
        code = 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
