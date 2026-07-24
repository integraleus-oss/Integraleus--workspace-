# Phase 5 Import Precheck

Status: prepared
Date: 2026-07-24

## Purpose

This precheck must pass before any later Phase 5 candidate-write approval can
be considered. It is intentionally stricter than the current prep-only scope.

## Required Before Real Candidate Import

- Exact source files are named in the approval request.
- Maximum candidate count is named.
- Source files are reviewed for secrets and private raw content.
- Every candidate has a source reference and checksum.
- Candidate writes use writer role only.
- Candidate queue remains separate from shared canon.
- Promotion remains disabled unless separately approved per record or batch.
- Markdown memory remains authoritative until a later migration decision.

## Default Denials

Do not import these sources without a future explicit approval naming them:

- `MEMORY.md`
- `STATE.md`
- `DECISIONS.md`
- `memory/*.md`
- session transcript exports
- Synology files
- backups, dumps, archives, `.env`, `*.session`

## Required Smoke Checks

```bash
.venv/bin/python scripts/plan_phase5_candidate_import.py \
  --source docs/phase5_synthetic_candidates.md \
  --output /tmp/phase5-candidates.jsonl

.venv/bin/python scripts/plan_phase5_candidate_import.py \
  --source MEMORY.md
# expected: refusal unless a later real-source flag and approval exist
```

## Stop Conditions

Stop immediately if:

- a candidate body contains a secret-like value;
- a source path resolves outside the approved source list;
- candidate count exceeds the approved cap;
- privacy class is missing or invalid;
- output would include raw Synology data;
- tooling attempts DB writes during prep.
