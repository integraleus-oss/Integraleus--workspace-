#!/usr/bin/env bash
set -euo pipefail

project_root=${ORCHESTRATOR_PROJECT_ROOT:?missing ORCHESTRATOR_PROJECT_ROOT}
artifact_root=/tmp/orchestrator-dotnet-qualification-artifacts
mode=${1:-}
common=(-m:1 /nodeReuse:false -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root")

case "$mode" in
  restore)
    dotnet restore "$project_root/Qualification.csproj" -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root"
    ;;
  focused)
    dotnet build "$project_root/Qualification.csproj" --no-restore "${common[@]}"
    dll_dir="$artifact_root/bin/Qualification/debug"
    run_expect_success() {
      local fixture_root=$1 expected=$2 output status
      set +e
      output=$(cd "$dll_dir" && ORCHESTRATOR_FIXTURE_ROOT="$fixture_root" dotnet Qualification.dll 2>&1)
      status=$?
      set -e
      printf '%s\n' "$output"
      (( status == 0 )) && grep -Fxq "$expected" <<<"$output"
    }
    run_expect_failure() {
      local fixture_root=$1 output status
      set +e
      if [[ "$fixture_root" == UNSET ]]; then
        output=$(cd "$dll_dir" && env -u ORCHESTRATOR_FIXTURE_ROOT dotnet Qualification.dll 2>&1)
      else
        output=$(cd "$dll_dir" && ORCHESTRATOR_FIXTURE_ROOT="$fixture_root" dotnet Qualification.dll 2>&1)
      fi
      status=$?
      set -e
      printf '%s\n' "$output"
      (( status != 0 ))
    }
    alternate_root="$artifact_root/qualification-fixture-alternate"
    mkdir -p "$alternate_root"
    printf '%s\n' 'broker-qualified-alternate' > "$alternate_root/expected.txt"
    run_expect_success "${ORCHESTRATOR_FIXTURE_ROOT:?missing ORCHESTRATOR_FIXTURE_ROOT}" broker-qualified || exit 1
    run_expect_success "$alternate_root" broker-qualified-alternate || exit 1
    run_expect_failure UNSET || exit 1
    run_expect_failure "$artifact_root/missing-fixture-root" || exit 1
    ;;
  *)
    printf 'usage: %s {restore|focused}\n' "$0" >&2
    exit 2
    ;;
esac
