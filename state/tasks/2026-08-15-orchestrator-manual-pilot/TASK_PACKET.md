# Controlled manual pilot: Codex-Claude orchestrator

Status: COMPLETE — RETURN FOR REWORK; NOT ACTIVATED

## Goal

Run 3–5 bounded real-project tasks in isolated Git worktrees and determine
whether the local orchestrator is safe and reliable for continued manual use.

## Fixed release subject

- Orchestrator commit: `b300207`
- Release tag: `orchestrator-local-cli-r1-2026-08-15`
- Mode: foreground, manual, supervised

## Global boundaries

- Maximum two Codex implementation attempts per task.
- Maximum one Claude final-full review-only leg per task.
- No direct changes to source repositories; disposable detached worktrees only.
- No automatic commit unless an individual passport explicitly permits it.
- No push, deploy, Gateway, OpenClaw config/runtime, cron, systemd, daemon,
  package, firewall, user, auth, Synology, or other system-state changes.
- Stop fail-closed on unknown error, path-boundary breach, missing evidence,
  invalid packet, digest/seal mismatch, exhausted reviewer repair budget,
  timeout, or operator interruption.
- Preserve task inputs, logs, hashes, diffs, gate results, review artifacts,
  policy decision, and terminal state under this task directory.

## Execution checklist

- [x] Pilot task packet created before autonomous work.
- [x] Candidate repositories inventoried at exact commits and dirty state checked.
- [x] Four real tasks provisionally selected and bounded.
- [x] One passport created for each task before launch.
- [x] Success-first-attempt implementation case observed (T01; terminal
  acceptance required a review-only final-full leg).
- [x] Reviewer REWORK followed by bounded Codex handling observed (T02; final
  outcome correctly escalated rather than falsely closed).
- [x] Test/gate failure case observed.
- [x] Known infrastructure failure case observed.
- [x] Unknown error fail-closed case observed.
- [x] Invalid Claude response repair-or-reject case observed (T03 bounded
  contract repair).
- [x] Operator interruption drill observed; structured terminal evidence defect
  recorded.
- [x] Source repository verified unchanged after T02 at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- [x] Final pilot report completed.

## Evidence layout

Each trial will use `trials/<trial-id>/` containing `PASSPORT.md`, immutable
inputs, execution logs, checksums, Git evidence, reviewer artifacts, decision,
and a concise `RESULT.md`. The cross-trial conclusion will be written to
`PILOT_REPORT.md`.

## Current approval boundary

The user message authorizes the controlled manual pilot described here. It does
not authorize autonomous mode or any external/system integration. If a task
would require broader authority, record the blocker and stop that trial.

## Repository inventory at intake

- `/home/stanislav/projects/home-agent-factory` — clean at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`; admitted only through detached
  isolated worktrees.
- `/home/stanislav/projects/alpha-bpr` — HEAD
  `5cfe9a7e316fc2ff002f518f260624069397c79a`, with nine pre-existing modified
  staging files. It is excluded from the initial pilot implementation set to
  avoid ambiguity with owner work. Read-only commit-based inspection remains
  allowed.

## Provisional real-task set

All four tasks target the clean Phase 0 `home-agent-factory` baseline and will
receive separate passports before launch:

1. Harden pack-slug lookup against path traversal and malformed slugs.
2. Harden instance-file lookup against escape from the project root.
3. Validate external-read methods without untyped input causing an uncontrolled
   exception; preserve GET-only fail-closed policy behavior.
4. Harden run-log file naming so an attacker-controlled run ID cannot escape
   its dated audit directory.

Failure drills are separate from task acceptance and may be overlaid on these
runs only through explicit, evidence-preserving harness inputs. A deliberately
failed gate, known-infrastructure classification, unknown-error stop,
invalid-reviewer response, and operator interruption must never be disguised as
a successful task result.
