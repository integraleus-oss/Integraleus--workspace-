# Independent review — declarative doctor verification manifest

Review the complete uncommitted four-file diff against TASK_PACKET.md.

Prior architecture was rejected because it attempted to parse arbitrary Bash.
The new design must not parse or execute `scripts/verify.sh`. It must use
`verification-manifest.json` as the explicit source of verification readiness,
detect script drift with SHA-256, validate manifest shape and path boundaries,
and check availability read-only.

Review both Spec and Standards. Confirm deterministic JSON, exact 0/2 exits,
Python 3.10 compatibility, aggregation of failures, four-file scope, and no
licensing calculation, price access, network, Web/API, deployment, commit,
transfer or external action. Treat the detached-worktree absence of the sibling
licensing corpus as an environment limitation, not a regression.

Report blocker, major and nit findings with file/line evidence. End with exactly
`VERDICT: ACCEPT` or `VERDICT: REWORK`.
