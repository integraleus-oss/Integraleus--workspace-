#!/usr/bin/env python3
"""Foreground process supervisor with durable state, recovery and exactly-once outbox."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import uuid

TERMINAL = {"SUCCEEDED", "TIMED_OUT", "CRASHED", "ESCALATED", "INTERRUPTED", "FAILED"}
EVIDENCE_MAP = {
    "ACCEPTED": "SUCCEEDED", "SUCCESS": "SUCCEEDED", "SUCCEEDED": "SUCCEEDED",
    "ESCALATED": "ESCALATED", "TIMEOUT": "TIMED_OUT", "TIMED_OUT": "TIMED_OUT",
    "INTERRUPTED": "INTERRUPTED", "CRASHED": "CRASHED", "FAILED": "FAILED",
}


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


def atomic_json(path: Path, value: dict) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pid_alive(pid: int) -> bool:
    try: os.kill(pid, 0)
    except ProcessLookupError: return False
    except PermissionError: return True
    return True


def terminal_from_evidence(path: Path | None) -> str | None:
    if not path or not path.exists(): return None
    try: data = load_json(path)
    except (OSError, json.JSONDecodeError): return None
    raw = str(data.get("terminalStatus", data.get("status", data.get("outcome", "")))).upper()
    return EVIDENCE_MAP.get(raw)


def update_evidence(path: Path, state: dict) -> None:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else "# Execution Evidence\n\n"
    lines = text.splitlines()
    replaced = False
    for index, line in enumerate(lines):
        if line.lower().startswith("status:"):
            lines[index] = f"Status: {state['status']}"
            replaced = True; break
    if not replaced: lines.insert(1, f"Status: {state['status']}")
    marker = "## Execution Supervisor"
    if marker in lines: lines = lines[:lines.index(marker)]
    lines += ["", marker, "", f"- Run ID: `{state['runId']}`", f"- PID: `{state.get('pid')}`",
              f"- Status: `{state['status']}`", f"- Started: `{state['startedAt']}`",
              f"- Last verified: `{state['lastVerified']}`", f"- Finished: `{state.get('finishedAt')}`",
              f"- Exit code: `{state.get('exitCode')}`", f"- State file: `{state['statePath']}`",
              f"- Notification ID: `{state.get('notificationId')}`",
              f"- Notification delivered: `{state.get('notificationDelivered', False)}`", ""]
    atomic_text(path, "\n".join(lines))


def notify_once(state: dict, state_path: Path, outbox: Path) -> None:
    if state.get("notificationId"): return
    event_id = f"exec-{state['runId']}-{state['status'].lower()}"
    event = {"id": event_id, "runId": state["runId"], "status": state["status"],
             "evidence": state["evidencePath"], "finishedAt": state.get("finishedAt"),
             "delivery": {"status": "pending"}}
    outbox.parent.mkdir(parents=True, exist_ok=True)
    with outbox.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n"); handle.flush(); os.fsync(handle.fileno())
    state["notificationId"] = event_id
    state["notificationDelivered"] = False
    atomic_json(state_path, state)


def finalize(state: dict, state_path: Path, evidence: Path, outbox: Path, status: str, exit_code: int | None) -> int:
    if state.get("status") in TERMINAL: return int(state.get("exitCode") or 0)
    state.update(status=status, exitCode=exit_code, finishedAt=now_iso(), lastVerified=now_iso())
    atomic_json(state_path, state); notify_once(state, state_path, outbox); update_evidence(evidence, state)
    return 0 if status == "SUCCEEDED" else (124 if status == "TIMED_OUT" else 4)


def run(args: argparse.Namespace) -> int:
    if not args.command: raise SystemExit("command required after --")
    run_id = args.run_id or uuid.uuid4().hex
    state = {"schemaVersion": 1, "runId": run_id, "status": "RUNNING", "startedAt": now_iso(),
             "lastVerified": now_iso(), "finishedAt": None, "pid": None, "exitCode": None,
             "command": args.command, "timeoutSeconds": args.timeout,
             "evidencePath": str(args.evidence.resolve()), "statePath": str(args.state.resolve()),
             "terminalEvidencePath": str(args.terminal_evidence.resolve()) if args.terminal_evidence else None,
             "outboxPath": str(args.outbox.resolve()), "notificationId": None,
             "notificationDelivered": False, "owner": args.owner,
             "flowId": args.flow_id, "disablePath": "SIGINT or terminate foreground supervisor"}
    state["sessionKey"] = args.session_key
    state["deliveryContext"] = json.loads(args.delivery_json) if args.delivery_json else None
    process = subprocess.Popen(args.command, start_new_session=True)
    state["pid"] = process.pid; atomic_json(args.state, state); update_evidence(args.evidence, state)
    started = time.monotonic()
    try:
        while True:
            code = process.poll()
            state["lastVerified"] = now_iso(); atomic_json(args.state, state); update_evidence(args.evidence, state)
            observed = terminal_from_evidence(args.terminal_evidence)
            if code is not None:
                return finalize(state, args.state, args.evidence, args.outbox,
                                observed or ("SUCCEEDED" if code == 0 else "CRASHED"), code)
            if observed in TERMINAL:
                os.killpg(process.pid, signal.SIGTERM); process.wait(timeout=5)
                return finalize(state, args.state, args.evidence, args.outbox, observed, process.returncode)
            if time.monotonic() - started >= args.timeout:
                os.killpg(process.pid, signal.SIGTERM)
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: os.killpg(process.pid, signal.SIGKILL); process.wait()
                return finalize(state, args.state, args.evidence, args.outbox, "TIMED_OUT", process.returncode)
            time.sleep(args.poll)
    except KeyboardInterrupt:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(process.pid, signal.SIGKILL); process.wait()
        return finalize(state, args.state, args.evidence, args.outbox, "INTERRUPTED", process.returncode)


def recover(args: argparse.Namespace) -> int:
    state = load_json(args.state)
    evidence = Path(state["evidencePath"]); outbox = Path(state["outboxPath"])
    if state["status"] in TERMINAL:
        notify_once(state, args.state, outbox); update_evidence(evidence, state); return 0
    observed = terminal_from_evidence(Path(state["terminalEvidencePath"]) if state.get("terminalEvidencePath") else None)
    if observed: return finalize(state, args.state, evidence, outbox, observed, state.get("exitCode"))
    if pid_alive(int(state["pid"])):
        state["lastVerified"] = now_iso(); atomic_json(args.state, state); update_evidence(evidence, state)
        print(f"RUNNING {state['runId']} pid={state['pid']}"); return 0
    return finalize(state, args.state, evidence, outbox, "CRASHED", state.get("exitCode"))


def acknowledge(args: argparse.Namespace) -> int:
    state = load_json(args.state)
    if args.notification_id != state.get("notificationId"): return 3
    state["notificationDelivered"] = True; state["deliveredAt"] = now_iso()
    atomic_json(args.state, state); update_evidence(Path(state["evidencePath"]), state); return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(); sub = root.add_subparsers(dest="action", required=True)
    launch = sub.add_parser("run"); launch.set_defaults(func=run)
    launch.add_argument("--evidence", type=Path, required=True); launch.add_argument("--state", type=Path, required=True)
    launch.add_argument("--outbox", type=Path, required=True); launch.add_argument("--terminal-evidence", type=Path)
    launch.add_argument("--timeout", type=float, required=True); launch.add_argument("--poll", type=float, default=.25)
    launch.add_argument("--run-id"); launch.add_argument("--owner", required=True); launch.add_argument("--flow-id"); launch.add_argument("--session-key")
    launch.add_argument("--delivery-json")
    launch.add_argument("command", nargs=argparse.REMAINDER)
    recovery = sub.add_parser("recover"); recovery.set_defaults(func=recover); recovery.add_argument("--state", type=Path, required=True)
    ack_parser = sub.add_parser("ack"); ack_parser.set_defaults(func=acknowledge); ack_parser.add_argument("--state", type=Path, required=True); ack_parser.add_argument("--notification-id", required=True)
    return root


if __name__ == "__main__":
    parsed = parser().parse_args()
    if getattr(parsed, "command", None) and parsed.command[0] == "--": parsed.command = parsed.command[1:]
    raise SystemExit(parsed.func(parsed))
