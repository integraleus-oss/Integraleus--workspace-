---
name: triz-engineering-solver
description: Apply Altshuller's TRIZ (ТРИЗ — теория решения изобретательских задач) to resolve contradictions and produce inventive concepts instead of compromises. TRIGGER on any trade-off ('improving X worsens Y'), physical contradiction (one element needs opposite properties), stalled optimization, or requests for inventive/breakthrough solutions — in any language, incl. Russian mentions of ТРИЗ, АРИЗ, ИКР, противоречие, вепольный анализ, приёмы Альтшуллера, матрица противоречий (see resources/ru_reference.md). For software/AI-agent design use heuristic mode per resources/software_ai_systems.md; for business/innovation problems use heuristic mode per resources/business_systems.md — matrix lookups are not authoritative in either. DO NOT trigger for UX/UI design or open brainstorming with no concrete contradiction — TRIZ degrades into generic advice without one.
---

# TRIZ Engineering Solver

A systematic analytical engine for solving engineering problems with Genrich Altshuller's Theory of Inventive Problem Solving (TRIZ). Replaces trial-and-error brainstorming with algorithmic problem-solving over a corpus of patent-derived patterns.

## When to use

- Engineering trade-offs where improving parameter A degrades parameter B (technical contradiction)
- A single element must exhibit opposite properties (physical contradiction)
- Design bottleneck where conventional optimization has plateaued
- System redesign aimed at the Ideal Final Result

## When NOT to use

- UX / interaction design
- Business or organizational strategy
- Open brainstorming with no concrete contradiction identified

**Multi-contradiction situations.** When the situation contains several coupled trade-offs, when earlier fixes caused the current problem, or when the ask is 'help untangle this' rather than 'solve this', build the problem network first per `resources/otsm_networks.md` (ENV normalisation → networks of problems/parameters/contradictions → key problem by fan-out and recurrence), then run the standard workflow on the key node only.

**Failure-cause and risk tasks.** When the user asks WHY something fails (unknown cause) or WHAT COULD go wrong with a planned change, route through `resources/subversion_analysis.md` (AFD-1 / AFD-2) instead of the contradiction track — then feed confirmed mechanisms back into the standard workflow for elimination.

## Special modes

- **Russian-language work** — when the conversation is in Russian or cites Russian TRIZ literature, load `resources/ru_reference.md` for canonical Russian names of the 39 parameters, the 40 principles, the extended principles 41–50, ЗРТС, and the АРИЗ-85-В part names. IDs are identical to the English resources; matrix and workflow unchanged.
- **Business / innovation problems** — heuristic mode with primary-source backing (Petrov & Petrov, 65 worked cases). Load `resources/business_systems.md`; use the ПП→ПТ→ПС chain and Анализ ПТ и ПС; skip the matrix; mark output `Source: business-heuristic`; add a second-order (competitor/regulator counter-move) check.
- **Software / AI-agent systems** — allowed only as an explicitly labelled heuristic. Load `resources/software_ai_systems.md`; skip the matrix (Step 3) unless a genuine physical analogue exists; mark all output `Source: heuristic-analogy`; name validated software-native alternatives alongside the TRIZ pass.

## Inputs required

Before analysis, collect from the user:

1. **System description** — current engineering system and its primary function. If the situation is fuzzy or the statement names only the system itself, run the System Operator grid first (`resources/thinking_toolkit.md`); for multi-component systems where the key disadvantage is unclear, build the function model and CECA chain (`resources/functional_analysis.md`) or a flow map (`resources/flow_and_fos.md`) before formulating the mini-problem
2. **Problem statement** — the specific bottleneck or undesired effect
3. **Contradiction parameters** — which parameter must improve, which one degrades
4. **Constraints** — environmental, cost, manufacturing, physical limits
5. **Available resources** — substances, fields, geometry, byproducts, environment

If any input is missing, use the self-prompting block in `## Intake prompt` below.

## Workflow

### Step 1 — Formulate the Ideal Final Result (IFR)

Describe the outcome where:
- The desired function is achieved perfectly
- No additional cost, complexity, or harmful side-effect is introduced
- Only existing internal / external / temporal resources are used
- The problem "solves itself"

Question to drive Step 1: *"In an ideal world, how would this system achieve [desired function] using only what already exists, with zero added complexity?"*

### Step 2 — Classify the contradiction

