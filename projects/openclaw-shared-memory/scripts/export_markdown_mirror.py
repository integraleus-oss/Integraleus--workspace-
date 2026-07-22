#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


DATABASE_URL = os.environ.get(
    "OPENCLAW_MEMORY_DATABASE_URL",
    "postgresql://openclaw_memory:openclaw_memory_dev@127.0.0.1:55432/openclaw_memory",
)
MIRROR_DIR = Path(os.environ.get("OPENCLAW_MEMORY_MIRROR_DIR", "./mirror"))
MIRROR_PRIVACY_CLASSES = {
    part.strip()
    for part in os.environ.get("OPENCLAW_MEMORY_MIRROR_PRIVACY_CLASSES", "shared_safe").split(",")
    if part.strip()
}


def safe_name(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    return "-".join(part for part in cleaned.split("-") if part)[:80] or "memory"


def main() -> int:
    if not MIRROR_PRIVACY_CLASSES:
        raise SystemExit("OPENCLAW_MEMORY_MIRROR_PRIVACY_CLASSES must not be empty")

    allowed_plaintext = {"shared_safe"}
    unsafe = MIRROR_PRIVACY_CLASSES - allowed_plaintext
    if unsafe:
        raise SystemExit(f"Refusing plaintext mirror export for privacy classes: {sorted(unsafe)}")

    MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        rows = conn.execute(
            """
            SELECT id, record_type, status, title, body, scope, privacy_class,
                   source, source_ref, owner, confidence, tags, created_at, updated_at
            FROM memory_records
            WHERE status IN ('shared', 'superseded', 'archived')
              AND privacy_class = ANY(%s)
            ORDER BY scope, record_type, updated_at DESC
            """,
            (list(sorted(MIRROR_PRIVACY_CLASSES)),),
        ).fetchall()

    index_lines = ["# OpenClaw Shared Memory Mirror", ""]
    for row in rows:
        filename = f"{row['scope']}-{row['record_type']}-{safe_name(row['title'])}-{row['id']}.md"
        path = MIRROR_DIR / filename
        tags = ", ".join(row["tags"] or [])
        path.write_text(
            "\n".join(
                [
                    "---",
                    f"id: {row['id']}",
                    f"type: {row['record_type']}",
                    f"status: {row['status']}",
                    f"scope: {row['scope']}",
                    f"privacy_class: {row['privacy_class']}",
                    f"source: {row['source']}",
                    f"source_ref: {row['source_ref'] or ''}",
                    f"owner: {row['owner'] or ''}",
                    f"confidence: {row['confidence']}",
                    f"tags: {tags}",
                    f"created_at: {row['created_at']}",
                    f"updated_at: {row['updated_at']}",
                    "---",
                    "",
                    f"# {row['title']}",
                    "",
                    row["body"],
                    "",
                ]
            ),
            encoding="utf-8",
        )
        index_lines.append(f"- [{row['title']}]({filename})")

    (MIRROR_DIR / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"EXPORT_OK rows={len(rows)} dir={MIRROR_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
