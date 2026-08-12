# Evidence — orchestrator live-launch slice

Status: COMPLETED_TARGETED_PASS
Baseline: `9f00f70`; decision record: `b707d78`

## Changed implementation

- `agent_launcher.py`: fixed-argv adapters for approved local Codex and Claude
  wrappers; single-use directories; bounded timeout; prompt/stdout/stderr and
  digest evidence; no shell evaluation of task content.
- `live_review_cycle.py`: admits exact JSON only after a successful Claude
  launch, then runs the accepted validator, projection, and deterministic
  policy. Failed launches produce no policy decision.
- focused tests for argv safety, failures, replay protection, JSON extraction,
  successful policy admission, and failed-launch fail-closed behavior.

## Real bounded dry run

- Codex: approved `scripts/codex-local-run.sh`, read-only sandbox, exit 0,
  `CODEX_LAUNCH_OK`, duration 6290 ms.
- Claude: approved `/home/stanislav/agent-runs/_bin/claude-review`, read-only,
  exit 0, duration 21354 ms.
- Prompt inputs were synthetic and non-private. The first Codex and Claude
  launcher smokes used the workspace root as their read-only project scope; no
  prompt requested Synology, memory, config, secrets, or customer data. Gateway,
  systemd, GitHub, and push were not used.
- Extracted Claude JSON validated against the trusted manifest:
  `contract_valid=true`, zero validation errors.
- Deterministic decision: `REWORK / R11_OPEN_FINDINGS`.
- The original launcher and policy smokes were separate. After closure review
  identified that gap, the actual composed `live_review_cycle.py` entry point
  ran successfully as `runs/live-cycle-r3/`: real Claude launch, exact verdict
  extraction, contract validation, projection, and deterministic
  `REWORK / R11_OPEN_FINDINGS` decision with `cycle-result.json`.

## Verification

- Integration suite after closure rework: 29/29 passed.
- Accepted core regression suite: 84/84 passed.
- `py_compile`: passed.
- `git diff --check`: passed.

## Closure review and rework

- Delayed wrapper output produced two independent `LIVE_LAUNCH_REWORK` reviews.
- Rework closed the reported blockers/majors: process-group timeout termination
  with a real background-child regression; no arbitrary wrapper override;
  exact envelope/error rejection; wrapper-output and extraction digests;
  symlink-safe verdict containment; durable `FAILED_ADMISSION`; Claude argv and
  negative-path coverage; absolute run paths across wrapper `cd`; and a real
  integrated live cycle with a synthetic fixture prompt against the narrow
  accepted core root
  `state/tasks/2026-08-11-codex-claude-orchestrator/implementation`.
- Fresh targeted closure completed before commit.

## Final closure

- Targeted R1 closed both original blockers and MAJ-1 through MAJ-5, returned
  `TARGETED_REWORK` for the remaining evidence wording and negative tests.
- Targeted R2 verified MAJ-6 and MAJ-7 closed and returned `TARGETED_PASS`.
- Final coordinator verification: 29/29 integration tests, 84/84 accepted-core
  tests, `py_compile`, and `git diff --check` passed.

## Residual boundaries

- This slice proves one review-to-decision cycle, not an unattended multi-cycle
  daemon.
- Automatic mutation/rework execution is not enabled. A `REWORK` result remains
  an instruction for the coordinator to launch a separately bounded Codex
  write attempt.
- Gateway/config/systemd/cron integration remains outside approval.
