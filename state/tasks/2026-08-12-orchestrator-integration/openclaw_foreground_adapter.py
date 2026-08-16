#!/usr/bin/env python3
"""Foreground-only adapter for one prebuilt production packet per invocation."""

from __future__ import annotations

import argparse
import hashlib
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


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _admit_authorization(packet_path: Path, authorization_path: Path) -> Path:
    authorization_path = _inside_packet_root(authorization_path)
    try:
        value = json.loads(authorization_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdapterError("manual authorization is unreadable") from exc
    required = {"document_type", "schema_version", "packet_digest", "approved_by", "source_message_id"}
    if (not isinstance(value, dict) or set(value) != required
            or value["document_type"] != "manual_foreground_authorization"
            or value["schema_version"] != "1.0.0"
            or value["packet_digest"] != _digest(packet_path)
            or value["approved_by"] != "Stanislav Pavlovskiy"
            or not isinstance(value["source_message_id"], str) or not value["source_message_id"].strip()):
        raise AdapterError("manual authorization does not match the packet and owner")
    used = authorization_path.with_suffix(authorization_path.suffix + ".used")
    try:
        with used.open("x", encoding="utf-8") as marker:
            marker.write(json.dumps({"authorization_digest": _digest(authorization_path),
                                     "packet_digest": _digest(packet_path)}, sort_keys=True) + "\n")
    except FileExistsError as exc:
        raise AdapterError("manual authorization is already used") from exc
    return used


def run_one(packet_path: Path, authorization_path: Path) -> dict[str, Any]:
    packet_path = _inside_packet_root(packet_path)
    packet = production_cycle_cli.load_packet(packet_path)
    if packet.get("schema_version") != "1.3.0" or packet.get("control_mode") != "manual":
        raise AdapterError("foreground adapter requires a manual schema-1.3 packet")
    marker = _admit_authorization(packet_path, authorization_path)
    result = production_cycle_cli.run_packet(packet_path, foreground_authorized=True)
    if result.get("status") not in {"ACCEPTED", "ESCALATED", "FAILED_INFRA", "INTERRUPTED"}:
        raise AdapterError("orchestrator returned an invalid terminal status")
    return {**result, "manual_authorization_marker": str(marker)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("authorization", type=Path)
    args = parser.parse_args()
    try:
        result = run_one(args.packet, args.authorization)
        code = 0 if result["status"] == "ACCEPTED" else 130 if result["status"] == "INTERRUPTED" else 4
    except BaseException as exc:
        interrupted = isinstance(exc, KeyboardInterrupt)
        result = {"status": "INTERRUPTED" if interrupted else "ERROR",
                  "error": {"type": type(exc).__name__, "message": str(exc)}}
        code = 130 if interrupted else 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
