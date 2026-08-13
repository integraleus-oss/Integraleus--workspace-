#!/usr/bin/env python3
"""Launch one fresh Claude review and evaluate it with the accepted policy."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Callable

import agent_launcher
import local_orchestrator_runner
from review_projection import ContractValidationError, ProjectionError


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def run_cycle(
    project_root: Path,
    prompt_path: Path,
    bundle_path: Path,
    cycle_root: Path,
    *,
    timeout_seconds: int = 300,
    pre_admission_verify: Callable[[], None] | None = None,
    allow_format_retry: bool = False,
    allow_contract_retry: bool = False,
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

    if pre_admission_verify is not None:
        pre_admission_verify()

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
    active_launch_root = cycle_root / "claude-launch"
    format_retry_launch = None
    contract_retry_launch = None
    contract_format_retry_launch = None
    try:
        try:
            agent_launcher.extract_claude_verdict(active_launch_root, verdict_path)
        except agent_launcher.LaunchError as exc:
            if not allow_format_retry or str(exc) != "Claude result does not contain exact JSON":
                raise
            if pre_admission_verify is not None:
                pre_admission_verify()
            retry_prompt = (
                prompt
                + "\n\nFORMAT-ONLY RETRY (one retry maximum): Your prior response was rejected only "
                  "because it was not exact JSON. Re-read the same sealed inputs. Return exactly one JSON "
                  "object matching the required review-verdict contract, with no prose, markdown, or code fences. "
                  "Do not change the substantive findings.\n"
            )
            active_launch_root = cycle_root / "claude-format-retry"
            format_retry_launch = agent_launcher.launch(
                "claude", project_root, retry_prompt, active_launch_root,
                timeout_seconds=timeout_seconds,
            )
            if format_retry_launch["status"] != "OK":
                raise agent_launcher.LaunchError("Claude format-only retry failed")
            if pre_admission_verify is not None:
                pre_admission_verify()
            agent_launcher.extract_claude_verdict(active_launch_root, verdict_path)
        try:
            decision_dir, manifest = local_orchestrator_runner.run(bundle_path, cycle_root / "policy-runs")
        except ContractValidationError as exc:
            if not allow_contract_retry:
                raise
            first_verdict = cycle_root / "contract-repair-first-verdict.json"
            shutil.copyfile(verdict_path, first_verdict)
            first_verdict.chmod(0o444)
            failed_runs = list((cycle_root / "policy-runs").iterdir())
            if len(failed_runs) != 1 or not (failed_runs[0] / "run-error.json").is_file():
                raise ProjectionError("contract-repair retry cannot identify one failed admission")
            failed_runs[0].replace(cycle_root / "contract-repair-first-admission")
            verdict_path.unlink()
            if pre_admission_verify is not None:
                pre_admission_verify()
            retry_prompt = (
                prompt
                + "\n\nCONTRACT-ONLY REPAIR (one retry maximum): The prior exact-JSON verdict was "
                  "rejected by the deterministic contract validator. Preserve every substantive finding, "
                  "status, evidence item, digest, and conclusion meaning. Change only fields required to "
                  "satisfy the sealed review-verdict.schema.json. Return exactly one JSON object with no prose.\n"
                  "Exact validator report:\n"
                + json.dumps(exc.validation, sort_keys=True, separators=(",", ":"))
                + "\n"
            )
            active_launch_root = cycle_root / "claude-contract-retry"
            contract_retry_launch = agent_launcher.launch(
                "claude", project_root, retry_prompt, active_launch_root,
                timeout_seconds=timeout_seconds,
            )
            if contract_retry_launch["status"] != "OK":
                raise agent_launcher.LaunchError("Claude contract-only retry failed")
            if pre_admission_verify is not None:
                pre_admission_verify()
            try:
                agent_launcher.extract_claude_verdict(active_launch_root, verdict_path)
            except agent_launcher.LaunchError as repair_exc:
                if str(repair_exc) != "Claude result does not contain exact JSON":
                    raise
                if pre_admission_verify is not None:
                    pre_admission_verify()
                repair_format_prompt = (
                    retry_prompt
                    + "\n\nCONTRACT-REPAIR FORMAT-ONLY RETRY (one retry maximum): Your contract-repair "
                      "response was rejected only because it was not exact JSON. Re-read the same sealed "
                      "inputs and the same validator report. Return exactly the same repaired verdict as one "
                      "JSON object, with no prose, markdown, or code fences. Do not change any substantive "
                      "finding, status, evidence item, digest, or conclusion meaning.\n"
                )
                active_launch_root = cycle_root / "claude-contract-format-retry"
                contract_format_retry_launch = agent_launcher.launch(
                    "claude", project_root, repair_format_prompt, active_launch_root,
                    timeout_seconds=timeout_seconds,
                )
                if contract_format_retry_launch["status"] != "OK":
                    raise agent_launcher.LaunchError("Claude contract-repair format-only retry failed")
                if pre_admission_verify is not None:
                    pre_admission_verify()
                agent_launcher.extract_claude_verdict(active_launch_root, verdict_path)
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
        "format_retry_launch": format_retry_launch,
        "contract_retry_launch": contract_retry_launch,
        "contract_format_retry_launch": contract_format_retry_launch,
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
