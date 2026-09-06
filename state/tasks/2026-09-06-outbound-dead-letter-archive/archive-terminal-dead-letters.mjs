#!/usr/bin/env node
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { backup, DatabaseSync } from 'node:sqlite';

const sourcePath = '/home/stanislav/.openclaw/state/openclaw.sqlite';
const archiveDir = '/home/stanislav/.openclaw/backups/outbound-dead-letter-archive-2026-09-06';
const backupPath = path.join(archiveDir, 'openclaw.sqlite');
const exportPath = path.join(archiveDir, 'delivery-dead-letters.redacted.json');
const evidencePath = path.join(import.meta.dirname, 'archive-result.json');
const terminalWhere = "status = 'failed' AND recovery_state = 'completed_permanent' AND platform_send_started_at IS NULL";

function sha256(value) {
  return createHash('sha256').update(String(value)).digest('hex');
}

function fileSha256(file) {
  return sha256(fs.readFileSync(file));
}

function reasonCategory(error) {
  const value = String(error ?? '').toLowerCase();
  if (!value) return 'none';
  if (value.includes('timeout') || value.includes('timed out')) return 'timeout';
  if (value.includes('network') || value.includes('econn') || value.includes('fetch')) return 'network';
  if (value.includes('media') || value.includes('attachment') || value.includes('file')) return 'media';
  if (value.includes('permission') || value.includes('denied')) return 'permission';
  return 'other';
}

if (fs.existsSync(archiveDir) || fs.existsSync(evidencePath)) {
  throw new Error(`refusing to overwrite existing archive artifact: ${fs.existsSync(archiveDir) ? archiveDir : evidencePath}`);
}

fs.mkdirSync(archiveDir, { mode: 0o700 });
fs.chmodSync(archiveDir, 0o700);

const sourceRead = new DatabaseSync(sourcePath, { readOnly: true });
const sourceIntegrityBefore = sourceRead.prepare('PRAGMA integrity_check').get().integrity_check;
const scopeRowsBefore = sourceRead.prepare(`SELECT queue_name, id, status, recovery_state, entry_kind, channel, retry_count, last_attempt_at, failed_at, enqueued_at, updated_at, platform_send_started_at, last_error, session_key, target, account_id, entry_json FROM delivery_queue_entries WHERE ${terminalWhere} ORDER BY queue_name, id`).all();
const sourceCountsBefore = sourceRead.prepare('SELECT status, COUNT(*) AS count FROM delivery_queue_entries GROUP BY status ORDER BY status').all();
sourceRead.close();

if (sourceIntegrityBefore !== 'ok') throw new Error(`source integrity failed before backup: ${sourceIntegrityBefore}`);
if (scopeRowsBefore.length !== 115) throw new Error(`expected 115 terminal dead letters, found ${scopeRowsBefore.length}`);
if (scopeRowsBefore.some((row) => row.status !== 'failed' || row.recovery_state !== 'completed_permanent' || row.platform_send_started_at !== null || row.failed_at === null)) {
  throw new Error('archive scope contains a non-terminal or platform-send-started row');
}

const sourceForBackup = new DatabaseSync(sourcePath, { readOnly: true });
await backup(sourceForBackup, backupPath);
sourceForBackup.close();
fs.chmodSync(backupPath, 0o600);

const backupDb = new DatabaseSync(backupPath, { readOnly: true });
const backupIntegrity = backupDb.prepare('PRAGMA integrity_check').get().integrity_check;
const backupRows = backupDb.prepare(`SELECT queue_name, id, status, recovery_state, entry_kind, channel, retry_count, last_attempt_at, failed_at, enqueued_at, updated_at, platform_send_started_at, last_error, session_key, target, account_id, entry_json FROM delivery_queue_entries WHERE ${terminalWhere} ORDER BY queue_name, id`).all();
backupDb.close();
if (backupIntegrity !== 'ok') throw new Error(`backup integrity failed: ${backupIntegrity}`);
if (backupRows.length !== scopeRowsBefore.length) throw new Error(`backup scope count mismatch: ${backupRows.length} vs ${scopeRowsBefore.length}`);

