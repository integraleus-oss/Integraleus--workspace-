# Closure review: two-phase OS authorization guard

Review commit `0957878` as closure of the blockers in
`AUTH_BOUNDARY_CLOSURE_REVIEW.md`. Threat model: root-owned plugin and live
Gateway are trusted; the model may invoke only registered tools and may mutate
user-owned task files. Return ACCEPT only with zero blocker and zero major.

Verify:

- PREPARE requires a fresh exact owner command and snapshots every consumed
  task-directory input through descriptor-relative O_NOFOLLOW reads;
- snapshot rejects symlinks/special files/races and has file/byte/depth limits;
- whole-tree digest binds paths and contents; staged packet remains digest-bound;
- snapshot is readable by the demoted runner but not writable by it;
- RUN accepts no path and only consumes the stored snapshot whose digest is in
  a second fresh exact owner command;
- replay, expiry, framing, timeout process-group cleanup, response handling,
  root service permissions and network needs fail safely;
- old adapter/direct guard flag remain outside the accepted execution path;
- tests are sufficient for one controlled pilot; no cron/commit/push/deploy.

Distinguish real blocker/major findings from hardening nits. Do not edit files.
