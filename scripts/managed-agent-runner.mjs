#!/usr/bin/env node
import { spawn } from "node:child_process";
import { readFile, rename, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { randomUUID } from "node:crypto";

function argumentsMap(argv) {
  const result = {};
  for (let i = 2; i < argv.length; i += 2) result[argv[i].replace(/^--/, "")] = argv[i + 1];
  return result;
}

async function atomicJson(path, value) {
  const temporary = resolve(dirname(path), `.${randomUUID()}.tmp`);
  await writeFile(temporary, JSON.stringify(value, null, 2) + "\n");
  await rename(temporary, path);
}

const args = argumentsMap(process.argv);
for (const required of ["prompt", "result", "agent-output", "session-key", "timeout"]) {
  if (!args[required]) throw new Error(`missing --${required}`);
}
const prompt = await readFile(args.prompt, "utf8");
const instruction = `${prompt}\n\nExecute this task to a verified terminal outcome. Read the referenced CONTEXT.json before deciding scope. Update the task evidence as work progresses. Do not send messages directly; the execution supervisor owns terminal delivery. End with a concise result including artifacts, checks, commit, and residual blockers.`;
const command = process.env.OPENCLAW_BIN || "/usr/bin/openclaw";
const child = spawn(command, ["agent", "--agent", "main", "--session-key", args["session-key"],
  "--message", instruction, "--timeout", args.timeout, "--json"], { stdio: ["ignore", "pipe", "pipe"] });
let stdout = "";
let stderr = "";
child.stdout.setEncoding("utf8"); child.stderr.setEncoding("utf8");
child.stdout.on("data", chunk => { stdout += chunk; });
child.stderr.on("data", chunk => { stderr += chunk; });
const exitCode = await new Promise((resolveExit, reject) => {
  child.on("error", reject); child.on("exit", code => resolveExit(code ?? 1));
});
await atomicJson(args["agent-output"], { exitCode, stdout, stderr });
await atomicJson(args.result, { terminalStatus: exitCode === 0 ? "SUCCEEDED" : "CRASHED",
  exitCode, finishedAt: new Date().toISOString(), agentOutputPath: args["agent-output"] });
process.exitCode = exitCode;
