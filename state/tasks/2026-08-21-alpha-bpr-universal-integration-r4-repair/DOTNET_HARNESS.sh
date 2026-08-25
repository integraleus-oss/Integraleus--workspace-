#!/usr/bin/env bash
set -euo pipefail

expected_project=/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-universal-integration-r4-repair
expected_fixture="$expected_project"
expected_artifact=/tmp/alpha-bpr-universal-integration-r4-repair-artifacts
project_root=${ORCHESTRATOR_PROJECT_ROOT:?missing ORCHESTRATOR_PROJECT_ROOT}
fixture_root=${ORCHESTRATOR_FIXTURE_ROOT:?missing ORCHESTRATOR_FIXTURE_ROOT}
artifact_root=${ORCHESTRATOR_ARTIFACT_ROOT:?missing ORCHESTRATOR_ARTIFACT_ROOT}
mode=${1:-}

[[ "$project_root" == "$expected_project" && "$fixture_root" == "$expected_fixture" && "$artifact_root" == "$expected_artifact" ]] || {
  printf 'FAIL sealed execution context mismatch\n' >&2
  exit 2
}
[[ -d "$project_root" && -d "$fixture_root" && "$artifact_root" == /tmp/* ]] || exit 2

common=(-m:1 /nodeReuse:false -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root")
export NUGET_PACKAGES="$artifact_root/nuget-packages"
export NUGET_HTTP_CACHE_PATH="$artifact_root/nuget-http-cache"
export NUGET_SCRATCH="$artifact_root/nuget-scratch"

run_tests() {
  local filter=$1 minimum=$2 label=$3 output passed status
  local args=(test "$project_root/tests/AlphaBpr.Tests/AlphaBpr.Tests.csproj" --no-restore "${common[@]}")
  [[ -z "$filter" ]] || args+=(--filter "$filter")
  set +e
  output=$(dotnet "${args[@]}" 2>&1)
  status=$?
  set -e
  printf '%s\n' "$output"
  (( status == 0 )) || return 1
  grep -Fq 'No test matches' <<<"$output" && return 1
  passed=$(sed -nE 's/.*Passed:[[:space:]]*([0-9]+).*/\1/p' <<<"$output" | tail -1)
  [[ -n "$passed" && "$passed" -ge "$minimum" ]] || {
    printf 'FAIL %s expected at least %s passed tests, observed %s\n' "$label" "$minimum" "${passed:-unknown}" >&2
    return 1
  }
  printf 'PASS %s=%s minimum=%s\n' "$label" "$passed" "$minimum"
}

case "$mode" in
  restore) dotnet restore "$project_root/AlphaBpr.sln" -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root" --ignore-failed-sources ;;
  focused) run_tests 'FullyQualifiedName~Integration' 20 focused_integration_tests ;;
  build) dotnet build "$project_root/AlphaBpr.sln" --no-restore "${common[@]}" ;;
  baseline) run_tests '' 353 baseline_regression_tests ;;
  full) run_tests '' 360 full_regression_tests ;;
  *) printf 'usage: %s {restore|focused|build|baseline|full}\n' "$0" >&2; exit 2 ;;
esac
