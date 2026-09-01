import assert from "node:assert/strict";
import { mkdtemp, readFile, realpath, writeFile } from "node:fs/promises";
import os from "node:os";
import { join } from "node:path";
import plugin from "./index.js";

const root = await realpath(await mkdtemp(join(os.tmpdir(), "execution-supervisor-plugin-")));
const evidencePath = join(root, "EVIDENCE.md");
const statePath = join(root, "execution-supervisor-state.json");
const outboxPath = join(root, "outbox.jsonl");
await writeFile(evidencePath, "# Plugin test\n\nStatus: READY\n");

const tools = new Map();
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
  runtime: { tasks: { flow: { fromToolContext: () => runtime } } },
  registerTool(factory, options) { tools.set(options.name, factory); }
};
plugin.register(api);
const ctx = { senderIsOwner: true, sessionKey: "agent:main:test", deliveryContext: {} };
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
assert.equal(terminal.sessionKey, "agent:main:test");
assert.equal((await readFile(outboxPath, "utf8")).trim().split("\n").length, 1);

const recover = tools.get("execution_supervisor_recover")(ctx);
const recovered = await recover.execute("call-2", { statePath });
assert.equal(recovered.details.mutation.applied, true);
assert.equal(records.get("flow-test-1").status, "succeeded");
console.log("TASKFLOW_PLUGIN_INTEGRATION_OK");
