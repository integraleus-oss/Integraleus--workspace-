#!/usr/bin/env python3
"""Root-owned local authorization guard for one controlled orchestrator run."""

from __future__ import annotations

import hashlib
import json
import os
import pwd
import socket
import struct
import subprocess
import time
from pathlib import Path

SOCKET_PATH = Path("/run/orchestrator-guard/guard.sock")
PACKET_ROOT = Path("/home/stanislav/.openclaw/workspace/agents/main/state/tasks")
RUNNER = Path("/opt/orchestrator-guard/runtime/production_cycle_cli.py")
AUDIT = Path("/var/log/orchestrator-guard/audit.jsonl")
OWNER_ID = "109592643"
CHAT_ID = "-1004417478336"
TOPIC_ID = "2922"
MAX_AGE_SECONDS = 120
MAX_REQUEST = 65536


class GuardError(RuntimeError):
    pass


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _gateway_peer(conn: socket.socket) -> int:
    pid, uid, _gid = struct.unpack("3i", conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
    if uid != pwd.getpwnam("stanislav").pw_uid:
        raise GuardError("peer uid is not the OpenClaw owner")
    cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    cgroup = Path(f"/proc/{pid}/cgroup").read_text(errors="replace")
    exe = Path(f"/proc/{pid}/exe").resolve()
    if (exe != Path("/usr/bin/node").resolve()
            or "/usr/lib/node_modules/openclaw/dist/index.js gateway --port 18789" not in cmdline
            or "openclaw-gateway.service" not in cgroup):
        raise GuardError("peer process is not the active OpenClaw Gateway")
    return pid


def _packet(value: str, expected_digest: str) -> Path:
    requested = Path(value)
    if requested.is_symlink() or not requested.is_file():
        raise GuardError("packet must be a regular non-symlink file")
    canonical = requested.resolve(strict=True)
    root = PACKET_ROOT.resolve(strict=True)
    if not canonical.is_relative_to(root):
        raise GuardError("packet is outside approved root")
    if _digest(canonical) != expected_digest:
        raise GuardError("packet digest mismatch")
    return canonical


def _validate(request: dict, now: int) -> Path:
    required = {"action", "accountId", "channelId", "chatId", "topicId", "messageId",
                "senderId", "timestamp", "packetPath", "packetDigest"}
    if set(request) != required or request.get("action") != "run_one":
        raise GuardError("request shape is invalid")
    if (request["accountId"] != "default" or request["channelId"] != "telegram"
            or request["chatId"] != CHAT_ID or request["topicId"] != TOPIC_ID
            or request["senderId"] != OWNER_ID):
        raise GuardError("trusted inbound metadata mismatch")
    if not str(request["messageId"]).isdigit():
        raise GuardError("message id is invalid")
    timestamp = int(request["timestamp"])
    if timestamp > now + 5 or now - timestamp > MAX_AGE_SECONDS:
        raise GuardError("owner message is not fresh")
    return _packet(str(request["packetPath"]), str(request["packetDigest"]))


def _audit(record: dict) -> None:
    AUDIT.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    os.chmod(AUDIT, 0o640)


def _run(packet: Path) -> dict:
    user = pwd.getpwnam("stanislav")
    def demote() -> None:
        os.setgroups([])
        os.setgid(user.pw_gid)
        os.setuid(user.pw_uid)
    completed = subprocess.run(
        ["/usr/bin/python3", str(RUNNER), str(packet), "--guard-authorized"],
        cwd=str(RUNNER.parent), capture_output=True, text=True, timeout=1800,
        preexec_fn=demote, env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": user.pw_dir},
    )
    terminal = completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else ""
    try:
        result = json.loads(terminal)
    except json.JSONDecodeError as exc:
        raise GuardError("runner did not produce structured terminal evidence") from exc
    if completed.returncode not in {0, 4, 130}:
        raise GuardError(f"runner failed with exit {completed.returncode}")
    return result


def handle(conn: socket.socket) -> dict:
    gateway_pid = _gateway_peer(conn)
    raw = conn.recv(MAX_REQUEST + 1)
    if len(raw) > MAX_REQUEST or not raw.endswith(b"\n"):
        raise GuardError("request framing is invalid")
    request = json.loads(raw)
    now = int(time.time())
    packet = _validate(request, now)
    identity = f'{request["chatId"]}:{request["topicId"]}:{request["messageId"]}'
    used = Path("/var/lib/orchestrator-guard/used") / hashlib.sha256(identity.encode()).hexdigest()
    used.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        fd = os.open(used, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    except FileExistsError as exc:
        raise GuardError("owner message was already consumed") from exc
    _audit({"event": "admitted", "at": now, "gatewayPid": gateway_pid, "messageId": request["messageId"],
            "packetDigest": request["packetDigest"]})
    result = _run(packet)
    _audit({"event": "terminal", "at": int(time.time()), "messageId": request["messageId"],
            "packetDigest": request["packetDigest"], "status": result.get("status")})
    return {"ok": True, "result": result, "messageId": request["messageId"], "packetDigest": request["packetDigest"]}


def main() -> int:
    listener = socket.fromfd(3, socket.AF_UNIX, socket.SOCK_STREAM)
    while True:
        conn, _ = listener.accept()
        with conn:
            try:
                response = handle(conn)
            except Exception as exc:
                response = {"ok": False, "error": type(exc).__name__, "message": str(exc)}
                _audit({"event": "rejected", "at": int(time.time()), "error": type(exc).__name__, "message": str(exc)})
            conn.sendall(json.dumps(response, sort_keys=True, separators=(",", ":")).encode() + b"\n")


if __name__ == "__main__":
    raise SystemExit(main())
