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
AUTHORIZATION_REGISTRY = Path("/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-16-orchestrator-proof-chain/manual-authorizations.json")
AUTHORIZATION_LEDGER = Path("/home/stanislav/agent-runs/orchestrator-authorizations-used")


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
    try:
        registry = json.loads(AUTHORIZATION_REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdapterError("trusted manual authorization registry is unavailable") from exc
    authorization_digest = _digest(authorization_path)
    allowed = registry.get("authorizations") if isinstance(registry, dict) else None
    if (not isinstance(allowed, list) or not any(
            isinstance(item, dict) and item.get("authorization_digest") == authorization_digest
            and item.get("packet_digest") == value["packet_digest"]
            and item.get("source_message_id") == value["source_message_id"] for item in allowed)):
        raise AdapterError("manual authorization is not admitted by the trusted registry")
    AUTHORIZATION_LEDGER.mkdir(parents=True, exist_ok=True)
    identity = hashlib.sha256((authorization_digest + "\0" + value["packet_digest"] + "\0" +
                               value["source_message_id"]).encode("utf-8")).hexdigest()
    used = AUTHORIZATION_LEDGER / f"{identity}.json"
    try:
        with used.open("x", encoding="utf-8") as marker:
            marker.write(json.dumps({"authorization_digest": authorization_digest,
                                     "packet_digest": _digest(packet_path),
                                     "source_message_id": value["source_message_id"]}, sort_keys=True) + "\n")
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
