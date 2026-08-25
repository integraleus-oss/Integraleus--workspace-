# Evidence Backlog Audit

Goal: classify the untracked `state/tasks/` evidence packages from 2026-08-17 through 2026-08-23 without deleting, committing, or modifying their contents.

## Checklist

- [x] Inventory packages, sizes, file types, and primary reports.
- [x] Match packages to canonical repositories and known commits.
- [x] Check for secrets, generated noise, duplicates, and incomplete evidence.
- [x] Classify each package: commit separately, consolidate, retain locally, or remove after approval.
- [x] Propose scoped commit groups and residual cleanup actions.

## Boundaries

- Read-only audit of existing evidence packages.
- No deletion, relocation, staging, commit, push, or deploy.
- Preserve all unrelated dirty-worktree changes.
