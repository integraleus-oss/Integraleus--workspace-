import { describe, expect, it } from "vitest";
import entry from "./index.js";

describe("orchestrator-auth-boundary", () => {
  it("declares the bounded plugin identity", () => {
    expect(entry.id).toBe("orchestrator-auth-boundary");
  });
});
