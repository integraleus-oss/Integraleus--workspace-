Implement the frozen universal read-only integration slice in the isolated Alpha BPR worktree.

Authoritative absolute paths for this run:

- packet: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-20-alpha-bpr-universal-integration-v1`
- project worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-v1`
- run root: `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-v1-run`
- focused-test harness: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-20-alpha-bpr-universal-integration-v1/FOCUSED_TEST_HARNESS.sh`

Do not use similarly named older task, worktree, run-root, or output paths.

Prefer one narrow vertical path over framework breadth: schemas and typed models, deterministic validation, a read-only gateway boundary, profile-driven normalization/diagnostics, three example profiles, and focused tests. Existing MIX01/PS01 demonstrations may remain, but new product code must not require their names or fixed NodeIds. The gateway interface must expose no write operation.

Allowed scope is limited to architecture/integration documentation, integration schemas/profiles/examples, new Application/Infrastructure integration code, focused tests, and minimal README updates. Do not modify existing runtime/deployment artifacts unless required only to classify the reference appliance in documentation.

Use fixture transports for this orchestrator run. Clearly state that fixture proof is not a connected Alpha Platform test. Do not access the network, credentials, private endpoints, Alpha packages, VMs, services, Gateway, or system state. Do not commit, push, deploy, or transfer.

The focused integration suite must execute at least six tests; a zero-test or
under-count result is a hard failure even when `dotnet test` exits zero.
