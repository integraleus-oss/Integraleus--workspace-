# Evidence Backlog Audit

Date: 2026-08-25

## Verdict

The backlog is legitimate task evidence, not unexplained generated output. It should not be committed as one batch. Seven packages are useful final evidence as-is; fourteen packages are intermediate or superseded runs that should first be reduced to concise lineage evidence. No package should be deleted before the reduction is reviewed.

Inventory: 21 directories, 220 files, 1.4 MiB total. Types: 116 Markdown, 74 JSON, 12 text, 11 shell, 2 C#, and one each of Python, PNG, patch, HTML, and C# project file.

The earlier rough count of approximately 246 files was corrected by the complete inventory to 220.

## Safety and quality checks

- Basic secret-pattern scan found no private keys, bearer tokens, API keys, GitHub tokens, or password assignments.
- The backlog contains raw Claude review JSON with session IDs, token/cost metadata, and repeated review text. This is not a secret, but it is noisy and should not become the durable evidence layer.
- Many requirements, policy, brief, and review files are exact duplicates across retry directories. Preserve one canonical copy per lineage and identify retries by result/digest.
- No live deploy, push, service mutation, credential access, or customer-runtime proof is claimed by these packages.
- Canonical implementation commits referenced by the evidence were verified locally where applicable:
  - Alpha-Presale `95a5818` — declarative doctor readiness checks.
  - Main orchestrator `e2a755a5` — bounded review loops.
  - Main orchestrator `0ebd3fe5` — review/test-gate hardening.
  - Home Agent Factory `f93b744` — factory status diagnostics.
  - Alpha BPR `b9e6377` — portable Track F appliance.
  - Alpha BPR `5951d02` — universal read-only OPC UA transport.
  - Alpha BPR `061fcc8` — P3 recipe approval proof summary.
  - Alpha BPR `ad1c2a8` — universal read-only integration profiles.

## Package classification

### Alpha-Presale doctor

1. `2026-08-17-alpha-presale-doctor-pilot` — **consolidate**. Important first REWORK state, but superseded by the declarative redesign and final transfer. Retain the result, admitted findings, fixed baseline and diff digest; omit repeated production-task generations.
2. `2026-08-18-alpha-presale-doctor-manifest` — **consolidate**. Captures the architectural change from shell parsing to a declarative manifest. Retain task/result and final accepted review; omit four raw Claude JSON attempts.
3. `2026-08-18-alpha-presale-doctor-rework` — **consolidate**. Contains bounded rework history and repeated reviews. Retain the final result and the material unresolved/closed findings; omit six raw review envelopes.
4. `2026-08-18-alpha-presale-doctor-transfer` — **commit-ready**. Concise canonical transfer evidence: exact files, 25/25 focused tests, 121/121 full suite, and commit `95a5818`.

Recommended durable unit: one scoped doctor evidence commit after creating a short lineage summary from packages 1–3 and keeping package 4 intact.

### Home Agent Factory and orchestrator review hardening

5. `2026-08-18-home-agent-factory-status-pilot` — **consolidate**. Valuable R1–R5 failure-to-acceptance lineage and transfer to `f93b744`, but the generated task-contract revisions are redundant. Keep result plus transfer evidence.
6. `2026-08-18-orchestrator-review-loop-reduction` — **consolidate**. Underlies accepted commit `e2a755a5`; keep the final result, policy decision and final review. Remove repeated transcript/session variants from the durable set.
7. `2026-08-20-orchestrator-pilot3-hardening` — **consolidate**. Underlies `0ebd3fe5`; keep result, transfer evidence and accepted follow-up review, not both raw review transcripts.
8. `2026-08-20-orchestrator-regression-pilot` — **commit-ready**. Compact proof that safeguards passed and further speculative hardening should stop; also contains the accepted Track F scoped-commit audit.
9. `2026-08-21-orchestrator-dotnet-sandbox-regression` — **commit-ready**. Small reproducible regression fixture proving the writable external artifact root and 14/14 launcher regression.

