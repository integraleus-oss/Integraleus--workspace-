# Task Note: <short name>

Status: draft
Risk: LOW
Owner: <main agent / human / job>
Date: <YYYY-MM-DD>

## Use When

Use this fast path for small but non-trivial work that is local, low-risk, and does not touch private data, production, secrets, access rights, Synology root/DSM settings, or external sending.

LOW is void and must be reclassified to MEDIUM or HIGH if private data, customer data, personal messages, secrets, production systems, access rights, destructive actions, or external send appear.

## Goal

- <what should be achieved>

## Scope

Allowed:

- <files/systems/actions>

Forbidden:

- secrets, `.env`, credentials;
- production deploy/access/config changes;
- Synology root-level or DSM changes;
- external send or public/customer-facing messages;
- raw Synology data export;
- unrelated cleanup.

## Touched Files

- <path>

## Checks

- [ ] <check command or manual verification>

## Result

- <what changed or what was learned>

## Next

- <follow-up, if any>
