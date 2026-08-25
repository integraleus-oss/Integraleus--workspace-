# Alpha BPR Track F portable bundle release audit

Status: PREPARED_NOT_STARTED
Owner: Stanislav Pavlovskiy
Profile: standard
Risk: MEDIUM (local read-only audit with evidence written only in an isolated worktree)

## Goal

Independently audit the portable Track F offline bundle and OVA before customer handoff, then issue an evidence-backed GO, DEFER, or STOP verdict without changing the canonical Alpha BPR project or the distributable artifacts.

## Fixed baseline and artifacts

- Canonical repository: `/home/stanislav/projects/alpha-bpr`
- Fixed baseline: `b9e637754c5b00f38fd09f5949c971afd12db7a1`
- Isolated audit worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-track-f-release-audit`
- Offline bundle: `/home/stanislav/projects/alpha-bpr/dist/track-f-complete-offline/Alpha_BPR_Track_F_Complete_Offline_Candidate_v1.tar.zst`
- Bundle SHA-256: `7c0291ebf06a4a54494f4448d811ab5c83f36272aa568303fd7dcafef927a850`
- OVA: `/home/stanislav/projects/alpha-bpr/dist/track-f-complete-offline/appliance/Alpha_BPR_Track_F_Appliance_v1.ova`
- OVA SHA-256: `7da558f1ffb20a66ab3da34c398356dc891d3e920117cad2ca75cffa772c76cc`

Both sidecar hashes were checked locally before this packet was sealed.

## Independent audit sections

1. Composition and integrity: sidecars, full SHA-256, archive readability, expected top-level payload and manifests.
2. Installation lifecycle evidence: install, first boot, start, smoke, remove, reinstall; distinguish direct execution from previously recorded evidence.
3. Documentation usability: a new engineer can identify prerequisites, import/install steps, licensing boundary, operation, verification, troubleshooting, evidence capture, and removal.
4. Security and privacy: no license key, embedded password, private key, secret, unnecessary private address, or raw private data is exposed in review evidence.
5. Portability boundary: Linux/KVM evidence may be evaluated; Windows, VirtualBox, VMware, Intel macOS, ARM64, and Apple Silicon remain DEFER unless direct evidence already exists in the fixed baseline.
6. Integrated verdict: one GO/DEFER/STOP result with findings classified as blocker, major, minor, or note.

These are sections of one audit packet, not promises of parallel agents.

## GO / DEFER / STOP

- GO: both artifacts match the pinned hashes; contents and documentation are coherent; available install/lifecycle evidence is sufficient for the specifically claimed platform; no blocker/major security finding exists.
- DEFER: the checked material is internally sound but a platform-specific or customer-environment claim lacks direct evidence. Windows/VirtualBox/VMware are expected DEFER in this run.
- STOP: hash mismatch, unreadable/corrupt artifact, missing critical installation/removal path, embedded credential/license/private key, unsafe default, misleading universal-platform claim, or evidence contradicting the release claim.

## Allowed writes

Only these paths in the isolated worktree may be created or changed:

- `audit-output/ORCHESTRATOR_AUDIT.md`
- `audit-output/EVIDENCE.md`
- `audit-output/VERDICT.json`

The local harness and packet files are read-only inputs. The canonical project, archives, VM, services, system configuration, Gateway, and network must not be changed.

## External-review boundary

Do not send the 4-GB bundle, OVA, raw extracted payload, credentials, private data, local logs, or private network details to external reviewers. Review inputs may contain only the three safe audit outputs, manifests, file names, hashes, counts, command status, and minimal redacted excerpts needed to substantiate findings.

## Follow-up boundary

This run is audit-only. It must not repair defects. Any repair requires a new bounded task packet after this verdict.

## Checklist

- [x] Fixed baseline verified and isolated worktree created
- [x] Bundle and OVA sidecar hashes verified
- [x] Task packet and read-only harness created
- [x] Orchestrator PREPARE authorized by owner
- [x] Orchestrator RUN authorized by owner
- [ ] Three valid in-scope audit outputs produced
- [ ] Independent standard-profile verdict completed
- [ ] Separate follow-up decision made for any defects

## Commit rule

No commit, push, deploy, transfer, VM start/stop, service change, or canonical-project modification is allowed.
