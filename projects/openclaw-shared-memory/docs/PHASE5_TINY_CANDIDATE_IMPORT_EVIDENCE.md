# Evidence: Phase 5 Tiny Candidate Import

Status: ready
Date: 2026-07-24

## Approved Scope

Stanislav approved:

```text
approve Phase 5 tiny candidate import from DECISIONS.md shared-memory entries, max 3, candidates only
```

## Boundaries

- Source: `DECISIONS.md`
- Selection: latest OpenClaw Shared Memory decisions only
- Maximum candidates: 3
- Target status: `candidate`
- Target privacy class: `project`
- MCP write exposure: forbidden
- Promotion: forbidden
- Markdown source of truth replacement: forbidden

## Files Created Or Changed

- [x] `docs/PHASE5_TINY_CANDIDATE_IMPORT_EVIDENCE.md`
- [x] `scripts/import_phase5_decision_candidates.py`
- [x] `TODO.md`

## Candidate Selection

- [x] `D-2026-07-23-05` — OpenClaw Shared Memory Phase 4 prep accepted
- [x] `D-2026-07-23-06` — OpenClaw Shared Memory Phase 4 read-only MCP runtime accepted
- [x] `D-2026-07-24-01` — OpenClaw Shared Memory Phase 5 prep accepted

## Commands Run

```bash
.venv/bin/python scripts/import_phase5_decision_candidates.py --max-count 3
```

Result:

```text
PHASE5_DECISION_CANDIDATE_IMPORT_DRY_RUN_OK count=3
```

First apply attempt refused because the default settings pointed at
`127.0.0.1:55432`, while the pilot is intentionally bound to
`192.168.68.125:55432`.

Second apply attempt refused because the Synology runbook role names
`ocsm_writer` do not match the actual home pilot login roles.

Read-only role inventory confirmed the actual home pilot login roles:

```text
ocsm_home_backup login=true bypass=true
ocsm_home_promoter login=true bypass=false
ocsm_home_reader login=true bypass=false
ocsm_home_writer login=true bypass=false
```

The successful apply used explicit in-process LAN DSNs for
`ocsm_home_reader`, `ocsm_home_writer`, and `ocsm_home_promoter` without
printing secret values.

```bash
.venv/bin/python scripts/import_phase5_decision_candidates.py --max-count 3 --apply
```

Result:

```text
PHASE5_DECISION_CANDIDATE_IMPORT_APPLY_OK count=3
```

Created candidate IDs:

```text
19309b52-9d04-47cb-83c8-fba1024522f4
31ea008d-0ce1-4032-a499-2a75e34f6de6
bf8b3331-7957-4e17-84e7-d9cf062b0c7c
```

Candidate queue and audit verification:

```text
PHASE5_CANDIDATE_QUEUE_AUDIT_OK
```

## Checks

- [x] dry-run selected exactly 3 candidates
- [x] DB write created only candidate records
- [x] candidate queue lists the imported records
- [x] audit retrieval shows `proposed` event for each imported candidate
- [x] no candidate was promoted
- [x] write MCP tools remain unexposed
- [x] compileall passes
- [x] pytest passes
- [x] git diff --check passes

## Result

Phase 5 tiny candidate-write pilot imported exactly three approved
`DECISIONS.md` OpenClaw Shared Memory entries as `project` privacy candidate
records. No promotion occurred. OpenClaw MCP remains read-only with 3 exposed
tools.

## Verification Summary

- `.venv/bin/python -m compileall -q src scripts` -> passed
- `.venv/bin/python -m pytest` -> `2 passed`
- `git diff --check -- projects/openclaw-shared-memory` -> passed
