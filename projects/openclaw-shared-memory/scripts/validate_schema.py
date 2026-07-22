#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require_contains(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise SystemExit(f"{path}: missing required snippets: {missing}")


def main() -> int:
    require_contains(
        ROOT / "migrations" / "001_initial_schema.sql",
        [
            "CREATE EXTENSION IF NOT EXISTS vector",
            "CREATE TABLE IF NOT EXISTS memory_records",
            "CREATE TABLE IF NOT EXISTS memory_audit_log",
            "CREATE TABLE IF NOT EXISTS memory_embeddings",
            "memory_privacy_class",
        ],
    )
    require_contains(
        ROOT / "docker-compose.yml",
        [
            "pgvector/pgvector:pg16",
            "127.0.0.1:55432:5432",
            "openclaw_shared_memory_pgdata",
        ],
    )
    require_contains(
        ROOT / "src" / "openclaw_shared_memory" / "repository.py",
        [
            "propose_memory",
            "promote_to_shared",
            "supersede",
            "search_memory",
            "get_with_audit",
            "pg_advisory_xact_lock",
        ],
    )
    print("VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
