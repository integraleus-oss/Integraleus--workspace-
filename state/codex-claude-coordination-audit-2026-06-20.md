# Codex / Claude CLI Coordination Audit - 2026-06-20

## Checklist

- [x] Identify active SSH/Termius terminal sessions.
- [x] Identify active Codex CLI processes.
- [x] Identify active Claude Code CLI processes.
- [x] Identify existing tmux/screen sessions.
- [x] Inspect recent local Codex session roots.
- [x] Inspect recent Claude project/session roots when available.
- [x] Summarize current task ownership and risks.
- [x] Propose migration path to supervised dashboard/tmux scheme.

## Findings

Audit time: 2026-06-20 11:01-11:12 MSK.

### Active Termius / Tailscale Sessions

- Two active interactive Tailscale SSH terminals from `100.81.237.50`, both started at about 09:53 MSK.
- `pts/2`: local Codex CLI.
- `pts/3`: local Claude Code CLI.
- Both are running from `/home/stanislav`, not from the project root.

### Active Codex CLI

- Version: `codex-cli 0.140.0`.
- Binary: `/usr/bin/codex`.
- Active process tree:
  - `node /usr/bin/codex`
  - native Codex child process
- CWD: `/home/stanislav`.
- Recent session file: `/home/stanislav/.codex/sessions/2026/06/20/rollout-2026-06-20T09-54-05-019ee3ce-dbd1-7883-a5b8-64436151acb0.jsonl`.
- Current task context from session log:
  - read information from Claude;
  - saved the Synology exchange convention into long-term task context;
  - audited new Claude work;
  - wrote `codex-to-claude_2026-06-20-1053_audit.md` into `/mnt/synology/Documents/OpenClawExchange/agent-messages/`;
  - latest visible assistant state: waiting for a new `claude-to-codex_*.md` answer.

### Active Claude Code CLI

- Version: `2.1.179 (Claude Code)`.
- Binary: `/usr/bin/claude`.
- Active process: `claude` on `pts/3`.
- CWD from process/session metadata: `/home/stanislav`.
- Claude session metadata: `/home/stanislav/.claude/sessions/2565738.json`.
- Claude session status at audit time: moved from `busy` to `waiting`.
- Claude project/session path: `/home/stanislav/.claude/projects/-home-stanislav/ce14e008-e76d-4abc-9528-40a0ab3f80e3.jsonl`.
- Actual working repo visible in Claude log: `/home/stanislav/projects/alpha-bpr`.
- Current task context:
  - reviewed Codex audit;
  - selected "station topology first";
  - confirmed TZ says 4 pumps and 4 valves for A/B/C/D;
  - started step-by-step fixes from the audit;
  - patched `docs/api/hmi-bpr-integration-contract.md` to clarify that payload v1 does not carry per-component `sequence` and that parallel grouping needs payload v2.

### Current `alpha-bpr` Worktree

- Branch: `master`.
- HEAD: `018e4ee FK hardening: enforce recipe->product and order->product at the DB level`.
- Modified tracked file:
  - `docs/api/hmi-bpr-integration-contract.md`
- Diff summary:
  - 1 file changed, 12 insertions, 3 deletions.
- Untracked files include today's Codex bootstrap memory files:
  - `AGENTS.md`
  - `STATE.md`
  - `DECISIONS.md`
  - `TODO.md`
  - `memory/`
- Other untracked handoff/adapter files are present:
  - `docs/integration/20260619-mix01-bpr-online-adapter.md`
  - `scripts/alpha-platform/mix01_bpr_online_adapter.py`

### Existing Multiplexing / Dashboard State

- No active `tmux` server.
- `screen` is not installed.
- No existing `/home/stanislav/agent-runs` directory.
- No local agent dashboard is currently deployed.

### Current Risks

