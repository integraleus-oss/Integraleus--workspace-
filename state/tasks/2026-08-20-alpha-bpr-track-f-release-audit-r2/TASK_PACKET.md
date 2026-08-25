# Alpha BPR Track F portable bundle release audit — R2

Status: ESCALATED / NONDETERMINISTIC_AUDIT_HARNESS
Owner: Stanislav Pavlovskiy
Profile: standard
Risk: MEDIUM (local read-only audit with evidence written only in an isolated worktree)

## Retry reason

R1 exhausted its only implementation attempt because the prompt did not bind
the absolute packet and output paths. R2 uses a fresh worktree/run-root and
names every authoritative path explicitly. R1 outputs are invalid and excluded.

## Goal

Independently audit the portable Track F offline bundle and OVA before customer
handoff, then issue an evidence-backed GO, DEFER, or STOP verdict without
changing the canonical Alpha BPR project or distributable artifacts.

## Fixed baseline and artifacts

- Canonical repository: `/home/stanislav/projects/alpha-bpr`
- Fixed baseline: `b9e637754c5b00f38fd09f5949c971afd12db7a1`
- Isolated audit worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/alpha-bpr-track-f-release-audit-r2`
- Authoritative packet: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-20-alpha-bpr-track-f-release-audit-r2`
- Offline bundle: `/home/stanislav/projects/alpha-bpr/dist/track-f-complete-offline/Alpha_BPR_Track_F_Complete_Offline_Candidate_v1.tar.zst`
- Bundle SHA-256: `7c0291ebf06a4a54494f4448d811ab5c83f36272aa568303fd7dcafef927a850`
- OVA: `/home/stanislav/projects/alpha-bpr/dist/track-f-complete-offline/appliance/Alpha_BPR_Track_F_Appliance_v1.ova`
- OVA SHA-256: `7da558f1ffb20a66ab3da34c398356dc891d3e920117cad2ca75cffa772c76cc`

## Audit sections

1. Composition and integrity.
2. Installation lifecycle evidence: install, first boot, start, smoke, remove, reinstall.
3. Documentation usability for a new engineer.
4. Security and privacy boundaries.
5. Portability boundaries and explicit DEFER routes.
6. Integrated GO/DEFER/STOP verdict with blocker/major/minor/note findings.

## Allowed writes

Exactly these worktree-root paths:

- `audit-output/ORCHESTRATOR_AUDIT.md`
- `audit-output/EVIDENCE.md`
- `audit-output/VERDICT.json`

The canonical project, archives, VM, services, system configuration, Gateway,
and network must not change. Files under `state/` are forbidden outputs.

## External-review boundary

Do not send the bundle, OVA, raw extracted payload, credentials, private data,
local logs, or private network details to reviewers. Only the three safe audit
outputs plus sealed safe metadata may enter review.

## Follow-up boundary

Audit only. Do not repair defects. Repair requires a new bounded packet.
Windows/VirtualBox/VMware, Intel macOS, ARM64, and Apple Silicon remain DEFER
without direct fixed-baseline evidence.

## Checklist

- [x] R1 failure diagnosed and excluded
- [x] Fresh isolated worktree created at fixed baseline
- [x] Absolute packet, harness, worktree, and output paths frozen
- [x] Root `audit-output/` confirmed not ignored by Git
- [x] R2 PREPARE authorized by owner
- [x] R2 RUN authorized by owner
- [x] Three valid audit outputs produced
- [ ] Independent standard-profile verdict completed (first review completed; closure review blocked by nondeterministic harness)

## Commit rule

No commit, push, deploy, transfer, VM start/stop, service change, or canonical
project modification is allowed.
