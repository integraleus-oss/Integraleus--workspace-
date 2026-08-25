Implement the frozen universal read-only integration slice in the isolated Alpha BPR R4 worktree.

Authoritative paths are supplied by the sealed Broker environment and must match:

- `ORCHESTRATOR_PROJECT_ROOT=/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-r4`
- `ORCHESTRATOR_FIXTURE_ROOT=/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-r4`
- `ORCHESTRATOR_ARTIFACT_ROOT=/tmp/alpha-bpr-universal-integration-r4-artifacts`
- harness: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-21-alpha-bpr-universal-integration-r4/DOTNET_HARNESS.sh`

Change only paths allowed by `PRODUCTION_TASK.json`. Never read, copy, or reuse implementation output from v1, R2, R3, their task directories, worktrees, or run roots. Do not modify or create `DECISIONS.md`, `STATE.md`, `TODO.md`, `memory/**`, or task-state files in Alpha BPR.

Implement one narrow vertical path: closed schemas and typed models, deterministic fail-closed validation, a read-only OPC UA gateway boundary, profile-driven normalization/diagnostics, MIX01/PS01/minimal examples, negative fixtures, and focused tests. Product code must not require example names or fixed NodeIds. The gateway interface must expose no write-shaped operation.

All code and tests must resolve example fixtures exclusively from the sealed `ORCHESTRATOR_FIXTURE_ROOT` contract with `examples/integration-profiles` appended. Validate the root as an absolute existing directory; do not derive repository paths from cwd, test DLL location, parent search, or fallback candidates.

Never invoke `dotnet`, MSBuild, or test binaries directly. Use only the authoritative harness modes `restore`, `focused`, `build`, or `full`. A zero-test or under-count result is failure. The qualified Broker, not Codex sandbox permissions, is authoritative for final gates.

Use fixture transports only and state explicitly that fixture proof is not a connected Alpha Platform test. Do not access credentials, private endpoints, Alpha packages, VMs, services, Gateway, or system state. Do not commit, push, deploy, transfer, or modify the canonical project.
