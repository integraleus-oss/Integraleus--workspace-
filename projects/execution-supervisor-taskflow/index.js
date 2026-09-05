import { spawn } from "node:child_process";
import { mkdir, readFile, readdir, realpath, rename, stat, unlink, writeFile } from "node:fs/promises";
import { mkdirSync, realpathSync } from "node:fs";
import { dirname, isAbsolute, relative, resolve } from "node:path";
import { createHash, createPublicKey, generateKeyPairSync, randomUUID, verify } from "node:crypto";
import { Type } from "typebox";
import { homedir } from "node:os";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const DEFAULT_ROOT = "/home/stanislav/.openclaw/workspace/agents/main";
const DEFAULT_RUNTIME_ROOT = resolve(homedir(), ".openclaw/runtime/execution-supervisor");
const ADMISSION_TTL_MS = 5 * 60 * 1000;
const TERMINAL = new Set(["SUCCEEDED", "TIMED_OUT", "CRASHED", "ESCALATED", "INTERRUPTED", "FAILED", "BLOCKED"]);
const DEFAULT_MANAGED_PATTERNS = [
  /(?:запусти|проведи|выполни)\s+(?:контрольный|live|end[- ]to[- ]end)\s+(?:drill|дрилл)/iu,
  /выполни[\s\S]{0,160}сообщи\s+по\s+завершении/iu,
  /сообщи\s+по\s+завершении/iu,
  /(?:run|execute|complete)[\s\S]{0,160}(?:notify|tell)\s+me\s+(?:when|once)\s+(?:done|complete)/iu,
  /(?:notify|tell)\s+me\s+(?:when|once)\s+(?:done|complete)/iu,
  /(?:implement|execute|complete|finish)[\s\S]{0,240}(?:full|entire|all)\s+(?:plan|migration|program|objective)/iu,
  /(?:^|\s)(?:implement|execute|complete|finish)(?:\s|[,:])[\s\S]*(?:full|entire|all)\s+(?:plan|migration|program|objective)(?:\s|[.!?,:]|$)/iu,
];
const SAFE_PRE_DISPATCH_TOOLS = new Set(["execution_supervisor_dispatch"]);
const PLUGIN_CONFIG_SCHEMA = Type.Object({
  workspaceRoot: Type.Optional(Type.String()),
  runtimeRoot: Type.Optional(Type.String()),
  supervisorPath: Type.Optional(Type.String()),
  managedRunnerPath: Type.Optional(Type.String()),
  managedAgentTimeoutSeconds: Type.Optional(Type.Integer({ minimum: 300, maximum: 86400, default: 3600 })),
  authorizedSessionKeys: Type.Optional(Type.Array(Type.String(), { uniqueItems: true })),
  authorizedSenderIds: Type.Optional(Type.Array(Type.String(), { uniqueItems: true })),
  delivery: Type.Optional(Type.Object({ channel: Type.String(), accountId: Type.Optional(Type.String()),
    to: Type.String(), threadId: Type.Optional(Type.String()) }, { additionalProperties: false })),
  pollMs: Type.Optional(Type.Integer({ minimum: 1000, maximum: 60000 })),
}, { additionalProperties: false });

export function requiresManagedExecution(prompt, patterns = DEFAULT_MANAGED_PATTERNS) {
  if (typeof prompt !== "string") return false;
  if (patterns.some(pattern => pattern.test(prompt))) return true;
  if (/(?:^|\s)(?:выполни|реализуй|сделай|доведи)(?:\s|[,:])[\s\S]{0,240}(?:план|полностью|все\s+этапы|программу\s+работ)(?:\s|[.!?,:]|$)/iu.test(prompt)) return true;
  if (/(?:^|\s)(?:выполни|реализуй|сделай|доведи)(?:\s|[,:])[\s\S]*(?:план|полностью|все\s+этапы|программу\s+работ)(?:\s|[.!?,:]|$)/iu.test(prompt)) return true;
  return false;
}

function admissionId(runId) {
  return String(runId || randomUUID()).replace(/[^a-zA-Z0-9_-]/g, "-");
}
function ingressAdmissionId(sessionKey, prompt) {
  return createHash("sha256").update(`${sessionKey || "unknown"}\0${prompt}`).digest("hex").slice(0, 32);
}

