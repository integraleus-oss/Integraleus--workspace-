#!/usr/bin/env python3
"""Foreground-only adapter for one prebuilt production packet per invocation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import production_cycle_cli


class AdapterError(RuntimeError):
    pass


APPROVED_PACKET_ROOT = Path("/home/stanislav/.openclaw/workspace/agents/main/state/tasks")


def _inside_packet_root(path: Path) -> Path:
    if path.is_symlink():
        raise AdapterError("packet symlinks are forbidden")
    resolved = path.resolve()
    root = APPROVED_PACKET_ROOT.resolve()
    if not resolved.is_file() or not resolved.is_relative_to(root):
        raise AdapterError("packet is outside the approved task root")
    return resolved


def run_one(packet_path: Path) -> dict[str, Any]:
    packet_path = _inside_packet_root(packet_path)
    packet = production_cycle_cli.load_packet(packet_path)
    if packet.get("schema_version") != "1.3.0" or packet.get("control_mode") != "manual":
        raise AdapterError("foreground adapter requires a manual schema-1.3 packet")
    result = production_cycle_cli.run_packet(packet_path, foreground_authorized=True)
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
