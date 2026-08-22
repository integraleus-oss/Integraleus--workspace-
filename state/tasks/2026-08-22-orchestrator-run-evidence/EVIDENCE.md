# Automatic RUN_EVIDENCE evidence

Status: REVIEW_BLOCKED
Implementation commit: `3d8ed15c`
Baseline: `9f8cf849`

## Delivered

- Versioned schema `1.0.0` with `start`, `agent_launch`, `changed_paths`,
  `gate`, `review`, and `terminal` events.
- Monotonic sequence and SHA-256 event hash chain.
- Exclusive, no-follow creation; append locking, flush and fsync; validation of
  the complete existing stream before each append.
- A single terminal event seals the stream.
- Terminal preservation for normal, error, and interrupted lifecycle paths.
- Evidence payload validation rejects secret-like keys and non-JSON values.
- Managed-cycle compatibility accepts only the exact regular evidence file in
  a pre-created run directory and otherwise retains the clean-root guard.

## Verification

- Red test: missing writer failed with `ModuleNotFoundError` before implementation.
- Focused suite: `55 passed`.
- Full orchestrator suite: `184 passed in 19.627s`.
- `git diff --check`: PASS.
- Scoped commit: `3d8ed15c feat: add automatic orchestrator run evidence`.
- Push and deploy: not performed.

## Review gate

The implementation is not accepted for production use yet. Independent review
attempts did not produce a usable terminal verdict:

- Claude read-only wrapper: empty result.
- Codex staged-diff and commit review: inspected the slice but emitted no final
  verdict.
- Claude commit-diff wrapper: empty result.
- Local Qwen bounded review: did not terminate with a verdict and was stopped.

These are review-transport failures, not PASS results. The provisional commit
keeps the exact reviewed candidate reproducible. It must not be pushed,
deployed, or used to qualify Alpha BPR until an independent review returns
`0 blocker / 0 major` and the closure tests are rerun.

## Scope audit

Only the six implementation/test files in commit `3d8ed15c` were changed.
Pre-existing unrelated untracked workspace files were left untouched. Alpha
BPR, `home-agent-factory`, Gateway, auth, Synology, cron, push, and deploy were
not changed.
