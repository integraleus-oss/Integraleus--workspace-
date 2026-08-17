#!/usr/bin/env python3
"""Root-owned two-phase authorization guard for one controlled orchestrator run."""

from __future__ import annotations

import hashlib
import json
import os
import pwd
import secrets
import signal
import socket
import stat
import struct
import subprocess
import tempfile
import time
from pathlib import Path

PACKET_ROOT = Path("/home/stanislav/.openclaw/workspace/agents/main/state/tasks")
RUNNER = Path("/opt/orchestrator-guard/runtime/production_cycle_cli.py")
AUDIT = Path("/var/log/orchestrator-guard/audit.jsonl")
SNAPSHOT_ROOT = Path("/run/orchestrator-guard/snapshots")
USED_ROOT = Path("/var/lib/orchestrator-guard/used")
OWNER_ID, CHAT_ID, TOPIC_ID = "109592643", "-1004417478336", "2922"
MAX_AGE_SECONDS, SNAPSHOT_TTL_SECONDS = 120, 1800
MAX_REQUEST, MAX_ENTRIES, MAX_BYTES, MAX_DEPTH = 65536, 64, 4 * 1024 * 1024, 6
prepared: dict[str, dict] = {}


class GuardError(RuntimeError):
    pass


def _snapshot_owner(path: Path) -> None:
    if os.geteuid() == 0:
        os.chown(path, 0, pwd.getpwnam("stanislav").pw_gid)


def _digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _digest(path: Path) -> str:
    return _digest_bytes(path.read_bytes())


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


