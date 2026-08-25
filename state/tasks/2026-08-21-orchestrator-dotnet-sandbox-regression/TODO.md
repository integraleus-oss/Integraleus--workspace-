# .NET sandbox regression

- [x] Identify a writable build-root mechanism supported by Codex CLI.
- [x] Add bounded `--add-dir` support to the local Codex wrapper and launcher.
- [x] Run launcher unit tests.
- [x] Run a real workspace-write Codex probe that edits one C# file and builds/tests via an external artifact root.
- [x] Prove the fixture has no in-worktree `bin/obj` and unchanged non-target fixture files.
- [x] Record verdict and next gate; do not start Universal Integration R3 here.

Boundaries: infrastructure regression only; no canonical Alpha BPR changes, product transfer, commit, push, or deploy.
