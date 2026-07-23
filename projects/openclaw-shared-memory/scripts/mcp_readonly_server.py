#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlunparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openclaw_shared_memory.config import Settings
from openclaw_shared_memory.repository import MemoryRepository


SERVER_INFO = {
    "name": "openclaw-shared-memory-readonly",
    "version": "0.1.0",
}

READONLY_TOOLS = [
    {
        "name": "search_memory",
        "description": "Search shared memory smoke/canon records visible to the reader privacy policy.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "query": {"type": "string", "minLength": 1},
                "scope": {"type": "string"},
                "status": {"type": "string", "default": "shared"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
                "caller": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_with_audit",
        "description": "Fetch one visible memory record with its audit trail.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "record_id": {"type": "string", "minLength": 1},
                "caller": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["record_id"],
        },
    },
    {
        "name": "list_candidates",
        "description": "List candidate memory records visible to the reader privacy policy.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "scope": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 20},
                "caller": {"type": "string"},
                "reason": {"type": "string"},
            },
        },
    },
]


def env_required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Set {name}")
    return value


def role_url(username: str, password: str) -> str:
    host = os.environ.get("OPENCLAW_MEMORY_BIND_HOST", "192.168.68.125")
    port = os.environ.get("OPENCLAW_MEMORY_PORT", "55432")
    dbname = os.environ.get("POSTGRES_DB", "openclaw_memory")
    auth = f"{quote(username)}:{quote(password)}"
    return urlunparse(("postgresql", f"{auth}@{host}:{port}", f"/{dbname}", "", "", ""))


def configure_readonly_env() -> None:
    reader_url = os.environ.get("OPENCLAW_MEMORY_READER_DATABASE_URL", "").strip()
    if not reader_url:
        reader_url = role_url("ocsm_home_reader", env_required("OCSM_READER_PASSWORD"))
    os.environ["OPENCLAW_MEMORY_DATABASE_URL"] = reader_url
    os.environ["OPENCLAW_MEMORY_READER_DATABASE_URL"] = reader_url
    os.environ["OPENCLAW_MEMORY_READABLE_PRIVACY_CLASSES"] = os.environ.get(
        "OPENCLAW_MEMORY_READABLE_PRIVACY_CLASSES",
        "project,shared_safe",
    )


def write_message(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
    sys.stdout.flush()


def result_text(payload: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False, default=str),
            }
        ],
        "structuredContent": payload,
    }


def error_result(message: str) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": (
                    "OpenClaw shared memory read is unavailable; use the existing "
                    f"markdown memory fallback. Error: {message}"
                ),
            }
        ],
        "isError": True,
    }


def require_identity(args: dict[str, Any]) -> None:
    if not str(args.get("caller", "")).strip():
        raise ValueError("caller is required for Phase 4 read-only gateway access")


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    require_identity(args)
    repo = MemoryRepository(Settings.from_env())
    if name == "search_memory":
        rows = repo.search_memory(
            str(args["query"]),
            args.get("scope"),
            str(args.get("status") or "shared"),
            int(args.get("limit") or 10),
        )
        return result_text({"ok": True, "records": rows, "count": len(rows)})
    if name == "get_with_audit":
        return result_text({"ok": True, **repo.get_with_audit(str(args["record_id"]))})
    if name == "list_candidates":
        rows = repo.list_candidates(args.get("scope"), int(args.get("limit") or 20))
        return result_text({"ok": True, "records": rows, "count": len(rows)})
    raise ValueError(f"Tool not found: {name}")


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if request_id is None:
        return None

    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {}},
                    "serverInfo": SERVER_INFO,
                },
            }
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": READONLY_TOOLS}}
        if method == "tools/call":
            params = message.get("params") or {}
            name = params.get("name")
            args = params.get("arguments") or {}
            try:
                result = call_tool(str(name), dict(args))
            except Exception as exc:
                result = error_result(f"{type(exc).__name__}: {exc}")
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": f"{type(exc).__name__}: {exc}"},
        }


def main() -> int:
    configure_readonly_env()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = handle_request(json.loads(line))
        if response is not None:
            write_message(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