- Both CLIs were launched from `/home/stanislav`, so Codex/Claude project identity is blurred even though the actual work is in `projects/alpha-bpr`.
- There is no central task ledger: current state is split between Termius terminals, CLI session logs, Synology exchange files, and git status.
- There is no single writer lock. Today Claude edited `alpha-bpr`; Codex also has project access and can write through the exchange workflow.
- The current direct Claude<->Codex Synology exchange works, but it bypasses a visible supervisor view unless OpenClaw audits it.
- Observation requires terminal/session-log inspection; Stanislav has no clean browser dashboard yet.
- Current Claude modification is not committed and not yet verified by tests.

## Proposed Transition

### Goal

Move from ad-hoc Termius sessions to a supervised local-agent workflow:

- OpenClaw supervises.
- Codex and Claude run in controlled task sessions.
- Stanislav observes through a browser dashboard, not terminals.
- Termius remains an admin/fallback tool, not the main coordination layer.

### Roles

- Codex CLI: default code writer and test runner.
- Claude Code CLI: default reviewer, second opinion, architecture/doc reviewer.
- OpenClaw: dispatcher, status keeper, lock owner, final integrator.

Default rule: one writer per project at a time.

### Task Folder Layout

Create one folder per task:

```text
/home/stanislav/agent-runs/YYYY-MM-DD-slug/
  TASK.md
  STATUS.md
  HANDOFF.md
  events.jsonl
  logs/
    codex.log
    claude.log
    tests.log
  artifacts/
```

`STATUS.md` is human-readable. `events.jsonl` is dashboard-readable.

### Process Backend

Use `tmux` internally, even if Stanislav never opens it:

```text
tmux session: agent-YYYYMMDD-slug
  pane 1: status/watch
  pane 2: Codex CLI
  pane 3: Claude Code CLI
  pane 4: tests/git/logs
```

The dashboard reads task files and log tails. It does not need direct terminal access.

### Browser Dashboard

First version:

- local-only or Tailscale-only web server;
- URL target: `http://openclaw-home:8787/agents`;
- cards for each task;
- status, owner, project, current phase, changed files, last log lines, git status;
- read-only buttons first: refresh, show diff, show handoff, request summary.

Control buttons such as pause/stop should be added only after the read-only dashboard is reliable.

### Migration Plan

1. Freeze the current ad-hoc state into this audit file.
2. Do not kill current Termius sessions.
3. Let current Claude/Codex reach a clean checkpoint:
   - Claude: either finish the current BPR doc/preflight step or stop after summarizing current diff.
   - Codex: record that it is waiting for a Claude exchange reply.
4. Create `/home/stanislav/agent-runs/2026-06-20-alpha-bpr-coordination/`.
5. Copy current state into:
   - `TASK.md`: "Coordinate Codex/Claude Alpha BPR/MIX01 audit follow-up."
   - `STATUS.md`: current owners, waiting states, dirty files.
   - `HANDOFF.md`: current Claude/Codex exchange summary.
6. Start the next CLI runs from the real project root:
   - Codex: `codex -C /home/stanislav/projects/alpha-bpr`
   - Claude: `cd /home/stanislav/projects/alpha-bpr && claude`
7. Use a writer lock for `alpha-bpr`:
   - `writer=codex` or `writer=claude`
   - reviewer can read but not edit.
8. Keep Synology exchange only as an external handoff channel, but mirror every exchange into the task folder.
9. Build dashboard v1 against `agent-runs/` files.
10. After dashboard v1 works, stop using fresh Termius-only sessions for new agent tasks.

### Immediate Recommendation

For the current `alpha-bpr` work:

1. Do not start another writer.
2. Ask Claude to summarize and stop after the current doc/preflight step.
3. Review `docs/api/hmi-bpr-integration-contract.md`.
4. Decide whether to keep/commit the doc patch.
5. Move the next step into the new supervised `agent-runs` structure.

### Implementation Order

1. `agent-runs` task folder convention.
2. Read-only dashboard from `STATUS.md` + `events.jsonl`.
3. Internal tmux runner.
4. Writer-lock enforcement.
5. Dashboard controls.
6. Optional OpenClaw Canvas presentation.
