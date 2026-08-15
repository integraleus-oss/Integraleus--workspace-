# TRIZ for Software & AI-Agent Systems (heuristic mode)

## Honest scope statement — read first

Classic TRIZ was distilled from patents on **physical** systems; its empirical base does not cover software architecture or AI agents. Applying it there is a **heuristic analogy, not a validated methodology**. In this mode:

- Do NOT present matrix lookups as authoritative. The 39 parameters describe mass, temperature, force — most have no software meaning. Skip Step 3 (matrix) unless the problem has a genuine physical analogue (latency ≈ speed, memory ≈ volume — use sparingly and say so).
- DO use: IFR thinking, contradiction formulation, separation principles, resource mapping, evolution trends, and the 40 principles as **reframing prompts**.
- Mark every suggestion `Source: heuristic-analogy` — never `Source: matrix`.
- If the user wants validated methods for software, say so and name alternatives (design patterns, queueing theory, CAP-style formal trade-off analysis) before or alongside the TRIZ pass.

## What transfers well

**1. Contradiction discipline.** The core move — refuse the compromise, sharpen the conflict, resolve it — is domain-independent. Formulate software trade-offs as TCs ("more agent autonomy → less oversight") or PCs ("the context must be long AND short"), then attack with separation:

- **Separation in time** → lazy loading, JIT compilation, canary stages, autonomy that varies by execution phase
- **Separation in space** → sharding, edge vs. core, sandboxing risky tool calls while trusted paths run free
- **Separation by condition** → feature flags, circuit breakers, human-in-the-loop only above a risk threshold
- **Separation system-level (part vs. whole)** → each microservice simple, the ensemble capable; each agent narrow, the swarm general

**2. IFR as an architecture razor.** "The function is performed, but the component does not exist." Ask of every subsystem: *what if this agent / queue / cache were absent — what existing resource performs its function by itself?* This prunes orchestration layers and is the strongest single transfer.

**3. Resource mapping.** Inventory what already exists before adding components: logs already emitted (→ free telemetry), idle compute in off-hours (→ batch reprocessing), the model's own outputs (→ self-critique loops), the user's message history (→ implicit preference signal).

**3a. EAK and the maturity ladders (primary-source support).** Petrov's «Законы развития систем» extends Su-Field to information systems directly: the EAK model (Element–Action–Knowledge) and its knowledge-integration ladder (K outside → partial K built in → all K inside, managed outside → K self-managed), plus the controllability ladder (open loop → feedback → self-tuning → self-learning → self-organizing → self-developing) and the dynamization ladder (changeable parameters → structure → algorithm → principle → function → goals). These map cleanly onto agent-autonomy maturity and are legitimately in-scope for information systems — cite `Source: zrts-eak` / `Source: zrts-line-<name>` (see `zrts_full.md`). The contradiction-matrix caveat is unchanged.

**4. Evolution trends for roadmapping.** Trends 1 (ideality), 3 (supersystem — platformisation), 5 (dynamism — hardcoded → configurable → learned), 6 (complexity then convolution — the framework explosion followed by consolidation), 8 (reducing human involvement — autocomplete → copilot → agent) demonstrably rhyme with software history. Use for "what comes next" questions.

## Principle translations that pull their weight

Only principles with a non-forced software reading. If a translation feels strained, drop it.

| # | Principle | Software / agent reading |
|---|-----------|--------------------------|
| 1 | Segmentation | Decompose into specialised sub-agents, microservices, composable skills |
| 2 | Taking out | Extract the risky / expensive path into an isolated component (sandbox, dead-letter queue) |
| 3 | Local quality | Different model tiers per task: cheap model for routing, strong model for reasoning |
| 5 | Merging | Batch API calls; merge agents whose contexts always overlap |
| 6 | Universality | One tool interface serving many agents (MCP-style) instead of per-agent integrations |
| 7 | Nested doll | Agents spawning sub-agents; recursive task decomposition |
| 9 | Preliminary anti-action | Adversarial testing / red-teaming before deployment; guardrails installed pre-launch |
| 10 | Preliminary action | Pre-computation, caching, prompt/context pre-loading, warm pools |
| 11 | Beforehand cushioning | Fallback models, retries with backoff, checkpointing long agent runs |
| 13 | The other way round | Instead of agent pulling data, data pushes to agent (events vs. polling); invert the review: human proposes, agent critiques |
| 15 | Dynamics | Runtime-adaptive parameters: temperature, tool budget, autonomy level varying with confidence |
| 16 | Partial or excessive action | Accept approximate retrieval + rerank (excess then filter); ship the 80% answer with uncertainty flags |
| 19 | Periodic action | Cron-triggered agents instead of resident daemons; periodic memory consolidation |
| 20 | Continuity of useful action | Fill agent idle time: background indexing, speculative pre-fetch |
| 22 | Harm into benefit | Failed runs become eval cases; hallucinations logged as training signal |
| 23 | Feedback | Self-critique loops, eval-driven regeneration, user thumbs as reward signal |
| 24 | Intermediary | Adapter/facade layers; a router agent between user and specialists |
| 25 | Self-service | System heals/configures itself: auto-retry, self-updating skill files, agents writing their own tools |
| 26 | Copying | Cheap replicas instead of the original: shadow deployments, distilled models, synthetic data |
| 27 | Cheap short-lived | Ephemeral sandboxes and throwaway prototypes instead of durable infrastructure |
| 34 | Discard & regenerate | Context pruning mid-run; agents that summarise-and-drop their own history |
| 35 | Parameter change | Quantisation, changing data representation (text → embeddings → graph) |

## Worked micro-example

**Problem**: an autonomous coding agent is fast when unsupervised but unsafe; adding human review makes it safe but slow.

- **TC**: autonomy ↑ → safety ↓. Sharpened PC: *the agent must be supervised AND unsupervised.*
- **Separation by condition**: supervision triggers only on risk signals (file deletion, network egress, credential access); all else runs free.
- **Principle 10 (preliminary action)**: pre-approve an allowlist of operations before the run.
- **Principle 26 (copying)**: run the risky plan in a disposable sandbox copy first; only the verified diff touches production.
- **IFR check**: "review happens by itself" → the type system / CI already rejects the dangerous class of change, so no human gate is needed for it at all.

`Source: heuristic-analogy` on all of the above.
