#!/usr/bin/env bash
set -euo pipefail

worktree=/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-r3
artifact_root=/tmp/alpha-bpr-universal-integration-r3-artifacts
mode=${1:-}
common=(-m:1 /nodeReuse:false -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root")

mkdir -p "$artifact_root"
cd "$worktree"

run_tests() {
  local filter=$1 minimum=$2 label=$3 output passed
  local args=(test tests/AlphaBpr.Tests/AlphaBpr.Tests.csproj --no-restore "${common[@]}")
  if [[ -n "$filter" ]]; then args+=(--filter "$filter"); fi
  if ! output=$(dotnet "${args[@]}" 2>&1); then
    printf '%s\n' "$output"
    return 1
  fi
  printf '%s\n' "$output"
  if grep -Fq 'No test matches' <<<"$output"; then
    printf 'FAIL %s executed zero tests\n' "$label" >&2
    return 1
  fi
  passed=$(sed -nE 's/.*Passed:[[:space:]]*([0-9]+).*/\1/p' <<<"$output" | tail -1)
  if [[ -z "$passed" || "$passed" -lt "$minimum" ]]; then
    printf 'FAIL %s expected at least %s passed tests, observed %s\n' "$label" "$minimum" "${passed:-unknown}" >&2
    return 1
  fi
  printf 'PASS %s=%s minimum=%s\n' "$label" "$passed" "$minimum"
}

case "$mode" in
  restore)
    dotnet restore AlphaBpr.sln -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root" --ignore-failed-sources
    ;;
  focused)
    run_tests 'FullyQualifiedName~Integration' 6 focused_integration_tests
    ;;
  build)
    dotnet build AlphaBpr.sln --no-restore "${common[@]}"
    ;;
  full)
    run_tests '' 346 full_regression_tests
    ;;
  *)
    printf 'usage: %s {restore|focused|build|full}\n' "$0" >&2
    exit 2
    ;;
esac
