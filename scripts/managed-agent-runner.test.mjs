import assert from "node:assert/strict";
import { chmod, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import os from "node:os";
import { createHash, generateKeyPairSync, verify } from "node:crypto";
import { closeSync, openSync } from "node:fs";
import { validateManagedOutcome } from "./managed-outcome-contract.mjs";
const PLACEHOLDER_HASH = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const TEST_HASH1 = createHash("sha256").update("package ok").digest("hex");
const TEST_HASH2 = createHash("sha256").update("gate ok").digest("hex");

async function runProcess(command, args, env) {
  const fd = env.TEST_CAP_PATH ? openSync(env.TEST_CAP_PATH, "r") : null;
  if (fd !== null) { env = { ...env, MANAGED_TERMINAL_FD: "3", MANAGED_RUN_NONCE: env.TEST_RUN_NONCE || "0123456789abcdef0123456789abcdef" }; delete env.TEST_CAP_PATH; }
  const child = spawn(command, args, { env, stdio: fd === null ? "inherit" : ["inherit", "inherit", "inherit", fd] });
  if (fd !== null) closeSync(fd);
  return await new Promise((resolve, reject) => {
    child.on("error", reject); child.on("exit", code => resolve(code));
  });
}

const passed = (status = "SUCCEEDED") => ({ schemaVersion: 1, status, summary: "done",
  objectiveComplete: status === "SUCCEEDED",
  packages: [{ id: "P1", title: "work", status: status === "SUCCEEDED" ? "PASSED" : "RUNNING", evidence: status === "SUCCEEDED" ? [{ kind: "file", path: "__EVIDENCE1__", sha256: TEST_HASH1 }] : [] },
    { id: "P2", title: "external step", status: status === "SUCCEEDED" ? "PASSED" : "PENDING", evidence: status === "SUCCEEDED" ? [{ kind: "file", path: "__EVIDENCE3__", sha256: PLACEHOLDER_HASH }] : [] }],
  gates: [{ id: "G1", title: "check", status: status === "SUCCEEDED" ? "PASSED" : "PENDING", evidence: status === "SUCCEEDED" ? [{ kind: "file", path: "__EVIDENCE2__", sha256: TEST_HASH2 }] : [] }], blocker: null });
const blocked = { ...passed("CONTINUE"), status: "BLOCKED", summary: "needs owner", blocker: {
  external: true, reason: "credential unavailable", evidence: [{ kind: "file", path: "__EVIDENCE__", sha256: PLACEHOLDER_HASH }], ownerAction: "provide credential" } };
blocked.packages = [{ ...passed().packages[0] }, { id: "P2", title: "external step", status: "BLOCKED", evidence: [] }];
blocked.gates = [{ ...passed().gates[0] }];

assert.equal(validateManagedOutcome(passed()).valid, true);
assert.equal(validateManagedOutcome({ ...passed(), objectiveComplete: false }).valid, false);
assert.equal(validateManagedOutcome({ ...blocked, blocker: null }).valid, false);
assert.equal(validateManagedOutcome({ ...blocked, blocker: { ...blocked.blocker, external: false } }).valid, false);
assert.equal(validateManagedOutcome({ ...blocked, packages: [{ ...blocked.packages[0], status: "PENDING" }] }).valid, false);
assert.equal(validateManagedOutcome({ ...blocked, packages: [{ ...blocked.packages[0], status: "FAILED" }] }).valid, false);
assert.equal(validateManagedOutcome({ ...blocked, gates: [{ ...blocked.gates[0], status: "FAILED" }] }).valid, false);
assert.equal(validateManagedOutcome({ ...passed("CONTINUE"), status: "FAILED" }).valid, false);
assert.equal(validateManagedOutcome({ ...passed(), gates: [{ id: "G1", title: "check", status: "PENDING" }] }).valid, false);

const root = await mkdtemp(join(os.tmpdir(), "managed-agent-runner-"));
const prompt = join(root, "TASK_PACKET.md"), result = join(root, "RESULT.json");
const outcome = join(root, "MANAGED_OUTCOME.json"), agentOutput = join(root, "agent-output.json");
const counter = join(root, "counter"), fakeOpenClaw = join(root, "openclaw-fake.mjs");
const capability = join(root, "capability");
const { privateKey, publicKey } = generateKeyPairSync("ed25519");
await writeFile(capability, privateKey.export({ format: "der", type: "pkcs8" }));
await writeFile(prompt, "# Task\n\nVerify the runner.\n");
const contextPath = join(root, "AGENTS.md");
await writeFile(contextPath, "trusted test instructions\n");
const evidence1 = join(root, "package-proof.txt"), evidence2 = join(root, "gate-proof.txt"), evidence3 = join(root, "blocker-proof.txt");
const hash1 = createHash("sha256").update("package ok").digest("hex"), hash2 = createHash("sha256").update("gate ok").digest("hex");
await writeFile(fakeOpenClaw, `#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFileSync, unlinkSync, utimesSync, writeFileSync } from "node:fs";
const message=process.argv[process.argv.indexOf("--message")+1];
if(process.env.MANAGED_TERMINAL_FD)process.exit(97);try{readFileSync(3);process.exit(98)}catch{}
if(message.includes("Independent planning")){if(process.env.FAKE_PLAN_MISSING==="1")process.exit(0);const p=message.match(/write (.+) as JSON/)[1];const t=message.match(/"planToken":"([^"]+)"/)[1];writeFileSync(p,JSON.stringify({schemaVersion:1,planToken:t,packages:[{id:"P1",title:"work"},{id:"P2",title:"external step"}],gates:[{id:process.env.FAKE_DUP_PLAN==="1"?"P1":"G1",title:"check"}]}));if(process.env.FAKE_TAMPER_SNAPSHOT==="1")writeFileSync(process.env.FAKE_SNAPSHOT_PATH,"narrowed");process.exit(0)}
if(message.includes("Independently review whether the plan")){const p=message.match(/write (.+) as JSON/)[1];const t=message.match(/"reviewToken":"([^"]+)"/)[1];writeFileSync(p,JSON.stringify({reviewToken:t,verdict:process.env.FAKE_PLAN_REVIEW||"PASS",reason:"complete"}));process.exit(0)}
if(message.includes("Independent terminal review")){const p=message.match(/Write (.+) atomically as JSON/)[1];const t=message.match(/"reviewToken":"([^"]+)"/)[1];const b=message.match(/"bindingToken":"([^"]+)"/)[1];const claims=JSON.parse(message.match(/"reviewedClaims":(\\[[^\\]]*\\])/)[1]);const verdict=p.endsWith(".second")?(process.env.FAKE_SECOND_REVIEW_VERDICT||process.env.FAKE_REVIEW_VERDICT||"PASS"):(process.env.FAKE_REVIEW_VERDICT||"PASS");writeFileSync(p,JSON.stringify({reviewToken:t,bindingToken:b,reviewedClaims:claims,verdict,reason:"verified evidence"}));process.exit(0)}
const path=message.match(/atomically write (.+) as JSON/)[1];
const sliceToken=message.match(/"sliceToken":"([^"]+)"/)[1];
const runToken=message.match(/"runToken":"([^"]+)"/)[1];
let n=0;try{n=Number(readFileSync(process.env.FAKE_COUNTER,"utf8"))}catch{}
const outcomes=JSON.parse(process.env.FAKE_OUTCOMES);const value=outcomes[Math.min(n,outcomes.length-1)];
const proof1=process.env.FAKE_NO_WRITE==="1"?readFileSync(process.env.FAKE_EVIDENCE1,"utf8"):"package ok\\n"+(process.env.FAKE_OMIT_TOKEN==="1"?"":runToken);const proof2=process.env.FAKE_NO_WRITE==="1"?readFileSync(process.env.FAKE_EVIDENCE2,"utf8"):"gate ok\\n"+runToken;const proof3="external blocker observed\\n"+runToken;
if(process.env.FAKE_NO_WRITE!=="1"){writeFileSync(process.env.FAKE_EVIDENCE1,proof1);writeFileSync(process.env.FAKE_EVIDENCE2,proof2);writeFileSync(process.env.FAKE_EVIDENCE3,proof3)}
if(process.env.FAKE_OLD_MTIME==="1")for(const p of [process.env.FAKE_EVIDENCE1,process.env.FAKE_EVIDENCE2])utimesSync(p,new Date(0),new Date(0));
for(const group of [value.packages||[],value.gates||[]])for(const claim of group)for(const evidence of claim.evidence||[]){evidence.runToken=runToken;if(process.env.FAKE_KEEP_HASH!=="1"&&evidence.path===process.env.FAKE_EVIDENCE1)evidence.sha256=createHash("sha256").update(proof1).digest("hex");if(process.env.FAKE_KEEP_HASH!=="1"&&evidence.path===process.env.FAKE_EVIDENCE2)evidence.sha256=createHash("sha256").update(proof2).digest("hex");if(process.env.FAKE_KEEP_HASH!=="1"&&evidence.path===process.env.FAKE_EVIDENCE3)evidence.sha256=createHash("sha256").update(proof3).digest("hex")}
for(const evidence of value.blocker?.evidence||[]){evidence.runToken=runToken;if(evidence.path===process.env.FAKE_EVIDENCE3)evidence.sha256=createHash("sha256").update(proof3).digest("hex")}
value.sliceToken=process.env.FAKE_BAD_SLICE_TOKEN==="1"?"stale":sliceToken;writeFileSync(process.env.FAKE_COUNTER,String(n+1));
if(process.env.FAKE_BAD_JSON==="1")writeFileSync(path,"{");else if(process.env.FAKE_SKIP_OUTCOME!=="1")writeFileSync(path,JSON.stringify(value));
if(process.env.FAKE_TAMPER_CONTEXT_EXECUTION==="1")writeFileSync(process.env.FAKE_CONTEXT_PATH,"attacker instructions");
if(process.env.FAKE_DELETE_PLAN==="1"){const plan=message.match(/locked by an independent planner at (.+)\. Preserve/)[1];unlinkSync(plan)}
process.exit(Number(process.env.FAKE_EXIT_CODE||0));
`);
await chmod(fakeOpenClaw, 0o755);
const runner = join(fileURLToPath(new URL(".", import.meta.url)), "managed-agent-runner.mjs");
const args = [runner,
  "--prompt", prompt, "--result", result, "--agent-output", agentOutput, "--outcome", outcome,
  "--session-key", "agent:main:managed:test", "--timeout", "240", "--thinking", "high"];
async function scenario(outcomes, expectedCode, expectedStatus, extra = {}) {
  await Promise.all([result, outcome, `${outcome}.locked-plan.json`, agentOutput, counter, evidence1, evidence2, evidence3].map(path => rm(path, { force: true, recursive: true })));
  if (extra.MAKE_AGENT_OUTPUT_DIR === "1") await mkdir(agentOutput);
  if (extra.FAKE_STALE === "1") { await writeFile(evidence1, "stale package"); await writeFile(evidence2, "stale gate"); extra = { ...extra, FAKE_NO_WRITE: "1" }; }
  const code = await runProcess(process.execPath, args, { ...process.env, OPENCLAW_BIN: fakeOpenClaw,
    TEST_CAP_PATH: capability,
    MANAGED_RUNNER_TEST: "1",
    FAKE_SNAPSHOT_PATH: `${prompt}.owner-task.txt`,
    FAKE_CONTEXT_PATH: contextPath,
    MANAGED_WORKSPACE_ROOT: root,
    FAKE_COUNTER: counter, FAKE_EVIDENCE1: evidence1, FAKE_EVIDENCE2: evidence2, FAKE_EVIDENCE3: evidence3,
    FAKE_OUTCOMES: JSON.stringify(outcomes).replaceAll("__EVIDENCE__", evidence3).replaceAll(PLACEHOLDER_HASH, hash1).replaceAll("__EVIDENCE1__", evidence1).replaceAll("__EVIDENCE2__", evidence2).replaceAll("__EVIDENCE3__", evidence3).replaceAll("__HASH1__", hash1).replaceAll("__HASH2__", hash2), MANAGED_MAX_SLICES: "3", ...extra });
  assert.equal(code, expectedCode);
  const terminalResult = JSON.parse(await readFile(result, "utf8"));
  assert.equal(terminalResult.terminalStatus, expectedStatus);
  assert.equal(typeof terminalResult.terminalSignature, "string");
  assert.equal(terminalResult.runNonce, "0123456789abcdef0123456789abcdef");
  const signedPayload = JSON.stringify([terminalResult.terminalStatus, terminalResult.contractValidated, terminalResult.exitCode, terminalResult.runNonce,
    terminalResult.taskDigest ?? null, terminalResult.planDigest ?? null, terminalResult.outcomeDigest ?? null,
    terminalResult.finishedAt ?? null, terminalResult.summary ?? null, terminalResult.slices ?? null,
    terminalResult.outcomePath ?? null, terminalResult.agentOutputPath ?? null, terminalResult.independentReviewPaths ?? null]);
  assert.equal(verify(null, Buffer.from(signedPayload), publicKey, Buffer.from(terminalResult.terminalSignature, "base64")), true);
  let agent = null;
  try { agent = JSON.parse(await readFile(agentOutput, "utf8")); } catch {}
  return { ...(agent || { attempts: [] }), terminalResult };
}

await scenario([passed("CONTINUE"), passed()], 0, "SUCCEEDED");
const continued = await scenario([passed("CONTINUE"), passed()], 0, "SUCCEEDED");
assert.equal(continued.attempts.length, 2);
await scenario([{ ...passed(), objectiveComplete: false }], 5, "FAILED");
const partialBlocked = await scenario([{ ...passed("CONTINUE"), status: "PARTIAL_BLOCKED" }], 5, "FAILED");
assert.match(partialBlocked.attempts[0].validationErrors.join(" "), /status/i);
const invalidBlockerContinued = await scenario([passed("CONTINUE"), { ...blocked, blocker: null }, passed()], 0, "SUCCEEDED");
assert.equal(invalidBlockerContinued.attempts.length, 3);
await scenario([passed("CONTINUE"), blocked], 4, "BLOCKED");
const crashed = await scenario([passed("CONTINUE")], 5, "FAILED", { FAKE_EXIT_CODE: "7" });
assert.equal(crashed.attempts.length, 3); assert.equal(crashed.attempts.every(item => item.exitCode === 7), true);
await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { FAKE_REVIEW_VERDICT: "FAIL" });
await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { FAKE_SECOND_REVIEW_VERDICT: "FAIL" });
const reused = passed(); reused.gates[0].evidence = [{ ...reused.packages[0].evidence[0] }];
await scenario([passed("CONTINUE"), reused], 5, "FAILED");
const wrongHash = passed(); wrongHash.packages[0].evidence[0].sha256 = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
await scenario([passed("CONTINUE"), wrongHash], 5, "FAILED", { FAKE_KEEP_HASH: "1" });
const narrowed = passed(); narrowed.packages[0].title = "narrowed";
await scenario([passed("CONTINUE"), narrowed], 5, "FAILED");
const removed = passed(); removed.packages = [];
await scenario([passed("CONTINUE"), removed], 5, "FAILED");
await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { FAKE_PLAN_REVIEW: "FAIL" });
const outside = passed(); outside.packages[0].evidence[0] = { kind: "file", path: "/etc/hostname", sha256: createHash("sha256").update(await readFile("/etc/hostname")).digest("hex") };
await scenario([passed("CONTINUE"), outside], 5, "FAILED");
const forbidden = passed(); forbidden.packages[0].evidence[0] = { kind: "file", path: prompt, sha256: createHash("sha256").update(await readFile(prompt)).digest("hex") };
await scenario([passed("CONTINUE"), forbidden], 5, "FAILED");
await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { FAKE_DELETE_PLAN: "1" });
const missingOutcome = await scenario([passed("CONTINUE")], 5, "FAILED", { FAKE_SKIP_OUTCOME: "1" });
assert.match(missingOutcome.attempts[0].validationErrors.join(" "), /outcome|sliceToken/i);
const malformedOutcome = await scenario([passed("CONTINUE")], 5, "FAILED", { FAKE_BAD_JSON: "1" });
assert.match(malformedOutcome.attempts[0].validationErrors.join(" "), /outcome|sliceToken/i);
await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { FAKE_BAD_SLICE_TOKEN: "1" });
await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { FAKE_OMIT_TOKEN: "1" });
await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { FAKE_OLD_MTIME: "1" });
const missingPlan = await scenario([passed("CONTINUE")], 5, "FAILED", { FAKE_PLAN_MISSING: "1" });
assert.equal(missingPlan.terminalResult.slices, 0); assert.match(missingPlan.terminalResult.summary, /planning/i);
const tamperedSnapshot = await scenario([passed("CONTINUE")], 5, "FAILED", { FAKE_TAMPER_SNAPSHOT: "1" });
assert.equal(tamperedSnapshot.terminalResult.slices, 0); assert.match(tamperedSnapshot.terminalResult.summary, /planning/i);
const duplicatePlan = await scenario([passed("CONTINUE")], 5, "FAILED", { FAKE_DUP_PLAN: "1" });
assert.equal(duplicatePlan.terminalResult.slices, 0); assert.match(duplicatePlan.terminalResult.summary, /planning/i);
const boundedContinue = await scenario([passed("CONTINUE")], 5, "FAILED");
assert.equal(boundedContinue.attempts.length, 3);
const firstSliceTerminal = await scenario([passed(), passed()], 0, "SUCCEEDED");
assert.match(firstSliceTerminal.attempts[0].validationErrors.join(" "), /slice 1 must/i);
const contextTamper = await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { FAKE_TAMPER_CONTEXT_EXECUTION: "1" });
assert.match(contextTamper.terminalResult.summary, /did not reach/i);
await scenario([passed("CONTINUE"), passed()], 5, "FAILED", { MAKE_AGENT_OUTPUT_DIR: "1" });
console.log("MANAGED_AGENT_RUNNER_OK");
