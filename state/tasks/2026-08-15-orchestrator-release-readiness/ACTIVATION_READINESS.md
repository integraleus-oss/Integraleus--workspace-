# Activation readiness: Codex-Claude local CLI

Status: **READY FOR CONTROLLED MANUAL PILOT; NOT ACTIVATED**

## Release subject

The release subject is the local CLI implementation under
`state/tasks/2026-08-12-orchestrator-integration/`, including deterministic
policy admission, trusted review inputs, bounded Codex/Claude launches, strict
transport/schema/semantic validation, and review-only final-full handling.

## Manual invocation boundary

- Run only from an explicit task packet using the production-cycle entrypoint
  documented by the implementation README.
- The project root and run root must be explicit absolute paths.
- The project must be a separately approved local Git repository or isolated
  worktree.
- Every task must declare allowed paths, deterministic gates, timeouts, task
  policy, reviewer instructions, and evidence destination.
- Invocation remains manual and supervised. This packet does not authorize a
  Gateway hook, cron job, systemd service, webhook, queue consumer, or daemon.

## Repository allowlist

Default: deny all repositories.

A repository is admitted only per task when its packet records:

1. exact canonical project path and current commit;
2. owner-approved goal and allowed paths;
3. forbidden paths and external-state boundaries;
4. test/gate commands with fixed argv and timeouts;
5. commit/no-commit and push/deploy rules.

For the initial pilot, use disposable fixtures or isolated worktrees. The clean
source `/home/stanislav/projects/home-agent-factory` is not automatically
allowlisted and must not be modified merely because it was used as a smoke
subject.

## Budgets

- Codex implementation legs: maximum 2.
- Review-only final-full leg: maximum 1 and no implementation edit.
- Reviewer transport/format repair: existing bounded implementation limit only.
- Reviewer contract/semantic repair: existing bounded implementation limit only.
- Per-agent timeout: declared by the task packet; recommended pilot ceiling
  600 seconds.
- Gate timeout: declared per gate; recommended pilot ceiling 120 seconds.
- Unknown or repeated infrastructure failures fail closed; no unbounded retry.

## Kill switch

Because the pilot is manual, the primary kill switch is termination of the
foreground controller process. Before any later supervised integration, define
and verify a separate enable flag plus a documented stop command. Absence of
that flag must mean disabled. No such integration is enabled by this release.

On interruption:

1. stop the foreground controller;
2. preserve the run directory and logs;
3. inspect the isolated worktree without merging it;
4. record terminal state as interrupted/ESCALATED rather than ACCEPTED;
5. do not deploy, push, or continue automatically.

## Logs and evidence

Each run must retain:

- immutable task input and prompt digests;
- Codex/Claude launch result, exit code, timeout, and stdout/stderr digests;
- observed Git diff and gate results;
- trusted manifest, projection binding, reviewer verdict, policy inputs;
- deterministic decision, rule ID, budgets, and terminal cycle result;
- exact source commit and isolated worktree/run paths.

Logs must exclude secrets, `.env`, credentials, session files, raw private chat,
and raw Synology contents. External review remains a separate data-transfer
boundary.

## Stop conditions

Stop and preserve evidence without further implementation when any of these
occurs:

- `ESCALATED` or an unknown/repeated infrastructure failure;
- path outside the declared allowlist;
- dirty or changed source boundary not accounted for by the task packet;
- invalid task packet, missing evidence, digest mismatch, or seal mismatch;
- reviewer output still invalid after its bounded repair budget;
- timeout, operator interruption, suspected secret exposure, deploy/push need,
  or requirement for Gateway/cron/runtime/config changes.

`ACCEPTED / R17_ACCEPT` authorizes only the scoped local task result. It does
not authorize merging, committing, pushing, deploying, activation, or risk
acceptance unless the task packet explicitly and separately permits it.

## Controlled pilot matrix

Before requesting supervised OpenClaw integration, complete and retain evidence
for at least these manual cases:

1. clean one-leg acceptance;
2. genuine reviewer REWORK followed by bounded closure;
3. deterministic test/gate failure;
4. allowlisted known infrastructure failure and unknown-infra fail-closed case;
5. invalid reviewer transport/contract output repaired or terminally rejected;
6. operator kill-switch/interruption drill.

Recommended promotion gate: 3-5 representative real tasks with no boundary
violation, plus the failure cases above. Any Gateway, cron, daemon, unattended
mode, automatic commit, push, or deploy requires a new explicit approval.

## Current evidence

- Commit `48c85c3` closes reviewer evidence-reference discipline.
- Real-project smoke r8 ended `ACCEPTED / R17_ACCEPT` with a review-only
  final-full leg and no third Codex implementation attempt.
- The integration suite passed 86/86 on 2026-08-15 immediately before this
  readiness packet was prepared.
