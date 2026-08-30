import app from "./index.mjs";

const TRACKED = new Set([
  "/",
  "/preco-por-kg",
  "/preco-por-litro",
  "/preco-por-unidade",
  "/comparar-pacotes",
  "/desconto-real",
  "/leve-mais-pague-menos",
  "/rendimento-diluicao",
  "/custo-com-frete",
]);

function response(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-packvalue-telemetry": "aggregate-only",
    },
  });
}

function cleanPath(value) {
  const path = String(value || "").trim();
  return TRACKED.has(path) ? path : null;
}

export class TrafficCounter {
  constructor(state) {
    this.state = state;
  }

  async increment(path, kind) {
    const safePath = cleanPath(path);
    if (!safePath) return false;
    const safeKind = kind === "acceptance" ? "acceptance" : "production";
    const now = new Date().toISOString();
    const day = now.slice(0, 10);
    const storage = this.state.storage;
    const dayKey = `day:${safeKind}:${day}:${safePath}`;
    const routeKey = `route:${safeKind}:${safePath}`;
    const totalKey = `total:${safeKind}`;

    const [dayCount, routeCount, totalCount, firstSeen] = await Promise.all([
      storage.get(dayKey),
      storage.get(routeKey),
      storage.get(totalKey),
      storage.get(`first:${safeKind}`),
    ]);

    await storage.put({
      [dayKey]: Number(dayCount || 0) + 1,
      [routeKey]: Number(routeCount || 0) + 1,
      [totalKey]: Number(totalCount || 0) + 1,
      [`first:${safeKind}`]: firstSeen || now,
      [`last:${safeKind}`]: now,
    });
    return true;
  }

  async snapshot() {
    const storage = this.state.storage;
    const [all, prodTotal, acceptanceTotal, prodFirst, prodLast] = await Promise.all([
      storage.list({ prefix: "route:" }),
      storage.get("total:production"),
      storage.get("total:acceptance"),
      storage.get("first:production"),
      storage.get("last:production"),
    ]);
    const routes = {};
    for (const [key, value] of all.entries()) {
      const parts = key.split(":");
      if (parts[1] !== "production") continue;
      const path = parts.slice(2).join(":");
      routes[path] = Number(value || 0);
    }
    return {
      ok: true,
      schema_version: "1.0",
      metric: "aggregate_http_requests",
      production_requests: Number(prodTotal || 0),
      acceptance_probe_requests: Number(acceptanceTotal || 0),
      routes,
      first_production_request_at: prodFirst || null,
      last_production_request_at: prodLast || null,
      unique_users_measured: false,
      pii_stored: false,
      ip_stored: false,
      cookie_stored: false,
      user_agent_stored: false,
      referrer_stored: false,
      form_values_stored: false,
      note: "Counts include ordinary HTTP requests to public calculator pages and may include crawlers. They are not unique-user metrics.",
    };
  }

  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "POST" && url.pathname === "/hit") {
      const body = await request.json().catch(() => ({}));
      const ok = await this.increment(body.path, body.kind);
      return response({ ok });
    }
    if (request.method === "GET" && url.pathname === "/snapshot") {
      return response(await this.snapshot());
    }
    return response({ ok: false, error: "not_found" }, 404);
  }
}

async function counterStub(env) {
  if (!env.TRAFFIC) return null;
  const id = env.TRAFFIC.idFromName("packvalue-tools-global");
  return env.TRAFFIC.get(id);
}

async function recordRequest(request, env, ctx, path, kind) {
  const stub = await counterStub(env);
  if (!stub) return;
  const task = stub.fetch("https://traffic.internal/hit", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ path, kind }),
  }).then(() => undefined).catch(() => undefined);
  if (ctx?.waitUntil) ctx.waitUntil(task);
  else await task;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, "") || "/";

    if (request.method === "GET" && path === "/metrics") {
      const stub = await counterStub(env);
      if (!stub) return response({ ok: false, error: "telemetry_binding_missing" }, 503);
      return stub.fetch("https://traffic.internal/snapshot");
    }

    if (request.method === "GET" && TRACKED.has(path) && !url.searchParams.has("ts")) {
      const kind = url.searchParams.get("telemetry_probe") === "acceptance" ? "acceptance" : "production";
      await recordRequest(request, env, ctx, path, kind);
    }

    return app.fetch(request, env, ctx);
  },
};
