No tools used; review is from the filtered packet only.

# Verdict: REWORK

`e5db7c4` genuinely closes the main authorization gap from the `a9a830e` review — the owner message must now be exactly `RUN ORCHESTRATOR PILOT <digest>`, so a model-chosen packet fails at both the plugin (`src/index.ts:99`) and the guard (`guard/orchestrator_guard.py:74`). Socket-activation assertion (`:163`), the framing loop (`:129-141`), and the systemd hardening additions are also real improvements. But the new `_stage_packet` step introduces one functional blocker and one root-side hazard, so the combined result is not safe/ready to install even for one controlled pilot.

## Blockers

1. **`orchestrator_guard.py:82-93,145` — the staged packet is unreadable by the demoted runner, so every pilot run fails.** `_stage_packet` copies into `/var/lib/orchestrator-guard/staged/<hex>`, and the unit sets `StateDirectory=orchestrator-guard` with `StateDirectoryMode=0700` owned by `root`. `_run` (`:103-115`) drops to `stanislav` via `preexec_fn`, then passes that path as argv. The child gets `EACCES` traversing `/var/lib/orchestrator-guard`. It fails closed, but the run never happens, the runner emits no JSON terminal line → `GuardError("runner did not produce structured terminal evidence")` — *after* the single-use replay marker at `:147-153` has already been burned. Each attempt costs the owner a fresh message.

2. **`orchestrator_guard.py:84-89` — root recursively copies a model-writable directory, guarded only by a TOCTOU scan.** `PACKET_ROOT` is the agent's own `state/tasks`, which the model can write. The `is_symlink()` pre-scan at `:84` and `copytree(..., symlinks=False)` at `:89` are separate passes; a symlink created in the window is *followed* (a symlink to a directory makes `copytree` recurse into it), giving an unbounded root-side read/copy primitive into a root-only tree, plus blocking reads on `/proc`-style pseudo-files. Independently of the race, the copy is unbounded in size and time with no limit and no cleanup: sibling task dirs in this very workspace hold hundreds of MB of `.blend`/asset trees, so a legitimate run can fill `/var/lib` and stall the single-threaded accept loop.

## Majors

3. **`orchestrator_guard.py:145` — authorization binds one file, but the runner is handed a whole directory.** Only `packet.name` is digest-checked (`:91`); every sibling file copied at `:89` is unauthenticated and model-mutable up to the moment of the copy. "Exact packet digest" is not what actually gates the run's inputs.

4. **`src/index.ts:82` — `event.content` is used raw, unverified and uncoerced.** Every other field goes through `String(...)`; `content` does not, and `Inbound.content` is declared `string`. If the inbound-claim payload exposes the text under a different key or as structured content, `inbound.content.trim()` at `:99` throws and the whole mechanism is dead — or worse, silently binds nothing. Nothing in the packet demonstrates this field exists on a real event; the new test at `index.test.ts` constructs the `Inbound` literal by hand, so it cannot catch this.

5. **`orchestrator_guard.py:112` — `start_new_session=True` breaks timeout containment.** On `timeout=1800`, `subprocess.run` kills only the session leader; the detached run tree survives until the service itself is stopped. `TimeoutExpired` also escapes `_run` uncaught (it is not a `GuardError`), landing in the generic handler at `:171` with the replay marker already consumed and processes possibly still running.

6. **`orchestrator_guard.py:113` — PATH now includes `/home/stanislav/.local/bin`, which the model can write.** No privilege gain (the child is `stanislav` either way), but every tool the runner resolves by name inside the "controlled" run becomes model-controlled. This was added by the closure commit and widens model influence over the guarded run.

7. **`orchestrator_guard.py:174` — `conn.sendall` sits outside the `try` at `:169-173`.** A peer that disconnects, or an `_audit` failure, raises out of the accept loop and terminates the daemon after the run has already executed: result lost, message consumed. `Restart=on-failure` recovers the service but not the evidence.

8. **`orchestrator_guard.py:121` — exit code `3` newly accepted with no stated meaning.** The guard then returns `{"ok": True, ...}`; terminal-status fidelity for the pilot depends on an undocumented runner convention.

