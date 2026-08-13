# Orchestrator real-project smoke: Home Agent Factory

Status: FAIL_CLOSED_REVIEW_TRANSPORT
Owner: Stanislav
Risk: MEDIUM — isolated local code change and external model review; no deploy
Source project: `/home/stanislav/projects/home-agent-factory`
Baseline: `3d9c27e`

## Goal

Exercise the accepted production orchestrator on a real local project by
closing one narrow CLI path-boundary defect: pack slugs must not escape the
project's `agent-packs/` directory. Add deterministic regression coverage and
preserve current valid `pack list`, `pack show`, and policy behavior.

## Boundaries

Allowed in the isolated worktree only:

- `src/cli/factory.js`;
- `test/cli.test.js`;
- existing tests may be read but not rewritten.

Forbidden:

- source project working tree changes;
- `.env`, private archives, Synology data, secrets, run logs;
- dependency installation or lockfile changes;
- commit, push, deploy, Gateway/config, cron, or service actions;
- automatic activation after the smoke.

## Checks

- `npm test`;
- `node ./src/cli/factory.js pack list`;
- `node ./src/cli/factory.js pack show private-archive-rag`;
- `git diff --check`.

## Acceptance

- traversal-like slugs such as `../...` cannot read JSON outside
  `agent-packs/<slug>/agent-pack.json`;
- valid pack commands still work;
- all checks pass from observed worktree state;
- trusted review inputs are sealed and deterministic policy returns acceptance;
- no more than two Codex attempts and one review-only final-full leg.

## Rollback

Delete the isolated worktree and run directory. The source project must remain
at baseline `3d9c27e` with its original status.

## Checklist

- [x] Task packet created.
- [x] Clean isolated worktree created and packet validated.
- [x] Full managed CLI smoke completed fail-closed; no acceptance inferred.
- [x] Source project unchanged.
- [x] Evidence and retention/rollback notes recorded.
- [ ] Commit decision made only after acceptance.
