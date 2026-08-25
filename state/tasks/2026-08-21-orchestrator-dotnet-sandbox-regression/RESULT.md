# .NET sandbox regression result

Status: `PASS / WRITABLE_EXTERNAL_ARTIFACT_ROOT`

- Codex CLI workspace-write sandbox included the fixture plus the explicitly bounded `/tmp/openclaw-orchestrator-dotnet-regression-artifacts` directory.
- Codex changed only `fixture/Message.cs` from `before` to `sandbox-pass`.
- The authoritative harness built `Probe.csproj` into the external artifact root and executed the resulting DLL successfully.
- Runtime evidence: `sandbox-pass` and `PASS external_artifact_root=/tmp/openclaw-orchestrator-dotnet-regression-artifacts`.
- No `bin/`, `obj/`, or `artifacts/` directory was created inside the fixture.
- SHA-256 checks for `Probe.csproj`, `Program.cs`, and `HARNESS.sh` remained unchanged across the successful Codex run.
- Launcher regression suite: 14/14 PASS, including the new repeated-argument contract for `--add-dir`.
- Shell syntax and `git diff --check` passed.

The first probe exposed a harness-specific `dotnet run` path mismatch with `ArtifactsPath`; the harness was corrected to `dotnet build` followed by execution of the external DLL, then the real sandbox probe was repeated successfully.

Next gate: prepare a fresh Universal Integration R3 packet/worktree that passes its external .NET artifact root through the bounded launcher option. Do not reuse or transfer R2 implementation output automatically. No product RUN was performed by this regression.
