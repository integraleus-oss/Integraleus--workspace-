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

    def _connect(self, role: str = "admin"):
        return psycopg.connect(self.settings.database_url_for_role(role), row_factory=dict_row)

    def _privacy_tuple(self, privacy_classes: set[str] | frozenset[str] | None = None) -> tuple[str, ...]:
        allowed = tuple(sorted(privacy_classes or self.settings.readable_privacy_classes))
        if not allowed:
            raise ValueError("privacy allowlist must not be empty")
        return allowed

    def _require_promoter(self, actor: str) -> None:
        if actor not in self.settings.promoter_actors:
            raise PermissionError(f"actor is not allowed to promote or mutate shared canon: {actor}")

    def propose_memory(self, draft: MemoryDraft, reason: str) -> dict[str, Any]:
        draft.validate()
        if not reason.strip():
            raise ValueError("reason must not be blank")
        if draft.privacy_class not in self.settings.writable_privacy_classes:
            raise PermissionError(f"privacy_class is not writable through propose_memory: {draft.privacy_class}")

        content_hash = draft.content_hash()
        with self._connect("writer") as conn:
            with conn.transaction():
                conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (content_hash,))
                existing = conn.execute(
                    """
                    SELECT *
                    FROM memory_records
                    WHERE content_hash = %s
                      AND status IN ('candidate', 'shared')
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """,
                    (content_hash,),
                ).fetchone()
                if existing is not None:
                    return {**dict(existing), "idempotent": True}

                row = conn.execute(
                    """
                    INSERT INTO memory_records (
                      record_type, title, body, scope, privacy_class, source, source_ref,
                      owner, created_by, updated_by, confidence, tags, metadata, content_hash
                    )
                    VALUES (
                      %(record_type)s, %(title)s, %(body)s, %(scope)s, %(privacy_class)s,
                      %(source)s, %(source_ref)s, %(owner)s, %(created_by)s,
                      %(created_by)s, %(confidence)s, %(tags)s, %(metadata)s::jsonb,
                      %(content_hash)s
                    )
                    RETURNING *
                    """,
                    {
                        **draft.__dict__,
                        "metadata": json.dumps(draft.metadata, ensure_ascii=False),
                        "content_hash": content_hash,
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

    def promote_to_shared(
        self,
        record_id: str,
        actor: str,
        reason: str,
        privacy_class: str,
        scope: str,
        source: str,
        confidence: float,
    ) -> dict[str, Any]:
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason must not be blank")
        self._require_promoter(actor)
        if not privacy_class.strip() or not scope.strip() or not source.strip():
            raise ValueError("privacy_class, scope, and source confirmations must not be blank")
        if not 0 <= confidence <= 1:
            raise ValueError("confidence confirmation must be between 0 and 1")

        with self._connect("promoter") as conn:
            with conn.transaction():
                conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s::text))", (record_id,))
                before = conn.execute(
                    "SELECT * FROM memory_records WHERE id = %s FOR UPDATE",
                    (record_id,),
                ).fetchone()
                if before is None:
                    raise KeyError(record_id)
                if before["status"] != "candidate":
                    raise ValueError(f"Only candidate records can be promoted, got {before['status']}")
                mismatches = {
                    "privacy_class": (before["privacy_class"], privacy_class),
                    "scope": (before["scope"], scope),
                    "source": (before["source"], source),
                }
                mismatches = {key: value for key, value in mismatches.items() if value[0] != value[1]}
                if abs(float(before["confidence"]) - float(confidence)) > 0.0005:
                    mismatches["confidence"] = (float(before["confidence"]), float(confidence))
                if mismatches:
                    raise ValueError(f"promotion confirmation mismatch: {mismatches}")
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

    def reject_candidate(self, record_id: str, actor: str, reason: str) -> dict[str, Any]:
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason must not be blank")
        self._require_promoter(actor)

        with self._connect("promoter") as conn:
            with conn.transaction():
                conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s::text))", (record_id,))
                before = conn.execute(
                    "SELECT * FROM memory_records WHERE id = %s FOR UPDATE",
                    (record_id,),
                ).fetchone()
                if before is None:
                    raise KeyError(record_id)
                if before["status"] != "candidate":
                    raise ValueError(f"Only candidate records can be rejected, got {before['status']}")
                after = conn.execute(
                    """
                    UPDATE memory_records
                    SET status = 'rejected', updated_by = %s
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
                    VALUES (%s, 'rejected', %s, %s, %s, 'rejected')
                    """,
                    (record_id, actor, reason, before["status"]),
                )
                return dict(after)

    def archive_record(self, record_id: str, actor: str, reason: str) -> dict[str, Any]:
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason must not be blank")
        self._require_promoter(actor)

        with self._connect("promoter") as conn:
            with conn.transaction():
                conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s::text))", (record_id,))
                before = conn.execute(
                    "SELECT * FROM memory_records WHERE id = %s FOR UPDATE",
                    (record_id,),
                ).fetchone()
                if before is None:
                    raise KeyError(record_id)
                if before["status"] not in {"shared", "superseded"}:
                    raise ValueError(f"Only shared/superseded records can be archived, got {before['status']}")
                after = conn.execute(
                    """
                    UPDATE memory_records
                    SET status = 'archived', updated_by = %s
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
                    VALUES (%s, 'archived', %s, %s, %s, 'archived')
                    """,
                    (record_id, actor, reason, before["status"]),
                )
                return dict(after)

    def supersede(self, old_record_id: str, replacement: MemoryDraft, actor: str, reason: str) -> dict[str, Any]:
        replacement.validate()
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason must not be blank")
        self._require_promoter(actor)

        content_hash = replacement.content_hash()
        with self._connect("promoter") as conn:
            with conn.transaction():
                conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s::text))", (old_record_id,))
                old = conn.execute(
                    "SELECT * FROM memory_records WHERE id = %s FOR UPDATE",
                    (old_record_id,),
                ).fetchone()
                if old is None:
                    raise KeyError(old_record_id)
                if old["status"] != "shared":
                    raise ValueError(f"Only shared records can be superseded, got {old['status']}")
                new = conn.execute(
                    """
                    INSERT INTO memory_records (
                      record_type, status, title, body, scope, privacy_class, source,
                      source_ref, owner, created_by, updated_by, confidence, tags,
                      metadata, supersedes_id, content_hash
                    )
                    VALUES (
                      %(record_type)s, 'shared', %(title)s, %(body)s, %(scope)s,
                      %(privacy_class)s, %(source)s, %(source_ref)s, %(owner)s,
                      %(created_by)s, %(updated_by)s, %(confidence)s, %(tags)s,
                      %(metadata)s::jsonb, %(supersedes_id)s, %(content_hash)s
                    )
                    RETURNING *
                    """,
                    {
                        **replacement.__dict__,
                        "metadata": json.dumps(replacement.metadata, ensure_ascii=False),
                        "supersedes_id": old_record_id,
                        "content_hash": content_hash,
                        "updated_by": actor,
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
        privacy_classes: set[str] | frozenset[str] | None = None,
    ) -> list[dict[str, Any]]:
        query_text = query.strip()
        if not query_text:
            raise ValueError("query must not be blank")
        allowed = self._privacy_tuple(privacy_classes)

        with self._connect("reader") as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM memory_records
                WHERE status = %s
                  AND (%s::text IS NULL OR scope = %s)
                  AND privacy_class = ANY(%s)
                  AND (
                    title ILIKE '%%' || %s || '%%'
                    OR body ILIKE '%%' || %s || '%%'
                    OR %s = ANY(tags)
                  )
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (status, scope, scope, list(allowed), query_text, query_text, query_text, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def list_candidates(
        self,
        scope: str | None = None,
        limit: int = 50,
        privacy_classes: set[str] | frozenset[str] | None = None,
    ) -> list[dict[str, Any]]:
        allowed = self._privacy_tuple(privacy_classes)
        with self._connect("reader") as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM memory_records
                WHERE status = 'candidate'
                  AND (%s::text IS NULL OR scope = %s)
                  AND privacy_class = ANY(%s)
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (scope, scope, list(allowed), limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_with_audit(
        self,
        record_id: str,
        privacy_classes: set[str] | frozenset[str] | None = None,
    ) -> dict[str, Any]:
        allowed = self._privacy_tuple(privacy_classes)
        with self._connect("reader") as conn:
            record = conn.execute(
                "SELECT * FROM memory_records WHERE id = %s AND privacy_class = ANY(%s)",
                (record_id, list(allowed)),
            ).fetchone()
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
