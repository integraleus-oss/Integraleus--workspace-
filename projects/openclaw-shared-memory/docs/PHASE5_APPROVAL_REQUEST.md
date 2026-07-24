# Phase 5 Approval Request: Controlled Candidate Import Prep

Status: draft, prep completed; real import not approved
Date: 2026-07-24

## Completed Approval

Stanislav approved:

```text
approve Phase 5 memory import prep only
```

This approval allows documentation, synthetic fixtures, local dry-run tooling,
and verification only.

## Not Approved Yet

- exposing `propose_memory` through OpenClaw MCP/runtime;
- importing real markdown memory into DB candidates;
- promoting candidates to shared canon;
- rejecting/archiving/superseding real records;
- changing markdown memory source-of-truth status;
- reading Synology data for import;
- deleting or purging DB rows.

## Future Candidate-Write Approval Shape

A later approval request should name:

- exact source files;
- maximum candidate count;
- target privacy class policy;
- whether `propose_memory` is exposed through MCP or run as a one-shot local
  tool;
- reviewer and promotion gate;
- rollback/rejection plan.

Example future phrase:

```text
approve Phase 5 tiny candidate import from <exact files>, max <N>, candidates only
```

Without that separate command, Phase 5 remains prep-only.
