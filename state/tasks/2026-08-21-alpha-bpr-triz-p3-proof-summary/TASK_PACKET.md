# Alpha BPR TRIZ P3 Proof-Summary — Prepare Packet

## Goal

Produce one independent, source-cited proof-summary for TRIZ concept P3:
the system browses an OPC UA information model, proposes a draft Customer
Integration Profile, and requires an engineer to confirm or correct mappings
before activation.

## Fixed point

- Evidence source: accepted universal-integration stages 0–4 at canonical
  commit `ad1c2a895b0221b2a5d6915e921ff5bb75be2a6f` in a fresh detached
  read-only-analysis worktree.
- Canonical Alpha BPR remains clean at `ad1c2a8` and is forbidden to change.
- Accepted fixture proof is not a connected Alpha Platform test.

## Required proof structure

1. Define P3 and distinguish it from the already implemented manual profile.
2. State the software-TRIZ analysis as `Source: heuristic-analogy`: system,
   main function, false-problem check, IFR, TC-1/TC-2, physical contradiction,
   and existing information resources.
3. Build a claim/evidence matrix with exact file and line citations. Every
   claim must be PASS, PARTIAL, FAIL, or NOT TESTED.
4. Cover at least: OPC UA browse/discovery, candidate inference, confidence or
   ambiguity handling, human confirmation, draft/activation state separation,
   dry-run, schema/profile validation, type/unit/quality/timestamp/freshness,
   arbitrary NodeIds/equipment, unchanged code path across three examples,
   read-only enforcement, and live-runtime evidence.
5. Reject the compromise "guess and auto-activate" explicitly.
6. End with an overall verdict and the smallest bounded next experiment,
   including measurable acceptance criteria and stop conditions.

## Boundaries

- Allowed output: `docs/evidence/TRIZ-P3-PROOF-SUMMARY.md` only in the isolated
  worktree.
- Read-only inspection of local source and sealed task artifacts is allowed.
- No implementation, source edits, test edits, generated profile activation,
  network, credentials, private endpoints, Alpha runtime, VMs, services,
  Gateway, customer data, commit, transfer, push, or deploy.
- Do not infer Alpha.Link support or introduce product/module names outside the
  canonical Alpha product cheatsheet.

## Acceptance

- One proof-summary exists at the exact allowlisted path and `git diff --check`
  passes.
- The summary distinguishes proved fixture capability from missing P3 and live
  Alpha Platform evidence.
- Every material conclusion has a local source citation or is labelled an
  inference/gap.
- Independent review reports zero blocker and zero major.

## Operator flow

`PREPARE -> explicit RUN -> review verdict -> separate decision on P3 experiment`
