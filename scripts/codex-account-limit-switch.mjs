#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const PROVIDER = 'openai-codex';
const PROFILES = [
  'openai-codex:stasiintegraleus@gmail.com',
  'openai-codex:integraleus55@gmail.com',
];
const THRESHOLD = Number(process.env.CODEX_ACCOUNT_REMAINING_MIN ?? '20');

function homePath(value) {
  if (!value) return value;
  return value.startsWith('~/') ? path.join(os.homedir(), value.slice(2)) : value;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function findCodexDist() {
  const projectsDir = homePath(process.env.OPENCLAW_NPM_PROJECTS_DIR ?? '~/.openclaw/npm/projects');
  const candidates = fs.readdirSync(projectsDir)
    .filter((name) => name.startsWith('openclaw-codex-'))
    .map((name) => path.join(projectsDir, name, 'node_modules/@openclaw/codex/dist'))
    .filter((dir) => fs.existsSync(path.join(dir, 'request-CF4f5hWY.js')) && fs.existsSync(path.join(dir, 'config--tW89bHH.js')))
    .sort();
  if (candidates.length === 0) throw new Error(`Codex plugin dist not found under ${projectsDir}`);
  return candidates[candidates.length - 1];
}

function remainingFromLimit(limit) {
  if (!limit) return null;
  const primaryUsed = limit.primary?.usedPercent;
  const secondaryUsed = limit.secondary?.usedPercent;
  return {
    fiveHour: typeof primaryUsed === 'number' ? Math.max(0, 100 - primaryUsed) : null,
    week: typeof secondaryUsed === 'number' ? Math.max(0, 100 - secondaryUsed) : null,
    blocked: Boolean(limit.rateLimitReachedType),
    reset5h: limit.primary?.resetsAt ?? null,
    resetWeek: limit.secondary?.resetsAt ?? null,
  };
}

function minRemaining(summary) {
  const values = [summary?.fiveHour, summary?.week].filter((value) => typeof value === 'number');
  return values.length ? Math.min(...values) : null;
}

function fmt(profile, summary) {
  if (!summary) return `${profile}: unavailable`;
  const parts = [
    `5h=${summary.fiveHour ?? '?'}%`,
    `week=${summary.week ?? '?'}%`,
  ];
  if (summary.blocked) parts.push('blocked');
  return `${profile}: ${parts.join(' ')}`;
}

async function readRateLimitsForProfile({ profile, config, pluginConfig, agentDir, request, resolveRuntime }) {
  const runtime = resolveRuntime({ pluginConfig });
  const result = await request({
    method: 'account/rateLimits/read',
    requestParams: undefined,
    timeoutMs: runtime.requestTimeoutMs,
    startOptions: runtime.start,
    config,
    authProfileId: profile,
    agentDir,
    isolated: true,
  });
  return remainingFromLimit(result?.rateLimitsByLimitId?.codex ?? result?.rateLimits);
}

async function main() {
  const configPath = homePath(process.env.OPENCLAW_CONFIG_PATH ?? '~/.openclaw/openclaw.json');
  const agentDir = homePath(process.env.OPENCLAW_AGENT_DIR ?? '~/.openclaw/agents/main/agent');
  const authStatePath = path.join(agentDir, 'auth-state.json');
  const config = readJson(configPath);
  const authState = fs.existsSync(authStatePath) ? readJson(authStatePath) : {};
  const order = authState.order?.[PROVIDER] ?? config.auth?.order?.[PROVIDER] ?? config.auth?.order?.openai ?? PROFILES;
  const current = order.find((profile) => PROFILES.includes(profile)) ?? PROFILES[0];
  const other = PROFILES.find((profile) => profile !== current);

  const dist = findCodexDist();
  const { l: resolveRuntime } = await import(pathToFileURL(path.join(dist, 'config--tW89bHH.js')).href);
  const { t: request } = await import(pathToFileURL(path.join(dist, 'request-CF4f5hWY.js')).href);
  const pluginConfig = config.plugins?.entries?.codex?.config ?? config.plugins?.entries?.codex ?? {};

  const summaries = {};
  for (const profile of PROFILES) {
    summaries[profile] = await readRateLimitsForProfile({ profile, config, pluginConfig, agentDir, request, resolveRuntime });
  }

  console.log('Codex account limit check:');
  for (const profile of PROFILES) console.log(`- ${fmt(profile, summaries[profile])}`);
  console.log(`active_order_first: ${current}`);

  const currentMin = minRemaining(summaries[current]);
  const otherMin = minRemaining(summaries[other]);
  const currentLow = summaries[current]?.blocked || (typeof currentMin === 'number' && currentMin < THRESHOLD);
  const otherHealthy = summaries[other] && !summaries[other].blocked && typeof otherMin === 'number' && otherMin > THRESHOLD;

  if (currentLow && otherHealthy) {
    const nextOrder = [other, current];
    const result = spawnSync('openclaw', ['models', 'auth', 'order', 'set', '--provider', PROVIDER, ...nextOrder], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    if (result.status !== 0) {
      throw new Error(`failed to switch Codex auth order: ${result.stderr || result.stdout || `exit ${result.status}`}`);
    }
    console.log(`WARN: switched Codex auth order to ${nextOrder.join(' -> ')} because ${current} is below ${THRESHOLD}% and ${other} is healthy.`);
    return;
  }

  if (currentLow && !otherHealthy) {
    console.log(`WARN: active Codex account is below ${THRESHOLD}%, but the other account is not healthy enough to switch.`);
    process.exitCode = 1;
    return;
  }

  console.log('codex_account_switch: no switch needed.');
}

main().catch((error) => {
  console.log(`WARN: Codex account limit switch check failed: ${error?.message ?? String(error)}`);
  process.exitCode = 1;
});
