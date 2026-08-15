# Functional Analysis, CECA & Trimming (modern TRIZ analytics I)

Cross-checked against MATRIZ Level-1 conventions. This is the problem-IDENTIFICATION layer of modern TRIZ: build the function model, locate key disadvantages, then remove components while keeping their useful functions. Strongest on cost-reduction and simplification tasks ("same value, fewer parts/steps"); pairs with the ИКР discipline — trimming is идеальность made procedural.

## Function model (procedure)

1. **Component model** — list system components + relevant supersystem elements (product, environment, user).
2. **Interaction model** — mark which components touch/act on which.
3. **Function model** — for each interaction, state the function as *carrier → action verb → object* ("brush bristles → remove → plaque"). Classify each function:
   - by usefulness: **useful** (basic — acts on the target object; auxiliary — acts on another system component) / **harmful**;
   - by performance: **normal / insufficient / excessive**;
   - note each component's approximate **cost** (money, mass, latency, tokens — whatever the system's currency is).
4. Diagnosis: harmful and insufficient functions feed the Su-Field pass (`vepol_deep.md`, `76_standard_solutions.md`); high-cost/low-function components are trimming candidates.

## CECA — cause-effect chain analysis

From each disadvantage, chain "…is caused by…" downward until you reach either (a) a contradiction — improving the cause worsens something else → main workflow, or (b) a root cause that can be attacked directly. Target the DEEPEST attackable node, not the symptom. (Same move as the ОП→ОП₁→ОП₂ deepening in `ariz_2010.md`, applied to system disadvantages.) Cite as `Source: ceca`.

## Trimming (свертывание as procedure)

**Candidate selection**: components with high cost + low functionality, carriers of harmful functions, components with many key disadvantages (from CECA).

**The three rules** — a component (function carrier) can be trimmed if, for each of its useful functions:
- **Rule A**: the function is no longer needed — often because the OBJECT of the function is also trimmed or redesigned; the strongest form, frequently forces a new operating principle;
- **Rule B**: the object of the function performs it ITSELF (paint moves itself → no pump);
- **Rule C**: another existing component of the system or supersystem takes the function over.

**Depth**: light trimming (few auxiliary components) → incremental improvement; radical trimming (a basic-function carrier) → new architecture. Each trimmed function generates a problem statement ("how does X get done without Y?") — these become inventive tasks for the standard workflow. Cite as `Source: trimming-<rule>`.

## Agent/software reading

The function model of a pipeline: components = agents/tools/steps; functions = "validator → checks → draft". Trimming questions map to: Rule A — is this check needed at all once upstream is fixed? (cf. false-problem check in `ariz_2010.md`); Rule B — can the artifact carry/verify its own invariant (schema-validated output instead of a validator agent)?; Rule C — can an existing step absorb it (the generator self-critiques instead of a critic agent)? Token/latency cost per step is the natural cost column. A multi-agent system that survives honest trimming is rare — run this pass before adding any new agent.
