# Alpha BPR Track F release audit R2 — result

Status: `ESCALATED / NONDETERMINISTIC_AUDIT_HARNESS`

## Cycle outcome

- Sealed packet: `sha256:11dd458bf6d6033ba34b9ea60c5f015b9a2897a08c3511a908b418bbea08d192`
- Baseline: `b9e637754c5b00f38fd09f5949c971afd12db7a1`
- Profile: `standard`
- Attempts used: 2 of 2
- Review 1: 0 blocker, 1 major, 2 nit; outcome `REWORK`
- Attempt 2: the selected major was corrected, then the repeat `audit-harness` gate failed before closure review
- Formal terminal status: `ESCALATED / policy_or_runtime_escalation`

## Root cause

The harness stores the full tar listing in a shell variable and checks required
entries with `printf | grep -q` while `set -o pipefail` is active. When `grep`
finds a match early it can close the pipe, causing `printf` to receive SIGPIPE;
the pipeline is then treated as failure. The same immutable bundle and harness
subsequently produced one failure and two passes in three consecutive reruns.
This is a nondeterministic harness defect, not evidence that an archive entry is
missing.

## Produced audit result

- Exactly three allowed files exist under worktree-root `audit-output/`.
- Combined digest of the three per-file SHA-256 records:
  `97349e91b94762f384a924555c2022841854b625f4eadbd991744860e8739912`
- Audit verdict: `DEFER`.
- Blockers: none.
- Main defers: exact-artifact lifecycle was not directly rehearsed; Windows,
  VirtualBox, VMware, Intel macOS, ARM64 and Apple Silicon routes are not proven;
  external pilot evidence and protected license activation remain outside scope.
- The rework explicitly classifies appliance/SSH hardening claims as direct,
  documented, or not directly verified.

## Safety and repository state

- Canonical `/home/stanislav/projects/alpha-bpr` remained clean.
- Isolated worktree contains only the three permitted untracked audit outputs.
- `git diff --check`: PASS.
- No commit, transfer, push, deploy, VM operation, service change, Gateway
  change, system configuration change, or artifact modification was performed.

## Admission

The audit outputs are not accepted for transfer because the required independent
closure review did not run. A fresh bounded closure packet must first replace
the nondeterministic membership checks with deterministic checks and then run
the gates plus one closure review without another implementation pass.
