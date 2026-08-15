# Shared Alpha project examples — extraction and routing

Source: public ownCloud share `Dz5n7RxIcNnPhdv`, folder `Проекты HMI+DevStudio`.

## Scope

- Download and preserve the source package locally as read-only reference material.
- Inventory projects `12105`, `14443`, and `20167` without executing unknown binaries.
- Extract reusable Alpha.HMI / Alpha.DevStudio patterns, configuration conventions, screen structures, scripts, and validation lessons.
- Route only relevant, evidence-backed knowledge to:
  - `/home/stanislav/work/alpha-hmi-dev`;
  - `/home/stanislav/projects/alpha-bpr`;
  - `/home/stanislav/workspace/alpha-presale`.
- Keep source-specific names, credentials, endpoints, customer data, and operational settings out of reusable guidance unless explicitly sanitized and necessary.

## Checklist

- [x] Download completed and checksum recorded.
- [x] Archive/path traversal and file-type inventory completed before extraction/use.
- [x] Per-project structure and Alpha component usage documented.
- [x] Reusable patterns classified with evidence paths.
- [x] Alpha-HMI-DEV knowledge updated where applicable.
- [x] Alpha-BPR knowledge updated where applicable.
- [x] Alpha-Presale knowledge updated where applicable.
- [x] Deprecated product-name scan completed.
- [x] Git status and relevant checks recorded for all three repositories.
- [x] No commit unless explicitly requested.

## Runtime verification — 20167

- [x] Create an isolated working copy outside the active Alpha-BPR roots.
- [x] Inventory and neutralize external PLC/OPC/Modbus endpoints before execution.
- [x] Check HMI/DevStudio dependencies and versions.
- [x] Import and compile the Alpha.HMI package; preserve logs and output hashes.
- [x] Open the compiled HMI in an isolated display session and capture evidence.
- [ ] Connect only to test data/Alpha.Imitator; prove at least one command/readback path if feasible.
- [x] Confirm Alpha-BPR services/configuration were not changed or restarted.
- [x] Record verified findings and gaps; no commit unless requested.

## Status

Source archives are downloaded, checked, extracted, and statically analyzed. Reusable guidance has been routed to separate project documents. Runtime verification of project 20167 confirmed HMI compile/render and DevStudio compile/build on an isolated working copy. End-to-end test data and command/readback remain open because an isolated Alpha.Domain/Alpha.Server/Alpha.Imitator instance requires a separate root-level network namespace or an approved alternate-port deployment. Active Alpha-BPR services were unchanged. No commit was created.
