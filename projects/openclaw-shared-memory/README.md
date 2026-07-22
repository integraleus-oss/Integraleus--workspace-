# OpenClaw Shared Memory

Shared memory canon for OpenClaw agents.

The goal is to keep private agent notes local while giving important cross-agent facts, decisions, current state, tasks, and incidents a controlled shared source of truth.

## Design

- Postgres is the canonical store.
- `pgvector` stores retrieval embeddings.
- Markdown files are a mirror and bootstrap path, not the canonical write target.
- All writes go through one API/MCP path.
- Audit history is append-only.
- Promotion into shared canon is explicit.

## Memory Lifecycle

1. `propose_memory`: create a candidate record from an agent, script, heartbeat, or human request.
2. `promote_to_shared`: mark a candidate as canonical after an explicit reason and classification.
3. `search_memory`: retrieve candidates/canon with filters and provenance.
4. `get_with_audit`: fetch one record plus audit trail.
5. `supersede`: replace a canonical record by appending a supersession event, not by deleting history.

## Privacy Classes

- `private_agent`: local notebook only; should not enter shared DB except as redacted metadata.
- `personal_stanislav`: private to Stanislav and trusted direct agents.
- `project`: usable inside the named project.
- `shared_safe`: safe for trusted OpenClaw agents.
- `external_forbidden`: must not be sent outside the local/private boundary without explicit approval.

## Canonical Record Types

- `decision`: durable approved decision.
- `state`: current status or operating state.
- `fact`: sourced factual knowledge.
- `preference`: user or project preference.
- `task`: durable task or checkpoint.
- `incident`: failure, outage, security event, or operational lesson.
- `procedure`: reusable operating steps.

## Local Start

```bash
cd projects/openclaw-shared-memory
cp .env.example .env
docker compose up -d
python3 scripts/validate_schema.py
```

Apply migrations after the database is running:

```bash
psql "$OPENCLAW_MEMORY_DATABASE_URL" -f migrations/001_initial_schema.sql
```

## Status

See `TODO.md`. This scaffold is not wired into OpenClaw runtime yet.