function taskMarkdown(record) {
  return `# Managed task\n\n- Admission ID: \`${record.admissionId}\`\n- Owner: main\n- Session: \`${record.sessionKey}\`\n- Created: ${record.createdAt}\n- Trigger: explicit completion notification\n- Expected output: completed task plus durable result/evidence\n- Timeout: ${record.timeoutSeconds}s\n\n## Request\n\n${record.prompt}\n\n## Context\n\nRecent source-session context is stored in \`${record.contextPath}\`. Use it only to resolve the request; the task packet and current owner request remain authoritative.\n\n## Completion contract\n\nThe runner requires a machine-readable package and acceptance-gate result at \`${record.outcomePath}\`. Partial work continues in another managed slice. Process exit code alone cannot prove completion. BLOCKED is reserved for evidenced external dependencies.\n\n## Checklist\n\n- [x] Admission recorded before work\n- [ ] Managed flow created\n- [ ] All objective packages and acceptance gates passed\n- [ ] Runner terminal evidence recorded\n- [ ] At-least-once terminal notification acknowledged\n`;
}

function evidenceMarkdown(record) {
  return `# Managed execution evidence\n\nStatus: ADMITTED\n\n- Admission ID: \`${record.admissionId}\`\n- Session: \`${record.sessionKey}\`\n- Created: ${record.createdAt}\n- Execution mechanism: pending owner-bound TaskFlow dispatch\n- Expected output: validated terminal result owned by the managed runner\n`;
}

function isTrustedOwnerContext(ctx, config) {
  return ctx.senderIsOwner === true
    || config.authorizedSessionKeys?.includes(ctx.sessionKey) === true
    || config.authorizedSenderIds?.includes(String(ctx.senderId ?? "")) === true;
}

async function safePath(root, requested) {
  const canonicalRoot = await realpath(root);
  const unresolved = resolve(requested);
  if (!unresolved.startsWith(`${canonicalRoot}/`)) throw new Error("path outside workspace root");
  const target = await realpath(unresolved);
  if (!target.startsWith(`${canonicalRoot}/`)) throw new Error("path outside workspace root");
  return target;
}

