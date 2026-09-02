import { spawn } from "node:child_process";
import { mkdir, readFile, readdir, realpath, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { randomUUID } from "node:crypto";
import { Type } from "typebox";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const DEFAULT_ROOT = "/home/stanislav/.openclaw/workspace/agents/main";
const TERMINAL = new Set(["SUCCEEDED", "TIMED_OUT", "CRASHED", "ESCALATED", "INTERRUPTED", "FAILED"]);
const DEFAULT_MANAGED_PATTERNS = [
  /выполни[\s\S]{0,160}сообщи\s+по\s+завершении/iu,
  /сообщи\s+по\s+завершении/iu,
  /(?:run|execute|complete)[\s\S]{0,160}(?:notify|tell)\s+me\s+(?:when|once)\s+(?:done|complete)/iu,
];
const SAFE_PRE_DISPATCH_TOOLS = new Set(["execution_supervisor_dispatch", "execution_supervisor_recover"]);

export function requiresManagedExecution(prompt, patterns = DEFAULT_MANAGED_PATTERNS) {
  return typeof prompt === "string" && patterns.some(pattern => pattern.test(prompt));
}

function admissionId(runId) {
  return String(runId || randomUUID()).replace(/[^a-zA-Z0-9_-]/g, "-");
}

function taskMarkdown(record) {
  return `# Managed task\n\n- Admission ID: \`${record.admissionId}\`\n- Owner: main\n- Session: \`${record.sessionKey}\`\n- Created: ${record.createdAt}\n- Trigger: explicit completion notification\n- Expected output: completed task plus durable result/evidence\n- Timeout: ${record.timeoutSeconds}s\n\n## Request\n\n${record.prompt}\n\n## Context\n\nRecent source-session context is stored in \`${record.contextPath}\`. Use it only to resolve the request; the task packet and current owner request remain authoritative.\n\n## Checklist\n\n- [x] Admission recorded before work\n- [ ] Managed flow created\n- [ ] Runner terminal evidence recorded\n- [ ] Exactly-once notification delivered\n`;
}

function evidenceMarkdown(record) {
  return `# Managed execution evidence\n\nStatus: ADMITTED\n\n- Admission ID: \`${record.admissionId}\`\n- Session: \`${record.sessionKey}\`\n- Created: ${record.createdAt}\n- Execution mechanism: pending owner-bound TaskFlow dispatch\n- Expected output: \`${record.resultPath}\`\n`;
}

function isTrustedOwnerContext(ctx, config) {
  if (ctx.senderIsOwner === true || config.authorizedSessionKeys?.includes(ctx.sessionKey) === true) return true;
  const prefixes = config.authorizedSessionPrefixes ?? ["agent:main:telegram:"];
  return ctx.sessionKey === "agent:main:main"
    || (typeof ctx.sessionKey === "string" && prefixes.some(prefix => ctx.sessionKey.startsWith(prefix)));
}

async function safePath(root, requested) {
  const canonicalRoot = await realpath(root);
  const target = resolve(requested);
  if (!target.startsWith(`${canonicalRoot}/`)) throw new Error("path outside workspace root");
  return target;
}

async function readState(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

async function findStateFiles(root) {
  const found = [];
  async function visit(dir) {
    let entries;
    try { entries = await readdir(dir, { withFileTypes: true }); }
    catch { return; }
    for (const entry of entries) {
      const path = resolve(dir, entry.name);
      if (entry.isDirectory()) await visit(path);
      else if (entry.isFile() && entry.name === "execution-supervisor-state.json") found.push(path);
    }
  }
  await visit(root);
  return found.sort();
}

function adapterTarget(delivery) {
  let to = delivery?.to;
  if (delivery?.channel === "telegram" && typeof to === "string") {
    to = to.replace(/^telegram:/, "").replace(/:topic:\d+$/, "");
  }
  return { channel: delivery?.channel, accountId: delivery?.accountId, to,
    threadId: delivery?.threadId == null ? undefined : String(delivery.threadId) };
}

const plugin = definePluginEntry({
  id: "execution-supervisor-taskflow",
  name: "Execution Supervisor TaskFlow",
  description: "Durable TaskFlow bridge for the execution-truth supervisor.",
  register(api) {
    const config = api.pluginConfig ?? {};
    const workspaceRoot = config.workspaceRoot ?? DEFAULT_ROOT;
    const supervisor = config.supervisorPath ?? resolve(workspaceRoot, "scripts/execution-supervisor.py");
    const activeRecoveries = new Set();
    const admissionsByRun = new Map();
    const admissionsBySession = new Map();

    function admissionForContext(ctx) {
      if (ctx.runId) return admissionsByRun.get(ctx.runId);
      return admissionsBySession.get(ctx.sessionKey);
    }

    async function createAdmission(event, ctx) {
      if (!requiresManagedExecution(event.prompt)) return null;
      if (typeof ctx.sessionKey === "string" && ctx.sessionKey.startsWith("agent:main:managed:")) return null;
      const id = admissionId(ctx.runId);
      const taskRoot = resolve(workspaceRoot, "state/tasks/managed-admission", id);
      const record = {
        schemaVersion: 1, admissionId: id, status: "ADMITTED", prompt: event.prompt,
        runId: ctx.runId ?? null, sessionKey: ctx.sessionKey ?? null,
        createdAt: new Date().toISOString(), timeoutSeconds: config.managedAgentTimeoutSeconds ?? 3600,
        taskRoot, taskPath: resolve(taskRoot, "TASK_PACKET.md"),
        contextPath: resolve(taskRoot, "CONTEXT.json"),
        evidencePath: resolve(taskRoot, "EVIDENCE.md"),
        statePath: resolve(taskRoot, "execution-supervisor-state.json"),
        outboxPath: resolve(taskRoot, "outbox.jsonl"),
        resultPath: resolve(taskRoot, "RESULT.json"),
        runnerOutputPath: resolve(taskRoot, "agent-result.json"),
      };
      await mkdir(taskRoot, { recursive: true });
      const recentMessages = Array.isArray(event.messages) ? event.messages.slice(-40) : [];
      await writeFile(record.contextPath, JSON.stringify({ sessionKey: record.sessionKey,
        capturedAt: record.createdAt, messages: recentMessages }, null, 2) + "\n", { flag: "wx" }).catch(error => {
        if (error?.code !== "EEXIST") throw error;
      });
      await writeFile(record.taskPath, taskMarkdown(record), { flag: "wx" }).catch(error => {
        if (error?.code !== "EEXIST") throw error;
      });
      await writeFile(record.evidencePath, evidenceMarkdown(record), { flag: "wx" }).catch(error => {
        if (error?.code !== "EEXIST") throw error;
      });
      await writeFile(resolve(taskRoot, "admission.json"), JSON.stringify(record, null, 2) + "\n");
      if (ctx.runId) admissionsByRun.set(ctx.runId, record);
      if (ctx.sessionKey) admissionsBySession.set(ctx.sessionKey, record);
      return record;
    }

    api.registerHook("before_agent_run", async (event, ctx) => {
      if (!isTrustedOwnerContext({ ...ctx, senderIsOwner: event.senderIsOwner }, config)) return;
      await createAdmission(event, ctx);
      return { outcome: "pass" };
    }, { name: "execution-supervisor-managed-admission", description: "Admit explicit completion-notification requests before agent work." });

    api.registerHook("before_agent_start", (_event, ctx) => {
      const admission = admissionForContext(ctx);
      if (!admission) return;
      return { prependContext: `MANAGED EXECUTION REQUIRED (admission ${admission.admissionId}). Before any task work, call execution_supervisor_dispatch with no arguments. Do not use bash, exec, apply_patch, Codex, subagents, or other work tools in this turn. After dispatch, report the returned flow/run/PID/evidence identifiers and stop.` };
    }, { name: "execution-supervisor-managed-prompt", description: "Force the managed dispatcher to be the first work action." });

    api.registerHook("before_tool_call", (event, ctx) => {
      const admission = admissionForContext(ctx);
      if (!admission || SAFE_PRE_DISPATCH_TOOLS.has(event.toolName)) return;
      return { block: true, blockReason: admission.status === "DISPATCHED"
        ? `Managed task ${admission.admissionId} is already detached; foreground work is blocked.`
        : `Managed admission ${admission.admissionId} requires execution_supervisor_dispatch before any work tool.` };
    }, { name: "execution-supervisor-managed-tool-gate", description: "Fail closed until managed dispatch and prevent duplicate foreground work." });

    async function reconcileState(statePath, runtimeConfig) {
      if (activeRecoveries.has(statePath)) return { skipped: "already-running" };
      activeRecoveries.add(statePath);
      try {
        const child = spawn("python3", [supervisor, "recover", "--state", statePath], { stdio: "ignore" });
        await new Promise((ok, fail) => { child.on("exit", code => code === 0 ? ok() : fail(new Error(`recovery exit ${code}`))); child.on("error", fail); });
        let state = await readState(statePath);
        if (TERMINAL.has(state.status) && !state.notificationDelivered) {
          const delivery = adapterTarget(state.deliveryContext);
          if (!delivery.channel || !delivery.to) throw new Error(`missing originating delivery context: ${statePath}`);
          const adapter = await api.runtime.channel.outbound.loadAdapter(delivery.channel);
          if (!adapter?.sendText) throw new Error(`outbound adapter unavailable: ${delivery.channel}`);
          const sent = await adapter.sendText({ cfg: runtimeConfig ?? api.config,
            accountId: delivery.accountId, to: delivery.to, threadId: delivery.threadId,
            text: `Execution supervisor: ${state.status}. Flow ${state.flowId}; run ${state.runId}; exit code ${state.exitCode ?? "n/a"}.`,
            deliveryQueueId: state.notificationId });
          const ack = spawn("python3", [supervisor, "ack", "--state", statePath,
            "--notification-id", state.notificationId], { stdio: "ignore" });
          await new Promise((ok, fail) => { ack.on("exit", code => code === 0 ? ok() : fail(new Error(`ack exit ${code}`))); ack.on("error", fail); });
          state = { ...await readState(statePath), delivery: sent };
        }
        if (!state.sessionKey || !state.flowId) return { state, mutation: null };
        const runtime = api.runtime.tasks.flow.bindSession({ sessionKey: state.sessionKey,
          requesterOrigin: state.deliveryContext });
        const record = runtime.get(state.flowId);
        if (!record) return { state, mutation: null };
        let mutation = null;
        if (TERMINAL.has(state.status) && !["succeeded", "failed", "cancelled"].includes(record.status)) {
          mutation = state.status === "SUCCEEDED"
            ? runtime.finish({ flowId: record.flowId, expectedRevision: record.revision, stateJson: { supervisor: state }, endedAt: Date.now() })
            : runtime.fail({ flowId: record.flowId, expectedRevision: record.revision, stateJson: { supervisor: state }, blockedSummary: `execution supervisor: ${state.status}`, endedAt: Date.now() });
        }
        return { state, mutation };
      } finally { activeRecoveries.delete(statePath); }
    }

    let recoveryTimer = null;
    api.registerService({
      id: "execution-supervisor-recovery",
      start: async (serviceCtx) => {
        const tick = async () => {
          for (const statePath of await findStateFiles(resolve(workspaceRoot, "state/tasks"))) {
            const state = await readState(statePath).catch(() => null);
            if (!state || (state.notificationDelivered && TERMINAL.has(state.status))) continue;
            await reconcileState(statePath, serviceCtx.config).catch(error =>
              serviceCtx.logger.error(`execution supervisor recovery failed (${statePath}): ${String(error)}`));
          }
        };
        await tick();
        recoveryTimer = setInterval(() => { tick().catch(() => {}); }, config.pollMs ?? 5000);
        recoveryTimer.unref?.();
      },
      stop: async () => { if (recoveryTimer) clearInterval(recoveryTimer); recoveryTimer = null; }
    });

    api.registerTool((ctx) => ({
      name: "execution_supervisor_dispatch",
      label: "Dispatch admitted managed execution",
      description: "Dispatch the current admitted request through an owner-bound TaskFlow and detached agent runner.",
      parameters: Type.Object({}, { additionalProperties: false }),
      execute: async () => {
        if (!isTrustedOwnerContext(ctx, config)) throw new Error("trusted owner required");
        const admission = admissionForContext(ctx);
        if (!admission) throw new Error("no managed admission for this turn");
        if (admission.status === "DISPATCHED") throw new Error(`admission already dispatched: ${admission.admissionId}`);
        const runtime = api.runtime.tasks.flow.fromToolContext(ctx);
        const flow = runtime.createManaged({ controllerId: "execution-supervisor-taskflow/v2", goal: admission.prompt,
          status: "running", notifyPolicy: "state_changes", currentStep: "managed-agent-runner",
          stateJson: { admissionId: admission.admissionId, evidencePath: admission.evidencePath,
            statePath: admission.statePath, outboxPath: admission.outboxPath } });
        const runner = config.managedRunnerPath ?? resolve(workspaceRoot, "scripts/managed-agent-runner.mjs");
        const managedSession = `agent:main:managed:${admission.admissionId}`;
        const argv = [supervisor, "run", "--evidence", admission.evidencePath, "--state", admission.statePath,
          "--outbox", admission.outboxPath, "--terminal-evidence", admission.resultPath,
          "--timeout", String(admission.timeoutSeconds), "--owner", "main", "--flow-id", flow.flowId,
          "--session-key", ctx.sessionKey, "--delivery-json", JSON.stringify(ctx.deliveryContext ?? {}), "--",
          process.execPath, runner, "--prompt", admission.taskPath, "--result", admission.resultPath,
          "--agent-output", admission.runnerOutputPath, "--session-key", managedSession,
          "--timeout", String(admission.timeoutSeconds)];
        const child = spawn("python3", argv, { detached: true, stdio: "ignore" }); child.unref();
        admission.status = "DISPATCHED";
        admission.flowId = flow.flowId;
        admission.supervisorPid = child.pid;
        admissionsByRun.set(ctx.runId, admission);
        admissionsBySession.set(ctx.sessionKey, admission);
        await writeFile(resolve(admission.taskRoot, "admission.json"), JSON.stringify(admission, null, 2) + "\n");
        return { content: [{ type: "text", text: JSON.stringify({ admissionId: admission.admissionId,
          flowId: flow.flowId, revision: flow.revision, supervisorPid: child.pid,
          evidencePath: admission.evidencePath, statePath: admission.statePath }) }],
          details: { admissionId: admission.admissionId, flowId: flow.flowId, revision: flow.revision,
            supervisorPid: child.pid, evidencePath: admission.evidencePath, statePath: admission.statePath } };
      }
    }), { name: "execution_supervisor_dispatch" });

    api.registerTool((ctx) => ({
      name: "execution_supervisor_start",
      label: "Start supervised execution",
      description: "Create a managed TaskFlow and launch one owner-scoped durable supervisor.",
      parameters: Type.Object({
        evidencePath: Type.String(), statePath: Type.String(), outboxPath: Type.String(),
        terminalEvidencePath: Type.Optional(Type.String()), timeoutSeconds: Type.Number({ minimum: 1 }),
        command: Type.Array(Type.String(), { minItems: 1 }), goal: Type.String()
      }, { additionalProperties: false }),
      execute: async (_id, raw) => {
        if (!isTrustedOwnerContext(ctx, config)) throw new Error("trusted owner required");
        if (!ctx.sessionKey) throw new Error("bound owner session required");
        const p = raw;
        const evidencePath = await safePath(workspaceRoot, p.evidencePath);
        const statePath = await safePath(workspaceRoot, p.statePath);
        const outboxPath = await safePath(workspaceRoot, p.outboxPath);
        const terminalPath = p.terminalEvidencePath ? await safePath(workspaceRoot, p.terminalEvidencePath) : null;
        const runtime = api.runtime.tasks.flow.fromToolContext(ctx);
        const flow = runtime.createManaged({ controllerId: "execution-supervisor-taskflow/v1", goal: p.goal,
          status: "running", notifyPolicy: "state_changes", currentStep: "supervise",
          stateJson: { evidencePath, statePath, outboxPath } });
        const argv = [supervisor, "run", "--evidence", evidencePath, "--state", statePath,
          "--outbox", outboxPath, "--timeout", String(p.timeoutSeconds), "--owner", "main",
          "--flow-id", flow.flowId, "--session-key", ctx.sessionKey,
          "--delivery-json", JSON.stringify(ctx.deliveryContext ?? {})];
        if (terminalPath) argv.push("--terminal-evidence", terminalPath);
        argv.push("--", ...p.command);
        const child = spawn("python3", argv, { detached: true, stdio: "ignore" }); child.unref();
        return { content: [{ type: "text", text: JSON.stringify({ flowId: flow.flowId,
          revision: flow.revision, supervisorPid: child.pid, statePath }) }],
          details: { flowId: flow.flowId, revision: flow.revision, supervisorPid: child.pid, statePath } };
      }
    }), { name: "execution_supervisor_start" });

    api.registerTool((ctx) => ({
      name: "execution_supervisor_recover",
      label: "Recover supervised execution",
      description: "Reconcile persisted supervisor state into its managed TaskFlow after interruption or restart.",
      parameters: Type.Object({ statePath: Type.String() }, { additionalProperties: false }),
      execute: async (_id, raw) => {
        if (!isTrustedOwnerContext(ctx, config)) throw new Error("trusted owner required");
        if (!ctx.sessionKey) throw new Error("bound owner session required");
        const statePath = await safePath(workspaceRoot, raw.statePath);
        const result = await reconcileState(statePath,
          ctx.getRuntimeConfig?.() ?? ctx.runtimeConfig ?? ctx.config ?? api.config);
        return { content: [{ type: "text", text: JSON.stringify(result) }], details: result };
      }
    }), { name: "execution_supervisor_recover" });
  }
});

export default plugin;
