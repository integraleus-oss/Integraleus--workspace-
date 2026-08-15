# Effects Pointer (указатель эффектов: function → candidate effects)

Compact index in the tradition of the classic указатели физических/химических/геометрических эффектов. Use at Step 4 when the solution's vepol needs a mechanism, or after the effect-NAMING rule (`vepol_deep.md`) tells you which field conversion to look for. Procedure: state the needed function generically → scan the row → shortlist 2–3 effects → verify applicability at the system's scale and conditions (an effect's usability changes drastically with size, temperature, and medium). This list is a starter index, not exhaustive; for exotic needs, run FOS (`flow_and_fos.md`) or a literature search. Cite as `Source: effect-<name>`.

## Generate / transform mechanical action

| Function | Candidate effects |
|---|---|
| Create force / pressure | thermal expansion; phase transition (freezing water, boiling); electro-/magnetostriction; piezo (inverse); electromagnetic forces; osmosis; centrifugal force; explosion/combustion |
| Move or transport an object | magnetic/electric field on (magnetized/charged) object; vibration + asymmetry (vibrotransport); capillarity; Archimedes/buoyancy; jet reaction; Coanda effect; ferrofluids as carriers |
| Hold / fix an object | vacuum; magnetic and electrostatic attraction; freezing-in; adhesives; friction (incl. wedge geometry); shape-memory clamping |
| Dose precisely | capillarity; surface tension (droplet quantization); piezo pumps; overflow geometry; melting a calibrated solid |
| Change friction | lubricant phase change; ultrasound (friction reduction); magneto-/electrorheological fluids (friction ON DEMAND); air/magnetic cushion; anisotropic surfaces |
| Crush / disperse | cavitation; ultrasound; thermal shock; electrohydraulic shock (Yutkin); freezing + brittleness; explosion |

## Thermal

| Function | Candidate effects |
|---|---|
| Heat locally / controllably | induction (conductors); dielectric/microwave heating; friction; exothermic reactions; concentrated radiation; Joule heat |
| Cool | evaporation; Joule–Thomson expansion; Peltier; endothermic dissolution/reactions; radiative cooling |
| Stabilize temperature | phase-change materials (constant-T at transition); Curie point (ferromagnetism switches off AT a fixed temperature — self-regulating induction heating); thermostatic bimetal |
| Transfer heat efficiently | heat pipes (evaporation–condensation cycle); convection enhancement; contact melting |

## Detect / measure (class-4 problems)

| Function | Candidate effects |
|---|---|
| Measure temperature | thermo-EMF (thermocouple); resistance change; thermochromism; thermal expansion; Curie point (threshold detector); IR radiation |
| Detect position / displacement | inductive/capacitive sensing; Hall effect; Moiré patterns (tiny displacements); interferometry; piezo (dynamic); luminescent marks |
| Measure force / pressure | piezoelectricity; strain-gauge resistance; magnetoelastic effect; birefringence under stress (photoelasticity) |
| Detect substance / composition | luminescence markers; selective absorption spectra; chromatography; smell/odor additives (ethyl mercaptan pattern); electrical conductivity of solutions |
| Make the invisible visible | luminescent/UV dyes; thermochromic films; ferromagnetic powder (field patterns); bubbles/smoke in flows; Kirlian/corona for discharges |

## Separate / mix / structure substances

| Function | Candidate effects |
|---|---|
| Separate mixtures | centrifugation; electrophoresis/electrostatic separation; magnetic separation; flotation; selective freezing/evaporation; diffusion/membranes; chromatography |
| Mix intensively | ultrasound; cavitation; turbulence; electromagnetic stirring (conductive melts); vibration |
| Concentrate / accumulate energy | flywheels; capacitors; phase-change storage; elastic elements; resonance (accumulate amplitude at matched frequency) |
| Amplify a weak action | resonance; triggers on unstable equilibria; avalanche/chain processes; lever/wedge geometry; coherent addition (lasers as pattern) |

## Geometric

| Function | Candidate effects |
|---|---|
| More surface, same volume | fractal/porous structures; foams; corrugation; capillary-porous materials (ties to the fragmentation line, `zrts_full.md`) |
| Rigidity without mass | shells and arches; honeycombs; triangulation; tensegrity; pressurized envelopes |
| One profile, many functions | Möbius strip (double working surface life); hyperboloid structures from straight elements; Reuleaux triangle (drilling near-square holes); helix (rotation→translation) |

## Information-systems analogue (heuristic, `Source: effect-info-<name>`)

The same "function → known mechanism" move for software: make tampering visible → hashes/signatures (the luminescent-dye analogue); detect near-duplicates → LSH/embeddings (Moiré analogue: small differences produce visible patterns); self-regulate load → backpressure (Curie-point analogue: built-in threshold switches the mechanism off); amplify weak signal → ensembling/majority vote (coherent addition); separate mixed streams → filters by learned features (electrophoresis analogue: different "charges" drift apart in an applied field). Treat as analogies for direction, then verify with domain-native engineering.
