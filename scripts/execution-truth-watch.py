#!/usr/bin/env python3
"""Read-only audit for unsupported RUNNING evidence records."""

from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
import re

STATUS_RE = re.compile(r"^Status:\s*`?([A-Za-z_-]+)`?\s*$", re.MULTILINE | re.IGNORECASE)
PID_RE = re.compile(r"^(?:Process )?PID:\s*(\d+)\s*$", re.MULTILINE | re.IGNORECASE)
VERIFIED_RE = re.compile(r"^(?:-\s*)?Last verified:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, ValueError):
        return False
    except PermissionError:
        return True
    return True


def parse_time(value: str) -> dt.datetime | None:
    value = value.removesuffix(" MSK").strip()
    try:
        return dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def audit_file(path: Path, now: dt.datetime, stale_minutes: int) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    status = STATUS_RE.search(text)
    if not status or status.group(1).upper() != "RUNNING":
        return []

    failures: list[str] = []
    if not (path.parent / "TASK_PACKET.md").exists() and "Task packet:" not in text:
        failures.append("missing task artifact")

    pid_match = PID_RE.search(text)
    managed = re.search(r"^(?:-\s*)?Managed (?:mechanism|job):\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    if pid_match:
        if not pid_alive(int(pid_match.group(1))):
            failures.append("dead PID")
    elif not managed:
        failures.append("missing process/managed-job identity")

    verified = VERIFIED_RE.search(text)
    verified_at = parse_time(verified.group(1)) if verified else None
    if verified_at is None:
        failures.append("missing/invalid Last verified")
    elif now - verified_at > dt.timedelta(minutes=stale_minutes):
        failures.append("stale evidence")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--stale-minutes", type=int, default=60)
    parser.add_argument("--now", type=dt.datetime.fromisoformat, default=dt.datetime.now())
    args = parser.parse_args()

    findings = []
    for path in sorted(args.root.rglob("EVIDENCE.md")):
        failures = audit_file(path, args.now, args.stale_minutes)
        if failures:
            findings.append(f"{path}: STALE: {', '.join(failures)}")
    if findings:
        print("\n".join(findings))
        return 2
    print("EXECUTION_TRUTH_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
