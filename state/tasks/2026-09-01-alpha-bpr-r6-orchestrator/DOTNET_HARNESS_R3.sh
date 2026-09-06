#!/usr/bin/env bash
set -euo pipefail

expected_project=/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-r6-continuation-r3
expected_fixture="$expected_project"
expected_artifact=/tmp/alpha-bpr-r6-orchestrator-artifacts
project_root=${ORCHESTRATOR_PROJECT_ROOT:?missing ORCHESTRATOR_PROJECT_ROOT}
fixture_root=${ORCHESTRATOR_FIXTURE_ROOT:?missing ORCHESTRATOR_FIXTURE_ROOT}
artifact_root=${ORCHESTRATOR_ARTIFACT_ROOT:?missing ORCHESTRATOR_ARTIFACT_ROOT}
mode=${1:-}

[[ "$project_root" == "$expected_project" && "$fixture_root" == "$expected_fixture" && "$artifact_root" == "$expected_artifact" ]] || exit 2
[[ -d "$project_root" && "$artifact_root" == /tmp/* ]] || exit 2

common=(-m:1 /nodeReuse:false -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root")
export NUGET_PACKAGES="$artifact_root/nuget-packages"
export NUGET_HTTP_CACHE_PATH="$artifact_root/nuget-http-cache"
export NUGET_SCRATCH="$artifact_root/nuget-scratch"

case "$mode" in
  restore)
    dotnet restore "$project_root/AlphaBpr.sln" -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root" --ignore-failed-sources
    ;;
  build)
    dotnet restore "$project_root/AlphaBpr.sln" -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root" --ignore-failed-sources
    dotnet build "$project_root/AlphaBpr.sln" --no-restore "${common[@]}"
    ;;
  unit)
    dotnet restore "$project_root/AlphaBpr.sln" -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root" --ignore-failed-sources
    dotnet test "$project_root/tests/AlphaBpr.Tests/AlphaBpr.Tests.csproj" --no-restore "${common[@]}" --filter 'FullyQualifiedName~RecipeTests'
    ;;
  integration)
    dotnet restore "$project_root/AlphaBpr.sln" -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root" --ignore-failed-sources
    dotnet test "$project_root/tests/AlphaBpr.IntegrationTests/AlphaBpr.IntegrationTests.csproj" --no-restore "${common[@]}" --filter 'FullyQualifiedName~RecipeMasterDataPinning|FullyQualifiedName~MasterDataOntologyEvidenceCodec|FullyQualifiedName~GovernedMasterDataTransition|FullyQualifiedName~GovernedMasterDataUi'
    ;;
  names)
    if rg -n 'Alpha\.Alarms 3\.30|Alpha\.Trends 3\.33' "$project_root/src" "$project_root/tests"; then exit 1; fi
    ;;
  *) exit 2 ;;
esac
