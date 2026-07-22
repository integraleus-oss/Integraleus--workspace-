# Main Server File Search

Created: 2026-07-09
Status: read-only search complete

## Scope

Search the Main server for the files referenced by the Discord work transfer and
the first operational workstreams. This search did not copy, edit, deploy, or
delete anything.

Main server checked:

- Host: `root@155.212.227.115`
- Workspace root: `/root/.openclaw/workspace`

Home comparison root:

- `/home/stanislav/.openclaw/workspace`

## Summary

The important missing Home contours are present on Main:

- `special-tech-astro/`
- `knowledge/rewrite/`
- `tmp/alpha_hmi_libs_20260506/UMOSS_3/`
- `tmp_specialtechnology_calculator.html`
- `tmp_specialtechnology_calculator.js`

Home already has:

- `agents/main/generated/promo/`

Interpretation:

- The Discord transfer is not enough by itself to resume all work on Home.
- Main still holds source/work artifacts that need to be treated as upstream
  evidence for the operational package.
- Do not deploy from Home until the Main artifacts are copied or compared in a
  controlled way and the source-of-truth decision is updated.

## Directories Found On Main

| Main path | Notes |
| --- | --- |
| `/root/.openclaw/workspace/special-tech-astro` | Newer Astro contour referenced by the transfer registry. |
| `/root/.openclaw/workspace/agents/main/website/spectech` | Static site contour, about 265M on Main. |
| `/root/.openclaw/workspace/knowledge/rewrite` | Alpha article rewrite/final package. |
| `/root/.openclaw/workspace/knowledge/rewrite/docx_out_v2` | DOCX final article outputs. |
| `/root/.openclaw/workspace/tmp/alpha_hmi_libs_20260506/UMOSS_3` | UMOSS/WeRTSim design prototype. |
| `/root/.openclaw/workspace/agents/main/generated/promo` | Promo/video assets. |

## Home Presence Check

| Relative path | Home state |
| --- | --- |
| `special-tech-astro` | missing |
| `knowledge/rewrite` | missing |
| `tmp/alpha_hmi_libs_20260506/UMOSS_3` | missing |
| `tmp_specialtechnology_calculator.html` | missing |
| `tmp_specialtechnology_calculator.js` | missing |
| `agents/main/generated/promo` | present |

## special-tech-astro

Main path:

- `/root/.openclaw/workspace/special-tech-astro`

Key files observed:

- `package.json`
- `astro.config.mjs`
- `src/pages/index.astro`
- `src/pages/about.astro`
- `src/pages/contact.astro`
- `src/pages/importozameshchenie-scada.astro`
- `src/pages/news.astro`
- `src/pages/news/digest-asu-tp-dispatching-2026-05/index.astro`
- `src/pages/podbor-scada.astro`
- `src/pages/privacy-policy.astro`
- `src/pages/raschet-licenziy-alpha-platform.astro`
- `src/pages/services.astro`

Relevant docs observed:

- `docs/Технический план переноса сайта СПЕЦТЕХ.md`
- `docs/Чек-лист приемки перед запуском сайта СПЕЦТЕХ.md`
- `docs/Предрелизная инструкция администратора СПЕЦТЕХ.md`
- `docs/Предрелизная инструкция пользователя личного кабинета.md`
- `docs/Процесс работы с новостями в ЛК СПЕЦТЕХ.md`
- `docs/qa-report-2026-05-14.md`

Interpretation:

- This looks like the missing newer site contour from the transfer registry.
- Home's first audit must be revised from "not found locally" to "not present
  on Home, present on Main."

## Static specialtechnology.ru Tree

Main path:

- `/root/.openclaw/workspace/agents/main/website/spectech`

Observed important files:

- `calculator.html` - 204438 bytes, timestamp 2026-06-03 16:31
- `send_calc.php` - 5838 bytes, timestamp 2026-05-31 08:59

Main static tree had local modifications when checked:

- `.htaccess`
- `alpha-chat-widget.js`
- `alpha-platform.html`
- `calculator.html`
- `index.html`
- `wertsim.html`

Recent commits seen in that tree:

- `43f2164 Sync production site and blog audit fixes`
- `09eb7f8 Block old WordPress URLs in robots.txt`
- `9473644 SEO: внутренняя перелинковка блога`
- `f511a86 Add Schema.org Article JSON-LD to all blog articles for Yandex Content Analytics`
- `3c7fbb9 Remove price table from Historian article, keep prices only in example`

Interpretation:

- Main static tree is not clean and is not automatically safer than Home.
- Need a three-way comparison for specialtechnology.ru: live site, Main static,
  Home static, plus Main Astro.

## Calculator Files

Main paths:

