# Task Packet: Deterministic Codex-Claude Orchestrator MVP

Status: COMPLETED
Owner: Stanislav
Coordinator: OpenClaw main
Risk: MEDIUM, local artifact work only

## Goal

Build a deterministic orchestration protocol in which Codex implements,
fresh-session Claude reviews, and code—not an LLM—controls acceptance.

## Approved architecture

Canonical decision: `D-2026-08-11-01` in workspace `DECISIONS.md`.

## Current slice

Ask a fresh read-only local Claude session to return, in its response only:

1. a draft `review-verdict.schema.json`;
2. valid and invalid JSON examples;
3. deterministic invariants and adversarial cases.

Claude must not edit files or implement the policy engine.

## Boundaries

Allowed inputs:

- this task's sanitized prompt;
- the architecture requirements copied into that prompt.

Forbidden:

- repository exploration;
- file edits;
- secrets, private chats, Synology data, or unrelated project context;
- Gateway/config/runtime changes;
- acceptance decisions made by an LLM.

## Acceptance criteria for Claude output

- AC-01: Draft is JSON Schema 2020-12 and rejects unknown fields.
- AC-02: Findings support blocker, major, and nit severity.
- AC-03: Blocker/major findings require reproducible evidence fields.
- AC-04: `criterion_id` may be null only with a required category and rationale.
- AC-05: Stable finding identity is separated from per-run occurrence identity.
- AC-06: Human-only resolutions are represented without granting Claude approval authority.
- AC-07: Review mode distinguishes full review from targeted verification.
- AC-08: Output includes valid and intentionally invalid examples with reasons.
- AC-09: Invariants cover severity floors, prompt injection, finding churn,
  false closure, and incomplete evidence.

## Checklist

- [x] Task folder created
- [x] Claude prompt created
- [x] Fresh Claude run completed
- [x] Output captured
- [x] Coordinator review completed
- [x] Codex implementation packet created
- [x] Codex implementation started
- [x] Two bounded Codex attempts classified `FAILED_INFRA`
- [x] Retry budget exhausted; no unsafe sandbox bypass used
- [x] Owner approved narrow AppArmor repair
- [x] Workspace-write sandbox probe passed
- [x] Codex implementation completed and independently verified
- [x] Fresh adversarial Claude review completed after one timed-out broad run
- [x] Confirmed blocker/major findings reproduced locally
- [x] Bounded Codex rework completed in workspace-write sandbox
- [x] Rework gates independently rerun: schema, 16 tests, py_compile, whitespace
- [x] First targeted Claude verification completed; three remaining majors reproduced
- [x] Codex Rework 2 completed; independent gates passed with 20 tests
- [x] Final targeted Claude review completed; two container-value crash paths found
- [x] Codex Rework 3 completed; independent gates passed with 22 tests
- [x] Fresh closure review returned `TARGETED_PASS` with no open blocker/major

## Evidence

- Claude prompt: `prompts/claude-contract-design.md`
- Claude response: `reviews/claude-contract-design.md`
- Coordinator assessment: `reviews/CLAUDE_ASSESSMENT.md`
- Codex packet: `CODEX_TASK_PACKET.md`
- Codex run evidence: `reviews/CODEX_RUN_EVIDENCE.md`
- Implementation evidence: `implementation/EVIDENCE.md`
- AppArmor change and rollback: `ops/APPARMOR_CHANGE.md`
- Adversarial review packet: `CLAUDE_ADVERSARIAL_REVIEW_PACKET.md`
- Bounded review packet: `CLAUDE_ADVERSARIAL_REVIEW_SLICE.md`
- Adversarial report: `reviews/claude-adversarial-review-slice.md`
- Rework packet: `CODEX_REWORK_PACKET.md`
- Targeted report: `reviews/claude-targeted-reverification.md`
- Rework 2 packet: `CODEX_REWORK_2_PACKET.md`
- Final targeted report: `reviews/claude-final-targeted.md`
- Rework 3 packet: `CODEX_REWORK_3_PACKET.md`
- Closure report: `reviews/claude-r3-closure.md`

## Commit rule

Do not commit automatically. Preserve unrelated dirty-worktree changes.
