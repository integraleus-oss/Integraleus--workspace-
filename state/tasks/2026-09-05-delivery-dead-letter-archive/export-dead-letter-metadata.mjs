#!/usr/bin/env node
import { backup, DatabaseSync } from 'node:sqlite';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const taskDir = path.dirname(new URL(import.meta.url).pathname);
const source = path.join(os.homedir(), '.openclaw/state/openclaw.sqlite');
const backupDir = path.join(os.homedir(), '.openclaw/backups/delivery-dead-letter-2026-09-05');
const backupPath = path.join(backupDir, 'openclaw.sqlite');
const exportPath = path.join(taskDir, 'dead-letter-metadata.redacted.json');

fs.mkdirSync(backupDir, { recursive: true, mode: 0o700 });
fs.chmodSync(backupDir, 0o700);
if (fs.existsSync(backupPath)) throw new Error(`refusing to overwrite existing backup: ${backupPath}`);

const db = new DatabaseSync(source, { readOnly: true });
const hash = (value) => crypto.createHash('sha256').update(String(value)).digest('hex');
const toIso = (value) => typeof value === 'number' ? new Date(value).toISOString() : null;

const outbound = db.prepare(`
  SELECT id, status, entry_kind, retry_count, recovery_state,
         enqueued_at, updated_at, failed_at,
         channel IS NOT NULL AS had_channel,
         target IS NOT NULL AS had_target,
         account_id IS NOT NULL AS had_account,
         last_error IS NOT NULL AS had_last_error,
         entry_json
  FROM delivery_queue_entries
  WHERE status = 'failed'
  ORDER BY enqueued_at, id
`).all().map((row) => ({
  idSha256: hash(row.id),
  status: row.status,
  entryKind: row.entry_kind,
  retryCount: row.retry_count,
  recoveryState: row.recovery_state,
  enqueuedAt: toIso(row.enqueued_at),
  updatedAt: toIso(row.updated_at),
  failedAt: toIso(row.failed_at),
  hadChannel: Boolean(row.had_channel),
  hadTarget: Boolean(row.had_target),
  hadAccount: Boolean(row.had_account),
  hadLastError: Boolean(row.had_last_error),
  entryJsonSha256: hash(row.entry_json),
}));

const inbound = db.prepare(`
  SELECT event_id, queue_name, channel_id, account_id, status, attempts,
         received_at, updated_at, last_attempt_at, failed_reason, failed_at,
         lane_key, payload_json, metadata_json
  FROM channel_ingress_events
  WHERE status = 'failed'
  ORDER BY received_at, event_id
`).all().map((row) => ({
  eventIdSha256: hash(row.event_id),
  queueNameSha256: hash(row.queue_name),
  channelId: row.channel_id,
  accountId: row.account_id,
  status: row.status,
  attempts: row.attempts,
  receivedAt: toIso(row.received_at),
  updatedAt: toIso(row.updated_at),
  lastAttemptAt: toIso(row.last_attempt_at),
  failedReason: row.failed_reason,
  failedAt: toIso(row.failed_at),
  laneKeySha256: row.lane_key == null ? null : hash(row.lane_key),
  payloadSha256: hash(row.payload_json),
  metadataSha256: row.metadata_json == null ? null : hash(row.metadata_json),
}));

await backup(db, backupPath);
db.close();
fs.chmodSync(backupPath, 0o600);

const exported = {
  schema: 'openclaw.delivery-dead-letter.redacted.v1',
  exportedAt: new Date().toISOString(),
  sourcePath: source,
  redaction: 'No payloads, message text, targets, raw IDs, lane keys, or errors are included.',
  counts: { outbound: outbound.length, inbound: inbound.length },
  outbound,
  inbound,
};
fs.writeFileSync(exportPath, `${JSON.stringify(exported, null, 2)}\n`, { mode: 0o600, flag: 'wx' });
console.log(JSON.stringify({ backupPath, exportPath, counts: exported.counts }));
