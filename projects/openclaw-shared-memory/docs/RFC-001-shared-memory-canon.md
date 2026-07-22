# RFC-001: OpenClaw Shared Memory Canon

Status: Draft
Date: 2026-07-22

## Problem

OpenClaw currently uses markdown memory files, daily logs, and scattered session context. This is readable and practical, but it is not transactional, provenance is uneven, and concurrent agents can drift after compaction or long-running work.

## Decision

Introduce a shared memory canon backed by Postgres and pgvector. Agents keep local/private notebooks, but durable cross-agent facts enter the shared canon only through an explicit write path with audit events.

## Non-Goals

- Replacing all markdown memory immediately.
- Importing private agent notes automatically.
- Sending Synology or other private data outside local/private boundaries.
- Letting every agent update canonical memory directly.

## Data Ownership

Every canonical record must carry:

- `record_type`
- `status`
- `scope`
- `privacy_class`
- `source`
- `source_ref` when available
- `owner` when there is a clear owner
- `created_by`
- `updated_by`
- `confidence`
- `tags`
- audit trail

## Write Rules

- A new record starts as `candidate`.
- Promotion to `shared` requires actor, reason, source, confidence, scope, and privacy class.
- Updates that change meaning should create a replacement record and supersede the old one.
- Deletion is not part of the normal workflow. Sensitive cleanup, if ever needed, must be treated as an explicit security operation.
- Audit log is append-only.

## Retrieval Rules

Retrieval must return:

- canonical record id
- status
- source and source_ref
- privacy class
- confidence
- updated_at
- enough audit information to explain why the record is trusted

## Migration Path

1. Keep existing markdown memory as operational source.
2. Start a local Postgres instance.
3. Apply schema and run restore drill against a disposable DB.
4. Import a small owner-approved subset from `DECISIONS.md` and `STATE.md`.
5. Wire an OpenClaw MCP tool to read shared canon.
6. Only then consider replacing direct markdown writes for durable shared facts.
