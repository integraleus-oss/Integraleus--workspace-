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
import fcntl
import hashlib
import ctypes
import base64
import binascii
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

TERMINAL = {"SUCCEEDED", "TIMED_OUT", "CRASHED", "ESCALATED", "INTERRUPTED", "FAILED", "BLOCKED"}
EVIDENCE_MAP = {
    "ACCEPTED": "SUCCEEDED", "SUCCESS": "SUCCEEDED", "SUCCEEDED": "SUCCEEDED",
    "ESCALATED": "ESCALATED", "TIMEOUT": "TIMED_OUT", "TIMED_OUT": "TIMED_OUT",
    "INTERRUPTED": "INTERRUPTED", "CRASHED": "CRASHED", "FAILED": "FAILED", "BLOCKED": "BLOCKED",
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


def pid_start_ticks(pid: int) -> int | None:
    try: return int(Path(f"/proc/{pid}/stat").read_text().split()[21])
    except (OSError, ValueError, IndexError): return None


def pid_alive(pid: int, expected_start_ticks: int | None = None) -> bool:
    try: os.kill(pid, 0)
    except ProcessLookupError: return False
    except PermissionError: return True
    return expected_start_ticks is None or pid_start_ticks(pid) == expected_start_ticks


def validate_recovery_state(state_path: Path, state: dict) -> None:
    root = state_path.resolve().parent
    expected = {
        "statePath": root / "execution-supervisor-state.json",
        "outboxPath": root / "outbox.jsonl",
        "terminalEvidencePath": root / "RESULT.json",
    }
    if state_path.resolve() != expected["statePath"]: raise ValueError("unexpected supervisor state filename")
    for key, path in expected.items():
        if key == "terminalEvidencePath" and not state.get(key): continue
        if Path(state.get(key, "")).resolve() != path: raise ValueError(f"unsafe {key}")
    evidence_path = Path(state.get("evidencePath", ""))
    if not evidence_path.is_absolute(): raise ValueError("unsafe evidencePath")


def managed_runner_alive(state: dict) -> bool:
    pid = int(state["pid"])
    if not state.get("pidStartTicks") or not pid_alive(pid, state["pidStartTicks"]): return False
    try: cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except OSError: return False
    command = state.get("command") or []
    expected_runner = str(Path(command[1]).resolve()) if len(command) > 1 else ""
    return bool(expected_runner) and expected_runner in cmdline and str(Path(state["statePath"]).parent / "RESULT.json") in cmdline


def verified_terminal(path: Path | None, terminal_public_key: str | None, expected_run_nonce: str | None = None) -> dict | None:
    if not path or not path.exists(): return None
    try: data = load_json(path)
    except (OSError, json.JSONDecodeError): return None
    if not terminal_public_key or not isinstance(data.get("terminalSignature"), str): return None
    status = str(data.get("terminalStatus", "")).upper()
    exit_code = data.get("exitCode")
    if status not in EVIDENCE_MAP or not isinstance(exit_code, int) or data.get("contractValidated") is not True: return None
    if not expected_run_nonce or data.get("runNonce") != expected_run_nonce: return None
    try:
        payload = json.dumps([status, True, exit_code, data.get("runNonce"), data.get("taskDigest"), data.get("planDigest"),
                              data.get("outcomeDigest"), data.get("finishedAt"), data.get("summary"), data.get("slices"),
                              data.get("outcomePath"), data.get("agentOutputPath"), data.get("independentReviewPaths")],
                             ensure_ascii=False, separators=(",", ":")).encode()
        key = serialization.load_der_public_key(base64.b64decode(terminal_public_key))
        if not isinstance(key, Ed25519PublicKey): return None
        key.verify(base64.b64decode(data["terminalSignature"]), payload)
    except (ValueError, TypeError, UnicodeEncodeError, binascii.Error, InvalidSignature): return None
    return data


def terminal_exit_code(path: Path | None, terminal_public_key: str | None, expected_run_nonce: str | None = None) -> int | None:
    data = verified_terminal(path, terminal_public_key, expected_run_nonce)
    return data.get("exitCode") if data else None


def terminal_from_evidence(path: Path | None, require_validated: bool = False, terminal_public_key: str | None = None,
                           expected_run_nonce: str | None = None) -> str | None:
    if not path or not path.exists(): return None
    if require_validated:
        data = verified_terminal(path, terminal_public_key, expected_run_nonce)
        if data is None: return None
    else:
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
    end_marker = "## /Execution Supervisor"
    suffix = []
    if marker in lines:
        start = lines.index(marker)
        if end_marker in lines[start + 1:]: suffix = lines[lines.index(end_marker, start + 1) + 1:]
        lines = lines[:start]
    while lines and not lines[-1].strip(): lines.pop()
    lines += ["", marker, "", f"- Run ID: `{state['runId']}`", f"- PID: `{state.get('pid')}`",
              f"- Status: `{state['status']}`", f"- Started: `{state['startedAt']}`",
              f"- Last verified: `{state['lastVerified']}`", f"- Finished: `{state.get('finishedAt')}`",
              f"- Exit code: `{state.get('exitCode')}`", f"- State file: `{state['statePath']}`",
              f"- Notification ID: `{state.get('notificationId')}`",
              f"- Notification delivered: `{state.get('notificationDelivered', False)}`", "", end_marker, ""] + suffix
    atomic_text(path, "\n".join(lines))


def notify_once(state: dict, state_path: Path, outbox: Path) -> None:
    if state.get("notificationId"): return
    event_id = f"exec-{state['runId']}-terminal-{state['status'].lower()}"
    event = {"id": event_id, "runId": state["runId"], "status": state["status"],
             "evidence": state["evidencePath"], "finishedAt": state.get("finishedAt"),
             "delivery": {"status": "pending"}}
    outbox.parent.mkdir(parents=True, exist_ok=True)
    if outbox.exists():
        for line in outbox.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                if json.loads(line).get("id") == event_id:
                    state["notificationId"] = event_id; state["notificationDelivered"] = False
                    atomic_json(state_path, state); return
            except json.JSONDecodeError: continue
    with outbox.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n"); handle.flush(); os.fsync(handle.fileno())
    state["notificationId"] = event_id
    state["notificationDelivered"] = False
    atomic_json(state_path, state)


def finalize(state: dict, state_path: Path, evidence: Path, outbox: Path, status: str, exit_code: int | None) -> int:
    lock_path = state_path.with_suffix(state_path.suffix + ".finalize.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            persisted = load_json(state_path)
            if persisted.get("status") in TERMINAL:
                immutable = persisted.get("status") != "SUCCEEDED" and bool(persisted.get("notificationId"))
                if persisted.get("status") == "SUCCEEDED":
                    proof = verified_terminal(Path(persisted["terminalEvidencePath"]), persisted.get("terminalPublicKey"), persisted.get("runNonce"))
                    immutable = proof is not None and proof.get("terminalStatus") == "SUCCEEDED" and proof.get("exitCode") == 0
                if immutable or (persisted.get("status") == status and persisted.get("exitCode") == exit_code):
                    notify_once(persisted, state_path, outbox); update_evidence(evidence, persisted)
                    return 0 if persisted["status"] == "SUCCEEDED" else (124 if persisted["status"] == "TIMED_OUT" else 4)
            state = persisted
        except (OSError, json.JSONDecodeError): pass
        state.update(status=status, exitCode=exit_code, finishedAt=now_iso(), lastVerified=now_iso())
        atomic_json(state_path, state); notify_once(state, state_path, outbox); update_evidence(evidence, state)
        return 0 if status == "SUCCEEDED" else (124 if status == "TIMED_OUT" else 4)


def run(args: argparse.Namespace) -> int:
    if not args.command: raise SystemExit("command required after --")
    ptrace_scope = Path("/proc/sys/kernel/yama/ptrace_scope")
    if ptrace_scope.exists() and int(ptrace_scope.read_text().strip()) < 1:
        raise SystemExit("managed execution requires kernel.yama.ptrace_scope >= 1")
    if args.terminal_evidence: args.terminal_evidence.unlink(missing_ok=True)
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
    state["requireValidatedTerminal"] = bool(args.terminal_evidence)
    state["runNonce"] = uuid.uuid4().hex if state["requireValidatedTerminal"] else None
    supplied_private_fd = os.environ.pop("MANAGED_SUPERVISOR_PRIVATE_FD", None)
    supplied_private_der = os.read(int(supplied_private_fd), 256) if supplied_private_fd else None
    if supplied_private_fd: os.close(int(supplied_private_fd))
    terminal_private_key = (serialization.load_der_private_key(supplied_private_der, None)
                            if supplied_private_der else Ed25519PrivateKey.generate()) if state["requireValidatedTerminal"] else None
    if terminal_private_key is not None and not isinstance(terminal_private_key, Ed25519PrivateKey):
        raise SystemExit("invalid managed terminal private key")
    private_der = terminal_private_key.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8,
                                                     serialization.NoEncryption()) if terminal_private_key else None
    public_der = terminal_private_key.public_key().public_bytes(serialization.Encoding.DER,
                                                                serialization.PublicFormat.SubjectPublicKeyInfo) if terminal_private_key else None
    terminal_public_key = base64.b64encode(public_der).decode() if public_der else None
    state["terminalKeyId"] = hashlib.sha256(public_der).hexdigest() if public_der else None
    state["terminalPublicKey"] = terminal_public_key
    state["deliveryContext"] = json.loads(args.delivery_json) if args.delivery_json else None
    previous_sigterm = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, lambda _signum, _frame: (_ for _ in ()).throw(KeyboardInterrupt()))
    ctypes.CDLL(None).prctl(4, 0, 0, 0, 0)  # PR_SET_DUMPABLE: protect supervisor memory from same-uid inspection.
    child_env = os.environ.copy(); child_env.pop("MANAGED_SUPERVISOR_PRIVATE_FD", None); read_fd = write_fd = None
    if private_der:
        read_fd, write_fd = os.pipe(); os.write(write_fd, private_der); os.close(write_fd)
        child_env["MANAGED_TERMINAL_FD"] = str(read_fd)
        child_env["MANAGED_RUN_NONCE"] = state["runNonce"]
    process = subprocess.Popen(args.command, start_new_session=True, env=child_env,
                               pass_fds=(read_fd,) if read_fd is not None else ())
    if read_fd is not None: os.close(read_fd)
    state["pid"] = process.pid
    state["pidStartTicks"] = pid_start_ticks(process.pid)
    atomic_json(args.state, state); update_evidence(args.evidence, state)
    started = time.monotonic()
    last_heartbeat = started
    try:
        while True:
            code = process.poll()
            if code is not None:
                observed = terminal_from_evidence(args.terminal_evidence, state["requireValidatedTerminal"], terminal_public_key, state.get("runNonce"))
                if observed == "SUCCEEDED" and code != 0: observed = "CRASHED"
                if observed: return finalize(state, args.state, args.evidence, args.outbox, observed, code)
                return finalize(state, args.state, args.evidence, args.outbox, "FAILED" if code == 0 else "CRASHED", code)
            if time.monotonic() - last_heartbeat >= 5:
                lock_path = args.state.with_suffix(args.state.suffix + ".finalize.lock")
                corrupt_state = False
                with lock_path.open("a+") as lock:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                    try: persisted = load_json(args.state)
                    except (OSError, json.JSONDecodeError):
                        os.killpg(process.pid, signal.SIGKILL); process.wait()
                        corrupt_state = True
                    if not corrupt_state:
                        wall_elapsed = (dt.datetime.now().astimezone() - dt.datetime.fromisoformat(state["startedAt"])).total_seconds()
                        if persisted.get("status") == "TIMED_OUT" and wall_elapsed >= args.timeout:
                            try: process.wait(timeout=5)
                            except subprocess.TimeoutExpired: os.killpg(process.pid, signal.SIGKILL); process.wait()
                            return 124
                        # Merge heartbeat-only fields into the latest persisted state so
                        # delivery acknowledgement and other concurrent bookkeeping survive.
                        persisted["status"] = "RUNNING"; persisted["lastVerified"] = now_iso()
                        state = persisted
                        atomic_json(args.state, state)
                if corrupt_state:
                    return finalize(state, args.state, args.evidence, args.outbox, "FAILED", process.returncode)
                last_heartbeat = time.monotonic()
            if time.monotonic() - started >= args.timeout:
                # A short post-deadline grace closes the result-write/exit race without
                # reading terminal evidence from a still-running process.
                try: process.wait(timeout=.25)
                except subprocess.TimeoutExpired: pass
                if process.poll() is not None:
                    observed = terminal_from_evidence(args.terminal_evidence, state["requireValidatedTerminal"], terminal_public_key, state.get("runNonce"))
                    if observed == "SUCCEEDED" and process.returncode != 0: observed = "CRASHED"
                    return finalize(state, args.state, args.evidence, args.outbox, observed or "CRASHED", process.returncode)
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
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)


