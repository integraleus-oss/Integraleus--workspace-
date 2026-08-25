#!/usr/bin/env bash
set -euo pipefail

worktree=/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-v1
minimum=6

output=$(cd "$worktree" && dotnet test tests/AlphaBpr.Tests/AlphaBpr.Tests.csproj --filter 'FullyQualifiedName~Integration' --no-restore 2>&1) || {
  printf '%s\n' "$output"
  exit 1
}
printf '%s\n' "$output"

if grep -Fq 'No test matches' <<<"$output"; then
  printf 'FAIL focused integration filter executed zero tests\n' >&2
  exit 1
fi

passed=$(sed -nE 's/.*Passed:[[:space:]]*([0-9]+).*/\1/p' <<<"$output" | tail -1)
if [[ -z "$passed" || "$passed" -lt "$minimum" ]]; then
  printf 'FAIL expected at least %s focused integration tests, observed %s\n' "$minimum" "${passed:-unknown}" >&2
  exit 1
fi

printf 'PASS focused_integration_tests=%s minimum=%s\n' "$passed" "$minimum"
