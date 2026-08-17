## Verdict: REJECT — 1 blocker, 5 majors

### Blocker

**B1. RUN phase cannot work: the demoted runner cannot reach the snapshot.**
`main()` does `SNAPSHOT_ROOT.mkdir(mode=0o750, ...)` with no `chown`, so `/run/orchestrator-guard/snapshots` is `root:root 0750`. `_copy_tree`/`_snapshot_owner` only chown the *per-snapshot* dir to `root:<stanislav gid>`, so the group-readable snapshot sits behind a directory `stanislav` cannot traverse. `_run_child` demotes to `stanislav` and passes `record["packet"]` as argv → `EACCES` on every real run. The "snapshot readability" requirement fails outright. Fix: chown `SNAPSHOT_ROOT` to `root:<stanislav gid>` (or mode `0711`) in `main()`, and assert readability as the target uid in tests. Fully masked today because `_run_child` is mocked.

### Major

**M2. TOCTOU escape from the approved root in `_open_packet_dir`.** `resolve(strict=True)` + `is_relative_to(root)` is a path-string check; the guard then re-traverses that path with `os.open(canonical.parent, O_NOFOLLOW)`. `O_NOFOLLOW` protects only the *final* component, so the model (which owns the tree) can replace any intermediate directory with a symlink after the check and have root open, read, and copy a tree outside `PACKET_ROOT` into a group-readable snapshot. The `staged_packet` digest re-check only pins one file, not the location. Fix: walk components with `openat`/`O_NOFOLLOW` from a fd on `PACKET_ROOT`, or verify `fstat(dir_fd)` dev/ino against a fd-based traversal — not against a re-resolved path.

**M3. Directory fd leak on every failure path in `_open_packet_dir`.** `directory_fd` is opened outside any `try`; the digest-mismatch `GuardError` (and a failing `os.open(canonical.name, ...)`) propagates without closing it. In a long-lived root daemon, repeated rejected requests exhaust the fd table and kill the accept loop. Wrap in `try/except: os.close(directory_fd); raise`.

**M4. Timeout cleanup is incomplete and can orphan the runner.** `os.killpg(pid, SIGTERM)` has no `SIGKILL` escalation, and the follow-up `process.communicate(timeout=10)` runs *inside* the `except` block: if the group ignores SIGTERM, `TimeoutExpired` propagates in place of the `GuardError`, leaving a live, unreaped process group holding the snapshot and stdio pipes. Escalate to `killpg(SIGKILL)` in a `finally`/second-stage and always reap.

**M5. Audit trail no longer proves admission.** The old pre-execution `admitted` record was dropped; the single success record is written *after* the phase completes, using `now` captured before execution. If `_run_child` raises (bad terminal evidence, disallowed exit code, timeout), the only record is `{"event":"REJECTED","error":<type>}` with no `messageId`, `snapshotDigest`, or `gatewayPid` — a run that actually executed is unattributable. Also, on the success path an `_audit` failure converts a completed run into an error response, while on the reject path `except Exception: pass` silently swallows audit failures (fail-open on logging). Log admission before executing, and include identifiers on rejection.

**M6. Owner never authorizes *which* tree runs.** `PREPARE` content is the constant `"PREPARE ORCHESTRATOR PILOT"` — no packet path or digest binding — and the response returns only an opaque `snapshotDigest` that the owner echoes back verbatim. The manifest digest covers relative paths + content, not the packet identity/location, and nothing owner-legible is surfaced. Given the stated threat model (model mutates the source task tree, and thus influences what the plugin submits as `packetPath`), the two-phase flow proves "the run matches the snapshot", but not "the owner approved *this* packet". Bind `packetPath` into the PREPARE command text and return a human-readable manifest summary alongside the digest.

**M7. Unbounded runner output buffered in the root process.** `Popen(stdout=PIPE, stderr=PIPE)` + `communicate()` with no cap: the runner's output (influenced by model-controlled packet content) is accumulated in the root guard's memory for up to 1800s. `MAX_BYTES` bounds input only. Cap the captured stream and truncate.

### Minor

- No GC anywhere: expired `prepared` entries and their snapshot directories are never deleted (TTL only gates `run`), and `/run` is tmpfs — snapshots accumulate in RAM and are lost across restarts, so they are neither cleaned nor durable evidence.
- Oversized packets surface as `"packet digest mismatch"` (digest computed over `read(MAX_BYTES + 1)`), a misleading error for a limit violation.
- `str(...).isdigit()` accepts non-ASCII digits (`'²'`, fullwidth forms) while replay markers hash the exact bytes; use `isascii() and isdigit()`.
- `__pycache__`/`.git` are silently excluded from both the copy and the manifest digest — undocumented holes in "whole-tree binding".
- All snapshot files are written `0640`, dropping exec bits; will break any runner that executes a script from the packet tree.
- The pervasive `a; b` / one-line `if x: y` compression in a security-critical file (and in `main()`'s error handling) materially hurts reviewability; several of the defects above are hidden by it.

### Test gaps

1. **Permissions/ownership are never asserted** — no test that the target uid can traverse+read the snapshot (would have caught B1), and no test that files/dirs are non-writable by `stanislav` (immutability is claimed but untested; `test_prepare_creates_readable_immutable_snapshot_and_run_command` only calls `read_text()` as the test user and never checks a mode, uid, or gid).
2. **`_run_child` is entirely mocked**: no coverage of timeout/`killpg` cleanup, SIGTERM-ignoring child, exit-code allowlist `{0,3,4,130}`, non-JSON terminal line, empty stdout, or the demotion `preexec_fn`.
3. **No TOCTOU tests**: intermediate-directory symlink swap (M2), packet replaced between the digest check and `_copy_tree` (the `staged_packet` re-check is never exercised), file growing/shrinking mid-read, `st_ino`/`st_dev` change guard.
4. **Coverage regressions**: the deleted `test_rejects_symlink_and_outside_packet` and `test_rejects_extra_fields` were not replaced — packet outside `PACKET_ROOT`, symlinked `packetPath`, extra/unknown request keys, and unknown `action` are now all untested; `_run_prepared`'s required-key set and `run` content-binding mismatch are untested.
5. **Limits**: only `MAX_BYTES` is tested; `MAX_FILES`, `MAX_DEPTH`, and non-regular entries (fifo/socket/device) are not.
6. **Expiry/replay**: `SNAPSHOT_TTL_SECONDS` expiry, unknown `snapshotId`, and the action-scoping of `_consume_message` (same `messageId` for `prepare` vs `run`) are untested.
7. **Framing/peer**: no test for EOF without newline, `> MAX_REQUEST`, non-object JSON, malformed JSON, or `recv` timeout; `_gateway_peer` has zero coverage.
8. **Audit**: no test asserts any audit record shape or that admission is logged before execution.
