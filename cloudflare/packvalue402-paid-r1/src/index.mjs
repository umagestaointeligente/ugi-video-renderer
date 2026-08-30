import { Hono } from "hono";
import { paymentMiddleware } from "x402-hono";

const VERSION = "packvalue402-paid-r1-preprod-2026-08-30.1";
const TARGET_PRICE = "$0.001";
const ORIGIN = "https://lsi-packvalue402-shadow-r1.umagestaointeligente.workers.dev";
const DEFAULT_FACILITATOR = "https://x402.org/facilitator";

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
  return {
    enabled,
    pay_to_configured: payToConfigured,
    ready: enabled && payToConfigured,
    network: env.NETWORK || "base",
    target_price_usd: 0.001,
    facilitator: env.FACILITATOR_URL || DEFAULT_FACILITATOR,
    server_private_key_required: false,
    server_can_spend: false,
  };
}
async function proxy(c) {
  const src = new URL(c.req.url);
  const dst = new URL(src.pathname + src.search, ORIGIN);
  const headers = new Headers(c.req.raw.headers);
  headers.delete("host");
  const init = { method: c.req.method, headers, redirect: "manual" };
  if (!["GET", "HEAD"].includes(c.req.method)) init.body = await c.req.raw.clone().arrayBuffer();
  const request = new Request(dst, init);
  const r = c.env.ORIGIN_SERVICE
    ? await c.env.ORIGIN_SERVICE.fetch(request)
    : await fetch(request);
  const outHeaders = new Headers(r.headers);
  outHeaders.set("x-packvalue-gateway", VERSION);
  outHeaders.set("x-packvalue-origin-mode", c.env.ORIGIN_SERVICE ? "service-binding" : "public-fallback");
  return new Response(r.body, { status: r.status, statusText: r.statusText, headers: outHeaders });
}

app.get("/health", (c) => {
  const p = paymentState(c.env);
  return c.json({
    ok: true,
    service: "PackValue402 x402 Gateway",
    version: VERSION,
    mode: p.ready ? "PAYMENT_READY" : "PREPROD_DISABLED",
    origin_mode: c.env.ORIGIN_SERVICE ? "service-binding" : "public-fallback",
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
    origin_mode: c.env.ORIGIN_SERVICE ? "service-binding" : "public-fallback",
    payment: {
      protocol: "x402-v2",
      enabled: p.enabled,
      ready: p.ready,
      network: p.network,
      price_usd: 0.001,
      pay_to_configured: p.pay_to_configured,
      server_can_spend: false,
    },
    tools: [
      { name: "normalize_pack", method: "GET", path: "/v1/normalize", paid: false },
      { name: "compare_pack_value", method: "POST", path: "/v1/compare", paid: true, price_usd: 0.001 },
    ],
  });
});

app.get("/v1/normalize", proxy);

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
  const mw = paymentMiddleware(
    c.env.PAY_TO,
    {
      "/v1/compare": {
        price: TARGET_PRICE,
        network: p.network,
        config: { description: "Compare multipack and effective unit economics for 2-25 offers" },
      },
    },
    { url: p.facilitator },
  );
  return mw(c, next);
});

app.post("/v1/compare", proxy);
app.all("*", (c) => c.json({ ok: false, error: "not_found" }, 404));

export default app;
