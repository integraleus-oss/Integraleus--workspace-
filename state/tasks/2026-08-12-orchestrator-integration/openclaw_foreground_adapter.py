#!/usr/bin/env python3
"""Foreground-only adapter for one prebuilt production packet per invocation."""

from __future__ import annotations

import argparse
import fcntl
import json
from pathlib import Path
from typing import Any

import production_cycle_cli


class AdapterError(RuntimeError):
    pass


APPROVED_PACKET_ROOT = Path("/home/stanislav/.openclaw/workspace/agents/main/state/tasks")
DEFAULT_LOCK = Path("/home/stanislav/agent-runs/orchestrator-foreground.lock")


def _inside_packet_root(path: Path) -> Path:
    resolved = path.resolve()
    root = APPROVED_PACKET_ROOT.resolve()
    if resolved.is_symlink() or not resolved.is_file() or not resolved.is_relative_to(root):
        raise AdapterError("packet is outside the approved task root")
    return resolved


def run_one(packet_path: Path, lock_path: Path = DEFAULT_LOCK) -> dict[str, Any]:
    packet_path = _inside_packet_root(packet_path)
    packet = production_cycle_cli.load_packet(packet_path)
    if packet.get("schema_version") != "1.3.0" or packet.get("control_mode") != "manual":
        raise AdapterError("foreground adapter requires a manual schema-1.3 packet")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise AdapterError("another orchestrator task is already running") from exc
        result = production_cycle_cli.run_packet(packet_path)
        if result.get("status") not in {"ACCEPTED", "ESCALATED", "FAILED_INFRA", "INTERRUPTED"}:
            raise AdapterError("orchestrator returned an invalid terminal status")
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    try:
        result = run_one(args.packet)
        code = 0 if result["status"] == "ACCEPTED" else 130 if result["status"] == "INTERRUPTED" else 4
    except Exception as exc:
        result = {"status": "ERROR", "error": {"type": type(exc).__name__, "message": str(exc)}}
        code = 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
