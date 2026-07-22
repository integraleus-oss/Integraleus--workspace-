# Home Knowledge Base Topic Audit

Date: 2026-07-22
Scope: read-only audit of Home/OpenClaw workspace for existing knowledge-base and shared-memory topics.

## Checklist

- [x] Record audit scope and boundaries
- [x] Search workspace files for knowledge-base/shared-memory references
- [x] Search memory and daily notes for relevant history
- [x] Check visible project/state/task artifacts
- [x] Check OpenClaw session history if available
- [x] Summarize topic clusters, owners, risks, and next actions
- [x] Record verification commands and git status

## Boundaries

- No Synology changes.
- No OpenClaw runtime configuration changes.
- No import, export, or promotion of memory records.
- Do not expose raw private file contents; summarize only what is needed.

## Executive Summary

Home already has several knowledge-base related layers, but they are not one active shared canon:

1. Live OpenClaw workspace KB skeleton:
   `/home/stanislav/.openclaw/workspace/data/knowledge_base`
2. Populated OpenClaw KB transfer archive:
   `/home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer`
3. Populated Alpha Platform KB transfer archive:
   `/home/stanislav/work/alpha-platform-knowledge-base/2026-06-17_transfer`
4. New shared memory project scaffold:
   `projects/openclaw-shared-memory`
5. App-local knowledge/memory layers:
   `projects/alpha-bot` and `projects/humanlike-agent`
6. Supporting prior audit:
   `state/knowledge-base-review-2026-06-21.md`

The main risk is fragmentation: similar concepts are spread across markdown memory, transferred KB archives, Alpha-Bot RAG/SQLite, HumanLike SQLite/RAG, and the new shared-memory scaffold. None of those should be treated as the single source of truth until the shared-memory Phase 0+pilot path is proven.

## Topic Clusters

### 1. Live Workspace Knowledge Base Skeleton

Path: `/home/stanislav/.openclaw/workspace/data/knowledge_base`

Observed contents:

- `README.md`
- `INDEX.md`
- `OPERATOR_GUIDE_RU.md`
- `Презентация_Тема_знаний_для_агента.pptx`

Observed size/count:

- `4` files
- `68K`

Assessment:

- This is a structural bootstrap, not a populated active corpus.
- It can document the intended KB layout, but should not be used as evidence that Home has an active canonical KB.

### 2. OpenClaw Knowledge Base Transfer

Path: `/home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer`

Observed size/count:

- `583` files by current `find`
- `15M`

Prior review summarized this as a transfer from `/root/.openclaw/workspace` including `MEMORY.md`, `memory/`, `knowledge/`, `data/knowledge_base/`, and `agents/main/MEMORY.md`. It deliberately excluded full `state/tasks`, Qdrant/vector DB internals, runtime secrets/auth/env/ssh.

Registry inventory from:
`/home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer/data/knowledge_base/registry.jsonl`

- total: `26`
- scope: `personal=12`, `ops=10`, `alpha=4`
- status: `raw=13`, `processed=1`, `verified=7`, `final=5`
- privacy: `local-private=19`, `confidential=4`, `public=3`
- source kind: `note=10`, `docx=8`, `url=7`, `xlsx=1`

Assessment:

- This is the richest OpenClaw KB archive on Home.
- It is not live runtime memory.
- Only `verified` and `final` items should be preferred for answers.
- `raw`, `processed`, `personal`, and `confidential` items should stay behind routing/review boundaries.

### 3. Curated Wiki Layer Inside OpenClaw Transfer

Path:
`/home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer/data/knowledge_base/wiki`

Notable files seen:

- `WIKI.md`
- `entities/openclaw-runtime.md`
- `entities/alpha-platform.md`
- `entities/alpha-hmi.md`
- `syntheses/ops-audit-decisions.md`
- `syntheses/home-codex-oauth-refresh-recovery-2026-06-17.md`
- reports for claim health, privacy review, provenance coverage, stale pages, relationship graph

Assessment:

- This looks like the closest predecessor to a curated knowledge graph/wiki.
- It already has provenance/privacy review concepts that map well to the new shared-memory canon.
- It should be treated as a candidate source for migration, not imported automatically.

### 4. Alpha Platform Knowledge Base Transfer

Path: `/home/stanislav/work/alpha-platform-knowledge-base/2026-06-17_transfer`

Observed size/count:

- `1293` files
- `42M`

Important areas:

- `agents/main/docs/alpha_platform`
- `data/licensing_automiq`
- `data/alpha_hmi`
- `alpha-presale`
- `workspace_selected/docs`
- `workspace_selected/state/tasks`
- `tests/alpha_hmi`

Assessment:

- This is a large Alpha-specific evidence/reference archive.
- It should not replace active project roots such as `/home/stanislav/work/alpha-hmi-dev` or `/home/stanislav/workspace/alpha-presale` without a separate decision.
- For Alpha product answers, current guardrails still dominate: product cheatsheet first; licensing preflight before calculations.

### 5. New OpenClaw Shared Memory Scaffold

Path: `projects/openclaw-shared-memory`

Status:

- Baseline scaffold committed as `acccbae docs: add OpenClaw shared memory scaffold`.
- Current project tree is clean except this audit file.
- Phase 0 hardening has not started.
- Synology, OpenClaw runtime config, and real memory import have not been touched.

Observed size/count:

- `32` tracked/intended files outside ignored `dist` and `__pycache__`
- `308K`

Assessment:

