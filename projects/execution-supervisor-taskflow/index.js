import { spawn } from "node:child_process";
import { readFile, readdir, realpath } from "node:fs/promises";
import { resolve } from "node:path";
import { Type } from "typebox";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const DEFAULT_ROOT = "/home/stanislav/.openclaw/workspace/agents/main";
const TERMINAL = new Set(["SUCCEEDED", "TIMED_OUT", "CRASHED", "ESCALATED", "INTERRUPTED", "FAILED"]);

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
