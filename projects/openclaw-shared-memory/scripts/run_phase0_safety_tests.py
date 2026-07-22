#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openclaw_shared_memory.config import Settings
from openclaw_shared_memory.models import MemoryDraft
from openclaw_shared_memory.repository import MemoryRepository


DATABASE_URL = os.environ.get(
    "OPENCLAW_MEMORY_TEST_DATABASE_URL",
    os.environ.get("OPENCLAW_MEMORY_DATABASE_URL", ""),
)


def require_disposable_database(url: str) -> None:
    if not url:
        raise SystemExit("Set OPENCLAW_MEMORY_TEST_DATABASE_URL")
    if os.environ.get("OPENCLAW_MEMORY_ALLOW_PHASE0_DESTRUCTIVE_TEST") == "1":
        return
    dbname = urlparse(url).path.rsplit("/", 1)[-1]
    if not any(marker in dbname for marker in ("phase0", "drill", "test", "scratch")):
        raise SystemExit(
            "Refusing DB-backed safety tests against non-disposable database; "
            "dbname must include phase0, drill, test, or scratch"
        )


def digest(*parts: str) -> str:
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def expect_error(label: str, fn) -> None:
    try:
        fn()
    except Exception:
        return
    raise AssertionError(f"Expected failure did not happen: {label}")


def as_role(conn, role: str, sql: str, params=()):
    with conn.transaction():
        conn.execute(f"SET LOCAL ROLE {role}")
        return conn.execute(sql, params)


