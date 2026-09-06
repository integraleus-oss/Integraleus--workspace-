Review the current uncommitted managed-program implementation for objective completeness and resistance to the original ZSR false-success failure. Inspect only:
- scripts/managed-outcome-contract.mjs
- scripts/managed-agent-runner.mjs
- scripts/managed-agent-runner.test.mjs
- state/tasks/2026-09-03-managed-program-orchestration/TASK_PACKET.md

Verify: independent locked planning before execution; bounded continuation after slice failure; SUCCEEDED only after all locked packages/gates have distinct fresh workspace-contained artifacts and an injection-aware independent terminal review; BLOCKED only for a genuine external dependency; no secret exposed to the model; malformed output fails safely. Report concrete HIGH/CRITICAL defects with file:line and finish with PASS or FAIL. Do not edit files. Do not read prior review result files.
