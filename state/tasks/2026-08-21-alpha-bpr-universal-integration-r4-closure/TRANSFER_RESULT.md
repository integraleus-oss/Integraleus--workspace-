# Transfer Result

Status: `TRANSFERRED_AND_COMMITTED_LOCAL`

- Approved patch digest:
  `sha256:c86ded480e5e4d662cb73f083db4c53d72163f9b750bb06006cb6ab3b3818044`.
- Canonical baseline before transfer: `b9e637754c5b00f38fd09f5949c971afd12db7a1`.
- Canonical commit after transfer:
  `ad1c2a895b0221b2a5d6915e921ff5bb75be2a6f`.
- Commit subject: `feat: add universal read-only integration profiles`.
- Staged and committed patch digest exactly matched the approved transfer
  artifact.
- Canonical focused tests: 27/27 PASS.
- Canonical full tests: 367/367 PASS.
- Canonical build: PASS, 0 warnings, 0 errors.
- Restore and `git diff --check`: PASS.
- Canonical worktree after commit: clean.
- Generated .NET `bin/obj` under `src/` and `tests/` were removed before commit;
  other historical/deployment directories named `bin` were not touched.
- Push and deploy were not performed.
