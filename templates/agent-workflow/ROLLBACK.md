# Rollback: <short name>

Status: draft
Date: <YYYY-MM-DD>
Task packet: <path>

## Scope

This rollback plan covers:

- <files/systems/data/services>

It does not cover:

- <explicit exclusions>

## Preconditions

- [ ] current state captured;
- [ ] backup/snapshot/checkpoint exists when needed;
- [ ] owner knows the rollback trigger;
- [ ] no destructive operation runs without explicit approval.

## Rollback Triggers

- failed tests or smoke checks;
- broken service health;
- unexpected privacy/security exposure;
- wrong data copied/imported;
- migration verification mismatch;
- user asks to stop;
- approval boundary crossed.

## Restore Steps

1. <step>
2. <step>
3. <step>

## Verification After Rollback

- [ ] service/status check;
- [ ] tests/smoke check;
- [ ] data count/checksum/health check if relevant;
- [ ] user-facing impact checked;
- [ ] evidence updated.

## Escalation

Stop and ask Stanislav before:

- root-level/system rollback;
- Synology root-level/DSM rollback;
- firewall/VPN/router rollback;
- production access changes;
- data deletion or storage pool changes.

## Result

- <filled after rollback if used>
