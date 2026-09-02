import assert from "node:assert/strict";
import { chmod, mkdtemp, readFile, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { join } from "node:path";
import os from "node:os";

async function runProcess(command, args, env) {
  const child = spawn(command, args, { env, stdio: "ignore" });
  return await new Promise((resolve, reject) => {
    child.on("error", reject); child.on("exit", code => resolve(code));
  });
}

const root = await mkdtemp(join(os.tmpdir(), "managed-agent-runner-"));
const prompt = join(root, "TASK_PACKET.md");
const result = join(root, "RESULT.json");
const agentOutput = join(root, "agent-output.json");
const fakeOpenClaw = join(root, "openclaw-fake");
await writeFile(prompt, "# Task\n\nVerify the runner.\n");
await writeFile(fakeOpenClaw, "#!/bin/sh\nprintf '{\"result\":\"ok\"}\\n'\nexit \"${FAKE_EXIT_CODE:-0}\"\n");
await chmod(fakeOpenClaw, 0o755);

const runner = "/home/stanislav/.openclaw/workspace/agents/main/scripts/managed-agent-runner.mjs";
const args = [runner, "--prompt", prompt, "--result", result, "--agent-output", agentOutput,
  "--session-key", "agent:main:managed:test", "--timeout", "60"];
let code = await runProcess(process.execPath, args, { ...process.env, OPENCLAW_BIN: fakeOpenClaw });
assert.equal(code, 0);
assert.equal(JSON.parse(await readFile(result, "utf8")).terminalStatus, "SUCCEEDED");
assert.equal(JSON.parse(await readFile(agentOutput, "utf8")).exitCode, 0);

code = await runProcess(process.execPath, args, { ...process.env, OPENCLAW_BIN: fakeOpenClaw, FAKE_EXIT_CODE: "7" });
assert.equal(code, 7);
assert.equal(JSON.parse(await readFile(result, "utf8")).terminalStatus, "CRASHED");
assert.equal(JSON.parse(await readFile(agentOutput, "utf8")).exitCode, 7);
console.log("MANAGED_AGENT_RUNNER_OK");
