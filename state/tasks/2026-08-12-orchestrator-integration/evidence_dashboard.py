#!/usr/bin/env python3
"""Generate a display-only static dashboard from digest-anchored evidence JSON."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any


class DashboardError(RuntimeError):
    pass


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _safe(value: Any) -> str:
    return html.escape(str(value), quote=True)


def generate_dashboard(evidence_path: Path, output_path: Path, expected_digest: str) -> None:
    evidence_path, output_path = evidence_path.resolve(), output_path.resolve()
    if not evidence_path.is_file() or evidence_path.is_symlink():
        raise DashboardError("evidence path is invalid")
    actual = file_digest(evidence_path)
    if actual != expected_digest:
        raise DashboardError("evidence digest mismatch")
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DashboardError("evidence JSON is invalid") from exc
    if not isinstance(evidence, dict):
        raise DashboardError("evidence root must be an object")
    requirements = evidence.get("requirements", [])
    tasks = evidence.get("tasks", [])
    tests = evidence.get("tests", [])
    findings = evidence.get("review_findings", [])
    artifacts = evidence.get("artifacts", [])
    if not all(isinstance(value, list) for value in (requirements, tasks, tests, findings, artifacts)):
        raise DashboardError("dashboard evidence collections are invalid")
    closed = sum(1 for item in requirements if isinstance(item, dict) and item.get("outcome") == "pass")
    rows = lambda values, keys: "".join(
        "<tr>" + "".join(f"<td>{_safe(item.get(key, ''))}</td>" for key in keys) + "</tr>"
        for item in values if isinstance(item, dict)
    )
    links = "".join(
        f'<li><a href="{_safe(item.get("path", "#"))}">{_safe(item.get("label", "artifact"))}</a></li>'
        for item in artifacts if isinstance(item, dict)
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Orchestrator evidence dashboard</title><style>
body{{font:15px system-ui;max-width:1100px;margin:32px auto;padding:0 18px;color:#17202a}}
.status{{padding:12px;border:2px solid #445;border-radius:8px}}table{{border-collapse:collapse;width:100%;margin:12px 0 24px}}
th,td{{border:1px solid #ccd;padding:7px;text-align:left}}code{{background:#eef;padding:2px 4px}}small{{color:#566}}
</style></head><body>
<h1>Orchestrator evidence dashboard</h1>
<p class="status"><strong>{_safe(evidence.get('stage', 'unknown'))}</strong> — {_safe(evidence.get('terminal_state', 'unknown'))}</p>
<p>Requirements: <strong>{closed}/{len(requirements)}</strong> · Attempts: {_safe(evidence.get('attempts', 0))} · Cycles: {_safe(evidence.get('cycles', 0))} · Duration: {_safe(evidence.get('duration_ms', 0))} ms</p>
<small>Display-only view. Evidence source: <code>{_safe(evidence_path)}</code><br>Verified digest: <code>{_safe(actual)}</code></small>
<h2>Requirements</h2><table><tr><th>ID</th><th>Outcome</th><th>Evidence</th></tr>{rows(requirements, ('requirement_id','outcome','evidence'))}</table>
<h2>Tasks</h2><table><tr><th>Task</th><th>Requirements</th><th>Status</th></tr>{rows(tasks, ('task_id','requirement_ids','status'))}</table>
<h2>Tests</h2><table><tr><th>Gate</th><th>Status</th><th>Details</th></tr>{rows(tests, ('gate_id','status','details'))}</table>
<h2>Review findings / stop reasons</h2><table><tr><th>ID</th><th>Severity</th><th>Status</th><th>Reason</th></tr>{rows(findings, ('finding_id','severity','status','reason'))}</table>
<h2>Artifacts</h2><ul>{links}</ul>
</body></html>"""
    if output_path.exists() or output_path.is_symlink():
        raise DashboardError("dashboard output must be new")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
