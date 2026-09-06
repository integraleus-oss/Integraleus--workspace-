# Standards review request

Review the scoped implementation for correctness, regressions, security, and
alignment with repository rules. Do not edit files.

Files:
- scripts/managed-outcome-contract.mjs
- scripts/managed-agent-runner.mjs
- scripts/managed-agent-runner.test.mjs
- scripts/execution-supervisor.py
- scripts/test_execution_supervisor.py
- projects/execution-supervisor-taskflow/index.js
- projects/execution-supervisor-taskflow/index.test.mjs
- projects/execution-supervisor-taskflow/openclaw.plugin.json
- projects/execution-supervisor-taskflow/package.json
- projects/execution-supervisor-taskflow/package-lock.json
- projects/execution-supervisor-taskflow/README.md

Focus on process lifetime, exit/status reconciliation, atomicity, restart
behavior, stale files, timeout budgeting, config contracts, test quality,
backward compatibility, and exactly-once terminal delivery. Return findings by
severity with exact file/line references. End with PASS or FAIL.
