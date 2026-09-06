import http from "node:http";
import { readFile, readdir, stat } from "node:fs/promises";
import { resolve, dirname, join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
export const workspaceRoot = resolve(here, "../..");
export const defaultStateRoot = resolve(workspaceRoot, "state/tasks");
const terminal = new Set(["SUCCEEDED", "FAILED", "CRASHED", "TIMED_OUT", "ESCALATED", "BLOCKED", "INTERRUPTED", "STALE"]);

async function json(path) {
  try { return JSON.parse(await readFile(path, "utf8")); } catch { return null; }
}

async function text(path, max = 24000) {
  try { return (await readFile(path, "utf8")).slice(0, max); } catch { return null; }
}

async function findStateFiles(root) {
  const found = [];
  async function walk(dir) {
    let entries;
    try { entries = await readdir(dir, { withFileTypes: true }); } catch { return; }
    await Promise.all(entries.map(async entry => {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) await walk(path);
      else if (entry.name === "execution-supervisor-state.json") found.push(path);
    }));
  }
  await walk(root);
  return found;
}

function routeLabel(state, admission) {
  const key = state.sessionKey || admission.sessionKey || "";
  const topic = key.match(/:topic:(\d+)$/)?.[1];
  if (topic) return `Telegram · тема ${topic}`;
  if (key.includes(":telegram:")) return "Telegram · личка";
  return key ? "Локальный запуск" : "Маршрут неизвестен";
}

function alive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return false;
  try { process.kill(pid, 0); return true; } catch { return false; }
}

export async function loadRuns(root = defaultStateRoot) {
  const stateFiles = await findStateFiles(root);
  const runs = await Promise.all(stateFiles.map(async statePath => {
    const dir = dirname(statePath);
    const [state, admission, result, evidence, info] = await Promise.all([
      json(statePath), json(join(dir, "admission.json")), json(join(dir, "RESULT.json")),
      text(join(dir, "EVIDENCE.md")), stat(statePath).catch(() => null)
    ]);
    if (!state) return null;
    const started = Date.parse(state.startedAt || admission?.createdAt || 0);
    const ended = Date.parse(state.finishedAt || state.lastVerified || 0);
    const processAlive = alive(state.pid);
    const effectiveStatus = state.status === "RUNNING" && !processAlive ? "STALE" : state.status;
    return {
      id: relative(root, dir).split(sep).join("/"),
      flowId: state.flowId || admission?.flowId || null,
      runId: state.runId || null,
      status: effectiveStatus || "UNKNOWN",
      recordedStatus: state.status || "UNKNOWN",
      prompt: admission?.prompt || null,
      owner: state.owner || null,
      pid: state.pid || null,
      supervisorPid: admission?.supervisorPid || null,
      processAlive,
      startedAt: state.startedAt || admission?.createdAt || null,
      lastVerified: state.lastVerified || null,
      finishedAt: state.finishedAt || result?.finishedAt || null,
      durationMs: Number.isFinite(started) && Number.isFinite(ended) ? Math.max(0, ended - started) : null,
      timeoutSeconds: state.timeoutSeconds ?? admission?.timeoutSeconds ?? null,
      exitCode: state.exitCode ?? result?.exitCode ?? null,
      notificationDelivered: Boolean(state.notificationDelivered),
      deliveredAt: state.deliveredAt || null,
      route: routeLabel(state, admission || {}),
      evidencePath: state.evidencePath || join(dir, "EVIDENCE.md"),
      statePath,
      evidence,
      updatedAt: info?.mtime?.toISOString() || null,
      terminal: terminal.has(effectiveStatus)
    };
  }));
  return runs.filter(Boolean).sort((a, b) => Date.parse(b.startedAt || 0) - Date.parse(a.startedAt || 0));
}

export function summarize(runs) {
  return {
    total: runs.length,
    running: runs.filter(r => r.status === "RUNNING").length,
    succeeded: runs.filter(r => r.status === "SUCCEEDED").length,
    attention: runs.filter(r => !["RUNNING", "SUCCEEDED"].includes(r.status)).length,
    deliveryPending: runs.filter(r => r.terminal && !r.notificationDelivered).length,
    generatedAt: new Date().toISOString()
  };
}

function send(res, status, body, type = "application/json; charset=utf-8") {
  res.writeHead(status, { "content-type": type, "cache-control": "no-store", "x-content-type-options": "nosniff" });
  res.end(body);
}

export function createServer({ stateRoot = defaultStateRoot } = {}) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, "http://localhost");
    if (url.pathname === "/api/runs") {
      const runs = await loadRuns(stateRoot);
      return send(res, 200, JSON.stringify({ summary: summarize(runs), runs }));
    }
    if (url.pathname === "/" || url.pathname === "/index.html") {
      return send(res, 200, await readFile(join(here, "index.html"), "utf8"), "text/html; charset=utf-8");
    }
    send(res, 404, JSON.stringify({ error: "not_found" }));
  });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const host = process.env.DASHBOARD_HOST || "127.0.0.1";
  const port = Number(process.env.DASHBOARD_PORT || 4177);
  createServer().listen(port, host, () => console.log(`Supervisor dashboard: http://${host}:${port}`));
}
