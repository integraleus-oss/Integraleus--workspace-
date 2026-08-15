# Subversion Analysis — Диверсионный анализ / AFD

Method by Б. Злотин and С. Вишнепольская (late 1970s; published as the Диверсионный Метод, 1985/1991; in the West — Anticipatory Failure Determination, AFD, per Kaplan–Visnepolschi–Zlotin–Zusman, 1999). Core inversion: instead of asking "why does this failure happen?" or "what could go wrong?", ask **"how could we deliberately CAUSE this failure — using only what is already in the system?"** — then solve that as an inventive task, and check which of the invented mechanisms the real system already implements. Inventing harm is psychologically easier and more systematic than confessing to it; the inversion converts a diagnostic question into a solvable synthesis task.

## AFD-1 — failure analysis (причины брака; reactive)

Use when a defect/incident EXISTS and the cause is unknown.

1. **Document the failure** precisely: what, where, when, under what conditions; strip explanations, keep observations.
2. **Invert**: formulate the inventive task "design a mechanism that reliably produces exactly this failure, at this location and timing, using only the system's own resources (ВПР — substances, fields, flows, states, timings present in the operational zone)". The resource restriction is what makes hypotheses checkable — a saboteur with outside equipment explains nothing.
3. **Solve** the inverted task with the full skill toolkit (effects via `effects_pointer.md`, Su-Field mechanisms, flow defects) — generate SEVERAL distinct failure mechanisms; one hypothesis is not an analysis.
4. **Verify**: for each invented mechanism, name its observable signature and check it against the real system/logs/experiments. Confirmed mechanism → eliminate via the harmful-link tree (`vepol_deep.md`) or the main workflow.

## AFD-2 — failure prediction (прогноз рисков; proactive)

Use BEFORE deploying a change, product, or process.

1. Describe the new system/change and its operational zones.
2. Play the saboteur systematically: walk the resource inventory (each substance, field, flow, state, timing, actor) and the system's life stages (make, transport, store, operate, maintain, decommission; for software — build, deploy, run, update, rollback) asking "how do I weaponize THIS to break THAT?"; use the fantasy operators (`rtv.md`) to escape the designer's inertia — the designer is the worst saboteur of their own system without them.
3. Rank invented failures by damage × ease of triggering; for the top ones, either redesign (main workflow) or add barriers — noting that per АРИЗ-2010's heuristics, conditions under which the failure CANNOT arise beat barriers that fight it.

## Scope and agent reading

Applied historically to manufacturing defects, technology rollouts, organizational processes, and software projects. For AI agents this is red-teaming with a TRIZ engine: AFD-1 = incident post-mortem via "reproduce the failure from inside" (prompt-injection paths, tool-result poisoning, context starvation as deliberate attacks); AFD-2 = pre-deployment adversarial review where the attacker is limited to the agent's own inputs, tools, and memory — exactly the realistic threat model. The resource restriction doubles as the fix-finder: whatever resource the "saboteur" used is the resource to control. Cite as `Source: afd-1` / `Source: afd-2`.