def recover(args: argparse.Namespace) -> int:
    state = load_json(args.state)
    validate_recovery_state(args.state, state)
    recovery_public_key = None
    if args.terminal_public_key:
        try:
            public_der = base64.b64decode(args.terminal_public_key)
            if hashlib.sha256(public_der).hexdigest() == state.get("terminalKeyId"):
                recovery_public_key = args.terminal_public_key
        except (ValueError, TypeError): pass
    evidence = Path(state["evidencePath"]); outbox = Path(state["outboxPath"])
    # Never inspect model-produced terminal evidence while the exact managed
    # runner process is still alive. A persisted terminal-looking state cannot
    # shorten this liveness check.
    if managed_runner_alive(state):
        started = dt.datetime.fromisoformat(state["startedAt"])
        if (dt.datetime.now().astimezone() - started).total_seconds() >= float(state.get("timeoutSeconds", 0)):
            try: os.killpg(int(state["pid"]), signal.SIGTERM)
            except ProcessLookupError: pass
            deadline = time.monotonic() + 5
            while managed_runner_alive(state) and time.monotonic() < deadline: time.sleep(.05)
            if managed_runner_alive(state):
                try: os.killpg(int(state["pid"]), signal.SIGKILL)
                except ProcessLookupError: pass
                deadline = time.monotonic() + 5
                while managed_runner_alive(state) and time.monotonic() < deadline: time.sleep(.05)
            if managed_runner_alive(state): raise RuntimeError("timed-out managed runner could not be terminated")
            finalize(state, args.state, evidence, outbox, "TIMED_OUT", state.get("exitCode")); return 0
        with args.state.with_suffix(args.state.suffix + ".finalize.lock").open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX); state = load_json(args.state)
            state["lastVerified"] = now_iso(); atomic_json(args.state, state); update_evidence(evidence, state)
        print(f"RUNNING {state['runId']} pid={state['pid']}"); return 0
    if state["status"] in TERMINAL:
        with args.state.with_suffix(args.state.suffix + ".finalize.lock").open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX); state = load_json(args.state)
            if state.get("status") == "SUCCEEDED":
                requires_validation = bool(state.get("requireValidatedTerminal"))
                observed = terminal_from_evidence(Path(state["terminalEvidencePath"]) if state.get("terminalEvidencePath") else None,
                                                  requires_validation, recovery_public_key, state.get("runNonce"))
                recovered_exit = terminal_exit_code(Path(state["terminalEvidencePath"]), recovery_public_key, state.get("runNonce")) if requires_validation else state.get("exitCode")
                if state.get("notificationDelivered") and (not requires_validation or (observed == "SUCCEEDED" and recovered_exit == 0)):
                    update_evidence(evidence, state); return 0
                if observed == "SUCCEEDED" and recovered_exit == 0:
                    notify_once(state, args.state, outbox); update_evidence(evidence, state); return 0
                state.update(status="RUNNING", notificationId=None, notificationDelivered=False)
                atomic_json(args.state, state)
            else:
                observed = terminal_from_evidence(Path(state["terminalEvidencePath"]) if state.get("terminalEvidencePath") else None,
                                                  bool(state.get("requireValidatedTerminal")), recovery_public_key, state.get("runNonce"))
                if not state.get("requireValidatedTerminal") or observed == state.get("status"):
                    notify_once(state, args.state, outbox); update_evidence(evidence, state); return 0
                state.update(status="RUNNING", notificationId=None, notificationDelivered=False)
                atomic_json(args.state, state)
    observed = terminal_from_evidence(Path(state["terminalEvidencePath"]) if state.get("terminalEvidencePath") else None,
                                      bool(state.get("requireValidatedTerminal")), recovery_public_key, state.get("runNonce"))
    recovered_exit = terminal_exit_code(Path(state["terminalEvidencePath"]) if state.get("terminalEvidencePath") else None,
                                        recovery_public_key, state.get("runNonce"))
    if observed == "SUCCEEDED" and recovered_exit != 0: observed = "CRASHED"
    if recovered_exit is not None: state["exitCode"] = recovered_exit
    finalize(state, args.state, evidence, outbox, observed or "CRASHED", state.get("exitCode")); return 0


