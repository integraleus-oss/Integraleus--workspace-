Review the current uncommitted supervisor/TaskFlow implementation for execution truth and activation safety. Inspect only:
- scripts/execution-supervisor.py
- scripts/test_execution_supervisor.py
- projects/execution-supervisor-taskflow/index.js
- projects/execution-supervisor-taskflow/index.test.mjs
- projects/execution-supervisor-taskflow/openclaw.plugin.json
- scripts/managed-agent-runner.mjs (capability consumption and child isolation only)

Verify: exit code 0 alone is never SUCCEEDED; terminal capability is not persisted in plaintext or inherited by the model; terminal evidence is read only after runner exit; finalization/outbox is race-safe; managed admission is idempotent, handles Russian/English large objectives, uses high thinking, removes arbitrary-command start, and reconciles owner delivery. Report concrete HIGH/CRITICAL defects with file:line and finish with PASS or FAIL. Do not edit files. Do not read prior review result files.
