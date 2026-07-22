# specialtechnology.ru Source-Of-Truth Audit

Created: 2026-07-09
Status: draft-read-only

## Scope

This audit turns the Discord transfer into a safe starting point for future
`specialtechnology.ru` work. It does not deploy, modify, or publish anything.

## Evidence Sources

- Discord transfer:
  `/home/stanislav/.openclaw/workspace/transfers/discord-work-full-20260709/`
- Registry:
  `sources/state-task-2026-06-22-discord-work-registry/registry.md`
- Server inventory:
  `sources/state-task-2026-06-22-discord-work-registry/server_inventory.md`
- Local static site:
  `website/spectech/`
- Live public site:
  `https://specialtechnology.ru/`

## Current Findings

### Local Source Contours

Found in current Home workspace:

- `website/spectech/` exists, size about 264M.
- `special-tech-astro/` was referenced by transferred server inventory, but was
  not found under `/home/stanislav` with a max-depth 7 search on 2026-07-09.
- A follow-up read-only search on Main found
  `/root/.openclaw/workspace/special-tech-astro`.

Interpretation:

- The only currently visible local site contour on Home is the old/static
  `website/spectech/` tree.
- The missing newer Astro contour exists on Main, not on Home. It should be
  included in the source-of-truth comparison before any site work.

### Local Git State

`website/spectech` has uncommitted modifications:

- `robots.txt`
- `sitemap.xml`
- 20 blog HTML files:
  `alarms`, `architecture`, `crossplatform`, `devstudio-migration`,
  `devstudio`, `energy-scada`, `historian-licensing`, `historian`, `hmi`,
  `hmi-frames-posters`, `import-substitution`, `industrial-software-dev`,
  `migration-aveva-to-alpha-oilfield`, `oil-refinery`,
  `ot-security-mistakes`, `plc-import-substitution`, `protocols`, `reports`,
  `scada-comparison`, `scaling`.

Diff summary:

- 22 files changed.
- 85 insertions, 99 deletions.
- `robots.txt` adds disallows for `/category/`, `/author/`, `/2023/`.
- `sitemap.xml` adds
  `/blog/migration-aveva-to-alpha-oilfield.html`.

Recent local commits:

- `f511a86 Add Schema.org Article JSON-LD to all blog articles for Yandex Content Analytics`
- `3c7fbb9 Remove price table from Historian article, keep prices only in example`
- `3503866 Fix Historian article: add official licensing policy facts (external tags only, events free, requires Alpha.Server)`
- `62e7dbd Audit: remove unverified claims from 3 blog articles, keep only documented facts`
- `9ecb7a3 Add 3 new blog articles: DevStudio migration, HMI frames, Historian licensing`

Interpretation:

- The local tree contains SEO/blog work after the older `STATE.md` note that
  last deploy was 2026-04-03.
- There are uncommitted changes that look SEO/content-related, not obviously
  Discord-transfer related.
- Do not overwrite or deploy these changes without a separate review.

### Live Site Checks

Checked on 2026-07-09:

- `https://specialtechnology.ru/` -> 200
- `https://specialtechnology.ru/robots.txt` -> 200, 318 bytes
- `https://specialtechnology.ru/sitemap.xml` -> 200, 5141 bytes
- `https://specialtechnology.ru/calculator.html` -> 200, 204438 bytes
- `https://specialtechnology.ru/wertsim.html` -> 200, 59197 bytes
- `https://specialtechnology.ru/alpha-platform.html` -> 200, 58740 bytes

Homepage comparison:

- Live `/` size: 147369 bytes.
- Local `website/spectech/index.html` SHA-256:
  `adee82302db3d971bb113934ba57823a03eb46bdf268fe860e1f66ad3fb39eaa`
- Live fetched homepage SHA-256:
  `2172b1cfa300cc477489ebf33156f9a8592d8b369a25753b4e5892907610814d`

Core live-vs-local fingerprints:

| Page | Live status | Live bytes | Local bytes | SHA match |
| --- | ---: | ---: | ---: | --- |
| `/` vs `index.html` | 200 | 147369 | 145485 | no |
| `about.html` | 200 | 31485 | 31584 | no |
| `calculator.html` | 200 | 204438 | 204504 | no |
| `wertsim.html` | 200 | 59197 | 59257 | no |
| `alpha-platform.html` | 200 | 58740 | 58704 | no |
| `robots.txt` | 200 | 318 | 230 | no |
| `sitemap.xml` | 200 | 5141 | 5141 | no |

Interpretation:

- The live homepage differs from the local `index.html` bytes.
- Key routes are up.
- Similar page sizes suggest the local static tree may be close to production,
  but it is not byte-identical and must not be treated as proven production
  source without a deeper diff.

## Discord Decisions To Preserve

From the registry:

- Accepted/fixed:
  - Navbar logo fixed.
  - `О компании` page fixed and user confirmed it worked.
  - `about.html` grid/theme issue fixed and deployed.
  - Consent checkbox CSS bug fixed and deployed.
- Rejected:
  - Blog illustration/photo experiment rejected; keep existing SVG icons unless
    there is a new explicit request.
  - Hero background experiment was rolled back.

Operational rule:

- Before visual/site work, verify the requested change does not revive a
  rejected Discord experiment.

## Recommended Next Step

Create a focused `spectech-live-vs-local` audit:

1. Fetch live copies of core pages.
2. Normalize volatile lines where needed.
3. Compare live pages to `website/spectech`.
4. List exact differences by page and classify:
   - already-live but not committed locally,
   - local pending but not live,
   - unknown/manual-review,
   - safe SEO metadata-only.
5. Only after that, choose a small deploy packet.

## Do Not Do Yet

- Do not deploy `website/spectech` wholesale.
- Do not copy anything from the transfer package into the live site tree.
- Do not restore the rejected visual experiments.
- Do not touch calculator/licensing logic until the calculator rules audit is
  created and Alpha licensing guardrails are loaded.
