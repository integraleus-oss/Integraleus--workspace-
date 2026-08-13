# Evidence

Status: real-project code/gates passed; review transport escalated fail-closed

## Baseline

- Source project: `/home/stanislav/projects/home-agent-factory`
- Baseline commit: `3d9c27e`
- Source worktree was clean at intake.

## Expected artifacts

- isolated worktree and managed run under
  `/home/stanislav/agent-runs/orchestrator-worktrees/`;
- sealed review inputs and policy decisions inside the managed run;
- terminal result, check counts, exact commit/diff, and source-project status.

## Attempt r1

- Packet validation passed and Codex stayed inside the two allowed files.
- Builder stopped before gates/review with `ESCALATED`: direct `npm` and `node`
  programs are not in the accepted gate-program allowlist.
- No result was accepted and the source project remained unchanged.
- r2 uses the already accepted `bash -c` gate program with fixed literal local
  commands; the failed r1 worktree/run are retained as fail-closed evidence.

## Attempt r2

- Packet validation passed against a clean clone of real project
  `home-agent-factory` at `3d9c27e`.
- Codex changed only `src/cli/factory.js` and added `test/cli.test.js`, exactly
  matching the allowlist. The change validates pack slugs before file lookup
  and covers valid list/show plus 14 malformed/traversal forms.
- Observed mandatory gates all passed: Node tests 8/8, `pack list`, `pack show
  private-archive-rag`, and `git diff --check`.
- Review transport exercised the full bounded chain: initial response ->
  format-only retry -> contract-only retry -> contract-repair format-only
  retry. The last exact-JSON candidate contained decoded `U+0009`; strict
  transport rejected it and the managed result was `ESCALATED` after one Codex
  attempt. Policy did not issue acceptance.
- Source project remains clean at `3d9c27e`; no change was copied, committed,
  pushed, or deployed.

## Verdict

The real-project smoke proves change scoping, observed gate execution, sealed
review inputs, bounded retry sequencing, and fail-closed admission. It does not
yet prove a successful terminal policy decision on this project. The next
orchestrator hardening slice should address reviewer-produced decoded control
characters without weakening strict JSON/schema/semantic admission, then rerun
from a fresh clean worktree. Direct `npm`/`node` gate ergonomics are a separate
minor operator improvement; r2 used fixed literal `bash -c` commands already
allowed by the accepted builder.
