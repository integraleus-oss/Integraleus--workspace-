#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from openclaw_shared_memory.config import Settings
from openclaw_shared_memory.models import MemoryDraft


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import markdown files as candidate memory records")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--record-type", default="fact")
    parser.add_argument("--privacy-class", default="personal_stanislav")
    parser.add_argument("--scope", default=Settings.from_env().default_scope)
    parser.add_argument("--created-by", default="openclaw-import")
    parser.add_argument("--source", default="markdown-import")
    parser.add_argument("--reason", default="Owner-reviewed markdown memory migration candidate")
    parser.add_argument("--apply", action="store_true", help="Write candidates to the database")
    return parser


def title_from_path(path: Path) -> str:
    first_heading = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            first_heading = line[2:].strip()
            break
    return first_heading or path.stem


def main() -> int:
    args = build_parser().parse_args()
    repo = None
    if args.apply:
        from openclaw_shared_memory.repository import MemoryRepository

        repo = MemoryRepository(Settings.from_env())
    for path in args.files:
        body = path.read_text(encoding="utf-8")
        draft = MemoryDraft(
            record_type=args.record_type,
            title=title_from_path(path),
            body=body,
            privacy_class=args.privacy_class,
            source=args.source,
            source_ref=str(path),
            created_by=args.created_by,
            scope=args.scope,
            tags=["markdown-import", path.stem.lower()],
        )
        draft.validate()
        if args.apply:
            assert repo is not None
            row = repo.propose_memory(draft, args.reason)
            print(f"IMPORTED {path} -> {row['id']}")
        else:
            print(f"DRY_RUN {path} title={draft.title!r} chars={len(body)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
