# specialtechnology.ru Live Source Matrix

Created: 2026-07-09
Status: read-only evidence

## Scope

Compare key public `specialtechnology.ru` pages against:

- live site,
- current Home static tree,
- imported Main static tree,
- imported Main Astro build where route equivalents exist.

No files were deployed or edited.

## Inputs

Live:

- `https://specialtechnology.ru/`

Home static:

- `/home/stanislav/.openclaw/workspace/agents/main/website/spectech`

Imported Main static:

- `/home/stanislav/.openclaw/workspace/transfers/main-server-evidence-20260709/root-openclaw-workspace/agents/main/website/spectech`

Imported Main Astro:

- `/home/stanislav/.openclaw/workspace/transfers/main-server-evidence-20260709/root-openclaw-workspace/special-tech-astro/dist`

## Fingerprint Matrix

| Page | Live | Home static | Main static | Astro dist |
| --- | --- | --- | --- | --- |
| `index.html` | 200, 147369 bytes, `2172b1cf...` | 145485 bytes, `adee8230...` | 147369 bytes, `2172b1cf...` | `index.html`, 32062 bytes, `f892f770...` |
| `about.html` | 200, 31485 bytes, `035f001b...` | 31584 bytes, `8e507359...` | 31485 bytes, `035f001b...` | `about/index.html`, 7336 bytes, `057c1eb9...` |
| `calculator.html` | 200, 204438 bytes, `dd8aca0b...` | 204504 bytes, `93137c6a...` | 204438 bytes, `dd8aca0b...` | missing direct equivalent |
| `wertsim.html` | 200, 59197 bytes, `db99ccff...` | 59257 bytes, `0c4c2b68...` | 59197 bytes, `db99ccff...` | missing direct equivalent |
| `alpha-platform.html` | 200, 58740 bytes, `996fbc1e...` | 58704 bytes, `cec812cc...` | 58740 bytes, `996fbc1e...` | missing direct equivalent |
| `robots.txt` | 200, 318 bytes, `73dab0e6...` | 230 bytes, `46edc96f...` | 318 bytes, `73dab0e6...` | 244 bytes, `2be8a501...` |
| `sitemap.xml` | 200, 5141 bytes, `589ed157...` | 5141 bytes, `8b4ec3ff...` | 5141 bytes, `589ed157...` | `sitemap-index.xml`, 190 bytes, `277b3184...` |

Full SHA-256 values from the check:

```text
index.html live/main 2172b1cfa300cc477489ebf33156f9a8592d8b369a25753b4e5892907610814d
index.html home      adee82302db3d971bb113934ba57823a03eb46bdf268fe860e1f66ad3fb39eaa

about.html live/main 035f001ba84b388c9d1c77924d315058b379e2760700ec47816557d4d4ffe424
about.html home      8e5073599443a9cec3e622f66b234f64dd01d5f1dcaeaf015248ab173a929c84

calculator.html live/main dd8aca0be4bf26bf9717605cb4aea4647cb1fbdd7edb6a0adf0386dc5beca3c5
calculator.html home      93137c6a2735a8abd57ef65b32c286335ebf82a2a56444482468a23eadf6da31

wertsim.html live/main db99ccff91be9a15803eb9307600a67a4ac8f8d23467d420949585ba1dfbe485
wertsim.html home      0c4c2b6858086727c0de44c95d3b0457645ee28be10a8367222f6b54c6197c11

alpha-platform.html live/main 996fbc1e65832e749cec31d4a2f37ef9aa02db85e4ef87f0746e2267099a947b
alpha-platform.html home      cec812ccb8a9ce1d9f5a0e0716bbcf710057a88fbbe8db4ba79fc3c6dd1f0eeb

robots.txt live/main 73dab0e6d5494620cd26655919cdda70fdf9fb7c0c295ea303c842bd543a9238
robots.txt home      46edc96f869935faacc503bcd17479282ee4e184da5b9dbd23f2033f6387e55b

sitemap.xml live/main 589ed157ed0d27a8df663c7d89683e8a9b015f29b587217cac8582dc435eb530
sitemap.xml home      8b4ec3ff2d40bcd654ffc8432ea21ee1f78d6fe83743d23bbd3fe1a15ec5353b
```

## Findings

- For the checked static files, **live matches imported Main static byte-for-byte**.
- Current Home static differs from live on every checked file.
- The earlier Home-only audit conclusion is now refined:
  - Home static is not the production mirror.
  - Imported Main static is the production mirror for these checked routes.
- Imported Astro is a different/newer contour, not the current public static
  production tree for the checked routes.

## Operational Implication

For immediate `specialtechnology.ru` maintenance:

- Treat imported Main static as the production evidence baseline.
- Treat Home static as a local divergent tree with pending/unknown changes.
- Treat Main Astro as a separate candidate contour that needs a product/design
  source-of-truth decision before use.

Do not deploy Home static wholesale.

## Recommended Next Step

Create a page-level diff packet:

1. Compare Home static vs imported Main static for the checked pages.
2. Classify differences as:
   - safe SEO/content pending change,
   - stale local change,
   - calculator/licensing-risk change,
   - manual decision needed.
3. Only then choose a small deploy packet or discard stale local deltas.
