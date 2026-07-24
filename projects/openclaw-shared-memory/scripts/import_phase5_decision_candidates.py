#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from openclaw_shared_memory.config import Settings
from openclaw_shared_memory.models import MemoryDraft
from openclaw_shared_memory.repository import MemoryRepository


DECISION_RE = re.compile(
    r"---\n"
    r"### ID: (?P<id>[^\n]+)\n"
    r"TYPE: DECISION\n"
    r"STATUS: (?P<status>[^\n]+)\n"
    r"DATE: (?P<date>[^\n]+)\n"
    r"TITLE: (?P<title>[^\n]+)\n"
    r"CONTENT: (?P<content>.*?)\n"
    r"RATIONALE: (?P<rationale>.*?)(?=\n---\n|\Z)",
    re.DOTALL,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import a tiny approved subset of DECISIONS.md as candidate records"
    )
    parser.add_argument("--source", type=Path, default=Path("../../DECISIONS.md"))
    parser.add_argument("--max-count", type=int, default=3)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--privacy-class", default="project")
    parser.add_argument("--scope", default=Settings.from_env().default_scope)
    parser.add_argument("--created-by", default="openclaw-main")
    parser.add_argument("--source-label", default="DECISIONS.md")
    parser.add_argument(
        "--query",
        default="OpenClaw Shared Memory",
        help="Only decisions whose title or content contains this text are selected.",
    )
    return parser


def parse_decisions(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    return [match.groupdict() for match in DECISION_RE.finditer(text)]


def build_draft(item: dict[str, str], source_path: Path, args: argparse.Namespace) -> MemoryDraft:
    body = "\n".join(
        [
            f"Decision ID: {item['id']}",
            f"Date: {item['date']}",
            f"Status: {item['status']}",
            "",
            item["content"].strip(),
            "",
            f"Rationale: {item['rationale'].strip()}",
        ]
    )
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    draft = MemoryDraft(
        record_type="decision",
        title=item["title"].strip(),
        body=body,
        privacy_class=args.privacy_class,
        source=args.source_label,
        source_ref=f"{source_path}:{item['id']}",
        created_by=args.created_by,
        scope=args.scope,
        confidence=0.95,
        tags=[
            "phase5-tiny-import",
            "decisions-md",
            "openclaw-shared-memory",
            item["id"].lower(),
        ],
        metadata={
            "decision_id": item["id"],
            "decision_date": item["date"],
            "source_sha256": digest,
            "candidate_import_approval": (
                "approve Phase 5 tiny candidate import from DECISIONS.md "
                "shared-memory entries, max 3, candidates only"
            ),
        },
    )
    draft.validate()
    return draft


def select_decisions(items: list[dict[str, str]], query: str, max_count: int) -> list[dict[str, str]]:
    query_lower = query.lower()
    matches = [
        item
        for item in items
        if query_lower in item["title"].lower() or query_lower in item["content"].lower()
    ]
    return matches[-max_count:]


def serializable_row(row: dict[str, Any]) -> dict[str, Any]:
    clean = dict(row)
    for key, value in clean.items():
        if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
            clean[key] = str(value)
    return clean


def main() -> int:
    args = build_parser().parse_args()
    if args.max_count != 3:
        raise ValueError("this approved pilot is capped at exactly max-count 3")
    if args.privacy_class != "project":
        raise ValueError("this approved pilot uses privacy_class=project")

    source_path = args.source.resolve()
    selected = select_decisions(parse_decisions(source_path), args.query, args.max_count)
    if len(selected) != args.max_count:
        raise ValueError(f"expected exactly {args.max_count} selected decisions, got {len(selected)}")

    drafts = [build_draft(item, source_path, args) for item in selected]
    repo = MemoryRepository(Settings.from_env()) if args.apply else None
    results: list[dict[str, Any]] = []
    reason = "Approved Phase 5 tiny candidate import from DECISIONS.md, candidates only"

    for draft in drafts:
        if repo is None:
            results.append(
                {
                    "would_write": False,
                    "candidate": asdict(draft),
                    "content_hash": draft.content_hash(),
                }
            )
        else:
            row = repo.propose_memory(draft, reason)
            results.append(
                {
                    "would_write": True,
                    "id": str(row["id"]),
                    "status": row["status"],
                    "title": row["title"],
                    "privacy_class": row["privacy_class"],
                    "idempotent": bool(row.get("idempotent", False)),
                }
            )

    print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    mode = "APPLY" if args.apply else "DRY_RUN"
    print(f"PHASE5_DECISION_CANDIDATE_IMPORT_{mode}_OK count={len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
