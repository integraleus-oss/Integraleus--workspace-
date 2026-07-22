# Knowledge Base Review - 2026-06-21

## Checklist

- [x] Locate knowledge-base roots.
- [x] Read top-level README / INDEX / operator guidance.
- [x] Count OpenClaw KB registry entries by scope, status, privacy, and source type.
- [x] Verify Alpha Platform transfer checksum manifest.
- [x] Identify safe routing and privacy constraints for group-chat use.
- [ ] Restore or locate missing OpenClaw KB CLI scripts for transferred KB validation/listing.
- [ ] Decide whether 2026-06-17 transfers should be mounted as active retrieval sources.

## Roots Found

### Live workspace skeleton

Path: `/home/stanislav/.openclaw/workspace/data/knowledge_base`

Current contents are only:

- `README.md`
- `INDEX.md`
- `OPERATOR_GUIDE_RU.md`
- `Презентация_Тема_знаний_для_агента.pptx`

This is a structure/skeleton, not the populated working corpus.

### OpenClaw Knowledge Base transfer

Path: `/home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer`

Transfer README says it was created on `2026-06-17T14:41:16Z` from
`/root/.openclaw/workspace`.

Included:

- `MEMORY.md`
- `memory/`
- `knowledge/`
- `data/knowledge_base/`
- `agents/main/MEMORY.md`

Excluded by default:

- `state/tasks`
- Qdrant internals
- runtime secrets/auth/env/ssh

Observed size/count:

- `582` files total
- `15M` total size
- major areas:
  - `memory`: `452` files, `13M`
  - `data`: `90` files, `728K`
  - `knowledge`: `35` files, `700K`
  - `agents`: `1` file, `16K`
  - `manifests`: `2` files, `92K`

### Alpha Platform Knowledge Base transfer

Path: `/home/stanislav/work/alpha-platform-knowledge-base/2026-06-17_transfer`

Transfer README says it was assembled on `2026-06-17 UTC` from
`/root/.openclaw/workspace`.

Important note from README: this is not a live working root and should not
replace `/home/stanislav/work/alpha-hmi-dev` or
`/home/stanislav/workspace/alpha-presale` without a separate decision.

Observed size/count:

- `1293` files total
- `42M` total size from manifest `du.txt`
- SHA256 manifest verification: `OK`
- major areas:
  - `agents/main/docs/alpha_platform`: `62` files, `18M`
  - `data/licensing_automiq`: `806` files, `8.4M`
  - `data/alpha_hmi`: `35` files, `880K`
  - `workspace_selected/docs`: `118` files, `4.4M`
  - `.agents/skills`: `16` files, `148K`

## OpenClaw KB Structure

Canonical structure described by `data/knowledge_base/README.md`:

- `inbox/`: new raw materials
- `topics/<topic>/raw/`: source materials by topic
- `topics/<topic>/processed/`: cleaned/marked-up versions
- `topics/<topic>/final/`: approved materials
- `topics/<topic>/SUMMARY.md`: topic summary
- `topics/<topic>/RULES.md`: mandatory rules/constraints
- `topics/<topic>/FAQ.md`: common Q/A
- `topics/<topic>/CHANGELOG.md`: change history
- `registry.jsonl`: one JSON object per KB item
- `schemas/item.schema.json`: registry metadata contract
- `OPERATOR_GUIDE_RU.md`: operator instructions
- `wiki/`: curated memory-wiki vault

Main scopes from `INDEX.md`:

- `personal`: private research links and notes
- `alpha`: Alpha Platform / Alpha.SCADA / Alpha.HMI materials
- `ops`: OpenClaw runtime and infrastructure operations

## OpenClaw KB Registry Inventory

Registry path:
`/home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer/data/knowledge_base/registry.jsonl`

Counts:

- total items: `26`
- by scope:
  - `personal`: `12`
  - `ops`: `10`
  - `alpha`: `4`
- by status:
  - `raw`: `13`
  - `processed`: `1`
  - `verified`: `7`
  - `final`: `5`
- by privacy:
  - `local-private`: `19`
  - `confidential`: `4`
  - `public`: `3`
- by source kind:
  - `note`: `10`
  - `docx`: `8`
  - `url`: `7`
  - `xlsx`: `1`

Topic file counts:

