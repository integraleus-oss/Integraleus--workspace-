---
name: "triz-contradiction-solver"
description: "Resolve explicit engineering contradictions with TRIZ."
license: "MIT"
---

# TRIZ Contradiction Solver

Use when the user explicitly asks for TRIZ/ТРИЗ/ARIZ/АРИЗ/IFR/ИКР, or when a real contradiction is central to the task: improving one parameter worsens another, one element needs opposite properties, optimization is stalled, or the user asks for a non-compromise inventive resolution.

Do not use for ordinary brainstorming, taste, UX polish, generic product strategy, or simple engineering advice when no contradiction is present. If the user did not mention TRIZ, silently drop this skill when the trigger is weak.

## Routing

- Physical engineering contradiction: use the main TRIZ workflow and matrix only when the 39 engineering parameters genuinely fit.
- Physical contradiction: use separation first: space, time, condition, system level, phase/state, or paired principle/anti-principle.
- Software or AI-agent design: heuristic mode only. Do not present matrix lookup as authoritative. Load references/software_ai_systems.md, tag concepts Source: heuristic-analogy, and name domain-native alternatives such as caching, queues, streaming, model cascades, backpressure, formal trade-off analysis, or design patterns.
- Business or innovation: only when the user explicitly asks for TRIZ-style business contradiction analysis. Load references/business_systems.md, use ПП -> ПТ -> ПС, skip the physical matrix, tag output Source: business-heuristic, and include competitor/regulator/customer counter-move checks.
- Failure cause or "what could go wrong": invert the task into AFD/subversion style instead of running the normal contradiction track; generate several mechanisms with observable signatures.
- Simplification: use function modeling and trimming before adding components.
- Many coupled trade-offs: map the problem network first, pick the key node, then solve that node.

## Workflow

1. State the system and main function as verb + object.
2. Run the false-problem check: obsolete decision, upstream error, downstream self-elimination, harmful consequence, or someone else for whom the problem is useful.
3. State the Ideal Final Result before generating concepts: the function happens by itself, using existing resources, with no added cost/complexity/harm.
4. Formulate both technical contradiction directions: TC-1 strengthening X improves A but worsens B; TC-2 weakening X improves B but worsens A.
5. Sharpen to a physical contradiction when one element needs opposite properties.
6. Inventory resources before adding anything new: internal, external/supersystem, temporal, waste/byproducts, idle capacity, geometry, information already emitted.
7. Resolve: for physical contradictions use separation; for technical contradictions map to the 39 parameters and run python scripts/matrix_lookup.py <improving> <worsening> from the applied skill directory; check both directions.
8. If matrix mapping is weak or empty, choose principles by meaning and tag Source: inferred.
9. Produce 2-4 concepts. For each: source tag, principle/separation axis, resource used, whether both requirements survived, closeness to IFR, prior-art note, validation risk.
10. Reject compromises explicitly. If every concept is a compromise, escalate to ARIZ or ask for missing constraints/resources.
11. Do not invent numbers. If no metric was supplied, write unknown and name what to measure.

## Output

Answer in the user language.

Use this compact structure unless the user asks for deep ARIZ:

- Intake summary
- IFR
- Contradiction statement
- Resource inventory
- Concepts, 2-4 items
- Recommended next validation

For a full structured deliverable, load references/output_template.md.

## References

Load only what the task needs:

- references/39_parameters.md
- references/40_principles.md
- references/contradiction_matrix.json
- references/software_ai_systems.md
- references/business_systems.md
- references/output_template.md
- scripts/matrix_lookup.py
- references/evals.json
- references/ATTRIBUTION.md
- references/LICENSE-MIT.txt

## Validation

After applying or changing this skill:

1. Validate frontmatter.
2. Run python scripts/matrix_lookup.py 9 10 from the skill directory; expected principles: 13, 28, 15, 19, plus reverse pair notice 13, 28, 15, 12.
3. Use references/evals.json as the regression checklist. The restraint cases must not trigger a full TRIZ run.
