---
name: "compliance-readiness-checklist-ru"
description: "RU compliance-readiness checklists with evidence, gaps, risks, and legal-review boundaries."
---

# Compliance Readiness Checklist RU

Use this skill to prepare internal Russian-language compliance-readiness checklists for documents, workflows, controls, governance drafts, operational procedures, and external-send preflights.

Default posture: readiness check only. Do not state that something is legally compliant, certified, safe to sign, regulator-ready, audit-passed, or officially approved unless the user provides authoritative evidence and explicitly asks for that wording.

## Quick Workflow

1. Classify the review target:
   - document draft;
   - SOP/process;
   - commercial proposal workflow;
   - contract risk triage workflow;
   - data/privacy handling workflow;
   - external-send preflight;
   - automation or connector plan.
2. Identify applicable risk domains:
   - source evidence;
   - privacy/personal data;
   - pricing/commercial terms;
   - legal wording/contracts;
   - security/secrets/access;
   - Alpha licensing/SKU/product claims;
   - external publication/sending;
   - audit trail and ownership.
3. Gather sources and separate:
   - confirmed facts;
   - assumptions;
   - missing evidence;
   - decisions requiring owner/legal/security approval.
4. Produce a checklist with pass/fail/needs-review fields.
5. Mark blockers and escalation path.
6. Avoid final compliance conclusions.

## Required Output Structure

For substantial checklists, include:

1. Title and draft status.
2. Review target and scope.
3. Sources reviewed.
4. Out-of-scope areas.
5. Readiness matrix.
6. Evidence requirements.
7. Gaps and blockers.
8. Risk notes by domain.
9. Required approvals or specialist reviews.
10. Final readiness summary with cautious wording.
11. Open questions.

Use status labels:

- `pass`;
- `needs evidence`;
- `needs owner approval`;
- `needs legal review`;
- `needs security review`;
- `blocked`;
- `out of scope`.

## Readiness Matrix Template

```text
| Domain | Check | Status | Evidence | Owner / next step |
| --- | --- | --- | --- | --- |
| Source evidence | ... | needs evidence | ... | ... |
| Privacy | ... | needs review | ... | ... |
| Legal wording | ... | needs legal review | ... | ... |
| External send | ... | blocked until approval | ... | ... |
```

## Source Discipline

Do not invent laws, certifications, internal policies, audit outcomes, customer permissions, approval rights, or security posture.

Use explicit labels:

```text
Основано на:
- ...

Не проверено:
- ...

Требует отдельного review:
- ...
```

If evidence is missing, mark the item `needs evidence` or `blocked`; do not infer compliance from silence.

## Routing Rules

Route specialized content instead of guessing:

- Legal claims, contracts, NDA, SLA, signing authority -> legal review / `contract-risk-review-ru` for triage only.
- Uploaded PDF/DOCX/XLSX -> `document-pipeline` before relying on content.
- Alpha Platform licensing, SKU, tags, SLA, WEB, Terminal/RDP, Historian, Reports -> `alpha-licensing-qa` / `alpha-platform-presale`.
- SOP/process quality -> `sop-writer-ru` or `process-documentation-ru` when available.
- Security, secrets, auth, config, production access, connectors/API/email/browser automation -> security review before changes.

## Boundaries

Do not:

- provide legal advice;
- certify compliance;
- say a document can be signed;
- claim audit readiness without evidence;
- publish or send anything externally;
- expose prices, customer data, personal data, contract text, secrets, credentials, private URLs, or negotiation details;
- change runtime/config/access/automation/CRM/repository state.

Use cautious labels:

- `readiness preflight`;
- `внутренняя предварительная проверка`;
- `не является юридическим заключением`;
- `не подтверждает соответствие требованиям закона`;
- `требует профильного review`.

## Quality Checklist

Before presenting a readiness checklist, verify:

- target and scope are clear;
- evidence and missing evidence are separated;
- legal/security/privacy/commercial items are routed;
- no final compliance conclusion is asserted;
- blockers are visible;
- external-send approval is explicit;
- confidential details are redacted for the current channel;
- next steps are actionable and bounded.

## Stop Signals

Stop and request approval or specialist review when:

- the user asks for a legal conclusion, certification, or sign-off;
- production config, auth, access rights, CRM, cron, connectors, email/browser/API automation, or external publication would change;
- sensitive details would be exposed in a group chat;
- evidence is missing for a material claim;
- deadline-sensitive regulatory or legal questions arise.

## Examples

Good requests:

- `Сделай compliance-readiness checklist для SOP подготовки КП`.
- `Проверь, чего не хватает перед внешней отправкой документа`.
- `Собери preflight по privacy/pricing/legal/security перед запуском процесса`.
- `Подготовь список blockers перед legal/security review`.

Bad behavior to avoid:

- saying `соответствует законодательству` without legal authority;
- treating a checklist as legal approval;
- hiding blockers to make the process look ready;
- exposing customer or contract details in group-visible output;
- approving automation/connectors without security review.
