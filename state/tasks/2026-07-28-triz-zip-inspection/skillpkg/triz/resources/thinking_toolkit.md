# Talented-Thinking Toolkit (thinking modes, System Operator, modeling)

Structured after Petrov, "Талантливое мышление. ТРИЗ". This file is the PRE-ANALYSIS layer: which thinking mode the task needs, and two instruments the main workflow doesn't cover — the System Operator (multi-screen scheme) and TRIZ modeling tools. Load it when the situation is fuzzy, when the user asks "how to think about X" rather than "solve X", or when psychological inertia is visibly narrowing the search.

## Six components of ТРИЗ thinking — mode selector

| Mode | What it is | Where in this skill |
|---|---|---|
| Системное | See parts, hierarchy, mutual influences, changes in time and by condition | System Operator below; intake steps |
| Эволюционное | Spot development patterns; apply the laws of evolution | `evolution_trends.md`, `zrts_full.md` |
| Через противоречия | Sharpen and resolve contradictions instead of trading off | Main workflow steps 2–4 |
| Ресурсное | Inventory and exploit what already exists | Main workflow step 5 |
| По моделям | Replace the object with a tractable model, solve on the model | Su-Field / EAK; ММЧ and modeling rules below |
| РТВ (творческое воображение) | Deliberate imagination control against psychological inertia | `rtv.md` |

Diagnostic use: if the pass over one mode stalls, name the mode you were in and switch — most hard cases yield to a mode the solver hasn't tried, and the six-item list makes the untried modes visible.

## System Operator (multi-screen scheme)

Altshuller's instrument for de-narrowing a situation; Petrov's form has three components:

1. **Hierarchy axis**: подсистемы ← СИСТЕМА → надсистема + окружающая среда.
2. **Time axis** at every level: прошлое ← настоящее → будущее. Together: the classic 9 screens (3 levels × 3 times).
3. **Antisystem axis** (Petrov's extension): for each screen, consider the антисистема — the system performing the OPPOSITE function — and its past/future. (Canonical illustration: pencil ↔ eraser; the fused pencil-with-eraser is a system–antisystem merge, one of the strongest надсистемные переходы — cf. системный переход 1б in `separation_principles.md`.)

Procedure: draw the 3×3 grid for the object; fill every screen with at least one concrete entry; then run the antisystem question over the column of the present. Weak screens (empty or generic) mark where the analysis — and often the solution resource — is hiding.

When to use in the workflow:
- **Intake / Step 1**: the user's problem statement names only the system itself → fill the grid before formulating the mini-problem; the conflict often dissolves at the надсистема level or in a neighboring time screen.
- **Prognosis**: the future row IS the forecast skeleton; combine with the ladders in `zrts_full.md`.
- **Stalled solution search**: resources found on other screens (past states, supersystem, antisystem) are legitimate ВПР — cite as `Source: system-operator-<screen>`.

Agent/software reading: подсистема = tools/functions; система = agent; надсистема = orchestration layer, product, user workflow; среда = infra, other agents, users; antisystem of a generator agent = a critic/verifier agent (their merge = self-critique loops — a system–antisystem fusion in the надсистема).

## TRIZ modeling tools

Modeling in TRIZ = веполи/EAK (`76_standard_solutions.md`, `zrts_full.md`), ММЧ, component-structural and functional modeling. Rules of a good model regardless of tool: a model is always a simplification — capture the **main parts** and the **main links** and nothing else; decompose a complex process into simple ones, model each, then re-complicate; an imprecise initial model gives imprecise conclusions, so restate the model whenever conclusions look off.

### ММЧ — метод маленьких человечков (Modeling with Little People)

Represent the operational zone as crowds of "little people," each able to act, move, hold, or let go. Three steps:
1. Draw the conflict zone as little people doing what currently happens (including the harmful action).
2. Redraw so the people DO what the ИКР requires — let them split into groups, change behavior by condition, rearrange freely; ignore physical plausibility at this step.
3. Translate the redrawn picture back into a physical/technical implementation (fields, substances, phase changes; for software — data structures, processes, policies).

Why it works: it forces micro-level, actor-based sight of the interaction and strips away the psychological inertia of the object's current construction. Use it when the operational zone is opaque or when solutions keep gravitating to the existing design. Cite as `Source: mmch`.

### Component-structural and functional modeling

Before resolving anything: list components (component model) → mark which component acts on which and how — useful / harmful / insufficient / excessive (structural model) → for each link state the function as verb + object (functional model). Harmful and insufficient links found here are the direct input for Su-Field diagnosis (Step 4 of the main workflow).

## Psychological inertia — working notes

Inertia enters through: special terms (fixate the current implementation — replace with generic words, as the main workflow's intake requires), the object's habitual image (break with ММЧ or the System Operator's non-present screens), and the first plausible solution (counter by generating from at least two different thinking modes before converging). РТВ (развитие творческого воображения) is the discipline of deliberately controlling imagination; its operational set — the six inertia causes with targeted counter-moves, the РВС operator, and the 12 fantasy operators — is in `rtv.md`.
