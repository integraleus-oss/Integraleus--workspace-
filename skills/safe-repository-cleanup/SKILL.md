---
name: "safe-repository-cleanup"
description: "Clean dirty repositories through verified, reversible archival without message replay."
---

# Safe Repository Cleanup

## Procedure

1. Inspect the branch, upstream divergence, worktree status, repository size, and filesystem capacity; write a pre-cleanup snapshot with the Git HEAD and timestamp, completing the step when the original boundary is reproducible.
2. Classify every candidate as durable source, durable evidence/state, generated output, backup/migration remnant, or ambiguous; for mixed directories, compare tracked and ignored paths and archive only individually proven derived outputs rather than trusting the directory name or moving the whole tree. Leave durable and ambiguous paths untouched, and when a semantic batch contains no proven disposable targets, record that result and proceed without creating an unnecessary archive, completing the step when the cleanup list contains only proven temporary or generated files or is explicitly empty.
3. Write an exact target manifest before moving files; validate that each target exists as a regular non-symlink file, completing the step when the manifest and validation counts match.
4. Archive targets outside the repository while preserving workspace-relative paths; calculate SHA-256 values before and after the move and verify archive readability, completing the step only when every hash matches.
5. Record archive location, payload size, target count, restoration instructions, and the post-cleanup worktree boundary; retain the archive until the owner separately approves disposal, completing the step when restoration can be performed from the evidence alone.
6. Treat staged inbound/outbound media, sent deliverables, delivery evidence, message queues, notification records, SQLite data, and delivery state as the messaging boundary rather than generated clutter; keep them out of repository cleanup unless separately scoped and approved, never replay or resend messages as a cleanup side effect, and complete the step when evidence confirms those systems and artifacts were not mutated.
7. Commit only semantically reviewed batches; for application source, inspect structure and dependencies, scan candidate files for secret-shaped material without printing values, and run the smallest meaningful tests plus smoke check before committing. Keep maintenance, memory/state, skills, runtime history, and application source in separate commits, completing the step when each commit has a narrow purpose and verification evidence.

## Stop Conditions

Stop before moving a path when its ownership, retention value, symlink status, or relation to a queue/message system is uncertain. Stop after any hash mismatch or unreadable archive and preserve both available copies for investigation.
