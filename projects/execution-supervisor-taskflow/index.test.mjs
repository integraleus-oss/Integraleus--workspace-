import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, realpath, writeFile } from "node:fs/promises";
import os from "node:os";
import { join } from "node:path";
import plugin from "./index.js";

const root = await realpath(await mkdtemp(join(os.tmpdir(), "execution-supervisor-plugin-")));
const taskRoot = join(root, "state", "tasks", "test-run");
await mkdir(taskRoot, { recursive: true });
const evidencePath = join(taskRoot, "EVIDENCE.md");
const statePath = join(taskRoot, "execution-supervisor-state.json");
const outboxPath = join(taskRoot, "outbox.jsonl");
await writeFile(evidencePath, "# Plugin test\n\nStatus: READY\n");

const tools = new Map();
const services = [];
const sends = [];
const records = new Map();
const runtime = {
  createManaged(input) {
    const value = { ...input, flowId: "flow-test-1", revision: 1, status: "running", stateJson: input.stateJson };
    records.set(value.flowId, value); return value;
  },
  get(id) { return records.get(id); },
  finish(input) {
    const value = { ...records.get(input.flowId), ...input, status: "succeeded", revision: 2 };
    records.set(input.flowId, value); return { applied: true, flow: value };
  },
  fail(input) {
    const value = { ...records.get(input.flowId), ...input, status: "failed", revision: 2 };
    records.set(input.flowId, value); return { applied: true, flow: value };
  }
};
const api = {
  pluginConfig: { workspaceRoot: root,
    supervisorPath: "/home/stanislav/.openclaw/workspace/agents/main/scripts/execution-supervisor.py" },
  config: {},
  runtime: {
    tasks: { flow: { fromToolContext: () => runtime, bindSession: () => runtime } },
    channel: { outbound: { loadAdapter: async () => ({ sendText: async input => { sends.push(input); return { messageId: "test-1" }; } }) } }
  },
  registerTool(factory, options) { tools.set(options.name, factory); },
  registerService(service) { services.push(service); }
};
plugin.register(api);
const ctx = { senderIsOwner: true, sessionKey: "agent:main:telegram:group:-100:topic:14",
  deliveryContext: { channel: "telegram", accountId: "default", to: "telegram:-100:topic:14", threadId: 14 } };
const start = tools.get("execution_supervisor_start")(ctx);
const started = await start.execute("call-1", { evidencePath, statePath, outboxPath,
  timeoutSeconds: 3, command: ["python3", "-c", "pass"], goal: "plugin integration test" });
assert.equal(started.details.flowId, "flow-test-1");

for (let attempt = 0; attempt < 100; attempt++) {
  try { const state = JSON.parse(await readFile(statePath, "utf8")); if (state.status === "SUCCEEDED") break; }
  catch {}
  await new Promise(resolve => setTimeout(resolve, 20));
}
const terminal = JSON.parse(await readFile(statePath, "utf8"));
assert.equal(terminal.status, "SUCCEEDED");
assert.equal(terminal.flowId, "flow-test-1");
assert.equal(terminal.sessionKey, ctx.sessionKey);
assert.deepEqual(terminal.deliveryContext, ctx.deliveryContext);
assert.equal((await readFile(outboxPath, "utf8")).trim().split("\n").length, 1);

await services[0].start({ config: {}, logger: { error() {} } });
for (let attempt = 0; attempt < 100; attempt++) {
  const state = JSON.parse(await readFile(statePath, "utf8"));
  if (state.notificationDelivered) break;
  await new Promise(resolve => setTimeout(resolve, 20));
}
await services[0].stop();
const delivered = JSON.parse(await readFile(statePath, "utf8"));
assert.equal(delivered.notificationDelivered, true);
assert.equal(sends.length, 1);
assert.equal(sends[0].to, "-100");
assert.equal(sends[0].threadId, "14");
assert.equal(records.get("flow-test-1").status, "succeeded");

const prefixCtx = { ...ctx, senderIsOwner: false };
const prefixStart = tools.get("execution_supervisor_start")(prefixCtx);
await assert.rejects(
  prefixStart.execute("call-2", { evidencePath: "/outside/EVIDENCE.md", statePath, outboxPath,
    timeoutSeconds: 3, command: ["python3", "-c", "pass"], goal: "prefix admission test" }),
  /path outside workspace root/
);
console.log("TASKFLOW_PLUGIN_INTEGRATION_OK");
