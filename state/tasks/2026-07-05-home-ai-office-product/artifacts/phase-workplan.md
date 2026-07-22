# Phase Workplan: Standalone Home Agent Factory

Date: 2026-07-05
Architecture decision: build the factory as a separate product. OpenClaw is one runtime adapter, not the product core.

## Product Boundary

Repository target:

- `projects/home-agent-factory/`

Core product owns:

- agent package schema;
- package instance schema;
- capability grant schema;
- runner;
- approval state;
- run logs;
- catalogue/UI/API;
- connector and runtime adapter interfaces.

OpenClaw adapter owns:

- invoking OpenClaw gateway/CLI;
- mapping factory permissions to OpenClaw tool/session constraints;
- reading OpenClaw result metadata;
- optional use of OpenClaw skills as playbooks.

## Phase 0: Product Skeleton and Boundaries

Duration: 1-2 days.

Goal: create a standalone project that cannot accidentally become just another OpenClaw skill folder.

Tasks:

- Create `projects/home-agent-factory/`.
- Initialize repo/package structure.
- Add `README.md` with product boundary and non-goals.
- Add `docs/architecture.md`.
- Add `docs/security-model.md`.
- Add `docs/decisions.md`.
- Add minimal CLI entrypoint: `factory --help`.
- Add `agent-packs/`, `instances/`, `runs/`, `schemas/`.
- Add test harness.

Deliverables:

- Working project skeleton.
- Product boundary documented.
- First commit.

Acceptance:

- Product builds/runs without importing OpenClaw internals.
- OpenClaw dependency is represented only as an adapter interface/stub.
- `factory --help` works.

## Phase 1: Schemas and Policy Core

Duration: 3-5 days.

Goal: define the contract before building UI or many agents.

Tasks:

- Create `schemas/agent-pack.schema.json`.
- Create `schemas/agent-instance.schema.json`.
- Create `schemas/capability-grant.schema.json`.
- Create `schemas/run-log.schema.json`.
- Implement schema validation.
- Implement policy compiler: pack + instance + request context -> capability grant.
- Implement hard gates:
  - private local-read + cloud model requires explicit grant;
  - private local-read + external-send requires explicit grant;
  - private local-read + group output denied by default;
  - external-read is GET/domain allowlist only;
  - destructive/system actions denied by default.
- Add negative policy tests.

Deliverables:

- Schema files.
- Policy compiler.
- Test suite.

Acceptance:

- Invalid packs fail validation.
- Dangerous permission combinations fail tests.
- Capability grant is deterministic and serializable.

## Phase 2: Append-First Runner and Audit Log

Duration: 4-7 days.

Goal: run one controlled agent package with evidence even when denied or failed.

Tasks:

- Implement run lifecycle:
  - `created`;
  - `validating`;
  - `grant_compiled`;
  - `running`;
  - `waiting_approval`;
  - `denied`;
  - `failed`;
  - `completed`.
- Implement append-first run log writer.
- Implement file/path scope checker.
- Implement tool-call guard interface.
- Implement model policy guard.
- Implement output-channel guard.
- Add CLI commands:
  - `factory pack list`;
  - `factory pack show <slug>`;
  - `factory run <slug> --input <file>`;
  - `factory runs list`;
  - `factory runs show <id>`.
- Add first stub local runtime that returns deterministic output for tests.

Deliverables:

- Runner core.
- CLI.
- Run logs.
- Guard tests.

Acceptance:

- A run creates audit evidence before touching data.
- Denied and failed runs are logged.
- Attempt to read outside declared folder is blocked.
- Attempt to output private-derived result to group context is blocked.

## Phase 3: First Real Pack - Private Archive RAG

Duration: 5-7 days.

Goal: prove the hardest privacy path first.

Tasks:

- Create `agent-packs/private-archive-rag/`.
- Add pack metadata, prompt/workflow, setup guide.
- Add one safe sample archive folder.
- Implement simple local indexing/search path.
- Decide first model mode:
  - local-only by default;
  - cloud only by explicit per-run approval.
- Produce cited answers.
- Add exfiltration tests:
  - private read -> group output denied;
  - private read -> cloud model denied without approval;
  - private read -> external URL denied;
  - private read -> DM summary allowed only within configured limits.

Deliverables:

- First real pack.
- Local sample data.
- End-to-end test.

Acceptance:

- User can run `factory run private-archive-rag`.
- Result includes citations.
- No raw private data is sent outside approved boundary.
- Negative exfiltration tests pass.

## Phase 4: OpenClaw Runtime Adapter

Duration: 5-10 days.

Goal: use OpenClaw as an execution backend without coupling the factory to OpenClaw internals.

Tasks:

- Define runtime adapter interface:
  - `runTask(request, grant)`;
  - `resumeApproval(runId, decision)`;
  - `getStatus(runId)`;
  - `cancel(runId)`.
