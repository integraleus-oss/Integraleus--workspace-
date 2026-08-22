# Automatic RUN_EVIDENCE evidence

Status: ACCEPTED
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

- Initial independent review: REWORK, 2 major. It found run-root creation race
  risks and possible masking of the original interrupt/error.
- Closure review found a false `REWORK` evidence event on non-repairable builder
  failures; this was corrected and pinned with an escalation-path test.
- Terminal-evidence diagnostic was hardened so neither evidence failure nor a
  broken stderr can replace the original exception.
- Final independent closure review: ACCEPTED, 0 blocker, 0 major.
- Final focused closure: `57 passed`.
- Final full orchestrator suite: `186 passed in 19.853s`.
- Final `git diff --check`: PASS.

Implementation and closure commits: `3d8ed15c`, `217daab5`, `3168c0a4`,
`3d60ce70`, `c4823ff8`, `3d2857c5`. No push or deploy was performed.

## Scope audit

Only the six implementation/test files in commit `3d8ed15c` were changed.
Pre-existing unrelated untracked workspace files were left untouched. Alpha
BPR, `home-agent-factory`, Gateway, auth, Synology, cron, push, and deploy were
not changed.
