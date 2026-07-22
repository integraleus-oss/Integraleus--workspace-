#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openclaw_shared_memory.config import Settings
from openclaw_shared_memory.models import MemoryDraft
from openclaw_shared_memory.repository import MemoryRepository


ADMIN_URL = os.environ.get(
    "OPENCLAW_MEMORY_PHASE1_ADMIN_DATABASE_URL",
    os.environ.get("OPENCLAW_MEMORY_DATABASE_URL", ""),
)

USERS = {
    "reader": ("ocsm_phase1_reader", "openclaw_memory_reader", "phase1_reader_pw"),
    "writer": ("ocsm_phase1_writer", "openclaw_memory_writer", "phase1_writer_pw"),
    "promoter": ("ocsm_phase1_promoter", "openclaw_memory_promoter", "phase1_promoter_pw"),
    "backup": ("ocsm_phase1_backup", "openclaw_memory_backup", "phase1_backup_pw"),
}


def require_disposable_database(url: str) -> None:
    if not url:
        raise SystemExit("Set OPENCLAW_MEMORY_PHASE1_ADMIN_DATABASE_URL")
    dbname = urlparse(url).path.rsplit("/", 1)[-1]
    if not any(marker in dbname for marker in ("phase1", "drill", "test", "scratch")):
        raise SystemExit(
            "Refusing Phase 1 pilot against non-disposable database; "
            "dbname must include phase1, drill, test, or scratch"
        )


def role_url(admin_url: str, role: str) -> str:
    parsed = urlparse(admin_url)
    username, _, password = USERS[role]
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    auth = quote(username)
    auth = f"{auth}:{quote(password)}"
    return urlunparse((parsed.scheme, f"{auth}@{netloc}", parsed.path, "", parsed.query, ""))


def digest(*parts: str) -> str:
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def expect_error(label: str, fn) -> None:
    try:
        fn()
    except Exception:
        return
    raise AssertionError(f"Expected failure did not happen: {label}")


def provision_users(admin_url: str) -> None:
    with psycopg.connect(admin_url, autocommit=True) as conn:
        for username, group_role, password in USERS.values():
            exists = conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,)).fetchone()
            if not exists:
                conn.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(username),
                        sql.Literal(password),
                    )
                )
            else:
                conn.execute(
                    sql.SQL("ALTER ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(username),
                        sql.Literal(password),
                    )
                )
            conn.execute(
                sql.SQL("GRANT {} TO {}").format(
                    sql.Identifier(group_role),
                    sql.Identifier(username),
                )
            )
            bypass = sql.SQL("BYPASSRLS") if group_role == "openclaw_memory_backup" else sql.SQL("NOBYPASSRLS")
            conn.execute(sql.SQL("ALTER ROLE {} {}").format(sql.Identifier(username), bypass))


def seed_forbidden_records(admin_url: str) -> tuple[str, str]:
    with psycopg.connect(admin_url, row_factory=dict_row, autocommit=True) as conn:
        existing = conn.execute("SELECT count(*) AS n FROM memory_records").fetchone()["n"]
        if existing:
            raise SystemExit("Phase 1 pilot requires an empty disposable database")
        rows = conn.execute(
            """
            INSERT INTO memory_records (
              record_type, status, title, body, scope, privacy_class, source,
              created_by, updated_by, confidence, content_hash
            )
            VALUES
              ('fact', 'shared', 'phase1 external forbidden', 'must not be visible', 'openclaw', 'external_forbidden', 'phase1-seed', 'phase1', 'phase1', 0.9, %s),
              ('fact', 'candidate', 'phase1 personal candidate', 'must not be listed', 'openclaw', 'personal_stanislav', 'phase1-seed', 'phase1', 'phase1', 0.9, %s)
            RETURNING id, title
            """,
            (
                digest("fact", "openclaw", "external_forbidden", "phase1 external forbidden", "must not be visible", "phase1-seed", ""),
                digest("fact", "openclaw", "personal_stanislav", "phase1 personal candidate", "must not be listed", "phase1-seed", ""),
            ),
        ).fetchall()
        return str(rows[0]["id"]), str(rows[1]["id"])