- `/root/.openclaw/workspace/agents/main/website/spectech/calculator.html`
- `/root/.openclaw/workspace/agents/main/website/spectech/send_calc.php`
- `/root/.openclaw/workspace/tmp_specialtechnology_calculator.html`
- `/root/.openclaw/workspace/tmp_specialtechnology_calculator.js`

Other related calculator files found:

- `/root/.openclaw/workspace/agents/main/website/automiq/calculator.html`
- `/root/.openclaw/workspace/agents/main/website/integraleus/calculator.html`
- `/root/.openclaw/workspace/agents/main/skills/product-calculator/templates/calculator.html`
- backups under `/root/.openclaw/workspace/backups/`

Interpretation:

- The temporary calculator snapshots are on Main, not Home.
- Calculator work should start from a source/rules audit, not from editing the
  visible Home static file.

## Alpha Articles

Main path:

- `/root/.openclaw/workspace/knowledge/rewrite`

Archives found:

- `articles_final.zip`
- `articles_final_docx.zip`
- `articles_final_docx_v2.zip`

Markdown finals found:

- `01_export_final.md`
- `02_sng_final.md`
- `03_opcua_final.md`
- `04_iec62443_final.md`
- `05_import_final.md`

DOCX v2 outputs found:

- `docx_out_v2/01_export_final.docx`
- `docx_out_v2/02_sng_final.docx`
- `docx_out_v2/03_opcua_final.docx`
- `docx_out_v2/04_iec62443_final.docx`
- `docx_out_v2/05_import_final.docx`

Interpretation:

- Article publication mapping should use Main `knowledge/rewrite` as the
  current artifact source, then fact-check against current Alpha guardrails
  before any publication.

## UMOSS / WeRTSim

Main path:

- `/root/.openclaw/workspace/tmp/alpha_hmi_libs_20260506/UMOSS_3`

Key files found:

- `index.html`
- `v2_product.html`
- `v3_enterprise.html`
- `v4_editorial.html`
- `v5_terminal.html`
- `v6_umoss.html`
- `v6_wertsim.html`
- `privacy.html`
- `competitors.md`
- `analytical-note.txt`

Interpretation:

- The prototype is on Main and should remain classified as prototype/design
  material until a clean production candidate and legal/claims checklist exist.

## Promo Assets

Main path:

- `/root/.openclaw/workspace/agents/main/generated/promo`

Files found:

- `promo_15sec.mp4` - 4194859 bytes
- `promo_v2.mp4` - 1822546 bytes

Interpretation:

- Home already has the promo folder, but Main confirms these are the same named
  working assets referenced by the transfer.
- Continue promo work from script/creative direction first, not by publishing the
  existing video as final.

## SEO / Webmaster Evidence

Main files found:

- `seo_audit_specialtechnology_sitemap_2026-05-05.csv`
- `seo_fixes_before_after_specialtechnology_2026-05-05.csv`
- `seo_fixes_before_after_specialtechnology_2026-05-05.md`
- `seo_monthly_baseline_specialtechnology_2026-04-01_2026-05-01.md`
- `seo_query_opportunities_specialtechnology_2026-04.md`
- `seo_webmaster_findings_specialtechnology_2026-05-05.md`
- `yandex_webmaster_queries_month_2026-04-01_2026-05-01.csv`
- `yandex_webmaster_query_aggregate_2026-04-17_2026-04-30.csv`
- `yandex_webmaster_query_url_aggregate_2026-04-17_2026-04-30.csv`
- `yandex_webmaster_url_aggregate_2026-04-17_2026-04-30.csv`

Interpretation:

- SEO decisions have source evidence on Main and should be pulled into the
  site/content audit before new SEO edits.

## Deploy Archives

Main files found:

- `special-tech-astro-deploy.zip`
- `special-tech-http-deploy.php`
- `special-tech-http-deploy.zip`
- `special-tech-production-deploy-2026-05-14.tar.gz`
- `special-tech-production-deploy-2026-05-14.tar.gz.sha256`

Interpretation:

- These are useful provenance/deploy evidence, not current deploy instructions.
- Any deployment path must be re-validated against the live site and current
  source tree before use.

## Recommended Next Step

Create a controlled import/sync plan:

1. Copy from Main to Home only into a quarantined evidence folder, not into live
   working trees.
2. Preserve checksums and timestamps where practical.
3. Compare:
   - live site,
   - Home `website/spectech`,
   - Main `agents/main/website/spectech`,
   - Main `special-tech-astro`.
4. Only after comparison, pick one small workstream:
   - specialtechnology.ru source-of-truth decision, or
   - calculator source/rules audit, or
   - Alpha article publication map.

## Do Not Do Yet

- Do not overwrite Home `website/spectech`.
- Do not deploy Main static or Astro artifacts directly.
- Do not publish Alpha articles before guardrail/fact-check.
- Do not treat UMOSS_3 as production-ready.
