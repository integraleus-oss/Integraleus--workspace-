# Orchestrator Test Broker + builder repair

Risk: MEDIUM, local non-production workflow code.

Goal: keep the external PREPARE/RUN interface unchanged while allowing one bounded repair after a deterministic implementation gate failure and executing tests through a trusted broker outside the Codex sandbox.

Allowed files:

- `state/tasks/2026-08-12-orchestrator-integration/**`
- `scripts/codex-local-run.sh`
- this task directory

Forbidden: Alpha BPR product files, canonical project mutation, deploy, push, external sends, sandbox weakening, arbitrary commands from Codex.

Checklist:

- [x] Define typed gate failure records and classification.
- [x] Add a trusted test-broker interface over sealed builder commands.
- [x] Convert repairable builder failures into one authenticated repair attempt.
- [x] Preserve immediate STOP for scope, ignored-state, and infrastructure failures.
- [x] Pass deterministic execution-context variables to sealed gates.
- [x] Add regression tests for assertion/count repair and non-repairable failures.
- [x] Prove the end-to-end state transition on a throwaway fixture.
- [x] Run internal Standards and Spec review; external Claude review was not authorized.
- [x] Record evidence; no Alpha BPR product RUN.

Residual qualification gate: nondeterministic harness detection remains a PREPARE-time repeated-run check; it has not been moved into the runtime broker.

Acceptance:

- Existing PREPARE/RUN command contract remains unchanged.
- Maximum implementation attempts remains bounded at two.
- Only sealed commands execute outside the Codex sandbox.
- A repairable gate failure produces a structured repair directive with bounded evidence.
- Non-repairable safety/infrastructure failures still escalate immediately.
- Existing regression suite remains green.
