## Verdict: ACCEPT — no blockers, no majors found

The commit's security-relevant changes hold up. The `WNOWAIT`-then-`killpg`-then-`waitpid` sequence is the correct fix for the PID/PGID-reuse hazard in the old code: the unreaped zombie leader pins the pgid so the group kill cannot land on a recycled group, and signalling a zombie leader does not alter the already-latched wait status, so `returncode` is still the runner's true exit. Snapshot lifecycle is now closed on all three paths (copy failure, TTL expiry, post-run), and `shutil.rmtree` is fd-based on Linux while `SNAPSHOT_ROOT` is `0750 root:stanislav` — the model cannot plant a symlink inside a snapshot to redirect the root-owned delete. PREPARE/RUN separation, digest binding, replay consumption, and expiry are untouched and intact.

### Minor

1. `_run_child` no longer has a `try/finally` around `Popen`. If thread creation raises between `Popen` and `_wait_without_reaping`, the child is left running, unreaped, and unsupervised, and `_run_prepared`'s `finally` deletes the snapshot out from under it. The old code guaranteed group termination.
2. Timeout/overflow paths call `os.waitpid(pid, 0)` with no bound; the old code used `process.wait(timeout=10)`. The guard is a single-threaded accept loop, so a child stuck in `D` state wedges the whole service rather than failing the one run.
3. `_terminate_group` gives SIGTERM only 200 ms before SIGKILL, down from 10 s. On the timeout path the runner effectively loses its graceful-shutdown window.
4. `thread.join(timeout=2)` can expire while a drain thread is still appending. A leaked drain thread then survives into the next run's `Popen`, which uses `preexec_fn` — fork-in-a-multithreaded-process, the classic pre-exec deadlock hazard. Separately, a timed-out join yields truncated stdout, so a successful run is reported as `did not produce structured terminal evidence` after its side effects already landed.
5. Overflow is a single shared `Event`, so a chatty **stderr** now aborts an otherwise-successful run at 1 MiB (previously stderr was unbounded and ignored). Fail-closed, but the message consumption and snapshot delete are already done, so recovery requires a fresh PREPARE/RUN pair.
6. `_purge_expired` only walks the in-memory `prepared` dict. Snapshot directories orphaned by a guard restart are never reclaimed — unreachable for auth purposes, but they accumulate in `/run` until reboot.
7. The manifest carries files only, so the snapshot digest does not bind empty directories. No substitution attack follows from it (the owner approves a digest computed over the tree just staged), but "whole-tree binding" is not literally whole-tree.
8. Test file damage: the new tests were spliced into the middle of `test_framing_supports_split_stream_and_rejects_multiple_records`, so its multi-record rejection assertions are now the tail of `test_expired_snapshot_is_removed`. Both still execute, but the framing test no longer tests what its name claims.

### Test gaps

- Neither error branch of `_wait_without_reaping` is exercised — no test for the timeout `GuardError` or for the overflow `GuardError`. Only the normal-exit branch is covered; `_bounded_drain` is tested in isolation, never wired through a real child.
- No test that the snapshot directory is removed after RUN (success and failure), nor that a partial snapshot is cleaned up when `_copy_tree` raises — both are new behaviour in this commit.
- No end-to-end test that mutating the source tree between PREPARE and RUN does not affect the run, i.e. that `_run_child` receives the staged copy. This is the central property of the design and is currently only implied by construction.
- No test that `handle()` triggers the purge; `_purge_expired` is only called directly.
- `_copy_tree` rejection branches for non-regular entries (symlink/FIFO/device), `MAX_DEPTH`, and `MAX_BYTES` are untested; only entry count and link count are.
- `test_wait_kills_background_process_group_before_reap` depends on the orphaned `sleep` being reaped by the subreaper within `_terminate_group`'s 200 ms sleep. Usually fine, mildly flake-prone under load or a non-reaping subreaper.
