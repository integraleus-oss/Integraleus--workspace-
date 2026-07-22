# Security Precheck: <short name>

Status: draft
Date: <YYYY-MM-DD>
Task packet: <path>

## Trigger

Use this precheck before any external review/send or when the task touches privacy-sensitive projects, secrets, production, access rights, customer data, personal messages, Synology/NAS data, HumanLike Agent, RAG/knowledge ingestion, or background automation.

## Classification

Risk tier: <LOW / MEDIUM / HIGH>

Privacy-sensitive project:

- [ ] `projects/openclaw-shared-memory`
- [ ] NAS/Synology migration
- [ ] `projects/humanlike-agent`
- [ ] RAG/knowledge-base ingestion
- [ ] customer documents/contracts/pricing
- [ ] Alpha-Bot with `.env`, logs, chats, customer data, or private RAG docs
- [ ] other: <describe>

## External Send Check

Is anything being sent to Claude, Codex/OpenAI, web tools, hosted review, marketplace/browser pages, remote servers, public/customer channels, or any service outside the home LAN?

- [ ] no
- [ ] yes, explicit approval recorded below

External destination:

- <service/channel/server>

Approval record:

- <who approved, where, timestamp/message id>

## Forbidden Data Checklist

Confirm the outgoing packet/artifact excludes:

- [ ] secrets/tokens/passwords/API keys;
- [ ] `.env` contents;
- [ ] raw Synology file contents;
- [ ] personal Telegram/Discord messages unless explicitly approved;
- [ ] customer confidential data unless explicitly approved and redacted;
- [ ] private prices/discounts/negotiation context;
- [ ] full database dumps/backups;
- [ ] unredacted logs containing tokens, cookies, auth headers, private URLs;
- [ ] unnecessary private local context.

## Redaction Summary

- <what was removed or generalized>

## Allowed Data Summary

- <what remains safe to send or use>

## Stop Conditions

Stop before proceeding if:

- any forbidden data remains;
- approval is missing for external send;
- task unexpectedly becomes HIGH-risk;
- reviewer would need secrets/raw private data;
- Synology root-level/DSM action is required without approval;
- production/access/root/destructive action is required without approval.

## Decision

- [ ] Safe to proceed locally only
- [ ] Safe to send externally with approval
- [ ] Blocked until redaction/approval

Decision notes:

- <notes>
