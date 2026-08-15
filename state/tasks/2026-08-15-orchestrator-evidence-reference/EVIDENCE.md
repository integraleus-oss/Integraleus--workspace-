# Evidence: reviewer evidence-reference discipline

## Implementation

- Added explicit evidence-reference guidance to every initial and bounded retry
  prompt. References must resolve to evidence objects carried by the same
  verdict; dangling references are removed rather than supported by fabricated
  evidence.
- Added evidence-object guidance: any `artifact_ref` requires its verified
  `content_digest`; missing digests must not be guessed.
- Removed transport ambiguity: reviewers must replace line breaks/tabs with
  printable separators/spaces and must not use JSON `\\n`/`\\t` escapes.
- Routed transport-invalid verdicts through the existing bounded contract repair
  by obtaining the validator report before parsing for ID normalization. Strict
  validation remains unchanged.

## Deterministic regression evidence

- Focused live-review suite: 15/15 PASS.
- Integration suite: 86/86 PASS.
- Accepted core contract/policy suite: 84/84 PASS.
- Regressions cover:
  - dangling evidence reference rejected, reported, and removed on bounded retry;
  - decoded `U+0009` on the initial verdict rejected and repaired through the
    bounded path;
  - `artifact_ref` without `content_digest` rejected and repaired;
  - retry prompts inherit transport, reference, and digest guidance.

## Real-project smoke sequence

- r5 failed closed on initial decoded `U+0009`, exposing that the old guidance
  was ambiguous and transport failure bypassed contract retry.
- r6 passed transport/reference checks, then failed closed on missing artifact
  digests after schema repair.
- r7 reproduced the target dangling-reference failure, repaired it successfully,
  reached policy `REWORK`, then stopped because the second Codex leg added one
  reviewer-requested test path outside the original two-file allowlist.
- r8 explicitly allowed that single test path. Both initial-full and final-full
  verdicts passed strict transport/schema/semantic validation with zero errors.
  Managed chain:
  - attempt 1: one Codex implementation leg, policy `R15_NEED_FULL_REVIEW`;
  - attempt 3: `SKIPPED_REVIEW_ONLY`, policy `R17_ACCEPT`;
  - terminal status: `ACCEPTED`.

Retained run:
`/home/stanislav/agent-runs/orchestrator-worktrees/home-agent-factory-real-smoke-r8-run`

## Boundary

- `/home/stanislav/projects/home-agent-factory` remains clean at `3d9c27e`.
- Smoke application changes remain only in detached worktrees; they were not
  copied, committed, pushed, or deployed to the source project.
- No Gateway, cron, deployment, or external production state was changed.
