# Rollback

1. Confirm the source repository remains clean at `3d9c27e`.
2. Remove only the explicitly named isolated worktree and managed run after
   evidence retention is no longer required.
3. Do not reset, clean, or delete anything in the source repository.
4. If the managed cycle fails, retain its run directory as fail-closed evidence
   and do not copy the attempted change back to the source project.
