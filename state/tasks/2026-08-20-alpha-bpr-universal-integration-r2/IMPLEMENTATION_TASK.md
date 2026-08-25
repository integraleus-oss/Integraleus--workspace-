Implement the frozen universal read-only integration slice in the isolated Alpha BPR R2 worktree.

Authoritative absolute paths:

- packet: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-20-alpha-bpr-universal-integration-r2`
- project worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-r2`
- run root: `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-r2-run`
- .NET artifact root: `/home/stanislav/agent-runs/dotnet-artifacts/alpha-bpr-universal-integration-r2-run`
- only authorized .NET entrypoint: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-20-alpha-bpr-universal-integration-r2/DOTNET_HARNESS.sh`

Do not read, copy, or reuse implementation output from v1 or any older task/worktree/run-root. Do not use similarly named paths.

Prefer one narrow vertical path: schemas and typed models, deterministic validation, a read-only gateway boundary, profile-driven normalization/diagnostics, three example profiles, and focused tests. Existing MIX01/PS01 demonstrations may remain, but new product code must not require their names or fixed NodeIds. The gateway interface must expose no write operation.

Allowed paths are only those declared in `PRODUCTION_TASK.json`. The following are explicitly forbidden even if found in the worktree: `DECISIONS.md`, `STATE.md`, `TODO.md`, `memory/**`, all task-state files, and all files outside the allowlist. Do not create progress, memory, decision, or state notes in the repository.

Never invoke `dotnet`, MSBuild, or test binaries directly. Use only `DOTNET_HARNESS.sh restore`, `focused`, `build`, or `full`; it redirects all generated build state outside the Git worktree. A zero-test or under-count result is a hard failure.

Use fixture transports only. Clearly state that fixture proof is not a connected Alpha Platform test. Do not access network resources, credentials, private endpoints, Alpha packages, VMs, services, Gateway, or system state. Do not commit, push, deploy, transfer, or change the canonical project.
