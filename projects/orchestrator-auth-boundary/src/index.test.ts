import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import entry from "./index.js";
import { testing } from "./index.js";

describe("orchestrator-auth-boundary", () => {
  it("declares the bounded plugin identity", () => {
    expect(entry.id).toBe("orchestrator-auth-boundary");
  });

  it("rejects packets outside the fixed task root", async () => {
    const dir = await mkdtemp(join(tmpdir(), "guard-plugin-"));
    const packet = join(dir, "packet.json");
    await writeFile(packet, "{}");
    try {
      await expect(testing.inspectPacket(packet)).rejects.toThrow("outside");
    } finally {
      await rm(dir, { recursive: true, force: true });
    }
  });

  it("purges expired inbound metadata", () => {
    testing.inboundBySession.set("expired", { sessionKey: "expired", accountId: "default",
      channelId: "telegram", chatId: "-1004417478336", topicId: "2922", messageId: "1",
      senderId: "109592643", timestamp: 1, content: "x", observedAt: 1 });
    testing.purge(1_000_000);
    expect(testing.inboundBySession.has("expired")).toBe(false);
  });
});
