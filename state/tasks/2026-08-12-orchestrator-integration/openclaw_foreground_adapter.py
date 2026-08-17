#!/usr/bin/env python3
"""Deprecated fail-closed shim; guarded runs are launched only by the OS guard."""

from __future__ import annotations

import json


class AdapterError(RuntimeError):
    pass


def run_one(*_args, **_kwargs):
    raise AdapterError("user-space foreground adapter is disabled; use the root-owned orchestrator guard")


def main() -> int:
    result = {"status": "ERROR", "error": {"type": "AdapterError",
              "message": "user-space foreground adapter is disabled; use the root-owned orchestrator guard"}}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
