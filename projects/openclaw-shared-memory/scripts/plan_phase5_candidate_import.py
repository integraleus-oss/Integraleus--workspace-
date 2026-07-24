#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path

from openclaw_shared_memory.models import MemoryDraft


PROTECTED_BASENAMES = {"MEMORY.md", "STATE.md", "DECISIONS.md"}
PROTECTED_PARTS = {"memory", "backups", "dist", ".venv", ".git"}
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-or-v1-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|token|password|secret|dsn)\s*[:=]\s*\S+"),
    re.compile(r"postgres(?:ql)?://[^@\s]+:[^@\s]+@"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan Phase 5 markdown-to-candidate records without DB writes"
    )
    parser.add_argument("--source", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--created-by", default="phase5-prep-planner")
    parser.add_argument("--source-label", default="phase5-dry-run")
    parser.add_argument("--reason", default="Phase 5 prep dry-run candidate planning")
    parser.add_argument(
        "--allow-protected-source",
        action="store_true",
        help="Allow protected real-memory paths. Do not use without later explicit owner approval.",
    )
    return parser


def refuse_protected_path(path: Path, allow_protected: bool) -> None:
    resolved = path.resolve()
    if allow_protected:
        return
    if resolved.name in PROTECTED_BASENAMES:
        raise PermissionError(f"protected real-memory source refused by default: {path}")
    if PROTECTED_PARTS.intersection(resolved.parts):
        if "docs" not in resolved.parts:
            raise PermissionError(f"protected source tree refused by default: {path}")


def assert_no_secret_like_text(path: Path, text: str) -> None:
    for pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            raise ValueError(f"secret-like content refused in {path}: {match.group(0)[:40]}")


def parse_candidate_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    body_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## TYPE:"):
            if current is not None:
                current["body"] = "\n".join(body_lines).strip()
                blocks.append(current)
            current = {"record_type": line.split(":", 1)[1].strip()}
            body_lines = []
            continue
        if current is None:
            continue
        if line.startswith("TITLE:"):
            current["title"] = line.split(":", 1)[1].strip()
        elif line.startswith("PRIVACY:"):
            current["privacy_class"] = line.split(":", 1)[1].strip()
        elif line.startswith("SCOPE:"):
            current["scope"] = line.split(":", 1)[1].strip()
        elif line.startswith("CONFIDENCE:"):
            current["confidence"] = line.split(":", 1)[1].strip()
        elif line.startswith("TAGS:"):
            current["tags"] = line.split(":", 1)[1].strip()
        elif line.strip():
            body_lines.append(line)
    if current is not None:
        current["body"] = "\n".join(body_lines).strip()
        blocks.append(current)
    return blocks


def build_drafts(path: Path, args: argparse.Namespace) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    assert_no_secret_like_text(path, text)
    checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
    planned: list[dict[str, object]] = []
    for index, block in enumerate(parse_candidate_blocks(text), start=1):
        tags = [tag.strip() for tag in block.get("tags", "").split(",") if tag.strip()]
        draft = MemoryDraft(
            record_type=block.get("record_type", ""),
            title=block.get("title", ""),
            body=block.get("body", ""),
            privacy_class=block.get("privacy_class", "personal_stanislav"),
            source=args.source_label,
            source_ref=f"{path}:{index}",
            created_by=args.created_by,
            scope=block.get("scope", "openclaw"),
            confidence=float(block.get("confidence", "0.7")),
            tags=["phase5-dry-run", *tags],
            metadata={
                "dry_run": True,
                "source_sha256": checksum,
                "reason": args.reason,
            },
        )
        draft.validate()
        planned.append(
            {
                "candidate": asdict(draft),
                "content_hash": draft.content_hash(),
                "would_write": False,
            }
        )
    if not planned:
        raise ValueError(f"no candidate blocks found in {path}")
    return planned


def main() -> int:
    args = build_parser().parse_args()
    all_candidates: list[dict[str, object]] = []
    for source in args.source:
        refuse_protected_path(source, args.allow_protected_source)
        all_candidates.extend(build_drafts(source, args))

    output = "\n".join(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in all_candidates)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    print(f"PHASE5_CANDIDATE_IMPORT_DRY_RUN_OK count={len(all_candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
