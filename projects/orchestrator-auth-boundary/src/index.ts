import { createHash } from "node:crypto";
import { lstat, readFile, realpath } from "node:fs/promises";
import { createConnection } from "node:net";
import { resolve } from "node:path";
import { Type } from "typebox";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const PACKET_ROOT = "/home/stanislav/.openclaw/workspace/agents/main/state/tasks";
const GUARD_SOCKET = "/run/orchestrator-guard/guard.sock";
const OWNER_ID = "109592643";
const CHAT_ID = "-1004417478336";
const TOPIC_ID = "2922";
const TTL_MS = 120_000;

type Inbound = {
  sessionKey: string; accountId: string; channelId: string; chatId: string;
  topicId: string; messageId: string; senderId: string; timestamp: number; observedAt: number;
};

const inboundBySession = new Map<string, Inbound>();

function sha256(value: Buffer): string {
  return `sha256:${createHash("sha256").update(value).digest("hex")}`;
}

async function inspectPacket(input: string): Promise<{ path: string; digest: string }> {
  const requested = resolve(input);
  const root = await realpath(PACKET_ROOT);
  const stat = await lstat(requested);
  if (!stat.isFile() || stat.isSymbolicLink()) throw new Error("packet must be a regular non-symlink file");
  const canonical = await realpath(requested);
  if (!canonical.startsWith(`${root}/`)) throw new Error("packet is outside the approved task root");
  return { path: canonical, digest: sha256(await readFile(canonical)) };
}

function purge(now = Date.now()): void {
  for (const [key, inbound] of inboundBySession) if (inbound.observedAt + TTL_MS <= now) inboundBySession.delete(key);
}

function callGuard(request: Record<string, unknown>): Promise<Record<string, unknown>> {
  return new Promise((resolvePromise, reject) => {
    const socket = createConnection(GUARD_SOCKET);
    let data = "";
    const timer = setTimeout(() => socket.destroy(new Error("guard timeout")), 1_810_000);
    socket.setEncoding("utf8");
    socket.on("connect", () => socket.write(`${JSON.stringify(request)}\n`));
    socket.on("data", (chunk) => { data += chunk; if (data.length > 1_000_000) socket.destroy(new Error("guard response too large")); });
    socket.on("error", reject);
    socket.on("end", () => {
      clearTimeout(timer);
      try {
        const response = JSON.parse(data) as Record<string, unknown>;
        if (response.ok !== true) return reject(new Error(`guard rejected request: ${String(response.message ?? response.error)}`));
        resolvePromise(response);
      } catch (error) { reject(error); }
    });
  });
}

export const testing = { inboundBySession, inspectPacket, purge };

const plugin = definePluginEntry({
  id: "orchestrator-auth-boundary",
  name: "Orchestrator Auth Boundary",
  description: "Routes one fresh trusted owner turn to the root-owned foreground orchestrator guard.",
  register(api) {
    api.on("inbound_claim", (event, ctx) => {
      purge();
      const sessionKey = ctx.sessionKey ?? event.sessionKey;
      const senderId = ctx.senderId ?? event.senderId;
      const messageId = ctx.messageId ?? event.messageId;
      const conversation = ctx.conversationId ?? event.conversationId ?? "";
      const chatMatch = String(conversation).match(/(-100\d+)/);
      const topicId = String(event.threadId ?? "");
      if (!event.senderIsOwner || senderId !== OWNER_ID || !sessionKey || !messageId
          || chatMatch?.[1] !== CHAT_ID || topicId !== TOPIC_ID) return;
      const rawTimestamp = Number(event.timestamp ?? Date.now());
      inboundBySession.set(sessionKey, {
        sessionKey, accountId: event.accountId ?? ctx.accountId ?? "", channelId: ctx.channelId,
        chatId: CHAT_ID, topicId, messageId: String(messageId), senderId: String(senderId),
        timestamp: rawTimestamp > 10_000_000_000 ? Math.floor(rawTimestamp / 1000) : Math.floor(rawTimestamp),
        observedAt: Date.now(),
      });
    }, { priority: 100, timeoutMs: 1_000 });

    api.registerTool((ctx) => ({
      name: "orchestrator_run_guarded_pilot",
      label: "Run guarded orchestrator pilot",
      description: "Run one exact task packet through the root-owned foreground guard from the current owner message.",
      parameters: Type.Object({ packetPath: Type.String() }, { additionalProperties: false }),
      execute: async (_id, rawParams) => {
        purge();
        if (!ctx.senderIsOwner || ctx.requesterSenderId !== OWNER_ID || !ctx.sessionKey) throw new Error("trusted owner turn required");
        const inbound = inboundBySession.get(ctx.sessionKey);
        if (!inbound || inbound.senderId !== ctx.requesterSenderId) throw new Error("no fresh trusted inbound owner metadata");
        inboundBySession.delete(ctx.sessionKey);
        const packet = await inspectPacket(String((rawParams as { packetPath: string }).packetPath));
        const response = await callGuard({ action: "run_one", ...inbound, sessionKey: undefined,
          observedAt: undefined, packetPath: packet.path, packetDigest: packet.digest });
        return { content: [{ type: "text", text: JSON.stringify(response) }], details: response };
      },
    }), { name: "orchestrator_run_guarded_pilot" });
  },
});

export default plugin;
