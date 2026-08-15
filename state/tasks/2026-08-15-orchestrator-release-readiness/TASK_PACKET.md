# Orchestrator local CLI release checkpoint and readiness

## Goal

Create a reproducible local release checkpoint for the tested Codex-Claude
orchestrator, protect it with a verified encrypted Synology backup, and define
the controlled-pilot operating boundary without activating any service.

## Authorized scope

- Create project-local release/readiness/evidence documents.
- Commit and tag the resulting local checkpoint.
- Create and verify one encrypted Git bundle backup under the approved Synology
  backup directory inside the home network.
- Perform read-only verification and temporary local restore checks.

## Forbidden scope

- No Gateway, OpenClaw runtime/config, systemd, cron, deploy, or network change.
- No unattended execution.
- No push or automatic project commit.
- No modification of `/home/stanislav/projects/home-agent-factory`.
- No raw Synology data may leave the home network.

## Checklist

- [x] Task packet exists before release work.
- [x] Activation-readiness packet completed.
- [x] Current integration suite passes.
- [x] Release checkpoint committed and annotated tag created.
- [x] Git bundle created from the checkpoint.
- [x] Bundle encrypted to Synology with mode `600` and external SHA-256.
- [x] Encrypted artifact decrypted into a temporary local directory.
- [x] Internal SHA-256, `git bundle verify`, and exact tagged commit verified.
- [x] Temporary restore files removed.
- [x] `git status` clean; Gateway/cron unchanged.

## Acceptance criteria

- A clean local commit and annotated release tag identify the exact checkpoint.
- The readiness packet defines invocation, allowlists, budgets, kill switch,
  logs/evidence, stop conditions, and approval boundaries.
- A portable encrypted backup can be decrypted and independently verified.
- No activation or external production state change occurs.
