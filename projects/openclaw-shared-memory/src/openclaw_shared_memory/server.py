from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .config import Settings
from .models import MemoryDraft
from .repository import MemoryRepository


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw shared memory command server")
    sub = parser.add_subparsers(dest="command", required=True)

    propose = sub.add_parser("propose_memory")
    propose.add_argument("--record-type", required=True)
    propose.add_argument("--title", required=True)
    propose.add_argument("--body", required=True)
    propose.add_argument("--privacy-class", required=True)
    propose.add_argument("--source", required=True)
    propose.add_argument("--created-by", required=True)
    propose.add_argument("--reason", required=True)
    propose.add_argument("--scope", default=Settings.from_env().default_scope)
    propose.add_argument("--source-ref")
    propose.add_argument("--owner")
    propose.add_argument("--confidence", type=float, default=0.7)
    propose.add_argument("--tag", action="append", default=[])

    promote = sub.add_parser("promote_to_shared")
    promote.add_argument("record_id")
    promote.add_argument("--actor", required=True)
    promote.add_argument("--reason", required=True)

    search = sub.add_parser("search_memory")
    search.add_argument("query")
    search.add_argument("--scope")
    search.add_argument("--status", default="shared")
    search.add_argument("--limit", type=int, default=10)

    get_audit = sub.add_parser("get_with_audit")
    get_audit.add_argument("record_id")

    supersede = sub.add_parser("supersede")
    supersede.add_argument("old_record_id")
    supersede.add_argument("--record-type", required=True)
    supersede.add_argument("--title", required=True)
    supersede.add_argument("--body", required=True)
    supersede.add_argument("--privacy-class", required=True)
    supersede.add_argument("--source", required=True)
    supersede.add_argument("--created-by", required=True)
    supersede.add_argument("--actor", required=True)
    supersede.add_argument("--reason", required=True)
    supersede.add_argument("--scope", default=Settings.from_env().default_scope)
    supersede.add_argument("--source-ref")
    supersede.add_argument("--owner")
    supersede.add_argument("--confidence", type=float, default=0.7)
    supersede.add_argument("--tag", action="append", default=[])

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = MemoryRepository(Settings.from_env())

    try:
        if args.command == "propose_memory":
            row = repo.propose_memory(
                MemoryDraft(
                    record_type=args.record_type,
                    title=args.title,
                    body=args.body,
                    privacy_class=args.privacy_class,
                    source=args.source,
                    created_by=args.created_by,
                    scope=args.scope,
                    source_ref=args.source_ref,
                    owner=args.owner,
                    confidence=args.confidence,
                    tags=args.tag,
                ),
                reason=args.reason,
            )
            _print_json(row)
        elif args.command == "promote_to_shared":
            _print_json(repo.promote_to_shared(args.record_id, args.actor, args.reason))
        elif args.command == "search_memory":
            _print_json(repo.search_memory(args.query, args.scope, args.status, args.limit))
        elif args.command == "get_with_audit":
            _print_json(repo.get_with_audit(args.record_id))
        elif args.command == "supersede":
            replacement = MemoryDraft(
                record_type=args.record_type,
                title=args.title,
                body=args.body,
                privacy_class=args.privacy_class,
                source=args.source,
                created_by=args.created_by,
                scope=args.scope,
                source_ref=args.source_ref,
                owner=args.owner,
                confidence=args.confidence,
                tags=args.tag,
            )
            _print_json(repo.supersede(args.old_record_id, replacement, args.actor, args.reason))
    except Exception as exc:
        _print_json({"ok": False, "error": type(exc).__name__, "message": str(exc)})
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
