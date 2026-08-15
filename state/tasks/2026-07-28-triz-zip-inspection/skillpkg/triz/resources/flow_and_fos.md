# Flow Analysis & Function-Oriented Search (modern TRIZ analytics II)

Two complementary identification instruments. Flow analysis finds WHERE the system loses value; function-oriented search finds WHO has already solved the function elsewhere.

## Flow analysis (поток-анализ)

Map the flows of **substance, energy, and information** through the system (for software: data, events, control, money, attention), then hunt the standard defect types:

- **Bottleneck (узкое место)** — the narrowest section limiting the whole flow → widen, parallelize, or reroute;
- **Stagnant zone (застойная зона)** — flow enters and stops; accumulations, dead stock, unread queues → drain, recirculate, or stop feeding it;
- **Gray zone (серая зона)** — a section where the flow's fate is unknown/unmeasured → instrument first, judge later;
- **Harmful flow** — a flow that damages (leaks, noise, interrupts, data exfiltration) → block via the harmful-link tree (`vepol_deep.md`);
- **Insufficient useful flow** — target of intensification (raise conductivity — the закон проводимости потоков in `zrts_full.md` is the governing law; a NEW system must first ensure every part is reached by the needed flows at all);
- **Excessive flow / losses** — energy or data delivered where it is not consumed → reclaim as a resource (ВПР pass, Step 5).

Procedure: draw the flow map (sources → paths → sinks) → mark defects per the list → each defect is either fixed by a standard move above or, if fixing it worsens something else, becomes a contradiction for the main workflow. Cite as `Source: flow-<defect>`.

Agent reading: context tokens are the primary flow — bottleneck = context window at the largest step; stagnant zone = retrieved-but-unused documents; gray zone = unlogged tool results; harmful flow = prompt-injected instructions moving from data into control; losses = tokens spent on content the next step ignores. A context-budget audit IS a flow analysis.

## Function-Oriented Search (ФОП / FOS)

Instead of inventing, find the industry that already performs your function at a superior level, and transfer.

1. **Generalize the function** — strip the domain: not "cool the CPU" but "remove heat from a compact object"; not "dedupe support tickets" but "cluster near-duplicate short texts". Choose the abstraction level deliberately: too narrow finds neighbors, too broad finds platitudes.
2. **Identify leading industries** — fields where this generalized function is life-critical or done at massive scale/precision (heat removal → rocket engines, blast furnaces, living tissue; deduplication → search engines, bioinformatics sequence matching).
3. **Harvest the leader's solution** and adapt it back, checking the transfer survives the domain shift (different scales, materials, failure costs).

FOS exploits the same fact the 40 principles were distilled from — solutions repeat across industries — but does the lookup live instead of via a precompiled list. Best when the function is clear and the contradiction is "we don't know a good mechanism" rather than a true conflict. Cite as `Source: fos`.
