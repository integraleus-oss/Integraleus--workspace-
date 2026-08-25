# R3 cycle result

Status: `ESCALATED / FOCUSED_TEST_FIXTURE_PATH_FAILURE`

- Sealed packet: `sha256:b55b776df1b799e111000d3f34ae482e3279f633a8d9a5efaa1eb36919e2e226`
- Baseline: `b9e637754c5b00f38fd09f5949c971afd12db7a1`
- Attempts used: 1
- Codex duration: 492988 ms; exit 0
- Review: not started because the required focused builder gate failed
- Transfer/commit/push/deploy: forbidden and not performed

## Primary failure

The unsandboxed builder executed all 11 focused tests. Two passed and nine failed with `DirectoryNotFoundException: Could not find examples/integration-profiles.`

The new tests derive the repository root from `Directory.GetCurrentDirectory()`. With external `ArtifactsPath`, VSTest runs the assembly from the external artifact tree, so this discovery method cannot locate repository fixtures. This is a deterministic test/fixture-path defect in the implementation, not an infrastructure or sandbox failure.

Codex separately encountered `SocketException (13): Permission denied` when attempting VSTest inside its workspace-write sandbox. That remains a sandbox feedback limitation, but it is not the builder's terminal cause: the builder could run VSTest and exposed the substantive nine-test failure.

## Scope and safety

- Changes remained within the declared allowlist.
- No ignored `bin/obj` state was created in the worktree.
- `git diff --check` passed.
- Canonical Alpha BPR remained clean on `b9e6377`.
- The isolated result is not accepted and must not be transferred or reused automatically.

Evidence digests:

- cycle result: `sha256:a238401adf9fdb33f945ff4312621003664aaa9e9b775589112d7daa64b02cb2`
- focused builder stdout: `sha256:d8fc9d7fa9637e95ef5bc6f42d4e098a23fffae015d047e1487421e49da65808`
- Codex launch result: `sha256:0ca5d7981a6134220ae9f5ea1cf3bb1c7d873909f2b37d5e1193465f2998e991`

Any retry requires a fresh sealed packet/worktree. It should provide repository fixture paths deterministically (for example through an authoritative harness environment variable) and include a focused green preflight against a controlled fixture before another product RUN.