def main() -> int:
    require_disposable_database(ADMIN_URL)
    provision_users(ADMIN_URL)
    forbidden_id, _personal_candidate_id = seed_forbidden_records(ADMIN_URL)

    os.environ["OPENCLAW_MEMORY_DATABASE_URL"] = ADMIN_URL
    os.environ["OPENCLAW_MEMORY_READER_DATABASE_URL"] = role_url(ADMIN_URL, "reader")
    os.environ["OPENCLAW_MEMORY_WRITER_DATABASE_URL"] = role_url(ADMIN_URL, "writer")
    os.environ["OPENCLAW_MEMORY_PROMOTER_DATABASE_URL"] = role_url(ADMIN_URL, "promoter")
    os.environ["OPENCLAW_MEMORY_BACKUP_DATABASE_URL"] = role_url(ADMIN_URL, "backup")
    os.environ["OPENCLAW_MEMORY_READABLE_PRIVACY_CLASSES"] = "project,shared_safe"
    os.environ["OPENCLAW_MEMORY_WRITABLE_PRIVACY_CLASSES"] = "project,shared_safe"
    os.environ["OPENCLAW_MEMORY_PROMOTER_ACTORS"] = "stanislav,openclaw-main"

    repo = MemoryRepository(Settings.from_env())

    primary = MemoryDraft(
        record_type="decision",
        title="phase1 role-scoped pilot",
        body="Distinct login users must enforce repository boundaries.",
        privacy_class="shared_safe",
        source="phase1-pilot",
        created_by="openclaw-main",
        confidence=0.7,
        tags=["phase1"],
    )
    candidate = repo.propose_memory(primary, "phase1 writer propose")
    duplicate = repo.propose_memory(primary, "phase1 duplicate propose")
    assert duplicate["id"] == candidate["id"]
    assert duplicate["idempotent"] is True
    assert any(row["id"] == candidate["id"] for row in repo.list_candidates(limit=20))

    expect_error("reader cannot write directly", lambda: _reader_insert())
    expect_error("writer cannot update directly", lambda: _writer_update(candidate["id"]))
    expect_error("app refuses forbidden propose", lambda: repo.propose_memory(_forbidden_draft(), "must fail"))
    expect_error(
        "non-allowlisted actor cannot promote",
        lambda: repo.promote_to_shared(candidate["id"], "random-agent", "bad actor", "shared_safe", "openclaw", "phase1-pilot", 0.7),
    )
    expect_error(
        "confirmation mismatch blocks promote",
        lambda: repo.promote_to_shared(candidate["id"], "stanislav", "bad source", "shared_safe", "openclaw", "other-source", 0.7),
    )

    promoted = repo.promote_to_shared(
        candidate["id"],
        "stanislav",
        "phase1 promote",
        "shared_safe",
        "openclaw",
        "phase1-pilot",
        0.7,
    )
    assert promoted["status"] == "shared"
    assert repo.get_with_audit(candidate["id"])["audit"]
    expect_error("forbidden shared record is denied by get_with_audit", lambda: repo.get_with_audit(forbidden_id))

    replacement = MemoryDraft(
        record_type="decision",
        title="phase1 replacement",
        body="Replacement after role-scoped supersede.",
        privacy_class="shared_safe",
        source="phase1-pilot",
        created_by="openclaw-main",
        confidence=0.8,
        tags=["phase1"],
    )
    new_shared = repo.supersede(candidate["id"], replacement, "stanislav", "phase1 supersede")
    assert new_shared["supersedes_id"] == candidate["id"]

    reject_draft = MemoryDraft(
        record_type="task",
        title="phase1 rejected candidate",
        body="Candidate intentionally rejected in pilot.",
        privacy_class="project",
        source="phase1-pilot",
        created_by="openclaw-main",
    )
    rejected_candidate = repo.propose_memory(reject_draft, "phase1 reject candidate")
    rejected = repo.reject_candidate(rejected_candidate["id"], "stanislav", "phase1 reject")
    assert rejected["status"] == "rejected"

    archived = repo.archive_record(candidate["id"], "stanislav", "phase1 archive superseded")
    assert archived["status"] == "archived"

    visible = repo.search_memory("phase1", limit=20)
    assert visible
    assert all(row["privacy_class"] in {"project", "shared_safe"} for row in visible)
    assert all(row["privacy_class"] in {"project", "shared_safe"} for row in repo.list_candidates(limit=20))

    _backup_can_see_forbidden(forbidden_id)
    print("PHASE1_LOCAL_PILOT_OK")
    return 0


def _forbidden_draft() -> MemoryDraft:
    return MemoryDraft(
        record_type="fact",
        title="phase1 forbidden propose",
        body="This must not be writable.",
        privacy_class="external_forbidden",
        source="phase1-pilot",
        created_by="openclaw-main",
    )


def _reader_insert() -> None:
    with psycopg.connect(role_url(ADMIN_URL, "reader"), autocommit=True) as conn:
        conn.execute(
            """
            INSERT INTO memory_records (
              record_type, status, title, body, scope, privacy_class, source,
              created_by, updated_by, content_hash
            )
            VALUES ('fact', 'candidate', 'reader insert', 'no', 'openclaw', 'shared_safe', 'phase1', 'reader', 'reader', %s)
            """,
            (digest("fact", "openclaw", "shared_safe", "reader insert", "no", "phase1", ""),),
        )


def _writer_update(record_id: str) -> None:
    with psycopg.connect(role_url(ADMIN_URL, "writer"), autocommit=True) as conn:
        conn.execute("UPDATE memory_records SET status = 'shared' WHERE id = %s", (record_id,))


def _backup_can_see_forbidden(record_id: str) -> None:
    with psycopg.connect(role_url(ADMIN_URL, "backup"), row_factory=dict_row, autocommit=True) as conn:
        row = conn.execute("SELECT id FROM memory_records WHERE id = %s", (record_id,)).fetchone()
        assert row is not None


if __name__ == "__main__":
    raise SystemExit(main())