const redacted = {
  schema: 'openclaw.delivery-dead-letter-redacted.v1',
  createdAt: new Date().toISOString(),
  sourcePathSha256: sha256(sourcePath),
  terminalPredicate: {
    status: 'failed',
    recoveryState: 'completed_permanent',
    platformSendStarted: false,
  },
  count: backupRows.length,
  records: backupRows.map((row) => ({
    queueNameSha256: sha256(row.queue_name),
    idSha256: sha256(row.id),
    status: row.status,
    recoveryState: row.recovery_state,
    entryKind: row.entry_kind,
    channel: row.channel,
    retryCount: row.retry_count,
    lastAttemptAt: row.last_attempt_at,
    failedAt: row.failed_at,
    enqueuedAt: row.enqueued_at,
    updatedAt: row.updated_at,
    reasonCategory: reasonCategory(row.last_error),
    hasSessionKey: row.session_key !== null,
    hasTarget: row.target !== null,
    hasAccountId: row.account_id !== null,
    hasEntryPayload: Boolean(row.entry_json),
  })),
};
fs.writeFileSync(exportPath, `${JSON.stringify(redacted, null, 2)}\n`, { mode: 0o600, flag: 'wx' });
fs.chmodSync(exportPath, 0o600);

const sourceWrite = new DatabaseSync(sourcePath);
sourceWrite.exec('BEGIN IMMEDIATE');
let deleted = 0;
try {
  const remove = sourceWrite.prepare(`DELETE FROM delivery_queue_entries WHERE queue_name = ? AND id = ? AND ${terminalWhere}`);
  for (const row of backupRows) deleted += Number(remove.run(row.queue_name, row.id).changes);
  if (deleted !== backupRows.length) throw new Error(`concurrent change detected: deleted ${deleted} of ${backupRows.length}`);
  sourceWrite.exec('COMMIT');
} catch (error) {
  sourceWrite.exec('ROLLBACK');
  sourceWrite.close();
  throw error;
}

const sourceIntegrityAfter = sourceWrite.prepare('PRAGMA integrity_check').get().integrity_check;
const terminalAfter = sourceWrite.prepare(`SELECT COUNT(*) AS count FROM delivery_queue_entries WHERE ${terminalWhere}`).get().count;
const failedAfter = sourceWrite.prepare("SELECT COUNT(*) AS count FROM delivery_queue_entries WHERE status = 'failed'").get().count;
const pendingAfter = sourceWrite.prepare("SELECT COUNT(*) AS count FROM delivery_queue_entries WHERE status = 'pending'").get().count;
const sourceCountsAfter = sourceWrite.prepare('SELECT status, COUNT(*) AS count FROM delivery_queue_entries GROUP BY status ORDER BY status').all();
sourceWrite.close();

if (sourceIntegrityAfter !== 'ok') throw new Error(`source integrity failed after archive: ${sourceIntegrityAfter}`);
if (terminalAfter !== 0 || failedAfter !== 0) throw new Error(`dead-letter count is not zero after archive: terminal=${terminalAfter}, failed=${failedAfter}`);

const result = {
  schema: 'openclaw.delivery-dead-letter-archive-result.v1',
  completedAt: new Date().toISOString(),
  sourcePath,
  archiveDir,
  sourceIntegrityBefore,
  backupIntegrity,
  sourceIntegrityAfter,
  sourceCountsBefore,
  sourceCountsAfter,
  archivedCount: backupRows.length,
  deletedCount: deleted,
  terminalAfter,
  failedAfter,
  pendingAfter,
  backupMode: (fs.statSync(backupPath).mode & 0o777).toString(8).padStart(4, '0'),
  exportMode: (fs.statSync(exportPath).mode & 0o777).toString(8).padStart(4, '0'),
  directoryMode: (fs.statSync(archiveDir).mode & 0o777).toString(8).padStart(4, '0'),
  backupSha256: fileSha256(backupPath),
  exportSha256: fileSha256(exportPath),
  replayPerformed: false,
};
fs.writeFileSync(evidencePath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600, flag: 'wx' });
console.log(JSON.stringify(result, null, 2));
