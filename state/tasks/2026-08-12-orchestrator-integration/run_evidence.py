#!/usr/bin/env python3
"""Append-only, hash-chained evidence stream for production-cycle runs."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0.0"
ALLOWED_EVENTS = {
    "start", "agent_launch", "changed_paths", "gate", "review", "terminal",
}
FORBIDDEN_KEY_PARTS = {
    "prompt", "secret", "token", "password", "authorization", "cookie", "api_key",
}


class EvidenceError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise EvidenceError("evidence payload is not JSON serializable") from exc


def _digest(value: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _validate_payload(value: Any, path: str = "payload") -> None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_payload(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise EvidenceError(f"{path} keys must be non-empty strings")
            normalized = key.lower().replace("-", "_")
            if any(part in normalized for part in FORBIDDEN_KEY_PARTS):
                raise EvidenceError(f"sensitive evidence key is forbidden: {key}")
            _validate_payload(item, f"{path}.{key}")
        return
    raise EvidenceError(f"unsupported evidence value at {path}")


def _parse_valid(raw: bytes) -> list[dict[str, Any]]:
    try:
        raw_lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise EvidenceError("evidence stream is not valid UTF-8") from exc
    if not raw_lines:
        raise EvidenceError("evidence stream is empty")
    events: list[dict[str, Any]] = []
    previous = None
    for index, line in enumerate(raw_lines, 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvidenceError("evidence stream contains malformed JSON") from exc
        required = {"document_type", "schema_version", "sequence", "timestamp", "event",
                    "payload", "previous_digest", "event_digest"}
        if not isinstance(event, dict) or set(event) != required:
            raise EvidenceError("evidence event fields are invalid")
        if (event["document_type"] != "orchestrator_run_evidence_event"
                or event["schema_version"] != SCHEMA_VERSION
                or event["sequence"] != index
                or event["event"] not in ALLOWED_EVENTS
                or event["previous_digest"] != previous):
            raise EvidenceError("evidence event contract is invalid")
        _validate_payload(event["payload"])
        unsigned = {key: value for key, value in event.items() if key != "event_digest"}
        if event["event_digest"] != _digest(unsigned):
            raise EvidenceError("evidence hash chain is invalid")
        if events and events[-1]["event"] == "terminal":
            raise EvidenceError("terminal evidence event is not last")
        previous = event["event_digest"]
        events.append(event)
    if events[0]["event"] != "start":
        raise EvidenceError("evidence stream must start with start event")
    return events


def _read_valid(path: Path) -> list[dict[str, Any]]:
    try:
        return _parse_valid(path.read_bytes())
    except OSError as exc:
        raise EvidenceError("cannot read evidence stream") from exc


class EvidenceStream:
    def __init__(self, path: Path, events: list[dict[str, Any]]):
        self.path = path
        self._sequence = len(events)
        self._previous_digest = events[-1]["event_digest"]
        self._sealed = events[-1]["event"] == "terminal"

    @classmethod
    def create(cls, path: Path, *, task_id: str, profile: str) -> "EvidenceStream":
        path = Path(path)
        if path.is_symlink():
            raise EvidenceError("evidence path must not be a symlink")
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except OSError as exc:
            raise EvidenceError("evidence stream already exists or cannot be created") from exc
        os.close(descriptor)
        stream = cls.__new__(cls)
        stream.path = path
        stream._sequence = 0
        stream._previous_digest = None
        stream._sealed = False
        stream.append("start", {"task_id": task_id, "profile": profile})
        return stream

    @classmethod
    def open(cls, path: Path) -> "EvidenceStream":
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            raise EvidenceError("evidence path must be a regular file")
        return cls(path, _read_valid(path))

    def append(self, event: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self._sealed:
            raise EvidenceError("evidence stream is sealed")
        if event not in ALLOWED_EVENTS or event == "start" and self._sequence:
            raise EvidenceError("evidence event type is invalid")
        if not isinstance(payload, dict):
            raise EvidenceError("evidence payload must be an object")
        _validate_payload(payload)
        record = {
            "document_type": "orchestrator_run_evidence_event",
            "schema_version": SCHEMA_VERSION,
            "sequence": self._sequence + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "event": event,
            "payload": payload,
            "previous_digest": self._previous_digest,
        }
        record["event_digest"] = _digest(record)
        encoded = _canonical(record) + b"\n"
        try:
            descriptor = os.open(self.path, os.O_RDWR | os.O_APPEND | os.O_NOFOLLOW)
            with os.fdopen(descriptor, "r+b", closefd=True) as handle:
                fcntl.flock(handle, fcntl.LOCK_EX)
                handle.seek(0)
                raw = handle.read()
                if self._sequence == 0:
                    if raw:
                        raise EvidenceError("new evidence stream is not empty")
                else:
                    current = _parse_valid(raw)
                    if (len(current) != self._sequence
                            or current[-1]["event_digest"] != self._previous_digest
                            or current[-1]["event"] == "terminal"):
                        raise EvidenceError("evidence stream changed outside the writer")
                handle.seek(0, os.SEEK_END)
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise EvidenceError("cannot append evidence event") from exc
        self._sequence += 1
        self._previous_digest = record["event_digest"]
        self._sealed = event == "terminal"
        return record
