# Controlled manual pilot report

Status: COMPLETE — RETURN FOR REWORK; NOT ACTIVATED

## Executive conclusion

Four bounded real tasks were processed in isolated detached worktrees. Three
reached terminal acceptance and one correctly escalated after the permitted
two implementation attempts. Failure drills confirmed fail-closed handling of
gates, known infrastructure, unknown failures, and invalid reviewer responses.
The manual-interruption drill stopped execution but exposed missing structured
terminal evidence. The pilot therefore does not meet every exit criterion and
the orchestrator must return for bounded rework. It remains not activated.

## Trial results

- T01 pack slug: `ACCEPTED / R17_ACCEPT`; one Codex implementation plus a
  review-only final-full leg. See `trials/T01-pack-slug/RESULT.md`.
- T02 instance path: `ESCALATED / R12_FINDINGS_EXHAUSTED`; two Codex
  implementation attempts used. This is a fail-closed pilot outcome, not an
  accepted implementation. See `trials/T02-instance-path/RESULT.md`.
- T03 external-read methods: `ACCEPTED / R17_ACCEPT`; one Codex
  implementation, bounded Claude contract repair, and review-only final-full
  leg. See `trials/T03-external-methods/RESULT.md`.
- T04 run-log identifier: `ACCEPTED / R17_ACCEPT`; one Codex implementation
  and review-only final-full leg. See `trials/T04-run-log-id/RESULT.md`.

## Defects found

- T02 evidence carry is lossy: `prior-findings.json` retained only IDs and open
  statuses, so the next reviewer could not re-verify earlier findings from
  sealed evidence.
- `Ctrl-C` is not converted into a structured `INTERRUPTED` terminal result.
  The CLI exits with an unhandled traceback and retains only partial evidence.
- The original foreground operator session ended after T02 without updating
  the report; status temporarily drifted from actual sealed evidence.

## Residual risks

- A rework attempt cannot reliably prove closure while prior finding details
  are omitted from the sealed carry-forward artifact.
- Operator interruption stops work but does not yet provide a complete audit
  trail or explicit terminal state.
- Real task changes exist only in disposable worktrees and were not committed
  or integrated; they are pilot evidence, not product changes.

## Recommendation

Return for bounded rework. Preserve manual-only and foreground-only operation;
do not connect to OpenClaw, Gateway, cron, systemd, daemon, or unattended mode.
Fix both defects, add regression tests, repeat the T02 re-verification and live
operator-interruption drills, and issue a new explicit readiness decision only
after both produce complete sealed evidence.

## Safety and verification

- Original `home-agent-factory` remained clean at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- All observed task changes stayed inside passport allowlists and detached
  worktrees.
- Full orchestrator integration suite: 86/86 passed.
- No commit, push, deploy, Gateway, OpenClaw runtime/config, cron, systemd,
  daemon, package, firewall, auth, Synology, or other system-state change.
