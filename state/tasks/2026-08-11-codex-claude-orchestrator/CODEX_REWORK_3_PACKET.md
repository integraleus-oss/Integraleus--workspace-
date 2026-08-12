# Codex Rework 3 Packet: Unhashable Trusted Values

Status: READY
Owner: Stanislav
Coordinator: OpenClaw main
Implementer: fresh local Codex, workspace-write sandbox

## Goal

Close the two remaining crash paths identified by the final targeted Claude
review without expanding the reviewer contract or policy authority.

## Inputs

- `reviews/claude-final-targeted.md`
- current `implementation/`

## Allowed files

Edit only under
`state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`.
Do not commit or edit task/review/shared/config files.

## Confirmed source-level failures

1. A prior finding with JSON `"status": []` reaches set membership and raises
   `TypeError: unhashable type: 'list'`.
2. Trusted-manifest `expected_review_mode: []` or
   `expected_coverage_scope: []` reaches set membership and raises the same
   exception.

## Required fixes

- Type-check each raw JSON value before set membership or other operations that
  assume a scalar/hashable value.
- Audit the new trusted-manifest and prior-findings structure validators for the
  same unhashable/container-value pattern and close equivalent branches locally.
- Add exact subprocess/CLI regression tests for both confirmed inputs. Require
  exit 2, empty stderr, exactly one JSON stdout object, `tool_input_failure`,
  and the specific `prior_findings_invalid` or `trusted_manifest_invalid` code.
- Preserve all 20 existing tests, valid initial/targeted/full-review behavior,
  and the 0/1/2 exit contract.
- Update README/EVIDENCE with exact results.

## Acceptance criteria

- AC-R3-01: Both confirmed inputs fail closed without traceback.
- AC-R3-02: Equivalent container values in trusted enum/status fields cannot
  raise uncaught exceptions.
- AC-R3-03: Full suite, schema self-check, py_compile, fixture expectations, and
  whitespace checks pass.
- AC-R3-04: No new acceptance/resolution/approval authority.
- AC-R3-05: No file outside `implementation/` changed; no commit.
