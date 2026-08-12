# Codex Rework 2 Packet: Trusted Input Closure

Status: READY
Owner: Stanislav
Coordinator: OpenClaw main
Implementer: fresh local Codex, workspace-write sandbox

## Goal

Close the three locally reproduced major findings from targeted verification.

## Inputs

- `reviews/claude-targeted-reverification.md`
- current `implementation/` files

## Allowed files

Edit only under
`state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`.
Do not commit or edit task/review/shared/config files.

## Confirmed failures

1. Incomplete manifest `{"document_type":"trusted_review_manifest"}` accepts
   an otherwise valid document (`contract_valid: true`).
2. Malformed prior findings with `"findings": 5` raises uncaught `TypeError`.
3. A targeted document changed to `review_mode=final_full` and
   `coverage_scope=full` bypasses the required prior-findings binding.

## Required fixes

- Strictly validate trusted-manifest structure and completeness before using
  it: required subject keys, acceptance/instruction digests, non-empty unique
  criteria records, and expected review mode/coverage scope supplied by the
  coordinator and compared to the reviewer document.
- Strictly validate prior-findings structure/types/uniqueness/status values.
  Malformed trusted input must yield one machine-readable JSON result and exit
  2, never traceback or empty stdout.
- Require and validate prior findings whenever the document contains a
  verification block or expected mode is targeted; eliminate reviewer-chosen
  mode bypass and avoid false mismatch for legitimate full-review documents.
- Add exact regression tests for all three confirmed inputs. Assertions must
  require the specific error code, not accept generic schema failure as an
  alternative.
- Preserve all 16 existing tests and documented 0/1/2 exit contract.
- Update README/EVIDENCE with exact results and remaining limitations.

## Acceptance criteria

- AC-R2-01: All three confirmed reproductions fail closed with specific codes.
- AC-R2-02: Malformed trusted input returns exit 2 and one JSON object.
- AC-R2-03: Valid initial and targeted fixtures still pass with complete trusted
  inputs.
- AC-R2-04: Full test suite, schema self-check, py_compile, fixture expectations,
  and whitespace checks pass.
- AC-R2-05: No file outside `implementation/` changed; no commit.
