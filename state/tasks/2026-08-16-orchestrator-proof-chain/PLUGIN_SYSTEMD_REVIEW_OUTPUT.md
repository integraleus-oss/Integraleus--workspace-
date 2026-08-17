I have enough to complete the review. I did not modify any files, and I did not connect to the guard socket.

## Verdict: **REJECT** — 1 blocker, 3 majors

### Scope

- `projects/orchestrator-auth-boundary/src/index.ts`, `src/index.test.ts`
- `projects/orchestrator-auth-boundary/systemd/orchestrator-guard.service`, `orchestrator-guard.socket`
- Commit range `a9a830e..3da82db`. `guard/orchestrator_guard.py` read only as the counterparty contract, per its separate acceptance.

Deployment state: `/opt/orchestrator-guard` does not exist and no units are installed, so this is a pre-install design review.

---

## Blocker

**B1 — `orchestrator-guard.socket:6-8`: the socket is exposed to every same-UID process, and the only narrowing control is forgeable by the model.**

`SocketMode=0660` + `SocketGroup=stanislav` grants connect rights to the whole `stanislav` group, and `RuntimeDirectoryMode=0750` root:stanislav (`.service:11-12`) makes the directory traversable by that group. So *any* process the model spawns can reach the guard. The required property is "narrowly expose only the Unix socket needed by the active OpenClaw Gateway"; the unit does not narrow beyond UID at all.

The compensating control is `_gateway_peer` (`orchestrator_guard.py:49-60`), which after `SO_PEERCRED` validates the peer by `/proc/<pid>/exe`, `/proc/<pid>/cmdline` and `/proc/<pid>/cgroup`. All four conditions are satisfiable by a process the model launches:

- `uid == stanislav` — the model's tool subprocesses already run as uid 1000.
- `exe == /usr/bin/node` — the model can execute the real `node`.
- `cmdline` must *contain* `/usr/lib/node_modules/openclaw/dist/index.js gateway --port 18789` — argv is chosen by the spawner, e.g. `node /tmp/x.js /usr/lib/node_modules/openclaw/dist/index.js gateway --port 18789` satisfies a substring test.
- `cgroup` must contain `openclaw-gateway.service` — **verified on this host**: `/proc/self/cgroup` for this agent's own tool context reads `/user.slice/user-1000.slice/user@1000.service/app.slice/openclaw-gateway.service`. Children inherit it, and moving into that cgroup is not required because the model is already inside it.

Consequence: the model can bypass the plugin entirely, open the socket directly, and submit a `prepare` request with self-authored `accountId=default`, `channelId=telegram`, `chatId`, `topicId`, `senderId=109592643`, a fresh `timestamp`, an unused `messageId`, and `content` matching the expected PREPARE string for a packet it wrote itself — then the matching `run`. Every stated property falls at once: fabricated trusted inbound metadata, no owner in the loop, arbitrary packet, unattended execution.

I verified the preconditions only; I did not attempt the impersonation.

Note on scope: the forgeable check lives in the separately-accepted Python guard. Under the narrowest reading of scope the finding still stands against `orchestrator-guard.socket` on its own terms — it is the layer that grants access and it provides no narrowing, so it cannot satisfy its stated property regardless of what the guard does. Unix DAC cannot express "the Gateway but not its children" while both run as uid 1000; a real fix needs a distinct uid for the Gateway (with model tool execution under another uid), or an unforgeable peer identity (`SO_PEERSEC` with an LSM label, or pidfd + LSM), not a `/proc` heuristic. `_gateway_peer` additionally has a PID-reuse race, since `/proc` is read after the peer may have exited.

---

## Major

**M2 — `orchestrator-guard.service:11` vs `orchestrator-guard.socket:5`: the service's `RuntimeDirectory` deletes the live socket path.**
`ListenStream=/run/orchestrator-guard/guard.sock` lives inside `RuntimeDirectory=orchestrator-guard`. With the default `RuntimeDirectoryPreserve=no`, systemd removes `/run/orchestrator-guard` recursively every time the service stops — including each `Restart=on-failure` cycle (`.service:37`). The socket unit keeps its listening fd and does not notice, so the bound inode is gone and every subsequent Gateway connect fails with `ENOENT` until the socket unit is manually restarted. A single transient guard crash becomes a permanent outage. Fail-closed, so not itself an escalation, but the boundary is not operable as committed. Set `RuntimeDirectoryPreserve=yes` (or move `ListenStream` outside the runtime directory).

**M3 — `orchestrator-guard.socket:7`: `SocketUser=orchestrator-guard` refers to a user that does not exist.**
`/etc/passwd` has no `orchestrator-guard` entry, the service runs `User=root` (`.service:9`), and no sysusers/tmpfiles fragment ships with the change — only prose in `SECURITY_PRECHECK.md:8`. systemd refuses to start a socket unit whose `SocketUser=` cannot be resolved, so the unit set as committed cannot start. The direct security impact is fail-closed; the significance is that this boundary has never been executed, so none of its runtime properties have been observed. It is also cosmetic as written: access is granted by `SocketMode=0660` + `SocketGroup=stanislav` regardless of the owning user.

**M4 — neither unit enforces or asserts that the guard code and runner are root-owned.**
`ExecStart` runs `/opt/orchestrator-guard/orchestrator_guard.py` (`.service:8`) and the guard execs `/opt/orchestrator-guard/runtime/production_cycle_cli.py` (`orchestrator_guard.py:22`). `ProtectSystem=strict` only stops *this service* from writing there; it says nothing about the model, which is the actual adversary. If `/opt/orchestrator-guard/runtime` is writable by `stanislav`, the model rewrites the program that executes under the owner's approval and the whole two-phase chain is decorative. There is no `ExecStartPre` ownership/mode assertion, and the path does not exist yet, so the property required of this review ("systemd must keep guard code/runtime root-owned") is currently neither enforced nor verifiable.

