# Discord Work Operationalization

Started: 2026-07-09
Status: active

## Goal

Turn the verified Discord work transfer into an actionable Home work backlog for:
specialtechnology.ru, Alpha content, calculator/licensing flows, UMOSS/WeRTSim,
promo/content assets, and related operational monitors.

## Source Package

- Transfer root: `/home/stanislav/.openclaw/workspace/transfers/discord-work-full-20260709/`
- Package summary: `SUMMARY.json`
- Integrity: `sha256sum -c SHA256SUMS` passed on Home on 2026-07-09 16:12 MSK.
- Main registry: `sources/state-task-2026-06-22-discord-work-registry/registry.md`
- Server inventory: `sources/state-task-2026-06-22-discord-work-registry/server_inventory.md`
- Transfer status: `sources/state-task-2026-07-09-discord-threads-full-home-transfer/status.md`

## Guardrails

- Do not publish or deploy from Discord artifacts directly.
- Treat the transfer as evidence and backlog input, not as an authoritative production tree.
- Before editing `specialtechnology.ru`, determine the authoritative contour:
  old static `agents/main/website/spectech` vs newer `special-tech-astro`.
- For Alpha product/licensing content, apply Alpha product/licensing guardrails before any final text or calculation.
- For UMOSS/WeRTSim, treat `UMOSS_3` as a design prototype until legal/claims/CDN/demo-form checks pass.
- Preserve the transfer package as read-only evidence; create derived work artifacts elsewhere.

## Checklist

- [x] Confirm transfer package exists on Home.
- [x] Confirm file count/size at a high level: 512 files, 765M.
- [x] Re-run `sha256sum -c SHA256SUMS` on Home.
- [x] Read transfer status and prior registry.
- [x] Create this operational task package.
- [x] Create `WORKING_INDEX.md` with prioritized workstreams.
- [x] Select first safe slice: specialtechnology.ru source-of-truth audit.
- [x] Create slice-specific artifact before coding/deploying.
- [x] Run initial source-of-truth audit for the selected slice.
- [x] Search Main for missing Discord/server-inventory artifacts.
- [x] Create `MAIN_SERVER_FILE_SEARCH.md`.
- [x] Draft safe Main-to-Home evidence import plan.
- [x] Attempt Main-to-Home import.
- [x] Resume Main-to-Home import after Main SSH connectivity returns.
- [x] Verify imported evidence manifest/checksums.
- [ ] Execute only the approved slice.

## Candidate First Slice

Recommended first slice: **specialtechnology.ru source-of-truth audit**.

Reason: Discord history contains accepted and rejected visual/content changes,
and server inventory shows two competing contours plus local modifications.
This slice should not deploy anything. It should produce an evidence-backed
decision: which tree is authoritative, what differs from live, and what is safe
to touch next.

Acceptance:

- Identify live URL state and local source contours.
- List local modified files and recent commits.
- Compare accepted/rejected Discord decisions that affect site appearance/content.
- Produce `SPECTECH_SOURCE_OF_TRUTH_AUDIT.md`.
- No deploy, no service changes, no external posting.
