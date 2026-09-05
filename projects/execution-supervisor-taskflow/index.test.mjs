import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, realpath, writeFile } from "node:fs/promises";
import os from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import plugin, { requiresManagedExecution } from "./index.js";

assert.equal(requiresManagedExecution("Выполни задачу и сообщи по завершении."), true);
assert.equal(requiresManagedExecution("Запусти контрольный drill"), true);
assert.equal(requiresManagedExecution("Повторно проведи полный контрольный drill Оркестратора"), true);
assert.equal(requiresManagedExecution("Execute this and notify me when done"), true);
assert.equal(requiresManagedExecution("Ответь коротко сейчас"), false);
assert.equal(requiresManagedExecution("Реализуй этот план полностью"), true);
assert.equal(requiresManagedExecution(`Реализуй ${"подробный шаг ".repeat(40)} полностью`), true);
assert.equal(requiresManagedExecution(`Implement ${"a detailed step ".repeat(40)} the entire objective`), true);

const root = await realpath(await mkdtemp(join(os.tmpdir(), "execution-supervisor-plugin-")));
const runtimeRoot = await realpath(await mkdtemp(join(os.tmpdir(), "execution-supervisor-runtime-")));
const projectRoot = fileURLToPath(new URL("../..", import.meta.url));
const taskRoot = join(root, "state", "tasks", "test-run");
await mkdir(taskRoot, { recursive: true });
const evidencePath = join(taskRoot, "EVIDENCE.md");
const statePath = join(taskRoot, "execution-supervisor-state.json");
const outboxPath = join(taskRoot, "outbox.jsonl");
const fakeRunnerPath = join(root, "fake-managed-runner.mjs");
await writeFile(evidencePath, "# Plugin test\n\nStatus: READY\n");
await writeFile(fakeRunnerPath, `import { writeFile } from "node:fs/promises";
import { createPrivateKey, sign } from "node:crypto";
const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, all) => index % 2 ? pairs : [...pairs, [value.replace(/^--/, ""), all[index + 1]]], []));
if (!args.outcome || args.thinking !== "high") process.exit(9);
import { readFileSync } from "node:fs";
const privateKey = createPrivateKey({ key: readFileSync(Number(process.env.MANAGED_TERMINAL_FD)), format: "der", type: "pkcs8" });
const terminalStatus = "SUCCEEDED", contractValidated = true, exitCode = 0;
const runNonce = process.env.MANAGED_RUN_NONCE;
const taskDigest=null, planDigest=null, outcomeDigest=null, finishedAt=null, summary=null, slices=null;
const outcomePath=null,agentOutputPath=null,independentReviewPaths=null;
const terminalSignature = sign(null, Buffer.from(JSON.stringify([terminalStatus, contractValidated, exitCode,runNonce,taskDigest,planDigest,outcomeDigest,finishedAt,summary,slices,outcomePath,agentOutputPath,independentReviewPaths])), privateKey).toString("base64");
await writeFile(args.result, JSON.stringify({ terminalStatus, contractValidated, exitCode,runNonce,taskDigest,planDigest,outcomeDigest,finishedAt,summary,slices,outcomePath,agentOutputPath,independentReviewPaths,terminalSignature }) + "\\n");
`);