Recommended durable units: one Factory status evidence commit for package 5; one orchestrator hardening evidence commit for packages 6–9 after pruning duplicate review transcripts.

### Alpha BPR Track F release audit

10. `2026-08-20-alpha-bpr-track-f-release-audit` — **consolidate**. Failed closed because packet path binding was wrong; useful as root-cause evidence, not as final product evidence.
11. `2026-08-20-alpha-bpr-track-f-release-audit-r2` — **consolidate**. Failed closed on a nondeterministic harness; retain root cause and produced audit result, deduplicate the repeated policy/specification packet.
12. `2026-08-20-alpha-bpr-track-f-release-audit-closure` — **commit-ready**. Final independent closure is accepted while the product disposition remains `DEFER`; this distinction is important and must remain explicit.

Recommended durable unit: one Track F audit-lineage commit with concise failure summaries from 10–11 and package 12 intact.

### Universal Integration v1 through R4

13. `2026-08-20-alpha-bpr-universal-integration-v1` — **consolidate**. Failed closed on ignored-state and scope handling; keep failure classification and safety boundary.
14. `2026-08-20-alpha-bpr-universal-integration-r2` — **consolidate**. Failed focused compilation; keep the compiler/root-cause evidence and prohibition on transfer.
15. `2026-08-21-alpha-bpr-universal-integration-r3` — **consolidate**. Failed focused test fixture-path resolution; keep the failure and external-artifact-root dependency.
16. `2026-08-21-alpha-bpr-universal-integration-r4` — **consolidate**. Build/tests passed but review admission failed; keep result and findings, not the repeated common packet files.
17. `2026-08-21-alpha-bpr-universal-integration-r4-repair` — **consolidate**. Review exhausted with open findings; keep result and exact remaining findings.
18. `2026-08-21-alpha-bpr-universal-integration-r4-closure` — **commit-ready after patch decision**. Final review accepted with 27/27 focused and 367/367 full tests. `TRANSFER.patch` is 88 KiB and duplicates code later represented by canonical commits; exclude it from the main-workspace evidence commit unless a standalone recovery patch is deliberately desired.

Recommended durable unit: one Universal Integration lineage commit containing concise outcomes for v1/R2/R3/R4/repair and final closure evidence. Exclude duplicated policy/spec/task-map files and normally exclude `TRANSFER.patch`. Canonical product source remains in Alpha BPR commits, not this workspace.

### TRIZ P3

19. `2026-08-21-alpha-bpr-triz-p3-proof-summary` — **retain as rejected-attempt evidence, then consolidate**. The orchestrated attempt used the wrong identity for TRIZ P3 and was not transferable. The real feature was later completed directly and committed as `061fcc8`. Keep the blocker and manual closure review so the failed attempt cannot be mistaken for accepted proof; omit the generated task packet duplication.

Recommended durable unit: include a short rejected-attempt record with the later canonical resolution, either in the Universal/Alpha BPR evidence commit or a small standalone TRIZ audit commit.

### Visual and standalone audits

20. `2026-08-23-orchestrator-architecture-visual` — **commit-ready separately**. Source HTML plus rendered PNG and checklist form one coherent visual deliverable. Keep separate from runtime evidence.
21. `2026-08-23-store-generator-audit` — **commit-ready separately**. A concise standalone security/readiness report. It should not be mixed with Alpha BPR or orchestrator implementation evidence.

## Recommended commit sequence

1. `docs: preserve alpha presale doctor evidence`
2. `docs: preserve home agent factory status evidence`
3. `docs: preserve orchestrator hardening evidence`
4. `docs: preserve alpha bpr track f audit evidence`
5. `docs: preserve universal integration audit lineage`
6. `docs: preserve rejected triz p3 orchestrator attempt`
7. `docs: add orchestrator architecture visual`
8. `docs: add store generator safety audit`

This sequence is a recommendation only. No backlog content was deleted, moved, staged, or committed during this audit.

## Next gate

Create concise lineage summaries and a precise keep/remove manifest for each commit group. Deletion of raw review envelopes, duplicate task contracts, or `TRANSFER.patch` requires explicit approval after that manifest is shown.
