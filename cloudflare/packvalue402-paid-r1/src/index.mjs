import { Hono } from "hono";
import { paymentMiddleware } from "@x402/hono";
import { x402ResourceServer, HTTPFacilitatorClient } from "@x402/core/server";
import { registerExactEvmScheme } from "@x402/evm/exact/server";
import { declareDiscoveryExtension, bazaarResourceServerExtension } from "@x402/extensions/bazaar";
import { normalizeOffer, compareOffers } from "../../lsi-packvalue402-shadow-r1.mjs";

const VERSION = "packvalue402-paid-r1-preprod-2026-08-30.5";
const TARGET_PRICE = "$0.001";
const DEFAULT_FACILITATOR = "https://facilitator.payai.network";
const DEFAULT_NETWORK = "eip155:8453";

const app = new Hono();

function paymentsEnabled(env) {
  return String(env.PAYMENTS_ENABLED || "").toLowerCase() === "true";
}
function validEvmAddress(v) {
  return /^0x[a-fA-F0-9]{40}$/.test(String(v || ""));
}
function paymentState(env) {
  const enabled = paymentsEnabled(env);
  const payToConfigured = validEvmAddress(env.PAY_TO);
  const network = env.NETWORK || DEFAULT_NETWORK;
  return {
    enabled,
    pay_to_configured: payToConfigured,
    ready: enabled && payToConfigured && network === DEFAULT_NETWORK,
    network,
    target_price_usd: 0.001,
    facilitator: env.FACILITATOR_URL || DEFAULT_FACILITATOR,
    protocol: "x402-v2",
    scheme: "exact",
    bazaar_declared: true,
    server_private_key_required: false,
    server_can_spend: false,
  };
}
function err(c, e) {
  return c.json({ ok: false, error: String(e?.message || e).slice(0, 200) }, 400);
}
function bazaarConfig() {
  return declareDiscoveryExtension({
    input: {
      offers: [
        { label: "6-pack", text: "6x330 ml", price: 5.94, currency: "USD" },
        { label: "2-liter", text: "2 L", price: 5.60, currency: "USD" },
      ],
    },
    inputSchema: {
      properties: {
        offers: {
          type: "array",
          minItems: 2,
          maxItems: 25,
          items: {
            type: "object",
            properties: {
              label: { type: "string", description: "Optional offer label" },
              text: { type: "string", description: "Pack expression such as 6x330 ml or 2 kg" },
              price: { type: "number", minimum: 0 },
              currency: { type: "string", description: "ISO-style currency code; all offers must match" },
              shipping: { type: "number", minimum: 0 },
              tax: { type: "number", minimum: 0 },
              discount: { type: "number", minimum: 0 },
              yield_pct: { type: "number", exclusiveMinimum: 0, maximum: 100 },
              dilution: { type: "number", exclusiveMinimum: 0 },
            },
            required: ["text", "price"],
          },
        },
      },
      required: ["offers"],
    },
    bodyType: "json",
    output: {
      example: {
        winner: "2-liter",
        currency: "USD",
        dimension: "volume",
        display_basis: "L",
        saving_vs_most_expensive_pct: 6.667,
      },
    },
  });
}
function buildPaymentMiddleware(env) {
  const p = paymentState(env);
  const facilitatorClient = new HTTPFacilitatorClient({ url: p.facilitator });
  const resourceServer = new x402ResourceServer(facilitatorClient);
  registerExactEvmScheme(resourceServer);
  resourceServer.registerExtension(bazaarResourceServerExtension);
  return paymentMiddleware(
    {
      "POST /v1/compare": {
        accepts: {
          scheme: "exact",
          network: p.network,
          payTo: env.PAY_TO,
          price: TARGET_PRICE,
        },
        description: "Compare multipack and effective unit economics for 2-25 shopping or procurement offers",
        mimeType: "application/json",
        serviceName: "PackValue402",
        tags: ["shopping", "procurement", "unit-price", "comparison"],
        extensions: {
          ...bazaarConfig(),
        },
      },
    },
    resourceServer,
  );
}

app.get("/health", (c) => {
  const p = paymentState(c.env);
  return c.json({
    ok: true,
    service: "PackValue402 x402 Gateway",
    version: VERSION,
    mode: p.ready ? "PAYMENT_READY" : "PREPROD_DISABLED",
    core_mode: "shared-proven-deterministic-core",
    payment: p,
    production_actions: false,
    money_movement_from_server: false,
  });
});

app.get("/.well-known/agent.json", (c) => {
  const p = paymentState(c.env);
  return c.json({
    name: "PackValue402",
    description: "Agent-native multipack and unit-economics normalization and comparison.",
    version: VERSION,
    mode: p.ready ? "PAYMENT_READY" : "PREPROD_DISABLED",
    core_mode: "shared-proven-deterministic-core",
    distribution: { bazaar_declared: true, bazaar_indexed: false, indexing_requires_valid_settlement: true },
    payment: {
      protocol: p.protocol,
      scheme: p.scheme,
      enabled: p.enabled,
      ready: p.ready,
      network: p.network,
      price_usd: 0.001,
      pay_to_configured: p.pay_to_configured,
      facilitator: p.facilitator,
      server_can_spend: false,
    },
    tools: [
      { name: "normalize_pack", method: "GET", path: "/v1/normalize", paid: false },
      { name: "compare_pack_value", method: "POST", path: "/v1/compare", paid: true, price_usd: 0.001 },
    ],
  });
});

app.get("/v1/normalize", (c) => {
  try {
    const q = c.req.query();
    const result = normalizeOffer({
      text: q.text,
      price: q.price,
      shipping: q.shipping,
      tax: q.tax,
      discount: q.discount,
      yield_pct: q.yield_pct || 100,
      dilution: q.dilution || 1,
      currency: q.currency || "USD",
    });
    return c.json({ ok: true, mode: paymentState(c.env).ready ? "PAYMENT_READY" : "PREPROD_DISABLED", result });
  } catch (e) {
    return err(c, e);
  }
});

app.use("/v1/compare", async (c, next) => {
  const p = paymentState(c.env);
  if (!p.enabled) {
    return c.json({
      ok: false,
      error: "payments_not_activated",
      mode: "PREPROD_DISABLED",
      wallet_bound: false,
      money_movement: false,
    }, 503);
  }
  if (!p.pay_to_configured) {
    return c.json({
      ok: false,
      error: "payment_recipient_not_configured",
      mode: "FAIL_CLOSED",
      money_movement: false,
    }, 503);
  }
  if (p.network !== DEFAULT_NETWORK) {
    return c.json({
      ok: false,
      error: "unsupported_production_network",
      mode: "FAIL_CLOSED",
      money_movement: false,
    }, 503);
  }
  return buildPaymentMiddleware(c.env)(c, next);
});

app.post("/v1/compare", async (c) => {
  try {
    const body = await c.req.json();
    const result = compareOffers(body.offers);
    return c.json({ ok: true, mode: "PAYMENT_READY", target_price_usd: 0.001, result });
  } catch (e) {
    return err(c, e);
  }
});

app.all("*", (c) => c.json({ ok: false, error: "not_found" }, 404));

export default app;