**Technical contradiction**: improving parameter A causes parameter B to worsen.
- *Example*: increasing strength (A) increases weight (B).

**Physical contradiction**: a single element must exhibit opposite properties simultaneously or under different conditions.
- *Example*: a surface must be rough (for grip) and smooth (for low friction).

Physical contradictions are typically resolved by **separation** in space, time, condition, or system level (parts vs. whole). For the decision procedure, the principles linked to each separation axis, the full Russian-canon 11-item separation list (system and phase transitions), and the 12 paired principles (приём—антиприём), see `resources/separation_principles.md`. Technical contradictions are resolved via the Contradiction Matrix → Inventive Principles.

### Step 3 — Map to the Contradiction Matrix

1. Identify the **improving parameter** from the 39 — see `resources/39_parameters.md`.
2. Identify the **worsening parameter** from the 39.
3. Look up the cell. **Preferred**: run `python scripts/matrix_lookup.py <improving> <worsening>` — it returns the principles with names, flags empty cells, and prints the reverse-pair result so the asymmetry is not missed. Fall back to reading `resources/contradiction_matrix.json` directly (`cells["<row>,<col>"]`) only if the script cannot be executed. Helpers: `--find <text>` searches parameter names, `--list` prints all 39.
4. For each suggested principle, retrieve its full description and sub-principles from `resources/40_principles.md`.
5. Apply the principles to the concrete system to generate candidate solutions.

> **Axis discipline**: rows = improving, columns = worsening, and the matrix is **asymmetric** — `9,10` and `10,9` give different principles. Transposing them yields a plausible but wrong answer that is invisible in the output, which is why the script exists. Always run both TC directions.

