# Independent review: Trusted Test Broker and builder repair

Review the current uncommitted orchestrator diff against two axes.

Standards:

- sealed commands remain allowlisted and fail closed;
- no arbitrary Codex-controlled command or path expansion;
- evidence is bounded and digest-backed;
- scope, ignored-state, timeout, interruption, and infrastructure failures remain terminal;
- existing production packet compatibility is preserved;
- no retry loop can exceed the documented budget.

Spec:

- operator interface remains PREPARE then RUN;
- a first repairable builder gate failure creates exactly one authenticated repair attempt;
- second/exhausted builder failure escalates;
- gates are rerun after repair before review;
- review runs only after successful gates;
- deterministic project/fixture context is supplied;
- no Alpha BPR product behavior is part of this change.

Report blocker, major, minor, and nit findings with exact file/line evidence. Explicitly examine shared builder/reviewer rework-budget behavior, light versus standard profile behavior, gate exit-code classification, environment leakage, and whether the new broker is genuinely a security boundary or only an execution adapter. Do not modify files.
