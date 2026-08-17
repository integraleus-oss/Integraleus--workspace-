## Verdict: **REWORK** — do not install for the pilot

3 blockers, 8 majors. The root guard as written does not establish the property it exists to establish, and the pilot would very likely fail closed after burning its single-use authorization.

---

### Blockers

**B1. The guard authenticates the channel, not the owner message — the Gateway self-attests.**
`guard/orchestrator_guard.py:62-76` validates `senderId`/`chatId`/`topicId`/`messageId`/`timestamp` only against hardcoded constants; every one of those values is **data supplied by the peer** over the socket. `_gateway_peer` (`:35-46`) proves only that the writer is the Gateway process. Anything executing inside that process — including a prompt-injected tool call, which is precisely the threat this boundary exists to stop — can mint `messageId = <fresh digits>`, `timestamp = now` and start a run. The guard has no independent evidence that an owner message ever existed. Root ownership buys audit integrity and replay-state integrity, nothing more; against the stated adversary the boundary is equivalent to the user-space adapter it replaces. Spec axis bullet 1 is not met.

**B2. Consent is not bound to the packet, and the previous binding was deleted.**
`src/index.ts:78-83` caches *any* matching owner message for 120 s; `src/index.ts:91-99` then consumes it for a `packetPath` chosen by **the model**, not by the owner. An unrelated owner "ok" in topic 2922 authorizes an arbitrary packet under the task root for the next two minutes. The removed adapter (`openclaw_foreground_adapter.py`, old `_admit_authorization`) bound `packet_digest` + `approved_by` + `source_message_id` to an owner-approved artifact in a trusted registry. That property is a net regression, not a migration.

**B3. Packet digest is TOCTOU-defeated.**
`orchestrator_guard.py:57` hashes the canonical path; `:92-96` passes the *path* to the child, which re-reads it as uid `stanislav`. `PACKET_ROOT` (`:17`) is user-writable, and the child runs as the same uid. Swap the file between verify and read and the digest pins nothing. The digest must be bound by copying the packet into a root-owned staging dir (or passing an O_PATH/`/dev/fd` handle) before dropping privilege.

---

### Majors

**M1. `ProtectHome=read-only` + minimal `PATH` will break the pilot, and the failure is unrecoverable.**
`systemd/orchestrator-guard.service:22-23` grants RW only to `/var/lib`, `/var/log`, `/home/stanislav/agent-runs`. `production_cycle_cli.py` accepts `/home/stanislav/projects` as a `SAFE_PROJECT_BASES` target — read-only in this namespace. `_run` (`:95`) sets `PATH=/usr/local/bin:/usr/bin:/bin` and no `USER`/`LOGNAME`, so nvm/npm-global `codex`/`claude` binaries and `~/.codex`/`~/.claude` state are unreachable; `PrivateDevices=yes` also removes any TTY. Because the replay marker is created at `:118-122` *before* `_run`, a failed pilot leaves the marker consumed with no documented reset path — only root can clear `/var/lib/orchestrator-guard/used`.

**M2. Stream framing is wrong and the guard can be hung indefinitely.**
`orchestrator_guard.py:109-111` does a single `conn.recv()` and requires a trailing newline. On a SOCK_STREAM a fragmented write fails the framing check spuriously; there is no read loop. There is also no `conn.settimeout()`, and `main` (`:131-141`) is single-threaded, so a peer that connects and never sends blocks `accept()` forever.

**M3. Chat binding is a substring regex, and the guard's `chatId` check is vacuous.**
`src/index.ts:72-73` extracts the chat via `String(conversation).match(/(-100\d+)/)` — an unanchored match against an unspecified composite identifier. `src/index.ts:80` then sends `chatId: CHAT_ID` (the constant), so `orchestrator_guard.py:67-70` merely re-checks its own constant. The only real chat binding is that regex.

**M4. Plugin does not build and its tests do not run.**
`package.json:7-10` invokes `tsc -p tsconfig.json` and `vitest run --config ./vitest.config.ts`; neither file exists in the commit. `npm test` fails before reaching the Python suite. `devDependencies.openclaw: "latest"` (`:26`) is an unpinned floating dependency in a security-critical plugin.

**M5. `FAILED_INFRA` is misclassified as a guard failure.**
`orchestrator_guard.py:102-103` accepts `{0, 4, 130}`. `production_cycle_cli.main` returns 3 for `FAILED_INFRA` — a legitimate terminal status. That path raises `GuardError`, discards the parsed result, and skips the `terminal` audit record (`:126`), leaving the run's outcome recorded only as `rejected`.

**M6. `socket.fromfd(3)` without socket-activation validation.**
`orchestrator_guard.py:132` assumes fd 3 is the listener. `LISTEN_FDS`/`LISTEN_PID` are never checked, and the unit (`orchestrator-guard.service:6-7`) has no guard against a manual `systemctl start orchestrator-guard.service`, where fd 3 is whatever systemd happened to leave open.

