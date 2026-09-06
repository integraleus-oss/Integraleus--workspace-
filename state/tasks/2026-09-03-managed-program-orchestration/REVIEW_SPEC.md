# Specification review request

Review whether the scoped implementation actually prevents the ZSR failure
mode. Do not edit files.

Required behavior:
- exit code 0 alone cannot prove objective completion;
- a complete objective is decomposed into durable packages and acceptance gates;
- partial work automatically continues in bounded slices;
- SUCCEEDED requires all packages/gates PASSED with evidence;
- BLOCKED requires an evidenced external dependency and owner action;
- internal defects, failed tests, task size, and remaining work cannot be used
  as BLOCKED;
- terminal state is reconciled through supervisor/TaskFlow and delivered once;
- complex managed slices do not inherit low thinking.

Inspect the same implementation files listed in REVIEW_STANDARDS.md plus
TASK_PACKET.md and EVIDENCE.md. Identify any path that can still reproduce
process-success/objective-failure divergence. Return findings by severity with
exact file/line references. End with PASS or FAIL.