---

## Minor

1. **`index.ts:37-39, 109` — `preparedBySession` is never purged.** `purge()` only expires `inboundBySession`. Every PREPARE without a matching RUN leaks an entry for the process lifetime, and entries outlive the guard's 1800 s snapshot TTL. Fail-closed (the guard rejects expired snapshot ids), but it is unbounded growth in a security-relevant map.
2. **`index.ts:88-133` — session binding rides on a cached tool descriptor.** `ctx.sessionKey` is captured in the `registerTool` factory closure. The runtime's descriptor cache key (`tools-V54L2wjJ.js:67-86`) includes `requesterSenderId`/`senderIsOwner`/`deliveryContext` but **omits `sessionKey` and `sessionId`**, and `descriptorCache` is a process-global LRU. The `ctx` an `execute` closes over is therefore not guaranteed to belong to the invoking session, so authorization state can be consumed under a different session's key for the same owner and delivery context. Content and digest binding still gate the action, which is why this is minor rather than major.
3. **`index.ts:80, 104-105` — the plugin never validates `accountId` or `channelId`.** "account `default`" and Telegram are enforced only at `orchestrator_guard.py:64`. End-to-end the property holds and unset values fail closed, but the component with the trusted inbound view does not enforce a constraint it is uniquely positioned to check.
4. **`index.ts:29-33, 100` — canonical/literal root mismatch.** The containment check uses `realpath(PACKET_ROOT)` while `relativePacket` slices by the literal `PACKET_ROOT.length`. If any component of the packet root is ever a symlink, the two diverge and PREPARE can never match the owner's message (the guard's `relative_to(PACKET_ROOT)` at `orchestrator_guard.py:189` would also raise). Fail-closed, but silently, and the failure mode is opaque. Slice by `root`.
5. **`orchestrator-guard.service:23` — `RestrictAddressFamilies` includes `AF_INET AF_INET6 AF_NETLINK`** and there is no `IPAddressDeny=any`, `SocketBindDeny=any`, or `SystemCallFilter=@system-service`. The guard itself needs only the passed `AF_UNIX` fd; the breadth appears to exist for the demoted child, which inherits the sandbox. Worth documenting as deliberate, or splitting the child's execution environment.
6. **`orchestrator-guard.service:22` — `ReadWritePaths=/home/stanislav/agent-runs`** grants a root-context service write access into a user-controlled directory. The guard never writes there today (only the demoted child does, as `stanislav`), so this is unnecessary symlink-attack surface. It also has no `-` prefix, so a missing directory fails the unit.
7. **Startup ordering leaves a permissions window.** The socket unit starts first and systemd creates `/run/orchestrator-guard` as a `ListenStream` parent at mode 0755 root:root; the service's `RuntimeDirectoryMode=0750` root:stanislav is applied only when the service later starts.

## Nits

- `index.ts:74` — the chat id is scraped from `conversationId` with an unanchored greedy `/(-100\d+)/` and only the first match is considered. I could not construct a widening case (greedy matching plus first-match-only fails closed), but a structural comparison against a canonical field beats regex-scraping an identifier in an authorization path.
- `index.ts:122-124` — RUN omits the `inbound.senderId !== ctx.requesterSenderId` cross-check that PREPARE performs at line 97. Equivalent today because entries are only stored for `OWNER_ID`, but the asymmetry is a latent gap.
- `index.ts:38` — TTL uses wall-clock `Date.now()`; a backwards clock jump extends inbound validity. The guard's independent 120 s check on the message timestamp limits this.
- `src/index.test.ts` — three tests, none covering the security-relevant paths: no owner mismatch, no content/digest mismatch, no replay, no expiry, no malformed guard response, no socket failure. The mismatch and restart cases the threat model names are untested at this layer.
- Snapshot ids are not opaque to the model: `/run/orchestrator-guard/snapshots` is 0750 root:stanislav with 0640 files, so the model can enumerate ids and recompute `snapshotDigest`. This is forced by design (the demoted child must read the snapshot), and integrity holds since the group has no write bit — but the security of RUN rests entirely on the owner content binding, not on the id being secret.

## What holds

- Two-phase separation is sound: PREPARE binds path + digest, RUN carries only the opaque snapshot id, and both are re-verified server-side (`orchestrator_guard.py:186-192, 302-311`).
- Single-use is enforced at both layers — map deletion before the guard call in the plugin (`index.ts:98, 128`) and the on-disk `O_EXCL` marker in the guard's `StateDirectory`, which correctly survives restart.
- Restart fail-closed is correct: both plugin maps and the guard's `prepared` dict are in-memory, and `RUN` accepts no caller-supplied snapshot id.
- Request construction is exact — `sessionKey: undefined` / `observedAt: undefined` are dropped by `JSON.stringify`, producing precisely the guard's required key set for both actions.
- Socket-activation hygiene matches: `Accept=` defaults to no, and the guard verifies `LISTEN_PID`/`LISTEN_FDS==1` before trusting fd 3.
- No automatic commit, transfer, push, deploy, cron, timer, or unattended execution appears in either unit or in the plugin. `Restart=on-failure` restarts a listener, not a pilot run.

The single change that would most improve this boundary is giving the Gateway an identity the model cannot assume — everything else in the chain is already bound correctly.
