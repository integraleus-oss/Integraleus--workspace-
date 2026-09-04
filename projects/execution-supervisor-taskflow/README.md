# Execution Supervisor TaskFlow

Prepared OpenClaw plugin adapter for `scripts/execution-supervisor.py`.

It creates an owner-bound managed TaskFlow, launches the durable supervisor,
and reconciles persisted terminal state after a tool interruption or Gateway
restart. TaskFlow `state_changes` supplies the managed owner-notification path;
the supervisor JSONL outbox remains the durable at-least-once delivery ledger.

## Activation status

Installed and enabled with explicit owner approval on 2026-09-01. Owner-only
tool access accepts either an authenticated channel owner or a session key
explicitly allowlisted in plugin config. The latter supports local Gateway RPC
drills without granting arbitrary sessions access to command execution.

The trusted delivery context of the originating owner session is persisted in
the supervisor state. A Gateway-side recovery service scans incomplete states,
sends through that originating channel/topic/direct route with the notification
id as the durable delivery queue id, and acknowledges the outbox only after the
provider send succeeds. Static `delivery` config remains legacy-only and is not
used for new runs.

Owner admission requires an authenticated owner sender or an exact session/sender
allowlist entry. It does not trust session-key prefixes. The workspace Execution Truth Protocol
requires any work that continues beyond the current turn to use this managed
tool; ordinary one-turn replies do not create synthetic background jobs.

## Program completion contract

Managed agent execution is multi-slice. Each slice persists
`MANAGED_OUTCOME.json` with work packages, acceptance gates, evidence, and the
next state. `CONTINUE` starts another slice in the same managed session.
`SUCCEEDED` is accepted only when every package and gate is evidenced as
passed. `BLOCKED` requires a genuine external dependency, supporting evidence,
and an explicit owner action. A zero process exit code by itself is not task
success.

### 0.3 migration note

The arbitrary-command `execution_supervisor_start` tool was removed. Managed
admission routes only through `managed-agent-runner.mjs`; its terminal envelope
is bound to a supervisor-generated nonce, and a clean process exit without that
validated envelope is `FAILED`. Planner, implementation slices, and terminal
reviewers always use `high` thinking.

Terminal owner notifications use **at-least-once** delivery. The durable
`notificationId` is reused across retries and concurrent senders are excluded
by a delivery lease. If a process dies after the provider accepted a message
but before acknowledgement is persisted, the message may be delivered again;
losing the terminal result is intentionally considered worse than a duplicate.
