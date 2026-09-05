import { readdir } from "node:fs/promises";

export async function readExistingDirectory(directory) {
  try { return await readdir(directory, { withFileTypes: true }); }
  catch (error) {
    if (error?.code === "ENOENT") return [];
    throw error;
  }
}
