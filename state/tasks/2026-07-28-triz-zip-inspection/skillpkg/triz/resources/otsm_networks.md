# OTSM — Networks of Problems (multi-contradiction situations)

OTSM (ОТСМ — Общая теория сильного мышления) by Nikolai Khomenko, developed with Altshuller from the 1980s. Classical TRIZ takes ONE problem with ONE contradiction; OTSM handles situations containing many interlinked problems, where solving one spawns the next. Load this file when the user's situation has several coupled trade-offs, when earlier fixes created the current problem, or when the request is "help me untangle this", not "solve this".

Key stance difference: OTSM does not SEARCH for a solution — it gradually CONSTRUCTS the problem situation until the roots become visible, then solves at the roots. Expect the analysis itself to be most of the value.

## ENV model (Element – Name of feature – Value)

The unit of description in OTSM. Every statement about the situation is decomposed into: **Element** (what) – **Name of feature/parameter** (which property) – **Value** (what value it has or must have).

Why it matters operationally: conflicting requirements are conflicting VALUES of the same named feature of the same element. Writing problems in ENV form makes shared parameters visible across problems that were phrased in different vocabularies — two teams' "problems" often turn out to be one parameter pulled in two directions. Use ENV as the normalizing step before building any network. Cite as `Source: otsm-env`.

## The four networks

Build them in this order; each is a layer over the previous.

1. **Network of problems** — nodes are problems and partial solutions, edges are "this partial solution causes that new problem" / "this problem must be solved to address that one". A fix that generated today's problem is an edge, not history.
2. **Network of parameters** — from the ENV descriptions, extract the parameters each problem touches. Parameters appearing in many problems are the situation's load-bearing axes.
3. **Network of contradictions** — where a parameter is required to take opposite values by different problems, write the contradiction. One parameter often carries several problems' conflicts at once.
4. **Problem Flow network** — the dynamic view: how problems propagate over the system's life or the project's timeline; which problems will appear later if current partial solutions are adopted.

## Finding what to actually solve

Rank nodes by:
- **Fan-out** — how many other problems dissolve if this node is resolved;
- **Recurrence** — the same contradiction reappearing in several branches (a strong signal of a root);
- **Driving contradictions** — the ones that govern the situation's evolution rather than describe a local nuisance;
- **Resource proximity** — nodes near available resources are cheaper to attack (each contradiction gets its own resource list).

The top-ranked node is the **key problem**. Only then hand it to the standard workflow (`SKILL.md`) or full ARIZ; solve at the root, and re-check the network afterwards — a good root solution should visibly prune branches, and if it doesn't, the ranking was wrong.

## Typical Solution vs New Problem technologies

- **Typical Solution technology** — if a node matches a known typical problem, apply standards/principles directly; don't network what a standard already solves.
- **New Problem technology** — for genuinely novel situations: transform the fuzzy description into a fractal network of problems, contradictions, and parameters (the procedure above), then work the roots.
- **Contradiction technology** — ARIZ-derived resolution applied per node, with OTSM's extended contradiction system (a contradiction as a system of elementary contradictions over ENV triples).

## Agent/software reading

Agentic architecture is a canonical OTSM situation: autonomy ↔ oversight, reasoning depth ↔ latency, context completeness ↔ cost, specialization ↔ orchestration complexity, memory richness ↔ privacy/staleness. Each pair looks like a separate trade-off, but in ENV form several collapse onto shared parameters (e.g. *context volume*, *number of model calls*, *degree of self-verification*) — those shared parameters are usually the real key problems, and resolving one prunes several branches. Same pattern for legacy-system refactors and organizational processes, where today's problem is yesterday's partial solution. Cite as `Source: otsm-network`.