const tools = new Map();
const services = [];
const hooks = new Map();
const sends = [];
const records = new Map();
const runtime = {
  createManaged(input) {
    const value = { ...input, flowId: `flow-test-${records.size + 1}`, revision: 1, status: "running", stateJson: input.stateJson };
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
  pluginConfig: { workspaceRoot: root, runtimeRoot,
    supervisorPath: join(projectRoot, "scripts", "execution-supervisor.py"),
    managedRunnerPath: fakeRunnerPath, managedAgentTimeoutSeconds: 300,
    authorizedSenderIds: ["109592643"] },
  config: {},
  runtime: {
    tasks: { flow: { fromToolContext: () => runtime, bindSession: () => runtime } },
    channel: { outbound: { loadAdapter: async () => ({ sendText: async input => { sends.push(input); return { messageId: "test-1" }; } }) } }
  },
  registerTool(factory, options) { tools.set(options.name, factory); },
  on(event, handler) { hooks.set(event, handler); },
  registerService(service) { services.push(service); }
};
plugin.register(api);
const ctx = { senderIsOwner: true, sessionKey: "agent:main:telegram:group:-100:topic:14",
  deliveryContext: { channel: "telegram", accountId: "default", to: "telegram:-100:topic:14", threadId: 14 } };
assert.equal(tools.has("execution_supervisor_start"), false);

assert.equal(typeof hooks.get("before_agent_run"), "function");
assert.equal(typeof hooks.get("before_prompt_build"), "function");
assert.equal(typeof hooks.get("before_tool_call"), "function");
assert.equal(typeof hooks.get("before_dispatch"), "function");
const ingressCtx = { channelId: "telegram", accountId: "default", senderId: "109592643",
  sessionKey: "agent:main:telegram:group:-100:topic:14", conversationId: "-100" };
const ingress = await hooks.get("before_dispatch")({
  content: "Выполни задачу и сообщи по завершении.", channel: "telegram", senderId: "109592643"
}, ingressCtx);
assert.equal(ingress.handled, true);
assert.match(ingress.text, /Managed execution started/);
const duplicateIngress = await hooks.get("before_dispatch")({
  content: "Выполни задачу и сообщи по завершении.", channel: "telegram", senderId: "109592643"
}, ingressCtx);
assert.match(duplicateIngress.text, /already started/);
const ingressAdmissions = await import("node:fs/promises").then(fs => fs.readdir(runtimeRoot));
assert.equal(ingressAdmissions.length, 1);
const ingressRecord = JSON.parse(await readFile(join(runtimeRoot, ingressAdmissions[0], "admission.json"), "utf8"));
assert.equal(ingressRecord.status, "DISPATCHED");
assert.equal(ingressRecord.sessionKey, ingressCtx.sessionKey);
const unauthorizedIngress = await hooks.get("before_dispatch")({
  content: "Выполни задачу и сообщи по завершении.", senderId: "999"
}, { ...ingressCtx, senderId: "999" });
assert.equal(unauthorizedIngress, undefined);
const managedRunId = "managed-run-1";
const managedCtx = { ...ctx, sessionKey: "agent:main:telegram:group:-100:topic:99", runId: managedRunId };
const gateDecision = await hooks.get("before_agent_run")({
  prompt: "Выполни задачу и сообщи по завершении.", senderIsOwner: true,
  messages: [{ role: "user", content: "Предыдущая задача — R7" }]
}, managedCtx);
assert.equal(gateDecision.outcome, "pass");
const promptMutation = hooks.get("before_prompt_build")({}, managedCtx);
assert.match(promptMutation.prependContext, /execution_supervisor_dispatch/);
const blocked = hooks.get("before_tool_call")({ toolName: "bash", params: {} }, { ...managedCtx, toolName: "bash" });
assert.equal(blocked.block, true);
const dispatchAllowed = hooks.get("before_tool_call")({ toolName: "execution_supervisor_dispatch", params: {} },
  { ...managedCtx, toolName: "execution_supervisor_dispatch" });
assert.equal(dispatchAllowed, undefined);
const dispatcher = tools.get("execution_supervisor_dispatch")(managedCtx);
const dispatched = await dispatcher.execute("dispatch-1", {});
assert.equal(dispatched.details.flowId, "flow-test-2");
assert.equal(dispatched.details.admissionId, managedRunId);
const blockedAfterDispatch = hooks.get("before_tool_call")({ toolName: "bash", params: {} }, { ...managedCtx, toolName: "bash" });
assert.equal(blockedAfterDispatch.block, true);
for (let attempt = 0; attempt < 100; attempt++) {
  try {
    const state = JSON.parse(await readFile(dispatched.details.statePath, "utf8"));
    if (state.status === "SUCCEEDED") break;
  } catch {}
  await new Promise(resolve => setTimeout(resolve, 20));
}
const managedTerminal = JSON.parse(await readFile(dispatched.details.statePath, "utf8"));
assert.equal(managedTerminal.status, "SUCCEEDED");
assert.equal(managedTerminal.sessionKey, managedCtx.sessionKey);
assert.equal(sends.length, 0);
assert.equal(hooks.get("before_tool_call")({ toolName: "bash", params: {} },
  { ...managedCtx, toolName: "bash" }), undefined);
const managedContext = JSON.parse(await readFile(join(root, "state", "tasks", "managed-admission", managedRunId, "CONTEXT.json"), "utf8"));
assert.equal(managedContext.messages.length, 1);
assert.equal(hooks.get("before_tool_call")({ toolName: "sessions_spawn", params: {} },
  { ...managedCtx, toolName: "sessions_spawn" }), undefined);
await services[0].start({ config: {}, logger: { error(...args) { console.error(...args); } } });
for (let attempt = 0; attempt < 100; attempt++) {
  const state = JSON.parse(await readFile(dispatched.details.statePath, "utf8"));
  if (state.notificationDelivered) break;
  await new Promise(resolve => setTimeout(resolve, 20));
}
await services[0].stop();
assert.equal(sends.length, 2);
assert.match(sends.at(-1).text, /SUCCEEDED/);
assert.equal(JSON.parse(await readFile(dispatched.details.statePath, "utf8")).status, "SUCCEEDED");
await services[0].start({ config: {}, logger: { error(...args) { console.error(...args); } } });
await new Promise(resolve => setTimeout(resolve, 30));
await services[0].stop();
assert.equal(sends.length, 2);

const privateCtx = { ...ctx, sessionKey: "agent:main:main", runId: "private-managed" };
await hooks.get("before_agent_run")({ prompt: "Выполни отчёт и сообщи по завершении", senderIsOwner: true }, privateCtx);
assert.match(hooks.get("before_prompt_build")({}, privateCtx).prependContext, /private-managed/);

const nestedCtx = { ...ctx, sessionKey: "agent:main:managed:nested", runId: "nested-managed" };
await hooks.get("before_agent_run")({ prompt: "Выполни задачу и сообщи по завершении", senderIsOwner: true }, nestedCtx);
assert.equal(hooks.get("before_prompt_build")({}, nestedCtx), undefined);

const foregroundRun = { ...ctx, runId: "foreground-run" };
await hooks.get("before_agent_run")({ prompt: "Ответь коротко сейчас", senderIsOwner: true }, foregroundRun);
assert.equal(hooks.get("before_prompt_build")({}, foregroundRun), undefined);
assert.equal(hooks.get("before_tool_call")({ toolName: "bash", params: {} }, { ...foregroundRun, toolName: "bash" }), undefined);

assert.equal(tools.has("execution_supervisor_recover"), false);
console.log("TASKFLOW_PLUGIN_INTEGRATION_OK");
