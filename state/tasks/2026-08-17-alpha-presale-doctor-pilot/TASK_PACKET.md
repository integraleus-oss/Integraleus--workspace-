# Alpha-Presale `doctor` — controlled manual pilot 002

## Goal

Run the orchestrator in controlled-manual mode to add a CLI command `doctor`
to Alpha-Presale. The command reports local project readiness as
machine-readable JSON and exits non-zero when readiness checks fail.

## Source

- Project: `/home/stanislav/workspace/alpha-presale`
- Fixed source commit: `52ea3ba`
- Mode: `controlled-manual`
- Owner authorization: Telegram topic 2922, message 3356

## Required behavior

- Check availability of required schemas and fixtures.
- Check validity of baseline local configuration.
- Check availability of project verification commands without executing
  licensing calculations.
- Emit deterministic machine-readable JSON.
- Exit `0` only when all required readiness checks pass.
- Exit non-zero with structured failed-check details otherwise.

## Allowed paths

- Alpha-Presale CLI implementation files required for `doctor`.
- Alpha-Presale tests for the command.
- `README.md`.

The implementation task packet must narrow this to explicit file paths before
the builder runs.

## Forbidden

- Licensing/TKP calculations, price data, financial totals, or quote outputs.
- Web/API changes.
- Deployment, services, systemd, Gateway, OpenClaw configuration, or DB writes.
- Customer-facing documents.
- Network access or external sends beyond the already-approved local
  Codex/Claude orchestrator workflow.
- Commit, transfer, push, deploy, or writes to the canonical Alpha-Presale
  worktree.

## Required checks

- Focused tests for success and failure exits plus JSON shape.
- Full Alpha-Presale test suite.
- Existing project verification command(s), if safe and local.
- `git diff --check`.
- Exact changed-path allowlist.
- Independent final review with Spec and Standards coverage.

## Fail-closed rules

- Any scope expansion, dirty fixed point, failed gate, invalid review contract,
  blocker/major finding, or missing evidence stops the pilot.
- Even `R17_ACCEPT` does not authorize transfer or commit.

## Checklist

- [x] Durable task packet created.
- [x] Project instructions and CLI structure inspected.
- [x] Clean detached worktree created at fixed source commit.
- [x] Explicit implementation task and acceptance criteria sealed.
- [x] Controlled-manual builder run completed.
- [x] Tests and diff checks recorded.
- [x] Independent review admitted.
- [x] Result and next gate reported.
