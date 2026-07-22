# Main To Home Evidence Import Plan

Created: 2026-07-09
Status: draft plan, not executed

## Goal

Bring the Main-only Discord/work artifacts into Home as quarantined evidence so
future work can compare and decide source-of-truth without overwriting active
Home working trees.

## Source

Main server:

- `root@155.212.227.115`
- Source root: `/root/.openclaw/workspace`

Artifacts identified by `MAIN_SERVER_FILE_SEARCH.md`:

- `special-tech-astro/`
- `knowledge/rewrite/`
- `tmp/alpha_hmi_libs_20260506/UMOSS_3/`
- `tmp_specialtechnology_calculator.html`
- `tmp_specialtechnology_calculator.js`
- SEO/Webmaster evidence files
- special-tech deploy archives

## Destination

Quarantine/evidence root on Home:

- `/home/stanislav/.openclaw/workspace/transfers/main-server-evidence-20260709/`

Do not copy into:

- `website/spectech/`
- `special-tech-astro/`
- `knowledge/rewrite/`
- `tmp/alpha_hmi_libs_20260506/UMOSS_3/`

## Import Rules

- Read from Main only.
- Preserve source relative paths under the quarantine root.
- Produce `MANIFEST.tsv` with path, size, mtime, and sha256 for every copied file.
- Produce `SOURCE_COMMANDS.md` with the exact rsync/ssh commands used.
- After copy, run checksum verification on Home.
- Do not deploy, build, install packages, or run project scripts as part of import.
- Do not delete anything from Main or Home.

## Candidate Copy Set

### Site Contours

- `/root/.openclaw/workspace/special-tech-astro/`
- `/root/.openclaw/workspace/agents/main/website/spectech/`

Reason:

- Needed for live vs Home static vs Main static vs Main Astro comparison.

### Calculator Evidence

- `/root/.openclaw/workspace/tmp_specialtechnology_calculator.html`
- `/root/.openclaw/workspace/tmp_specialtechnology_calculator.js`
- `/root/.openclaw/workspace/agents/main/website/spectech/calculator.html`
- `/root/.openclaw/workspace/agents/main/website/spectech/send_calc.php`

Reason:

- Needed for `CALCULATOR_SOURCE_AND_RULES_AUDIT.md`.

### Articles

- `/root/.openclaw/workspace/knowledge/rewrite/`

Reason:

- Needed for `ALPHA_ARTICLES_PUBLICATION_MAP.md`.

### UMOSS / WeRTSim

- `/root/.openclaw/workspace/tmp/alpha_hmi_libs_20260506/UMOSS_3/`

Reason:

- Needed for `UMOSS_PRODUCTION_CANDIDATE_CHECKLIST.md`.

### SEO / Webmaster Evidence

- `/root/.openclaw/workspace/seo_*specialtechnology*`
- `/root/.openclaw/workspace/yandex_webmaster_*`

Reason:

- Needed to understand accepted SEO fixes and baseline data before new edits.

### Deploy Provenance

- `/root/.openclaw/workspace/special-tech-astro-deploy.zip`
- `/root/.openclaw/workspace/special-tech-http-deploy.php`
- `/root/.openclaw/workspace/special-tech-http-deploy.zip`
- `/root/.openclaw/workspace/special-tech-production-deploy-2026-05-14.tar.gz`
- `/root/.openclaw/workspace/special-tech-production-deploy-2026-05-14.tar.gz.sha256`

Reason:

- Provenance only; not a deploy instruction.

## Verification

After import:

1. `find transfers/main-server-evidence-20260709 -type f | wc -l`
2. Generate `MANIFEST.tsv`.
3. Verify sha256 entries.
4. Compare high-level sizes against Main.
5. Update:
   - `MAIN_SERVER_FILE_SEARCH.md`
   - `SPECTECH_SOURCE_OF_TRUTH_AUDIT.md`
   - `WORKING_INDEX.md`

## Acceptance

- Evidence folder exists on Home.
- All copied files are under `transfers/main-server-evidence-20260709/`.
- Manifest/checksum verification passes.
- No working tree, live site, service, config, or deployment target is changed.

## Stop Conditions

- SSH to Main fails.
- Any checksum mismatch appears after copy.
- Destination would overlap with an active working tree.
- Copied data unexpectedly contains secrets or private material that should not
  be retained in the working evidence package.
