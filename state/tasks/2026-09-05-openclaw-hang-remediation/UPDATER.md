# Transactional OpenClaw updater

Canonical script: `scripts/openclaw-transactional-update.sh`

## Safety properties

- Takes the process lock before making changes.
- Detects whether the user Gateway service was active at entry.
- Validates config before update and again before doctor/restart.
- Creates and verifies an OpenClaw backup archive without workspace content.
  The archive includes config and supported SQLite state snapshots.
- Installs via `openclaw update --no-restart`; the running Gateway remains live
  on its loaded code during package installation.
- Uses per-step timeouts and a durable, permission-restricted log/status file.
- Performs exactly one planned Gateway restart, after all update/doctor steps.
- Its EXIT trap starts the Gateway if it was running at entry but is inactive
  after a failure.
- Dry-run does not create a backup, update packages, run doctor, or restart.

## Invocation

Run this from an external managed user-systemd job, not from an active Gateway
conversation process:

```bash
scripts/openclaw-transactional-update.sh --dry-run
scripts/openclaw-transactional-update.sh
```

Durable state defaults to:

```text
~/.openclaw/state/transactional-update/
  latest.status
  update.lock
  backups/<run-id>.tar.gz
  runs/<run-id>/status
  runs/<run-id>/update.log
```

The log/status contain paths and command output; they must remain mode 0600 in
a mode 0700 state directory. Do not add credentials as CLI arguments.

## Verification without service mutation

```bash
bash -n scripts/openclaw-transactional-update.sh
bash scripts/test_openclaw_transactional_update.sh
scripts/openclaw-transactional-update.sh --dry-run
```

The mock test does not call the real OpenClaw CLI or systemd.
