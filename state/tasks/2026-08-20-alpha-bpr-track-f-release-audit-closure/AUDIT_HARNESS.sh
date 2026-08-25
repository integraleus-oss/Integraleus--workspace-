#!/usr/bin/env bash
set -euo pipefail

project=/home/stanislav/projects/alpha-bpr
worktree=/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-track-f-release-audit-r2
bundle="$project/dist/track-f-complete-offline/Alpha_BPR_Track_F_Complete_Offline_Candidate_v1.tar.zst"
ova="$project/dist/track-f-complete-offline/appliance/Alpha_BPR_Track_F_Appliance_v1.ova"
baseline=b9e637754c5b00f38fd09f5949c971afd12db7a1

fail() { printf 'FAIL %s\n' "$*"; exit 1; }
pass() { printf 'PASS %s\n' "$*"; }

test "$(git -C "$worktree" rev-parse HEAD)" = "$baseline" || fail 'isolated baseline mismatch'
test -z "$(git -C "$project" status --short)" || fail 'canonical alpha-bpr worktree is dirty'
(cd "$(dirname "$bundle")" && sha256sum -c "$(basename "$bundle").sha256") >/dev/null || fail 'bundle SHA-256 mismatch'
(cd "$(dirname "$ova")" && sha256sum -c "$(basename "$ova").sha256") >/dev/null || fail 'OVA SHA-256 mismatch'
zstd -q -t "$bundle" || fail 'bundle zstd integrity'
tar --zstd -tf "$bundle" >/dev/null || fail 'bundle tar readability'
tar -tf "$ova" >/dev/null || fail 'OVA tar readability'

bundle_names=$(tar --zstd -tf "$bundle")
for expected in README.md preflight.sh install.sh start.sh smoke.sh remove.sh; do
  grep -Eq "(^|/)$expected$" <<<"$bundle_names" || fail "bundle missing $expected"
done

ova_names=$(tar -tf "$ova")
grep -Eq '\.ovf$' <<<"$ova_names" || fail 'OVA missing OVF descriptor'
grep -Eq '\.(vmdk|vdi)$' <<<"$ova_names" || fail 'OVA missing virtual disk'

combined_names=$(printf '%s\n%s\n' "$bundle_names" "$ova_names")
if grep -Eiq '(^|/)(id_rsa|id_ed25519|.*\.pem|.*\.key|license.key|secrets?\.json|\.env)(/|$)' <<<"$combined_names"; then
  fail 'suspicious secret-bearing filename in artifact listing'
fi

for output in ORCHESTRATOR_AUDIT.md EVIDENCE.md VERDICT.json; do
  test -s "$worktree/audit-output/$output" || fail "missing audit-output/$output"
done
python3 -m json.tool "$worktree/audit-output/VERDICT.json" >/dev/null || fail 'VERDICT.json invalid'

unexpected=$(git -C "$worktree" status --porcelain --untracked-files=all | awk '{print $2}' | grep -Ev '^audit-output/(ORCHESTRATOR_AUDIT\.md|EVIDENCE\.md|VERDICT\.json)$' || true)
test -z "$unexpected" || fail "unexpected worktree paths: $unexpected"

pass 'deterministic_closure_harness'
