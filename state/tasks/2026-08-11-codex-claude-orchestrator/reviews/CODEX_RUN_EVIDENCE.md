# Codex Run Evidence

## Outcome

The first two attempts reached `ESCALATED` after consecutive `FAILED_INFRA`
results. The owner then explicitly approved a narrow AppArmor repair. The
workspace-write sandbox probe and a fresh local Codex implementation run
completed successfully without `--danger`; the historical failures below are
retained as evidence that retry and escalation policy worked.

## Attempt 1

- Runtime: local Codex CLI `0.146.0`, workspace-write sandbox.
- Empty implementation directories were created under the allowed path.
- `apply_patch` could not create even a one-line file.
- Python and shell-write probes intermittently failed before command execution
  with:

  `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`

- No implementation deliverable or commit was produced.

## Attempt 2

- Fresh local Codex session with the same workspace-write boundary.
- Required first action was a one-line `apply_patch` probe.
- Probe failed with `Failed to write file .../implementation/.write-probe`.
- Run stopped immediately as instructed.

## Safety boundary

- No `--danger` or sandbox bypass.
- No shell-redirection fallback.
- No system packages, services, Gateway config, wrappers, or unrelated files
  changed.
- Retry budget exhausted; further automatic retries are forbidden until the
  sandbox condition changes or the owner approves a different execution path.

## Recovery and successful attempt

- Installed and loaded the documented `/etc/apparmor.d/bwrap` profile.
- Kept `kernel.apparmor_restrict_unprivileged_userns=1` globally.
- Direct bubblewrap namespace probe passed.
- Local Codex workspace-write probe created `implementation/SANDBOX_PROBE.md`
  and executed Python inside the sandbox.
- Fresh local Codex run produced the contract slice and exited 0.
- Independent verification: schema self-check passed; 2 valid fixtures passed;
  15 invalid fixtures failed as expected; 5 unit tests passed; whitespace and
  scope checks passed.
- No commit was made.
