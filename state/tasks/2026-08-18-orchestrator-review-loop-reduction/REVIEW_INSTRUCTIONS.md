# Independent review: review-loop reduction

Review the uncommitted diff in the isolated orchestrator worktree.

Check especially:

- standard execution has at most two substantive reviews and never silently launches a third final-full review;
- light execution has exactly one substantive review while retaining fail-closed behavior;
- acceptance criteria are frozen across managed rework;
- blocker/major policy outcomes cannot be admitted as ACCEPTED;
- second-pass R15 admission is safe and cannot be used on the first review;
- exhausted review budgets produce an explicit escalation/follow-up record;
- CLI plumbing, compatibility, tests, and documentation are coherent.

Treat enhancements outside the frozen task criteria as nits or follow-ups. Report blocker/major only for a correctness, safety, regression, or frozen-criteria violation. Do not modify files.
