import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { loadRuns, summarize } from "./server.mjs";

test("loads a managed run and derives summary", async t => {
  const root = await mkdtemp(join(tmpdir(), "supervisor-dashboard-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const run = join(root, "managed-admission", "one");
  await mkdir(run, { recursive: true });
  await writeFile(join(run, "admission.json"), JSON.stringify({ prompt: "Проверить", supervisorPid: 42, sessionKey: "agent:main:telegram:group:-1:topic:14" }));
  await writeFile(join(run, "execution-supervisor-state.json"), JSON.stringify({
    runId: "run-1", flowId: "flow-1", status: "SUCCEEDED", pid: 99999999,
    startedAt: "2026-09-02T10:00:00Z", finishedAt: "2026-09-02T10:00:05Z",
    notificationDelivered: true, exitCode: 0
  }));
  const runs = await loadRuns(root);
  assert.equal(runs.length, 1);
  assert.equal(runs[0].route, "Telegram · тема 14");
  assert.equal(runs[0].durationMs, 5000);
  assert.deepEqual(summarize(runs), { total: 1, running: 0, succeeded: 1, attention: 0, deliveryPending: 0, generatedAt: summarize(runs).generatedAt });
});

test("marks orphaned RUNNING process as STALE", async t => {
  const root = await mkdtemp(join(tmpdir(), "supervisor-dashboard-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const run = join(root, "one");
  await mkdir(run);
  await writeFile(join(run, "execution-supervisor-state.json"), JSON.stringify({ status: "RUNNING", pid: 99999999 }));
  const [item] = await loadRuns(root);
  assert.equal(item.status, "STALE");
  assert.equal(item.recordedStatus, "RUNNING");
});
