# Claude Audit: Agent Workflow Rollout Plan v2

Verdict: GO

Scope: read-only review of `PLAN_V2.md` against `CLAUDE_AUDIT.md` and the live workspace.

Claude verified:

- all 15 canonical rule files exist;
- `projects/` contains `alpha-bot`, `humanlike-agent`, `openclaw-shared-memory`, `presentations`, `rag-pipeline`;
- there is no local `projects/spectech-sites`;
- `templates/` does not exist yet;
- no files were changed by Claude.

## Closure Check

| v1 finding | Status in v2 |
|---|---|
| Risk never defined | Addressed: LOW/MEDIUM/HIGH tiers with concrete triggers and minimum artifacts |
| Packet as exfiltration channel | Addressed: external send definition, forbidden contents, minimal safe packet, `SECURITY_PRECHECK` |
| Cron/background not barred | Addressed: autonomous agent ceiling and per-job owner/timeout/kill-switch |
| Protected-file list stale | Addressed: canonical files enumerated, cron barred from changing them |
| No reconciliation with AGENT-RULES | Addressed: existing rules remain source of truth |
| Phantom `spectech-sites` path | Addressed: moved to discovery track |
| Secrets/prod per-project only | Addressed: global boundary added |
| Web prompt-injection | Addressed: web/tool content treated as untrusted input |
| No fast-path artifact | Addressed: `TASK_NOTE.md` |
| Phase 1 mostly blocked | Addressed: narrowed to Shared Memory; NAS and Sites deferred |
| No change control | Addressed: change-control section added |

## Blockers

None. Claude says v2 is ready to use as the basis for Phase 0 template creation.

## Important Fixes Before Phase 0 Execution

1. Decide template home.
   - `templates/` does not exist.
   - Claude recommends `templates/agent-workflow/`.

2. Reconcile template inventory.
   - Phase 0 creates 7 templates.
   - Later tracks reference `PLAN.md`, `TODO.md`, `REPORT.md`, `PRECHECKS.md`, `MIGRATION_CHECKLIST.md`.
   - Either add those templates or mark them as generated per-track, not Phase 0.

3. Confirm gating approvals.
   - Need explicit approval of v2 direction before Phase 0.
   - Authority model can wait until after pilot because Phase 0 does not edit canonical rules.

## Nice-To-Have Improvements

- Make MEDIUM review escalation more objective.
  - Example: any privacy-sensitive project requires review.

- Define a concrete cron kill-switch mechanism.

- Add a note that LOW becomes MEDIUM/HIGH if private data or external send appears.

## Residual Risks

- External-review self-test: sending packets to Claude/Codex is itself external send, so `SECURITY_PRECHECK.md` must be strong.
- Tier assignment is still judgment-based and will need dogfooding.
- Authority ambiguity remains acceptable for draft, but must be resolved before canonical-rule migration.

## Recommended Next Step

Proceed to Phase 0 after Stanislav approves v2 direction:

1. Fix template home to `templates/agent-workflow/`.
2. Create the 7 templates, prioritizing `SECURITY_PRECHECK.md` and `TASK_PACKET.md`.
3. Run one harmless LOW/MEDIUM dry test.
4. Then use the process on the Shared Memory pilot.

Canonical-rule edits and the final authority-model decision should wait until after the pilot.
