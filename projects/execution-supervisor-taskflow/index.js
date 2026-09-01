import { spawn } from "node:child_process";
import { readFile, realpath } from "node:fs/promises";
import { resolve } from "node:path";
import { Type } from "typebox";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const DEFAULT_ROOT = "/home/stanislav/.openclaw/workspace/agents/main";
const TERMINAL = new Set(["SUCCEEDED", "TIMED_OUT", "CRASHED", "ESCALATED", "INTERRUPTED", "FAILED"]);

function isTrustedOwnerContext(ctx, config) {
  return ctx.senderIsOwner === true || config.authorizedSessionKeys?.includes(ctx.sessionKey) === true;
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

const plugin = definePluginEntry({
  id: "execution-supervisor-taskflow",
  name: "Execution Supervisor TaskFlow",
  description: "Durable TaskFlow bridge for the execution-truth supervisor.",
  register(api) {
    const config = api.pluginConfig ?? {};
    const workspaceRoot = config.workspaceRoot ?? DEFAULT_ROOT;
    const supervisor = config.supervisorPath ?? resolve(workspaceRoot, "scripts/execution-supervisor.py");

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
          "--flow-id", flow.flowId, "--session-key", ctx.sessionKey];
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
        const child = spawn("python3", [supervisor, "recover", "--state", statePath], { stdio: "ignore" });
        await new Promise((ok, fail) => { child.on("exit", code => code === 0 ? ok() : fail(new Error(`recovery exit ${code}`))); child.on("error", fail); });
        let state = await readState(statePath);
        if (TERMINAL.has(state.status) && !state.notificationDelivered && config.delivery) {
          const adapter = await api.runtime.channel.outbound.loadAdapter(config.delivery.channel);
          if (!adapter?.sendText) throw new Error(`outbound adapter unavailable: ${config.delivery.channel}`);
          const delivery = await adapter.sendText({
            cfg: ctx.getRuntimeConfig?.() ?? ctx.runtimeConfig ?? ctx.config ?? api.config,
            accountId: config.delivery.accountId,
            to: config.delivery.to,
            threadId: config.delivery.threadId,
            text: `Execution supervisor: ${state.status}. Flow ${state.flowId}; run ${state.runId}; exit code ${state.exitCode ?? "n/a"}.`,
            deliveryQueueId: state.notificationId
          });
          const ack = spawn("python3", [supervisor, "ack", "--state", statePath,
            "--notification-id", state.notificationId], { stdio: "ignore" });
          await new Promise((ok, fail) => { ack.on("exit", code => code === 0 ? ok() : fail(new Error(`ack exit ${code}`))); ack.on("error", fail); });
          state = { ...await readState(statePath), delivery };
        }
        const runtime = api.runtime.tasks.flow.fromToolContext(ctx);
        const record = runtime.get(state.flowId);
        if (!record) throw new Error("managed flow not found in owner session");
        let mutation = null;
        if (TERMINAL.has(state.status) && !["succeeded", "failed", "cancelled"].includes(record.status)) {
          mutation = state.status === "SUCCEEDED"
            ? runtime.finish({ flowId: record.flowId, expectedRevision: record.revision, stateJson: { supervisor: state }, endedAt: Date.now() })
            : runtime.fail({ flowId: record.flowId, expectedRevision: record.revision, stateJson: { supervisor: state }, blockedSummary: `execution supervisor: ${state.status}`, endedAt: Date.now() });
        }
        return { content: [{ type: "text", text: JSON.stringify({ state, mutation }) }], details: { state, mutation } };
      }
    }), { name: "execution_supervisor_recover" });
  }
});

export default plugin;
