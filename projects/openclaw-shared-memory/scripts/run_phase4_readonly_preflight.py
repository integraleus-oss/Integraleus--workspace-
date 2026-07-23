#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import quote, urlunparse

import psycopg
from psycopg import errors

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openclaw_shared_memory.config import Settings
from openclaw_shared_memory.repository import MemoryRepository


def env_required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Set {name}")
    return value


def role_url(username: str, password: str) -> str:
    host = os.environ.get("OPENCLAW_MEMORY_BIND_HOST", "192.168.68.125")
    port = os.environ.get("OPENCLAW_MEMORY_PORT", "55432")
    dbname = os.environ.get("POSTGRES_DB", "openclaw_memory")
    auth = f"{quote(username)}:{quote(password)}"
    return urlunparse(("postgresql", f"{auth}@{host}:{port}", f"/{dbname}", "", "", ""))


def expect_error(label: str, expected_error: type[BaseException], fn) -> None:
    try:
        fn()
    except expected_error:
        return
    except Exception as exc:
        raise AssertionError(
            f"Expected {label} to raise {expected_error.__name__}, got {type(exc).__name__}: {exc}"
        ) from exc
    raise AssertionError(f"Expected failure did not happen: {label}")


def configure_urls() -> str:
    admin_url = role_url(env_required("POSTGRES_USER"), env_required("POSTGRES_PASSWORD"))
    reader_url = role_url("ocsm_home_reader", env_required("OCSM_READER_PASSWORD"))
    os.environ["OPENCLAW_MEMORY_DATABASE_URL"] = admin_url
    os.environ["OPENCLAW_MEMORY_READER_DATABASE_URL"] = reader_url
    os.environ["OPENCLAW_MEMORY_READABLE_PRIVACY_CLASSES"] = "project,shared_safe"
    return admin_url


def check_role_attributes(admin_url: str) -> None:
    with psycopg.connect(admin_url) as conn:
        rows = conn.execute(
            """
            SELECT rolname, rolbypassrls
            FROM pg_roles
            WHERE rolname IN (
              'ocsm_home_reader',
              'ocsm_home_writer',
              'ocsm_home_promoter',
              'ocsm_home_backup'
            )
            ORDER BY rolname
            """
        ).fetchall()
    attrs = {name: bypass for name, bypass in rows}
    expected = {
        "ocsm_home_backup": True,
        "ocsm_home_promoter": False,
        "ocsm_home_reader": False,
        "ocsm_home_writer": False,
    }
    if attrs != expected:
        raise AssertionError(f"Unexpected role attributes: {attrs}")


def check_reader_direct_write_denied() -> None:
    reader_url = os.environ["OPENCLAW_MEMORY_READER_DATABASE_URL"]

    def attempt_insert() -> None:
        with psycopg.connect(reader_url, autocommit=True) as conn:
            conn.execute(
                """
                INSERT INTO memory_records (
                  record_type, status, title, body, scope, privacy_class,
                  source, created_by, updated_by, content_hash
                )
                VALUES (
                  'fact', 'candidate', 'phase4 reader direct write',
                  'this write must be denied', 'openclaw', 'shared_safe',
                  'phase4-preflight', 'phase4', 'phase4',
                  'phase4-reader-direct-write-denied'
                )
                """
            )

    expect_error("reader direct write", errors.InsufficientPrivilege, attempt_insert)


def main() -> int:
    admin_url = configure_urls()
    check_role_attributes(admin_url)

    settings = Settings.from_env()
    repo = MemoryRepository(settings)

    records = repo.search_memory("home shared memory smoke", limit=20)
    if not records:
        raise AssertionError("Expected at least one shared_safe smoke record")
    if any(row["privacy_class"] not in {"project", "shared_safe"} for row in records):
        raise AssertionError("Search returned a record outside the Phase 4 privacy allowlist")

    forbidden = repo.search_memory("must not be visible", limit=20)
    if forbidden:
        raise AssertionError("Privacy-denied smoke content was visible to reader")

    candidates = repo.list_candidates(limit=20)
    if any(row["privacy_class"] not in {"project", "shared_safe"} for row in candidates):
        raise AssertionError("Candidate listing returned a record outside the Phase 4 privacy allowlist")

    audited = repo.get_with_audit(str(records[0]["id"]))
    if not audited["record"] or "audit" not in audited:
        raise AssertionError("get_with_audit did not return record plus audit list")

    check_reader_direct_write_denied()
    print("PHASE4_READONLY_PREFLIGHT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