- This is the right place to consolidate future shared canon work.
- It is not currently connected to runtime, Synology, Alpha-Bot, HumanLike, or existing markdown memory.

### 6. Alpha-Bot Knowledge and Memory Layer

Paths:

- `projects/alpha-bot`
- `/opt/alpha-bot-data`

Observed:

- `projects/alpha-bot/knowledge_base.py` contains a compact Alpha Platform system prompt.
- `projects/alpha-bot/rag.py` implements hybrid RAG with ChromaDB + BM25 + reranking.
- `projects/alpha-bot/conversation_memory.py` uses SQLite for contextual memory.
- `/opt/alpha-bot-data/chroma_db/chroma.sqlite3` exists.
- `/opt/alpha-bot-data/conversations.db` exists.

Assessment:

- Alpha-Bot has its own app-local RAG and conversation memory.
- It is an important future consumer/source candidate, but it is not a shared canon.
- It should not be bulk-merged into shared memory; only durable decisions/facts should be proposed with provenance.

### 7. HumanLike Agent Knowledge and Memory Layer

Path: `projects/humanlike-agent`

Observed:

- `memory.py` stores long-term chat memory in SQLite.
- `rag_client.py` is designed to reuse the Alpha-Bot index path.
- `README.md` describes SQLite memory, missions, and RAG-like behavior.

Assessment:

- HumanLike Agent is another app-local memory layer.
- It should connect to future shared memory through a role-scoped gateway/API, not by direct unrestricted DB access.

### 8. Session/Transcript Visibility

Attempted:

- `sessions_list` search for `База знаний`
- `sessions_list` search for `knowledge base`
- session-corpus `memory_search` for `Telegram topic База знаний knowledge base review shared memory session`

Result:

- `sessions_list` returned no directly matching visible session keys.
- session-corpus `memory_search` timed out due to embedding/provider error.

Assessment:

- This audit cannot claim full coverage of historical chat/session transcripts.
- File and memory evidence is still enough to identify the main Home-side KB topic clusters.

## Risks

1. Fragmented authority:
   memory files, transfer archives, app-local SQLite, Alpha-Bot RAG, HumanLike memory, and shared-memory scaffold all contain partially overlapping context.

2. Privacy routing:
   existing OpenClaw KB transfer has mostly `local-private` and some `confidential` material. Group-chat answers must not expose raw/private content.

3. Stale archive confusion:
   the 2026-06-17 transfer roots are valuable, but they are archives. They should not silently become active runtime truth.

4. App-local memory drift:
   Alpha-Bot and HumanLike maintain their own SQLite memories. Without a shared canon proposal path, they can diverge from main-agent decisions.

5. Missing live validation tooling:
   prior audit notes expected `scripts/kb_ingest.py` was not present in the transfer tree, so the old KB archive is not self-validating as-is.

## Recommendations

1. Treat `projects/openclaw-shared-memory` as the consolidation project for shared canon work.
2. Keep current markdown files and transfer archives as bootstrap/evidence sources until after Phase 0 and pilots.
3. Do not bulk-import old KB/memory. Start with candidate proposals for a small set of `decision`, `state`, and `fact` records.
4. Make Alpha-Bot and HumanLike future clients of the MCP/API gateway, not privileged DB writers.
5. Use the curated wiki layer from the OpenClaw transfer as a migration input candidate because it already has provenance/privacy concepts.
6. Before any migration, define a source priority table:
   current guardrail files > approved decisions/state > verified/final KB records > active project docs > raw/processed archives.
7. Add a future Phase 1/2 task to verify whether the old KB transfer should be mounted as read-only retrieval source.

## Evidence Log

- Created this audit artifact:
  `projects/openclaw-shared-memory/docs/HOME_KNOWLEDGE_BASE_TOPIC_AUDIT.md`
- Memory recall:
  `memory_search` found the 2026-06-17 KB transfer notes, the 2026-06-21 review, and the 2026-07-22 shared-memory discussion.
- File search:
  `rg -n -i "база знаний|knowledge[-_ ]base|knowledge_base|shared memory|shared-memory|pgvector|canon|канон|канони" .`
- Existing review read:
  `state/knowledge-base-review-2026-06-21.md`
- Root counts:
  `find /home/stanislav/.openclaw/workspace/data/knowledge_base -type f | wc -l` -> `4`
  `find /home/stanislav/work/openclaw-knowledge-base/2026-06-17_transfer -type f | wc -l` -> `583`
  `find /home/stanislav/work/alpha-platform-knowledge-base/2026-06-17_transfer -type f | wc -l` -> `1293`
  `find projects/openclaw-shared-memory -type f -not -path '*/dist/*' -not -path '*/__pycache__/*' | wc -l` -> `32`
- Size check:
  live skeleton `68K`, OpenClaw transfer `15M`, Alpha transfer `42M`, shared-memory project `308K`
- OpenClaw KB registry stats:
  total `26`; scope `personal=12`, `ops=10`, `alpha=4`; status `raw=13`, `processed=1`, `verified=7`, `final=5`; privacy `local-private=19`, `confidential=4`, `public=3`
- Session-history limitation:
  `sessions_list` found no directly matching visible session keys for `База знаний` or `knowledge base`; session-corpus memory search timed out.
- Git status note:
  `projects/openclaw-shared-memory/docs/HOME_KNOWLEDGE_BASE_TOPIC_AUDIT.md` is newly added.
  `state/knowledge-base-review-2026-06-21.md` is also untracked in the outer workspace and predates this audit.
