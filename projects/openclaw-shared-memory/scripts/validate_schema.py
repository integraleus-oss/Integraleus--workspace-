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
        ROOT / "migrations" / "002_hardening.sql",
        [
            "openclaw_memory_reader",
            "openclaw_memory_writer",
            "openclaw_memory_promoter",
            "openclaw_memory_backup",
            "openclaw_memory_admin",
            "CREATE EXTENSION IF NOT EXISTS pgcrypto",
            "content_hash",
            "ENABLE ROW LEVEL SECURITY",
            "FORCE ROW LEVEL SECURITY",
            "actual backup LOGIN role must be provisioned with BYPASSRLS",
            "prevent_memory_audit_mutation",
            "BEFORE TRUNCATE ON memory_audit_log",
            "security_invoker",
            "current_shared_canon",
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
            "reject_candidate",
            "archive_record",
            "list_candidates",
            "supersede",
            "search_memory",
            "get_with_audit",
            "pg_advisory_xact_lock",
            "_require_promoter",
            "writable_privacy_classes",
            "content_hash",
        ],
    )
    require_contains(
        ROOT / "deploy" / "synology" / "docker-compose.synology.yml",
        [
            "OPENCLAW_MEMORY_BIND_HOST",
            "?set OPENCLAW_MEMORY_BIND_HOST",
        ],
    )
    require_contains(
        ROOT / "scripts" / "export_markdown_mirror.py",
        [
            "OPENCLAW_MEMORY_MIRROR_PRIVACY_CLASSES",
            "Refusing plaintext mirror export",
            "privacy_class = ANY",
        ],
    )
    require_contains(
        ROOT / "scripts" / "backup_memory.sh",
        [
            "OPENCLAW_MEMORY_REAL_DATA",
            "OPENCLAW_MEMORY_BACKUP_AGE_RECIPIENT",
            "Refusing real-data plaintext backup",
        ],
    )
    require_contains(
        ROOT / "scripts" / "restore_drill.sh",
        [
            "sha256sum -c",
            "Refusing restore drill",
            "drill, test, or scratch",
        ],
    )
    require_contains(
        ROOT / "scripts" / "run_phase0_safety_tests.py",
        [
            "PHASE0_DB_SAFETY_OK",
            "openclaw_memory_reader",
            "writer cannot promote",
            "audit update is blocked",
            "audit truncate is blocked",
            "app refuses forbidden propose",
            "non-allowlisted actor cannot promote",
            "get_with_audit denies forbidden record",
        ],
    )
    require_contains(
        ROOT / "scripts" / "run_phase1_local_pilot.py",
        [
            "PHASE1_LOCAL_PILOT_OK",
            "ocsm_phase1_reader",
            "OPENCLAW_MEMORY_READER_DATABASE_URL",
            "writer cannot update directly",
            "backup_can_see_forbidden",
            "BYPASSRLS",
        ],
    )
    print("VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
