# Result

Outcome: **REWORK / R11_OPEN_FINDINGS; TRANSFER FORBIDDEN**

The fresh controlled-manual builder produced a three-file Alpha-Presale
`doctor` implementation from source commit `52ea3ba`. Its allowlist, ignored
file boundary, 11 focused tests, read-only Python compilation, and whitespace
gate all pass. The fixed diff digest is
`df5a9865959f8dcd62b2cb09ff2eb2dfeaa2d82f34f31d3bfb2bca653a2eac3e`.

The review-only retry preserved and reverified the fixed diff, then produced an
admitted independent decision. Policy returned `REWORK / R11_OPEN_FINDINGS`
with 4 major findings and 2 nits. The major findings are:

1. Unreadable or non-UTF-8 schema/fixture/verify inputs can escape as an
   exception instead of producing aggregated JSON and exit 2.
2. The command does not check baseline local configuration from
   `pyproject.toml`, despite the active requirement.
3. A verification command expressed through a shell variable is silently
   omitted from both availability lists.
4. Success tests depend on host `node` and `rg`, so the mandatory gate is not
   hermetic.

The nits are an uncovered non-executable local-command branch and a fragile
shell-keyword filter. Repeated tests remain 11/11 and `git diff --check` passes;
the diff digest is unchanged.

Next gate: bounded implementation rework in the same isolated worktree,
followed by focused/full checks and a fresh independent review. No transfer is
allowed before an admitted `R17_ACCEPT`.

No commit, transfer, push, deploy, canonical worktree write, Gateway/systemd,
Web/API, licensing calculation, or customer-facing action occurred.
