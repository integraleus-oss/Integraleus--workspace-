# Execution Supervisor TaskFlow

Prepared OpenClaw plugin adapter for `scripts/execution-supervisor.py`.

It creates an owner-bound managed TaskFlow, launches the durable supervisor,
and reconciles persisted terminal state after a tool interruption or Gateway
restart. TaskFlow `state_changes` supplies the managed owner-notification path;
the supervisor JSONL outbox remains the exactly-once local delivery ledger.

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

Owner admission covers every Telegram topic/direct session routed to agent
`main`, plus its canonical direct session `agent:main:main`. It does not admit
sessions belonging to other agents. The workspace Execution Truth Protocol
requires any work that continues beyond the current turn to use this managed
tool; ordinary one-turn replies do not create synthetic background jobs.