9. **`systemd/orchestrator-guard.service` — `PrivateNetwork=yes` plus `RestrictAddressFamilies=AF_UNIX` are inherited by the demoted child**, and `ProtectHome=read-only` with `ReadWritePaths=.../agent-runs` means the run cannot write back into the task dir it was staged from. This is fine (good, even) if the runner is a pure local-filesystem cycle; if it needs an API call or writes evidence next to the packet, the pilot cannot produce a meaningful result. The runner's I/O contract is not in this packet, so this needs verifying before install.

10. **Reachability of the socket is unverified.** `RuntimeDirectory=orchestrator-guard` / `RuntimeDirectoryMode=0750` with `User=root Group=root` yields a `root:root 0750` directory that `stanislav` cannot traverse. The `.socket` unit is outside the filtered pathspec, so I cannot confirm `SocketUser`/`SocketGroup`/`SocketMode` or the directory ownership it establishes.

11. **`--guard-authorized` is an argv flag, not an authorization.** The spec item "old adapter and direct hidden CLI flag fail closed outside the guard parent/cgroup" is enforced in the runner, which is not in this packet — unverifiable here. Note the flag is world-visible via `ps`; if the runner treats it as sufficient, the boundary is bypassable by any same-UID process.

12. **`orchestrator_guard.py:145` before `:147-153` — side effects precede the replay check.** `rmtree` + `copytree` execute before the `O_EXCL` marker, so a replayed request performs the full root-side copy before being rejected.

## Minors

- `LogsDirectoryMode=0750` root:root makes `audit.jsonl` unreadable to the pilot operator without `sudo`; `_audit` at `:172` also writes raw `str(exc)`, which includes packet paths.
- No supplementary groups after `os.setgroups([])` (`:106`) — any group-based file access in the run fails.
- No `StartLimitBurst`/`StartLimitIntervalSec` alongside the new `Restart=on-failure`; a crash loop can take the socket unit down.
- No `SystemCallFilter=`; `MemoryMax=1G` but no disk bound on `staged/`, which is never pruned.
- 120s freshness (`MAX_AGE_SECONDS`) is measured from the Telegram message timestamp; a slow model turn expires a legitimate command.

## Test gaps

- `_stage_packet` has **no test at all** — not the symlink rejection, not the staged-digest re-verification, not the `rmtree`/`copytree` path, not the readability of the result by the demoted child (which would have caught blocker 1).
- `_gateway_peer` is untested: no coverage of wrong UID, wrong `exe`, wrong cmdline, wrong cgroup, or PID-reuse behavior. This is the root of the whole guard.
- Replay single-use (`O_EXCL` at `:150`) is untested; so is concurrent/duplicate delivery.
- `handle()` framing is untested: split writes, oversize, missing trailing newline, embedded newline, 5s timeout expiry.
- `_run` untested: demotion, env, `timeout`, and specifically the newly widened `{0, 3, 4, 130}` set.
- Guard content checks: no case for a missing/non-string `content`, and none where the content digest names a *different* packet than `packetPath`.
- Plugin: the tool itself is untested — owner gating, single-use consumption of `inboundBySession`, the content-vs-digest rejection at `:99`, and the exact JSON key set sent to `callGuard` (`:102-103` relies on `JSON.stringify` dropping `sessionKey`/`observedAt` to satisfy the guard's strict `set(request) != required`; a rename breaks it only at runtime).
- `index.test.ts` "rejects packets outside the fixed task root" depends on `PACKET_ROOT` existing on the test host; elsewhere it throws `ENOENT` and the `toThrow("outside")` assertion fails for the wrong reason.
- No negative test that an ordinary same-UID non-Gateway process is refused, and none that the old user-space adapter / `--guard-authorized` path fails closed outside the guard's parent/cgroup.

**Minimum to reach ACCEPT:** fix the staged-path readability (or drop staging in favour of an atomic root-side re-read of the single digest-bound file), eliminate the root-side directory copy of model-writable content (or bind a manifest digest over every file consumed), coerce/validate `event.content` against the real inbound payload, and move `sendall` inside the loop's `try`.
