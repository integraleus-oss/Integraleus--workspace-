# Audit Packet: <short name>

Status: draft
Risk of audited work: <LOW / MEDIUM / HIGH>
Audit mode: read-only
Date: <YYYY-MM-DD>

## Audit Goal

- <what the reviewer should verify>

## Files / Artifacts To Review

- <path>

## Context

- <minimal redacted context>

## Security Boundary

This packet may be sent to an external model or agent. If so, this is external send and requires data minimization first.

Before external review, confirm:

- [ ] no secrets/tokens/passwords/API keys;
- [ ] no `.env` contents;
- [ ] no raw Synology file contents;
- [ ] no personal Telegram/Discord message contents unless explicitly approved;
- [ ] no customer confidential data unless explicitly approved and redacted;
- [ ] no private prices/discounts/negotiation context;
- [ ] no database dumps/backups;
- [ ] no unredacted logs with tokens, cookies, auth headers, private URLs;
- [ ] no private local context unnecessary for the audit.

If any item cannot be checked cleanly, create `SECURITY_PRECHECK.md` first and do not send externally until approved.

## Allowed Reviewer Actions

- read listed files;
- inspect diffs;
- run read-only commands if needed;
- report findings.

## Forbidden Reviewer Actions

- edit files;
- run write/deploy/destructive commands;
- access secrets;
- contact external parties;
- send messages;
- broaden scope without asking.

## Review Questions

1. <question>
2. <question>
3. <question>

## Expected Output

Use findings-first structure:

- Verdict: GO / GO_WITH_FIXES / NO_GO
- Blockers
- Important findings
- Nice-to-have improvements
- Residual risks
- Recommended next step

## Evidence Available

- <EVIDENCE.md / logs / command output summary>