**M7. Entire OpenClaw SDK surface is unverified and untested.**
`src/index.ts:6` (`openclaw/plugin-sdk/plugin-entry`), `:67` hook id `inbound_claim`, and the fields `event.senderIsOwner`, `event.threadId`, `event.timestamp`, `ctx.requesterSenderId`, `ctx.sessionKey` are asserted, not demonstrated. Note the failure mode is fail-closed (a missing field means the hook returns early and the tool always throws), plus a type hazard: `senderId !== OWNER_ID` at `:75` is a strict compare against a string, so a numeric sender id never matches while `:80` coerces with `String()`. Install would need each field confirmed against the installed SDK version first.

**M8. Freshness is not provable.** `src/index.ts:77` falls back to `Date.now()` when `event.timestamp` is absent, so `MAX_AGE_SECONDS` (`orchestrator_guard.py:23`) bounds *observation* time, not message time.

**M9. Root unit hardening is incomplete for a full-capability root service.**
`orchestrator-guard.service` sets no `CapabilityBoundingSet=` (root retains all caps though only `setuid`/`setgid` are needed), no `SystemCallFilter=@system-service`, no `PrivateNetwork=yes` (only `RestrictAddressFamilies`), no `RestrictNamespaces=`, `ProtectKernelTunables/Modules/Logs=`, `ProtectControlGroups=`, `UMask=`, `MemoryMax=`, and no `Restart=`. Combined with `:141` — an exception inside the `except` handler's `_audit` (disk full, EPERM) escapes the loop and exits the process — availability depends on socket re-activation with no restart policy.

---

### Minors

- `orchestrator_guard.py:36-41`: PID-reuse window between the SO_PEERCRED snapshot and the `/proc/<pid>` reads; re-verify via `/proc/<pid>` start-time or an fd pin.
- `:92-96`: `capture_output=True` buffers up to 30 min of agent output in the root process; no `MemoryMax`. `completed.stderr` is never audited or returned, so failures are undiagnosable.
- `:92-96`: no `start_new_session`; on `TimeoutExpired` the direct child is killed but agent grandchildren survive.
- `src/index.ts:44,48`: the 1,810 s timer is cleared only in the `end` handler, leaking on the error path.
- `production_cycle_cli.py:34`: `"Uid:\t0\t0\t0\t0"` is a brittle literal parse of `/proc/<pid>/status` and assumes a cgroup-v2 string shape.
- `ROLLBACK.md`: no `daemon-reload`, no post-rollback verification commands, and no procedure for clearing a consumed replay marker (see M1).
- Legacy (non-1.3) packets: `main()` still reaches `run_packet` without any guard authorization; the schema gate at `run_packet` covers only `1.3.0`. Whether `_run_loaded_packet`'s `allow_legacy=False` blocks execution is not visible in this filtered packet — confirm before install, since a residual unauthorized run path would negate the boundary.

---

### Test gaps

1. **`_gateway_peer` is entirely untested** — the peer UID / exe / cmdline / cgroup check is the security core of the root guard and has zero coverage, including the non-Gateway-peer rejection case.
2. **Replay coverage regressed.** The old suite's `test_authorization_copy_cannot_replay` was deleted; the guard's `O_CREAT|O_EXCL` marker at `orchestrator_guard.py:118-122` has no replacement test.
3. **No test for `handle` framing** — short read, missing newline, oversize request, or hung peer.
4. **No test for `_run`** — exit-code mapping (notably 3), non-JSON terminal output, empty stdout, timeout, or the `demote` ordering.
5. **Zero TypeScript tests.** `export const testing` at `src/index.ts:60` exists but nothing exercises `inspectPacket` (symlink/outside-root), `purge` TTL, the chat regex, the owner check, or `callGuard` response handling — and the harness config files are missing (M4).
6. **`test_guard_flag_admits_only_after_parent_check` patches out the thing under test.** `_guard_parent_authorized`'s actual `/proc` parsing is never exercised against real files.
7. **`_validate` coverage is partial** — no cases for `action`, `accountId`, `channelId`, non-digit `messageId`, future timestamps beyond the +5 s skew, or non-string/non-int types.
8. **No end-to-end socket test** and no negative test proving a non-Gateway process on the same UID is rejected.
9. **No systemd verification step** (e.g. `systemd-analyze security orchestrator-guard.service`) is wired into the precheck's stop conditions.

---

### If you want a minimal path to a *safe* pilot

The cheapest fix for B1/B2 that keeps the design: have the guard fetch the referenced message itself (root-side Telegram read via a root-only credential) and require the owner message body to contain the packet digest — so the packet is approved by the owner, not chosen by the model. Failing that, restore the owner-signed authorization artifact from the old adapter and have the guard validate it against a **root-owned** registry outside `/home/stanislav`. B3 needs a root-owned copy of the packet before privilege drop; M1 needs the real project/agent paths in `ReadWritePaths` plus a resolved `PATH`, validated by a dry run before the marker is consumed.