> **Note**: `resources/contradiction_matrix.json` contains the full Altshuller 39×39 matrix (1190 populated cells; 292 cells are legitimately empty in the original — Altshuller's patent analysis found no dominant principle for those contradictions). For empty cells, fall back to reasoning over the 40 principles directly and mark the suggestion as `Source: inferred` rather than `Source: matrix`. See the JSON `meta.primary_source` for transcription provenance.

### Step 4 — Su-Field (Substance–Field) analysis

Model the system's function as a triad:
- **S1** — object being acted upon
- **S2** — tool / agent acting on S1
- **F** — field carrying the action (mechanical, thermal, chemical, electromagnetic, gravitational, acoustic)

Diagnose:
- **Incomplete system** (missing S2 or F): add the missing element, preferring existing resources.
- **Insufficient/ineffective interaction**: introduce a more controllable field, intermediate substance, or field additive.
- **Harmful interaction**: insert a barrier substance, introduce a counteracting field, or modify field properties.

When a concept needs a concrete physical mechanism, shortlist candidates via `resources/effects_pointer.md`. For the harmful-link elimination tree, the effect-finding rule, and the ЭлДЗ/ДаФЗ apparatus for information systems, consult `resources/vepol_deep.md`. For systematic Su-Field transformations, consult `resources/76_standard_solutions.md` — class taxonomy, diagnostic flow, and the most-cited operational sub-rules of the **76 Standard Solutions** (Altshuller, grouped into 5 classes). When you cite a Standard Solution, mark `Source: standard-solution-<class.subclass>` in the output.

### Step 5 — Resource utilization

Enumerate before generating concepts:

- **Internal resources**: unused properties of components, byproducts, idle time, geometric features (holes, surfaces, edges).
- **External resources**: environmental substances (air, water, gravity), environmental fields (magnetic, thermal gradients), supersystem (adjacent systems).
- **Temporal resources**: pre-process preparation, post-process utilization, parallel operations.

Prefer concepts that consume **free** resources over concepts requiring new components.

### Step 6 (optional) — ARIZ deepening

For hard problems where the 40-principles pass yielded no strong concept (no concept reaches `ideality > 1`, see Output format below), switch to **ARIZ-85C** (Algorithm for Inventive Problem Solving) — a formal 9-part procedure that reframes the problem mini-problem → operational zone → operational time → substance-field resources → IFR-1 → physical contradiction → standard solution. Full procedure and operational checklist: `resources/ariz_85c.md`. Before committing to the full 9-part run, consult the graded escalation ladder, the 7-step Краткий АРИЗ, and the false-problem check in `resources/ariz_2010.md` — most problems resolve at a lighter tier, and some should not be solved as posed at all. Invoke explicitly when the user asks for "deep TRIZ" / "ARIZ analysis" or when the quickstart fails the ideality bar.

### Step 7 (optional) — Trends of Engineering System Evolution

For prognostic / roadmapping questions ("where will this technology go next?"), map the system to the 8 trends (increasing ideality, non-uniform development of parts, transition to supersystem, transition to micro-level, increasing dynamism, complexity → convolution, matching/mismatching, reducing human involvement). Full list, S-curve framing, and the diagnostic procedure: `resources/evolution_trends.md`. For the full law hierarchy (needs → functions → organization → evolution laws), operational development lines (controllability and dynamization ladders, fragmentation line, convolution mechanisms), the EAK model for information systems, the express-forecast procedure, and the maturity audit — load `resources/zrts_full.md`. Out of scope for the contradiction-resolution workflow above — invoke only when the user's question is prognostic, not corrective.

## Output format

The full machine-readable template lives in `resources/output_template.md` — **use it verbatim**. The sections below are the inline summary for quick reference. Every concept must report a numeric (or banded) **ideality** estimate (see "Ideality metric" below). Concepts with `ideality ≤ 1` are dropped, not compromised.

Generate a structured analysis containing the sections below. Keep each section tight; this is an engineering deliverable, not an essay.

### 1. Contradiction statement

```
Technical contradiction: improving [Parameter A, with #] causes [Parameter B, with #] to worsen.
— OR —
Physical contradiction: [Element X] must be [Property 1] AND [Property 2].
  Separation strategy candidate: [space | time | condition | system-level].
```

### 2. Ideal Final Result

```
IFR: The system achieves [desired function] using [existing resource],
without adding [cost/complexity/harm], where [problem element] solves itself.
```

### 3. Inventive concepts (3–5)

For each concept:

- **Concept name** — short descriptive title
- **TRIZ principle(s) applied** — number + name (from `resources/40_principles.md`)
- **Source** — one of `matrix` (cell-derived), `inferred` (reasoning over the 40 principles), `standard-solution-<class.subclass>` (Su-Field, see `resources/76_standard_solutions.md`), or `separation-<axis>` (physical contradiction, see `resources/separation_principles.md`)
- **Description** — specific, actionable engineering solution (2–3 sentences)
- **Resource utilized** — which internal / external / temporal resource is leveraged
- **Implementation path** — high-level technical pathway
- **Risks / open questions** — what would need to be validated experimentally

### 4. Principle-to-concept summary table

Sorted by **Ideality descending**.

| # | Concept | Principle(s) | Source | Key resource | Ideality | Risk |
|---|---------|--------------|--------|--------------|----------|------|

### 5. Recommendation

State the top concept, the rationale (one sentence on ideality + risk), the next concrete validation action (experiment / prototype / simulation), and an escalation rule: if no concept reaches `ideality > 1`, invoke ARIZ (`resources/ariz_85c.md`).

## Ideality metric

For each concept compute:

```
ideality = Σ (useful functions) / (Σ (harmful functions) + Σ (costs))
```

- *Useful functions*: each output the concept delivers (deceleration, heat dissipation, safety isolation, …) — count and, where possible, quantify.
- *Harmful functions*: side-effects the concept introduces (NVH, mass penalty, leaked field, …).
- *Costs*: capex, complexity, manufacturing penalty, certification burden, lifetime degradation.

Numeric estimation is preferred. When quantities are unavailable, use the bands `low (≤1) | medium (1–3) | high (>3)` and explain why a numeric estimate is impossible. A concept with `ideality ≤ 1` must be dropped — TRIZ forbids compromise solutions.

## Intake prompt

If any required input is missing, ask the user:

```
To run TRIZ analysis I need:

[ ] System description — what is the system and its primary function?
[ ] Problem statement — what bottleneck or unwanted effect must be resolved?
[ ] Contradiction — which parameter must improve, and which one degrades?
[ ] Constraints — cost, dimensional, environmental, manufacturing limits?
[ ] Resources — substances, fields, geometry, byproducts available?

Please fill the gaps so I can generate inventive concepts.
```

## Agent instructions

1. **Scope check** — before intake, confirm the problem is engineering: physical system, physical field, measurable physical parameters. For software / AI-agent problems, offer heuristic mode per `resources/software_ai_systems.md`; for business / innovation problems, heuristic mode per `resources/business_systems.md`. Otherwise refuse-with-reframe per `examples/anti_example_misframed.md`.
   **When the skill does not apply, calibrate what you say to how it was invoked.** If the user explicitly called the skill (by name, @-mention, or a skill entry point), one short line explaining that the full method is not being run is appropriate. If it fired automatically and the user never mentioned TRIZ, say nothing about it — silently drop the framework and help with the request as asked. This holds for every turn, including follow-ups in a conversation where the method WAS used earlier: do not retroactively label a normal answer in method vocabulary (divergent, convergent, IFR, contradiction, heuristic mode). If the request is under-specified, give a first useful answer under stated assumptions rather than replying with questions alone.
2. **Intake** — collect all five inputs; do not proceed with placeholders.
3. **Analysis** — execute Steps 1–5 in order. Step 6 (ARIZ-85C, `resources/ariz_85c.md`) and Step 7 (Trends, `resources/evolution_trends.md`) only on explicit request or as the ARIZ escalation triggered by failing the ideality bar.
4. **Synthesis** — produce 3–5 concrete concepts, not generic advice. Use `resources/output_template.md` verbatim.
5. **Citation** — always reference principle by `#NN — Name` and mark `Source: matrix | inferred | standard-solution-<class.subclass> | separation-<axis>`.
6. **Prior art** — if a concept matches existing production technology or a standard industry pattern, say so explicitly and state what, if anything, remains novel. A rediscovered strong solution is a success of the method, but presenting it as new is not.
7. **No invented numbers** — never state percentages, benchmarks, effect sizes, or cost figures that were not given to you. Write "unknown" and name the metric to measure instead. This applies to ideality scores too: they rank concepts, they do not measure them.
6. **Validation** — every concept must (a) name the principle, (b) name the resource it consumes, (c) report a numeric or banded **ideality** estimate, (d) state at least one open validation risk.
7. **Ideality bar** — drop any concept with `ideality ≤ 1`. If no concept clears the bar, escalate to ARIZ-85C rather than compromise.
8. **Anti-pattern** — never compromise between A and B; the point of TRIZ is to *resolve* the contradiction, not split the difference. Compromise candidates must be listed as `Source: rejected` for discipline.

## Example applications

- `examples/brake_disc.md` — automotive brake disc (friction vs heat dissipation). Mechanical / thermal contradiction; canonical TRIZ recovery of the ventilated-disc industry solution from first principles.
- `examples/battery_pack.md` — EV battery pack (energy density vs thermal safety). Electromechanical, contemporary; demonstrates the *physical contradiction* path via separation-by-condition and the 76 Standard Solutions.
- `examples/heat_exchanger_fouling.md` — petrochemical heat exchanger (fouling vs pressure-drop). Process-industry contradiction; demonstrates the **30→22** harm-versus-energy-loss pattern, Su-Field Class 1.2 destruction routing, and the ideality drop rule (one concept eliminated).
- `examples/anti_example_misframed.md` — UX onboarding flow (out-of-scope). Demonstrates the **refuse-with-reframe** behaviour when the problem is not engineering.

## Resources

- `resources/39_parameters.md` — the 39 engineering parameters with definitions
- `resources/40_principles.md` — the 40 inventive principles with sub-principles
- `resources/contradiction_matrix.json` — full Altshuller 39×39 matrix (1190 populated cells out of 1482 non-diagonal; the 292 empty cells reflect contradictions for which Altshuller's analysis surfaced no dominant principle)
- `resources/separation_principles.md` — four-axis decision procedure for physical contradictions, linked to the 40 principles
- `resources/76_standard_solutions.md` — full 5-class / subclass taxonomy of the 76 Standard Solutions with Su-Field algebra notation, diagnostic flow, and rule texts (reconciled from Salamatov 1999, Mann 2002, ICG Training & Consulting materials)
- `resources/ariz_85c.md` — ARIZ-85C nine-part deep-analysis procedure with operational checklist
- `resources/ru_reference.md` — canonical Russian terminology: 39 параметров, 40 приёмов, extended principles 41–50 (пауз, многоступенчатое действие, пена, вставные части, БИ-принцип, ВВ, сборка на воде, «мешок с вакуумом», диссоциация—ассоциация, самоорганизация), ЗРТС mapping to the 8 trends, АРИЗ-85-В part names. Cross-checked against Petrov, "Основы ТРИЗ" (2nd ed.)
- `resources/rtv.md` — divergence operators: six psychological-inertia causes with targeted counter-moves, the РВС (size-time-cost limit) operator, 12 fantasy operators mapped to inventive principles, and idea-processing methods (фантограмма sweep, золотая рыбка ИКР-to-roadmap decomposition, снежный ком consequence analysis, «Фантазия» triage scale); use when concept generation is homogeneous or inertia is visible
- `resources/thinking_toolkit.md` — pre-analysis layer: six ТРИЗ thinking modes with a mode selector, the System Operator (9 screens + antisystem axis) for fuzzy situations and prognosis, ММЧ (little-people modeling), component-structural/functional modeling, psychological-inertia counter-moves
- `resources/otsm_networks.md` — OTSM (Khomenko) for situations with many interlinked contradictions: ENV (element–feature–value) normalisation, networks of problems/parameters/contradictions, Problem Flow view, key-problem ranking by fan-out, recurrence and driving character
- `resources/functional_analysis.md` — modern analytics I: component/function model with usefulness–performance–cost ranking, CECA cause-effect chains, trimming rules A/B/C with candidate selection; the procedural form of идеальность
- `resources/flow_and_fos.md` — modern analytics II: substance/energy/information flow mapping with standard defect types (bottleneck, stagnant zone, gray zone, harmful flow), and Function-Oriented Search (generalize the function → find the leading industry → transfer)
- `resources/subversion_analysis.md` — диверсионный анализ / AFD: invert 'why does it fail' into 'how would we cause this failure with the system's own resources'; AFD-1 incident analysis, AFD-2 pre-deployment risk prediction; agent red-teaming procedure
- `scripts/matrix_lookup.py` — CLI for the matrix: `matrix_lookup.py 9 10` → named principles, empty-cell handling, reverse-pair output; also `--find`, `--list`, `--principle`
- `evals/evals.json` — 15-scenario regression set (71 expectations) covering the workflow, domain modes, routing, and restraint; see `evals/README.md` for how to run it after changes
- `resources/effects_pointer.md` — function → candidate-effects index (mechanical, thermal, detection, separation, geometric) plus an information-systems analogue table; use when the solution needs a physical mechanism
- `resources/ariz_2010.md` — Petrov's modern ARIZ: escalation ladder (логика → краткий → 2010 → 85-В), the 7-step Краткий АРИЗ with formal notation, ПП→УП→ОП terminology mapping, the 5-question false-problem check, solving heuristics, modular architecture with the Выбор задачи module (task reformulation, диверсионный анализ)
- `resources/vepol_deep.md` — deep Su-Field layer: systematic harmful-link elimination tree (3 branches by link type), effect-finding rule (field-pair naming), ЭлДЗ parametric analysis, knowledge-development regularities, ДаФЗ/DFK diagnostic ladder for information-processing systems and agents
- `resources/business_systems.md` — business/innovation heuristic mode: ПП→ПТ→ПС contradiction chain with С/анти-С notation, Анализ ПТ и ПС pre-separation procedure, transfer map with case-pattern tags, second-order counter-move check
- `resources/zrts_full.md` — Petrov's full hierarchy of system-evolution laws: organization vs. evolution laws, trend—anti-trend pairs, operational ladders (controllability, dynamization, fragmentation, fields), EAK (Element–Action–Knowledge) Su-Field extension for information systems with the knowledge-integration ladder, express/deep forecast procedures, maturity audit
- `resources/software_ai_systems.md` — heuristic-mode adaptation for software and AI-agent systems: what transfers (IFR, separation, resources, trends), what does not (matrix), principle translations, worked agent-autonomy example
- `resources/evolution_trends.md` — eight trends of engineering system evolution + S-curve framing for roadmapping
- `resources/glossary.md` — operational definitions of every term used in the skill
- `resources/output_template.md` — machine-readable output template (use verbatim)

## References

- Altshuller, G. (1984). *Creativity as an Exact Science*.
- Altshuller, G. (1999). *The Innovation Algorithm: TRIZ, Systematic Innovation and Technical Creativity*.
- Mann, D. (2002). *Hands-On Systematic Innovation*.
- Souchkov, V. *Breakthrough Thinking with TRIZ for Business and Management*.

## Tags

#triz #engineering #problem-solving #innovation #systematic-invention #contradiction-resolution #inventive-principles