- `personal`: `26`
- `ops`: `17`
- `alpha`: `8`

Usability implication:

- Default answer layer should prefer only `verified` and `final`.
- `raw` and `processed` should be treated as search hints, not final truth.
- `personal`, `confidential`, pricing, and customer-sensitive materials must
  not be surfaced into group chats or broad/public search.

## Curated Wiki Layer

Path:
`/home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer/data/knowledge_base/wiki`

Mode from `WIKI.md`:

- plugin: `memory-wiki`
- vault mode: `isolated`
- render mode: `native`
- search corpus default: `wiki`

Important pages:

- `entities/alpha-platform.md`
- `entities/alpha-hmi.md`
- `entities/openclaw-runtime.md`
- `syntheses/alpha-hmi-validated-omobj.md`
- `syntheses/ops-audit-decisions.md`
- `syntheses/home-codex-oauth-refresh-recovery-2026-06-17.md`

Privacy review reports `24` entries, including local-private and confidential
Alpha/OpenClaw claims. Treat this layer as useful but privacy-routed.

## Alpha Platform KB Map

Important areas from README and file inventory:

- `agents/main/docs/alpha_platform/`: extracted/reference Alpha Platform docs corpus.
- `data/licensing_automiq/`: licensing/tariff/source data and hard checks.
- `data/alpha_hmi/`: Alpha.HMI data sources.
- `.agents/skills/alpha-licensing-qa/`: mandatory licensing QA skill from the transfer.
- `.agents/skills/alpha-platform-presale/`: presale orchestration skill.
- `.agents/skills/alpha-hmi-omobj-generator/`: Alpha.HMI generation/validation skill.
- `memory/alpha_platform/` and `workspace_selected/memory/`: durable Alpha-related notes.
- `workspace_selected/docs/`: Alpha-related docs from workspace `docs/`.
- `workspace_selected/scripts/` and `tests/alpha_hmi/`: Alpha.HMI helper scripts and tests.
- `workspace_selected/state/tasks/`: task-local history for Alpha/HMI/presale work.

Operational rule:

- For live work, prefer active roots:
  - `/home/stanislav/work/alpha-hmi-dev`
  - `/home/stanislav/workspace/alpha-presale`
- Use the transfer as reference/evidence unless Stanislav separately decides
  to merge or mount it.

## Verification Performed

- Read transfer READMEs for both KB roots.
- Read OpenClaw KB README, INDEX, and operator guide.
- Counted OpenClaw KB registry entries by metadata fields.
- Checked live workspace skeleton contents.
- Checked Alpha Platform transfer SHA256 manifest:
  - command: `sha256sum -c --quiet manifests/SHA256SUMS && echo OK`
  - result: `OK`

Could not run OpenClaw KB validate/list in the transfer root:

- attempted from `/home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer`
- expected command from docs: `python3 scripts/kb_ingest.py validate`
- result: `scripts/kb_ingest.py` is missing in that transfer tree
- search also did not find `kb_ingest.py` or `test_kb_ingest_smoke.sh` under
  `/home/stanislav/.openclaw/workspace`

## Current Understanding

I have now studied the KB at the structural and operational level:

- where the populated corpora actually are;
- what is active skeleton vs transferred archive;
- how OpenClaw KB expects raw/processed/verified/final promotion;
- what is safe for group answers and what must stay private/confidential;
- which Alpha Platform areas are available and which live project roots should
  remain authoritative for ongoing implementation.

I have not read every raw/private/personal document line-by-line, deliberately:
that would be both inefficient and unsafe for group-chat context. For future
answers, I should route by topic and read only the relevant verified/final or
project-source files.

## Recommended Next Steps

1. Decide whether the two 2026-06-17 transfer roots should be registered as
   active retrieval sources or remain manual reference archives.
2. Restore or locate the missing `scripts/kb_ingest.py` and smoke tests if the
   OpenClaw KB transfer is expected to be self-validating.
3. For Alpha questions, continue following the existing guardrails:
   - read current product cheatsheet before product/module answers;
   - run licensing preflight before licensing/TKP calculations;
   - use Alpha-HMI-DEV as the live source for Alpha.HMI generation work.
4. Promote useful raw/processed KB items to verified/final only with evidence,
   not by bulk trust.
