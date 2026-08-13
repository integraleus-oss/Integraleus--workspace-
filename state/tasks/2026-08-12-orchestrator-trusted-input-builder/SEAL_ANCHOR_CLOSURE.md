I traced the change across all four files plus `managed_one_cycle.py` and `test_trusted_review_builder.py`. **No files edited. Tests were not run** — `python3 -m unittest` was denied by the permission mode this session, as it was for the prior closure. Everything below is static.

## The four required confirmations

**1. Anchor captured before Claude launch, retained outside the reviewer-writable directory — confirmed**

`production_cycle_cli.py:191` `anchored_seal_digest = _sha256(built["seal"])`, inside the builder branch of `review()`. That is before `run_cycle` at `:208`, which is what launches Claude (`live_review_cycle.py:33`). The value lives only as a Python local captured by the lambda closure at `:211-213` — in-process memory, never written to disk, never inside `out/`. That is the right shape: a same-UID adversary with arbitrary write and code execution (the wrapper allowlist is unchanged) cannot be fenced out by file permissions, only by state they cannot reach.

Digest formats match, which is load-bearing: `production_cycle_cli._sha256:38-39` and `trusted_review_builder._digest_bytes:23-24` both emit `"sha256:" + hexdigest()` over raw bytes. A mismatch here would have made the check fire on every run rather than never — but they are identical.

**2. Required by the pre-admission verifier before any sealed input is read or the verdict is materialized — confirmed**

`verify_seal:313-314` is the first statement in the body: `if expected_seal_digest is not None and _digest(seal_path) != expected_seal_digest: raise`. It precedes the `seal.json` JSON parse at `:316`, the per-file digest loop at `:321`, the evidence read at `:326`, and the tree recheck at `:350`.

The callback ordering in `run_cycle` is unchanged and still correct: `:48-49` verify → `:51` first bundle read → `:63-65` verdict materialization → `:66` policy run. A raise at `:49` propagates out with no verdict file and no `policy-runs/`, landing in `managed_one_cycle.py:86-89`'s broad `except Exception` as `ESCALATED`. Fail-closed.

The ordering test now pins the callback *after* the launch — `test_live_review_cycle.py:101` asserts `cycle/claude-launch/launch-result.json` exists, which closes the prior residual that the assertions would also have held if the callback ran first.

**3. Rewriting both inputs and `seal.json` cannot satisfy the check — confirmed**

The two legs are mutually exclusive. Rewrite an input and leave `seal.json` alone → `:321-324` digest mismatch. Rewrite `seal.json` to match → its own bytes change → `:313` root digest mismatch. Satisfying both requires a SHA-256 second preimage of the original `seal.json` bytes that also encodes different member digests. `seal.json` is no longer its own root of trust; the root is now the pre-launch in-memory digest. The B-1 failure scenario — recompute the eight digests and rewrite `seal.json` — dies at `:313`.

Coverage of both legs exists: `test_trusted_review_builder.py:112-121` rewrites `seal.json` and asserts `"seal root digest mismatch"` under an anchor; `:104-110` rewrites `evidence.json` and asserts `"digest mismatch"`. Gate logs and the reviewed tree are anchored transitively through the sealed `evidence.json`, and `:341-347`'s file-set equality still blocks additions and deletions.

**4. Builder mode cannot omit it; legacy unchanged — confirmed**

One call site. `packet["builder"]` is validated as a non-empty dict at `:142-143`, so it cannot be falsy in builder mode, and the same expression gates the build (`:185`), the prompt augmentation (`:201`) and the callback (`:214`). `anchored_seal_digest` is assigned on both branches (`:191` / `:194`) and never reassigned, so the lambda's late binding is safe. `test_production_cycle_cli.py:214-215` asserts non-`None` and invokes the real `verify_seal` with the real anchor against real built inputs.

Legacy: both new parameters are keyword-only with `None` defaults. Schema `1.0.0` packets yield `builder=None` → `anchored_seal_digest=None` → `pre_admission_verify=None`, byte-identical behavior. The `verify_seal` call sites at `test_trusted_review_builder.py:52/110/129/133` and `production_cycle_cli.py:189` are unchanged positional forms. `run_cycle`'s CLI path (`:100`) passes nothing. The legacy CLI tests at `test_production_cycle_cli.py:96-133` stub `run_cycle` with `MagicMock`, which absorbs the new kwarg.

**B-1 is closed.**

## Non-blocking residuals

- **Anchor is re-read from disk rather than returned in-process.** `:191` digests `out/seal.json` again instead of `build_review_inputs` returning the digest it computed at write time. An adversary active between `:189` and `:191` — a daemonized Codex child, say — could get a tampered seal anchored. Outside B-1's postulated actor, but returning the digest from the builder would remove the window for free.
- **Carried, unchanged:** tamper detection writes no `cycle-result.json` (`:48-49` sits outside the `try` at `:64`); TOCTOU between verify and `local_orchestrator_runner`'s re-read at `:66`; no end-to-end tamper test driving a mutated directory through `production_cycle_cli` → `run_cycle`; no structural enforcement inside `run_cycle` (a refactor dropping the argument fails only `test_production_cycle_cli.py:214`).
- The complementary change B-1 suggested — materializing the verdict outside the sealed directory — was not made (`live_review_cycle.py:57-63` still uses `bundle_base`). It is no longer needed for the security property, since the verdict is written strictly after the verify and unlinked at `:78`; it remains a structural cleanup only.

The above are hardening and forensics items. None of them reopens the bypass, and none is in the scope of the four checks.

SEAL_ANCHOR_CLOSURE_PASS
