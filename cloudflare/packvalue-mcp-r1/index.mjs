import { McpServer, createMcpHandler } from "@modelcontextprotocol/server";
import * as z from "zod/v4";
import { normalizeOffer, compareOffers } from "../lsi-packvalue402-shadow-r1.mjs";

const VERSION = "1.1.0";

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

function r(n, digits = 6) {
  const p = 10 ** digits;
  return Math.round(Number(n) * p) / p;
}

function toolResult(value) {
  return { content: [{ type: "text", text: JSON.stringify(value) }] };
}

function toolError(error) {
  return {
    isError: true,
    content: [{ type: "text", text: JSON.stringify({ ok: false, error: String(error?.message || error).slice(0, 200) }) }],
  };
}

function createServer() {
  const server = new McpServer({ name: "PackValue Tools", version: VERSION });

  server.registerTool(
    "normalize_pack_value",
    {
      title: "Normalize pack value",
      description: "Normalize a product pack such as 6x330 ml or 3x200 g into comparable quantity and effective unit price. Deterministic; no LLM is used for the calculation.",
      inputSchema: offerSchema,
    },
    async (input) => {
      try { return toolResult({ ok: true, result: normalizeOffer(input) }); }
      catch (error) { return toolError(error); }
    },
  );

  server.registerTool(
    "compare_pack_values",
    {
      title: "Compare pack values",
      description: "Compare 2 to 25 shopping or procurement offers with compatible dimensions and currency, including shipping, tax, discount, yield and dilution adjustments.",
      inputSchema: z.object({ offers: z.array(offerSchema).min(2).max(25) }),
    },
    async ({ offers }) => {
      try { return toolResult({ ok: true, result: compareOffers(offers) }); }
      catch (error) { return toolError(error); }
    },
  );

  server.registerTool(
    "calculate_real_discount",
    {
      title: "Calculate real discount",
      description: "Calculate absolute savings and effective discount percentage from original and final prices.",
      inputSchema: z.object({
        original_price: z.number().gt(0),
        final_price: z.number().min(0),
        currency: z.string().max(12).optional().default("USD"),
      }),
    },
    async ({ original_price, final_price, currency }) => {
      try {
        if (final_price > original_price) throw new Error("final_price_above_original");
        const savings = original_price - final_price;
        return toolResult({ ok: true, result: {
          currency,
          original_price: r(original_price),
          final_price: r(final_price),
          savings: r(savings),
          discount_pct: r((savings / original_price) * 100),
        }});
      } catch (error) { return toolError(error); }
    },
  );

  server.registerTool(
    "calculate_delivered_unit_cost",
    {
      title: "Calculate delivered unit cost",
      description: "Calculate delivered cost per unit including shipping, tax and explicit discount.",
      inputSchema: z.object({
        item_price: z.number().min(0),
        quantity: z.number().int().gt(0).max(1000000),
        shipping: z.number().min(0).optional().default(0),
        tax: z.number().min(0).optional().default(0),
        discount: z.number().min(0).optional().default(0),
        currency: z.string().max(12).optional().default("USD"),
      }),
    },
    async ({ item_price, quantity, shipping, tax, discount, currency }) => {
      try {
        const subtotal = item_price * quantity;
        const total = subtotal + shipping + tax - discount;
        if (total < 0) throw new Error("discount_exceeds_total_cost");
        return toolResult({ ok: true, result: {
          currency,
          quantity,
          merchandise_subtotal: r(subtotal),
          shipping: r(shipping),
          tax: r(tax),
          discount: r(discount),
          delivered_total: r(total),
          delivered_unit_cost: r(total / quantity),
        }});
      } catch (error) { return toolError(error); }
    },
  );

  server.registerTool(
    "calculate_dilution_value",
    {
      title: "Calculate dilution value",
      description: "Calculate prepared yield and effective cost after diluting a concentrate with added parts of water or another zero-cost diluent.",
      inputSchema: z.object({
        concentrate_volume_l: z.number().gt(0),
        concentrate_price: z.number().min(0),
        added_parts_per_concentrate_part: z.number().min(0).max(1000),
        currency: z.string().max(12).optional().default("USD"),
      }),
    },
    async ({ concentrate_volume_l, concentrate_price, added_parts_per_concentrate_part, currency }) => {
      try {
        const factor = 1 + added_parts_per_concentrate_part;
        const prepared = concentrate_volume_l * factor;
        return toolResult({ ok: true, result: {
          currency,
          dilution_factor: r(factor),
          concentrate_volume_l: r(concentrate_volume_l),
          prepared_volume_l: r(prepared),
          concentrate_price: r(concentrate_price),
          effective_cost_per_prepared_l: r(concentrate_price / prepared),
        }});
      } catch (error) { return toolError(error); }
    },
  );

  server.registerTool(
    "calculate_buy_x_pay_y",
    {
      title: "Calculate buy X pay Y promotion",
      description: "Calculate total paid, effective unit price and discount for buy-X-pay-Y or take-X-pay-Y promotions.",
      inputSchema: z.object({
        take_units: z.number().int().gt(0).max(1000000),
        pay_units: z.number().int().min(0).max(1000000),
        regular_unit_price: z.number().min(0),
        currency: z.string().max(12).optional().default("USD"),
      }),
    },
    async ({ take_units, pay_units, regular_unit_price, currency }) => {
      try {
        if (pay_units > take_units) throw new Error("pay_units_above_take_units");
        const regularTotal = take_units * regular_unit_price;
        const paidTotal = pay_units * regular_unit_price;
        const savings = regularTotal - paidTotal;
        return toolResult({ ok: true, result: {
          currency,
          take_units,
          pay_units,
          regular_unit_price: r(regular_unit_price),
          regular_total: r(regularTotal),
          paid_total: r(paidTotal),
          savings: r(savings),
          effective_unit_price: r(paidTotal / take_units),
          effective_discount_pct: regularTotal > 0 ? r((savings / regularTotal) * 100) : 0,
        }});
      } catch (error) { return toolError(error); }
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
        tool_count: 6,
      }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
    }
    return mcp.fetch(request, env, ctx);
  },
};
