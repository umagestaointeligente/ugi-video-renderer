import { McpServer, createMcpHandler } from "@modelcontextprotocol/server";
import * as z from "zod/v4";
import { normalizeOffer, compareOffers } from "../lsi-packvalue402-shadow-r1.mjs";

const VERSION = "1.0.0";

const offerSchema = z.object({
  label: z.string().max(160).optional(),
  text: z.string().min(1).max(300),
  price: z.number().min(0),
  currency: z.string().max(12).optional().default("USD"),
  shipping: z.number().min(0).optional().default(0),
  tax: z.number().min(0).optional().default(0),
  discount: z.number().min(0).optional().default(0),
  yield_pct: z.number().gt(0).max(100).optional().default(100),
  dilution: z.number().gt(0).optional().default(1),
});

function toolResult(value) {
  return {
    content: [{ type: "text", text: JSON.stringify(value) }],
  };
}

function toolError(error) {
  return {
    isError: true,
    content: [{ type: "text", text: JSON.stringify({ ok: false, error: String(error?.message || error).slice(0, 200) }) }],
  };
}

function createServer() {
  const server = new McpServer({
    name: "PackValue Tools",
    version: VERSION,
  });

  server.registerTool(
    "normalize_pack_value",
    {
      title: "Normalize pack value",
      description: "Normalize a product pack such as 6x330 ml or 3x200 g into comparable quantity and effective unit price. Deterministic; no LLM is used for the calculation.",
      inputSchema: offerSchema,
    },
    async (input) => {
      try {
        return toolResult({ ok: true, result: normalizeOffer(input) });
      } catch (error) {
        return toolError(error);
      }
    },
  );

  server.registerTool(
    "compare_pack_values",
    {
      title: "Compare pack values",
      description: "Compare 2 to 25 shopping or procurement offers with compatible dimensions and currency, including shipping, tax, discount, yield and dilution adjustments.",
      inputSchema: z.object({
        offers: z.array(offerSchema).min(2).max(25),
      }),
    },
    async ({ offers }) => {
      try {
        return toolResult({ ok: true, result: compareOffers(offers) });
      } catch (error) {
        return toolError(error);
      }
    },
  );

  return server;
}

const mcp = createMcpHandler(createServer, { legacy: "stateless" });

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return new Response(JSON.stringify({
        ok: true,
        service: "packvalue-mcp",
        version: VERSION,
        protocol: "MCP",
        transport: "streamable-http",
        endpoint: "/mcp",
        auth_required: false,
        payment_required: false,
        deterministic_core: true,
        pii_storage: false,
      }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
    }
    return mcp.fetch(request, env, ctx);
  },
};
