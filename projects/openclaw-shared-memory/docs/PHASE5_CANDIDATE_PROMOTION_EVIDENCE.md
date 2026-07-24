# Evidence: Phase 5 Candidate Promotion Pilot

Status: ready
Date: 2026-07-24

## Approved Scope

Stanislav approved:

```text
approve Phase 5 promote imported shared-memory candidates 19309b52-9d04-47cb-83c8-fba1024522f4 31ea008d-0ce1-4032-a499-2a75e34f6de6 bf8b3331-7957-4e17-84e7-d9cf062b0c7c
```

## Boundaries

- Promote only the three listed candidate IDs.
- Keep privacy class `project`.
- Do not import additional candidates.
- Do not expose write tools through MCP/runtime.
- Do not replace markdown as source of truth.
- Do not reject, archive, supersede, or delete records.

## Files Created Or Changed

- [x] `docs/PHASE5_CANDIDATE_PROMOTION_EVIDENCE.md`
- [x] `scripts/promote_phase5_candidates.py`
- [x] `TODO.md`

## Approved Candidate IDs

- [x] `19309b52-9d04-47cb-83c8-fba1024522f4`
- [x] `31ea008d-0ce1-4032-a499-2a75e34f6de6`
- [x] `bf8b3331-7957-4e17-84e7-d9cf062b0c7c`

## Commands Run

Preflight/dry-run:

```bash
.venv/bin/python scripts/promote_phase5_candidates.py
```

Result:

```text
PHASE5_CANDIDATE_PROMOTION_DRY_RUN_OK count=3
```

Apply:

```bash
.venv/bin/python scripts/promote_phase5_candidates.py --apply
```

Result:

```text
PHASE5_CANDIDATE_PROMOTION_APPLY_OK count=3
```

Post-promotion verification:

```text
PHASE5_PROMOTION_SEARCH_AND_QUEUE_OK
```

OpenClaw MCP probe:

```text
openclaw-shared-memory-readonly: 3 tools
```

## Checks

- [x] preflight confirmed all 3 records are `candidate`
- [x] promotion affected only the 3 approved IDs
- [x] each record status became `shared`
- [x] each record kept privacy class `project`
- [x] audit retrieval shows `proposed` then `promoted`
- [x] search returns promoted records through reader policy
- [x] candidate queue no longer lists the promoted records
- [x] write MCP tools remain unexposed
- [x] compileall passes
- [x] pytest passes
- [x] git diff --check passes

## Result

Phase 5 candidate promotion pilot promoted exactly three owner-approved
records from `candidate` to `shared`. No additional candidates were imported.
OpenClaw MCP remains read-only. Markdown remains the source of truth until a
separate migration decision.

## Verification Summary

- `.venv/bin/python -m compileall -q src scripts` -> passed
- `.venv/bin/python -m pytest` -> `2 passed`
- `git diff --check -- projects/openclaw-shared-memory` -> passed
