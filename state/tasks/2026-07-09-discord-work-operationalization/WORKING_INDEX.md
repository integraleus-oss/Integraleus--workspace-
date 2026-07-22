# Working Index: Discord Work Transfer

Source package:
`/home/stanislav/.openclaw/workspace/transfers/discord-work-full-20260709/`

This index converts the verified archive into practical workstreams. It is a
working layer; the transfer package remains the evidence layer.

Related operational artifacts:

- `MAIN_SERVER_FILE_SEARCH.md` - read-only search results from Main.
- `MAIN_TO_HOME_EVIDENCE_IMPORT_PLAN.md` - safe quarantine import plan.
- `MAIN_TO_HOME_IMPORT_STATUS.md` - completed import status.
- `/home/stanislav/.openclaw/workspace/transfers/main-server-evidence-20260709/` - imported Main evidence with `MANIFEST.tsv`, `SHA256SUMS`, and `SOURCE_COMMANDS.md`.
- `SPECTECH_LIVE_SOURCE_MATRIX.md` - live/Home/Main/Astro fingerprint matrix.

## 1. specialtechnology.ru

Evidence:

- Discord registry: `specialtechnology.ru website`
- Server inventory: static `agents/main/website/spectech/` and newer `special-tech-astro/`
- Main search: `MAIN_SERVER_FILE_SEARCH.md`
- Known local modified static files: `.htaccess`, `alpha-chat-widget.js`,
  `alpha-platform.html`, `calculator.html`, `index.html`, `wertsim.html`

Current interpretation:

- High-value but risky area because Discord includes both accepted fixes and rejected experiments.
- Do not start with visual changes. Start with a source-of-truth audit.
- Home has `website/spectech/`; Main has both `website/spectech/` and the
  missing `special-tech-astro/` contour.

Next artifact:

- `SPECTECH_SOURCE_OF_TRUTH_AUDIT.md`
- `SPECTECH_LIVE_SOURCE_MATRIX.md`

Likely steps:

- Identify authoritative source contour.
- Compare live site vs local sources.
- Reconcile accepted/rejected Discord decisions.
- Only then create a small change packet.

Current source-of-truth update:

- Imported Main static matches live byte-for-byte on checked key routes.
- Home static differs from live and Main static on those routes.
- Main Astro is a separate candidate contour, not the current checked live tree.

## 2. Calculator / Licensing Entry Point

Evidence:

- Discord registry did not find a dedicated calculator thread reliably.
- Server inventory confirms actual calculator artifacts:
  `agents/main/website/spectech/calculator.html`, `send_calc.php`,
  `tmp_specialtechnology_calculator.html`, `tmp_specialtechnology_calculator.js`.
- Main search confirms temp calculator snapshots exist on Main but are missing
  on Home.
- Related Alpha licensing data exists under `/root/.openclaw/workspace/data/licensing_automiq/`.

Current interpretation:

- This is probably a real business-critical surface.
- Must be handled under Alpha licensing guardrails.

Next artifact:

- `CALCULATOR_SOURCE_AND_RULES_AUDIT.md`

Likely steps:

- Compare current calculator files with temp working snapshots.
- Check whether calculator logic matches current Alpha licensing rules.
- Separate UX fixes from commercial calculation correctness.

## 3. Alpha Articles / Blog Content

Evidence:

- Final archive: `knowledge/rewrite/articles_final_docx_v2.zip`
- DOCX outputs: `knowledge/rewrite/docx_out_v2/*.docx`
- Markdown variants: `knowledge/rewrite/*_final.md`
- Main search confirms `knowledge/rewrite/` exists on Main and is missing on
  Home.

Current interpretation:

- Good candidate for the new supervised agentic editorial pipeline.
- Do not publish directly; map to site/blog needs and fact-check against current Alpha docs.

Next artifact:

- `ALPHA_ARTICLES_PUBLICATION_MAP.md`

Likely steps:

- Locate final v2 sources.
- Map each article to target page/blog slot.
- Check claims against Alpha product guardrails.
- Prepare publish-ready drafts with human approval gates.

## 4. UMOSS / WeRTSim

Evidence:

- Prototype: `tmp/alpha_hmi_libs_20260506/UMOSS_3/`
- Review screenshots: `artifacts/umoss_review_screens_2026-05-06/`
- Static pages: `v6_umoss.html`, `v6_wertsim.html`, `privacy.html`, plus older variants.
- Main search confirms `UMOSS_3/` exists on Main and is missing on Home.

Current interpretation:

- Design/prototype material, not production-ready.
- Main risk is public claims/legal/privacy/demo-form/CDN, not HTML mechanics.

Next artifact:

- `UMOSS_PRODUCTION_CANDIDATE_CHECKLIST.md`

Likely steps:

- Extract clean candidate from v6 pages only.
- Remove/archive older variants and internal notes from deploy candidate.
- Check legal/privacy/contact/claims/CDN/demo form.

## 5. Content / Promo Video

Evidence:

- `agents/main/generated/promo/promo_15sec.mp4`
- `agents/main/generated/promo/promo_v2.mp4`
- Source clips/images in the same folder.
- Discord note: jitter/zoompan issue existed; user clarified СпецТех is a distributor.

Current interpretation:

- Continue as a script/creative package before generating more video.

Next artifact:

- `SPECTECH_DISTRIBUTOR_PROMO_SCRIPT.md`

Likely steps:

- Define target duration and channel.
- Write distributor-positioned script.
- Reuse `promo_v2.mp4` only as rough reference, not as accepted final.

## 6. CRM / Estimates Concept

Evidence:

- Discord main-channel concept: local CRM on OpenClaw/DenchClaw for leads, requests, estimates, follow-up.
- No full local implementation found in quick server inventory.

Current interpretation:

- Product/spec backlog, not implementation-ready.

Next artifact:

- `LOCAL_CRM_ESTIMATES_MVP_SPEC.md`

Likely steps:

- Define entities: Companies, Contacts, Opportunities, Estimates, Tasks.
- Connect to calculator/licensing only after calculator rules audit.

## 7. GitVerse / Fielddev Monitor

Evidence:

- Discord says weekly GitVerse monitor configured and daily duplicate removed.
- Server inventory warns older memory says broken monitor jobs were disabled.

Current interpretation:

- Runtime truth unresolved. Check live cron before relying on it.

Next artifact:

- `FIELDDEV_MONITOR_RUNTIME_CHECK.md`

Likely steps:

- Run OpenClaw cron status/list.
- Confirm whether monitor exists and where it reports.
- Fix only after explicit maintenance request.

## Priority Queue

1. specialtechnology.ru source-of-truth audit.
2. Calculator source/rules audit.
3. Alpha articles publication map.
4. UMOSS production candidate checklist.
5. СпецТех distributor promo script.
6. Local CRM/estimates MVP spec.
7. Fielddev/GitVerse runtime check.
