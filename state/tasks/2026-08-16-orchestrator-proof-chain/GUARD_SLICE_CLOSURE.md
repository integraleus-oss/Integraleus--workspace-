## Verdict: REQUEST CHANGES — 0 blockers, 4 majors

The core two-phase design is sound (PREPARE/RUN separation, per-message consume marker, no-follow component walk, staged-digest re-check after copy). The majors below are all in the guard's own bounds/cleanup, not in the authorization logic.

### Major

**M1 — `_copy_tree` bounds do not cover directories (root-privileged tmpfs exhaustion).**
`MAX_FILES`/`MAX_BYTES` are only incremented for `S_ISREG` entries. Directory entries are `mkdir`'d unconditionally, and fan-out at each level is unbounded (only `MAX_DEPTH` is checked). Since the model controls the source task tree, it can pre-plant a wide tree of empty directories; the next routine owner `PREPARE` makes the root guard create all of them under `/run` (tmpfs = kernel memory + inodes), plus unbounded `os.listdir` buffers. The stated snapshot bound is bypassable by an untrusted input. Fix: count directories against `MAX_FILES` (or add `MAX_DIRS`) and enforce a per-directory entry-count cap before recursing.

**M2 — No `st_nlink`/ownership check on copied files; root re-publishes content to the unprivileged user.**
`_copy_tree` reads each regular file as root and writes it into a snapshot chowned `root:stanislav`, mode `0640` — i.e. readable by the runner user. A hardlink planted in the task tree to a root-only-readable file is indistinguishable from a normal file here (`S_ISREG` passes, no `st_nlink`/`st_uid` check), so the guard becomes a confused deputy that copies out privileged content. This is currently blocked in practice by `fs.protected_hardlinks=1`, so it is conditional — but a root-owned guard should not depend on a sysctl for its own invariant. Fix: reject `info.st_nlink > 1`, and/or require `st_uid == stanislav` for copied files.

**M3 — Process-group cleanup only happens on timeout.**
`os.killpg` is called exclusively in the `TimeoutExpired` path. On normal exit (and on the `_run_child` failure paths), any grandchildren the runner left in its new session keep running as `stanislav`, unbounded and unaudited, after the guard reports `TERMINAL`. Given the runner is an orchestrator driving a model-controlled packet, spawned background work is the expected case, which breaks the "one controlled run" invariant. Fix: `killpg(SIGTERM)` → short wait → `killpg(SIGKILL)` in a `finally` around `process.wait()`, on every exit path.

**M4 — `RLIMIT_FSIZE` 1 MiB is applied to the whole runner as a hard limit.**
`demote()` sets both soft and hard `RLIMIT_FSIZE` to 1 MiB *before* `setuid`, so the runner can never raise it and any single file write past 1 MiB raises `SIGXFSZ` and kills the process — not just the stdout/stderr capture files. Any legitimate report/evidence artifact over 1 MiB silently turns a valid run into `runner did not produce structured terminal evidence`. The stdout bound is already enforced independently by `stdout_file.read(1_048_577)`. Fix: drop the rlimit (or set only a generous hard limit) and bound the capture files by truncating on read, as is already done.

### Minor

- **Exit-code check ordered after JSON parse** in `_run_child`: a crashed/`SIGXFSZ`-killed runner surfaces "did not produce structured terminal evidence" instead of the real exit status. Check `returncode` first. Also, `130` (SIGINT) in the success allowlist accepts an interrupted run as terminal.
- **`stderr_file` is written but never read**, audited, or included in the failure record — all diagnostics for a rejected run are discarded.
- **No snapshot lifecycle**: snapshot dirs are never removed after `RUN`, after a failed `_prepare` (a partial tree is left behind), or on TTL expiry; `prepared` entries also never get purged, and orphans survive guard restarts. `/run` grows monotonically.
- **`relative_to` in `_prepare` raises bare `ValueError`**, so an out-of-root `packetPath` audits as `error: ValueError` rather than a `GuardError` — inconsistent with the fail-closed error taxonomy elsewhere.
- **`REJECTED` audit records carry only `error` type** — no `gatewayPid`, `messageId`, or phase, so rejections are not attributable.
- **No `umask` set**: `mkdir(0o750)`/`open(…, 0o640)` are umask-masked, so a restrictive service umask would silently strip the group-read the runner depends on. Set `os.umask(0o027)` in `main()`.
- **`SNAPSHOT_ROOT.mkdir(exist_ok=True)` does not re-assert mode** on a pre-existing directory (only `chown` via `_snapshot_owner`); add an explicit `chmod`.
- **Consume markers in `USED_ROOT` accumulate forever** even though replay is already bounded to `MAX_AGE_SECONDS`; no pruning.
- **`_gateway_peer` has an inherent `SO_PEERCRED`→`/proc` TOCTOU** (pid reuse / post-connect `exec`). Out of scope under the trusted-Gateway model, but a `pidfd`/`starttime` check would close it.

### Test gaps

1. `_run_child` is mocked in every test — **zero coverage** of the timeout `SIGTERM`→`SIGKILL` escalation, `killpg` targeting, exit-code allowlist, terminal-JSON parsing, stdout truncation, or `demote()`/rlimit behaviour. This is exactly the code M3/M4 concern.
2. No negative test for the **new PREPARE binding**: content with a stale digest, a mismatched relative path, or the old unbound `PREPARE ORCHESTRATOR PILOT` string must be rejected — none is asserted, so the headline fix of this commit is untested.
3. No path-traversal tests: `packetPath` outside `PACKET_ROOT`, containing `..`, relative, a prefix-confusion sibling (`…/tasks-evil/x`), or a **symlinked parent component** (the whole point of the `O_NOFOLLOW` component walk). The existing symlink test only covers a symlink *inside* the packet dir.
4. No TOCTOU test: swap the packet between digest verification and `_copy_tree` and assert `staged packet digest mismatch`.
5. No test for `MAX_DEPTH`, `MAX_FILES`, directory fan-out (M1), or the "source changed during read" size-mismatch branch.
6. No `SNAPSHOT_TTL_SECONDS` expiry test in `_run_prepared`, and no test for wrong `snapshotId` / wrong digest in run content (only the double-run replay case).
7. No test for the `isascii()` fix (e.g. `messageId="٣٣٠١"`), and no coverage of missing/extra request keys or a non-`prepare`/`run` action falling through to `_run_prepared`.
8. Immutability is asserted only via mode bits, not ownership — since tests run unprivileged, `_snapshot_owner` is a no-op and the "root-owned, runner-read-only" property is never actually verified.
9. `handle()` itself is untested: no assertion that `PREPARED`/`ADMITTED`/`TERMINAL`/`FAILED` audit records are emitted with the expected fields.