def acknowledge(args: argparse.Namespace) -> int:
    with args.state.with_suffix(args.state.suffix + ".finalize.lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX); state = load_json(args.state)
        if args.notification_id != state.get("notificationId"): return 3
        if state.get("deliveryClaimId") and args.claim_id != state.get("deliveryClaimId"): return 3
        state["notificationDelivered"] = True; state["deliveredAt"] = now_iso()
        state["deliveryClaimId"] = None; state["deliveryClaimedAt"] = None
        atomic_json(args.state, state); update_evidence(Path(state["evidencePath"]), state); return 0


def claim_delivery(args: argparse.Namespace) -> int:
    with args.state.with_suffix(args.state.suffix + ".finalize.lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX); state = load_json(args.state)
        if args.notification_id != state.get("notificationId") or state.get("notificationDelivered"): return 3
        claimed_at = state.get("deliveryClaimedAt")
        if claimed_at and (dt.datetime.now().astimezone() - dt.datetime.fromisoformat(claimed_at)).total_seconds() < 60: return 3
        claim_id = uuid.uuid4().hex
        state["deliveryClaimId"] = claim_id; state["deliveryClaimedAt"] = now_iso()
        atomic_json(args.state, state); print(claim_id); return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(); sub = root.add_subparsers(dest="action", required=True)
    launch = sub.add_parser("run"); launch.set_defaults(func=run)
    launch.add_argument("--evidence", type=Path, required=True); launch.add_argument("--state", type=Path, required=True)
    launch.add_argument("--outbox", type=Path, required=True); launch.add_argument("--terminal-evidence", type=Path)
    launch.add_argument("--timeout", type=float, required=True); launch.add_argument("--poll", type=float, default=.25)
    launch.add_argument("--run-id"); launch.add_argument("--owner", required=True); launch.add_argument("--flow-id"); launch.add_argument("--session-key")
    launch.add_argument("--require-validated-terminal", action="store_true")
    launch.add_argument("--delivery-json")
    launch.add_argument("command", nargs=argparse.REMAINDER)
    recovery = sub.add_parser("recover"); recovery.set_defaults(func=recover); recovery.add_argument("--state", type=Path, required=True)
    recovery.add_argument("--terminal-public-key")
    ack_parser = sub.add_parser("ack"); ack_parser.set_defaults(func=acknowledge); ack_parser.add_argument("--state", type=Path, required=True); ack_parser.add_argument("--notification-id", required=True)
    ack_parser.add_argument("--claim-id")
    claim_parser = sub.add_parser("claim-delivery"); claim_parser.set_defaults(func=claim_delivery); claim_parser.add_argument("--state", type=Path, required=True); claim_parser.add_argument("--notification-id", required=True)
    return root


if __name__ == "__main__":
    parsed = parser().parse_args()
    if getattr(parsed, "command", None) and parsed.command[0] == "--": parsed.command = parsed.command[1:]
    raise SystemExit(parsed.func(parsed))