def _metadata(request: dict, now: int) -> None:
    if (request.get("accountId") != "default" or request.get("channelId") != "telegram"
            or request.get("chatId") != CHAT_ID or request.get("topicId") != TOPIC_ID
            or request.get("senderId") != OWNER_ID
            or not str(request.get("messageId", "")).isascii()
            or not str(request.get("messageId", "")).isdigit()):
        raise GuardError("trusted inbound metadata mismatch")
    try:
        timestamp = int(request["timestamp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise GuardError("message timestamp is invalid") from exc
    if timestamp > now + 5 or now - timestamp > MAX_AGE_SECONDS:
        raise GuardError("owner message is not fresh")


def _consume_message(request: dict) -> None:
    identity = f'{request["chatId"]}:{request["topicId"]}:{request["messageId"]}:{request["action"]}'
    USED_ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    marker = USED_ROOT / hashlib.sha256(identity.encode()).hexdigest()
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    except FileExistsError as exc:
        raise GuardError("owner message was already consumed") from exc


def _open_packet_dir(packet_value: str, expected_digest: str) -> tuple[int, str]:
    requested = Path(packet_value)
    try:
        relative = requested.relative_to(PACKET_ROOT)
    except ValueError as exc:
        raise GuardError("packet is outside approved root") from exc
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise GuardError("packet path is invalid")
    directory_fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in PACKET_ROOT.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child
        for part in relative.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child
        packet_name = relative.parts[-1]
        packet_fd = os.open(packet_name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
        try:
            info = os.fstat(packet_fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
                raise GuardError("packet is not a bounded regular file")
            data = os.read(packet_fd, info.st_size + 1)
            if len(data) != info.st_size or _digest_bytes(data) != expected_digest:
                raise GuardError("packet digest mismatch")
        finally:
            os.close(packet_fd)
        return directory_fd, packet_name
    except Exception:
        os.close(directory_fd)
        raise


def _copy_tree(src_fd: int, target: Path, rel: str = "", depth: int = 0,
               budget: dict | None = None) -> list[tuple[str, str]]:
    if depth > MAX_DEPTH:
        raise GuardError("snapshot directory depth exceeds limit")
    budget = budget if budget is not None else {"entries": 0, "bytes": 0}
    target.mkdir(mode=0o750, parents=True, exist_ok=False if depth == 0 else True)
    _snapshot_owner(target)
    manifest: list[tuple[str, str]] = []
    names = sorted(os.listdir(src_fd))
    if len(names) > MAX_ENTRIES:
        raise GuardError("snapshot directory entry count exceeds limit")
    for name in names:
        if name in {"__pycache__", ".git"}:
            continue
        info = os.stat(name, dir_fd=src_fd, follow_symlinks=False)
        child_rel = f"{rel}/{name}" if rel else name
        destination = target / name
        budget["entries"] += 1
        if budget["entries"] > MAX_ENTRIES:
            raise GuardError("snapshot total entry count exceeds limit")
        if stat.S_ISDIR(info.st_mode):
            child_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=src_fd)
            try:
                manifest.extend(_copy_tree(child_fd, destination, child_rel, depth + 1, budget))
            finally:
                os.close(child_fd)
        elif stat.S_ISREG(info.st_mode):
            budget["bytes"] += info.st_size
            if budget["bytes"] > MAX_BYTES:
                raise GuardError("snapshot exceeds file or byte limit")
            if info.st_uid != pwd.getpwnam("stanislav").pw_uid or info.st_nlink != 1:
                raise GuardError("snapshot file ownership or link count is unsafe")
            source = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=src_fd)
            try:
                current = os.fstat(source)
                if current.st_ino != info.st_ino or current.st_dev != info.st_dev:
                    raise GuardError("snapshot source changed during open")
                data = b""
                while len(data) <= info.st_size:
                    chunk = os.read(source, min(65536, info.st_size + 1 - len(data)))
                    if not chunk:
                        break
                    data += chunk
                if len(data) != info.st_size:
                    raise GuardError("snapshot source changed during read")
            finally:
                os.close(source)
            fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o640)
            try:
                os.write(fd, data)
            finally:
                os.close(fd)
            _snapshot_owner(destination)
            manifest.append((child_rel, _digest_bytes(data)))
        else:
            raise GuardError("snapshot contains a non-regular entry")
    return manifest


def _prepare(request: dict, now: int) -> dict:
    required = {"action", "accountId", "channelId", "chatId", "topicId", "messageId",
                "senderId", "timestamp", "content", "packetPath", "packetDigest"}
    if set(request) != required or request["action"] != "prepare":
        raise GuardError("prepare request is invalid")
    _metadata(request, now)
    relative = Path(str(request["packetPath"])).relative_to(PACKET_ROOT).as_posix()
    expected_command = f'PREPARE ORCHESTRATOR PILOT {request["packetDigest"]} {relative}'
    if request["content"].strip() != expected_command:
        raise GuardError("prepare command is not bound to packet path and digest")
    _consume_message(request)
    source_fd, packet_name = _open_packet_dir(str(request["packetPath"]), str(request["packetDigest"]))
    snapshot_id = secrets.token_hex(16)
    target = SNAPSHOT_ROOT / snapshot_id
    try:
        manifest = _copy_tree(source_fd, target)
    finally:
        os.close(source_fd)
    tree = json.dumps(manifest, separators=(",", ":"), ensure_ascii=False).encode()
    snapshot_digest = _digest_bytes(tree)
    staged_packet = target / packet_name
    if _digest(staged_packet) != request["packetDigest"]:
        raise GuardError("staged packet digest mismatch")
    prepared[snapshot_id] = {"packet": staged_packet, "digest": snapshot_digest, "created": now}
    return {"ok": True, "phase": "PREPARED", "snapshotId": snapshot_id,
            "snapshotDigest": snapshot_digest, "runCommand": f"RUN ORCHESTRATOR PILOT {snapshot_digest}"}


def _run_child(packet: Path) -> dict:
    user = pwd.getpwnam("stanislav")
    def demote() -> None:
        os.setgroups([])
        os.setgid(user.pw_gid)
        os.setuid(user.pw_uid)
    with tempfile.TemporaryFile(mode="w+t") as stdout_file, tempfile.TemporaryFile(mode="w+t") as stderr_file:
        process = subprocess.Popen(
            ["/usr/bin/python3", str(RUNNER), str(packet), "--guard-authorized"], cwd=str(RUNNER.parent),
            stdout=stdout_file, stderr=stderr_file, text=True, preexec_fn=demote, start_new_session=True,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": user.pw_dir,
                 "USER": user.pw_name, "LOGNAME": user.pw_name})
        timed_out = False
        try:
            process.wait(timeout=1800)
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=10)
            raise GuardError("runner timed out and its process group was terminated") from exc
        finally:
            if not timed_out:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    time.sleep(0.2)
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        stdout_file.seek(0)
        stdout = stdout_file.read(1_048_577)
        if len(stdout) > 1_048_576:
            raise GuardError("runner stdout exceeded capture limit")
    terminal = stdout.strip().splitlines()[-1] if stdout.strip() else ""
    try:
        result = json.loads(terminal)
    except json.JSONDecodeError as exc:
        raise GuardError("runner did not produce structured terminal evidence") from exc
    if process.returncode not in {0, 3, 4, 130}:
        raise GuardError(f"runner failed with exit {process.returncode}")
    return result


