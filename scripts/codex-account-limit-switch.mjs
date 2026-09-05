#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const LEGACY_PROVIDER = 'openai-codex';
const PROVIDER = 'openai';
const LEGACY_PROFILES = [
  'openai-codex:stasiintegraleus@gmail.com',
  'openai-codex:integraleus55@gmail.com',
];
const PROFILES = [
  'openai:stasiintegraleus@gmail.com',
  'openai:integraleus55@gmail.com',
];
const THRESHOLD = Number(process.env.CODEX_ACCOUNT_REMAINING_MIN ?? '20');
const AUTO_SWITCH = process.env.CODEX_ACCOUNT_AUTO_SWITCH === '1';
const DRY_RUN = process.env.CODEX_ACCOUNT_SWITCH_DRY_RUN === '1';

function homePath(value) {
  if (!value) return value;
  return value.startsWith('~/') ? path.join(os.homedir(), value.slice(2)) : value;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function runJson(command, args) {
  const result = spawnSync(command, args, {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  if (result.status !== 0) return null;
  try {
    return JSON.parse(result.stdout);
  } catch {
    return null;
  }
}

function profileAlias(profile) {
  const legacyIndex = LEGACY_PROFILES.indexOf(profile);
  if (legacyIndex >= 0) return PROFILES[legacyIndex];
  const currentIndex = PROFILES.indexOf(profile);
  if (currentIndex >= 0) return LEGACY_PROFILES[currentIndex];
  return null;
}

function canonicalProfile(profile, availableProfiles) {
  if (availableProfiles.has(profile)) return profile;
  const alias = profileAlias(profile);
  if (alias && availableProfiles.has(alias)) return alias;
  return profile;
}

function findCodexDist() {
  const projectsDir = homePath(process.env.OPENCLAW_NPM_PROJECTS_DIR ?? '~/.openclaw/npm/projects');
  const candidates = fs.readdirSync(projectsDir)
    .filter((name) => name.startsWith('openclaw-codex-'))
    .map((name) => path.join(projectsDir, name, 'node_modules/@openclaw/codex/dist'))
    .filter((dir) => {
      if (!fs.existsSync(dir)) return false;
      const files = fs.readdirSync(dir);
      return files.some((file) => /^request-.*\.js$/.test(file)) && files.some((file) => /^config-.*\.js$/.test(file));
    })
    .sort();
  if (candidates.length === 0) throw new Error(`Codex plugin dist not found under ${projectsDir}`);
  return candidates[candidates.length - 1];
}

function findDistFile(dist, prefix) {
  const file = fs.readdirSync(dist).find((name) => name.startsWith(prefix) && name.endsWith('.js'));
  if (!file) throw new Error(`Codex plugin ${prefix}*.js not found under ${dist}`);
  return path.join(dist, file);
}

function findNamedFunction(module, name) {
  const match = Object.values(module).find((value) => typeof value === 'function' && value.name === name);
  if (!match) throw new Error(`Codex ${name} export not found`);
  return match;
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
  const profileStorePath = path.join(agentDir, 'auth-profiles.json');
  const profileStore = fs.existsSync(profileStorePath) ? readJson(profileStorePath) : {};
  const modelsStatus = runJson('openclaw', ['models', 'status', '--json']);
  const statusOpenaiProfiles = modelsStatus?.auth?.oauth?.providers
    ?.find((provider) => provider.provider === PROVIDER)
    ?.effectiveProfiles
    ?.map((profile) => profile.profileId)
    ?.filter((profile) => PROFILES.includes(profile) || LEGACY_PROFILES.includes(profile));
  const availableProfiles = new Set([
    ...Object.keys(profileStore.profiles ?? {}),
    ...(modelsStatus?.auth?.oauth?.profiles ?? []).map((profile) => profile.profileId),
  ]);
  const activeProfiles = statusOpenaiProfiles?.length >= 2
    ? statusOpenaiProfiles.slice(0, 2)
    : PROFILES.every((profile) => availableProfiles.has(profile))
      ? PROFILES
      : LEGACY_PROFILES;
  const order =
    statusOpenaiProfiles?.length >= 2
      ? statusOpenaiProfiles.slice(0, 2)
      : authState.order?.[PROVIDER]
        ?? config.auth?.order?.[PROVIDER]
        ?? authState.order?.[LEGACY_PROVIDER]
        ?? config.auth?.order?.[LEGACY_PROVIDER]
        ?? activeProfiles;
  const normalizedOrder = order.map((profile) => canonicalProfile(profile, new Set(activeProfiles)));
  const current = normalizedOrder.find((profile) => activeProfiles.includes(profile)) ?? activeProfiles[0];
  const other = activeProfiles.find((profile) => profile !== current);
  if (!other) throw new Error(`could not determine second Codex account profile from: ${activeProfiles.join(', ')}`);

  const dist = findCodexDist();
  const configModule = await import(pathToFileURL(findDistFile(dist, 'config-')).href);
  const requestModule = await import(pathToFileURL(findDistFile(dist, 'request-')).href);
  const resolveRuntime = findNamedFunction(configModule, 'resolveCodexAppServerRuntimeOptions');
  const request = findNamedFunction(requestModule, 'requestCodexAppServerJson');
  const pluginConfig = config.plugins?.entries?.codex?.config ?? config.plugins?.entries?.codex ?? {};

  const summaries = {};
  for (const profile of activeProfiles) {
    summaries[profile] = await readRateLimitsForProfile({ profile, config, pluginConfig, agentDir, request, resolveRuntime });
  }

  console.log('Codex account limit check:');
  for (const profile of activeProfiles) console.log(`- ${fmt(profile, summaries[profile])}`);
  console.log(`active_order_first: ${current}`);

  const currentMin = minRemaining(summaries[current]);
  const otherMin = minRemaining(summaries[other]);
  const currentLow = summaries[current]?.blocked || (typeof currentMin === 'number' && currentMin < THRESHOLD);
  const otherHealthy = summaries[other] && !summaries[other].blocked && typeof otherMin === 'number' && otherMin > THRESHOLD;

  if (currentLow && otherHealthy) {
    const nextOrder = [other, current];
    const orderProvider = LEGACY_PROFILES.some((profile) => order.includes(profile)) ? LEGACY_PROVIDER : PROVIDER;
    const commandOrder = orderProvider === LEGACY_PROVIDER
      ? nextOrder.map((profile) => profileAlias(profile) ?? profile)
      : nextOrder;
    const switchMessage = `would switch Codex auth order to ${commandOrder.join(' -> ')} because ${current} is below ${THRESHOLD}% and ${other} is healthy.`;
    if (!AUTO_SWITCH || DRY_RUN) {
      if (DRY_RUN) console.log(`DRY_RUN: ${switchMessage}`);
      else console.log(`WARN: ${switchMessage}`);
      console.log(`WARN: Codex auth order not changed; ${DRY_RUN ? 'dry-run is enabled.' : 'auto-switch is disabled; set CODEX_ACCOUNT_AUTO_SWITCH=1 to allow changing auth order.'}`);
      process.exitCode = 1;
      return;
    }
    const result = spawnSync('openclaw', ['models', 'auth', 'order', 'set', '--provider', orderProvider, ...commandOrder], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    if (result.status !== 0) {
      throw new Error(`failed to switch Codex auth order: ${result.stderr || result.stdout || `exit ${result.status}`}`);
    }
    console.log(`WARN: switched Codex auth order to ${commandOrder.join(' -> ')} because ${current} is below ${THRESHOLD}% and ${other} is healthy.`);
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
