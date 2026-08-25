#!/usr/bin/env bash
set -euo pipefail

report="docs/evidence/TRIZ-P3-PROOF-SUMMARY.md"
test -f "$report"
actual_status="$(git status --porcelain --untracked-files=all | sort)"
expected_status="$(printf '%s\n' \
  '?? docs/evidence/TRIZ-P3-PROOF-SUMMARY.md' | sort)"
if [[ "$actual_status" != "$expected_status" ]]; then
  printf 'scope mismatch\nexpected:\n%s\nactual:\n%s\n' \
    "$expected_status" "$actual_status" >&2
  exit 20
fi
rg -q 'Source: heuristic-analogy' "$report"
rg -q 'fixture proof is not a connected Alpha Platform test' "$report"
rg -q 'PASS' "$report"
rg -q 'PARTIAL' "$report"
rg -q 'NOT TESTED' "$report"
rg -q 'human confirmation|engineer confirmation|инженер.*подтверж' "$report"
git diff --check
