#!/usr/bin/env python3
"""Heartbeat fallback: recover durable supervisors and expose pending alerts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

SUPERVISOR = Path(__file__).with_name("execution-supervisor.py")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    failures = 0; pending = []
    for state_path in sorted(args.root.rglob("execution-supervisor-state.json")):
        result = subprocess.run([sys.executable, str(SUPERVISOR), "recover", "--state", str(state_path)],
                                capture_output=True, text=True)
        if result.returncode != 0:
            failures += 1; print(f"RECOVERY_FAILED {state_path}: {result.stderr.strip()}")
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("notificationId") and not state.get("notificationDelivered"):
            pending.append({"statePath": str(state_path), "notificationId": state["notificationId"],
                            "status": state["status"], "evidencePath": state["evidencePath"],
                            "flowId": state.get("flowId"), "sessionKey": state.get("sessionKey"),
                            "deliveryContext": state.get("deliveryContext")})
    for item in pending: print("PENDING_NOTIFICATION " + json.dumps(item, ensure_ascii=False))
    if not failures and not pending: print("SUPERVISOR_RECOVERY_OK")
    return 2 if failures else (1 if pending else 0)


if __name__ == "__main__": raise SystemExit(main())