async function readState(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

async function managedStateProcessAlive(state, expectedRunner, expectedResult) {
  if (!Number.isInteger(state?.pid) || !Number.isInteger(state?.pidStartTicks)) return false;
  try {
    process.kill(state.pid, 0);
    const statFields = (await readFile(`/proc/${state.pid}/stat`, "utf8")).split(" ");
    if (Number(statFields[21]) !== state.pidStartTicks) return false;
    const cmdline = (await readFile(`/proc/${state.pid}/cmdline`)).toString("utf8").replaceAll("\0", " ");
    return cmdline.includes(expectedRunner) && cmdline.includes(expectedResult);
  } catch { return false; }
}

async function atomicJson(path, value) {
  const temporary = resolve(dirname(path), `.${randomUUID()}.tmp`);
  await writeFile(temporary, JSON.stringify(value, null, 2) + "\n");
  await rename(temporary, path);
}

async function trustedTerminal(state, record) {
  try {
    const publicDer = Buffer.from(record?.stateJson?.terminalPublicKey || "", "base64");
    if (!publicDer.length || createHash("sha256").update(publicDer).digest("hex") !== state.terminalKeyId) return null;
    const data = JSON.parse(await readFile(state.terminalEvidencePath, "utf8"));
    if (!state.runNonce || data.runNonce !== state.runNonce) return null;
    const payload = JSON.stringify([String(data.terminalStatus || "").toUpperCase(), data.contractValidated === true, data.exitCode,
      data.runNonce, data.taskDigest ?? null, data.planDigest ?? null, data.outcomeDigest ?? null, data.finishedAt ?? null,
      data.summary ?? null, data.slices ?? null, data.outcomePath ?? null, data.agentOutputPath ?? null,
      data.independentReviewPaths ?? null]);
    const key = createPublicKey({ key: publicDer, format: "der", type: "spki" });
    return verify(null, Buffer.from(payload), key, Buffer.from(data.terminalSignature || "", "base64")) ? data : null;
  } catch { return null; }
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
  configSchema: PLUGIN_CONFIG_SCHEMA,
  register(api) {
    const config = api.pluginConfig ?? {};
    const workspaceRoot = realpathSync(resolve(config.workspaceRoot ?? DEFAULT_ROOT));
    mkdirSync(resolve(config.runtimeRoot ?? DEFAULT_RUNTIME_ROOT), { recursive: true, mode: 0o700 });
    const runtimeRoot = realpathSync(resolve(config.runtimeRoot ?? DEFAULT_RUNTIME_ROOT));
    const runtimeRelative = relative(workspaceRoot, runtimeRoot);
    if (runtimeRelative === "" || (!runtimeRelative.startsWith("..") && !isAbsolute(runtimeRelative))) {
      throw new Error("runtimeRoot must be outside the managed executor workspace");
    }
    const supervisor = config.supervisorPath ?? resolve(workspaceRoot, "scripts/execution-supervisor.py");
    const activeRecoveries = new Set();
    const admissionsByRun = new Map();
    const admissionsBySession = new Map();
    const supervisorResults = new Map();

    function admissionForContext(ctx) {
      const admission = (ctx.runId ? admissionsByRun.get(ctx.runId) : undefined) ?? admissionsBySession.get(ctx.sessionKey);
      if (admission?.status === "ADMITTED" && Date.now() - Date.parse(admission.createdAt) > ADMISSION_TTL_MS) {
        if (admission.runId) admissionsByRun.delete(admission.runId);
        if (admission.sessionKey) admissionsBySession.delete(admission.sessionKey);
        return undefined;
      }
      return admission;
    }

    async function createAdmission(event, ctx) {
      const prompt = event.prompt ?? event.content;
      if (!requiresManagedExecution(prompt)) return null;
      if (typeof ctx.sessionKey === "string" && ctx.sessionKey.startsWith("agent:main:managed:")) return null;
      let id = ctx.runId ? admissionId(ctx.runId) : ingressAdmissionId(ctx.sessionKey, prompt);
      const known = (ctx.runId && admissionsByRun.get(ctx.runId)) || (ctx.sessionKey && admissionsBySession.get(ctx.sessionKey));
      if (known && ["ADMITTED", "DISPATCHED"].includes(known.status)) return known;
      let taskRoot = resolve(workspaceRoot, "state/tasks/managed-admission", id);
      let trustedRoot = resolve(runtimeRoot, id);
      let persisted = await readFile(resolve(trustedRoot, "admission.json"), "utf8").then(JSON.parse).catch(() => null);
      if (persisted && (TERMINAL.has(persisted.status)
          || (persisted.status === "ADMITTED" && Date.now() - Date.parse(persisted.createdAt) > ADMISSION_TTL_MS))) {
        id = admissionId(); taskRoot = resolve(workspaceRoot, "state/tasks/managed-admission", id);
        trustedRoot = resolve(runtimeRoot, id); persisted = null;
      }
      if (persisted?.admissionId === id) {
        if (ctx.runId) admissionsByRun.set(ctx.runId, persisted);
        if (ctx.sessionKey) admissionsBySession.set(ctx.sessionKey, persisted);
        return persisted;
      }
      const record = {
        schemaVersion: 1, admissionId: id, status: "ADMITTED", prompt,
        runId: ctx.runId ?? null, sessionKey: ctx.sessionKey ?? null,
        createdAt: new Date().toISOString(), timeoutSeconds: config.managedAgentTimeoutSeconds ?? 3600,
        taskRoot, trustedRoot, taskPath: resolve(taskRoot, "TASK_PACKET.md"),
        contextPath: resolve(taskRoot, "CONTEXT.json"),
        evidencePath: resolve(taskRoot, "EVIDENCE.md"),
        statePath: resolve(trustedRoot, "execution-supervisor-state.json"),
        outboxPath: resolve(trustedRoot, "outbox.jsonl"),
        resultPath: resolve(trustedRoot, "RESULT.json"),
        outcomePath: resolve(taskRoot, "MANAGED_OUTCOME.json"),
        runnerOutputPath: resolve(taskRoot, "agent-result.json"),
      };
      await mkdir(taskRoot, { recursive: true });
      await mkdir(trustedRoot, { recursive: true, mode: 0o700 });
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
      try { await writeFile(resolve(trustedRoot, "admission.json"), JSON.stringify(record, null, 2) + "\n", { flag: "wx", mode: 0o600 }); }
      catch (error) {
        if (error?.code !== "EEXIST") throw error;
        const existing = await readFile(resolve(trustedRoot, "admission.json"), "utf8").then(JSON.parse);
        if (ctx.runId) admissionsByRun.set(ctx.runId, existing);
        if (ctx.sessionKey) admissionsBySession.set(ctx.sessionKey, existing);
        return existing;
      }
      if (ctx.runId) admissionsByRun.set(ctx.runId, record);
      if (ctx.sessionKey) admissionsBySession.set(ctx.sessionKey, record);
      return record;
    }

    function deliveryFromDispatch(event, ctx) {
      const sessionKey = ctx.sessionKey ?? event.sessionKey ?? "";
      const topic = sessionKey.match(/:group:(-?\d+):topic:(\d+)$/);
      if (topic) return { channel: ctx.channelId ?? event.channel ?? "telegram",
        accountId: ctx.accountId, to: `telegram:${topic[1]}:topic:${topic[2]}`, threadId: topic[2] };
      const direct = sessionKey.match(/:direct:(\d+)$/);
      if (direct) return { channel: ctx.channelId ?? event.channel ?? "telegram",
        accountId: ctx.accountId, to: `telegram:${direct[1]}` };
      return { channel: ctx.channelId ?? event.channel, accountId: ctx.accountId,
        to: ctx.conversationId };
    }

    async function dispatchAdmission(admission, runtime, deliveryContext) {
      if (!deliveryContext?.channel || !deliveryContext?.to) throw new Error("originating delivery context required");
      const dispatchLock = resolve(admission.trustedRoot, "dispatch.lock");
      try { await writeFile(dispatchLock, `${process.pid}\n`, { flag: "wx" }); }
      catch (error) {
        if (error?.code !== "EEXIST") throw error;
        if (Date.now() - (await stat(dispatchLock)).mtimeMs > 30000) {
          const state = await readState(admission.statePath).catch(() => null);
          if (state?.status === "RUNNING" && await managedStateProcessAlive(state,
              config.managedRunnerPath ?? resolve(workspaceRoot, "scripts/managed-agent-runner.mjs"), admission.resultPath)) {
            try {
              Object.assign(admission, { status: "DISPATCHED", flowId: state.flowId, supervisorPid: state.pid });
              await atomicJson(resolve(admission.trustedRoot, "admission.json"), admission);
              return { admissionId: admission.admissionId, flowId: state.flowId, supervisorPid: state.pid,
                evidencePath: admission.evidencePath, statePath: admission.statePath };
            } catch {}
          }
          const staleLock = `${dispatchLock}.stale.${randomUUID()}`;
          try { await rename(dispatchLock, staleLock); }
          catch (error) {
            if (error?.code !== "ENOENT") throw error;
            return dispatchAdmission(admission, runtime, deliveryContext);
          }
          await unlink(staleLock).catch(() => {});
          return dispatchAdmission(admission, runtime, deliveryContext);
        }
        for (let attempt = 0; attempt < 100; attempt++) {
          const current = await readFile(resolve(admission.trustedRoot, "admission.json"), "utf8").then(JSON.parse).catch(() => null);
          if (current?.status === "DISPATCHED") return { admissionId: current.admissionId, flowId: current.flowId,
            supervisorPid: current.supervisorPid, evidencePath: current.evidencePath, statePath: current.statePath };
          await new Promise(done => setTimeout(done, 50));
        }
        throw new Error(`concurrent admission dispatch did not settle: ${admission.admissionId}`);
      }
      let flow = null;
      let child = null;
      try {
      const { privateKey, publicKey } = generateKeyPairSync("ed25519");
      const terminalPrivateKey = privateKey.export({ format: "der", type: "pkcs8" });
      const terminalPublicKey = publicKey.export({ format: "der", type: "spki" }).toString("base64");
      flow = runtime.createManaged({ controllerId: "execution-supervisor-taskflow/v2", goal: admission.prompt,
        status: "running", notifyPolicy: "state_changes", currentStep: "managed-agent-runner",
        stateJson: { admissionId: admission.admissionId, evidencePath: admission.evidencePath,
          statePath: admission.statePath, outboxPath: admission.outboxPath, terminalPublicKey } });
      const runner = config.managedRunnerPath ?? resolve(workspaceRoot, "scripts/managed-agent-runner.mjs");
      const managedSession = `agent:main:managed:${admission.admissionId}`;
      const argv = [supervisor, "run", "--evidence", admission.evidencePath, "--state", admission.statePath,
        "--outbox", admission.outboxPath, "--terminal-evidence", admission.resultPath,
        "--timeout", String(admission.timeoutSeconds), "--owner", "main", "--flow-id", flow.flowId,
        "--session-key", admission.sessionKey, "--delivery-json", JSON.stringify(deliveryContext ?? {}),
        "--require-validated-terminal", "--",
        process.execPath, runner, "--prompt", admission.taskPath, "--result", admission.resultPath,
        "--agent-output", admission.runnerOutputPath, "--outcome", admission.outcomePath, "--session-key", managedSession,
        "--timeout", String(Math.max(5, admission.timeoutSeconds - 150)), "--thinking", "high",
        "--executor-agent", "managed-worker"];
      child = spawn("python3", argv, { detached: true, stdio: ["ignore", "ignore", "ignore", "pipe"], env: { ...process.env,
        MANAGED_WORKSPACE_ROOT: workspaceRoot, MANAGED_SUPERVISOR_PRIVATE_FD: "3" } });
      child.stdio[3].end(terminalPrivateKey);
      child.once("exit", code => supervisorResults.set(admission.admissionId, code));
      await new Promise((ok, fail) => { child.once("spawn", ok); child.once("error", fail); });
      let startedState = null;
      for (let attempt = 0; attempt < 100; attempt++) {
        startedState = await readState(admission.statePath).catch(() => null);
        if ((startedState?.status === "RUNNING" || TERMINAL.has(startedState?.status)) && Number.isInteger(startedState.pid) && startedState.pidStartTicks) break;
        if (supervisorResults.has(admission.admissionId)) break;
        await new Promise(done => setTimeout(done, 50));
      }
      if (!((startedState?.status === "RUNNING" || TERMINAL.has(startedState?.status)) && Number.isInteger(startedState.pid) && startedState.pidStartTicks)) {
        throw new Error(`execution supervisor failed to establish RUNNING state: ${admission.admissionId}`);
      }
      if (startedState.status === "RUNNING") {
        try { process.kill(startedState.pid, 0); }
        catch { throw new Error(`managed runner was not alive after dispatch: ${admission.admissionId}`); }
      }
      child.unref();
      Object.assign(admission, { status: "DISPATCHED", flowId: flow.flowId, supervisorPid: child.pid, deliveryContext });
      if (admission.runId) admissionsByRun.set(admission.runId, admission);
      if (admission.sessionKey) admissionsBySession.set(admission.sessionKey, admission);
      await atomicJson(resolve(admission.trustedRoot, "admission.json"), admission);
      const details = { admissionId: admission.admissionId, flowId: flow.flowId, revision: flow.revision,
        supervisorPid: child.pid, evidencePath: admission.evidencePath, statePath: admission.statePath };
      await unlink(dispatchLock).catch(() => {});
      return details;
      } catch (error) {
        if (child && child.exitCode === null) {
          try { child.kill("SIGTERM"); } catch {}
        }
        if (flow && !["succeeded", "failed", "cancelled"].includes(runtime.get(flow.flowId)?.status)) {
          try { runtime.fail({ flowId: flow.flowId, expectedRevision: runtime.get(flow.flowId)?.revision ?? flow.revision,
            stateJson: { ...flow.stateJson, dispatchFailure: String(error) },
            blockedSummary: "execution supervisor failed before RUNNING was established", endedAt: Date.now() }); } catch {}
        }
        Object.assign(admission, { status: "FAILED", dispatchError: String(error) });
        await atomicJson(resolve(admission.trustedRoot, "admission.json"), admission).catch(() => {});
        await unlink(dispatchLock).catch(() => {});
        throw error;
      }
    }

    api.on("before_dispatch", async (event, ctx) => {
      if (!requiresManagedExecution(event.content)) return;
      const allowedSenders = config.authorizedSenderIds ?? [];
      if (allowedSenders.length > 0 && !allowedSenders.includes(String(ctx.senderId ?? event.senderId ?? ""))) return;
      if (!isTrustedOwnerContext(ctx, config)) return;
      const derivedDelivery = deliveryFromDispatch(event, ctx);
      const deliveryContext = derivedDelivery?.channel && derivedDelivery?.to ? derivedDelivery : config.delivery;
      const admission = await createAdmission({ content: event.content, messages: [] }, ctx);
      if (!admission) return;
      if (admission.status === "DISPATCHED") return { handled: true,
        text: `Managed execution already started. Flow ${admission.flowId}; PID ${admission.supervisorPid}; evidence ${admission.evidencePath}` };
      const runtime = api.runtime.tasks.flow.bindSession({ sessionKey: admission.sessionKey,
        requesterOrigin: deliveryContext });
      const details = await dispatchAdmission(admission, runtime, deliveryContext);
      return { handled: true, text: `Managed execution started. Flow ${details.flowId}; PID ${details.supervisorPid}; evidence ${details.evidencePath}` };
    });

    api.on("before_agent_run", async (event, ctx) => {
      if (!isTrustedOwnerContext({ ...ctx, senderIsOwner: event.senderIsOwner }, config)) return;
      await createAdmission(event, ctx);
      return { outcome: "pass" };
    });

    api.on("before_prompt_build", (_event, ctx) => {
      const admission = admissionForContext(ctx);
      if (!admission || admission.status === "DISPATCHED") return;
      return { prependContext: `MANAGED EXECUTION REQUIRED (admission ${admission.admissionId}). Before any task work, call execution_supervisor_dispatch with no arguments. Do not use bash, exec, apply_patch, Codex, subagents, or other work tools in this turn. After dispatch, report the returned flow/run/PID/evidence identifiers and stop.` };
    });

    api.on("before_tool_call", (event, ctx) => {
      const admission = admissionForContext(ctx);
      if (!admission || SAFE_PRE_DISPATCH_TOOLS.has(event.toolName)) return;
      return { block: true, blockReason: admission.status === "DISPATCHED"
        ? `Managed task ${admission.admissionId} is already detached; foreground work is blocked.`
        : `Managed admission ${admission.admissionId} requires execution_supervisor_dispatch before any work tool.` };
    });

    async function reconcileState(statePath, runtimeConfig) {
      if (activeRecoveries.has(statePath)) return { skipped: "already-running" };
      activeRecoveries.add(statePath);
      try {
        let state = await readState(statePath);
        const admissionPath = resolve(statePath, "../admission.json");
        const admission = await readFile(admissionPath, "utf8").then(JSON.parse).catch(() => null);
        if (!admission || admission.statePath !== statePath || admission.flowId !== state.flowId
            || admission.sessionKey !== state.sessionKey) throw new Error(`untrusted supervisor state: ${statePath}`);
        const persistedDelivery = state.deliveryContext;
        const liveAdmission = [...admissionsByRun.values(), ...admissionsBySession.values()]
          .find(item => item.statePath === statePath);
        const liveDelivery = liveAdmission?.deliveryContext;
        state.deliveryContext = liveDelivery?.channel && liveDelivery?.to ? liveDelivery
          : (persistedDelivery?.channel && persistedDelivery?.to ? persistedDelivery : config.delivery);
        if (!state.sessionKey || !state.flowId) throw new Error(`untrusted supervisor state: ${statePath}`);
        const runtime = api.runtime.tasks.flow.bindSession({ sessionKey: state.sessionKey,
          requesterOrigin: state.deliveryContext });
        const record = runtime.get(state.flowId);
        if (!record || record.stateJson?.admissionId !== admission.admissionId
            || record.stateJson?.statePath !== statePath) throw new Error(`untrusted managed flow: ${statePath}`);
        const runRecovery = async () => {
          const child = spawn("python3", [supervisor, "recover", "--state", statePath,
            "--terminal-public-key", record.stateJson.terminalPublicKey], { stdio: "ignore" });
          await new Promise((ok, fail) => { child.on("exit", code => code === 0 ? ok() : fail(new Error(`recovery exit ${code}`))); child.on("error", fail); });
          state = await readState(statePath);
        };
        const runnerPath = config.managedRunnerPath ?? resolve(workspaceRoot, "scripts/managed-agent-runner.mjs");
        if (await managedStateProcessAlive(state, runnerPath, admission.resultPath)) {
          await runRecovery();
          return { state, mutation: null, skipped: "runner-alive" };
        }
        if (!TERMINAL.has(state.status) || !state.notificationId) await runRecovery();
        if (state.status === "SUCCEEDED") {
          const terminalProof = await trustedTerminal(state, record);
          const trustedSuccess = terminalProof?.contractValidated === true
            && String(terminalProof.terminalStatus).toUpperCase() === "SUCCEEDED" && terminalProof.exitCode === 0;
          if (!trustedSuccess || supervisorResults.get(admission.admissionId) > 0) await runRecovery();
        }
        let mutation = null;
        if (TERMINAL.has(state.status) && !["succeeded", "failed", "cancelled"].includes(record.status)) {
            mutation = state.status === "SUCCEEDED"
              ? runtime.finish({ flowId: record.flowId, expectedRevision: record.revision, stateJson: { ...record.stateJson, supervisor: state }, endedAt: Date.now() })
              : runtime.fail({ flowId: record.flowId, expectedRevision: record.revision, stateJson: { ...record.stateJson, supervisor: state }, blockedSummary: `execution supervisor: ${state.status}`, endedAt: Date.now() });
        }
        if (TERMINAL.has(state.status) && !state.notificationDelivered) {
          // Owner-approved at-least-once contract: after an unknown send/ack
          // outcome the lease expires and this notificationId may be retried.
          // A rare duplicate is preferable to losing the terminal result.
          const claim = spawn("python3", [supervisor, "claim-delivery", "--state", statePath,
            "--notification-id", state.notificationId], { stdio: ["ignore", "pipe", "ignore"] });
          let claimId = ""; claim.stdout.setEncoding("utf8"); claim.stdout.on("data", chunk => { claimId += chunk; });
          const claimed = await new Promise((ok, fail) => { claim.on("exit", code => code === 0 ? ok(true) : code === 3 ? ok(false) : fail(new Error(`delivery claim exit ${code}`))); claim.on("error", fail); });
          if (!claimed) return { state, mutation, skipped: "delivery-claimed" };
          claimId = claimId.trim();
          const delivery = adapterTarget(state.deliveryContext);
          if (!delivery.channel || !delivery.to) throw new Error(`missing originating delivery context: ${statePath}`);
          const adapter = await api.runtime.channel.outbound.loadAdapter(delivery.channel);
          if (!adapter?.sendText) throw new Error(`outbound adapter unavailable: ${delivery.channel}`);
          const sendPromise = adapter.sendText({ cfg: runtimeConfig ?? api.config,
            accountId: delivery.accountId, to: delivery.to, threadId: delivery.threadId,
            text: `Execution supervisor: ${state.status}. Flow ${state.flowId}; run ${state.runId}; exit code ${state.exitCode ?? "n/a"}.`,
            deliveryQueueId: state.notificationId });
          const sent = await Promise.race([sendPromise, new Promise((_, reject) => {
            const timer = setTimeout(() => reject(new Error(`outbound provider timeout: ${delivery.channel}`)), 30000);
            timer.unref?.();
          })]);
          const ack = spawn("python3", [supervisor, "ack", "--state", statePath,
            "--notification-id", state.notificationId, "--claim-id", claimId], { stdio: "ignore" });
          await new Promise((ok, fail) => { ack.on("exit", code => code === 0 ? ok() : fail(new Error(`ack exit ${code}`))); ack.on("error", fail); });
          state = { ...await readState(statePath), delivery: sent };
        }
        if (TERMINAL.has(state.status)) {
          const persistedAdmission = await readFile(admissionPath, "utf8").then(JSON.parse).catch(() => null);
          if (persistedAdmission) await atomicJson(admissionPath, { ...persistedAdmission, status: state.status });
          for (const [key, value] of admissionsByRun) if (value.statePath === statePath) admissionsByRun.delete(key);
          for (const [key, value] of admissionsBySession) if (value.statePath === statePath) admissionsBySession.delete(key);
          supervisorResults.delete(admission.admissionId);
        }
        return { state, mutation };
      } finally { activeRecoveries.delete(statePath); }
    }

    let recoveryTimer = null;
    api.registerService({
      id: "execution-supervisor-recovery",
      start: async (serviceCtx) => {
        const tick = async () => {
          for (const statePath of await findStateFiles(runtimeRoot)) {
            const state = await readState(statePath).catch(() => null);
            if (!state) continue;
            if (state.notificationDelivered && TERMINAL.has(state.status)) {
              const admission = await readFile(resolve(statePath, "../admission.json"), "utf8").then(JSON.parse).catch(() => null);
              if (admission?.status === state.status) continue;
            }
            if (state.status === "RUNNING" && Date.now() - Date.parse(state.lastVerified) < 15000) continue;
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
        const derived = deliveryFromDispatch({}, { ...ctx, sessionKey: admission.sessionKey });
        const delivery = derived?.channel && derived?.to ? derived : config.delivery;
        const details = await dispatchAdmission(admission, runtime, delivery);
        return { content: [{ type: "text", text: JSON.stringify(details) }], details };
      }
    }), { name: "execution_supervisor_dispatch" });

  }
});

export default plugin;
