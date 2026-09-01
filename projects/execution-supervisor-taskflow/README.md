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

Terminal recovery sends through the configured channel outbound adapter with
the supervisor notification id as the durable delivery queue id, then
acknowledges the local outbox only after the provider send succeeds.
