# Independent Closure Review — `docs/evidence/TRIZ-P3-PROOF-SUMMARY.md`

**Counts: blocker = 1 · major = 5 · nit = 6**

Verification basis: every citation in the report was opened and checked against the worktree. All ~40 file:line citations resolve, and the substantive quotes from ADR-009, the integration readme, the stage tracker, the validator, the schema, and the fixture profile are accurate. The findings below are the exceptions.

---

## Blocker

**B1 — The title and filename take the identity of a different, still-open tracked deliverable.**
Report lines 1 and 10–16 define "TRIZ P3" as the self-generating-profile concept. In this repository, TRIZ P3 is **Recipe Lifecycle Ideality** (`docs/product/alpha-bpr-triz-reframed-plan-20260725.md:323-341`), and "TRIZ P3 proof summary" is an open, Track-E-gating checklist item with a *different* definition: "approval screen must show lifecycle, audit, ontology, diff, report readiness, and mode/source proof in one visible reviewer summary" (`TODO.md:380-382`, gated at `docs/product/alpha-bpr-p2-honest-mode-contract-20260728.md:201` and `docs/product/alpha-bpr-p1-guard-registry-20260728.md:63,118`). The report never cites where its own P3 definition comes from, and it addresses none of the recipe-approval criteria. Filed as `docs/evidence/TRIZ-P3-PROOF-SUMMARY.md`, it reads as closure of a gate that is still open.
**Correction:** rename to `docs/evidence/self-generating-profile-proof-summary-20260821.md`, drop "TRIZ P3" from the H1, cite the source of the browse→infer→confirm→dry-run definition, and add an explicit disambiguation line: "This is not the TRIZ P3 (Recipe Lifecycle Ideality) proof summary required by `TODO.md:380`; that item remains open."

## Major

**M1 — No PASS/PARTIAL/FAIL/NOT TESTED labels anywhere; test evidence is asserted without an execution record.**
Report line 54 states the fixture tests prove fail-closed behavior for seven negative cases, but line 4–6 rules out any runtime action, and no recorded run of `UniversalReadOnlyIntegrationTests` exists anywhere in the repo — the tracker records only `--filter Recipe` 119/119 (`state/tasks/2026-07-21-alpha-bpr-full-product-implementation/TODO.md:328-329`) and `--filter RecipeStep` 11/11 (`:409-410`), neither of which covers that suite. The row is source-reading presented as proof.
**Correction:** add an explicit status column and label each row; mark line 54 `NOT TESTED — test source read only, no recorded run of UniversalReadOnlyIntegrationTests` (or run it and cite the result).

**M2 — Stale runtime claim: the "curated write guard" resource no longer describes current code.**
Line 135–139 lists "Existing HMI/BFF mode separation and curated write guards from stages 0-4" in the present tense, citing 2026-07-21 tracker evidence in which public curated POSTs returned `409`. Current code key-gates rather than blocks: curated create falls through to a Technologist-key path (`scripts/demo/hmi_bff_demo_server.py:659-671`) and curated formula/procedure/approve/make-effective are key-gated (`:396-411`). The blanket `409` guard now survives only for batch/EBR/QA actions (`:950-956`, `:1023-1029`, `:1119-1125`).
**Correction:** re-cite to current code and restate as "curated mode requires an explicit workflow API key for recipe writes; the blanket `409` curated guard now applies only to batch/EBR/QA execution routes."

**M3 — The experiment's acceptance criteria cannot fail on the only thing being tested.**
Line 158 derives the browse tree from `examples/integration-profiles/mix01/profile.json` — the file that already declares every semantic (`:28-102`), i.e. the answer key. Line 171–172's criterion "at least one high-confidence mapping and one deliberately ambiguous mapping are produced" is a construction requirement: no numeric confidence threshold, no definition of ambiguity, no correctness or calibration measure. Nothing in lines 168–177 fails if inference is wrong.
**Correction:** replace line 171–172 with measurable thresholds, e.g. "≥4 of 5 mix01 signals map to the correct declared semantic at confidence ≥0.8; zero incorrect mapping is emitted at confidence ≥0.8; every confidence value cites the feature basis that produced it" — and add a matching abandon condition under Stop conditions: "record FAIL and stop if the correct-semantic rate is <3/5 or any incorrect mapping scores ≥0.8."

**M4 — Resource inventory omits the repo's only real OPC UA read paths, which changes the recommended experiment.**
Lines 124–141 list only fixture and static-profile resources. The repo already has a local MIX01 OPC UA simulator with a real namespace and variables (`scripts/alpha-platform/mixing_station_opcua_server.py:83-94`) and a read-only, fail-closed, manifest-driven collector (`scripts/ops/alpha-bpr-track-f-opcua-collector.py:246-268`). A genuine browse namespace is therefore available with no customer, live stand, or credential involvement — while the report proposes a synthetic tree derived from the answer key.
**Correction:** add both to the Resource Inventory, and change experiment step 1 (line 158) to browse the local simulator namespace, keeping `mix01/profile.json` only as the scoring key.

**M5 — The proposed human-confirmation gate cannot identify a human.**
Line 163–165 makes the confirmation gate "a separate checked-in `confirmation.json`" with no confirmer identity, role, reason, or timestamp. This contradicts the repo's own audit discipline, where every recipe write requires an attributed change reason (`scripts/demo/hmi_bff_demo_server.py:2402-2404`), and it means the spec's "engineer confirmation" step is unattributable.
**Correction:** require `confirmedBy`, `role`, `reason`, and `confirmedAt` per candidate, and add an acceptance criterion: "a confirmation record missing identity, role, or reason fails closed with a named diagnostic and cannot unlock dry-run."

## Nit

**N1 — Line 48:** the unescaped pipe in `` `HMI_BFF_TRIAL_MODE=curated|live-sandbox` `` splits the table cell in GFM (code spans do not protect pipes), breaking the row. Escape as `curated\|live-sandbox`.

**N2 — Lines 32–33:** the quote "does not connect to Alpha Platform" is at `ADR-009-universal-read-only-integration-boundary.md:16-17`; `:15` is the separate `ReadAsync` sentence. Cite `:16-17`.

**N3 — Line 50:** `docs/hmi/prototype/alpha-bpr-integrated-hmi-prototype.html:1888-1918` points at `cloneRecipe()` (starts at 1889), which posts a *new version*, not the create-form submit path. The claim is technically true; cite the create-form handler or restate as "clone/create both post through the workbench create route."

**N4 — Lines 53 and 54:** two ranges truncate their evidence. `StationProfile.cs:64-143` cuts `GenericCountProfile` short (it ends at 145), and the "gateway exposes only `ReadAsync`" assertion in `:175-208` actually sits at `UniversalReadOnlyIntegrationTests.cs:195-209` (assertion at 203). Use `:64-145` and `:175-183, :195-209`.

**N5 — Line 136:** `TODO.md:97-121` is the "Curated-safe Deployment" record, not mode-separation or write-guard implementation evidence. Cite `:39-41` (curated write-guard message) instead.

**N6 — Line 22:** "the accepted stages 0-4" silently omits stages 5–8, which are complete in the tracker (`TODO.md:419`, `:491`, `:584`, `:691`) — including Stage 5 approval/diff/make-effective, the surface the repo's actual P3 concerns. Either say why 5–8 are out of scope or extend the survey. **N7 — Filename** lacks the date suffix used by the comparable P1/P2 artifacts (`alpha-bpr-p1-guard-registry-20260728.md`).

---

**REWORK**
