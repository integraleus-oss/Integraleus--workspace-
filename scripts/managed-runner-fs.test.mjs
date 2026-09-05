import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import { join } from "node:path";
import { readExistingDirectory } from "./managed-runner-fs.mjs";

const directory = await mkdtemp(join(os.tmpdir(), "managed-runner-walk-"));
await rm(directory, { recursive: true, force: true });
assert.deepEqual(await readExistingDirectory(directory), []);

await assert.rejects(
  readExistingDirectory("/proc/1/mem"),
  error => error?.code !== "ENOENT",
);

console.log("MANAGED_RUNNER_FS_OK");
