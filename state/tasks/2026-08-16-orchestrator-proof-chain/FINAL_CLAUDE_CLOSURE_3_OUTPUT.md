# Review of `9ca557a` against M1–M4

## Blockers
None.

## Major

**1. The "trusted" registry and the global ledger are both writable by the principal the gate constrains (`openclaw_foreground_adapter.py:_admit_authorization`).**
`AUTHORIZATION_REGISTRY` sits at `state/tasks/2026-08-16-orchestrator-proof-chain/manual-authorizations.json` — inside the same worktree this agent authors and commits — and `AUTHORIZATION_LEDGER` is a plain directory under `$HOME/agent-runs/`. Nothing in the packet establishes out-of-band ownership (signature, root-owned mode, append-only store). Under the threat model this control exists for — an agent must not self-authorize a foreground production run — a party that can write the authorization file can also append its own `{authorization_digest, packet_digest, source_message_id}` triple to the registry and `rm` the ledger marker. The path is *fixed*; *trusted* is unverified. Two aggravating sub-points: registry entries never expire or get consumed, so ledger durability is the sole replay defense, and `agent-runs/` is exactly the kind of directory subject to cleanup; and `mkdir(parents=True, exist_ok=True)` will happily recreate a deleted ledger, silently restoring replayability. I cannot inspect file modes from this packet — if the registry is root-owned and read-only to the agent, this drops to informational, but that fact is not evidenced anywhere in the commit or the tests.

**2. Packet content is not pinned between authorization and execution (`openclaw_foreground_adapter.py:run_one`).**
Order is: `load_packet(packet_path)` → schema/control-mode gate → `_admit_authorization` (which computes `_digest(packet_path)`) → `run_packet(packet_path)`. The packet file is opened four separate times, and the bytes that satisfied `packet_digest` are never the bytes handed to the orchestrator. The schema gate is likewise applied to an earlier, independent read. A swap between the digest check and `run_packet` executes unauthorized content under a consumed, "valid" ledger marker. Read once, verify the digest against those bytes, and pass the verified content (or an open fd) to `run_packet`.

**3. The untracked-file branch of `project_state` still slurps whole files (`blind_acceptance.py:project_state`).**
M3 as literally stated is satisfied — the ignored-file loop now chunks at 1 MiB. But the `??` loop three lines above is unchanged: `digest.update(raw + b"\0" + path.read_bytes())`. This worktree's untracked set is dominated by `.blend` files and asset trees, so the memory blow-up the fix targets is still reachable on the more likely path, and it runs twice per verification sweep (before and after). Neither loop guards `OSError`: a file listed by `git status`/`ls-files` and removed before the read raises `FileNotFoundError` straight out of `project_state`, and `MemoryError` does the same — both escape the `BlindAcceptanceError` contract rather than producing a structured failure.

## Minor

- **M2 is true but load-bearing on nothing.** `authorization_digest` is the SHA-256 of the whole authorization file, which already covers `packet_digest` and `source_message_id`; requiring the registry to also match those two fields is redundant, and the derived `identity` hash is likewise fully determined by the file content. The registry check reduces to a digest allowlist. More importantly, `source_message_id` is validated only as a non-empty string and is never checked against any actual message source — "registry-bound" means "an operator typed the same string twice," not "this authorization traces to a real owner message."
- **Ledger marker records intent, not outcome.** The marker is written before `run_packet` and never finalized; it carries no run id, run_dir, timestamp, or terminal status, so the ledger cannot be audited to link an authorization to the run it authorized. For a proof-chain artifact that is a meaningful omission.
- **Digest stream framing in `project_state` is ambiguous.** Entries are `path + b"\0" + content` with no length prefix; file contents may contain NUL, so a rename-plus-content-edit can in principle reproduce an identical stream and mask a mutation. The `b"<special>"` sentinel also collides with a file whose literal content is `<special>`. Both pre-existing; cheap to fix with a length prefix.
- **`mkdir` failure mode is unstructured.** If `AUTHORIZATION_LEDGER` exists as a regular file, `mkdir(..., exist_ok=True)` raises `FileExistsError` outside the `try`, surfacing as a generic `ERROR` rather than an `AdapterError`.
- **Consumed-on-crash semantics.** A `KeyboardInterrupt` or infra fault after the marker write burns the authorization permanently, and recovery requires hand-editing the ledger. Fail-closed is the right default, but it should be a documented operator procedure, not an undocumented side effect.

## M4
Not verifiable from this packet. `production_cycle_cli.run_packet` is not in the filtered diff, so the claim that pre-existing managed-cycle exception handling yields the structured terminal path cannot be confirmed here. What *is* present at the adapter boundary: `run_one` rejects statuses outside `{ACCEPTED, ESCALATED, FAILED_INFRA, INTERRUPTED}`, and `main()` catches `BaseException` into a JSON `{status, error}` with exit 0/130/4/2. Note `main()` also swallows `SystemExit` into `status: ERROR`.

## Test gaps
- No negative test for the registry: an authorization absent from `authorizations`, a registry that is missing, malformed, a non-dict, or has a non-list `authorizations` — every fail-closed branch added in this commit is uncovered.
- No test that a registry entry with a mismatched `source_message_id` (or `packet_digest`) is rejected. M2, the claim under review, has zero assertions behind it.
- Production constants are never exercised. All three tests patch `APPROVED_PACKET_ROOT`, `AUTHORIZATION_REGISTRY`, and `AUTHORIZATION_LEDGER`; a missing or misspelled real registry path would surface only at invocation time, and the committed diff does not add `manual-authorizations.json` (it may exist from an earlier commit — the filtered pathspec cannot rule that in or out).
- `test_authorization_copy_cannot_replay` proves the copy case within one process against a patched ledger. Uncovered: replay after ledger-entry deletion (the tamper case that matters), replay of a *modified* authorization, and replay against the unpatched global ledger.
- `blind_acceptance.py` has no test in this commit at all. Uncovered: that a content change in a large ignored file is detected, that chunked hashing equals whole-file hashing, that ignored symlinks/directories hash to `<special>`, and the untracked-file branch.
- No test for the terminal-status passthrough (`ESCALATED`/`FAILED_INFRA`/`INTERRUPTED`), the invalid-status rejection, or `main()`'s exit codes and JSON shape — the M4-adjacent surface.
- No test that the marker file is a well-formed, parseable ledger record; the happy-path test asserts only `is_file()`.

Findings 1–3 must close before this can carry the claims made for it. Finding 1 is the one that decides the verdict: produce evidence that the registry is owner-controlled and the ledger is tamper-evident, or move both behind a boundary the agent cannot write.

VERDICT: REJECT
