# Local Codex Runner

Use this when OpenClaw should delegate heavy local work to the user's local
Codex CLI instead of spending the current OpenClaw model context or degrading
to `ollama/phi3:instruct`.

## Runner

```bash
/home/stanislav/.openclaw/workspace/agents/main/scripts/codex-local-run.sh
```

The runner:

- uses `/home/stanislav/.local/bin/codex-local`;
- verifies local Codex login;
- checks OpenAI routes through NL VPN `awg0` with source `10.8.1.19`;
- runs `codex exec` from the explicit `--cd` directory;
- defaults to `--read-only`.

## Read-Only Analysis

Use for reviews, explanations, log/config analysis, and second opinions.

```bash
/home/stanislav/.openclaw/workspace/agents/main/scripts/codex-local-run.sh \
  --cd /path/to/project \
  --read-only \
  -- 'Analyze this project narrowly: focus on <specific files/problem>. Report only findings and risks.'
```

For non-repo or temporary checks:

```bash
/home/stanislav/.openclaw/workspace/agents/main/scripts/codex-local-run.sh \
  --cd /tmp \
  --read-only \
  -- 'Answer briefly: <question>'
```

## Workspace-Write Changes

Use only when local Codex should edit files inside one target project.
Afterwards, inspect the diff and run tests independently.

```bash
/home/stanislav/.openclaw/workspace/agents/main/scripts/codex-local-run.sh \
  --cd /path/to/project \
  --write \
  -- 'Implement <specific change>. Keep edits scoped. Run relevant tests if available.'
```

Then verify outside Codex:

```bash
cd /path/to/project
git diff
git status --short
```

## Large Logs Or Narrow Inputs

Prefer passing only the relevant excerpt instead of pointing Codex at the whole
main workspace.

```bash
tail -n 300 /path/to/log |
  /home/stanislav/.openclaw/workspace/agents/main/scripts/codex-local-run.sh \
    --cd /tmp \
    --read-only \
    -- 'Summarize errors and likely root cause. Do not speculate beyond the log.'
```

## When Not To Use

- Tiny Telegram answers that do not need another model.
- Tasks involving Synology raw file contents unless Станислав explicitly allows.
- Root/system/service/config changes unless the user explicitly approved that
  operation.
- True OpenClaw gateway-level fallback. `codex-local` is currently a CLI helper,
  not a model provider.

## Known Sandbox Limitation

Simple prompt runs work. If local Codex needs to run shell commands inside its
own `--sandbox read-only`, it may fail with:

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

Treat this as a local sandbox/user-namespace issue, not as an auth or VPN
failure. For now, use narrow prompt-only checks when possible, or investigate
the sandbox separately before relying on Codex-managed shell execution.
