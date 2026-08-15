#!/usr/bin/env python3
"""Bounded launch adapter for the approved local Codex and Claude wrappers."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any


CODEX_WRAPPER = Path("/home/stanislav/.openclaw/workspace/agents/main/scripts/codex-local-run.sh")
CLAUDE_WRAPPER = Path("/home/stanislav/agent-runs/_bin/claude-review")
ROLES = {"codex", "claude"}


class LaunchError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _terminate_process_group(process: subprocess.Popen[str]) -> tuple[str, str]:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        try:
            return process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.communicate(timeout=2)
    try:
        return process.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return process.communicate(timeout=2)


def launch(
    role: str,
    project_root: Path,
    prompt: str,
    run_dir: Path,
    *,
    timeout_seconds: int = 300,
    codex_write: bool = False,
) -> dict[str, Any]:
    if role not in ROLES:
        raise LaunchError("unsupported agent role")
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise LaunchError("project_root is not a directory")
    if not isinstance(prompt, str) or not prompt.strip():
        raise LaunchError("prompt must be non-empty")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 1800:
        raise LaunchError("timeout_seconds must be between 1 and 1800")
    run_dir = run_dir.resolve()
    wrapper = (CODEX_WRAPPER if role == "codex" else CLAUDE_WRAPPER).resolve()
    if not wrapper.is_file() or not os.access(wrapper, os.X_OK):
        raise LaunchError("approved wrapper is missing or not executable")
    if run_dir.exists():
        raise LaunchError("launch run directory already exists")
    run_dir.mkdir(parents=True)
    prompt_path = run_dir / "input-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    prompt_path.chmod(0o444)
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"

    if role == "codex":
        argv = [str(wrapper), "--cd", str(project_root), "--write" if codex_write else "--read-only", "--", prompt]
    else:
        argv = [str(wrapper), str(project_root), str(prompt_path), str(run_dir / "wrapper-output.json"), str(timeout_seconds)]

    started = time.monotonic_ns()
    timed_out = False
    interrupted = False
    saved_sigint_handler: Any = None
    process: subprocess.Popen[str] | None = None
    try:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        process = subprocess.Popen(
            argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True, env=env,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            exit_code = process.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout, stderr = _terminate_process_group(process)
            exit_code = 124
            if exc.stdout:
                partial = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout
                if not stdout.startswith(partial):
                    stdout = partial + stdout
            if exc.stderr:
                partial = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
                if not stderr.startswith(partial):
                    stderr = partial + stderr
        except KeyboardInterrupt:
            saved_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
            interrupted = True
            try:
                stdout, stderr = _terminate_process_group(process)
            except BaseException as exc:
                stdout, stderr = "", f"teardown error: {type(exc).__name__}: {exc}\n"
            exit_code = 130
    except KeyboardInterrupt:
        saved_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        interrupted = True
        try:
            stdout, stderr = _terminate_process_group(process) if process is not None else ("", "")
        except BaseException as exc:
            stdout, stderr = "", f"teardown error: {type(exc).__name__}: {exc}\n"
        exit_code = 130
    except OSError as exc:
        exit_code = 126
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}\n"
    try:
        ended = time.monotonic_ns()
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        result = {
            "document_type": "local_agent_launch_result",
            "schema_version": "1.0.0",
            "role": role,
            "status": "INTERRUPTED" if interrupted else "OK" if exit_code == 0 and not timed_out else "FAILED",
            "exit_code": exit_code,
            "timed_out": timed_out,
            "duration_ms": (ended - started) // 1_000_000,
            "project_root": str(project_root),
            "wrapper": str(wrapper),
            "sandbox": "workspace-write" if role == "codex" and codex_write else "read-only",
            "prompt_digest": _sha256(prompt_path),
            "stdout_digest": _sha256(stdout_path),
            "stderr_digest": _sha256(stderr_path),
        }
        wrapper_output = run_dir / "wrapper-output.json"
        if wrapper_output.is_file():
            result["wrapper_output_digest"] = _sha256(wrapper_output)
        _write_json(run_dir / "launch-result.json", result)
        return result
    finally:
        if saved_sigint_handler is not None:
            signal.signal(signal.SIGINT, saved_sigint_handler)


def extract_claude_verdict(run_dir: Path, verdict_path: Path) -> dict[str, Any]:
    output_path = run_dir / "wrapper-output.json"
    if not output_path.is_file():
        raise LaunchError("Claude wrapper output is missing")
    try:
        envelope = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LaunchError("Claude wrapper output is not valid JSON") from exc
    if not isinstance(envelope, dict) or "result" not in envelope:
        raise LaunchError("Claude wrapper envelope has no result")
    if envelope.get("is_error"):
        raise LaunchError("Claude wrapper reported an error")
    payload: Any = envelope["result"]
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise LaunchError("Claude result does not contain exact JSON") from exc
    if not isinstance(payload, dict):
        raise LaunchError("Claude verdict root is not an object")
    _write_json(verdict_path, payload)
    _write_json(run_dir / "verdict-extraction.json", {
        "document_type": "local_verdict_extraction",
        "schema_version": "1.0.0",
        "source": str(output_path),
        "source_digest": _sha256(output_path),
        "verdict": str(verdict_path),
        "verdict_digest": _sha256(verdict_path),
    })
    return payload
