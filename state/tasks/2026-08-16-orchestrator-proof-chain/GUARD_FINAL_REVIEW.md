## Verdict: REJECT — 3 majors

### Major

**M1 — `RLIMIT_FSIZE` removed with no replacement bound; child output is unbounded on disk.**
`orchestrator_guard.py` `_run_child`: the diff deletes `resource.setrlimit(RLIMIT_FSIZE, 1MiB)` from `demote()` and replaces it with a *read-side* check (`stdout_file.read(1_048_577)` → `GuardError`). The write side is now uncapped: the runner (executing a model-mutable task packet, for up to 1800 s) can write arbitrarily to the root-created `TemporaryFile` in `TMPDIR`, and `stderr_file` is never read or bounded at all. That is a filesystem-exhaustion path in a root daemon, introduced by a commit whose stated purpose is bounding resources. Secondary: the cap fires only *after* the run has executed its side effects, so the terminal evidence is discarded post-hoc rather than the run being constrained; and stderr is silently dropped, so timeouts/failures have no diagnostics. Restore an `RLIMIT_FSIZE` (and ideally `RLIMIT_NPROC`/`RLIMIT_AS`) in `demote()`, and bound/read stderr.

**M2 — `os.killpg(process.pid, …)` in the new `finally` runs after the child has been reaped (PID/PGID reuse race).**
`process.wait(timeout=1800)` reaps the child and frees its PID before the `finally: if not timed_out:` block issues `SIGTERM`, `sleep(0.2)`, `SIGKILL` against that same number as a *process group id*. If the PID is recycled as a group leader in that window, a root process signals an unrelated process group — including plausibly the gateway unit or a system service. Only `ProcessLookupError` is swallowed, which does not help here (the recycled group exists). The timeout branch is correct (kill precedes reap); the normal-exit branch is not. Bound the child with a cgroup (systemd scope + `cgroup.kill`) or an intermediate supervisor that stays alive as group leader, rather than signalling a post-reap PID.

**M3 — No snapshot lifecycle; `/run` tree and `prepared` grow without bound.**
`SNAPSHOT_TTL_SECONDS` is enforced only lazily inside `_run_prepared`. Nothing ever removes snapshot directories — not after a successful run, not after `_run_child` fails, and not when `_copy_tree` raises partway (the partial `SNAPSHOT_ROOT/<id>` is left behind while the owner message is already consumed, so the operation is neither completed nor reclaimable). `prepared` entries are likewise never evicted on expiry. `SNAPSHOT_ROOT` is under `/run` (tmpfs), so this is unreclaimed RAM in a root service, at up to `MAX_BYTES` per prepare. A commit titled "bound guard resources" should not leave the snapshot store unbounded; add TTL sweeping plus `finally`-scoped teardown on prepare failure and post-run.

### Minor

- `_copy_tree` accounts `budget["bytes"] += info.st_size` from the pre-open `lstat`, and the error text still reads `"snapshot exceeds file or byte limit"` after the file counter was removed — stale message, and the byte total is declared-size rather than bytes actually copied.
- `MAX_ENTRIES = 64` is reused for both per-directory fanout (`len(names)`) and the cumulative budget, and the cumulative counter now includes directories. A legitimate multi-directory packet can be rejected by a limit that was previously 64 *files*. Use separate constants and distinct messages.
- The new `st_uid`/`st_nlink` checks are taken from the pre-open `lstat`, not from `os.fstat(source)`. The subsequent `st_ino`/`st_dev` equality check makes this mostly sound, but moving both checks onto the opened fd removes the reasoning step entirely.
- Timeout path: `process.wait(timeout=10)` after `SIGKILL` can itself raise `TimeoutExpired`, which escapes uncaught and replaces the intended `GuardError` (e.g. uninterruptible-sleep child).
- `main()` returns `{"error": …, "message": str(exc)}` to the gateway; several `GuardError`s and the `Path.relative_to` `ValueError` embed absolute paths. Trusted peer, so informational only.
- Unconditional `time.sleep(0.2)` on every successful run.
- Scope note (pre-existing, not introduced here): PREPARE is authorized against `packetDigest` + relative path only, while RUN is authorized against a whole-tree manifest hash. The owner approving `RUN ORCHESTRATOR PILOT <digest>` has no way to relate that opaque digest to what they approved in phase one; the binding is sound, the human-verifiability is not.

### Test gaps

- **The central immutability property is untested.** No test mutates the source tree between `_prepare` and `_run_prepared` and asserts the run consumes snapshot content. `test_run_consumes_only_matching_prepared_snapshot` mocks `_run_child` and asserts only `assert_called_once()` — it never inspects the packet path argument, so "run uses the snapshot, not the live tree" is unverified.
- `_run_child` is never exercised: no coverage of the timeout path, the process-group cleanup (M2), the new `finally` block, the stdout > 1 MiB `GuardError`, or the `returncode not in {0,3,4,130}` gate. Every behaviour this commit added to `_run_child` is untested.
- `test_prepare_rejects_unbound_command_and_directory_fanout` creates 65 dirs in one directory, which trips `len(names) > MAX_ENTRIES` first; `assertRaisesRegex(…, "entry count")` matches both messages, so the cumulative cross-directory budget has no coverage. Needs a nested-tree case and distinct messages.
- No coverage for `SNAPSHOT_TTL_SECONDS` expiry in `_run_prepared`, `MAX_DEPTH`, non-regular entries other than symlink (FIFO/device/socket), `st_uid` mismatch (patchable via `pwd.getpwnam`), `_open_packet_dir` traversal rejection (`..`, outside `PACKET_ROOT`), `MAX_REQUEST` oversize framing, or `_gateway_peer`.
- Mode assertions (`0o640`, `0o750`) depend on the test runner's umask, since `os.umask(0o027)` is set only in `main()` and unit tests call `_prepare` directly. They pass at umask 022/027 and fail at 077.
- `test_prepare_rejects_hardlinked_input` introduces `os.link`; the import block is outside the diff context — confirm `os` is imported in the test module.
