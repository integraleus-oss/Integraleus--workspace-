#!/usr/bin/env bash
set -euo pipefail

project=/home/stanislav/projects/alpha-bpr
worktree=/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-track-f-release-audit
bundle="$project/dist/track-f-complete-offline/Alpha_BPR_Track_F_Complete_Offline_Candidate_v1.tar.zst"
bundle_sidecar="$bundle.sha256"
ova="$project/dist/track-f-complete-offline/appliance/Alpha_BPR_Track_F_Appliance_v1.ova"
ova_sidecar="$ova.sha256"
baseline=b9e637754c5b00f38fd09f5949c971afd12db7a1

fail() { printf 'FAIL %s\n' "$*"; exit 1; }
pass() { printf 'PASS %s\n' "$*"; }

test "$(git -C "$worktree" rev-parse HEAD)" = "$baseline" || fail 'isolated baseline mismatch'
pass "baseline=$baseline"

canonical_status=$(git -C "$project" status --short)
test -z "$canonical_status" || fail 'canonical alpha-bpr worktree is dirty'
pass 'canonical_worktree_clean'

(cd "$(dirname "$bundle")" && sha256sum -c "$(basename "$bundle_sidecar")") >/dev/null || fail 'bundle SHA-256 mismatch'
pass 'bundle_sha256=7c0291ebf06a4a54494f4448d811ab5c83f36272aa568303fd7dcafef927a850'

(cd "$(dirname "$ova")" && sha256sum -c "$(basename "$ova_sidecar")") >/dev/null || fail 'OVA SHA-256 mismatch'
pass 'ova_sha256=7da558f1ffb20a66ab3da34c398356dc891d3e920117cad2ca75cffa772c76cc'

zstd -q -t "$bundle" || fail 'bundle zstd integrity'
pass 'bundle_zstd_integrity'

tar --zstd -tf "$bundle" >/dev/null || fail 'bundle tar readability'
pass "bundle_entries=$(tar --zstd -tf "$bundle" | wc -l)"

tar -tf "$ova" >/dev/null || fail 'OVA tar readability'
pass "ova_entries=$(tar -tf "$ova" | wc -l)"

bundle_names=$(tar --zstd -tf "$bundle")
for expected in README.md preflight.sh install.sh start.sh smoke.sh remove.sh; do
  printf '%s\n' "$bundle_names" | grep -Eq "(^|/)$expected$" || fail "bundle missing $expected"
done
pass 'bundle_required_entry_names'

ova_names=$(tar -tf "$ova")
printf '%s\n' "$ova_names" | grep -Eq '\.ovf$' || fail 'OVA missing OVF descriptor'
printf '%s\n' "$ova_names" | grep -Eq '\.(vmdk|vdi)$' || fail 'OVA missing virtual disk'
pass 'ova_required_entry_names'

if printf '%s\n%s\n' "$bundle_names" "$ova_names" | grep -Eiq '(^|/)(id_rsa|id_ed25519|.*\.pem|.*\.key|license.key|secrets?\.json|\.env)(/|$)'; then
  fail 'suspicious secret-bearing filename in artifact listing'
fi
pass 'artifact_name_secret_screen'

for output in ORCHESTRATOR_AUDIT.md EVIDENCE.md VERDICT.json; do
  test -s "$worktree/audit-output/$output" || fail "missing audit-output/$output"
done
pass 'required_audit_outputs'

python3 -m json.tool "$worktree/audit-output/VERDICT.json" >/dev/null || fail 'VERDICT.json invalid'
pass 'verdict_json_valid'

unexpected=$(git -C "$worktree" status --porcelain --untracked-files=all | awk '{print $2}' | grep -Ev '^audit-output/(ORCHESTRATOR_AUDIT\.md|EVIDENCE\.md|VERDICT\.json)$' || true)
test -z "$unexpected" || fail "unexpected worktree paths: $unexpected"
pass 'allowed_paths_only'
