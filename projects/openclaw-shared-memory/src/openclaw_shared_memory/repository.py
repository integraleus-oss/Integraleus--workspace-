from __future__ import annotations

import json
from typing import Any

import psycopg
from psycopg.rows import dict_row

from .config import Settings
from .models import MemoryDraft


class MemoryRepository:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _connect(self):
        return psycopg.connect(self.settings.database_url, row_factory=dict_row)

    def propose_memory(self, draft: MemoryDraft, reason: str) -> dict[str, Any]:
        draft.validate()
        if not reason.strip():
            raise ValueError("reason must not be blank")

        with self._connect() as conn:
            with conn.transaction():
                row = conn.execute(
                    """
                    INSERT INTO memory_records (
                      record_type, title, body, scope, privacy_class, source, source_ref,
                      owner, created_by, updated_by, confidence, tags, metadata
                    )
                    VALUES (
                      %(record_type)s, %(title)s, %(body)s, %(scope)s, %(privacy_class)s,
                      %(source)s, %(source_ref)s, %(owner)s, %(created_by)s,
                      %(created_by)s, %(confidence)s, %(tags)s, %(metadata)s::jsonb
                    )
                    RETURNING *
                    """,
                    {
                        **draft.__dict__,
                        "metadata": json.dumps(draft.metadata, ensure_ascii=False),
                    },
                ).fetchone()
                conn.execute(
                    """
                    INSERT INTO memory_audit_log (
                      record_id, event_type, actor, reason, after_status, event_data
                    )
                    VALUES (%s, 'proposed', %s, %s, 'candidate', %s::jsonb)
                    """,
                    (
                        row["id"],
                        draft.created_by,
                        reason,
                        json.dumps({"source": draft.source, "source_ref": draft.source_ref}, ensure_ascii=False),
                    ),
                )
                return dict(row)

    def promote_to_shared(self, record_id: str, actor: str, reason: str) -> dict[str, Any]:
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason must not be blank")

        with self._connect() as conn:
            with conn.transaction():
                conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (record_id,))
                before = conn.execute(
                    "SELECT * FROM memory_records WHERE id = %s FOR UPDATE",
                    (record_id,),
                ).fetchone()
                if before is None:
                    raise KeyError(record_id)
                if before["status"] != "candidate":
                    raise ValueError(f"Only candidate records can be promoted, got {before['status']}")
                after = conn.execute(
                    """
                    UPDATE memory_records
                    SET status = 'shared', updated_by = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (actor, record_id),
                ).fetchone()
                conn.execute(
                    """
                    INSERT INTO memory_audit_log (
                      record_id, event_type, actor, reason, before_status, after_status
                    )
                    VALUES (%s, 'promoted', %s, %s, %s, 'shared')
                    """,
                    (record_id, actor, reason, before["status"]),
                )
                return dict(after)

    def supersede(self, old_record_id: str, replacement: MemoryDraft, actor: str, reason: str) -> dict[str, Any]:
        replacement.validate()
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason must not be blank")

        with self._connect() as conn:
            with conn.transaction():
                conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (old_record_id,))
                old = conn.execute(
                    "SELECT * FROM memory_records WHERE id = %s FOR UPDATE",
                    (old_record_id,),
                ).fetchone()
                if old is None:
                    raise KeyError(old_record_id)
                new = conn.execute(
                    """
                    INSERT INTO memory_records (
                      record_type, status, title, body, scope, privacy_class, source,
                      source_ref, owner, created_by, updated_by, confidence, tags,
                      metadata, supersedes_id
                    )
                    VALUES (
                      %(record_type)s, 'shared', %(title)s, %(body)s, %(scope)s,
                      %(privacy_class)s, %(source)s, %(source_ref)s, %(owner)s,
                      %(created_by)s, %(created_by)s, %(confidence)s, %(tags)s,
                      %(metadata)s::jsonb, %(supersedes_id)s
                    )
                    RETURNING *
                    """,
                    {
                        **replacement.__dict__,
                        "metadata": json.dumps(replacement.metadata, ensure_ascii=False),
                        "supersedes_id": old_record_id,
                    },
                ).fetchone()
                conn.execute(
                    """
                    UPDATE memory_records
                    SET status = 'superseded', superseded_by_id = %s, updated_by = %s
                    WHERE id = %s
                    """,
                    (new["id"], actor, old_record_id),
                )
                conn.execute(
                    """
                    INSERT INTO memory_audit_log (
                      record_id, event_type, actor, reason, before_status, after_status,
                      event_data
                    )
                    VALUES (%s, 'superseded', %s, %s, %s, 'superseded', %s::jsonb)
                    """,
                    (
                        old_record_id,
                        actor,
                        reason,
                        old["status"],
                        json.dumps({"replacement_id": str(new["id"])}, ensure_ascii=False),
                    ),
                )
                return dict(new)

    def search_memory(
        self,
        query: str,
        scope: str | None = None,
        status: str = "shared",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        query_text = query.strip()
        if not query_text:
            raise ValueError("query must not be blank")

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM memory_records
                WHERE status = %s
                  AND (%s IS NULL OR scope = %s)
                  AND (
                    title ILIKE '%%' || %s || '%%'
                    OR body ILIKE '%%' || %s || '%%'
                    OR %s = ANY(tags)
                  )
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (status, scope, scope, query_text, query_text, query_text, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_with_audit(self, record_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            record = conn.execute("SELECT * FROM memory_records WHERE id = %s", (record_id,)).fetchone()
            if record is None:
                raise KeyError(record_id)
            audit = conn.execute(
                """
                SELECT *
                FROM memory_audit_log
                WHERE record_id = %s
                ORDER BY created_at ASC, id ASC
                """,
                (record_id,),
            ).fetchall()
            return {"record": dict(record), "audit": [dict(row) for row in audit]}