- Implement `openclaw-adapter`.
- Map factory channel context to OpenClaw session/message context.
- Map factory approval gates to OpenClaw approval/message flow.
- Map factory run metadata to OpenClaw session/tool metadata where possible.
- Add adapter config file.
- Add tests with mocked OpenClaw responses.
- Add one live smoke test on Home.

Deliverables:

- OpenClaw adapter.
- Adapter config.
- Smoke result.

Acceptance:

- Factory can run one pack through OpenClaw adapter.
- Factory run log remains source of truth.
- OpenClaw can fail without corrupting package/instance state.

## Phase 5: Telegram Control Surface

Duration: 4-7 days.

Goal: make the first usable UX Telegram-first.

Tasks:

- Add Telegram adapter or OpenClaw-message bridge.
- Commands:
  - `/factory list`;
  - `/factory show <slug>`;
  - `/factory run <slug>`;
  - `/factory approvals`;
  - `/factory approve <run-id>`;
  - `/factory deny <run-id>`.
- Persist paused approvals.
- Default-deny approval timeout.
- DM/group context detection.
- Group output guard.

Deliverables:

- Telegram command UX.
- Approval loop.
- Group safety checks.

Acceptance:

- Owner can launch a pack from Telegram.
- Approval prompt is clear and includes destination/data scope.
- Private-derived output to group is refused and logged.

## Phase 6: Two More MVP Packs

Duration: 5-8 days.

Goal: prove that the platform supports more than RAG without expanding too far.

Packs:

1. `project-status-digest`
   - reads selected project folder;
   - summarizes TODO/state/git status;
   - can run on schedule;
   - no external send except reply to owner.

2. `telegram-support-triage`
   - classifies inbound messages;
   - drafts replies;
   - requires approval before sending;
   - does not read private files by default.

Tasks:

- Create pack definitions.
- Create instance examples.
- Add pack tests.
- Add one scheduled run for project digest.
- Add one approval-before-send flow for support triage.

Deliverables:

- 3 total MVP packs.
- 2 demos.

Acceptance:

- Scheduled digest writes run log.
- Support triage cannot send without approval.
- All three packs use same runner/policy system.

## Phase 7: Minimal Web/Catalogue UI

Duration: 5-10 days.

Goal: make the product understandable without reading YAML.

Tasks:

- Build local UI:
  - pack list;
  - pack detail;
  - instance config;
  - recent runs;
  - pending approvals;
  - risk badges.
- Add read-only dashboard first.
- Add install/configure after read-only view is stable.
- Add icons/categories.
- Add privacy explanations per pack.

Deliverables:

- Local UI.
- Screenshot/demo.

Acceptance:

- Non-technical user can understand what each pack does.
- Risky permissions are visible before run.
- UI does not allow bypassing policy.

## Phase 8: Reliability and Operations

Duration: 5-10 days.

Goal: make it run unattended on Home.

Tasks:

- Add systemd service.
- Add backup/export for packs/instances/runs.
- Add health endpoint/CLI.
- Add log rotation.
- Add crash recovery for paused runs.
- Add adapter health checks.
- Add model usage tracking.
- Add integration health page.

Deliverables:

- Service install docs.
- Health checks.
- Backup/export command.

Acceptance:

- Service survives restart.
- Paused/denied/completed runs remain inspectable.
- Backup can restore pack and run history.

## Phase 9: Productization Decision

Duration: 3-5 days.

Goal: decide whether this remains private Home tooling or becomes a distributable product.

Tasks:

- Review MVP usage.
- Review security incidents/blocked runs.
- Review which packs were actually useful.
- Decide packaging path:
  - private Home-only;
  - OpenClaw plugin;
  - standalone LAN appliance;
  - public SaaS later.
- Create roadmap v2.

Deliverables:

- `docs/mvp-retrospective.md`.
- `docs/roadmap-v2.md`.

Acceptance:

- Clear go/no-go for public/distributable product.
- No public exposure before security review.

## First Sprint Detail

Sprint duration: 5 working days.

Sprint goal: prove policy core, not agent variety.

Day 1:

- create repo skeleton;
- add architecture/security docs;
- add CLI stub.

Day 2:

- add pack/instance/grant schemas;
- add validation tests.

Day 3:

- implement policy compiler;
- implement hard gate tests.

Day 4:

- implement append-first run log;
- implement runner lifecycle with stub runtime.

Day 5:

- create `private-archive-rag` skeleton;
- run negative tests;
- write sprint demo notes.

Sprint exit criteria:

- `factory pack list` works.
- `factory run private-archive-rag` creates a run log.
- private-read + cloud/send/group is blocked without approval.
- read outside declared folder is blocked.
- all tests pass.

## Explicit Non-Goals Until After MVP

- Public SaaS accounts.
- Billing.
- Open marketplace.
- Visual workflow editor.
- Desktop screen automation.
- Full 1C/CRM/WhatsApp connector set.
- Multi-tenant security model.
- Direct dependence on OpenClaw internal file layout.