def _run_prepared(request: dict, now: int) -> dict:
    required = {"action", "accountId", "channelId", "chatId", "topicId", "messageId",
                "senderId", "timestamp", "content", "snapshotId"}
    if set(request) != required or request["action"] != "run":
        raise GuardError("run request is invalid")
    _metadata(request, now)
    record = prepared.get(str(request["snapshotId"]))
    if not record or now - record["created"] > SNAPSHOT_TTL_SECONDS:
        raise GuardError("prepared snapshot is missing or expired")
    if request["content"].strip() != f'RUN ORCHESTRATOR PILOT {record["digest"]}':
        raise GuardError("run command is not bound to the prepared snapshot")
    _consume_message(request)
    del prepared[str(request["snapshotId"])]
    _audit({"event": "ADMITTED", "at": now, "messageId": request["messageId"],
            "snapshotDigest": record["digest"]})
    try:
        result = _run_child(record["packet"])
    except Exception as exc:
        _audit({"event": "FAILED", "at": int(time.time()), "messageId": request["messageId"],
                "snapshotDigest": record["digest"], "error": type(exc).__name__})
        raise
    return {"ok": True, "phase": "TERMINAL", "snapshotDigest": record["digest"], "result": result}


def _audit(record: dict) -> None:
    AUDIT.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    os.chmod(AUDIT, 0o640)


def _read_request(conn: socket.socket) -> dict:
    conn.settimeout(5); chunks = []; size = 0
    while True:
        chunk = conn.recv(min(4096, MAX_REQUEST + 1 - size))
        if not chunk: break
        chunks.append(chunk); size += len(chunk)
        if size > MAX_REQUEST or b"\n" in chunk: break
    raw = b"".join(chunks)
    if len(raw) > MAX_REQUEST or raw.count(b"\n") != 1 or not raw.endswith(b"\n"):
        raise GuardError("request framing is invalid")
    value = json.loads(raw)
    if not isinstance(value, dict): raise GuardError("request must be an object")
    return value


def handle(conn: socket.socket) -> dict:
    gateway_pid = _gateway_peer(conn); request = _read_request(conn); now = int(time.time())
    response = _prepare(request, now) if request.get("action") == "prepare" else _run_prepared(request, now)
    _audit({"event": response["phase"], "at": now, "gatewayPid": gateway_pid,
            "messageId": request["messageId"], "snapshotDigest": response["snapshotDigest"]})
    return response


def main() -> int:
    if os.environ.get("LISTEN_PID") != str(os.getpid()) or os.environ.get("LISTEN_FDS") != "1":
        raise SystemExit("guard requires exactly one systemd-activated socket")
    os.umask(0o027)
    SNAPSHOT_ROOT.mkdir(mode=0o750, parents=True, exist_ok=True)
    os.chmod(SNAPSHOT_ROOT, 0o750)
    _snapshot_owner(SNAPSHOT_ROOT)
    listener = socket.fromfd(3, socket.AF_UNIX, socket.SOCK_STREAM)
    while True:
        conn, _ = listener.accept()
        with conn:
            try:
                response = handle(conn)
            except Exception as exc:
                response = {"ok": False, "error": type(exc).__name__, "message": str(exc)}
                try:
                    _audit({"event": "REJECTED", "at": int(time.time()), "error": type(exc).__name__})
                except Exception: pass
            try: conn.sendall(json.dumps(response, sort_keys=True, separators=(",", ":")).encode() + b"\n")
            except OSError: pass


if __name__ == "__main__":
    raise SystemExit(main())
