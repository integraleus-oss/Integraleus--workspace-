# Automatic trusted review-input builder

Status: ACCEPTED
Owner: Stanislav
Risk: MEDIUM — local code, Git inspection, bounded local checks, external model review
Baseline: `c0276c2` (production CLI implementation: `59d42a3`)

## Goal

After each actual Codex attempt, derive the review manifest, projection binding,
evidence index, and run bundle from the observed Git change and gate results.
Bind every generated input with SHA-256 digests so stale, incomplete, tampered,
or out-of-scope evidence fails closed before Claude review or policy admission.

## Boundaries

Allowed:

- this task folder;
- `state/tasks/2026-08-12-orchestrator-integration/` implementation/tests/docs;
- isolated synthetic Git worktrees under the approved local worktree base;
- fixed local Codex/Claude wrappers for the bounded canary/review.

Forbidden:

- unrelated dirty-worktree files;
- Gateway, OpenClaw config, systemd, cron, unattended activation;
- GitHub/push, deploy, automatic commit;
- Synology changes until the implementation is independently closed and
  committed;
- secrets, `.env`, private chats, or Synology content in review packets.

## Checklist

- [x] Create task packet before implementation.
- [x] Implement deterministic Git/diff/gate capture.
- [x] Generate digest-bound manifest, binding, evidence, and bundle.
- [x] Connect generated inputs to production CLI review legs.
- [x] Add tamper, scope, missing-gate, dirty-baseline, and digest tests.
- [x] Run focused and core regressions.
- [x] Run isolated builder canary.
- [x] Independent Standards + Spec closure review and live policy acceptance.
- [x] Scoped local commit and evidence update.
- [x] Create and verify encrypted Synology backup after commit.

## Current review blocker

The accepted policy requires a targeted verification to resolve carried
findings and then a final full review before `R17_ACCEPT`. The current managed
controller has two implementation/review legs only. The next rework must add a
bounded third, review-only final-full leg after the second Codex attempt and
carry a schema-valid prior-attempt record plus prior-findings evidence. Do not
weaken or reset the finding registry to force acceptance.

The three-leg controller and targeted policy path are live-proven. Canary r17
completed attempt 1 REWORK, attempt 2 targeted closure, and one review-only
final-full leg with `R17_ACCEPT`. No third Codex implementation attempt ran.
The contract-repair transport path now has one separately bounded format-only
retry and fail-closed regression coverage; r17's repair response was already
exact JSON, so that fallback was not needed in the accepted live run.

## Acceptance criteria

- The builder observes repository state; Codex/packet prose cannot declare its
  own changed paths or successful checks.
- Baseline must be clean and pinned; changed paths must stay inside an explicit
  allowlist and include no symlinks.
- Every required gate must run, return zero, and have immutable stdout/stderr
  plus exit-code evidence.
- Manifest, binding, evidence index, diff, changed-path list, task/spec, and
  review instructions are digest-bound.
- Any missing file, post-build mutation, digest mismatch, scope escape, or gate
  failure stops before Claude review.
- Existing 58 integration and 84 core tests remain green.

## Blocker behavior

Unknown errors, incomplete gates, mutable inputs, or provenance mismatches are
`ESCALATED`; no acceptance is inferred from missing evidence.

## Commit rule

Commit only this slice after all tests, canary, and independent closure pass.
Leave all pre-existing unrelated changes untouched. No push.
