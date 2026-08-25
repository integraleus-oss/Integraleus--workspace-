#!/usr/bin/env bash
set -euo pipefail

fixture=/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-21-orchestrator-dotnet-sandbox-regression/fixture
artifact_root=/tmp/openclaw-orchestrator-dotnet-regression-artifacts

mkdir -p "$artifact_root"
dotnet build "$fixture/Probe.csproj" -m:1 /nodeReuse:false \
  -p:UseArtifactsOutput=true -p:ArtifactsPath="$artifact_root"
output=$(dotnet "$artifact_root/bin/Probe/debug/Probe.dll" 2>&1)
printf '%s\n' "$output"
[[ "$output" == *"sandbox-pass"* ]] || {
  printf 'FAIL expected sandbox-pass\n' >&2
  exit 1
}
printf 'PASS external_artifact_root=%s\n' "$artifact_root"
