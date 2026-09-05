#!/usr/bin/env node
import { backup, DatabaseSync } from 'node:sqlite';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const source = path.join(os.homedir(), '.openclaw/state/openclaw.sqlite');
const archiveDir = path.join(os.homedir(), '.openclaw/backups/inbound-timeout-retirement-2026-09-05');
const backupPath = path.join(archiveDir, 'openclaw.sqlite');
const evidencePath = path.join(path.dirname(new URL(import.meta.url).pathname), 'inbound-timeout-retirement.redacted.json');
const expected = 20;

if (fs.existsSync(archiveDir) || fs.existsSync(evidencePath)) {
  throw new Error('refusing to overwrite existing archive artifacts');
}
fs.mkdirSync(archiveDir, { recursive: false, mode: 0o700 });
fs.chmodSync(archiveDir, 0o700);

const db = new DatabaseSync(source);
const where = `status = 'failed' AND failed_reason = 'handler-timeout' AND channel_id = 'telegram'`;
const count = Number(db.prepare(`SELECT count(*) AS n FROM channel_ingress_events WHERE ${where}`).get().n);
const pending = Number(db.prepare("SELECT count(*) AS n FROM channel_ingress_events WHERE status != 'failed'").get().n);
if (count !== expected) throw new Error(`expected ${expected} archived timeout rows, found ${count}`);

const digestRows = db.prepare(`
  SELECT event_id, queue_name, account_id, received_at, failed_at
  FROM channel_ingress_events WHERE ${where} ORDER BY event_id
`).all();
const digest = crypto.createHash('sha256').update(JSON.stringify(digestRows)).digest('hex');

await backup(db, backupPath);
fs.chmodSync(backupPath, 0o600);

db.exec('BEGIN IMMEDIATE');
try {
  const result = db.prepare(`DELETE FROM channel_ingress_events WHERE ${where}`).run();
  if (Number(result.changes) !== expected) throw new Error(`delete count changed: ${result.changes}`);
  db.exec('COMMIT');
} catch (error) {
  db.exec('ROLLBACK');
  throw error;
}

const remaining = Number(db.prepare(`SELECT count(*) AS n FROM channel_ingress_events WHERE ${where}`).get().n);
const integrity = db.prepare('PRAGMA integrity_check').get().integrity_check;
db.close();

const backupDb = new DatabaseSync(backupPath, { readOnly: true });
const backupCount = Number(backupDb.prepare(`SELECT count(*) AS n FROM channel_ingress_events WHERE ${where}`).get().n);
const backupIntegrity = backupDb.prepare('PRAGMA integrity_check').get().integrity_check;
backupDb.close();
if (remaining !== 0 || integrity !== 'ok' || backupCount !== expected || backupIntegrity !== 'ok') {
  throw new Error('post-archive verification failed');
}

const evidence = {
  schema: 'openclaw.inbound-timeout-retirement.redacted.v1',
  archivedAt: new Date().toISOString(),
  predicate: { status: 'failed', failedReason: 'handler-timeout', channelId: 'telegram' },
  counts: { archived: count, remainingMatching: remaining, otherNonFailedBefore: pending, backupMatching: backupCount },
  archivedRecordSetSha256: digest,
  integrity: { sourceAfter: integrity, backup: backupIntegrity },
  replayed: false,
  outboundRowsChanged: false,
};
fs.writeFileSync(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`, { mode: 0o600, flag: 'wx' });
console.log(JSON.stringify(evidence));
