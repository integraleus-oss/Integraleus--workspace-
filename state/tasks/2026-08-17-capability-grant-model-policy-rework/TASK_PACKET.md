# Capability-grant modelPolicy REWORK

Status: ESCALATED — FINAL REVIEW TRANSPORT FAILURE; TRANSFER FORBIDDEN
Risk: MEDIUM

## Goal

Resolve the admitted runtime/schema findings without changing the business
semantics of the capability grant:

- original blocker `fnd_c5c661cd771ca41e0fcb9340cd95464e` for `modelPolicy`;
- follow-up major `fnd_02b20f15ce146299ddb87dfefa82e255` for non-string
  `runId` and `packSlug`.

## Fixed subject

- Worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/manual-pilot-001-capability-grant`
- Base/source: `8985b8e95427c471662562afa1b89a9e5b17a6a0`
- Pre-REWORK diff SHA-256: `98f3f457cfdb83fb97f6e1af97a0c13ad57774891187a675537ac891b7dccf51`
- Allowed files: `src/core/policy.js`, `schemas/capability-grant.schema.json`, `test/policy.test.js`

## Boundaries

- Fix admitted blocker/major findings only; do not silently expand into the
  advisory nits.
- No source transfer, source commit, push, deploy, Gateway, systemd, or cron.
- Preserve existing external-read, model selection, approval, and immutability behavior.
- Unsupported `modelPolicy.default` and `allowCloudWithPrivateData` values must fail with controlled `PolicyError` before a grant is emitted.
- Non-string `runId` and `pack.slug` must fail with controlled `PolicyError`
  before a grant is emitted.

## Acceptance

- Red-capable regression proves request precedence cannot hide an invalid pack policy.
- Every emitted grant satisfies the schema-derived contract.
- Full tests and `git diff --check` pass.
- Fresh sealed review returns an admitted terminal policy decision.

## Checklist

- [x] Task packet
- [x] Red regression
- [x] Runtime fix
- [x] Full tests
- [x] Fresh sealed initial and targeted reviews
- [x] Policy-required final-full review attempted
- [x] Evidence and handoff
- [ ] Admitted terminal acceptance