def main() -> int:
    require_disposable_database(DATABASE_URL)
    with psycopg.connect(DATABASE_URL, row_factory=dict_row, autocommit=True) as conn:
        existing = conn.execute(
            "SELECT count(*) AS n FROM memory_records"
        ).fetchone()["n"]
        if existing:
            raise SystemExit("Phase 0 safety tests require an empty disposable database")
        with conn.transaction():
            rows = conn.execute(
                """
                INSERT INTO memory_records (
                  record_type, status, title, body, scope, privacy_class, source,
                  created_by, updated_by, confidence, content_hash
                )
                VALUES
                  ('decision', 'shared', 'safe shared', 'safe body', 'openclaw', 'shared_safe', 'test', 'tester', 'tester', 0.8, %s),
                  ('fact', 'shared', 'project shared', 'project body', 'openclaw', 'project', 'test', 'tester', 'tester', 0.8, %s),
                  ('state', 'shared', 'forbidden shared', 'secret body', 'openclaw', 'external_forbidden', 'test', 'tester', 'tester', 0.8, %s),
                  ('task', 'candidate', 'candidate safe', 'candidate body', 'openclaw', 'shared_safe', 'test', 'tester', 'tester', 0.8, %s)
                RETURNING id, title
                """,
                (
                    digest("decision", "openclaw", "shared_safe", "safe shared", "safe body", "test", ""),
                    digest("fact", "openclaw", "project", "project shared", "project body", "test", ""),
                    digest("state", "openclaw", "external_forbidden", "forbidden shared", "secret body", "test", ""),
                    digest("task", "openclaw", "shared_safe", "candidate safe", "candidate body", "test", ""),
                ),
            ).fetchall()
            safe_id = rows[0]["id"]
            forbidden_id = rows[2]["id"]
            candidate_id = rows[3]["id"]
            conn.execute(
                """
                INSERT INTO memory_audit_log (record_id, event_type, actor, reason, after_status)
                VALUES (%s, 'promoted', 'tester', 'seed audit', 'shared')
                """,
                (safe_id,),
            )

        reader_rows = as_role(
            conn,
            "openclaw_memory_reader",
            "SELECT privacy_class FROM memory_records ORDER BY title",
        ).fetchall()
        visible_privacy = {row["privacy_class"] for row in reader_rows}
        assert visible_privacy == {"project", "shared_safe"}, visible_privacy

        view_rows = as_role(
            conn,
            "openclaw_memory_reader",
            "SELECT privacy_class FROM current_shared_canon ORDER BY title",
        ).fetchall()
        assert {row["privacy_class"] for row in view_rows} == {"project", "shared_safe"}

        candidates = as_role(
            conn,
            "openclaw_memory_reader",
            "SELECT title FROM memory_records WHERE status = 'candidate'",
        ).fetchall()
        assert [row["title"] for row in candidates] == ["candidate safe"]

        expect_error(
            "reader cannot insert",
            lambda: as_role(
                conn,
                "openclaw_memory_reader",
                """
                INSERT INTO memory_records (
                  record_type, status, title, body, scope, privacy_class, source,
                  created_by, updated_by, content_hash
                )
                VALUES ('fact', 'candidate', 'reader write', 'no', 'openclaw', 'shared_safe', 'test', 'reader', 'reader', %s)
                """,
                (digest("fact", "openclaw", "shared_safe", "reader write", "no", "test", ""),),
            ),
        )

        expect_error(
            "writer cannot promote/update",
            lambda: as_role(
                conn,
                "openclaw_memory_writer",
                "UPDATE memory_records SET status = 'shared' WHERE id = %s",
                (candidate_id,),
            ),
        )

        expect_error(
            "writer cannot insert external_forbidden",
            lambda: as_role(
                conn,
                "openclaw_memory_writer",
                """
                INSERT INTO memory_records (
                  record_type, status, title, body, scope, privacy_class, source,
                  created_by, updated_by, content_hash
                )
                VALUES ('fact', 'candidate', 'forbidden insert', 'no', 'openclaw', 'external_forbidden', 'test', 'writer', 'writer', %s)
                """,
                (digest("fact", "openclaw", "external_forbidden", "forbidden insert", "no", "test", ""),),
            ),
        )

        expect_error(
            "audit update is blocked",
            lambda: conn.execute("UPDATE memory_audit_log SET reason = 'mutated' WHERE record_id = %s", (safe_id,)),
        )
        expect_error(
            "audit delete is blocked",
            lambda: conn.execute("DELETE FROM memory_audit_log WHERE record_id = %s", (safe_id,)),
        )
        expect_error(
            "audit truncate is blocked",
            lambda: conn.execute("TRUNCATE memory_audit_log"),
        )

    os.environ["OPENCLAW_MEMORY_DATABASE_URL"] = DATABASE_URL
    os.environ["OPENCLAW_MEMORY_READER_DATABASE_URL"] = DATABASE_URL
    os.environ["OPENCLAW_MEMORY_WRITER_DATABASE_URL"] = DATABASE_URL
    os.environ["OPENCLAW_MEMORY_PROMOTER_DATABASE_URL"] = DATABASE_URL
    os.environ["OPENCLAW_MEMORY_PROMOTER_ACTORS"] = "stanislav,openclaw-main"

    repo = MemoryRepository(Settings.from_env())
    forbidden_draft = MemoryDraft(
        record_type="fact",
        title="phase0 forbidden app propose",
        body="This class must not be app-writable.",
        privacy_class="external_forbidden",
        source="phase0-safety",
        created_by="openclaw-main",
    )
    expect_error("app refuses forbidden propose", lambda: repo.propose_memory(forbidden_draft, "must fail"))

    workflow_draft = MemoryDraft(
        record_type="decision",
        title="phase0 repository workflow",
        body="Repository workflow must be guarded and idempotent.",
        privacy_class="shared_safe",
        source="phase0-safety",
        created_by="openclaw-main",
        confidence=0.7,
    )
    candidate = repo.propose_memory(workflow_draft, "phase0 repository propose")
    duplicate = repo.propose_memory(workflow_draft, "phase0 duplicate propose")
    assert duplicate["id"] == candidate["id"]
    assert duplicate["idempotent"] is True

    expect_error(
        "non-allowlisted actor cannot promote",
        lambda: repo.promote_to_shared(
            candidate["id"],
            "random-agent",
            "bad actor",
            "shared_safe",
            "openclaw",
            "phase0-safety",
            0.7,
        ),
    )
    expect_error(
        "promote confirmation mismatch",
        lambda: repo.promote_to_shared(
            candidate["id"],
            "stanislav",
            "bad confidence",
            "shared_safe",
            "openclaw",
            "phase0-safety",
            0.2,
        ),
    )
    promoted = repo.promote_to_shared(
        candidate["id"],
        "stanislav",
        "phase0 repository promote",
        "shared_safe",
        "openclaw",
        "phase0-safety",
        0.7,
    )
    assert promoted["status"] == "shared"
    assert repo.get_with_audit(candidate["id"])["audit"]
    expect_error("get_with_audit denies forbidden record", lambda: repo.get_with_audit(forbidden_id))

    replacement = MemoryDraft(
        record_type="decision",
        title="phase0 replacement",
        body="Replacement record created by supersede.",
        privacy_class="shared_safe",
        source="phase0-safety",
        created_by="openclaw-main",
        confidence=0.8,
    )
    superseded = repo.supersede(candidate["id"], replacement, "stanislav", "phase0 supersede")
    assert superseded["supersedes_id"] == candidate["id"]

    expect_error("supersede non-shared record", lambda: repo.supersede(candidate_id, replacement, "stanislav", "must fail"))
    rejected = repo.reject_candidate(candidate_id, "stanislav", "phase0 reject seed candidate")
    assert rejected["status"] == "rejected"
    archived = repo.archive_record(candidate["id"], "stanislav", "phase0 archive superseded")
    assert archived["status"] == "archived"
    assert all(row["privacy_class"] in {"project", "shared_safe"} for row in repo.search_memory("phase0", limit=10))
    assert all(row["privacy_class"] in {"project", "shared_safe"} for row in repo.list_candidates(limit=10))

    print("PHASE0_DB_SAFETY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
