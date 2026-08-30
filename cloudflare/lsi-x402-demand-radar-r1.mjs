const VERSION = "lsi-x402-demand-radar-r1.2-2026-08-30";
const RADAR_ID = "lsi-x402-demand-global-r1";
const API_BASE = "https://x402-list.com/api/v1/services";
const DEFAULT_CADENCE_MS = 60 * 60 * 1000;
const MIN_CADENCE_MS = 30 * 60 * 1000;
const MAX_CADENCE_MS = 24 * 60 * 60 * 1000;
const MAX_CYCLES = 168;
const DETAIL_SAMPLE_LIMIT = 40;
const DETAIL_CONCURRENCY = 8;
const BENCHMARK_SLUGS = [
  "nansen",
  "anyspend",
  "x402engine",
  "coinmarketcap",
  "openinterest",
  "gridpulse",
  "cyclepulse",
  "agent-web-reader-x402",
  "10x402",
  "sovereign-execution-engine",
];

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-lsi-version": VERSION,
    },
  });
}

function safeString(v, max = 4000) { return String(v ?? "").slice(0, max); }
function num(v, fallback = 0) { const n = Number(v); return Number.isFinite(n) ? n : fallback; }
function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }
function logScore(value, scale, cap) { if (!(value > 0)) return 0; return Math.min(cap, Math.log1p(value) * scale); }

function adminOk(request, env) {
  const expected = safeString(env.ADMIN_TOKEN, 512);
  if (!expected) return false;
  return (request.headers.get("authorization") || "") === `Bearer ${expected}`;
}

function normalizeShare(value) {
  const n = num(value, NaN);
  if (!Number.isFinite(n)) return null;
  if (n > 1 && n <= 100) return clamp(n / 100, 0, 1);
  return clamp(n, 0, 1);
}

function broadDemandScore(service) {
  const t = service?.assessment?.traction || {};
  if (t.status !== "measured") return 0;
  const buyers = num(t.unique_buyers_30d);
  const tx = num(t.tx_count_30d);
  const volume = num(t.volume_usd_30d);
  if (buyers <= 0 || tx <= 0) return 0;
  const repeatRate = tx / buyers;
  const topShare = normalizeShare(t.top_buyer_share_30d);
  const trend = num(t.trend_7d_vs_30d, 0);
  const price = num(service?.min_price_usd, num(service?.assessment?.economics?.price_usd, 0));
  const upstreamRisk = /search|scrap|crawl|video|image|llm|openai|anthropic|exa|serp|maps|geocod|weather/i.test(
    `${safeString(service?.name)} ${safeString(service?.description)} ${safeString(service?.category)}`
  );
  const buyersScore = logScore(buyers, 7.2, 34);
  const repeatScore = logScore(repeatRate, 5.5, 22);
  const concentrationScore = topShare === null ? 5 : (1 - topShare) * 20;
  const trendScore = clamp(trend * 4, -5, 10) + 5;
  const volumeScore = logScore(volume, 2.4, 9);
  const priceFitScore = price > 0 && price <= 0.05 ? 5 : price <= 0.25 ? 3 : 1;
  const upstreamPenalty = upstreamRisk ? 5 : 0;
  return Math.round(clamp(
    buyersScore + repeatScore + concentrationScore + trendScore + volumeScore + priceFitScore - upstreamPenalty,
    0, 100
  ) * 10) / 10;
}

function serviceView(service) {
  const t = service?.assessment?.traction || {};
  const buyers = num(t.unique_buyers_30d);
  const tx = num(t.tx_count_30d);
  const repeatRate = buyers > 0 ? tx / buyers : 0;
  const topShare = normalizeShare(t.top_buyer_share_30d);
  return {
    slug: safeString(service?.slug, 160),
    name: safeString(service?.name, 240),
    category: safeString(service?.category || "Other", 80),
    description: safeString(service?.description, 600),
    status: safeString(service?.status, 40),
    payment_ready: Boolean(service?.payment_ready),
    endpoint_count: num(service?.endpoint_count),
    min_price_usd: num(service?.min_price_usd, null),
    uptime_24h: num(service?.uptime_24h, null),
    traction_status: safeString(t.status, 80),
    volume_usd_30d: num(t.volume_usd_30d),
    tx_count_30d: tx,
    unique_buyers_30d: buyers,
    repeat_tx_per_buyer_30d: Math.round(repeatRate * 100) / 100,
    top_buyer_share_30d: topShare,
    trend_7d_vs_30d: num(t.trend_7d_vs_30d, null),
    shared_payout: Boolean(t.shared_payout),
    broad_demand_score: broadDemandScore(service),
    source_url: `https://x402-list.com/services/${encodeURIComponent(safeString(service?.slug, 160))}`,
  };
}

function categorizeOpportunity(agg) {
  const serviceCount = agg.services;
  const paidServices = agg.services_with_buyers;
  const buyerInstances = agg.service_buyer_instances;
  const settlements = agg.settlements_30d;
  const volume = agg.volume_usd_30d;
  const activeRatio = serviceCount > 0 ? paidServices / serviceCount : 0;
  const txPerPaidService = paidServices > 0 ? settlements / paidServices : 0;
  const buyerInstancesPerService = serviceCount > 0 ? buyerInstances / serviceCount : 0;
  let score = 0;
  score += logScore(buyerInstances, 5.5, 30);
  score += logScore(settlements, 2.7, 25);
  score += logScore(volume, 2.1, 15);
  score += clamp(activeRatio * 20, 0, 20);
  score += clamp(Math.log1p(txPerPaidService) * 2, 0, 10);
  if (serviceCount > 100) score -= 8;
  if (buyerInstancesPerService < 0.5) score -= 5;
  return Math.round(clamp(score, 0, 100) * 10) / 10;
}

async function fetchJson(url, label) {
  const response = await fetch(url, {
    headers: { accept: "application/json", "user-agent": "LSI-x402-Demand-Radar/1.2 (+public-market-research)" },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${label}_${response.status}:${text.slice(0, 240)}`);
  }
  return response.json();
}

async function fetchPage(page, perPage = 100) {
  const u = new URL(API_BASE);
  u.searchParams.set("status", "online");
  u.searchParams.set("per_page", String(perPage));
  u.searchParams.set("page", String(page));
  return fetchJson(u.toString(), "x402_list");
}

async function fetchServiceDetail(slug) {
  const payload = await fetchJson(`${API_BASE}/${encodeURIComponent(safeString(slug, 160))}`, "x402_detail");
  return payload?.data || null;
}

function discoveryCandidateScore(service) {
  const readyBoost = service?.payment_ready ? 120 : 0;
  const uptimeBoost = clamp(num(service?.uptime_24h, 0), 0, 100);
  const price = num(service?.min_price_usd, 999);
  const priceBoost = price > 0 && price <= 0.05 ? 50 : price <= 0.25 ? 25 : 0;
  const endpointBoost = Math.min(30, num(service?.endpoint_count, 0));
  return readyBoost + uptimeBoost + priceBoost + endpointBoost;
}

async function enrichWithMeasuredDetails(services, cycleCount = 0) {
  const bySlug = new Map(services.map((s) => [safeString(s?.slug, 160), s]));
  const benchmarkCandidates = BENCHMARK_SLUGS.map((slug) => bySlug.get(slug) || { slug }).filter(Boolean);
  const benchmarkSet = new Set(BENCHMARK_SLUGS);
  const discoveryPool = [...services]
    .filter((s) => safeString(s?.slug, 160) && !benchmarkSet.has(safeString(s?.slug, 160)))
    .sort((a, b) => discoveryCandidateScore(b) - discoveryCandidateScore(a));

  const discoverySlots = Math.max(0, DETAIL_SAMPLE_LIMIT - benchmarkCandidates.length);
  const offset = discoveryPool.length ? (cycleCount * Math.max(1, discoverySlots)) % discoveryPool.length : 0;
  const rotated = discoveryPool.length
    ? [...discoveryPool.slice(offset), ...discoveryPool.slice(0, offset)].slice(0, discoverySlots)
    : [];
  const candidates = [...benchmarkCandidates, ...rotated].slice(0, DETAIL_SAMPLE_LIMIT);

  const detailMap = new Map();
  let detailFailures = 0;
  for (let i = 0; i < candidates.length; i += DETAIL_CONCURRENCY) {
    const batch = candidates.slice(i, i + DETAIL_CONCURRENCY);
    const results = await Promise.all(batch.map(async (s) => {
      try { return { slug: s.slug, detail: await fetchServiceDetail(s.slug) }; }
      catch { return { slug: s.slug, detail: null }; }
    }));
    for (const item of results) {
      if (item.detail) detailMap.set(item.slug, item.detail);
      else detailFailures += 1;
    }
  }

  return {
    services: services.map((s) => detailMap.get(s.slug) || s),
    extra_benchmarks: [...detailMap.entries()]
      .filter(([slug]) => !bySlug.has(slug))
      .map(([, detail]) => detail),
    detail_requested: candidates.length,
    detail_succeeded: detailMap.size,
    detail_failed: detailFailures,
    benchmark_requested: benchmarkCandidates.length,
    discovery_requested: rotated.length,
    rotation_offset: offset,
  };
}

async function fetchAllServices(cycleCount = 0) {
  const first = await fetchPage(1, 100);
  const totalPages = clamp(num(first?.meta?.total_pages, 1), 1, 20);
  const all = [...(Array.isArray(first?.data) ? first.data : [])];
  for (let page = 2; page <= totalPages; page += 1) {
    const p = await fetchPage(page, 100);
    if (Array.isArray(p?.data)) all.push(...p.data);
  }
  const enrichment = await enrichWithMeasuredDetails(all, cycleCount);
  return {
    services: [...enrichment.services, ...enrichment.extra_benchmarks],
    meta: first?.meta || {},
    provenance: first?.provenance || {},
    enrichment: {
      strategy: "measured_benchmarks_plus_rotating_discovery",
      limit_per_cycle: DETAIL_SAMPLE_LIMIT,
      requested: enrichment.detail_requested,
      succeeded: enrichment.detail_succeeded,
      failed: enrichment.detail_failed,
      benchmark_requested: enrichment.benchmark_requested,
      discovery_requested: enrichment.discovery_requested,
      rotation_offset: enrichment.rotation_offset,
      daily_request_budget_note: "40 detail calls + catalog pages per hourly cycle remains below the public 2,000 reads/day threshold and Cloudflare Free subrequest ceiling",
    },
  };
}

function analyzeMarket(raw) {
  const serviceViews = raw.services.map(serviceView);
  const measured = serviceViews.filter((s) => s.traction_status === "measured");
  const activePaid = measured.filter((s) => s.unique_buyers_30d > 0 && s.tx_count_30d > 0);
  const topBroad = [...activePaid]
    .sort((a, b) => b.broad_demand_score - a.broad_demand_score || b.unique_buyers_30d - a.unique_buyers_30d)
    .slice(0, 30);

  const categoryMap = new Map();
  for (const s of serviceViews) {
    const key = s.category || "Other";
    if (!categoryMap.has(key)) categoryMap.set(key, {
      category: key, services: 0, measured_services: 0, services_with_buyers: 0,
      service_buyer_instances: 0, settlements_30d: 0, volume_usd_30d: 0, score_sum: 0,
    });
    const a = categoryMap.get(key);
    a.services += 1;
    if (s.traction_status === "measured") a.measured_services += 1;
    if (s.unique_buyers_30d > 0) a.services_with_buyers += 1;
    a.service_buyer_instances += s.unique_buyers_30d;
    a.settlements_30d += s.tx_count_30d;
    a.volume_usd_30d += s.volume_usd_30d;
    a.score_sum += s.broad_demand_score;
  }

  const categories = [...categoryMap.values()].map((a) => ({
    ...a,
    volume_usd_30d: Math.round(a.volume_usd_30d * 1e6) / 1e6,
    avg_broad_demand_score: Math.round((a.score_sum / Math.max(1, a.services)) * 10) / 10,
    opportunity_score: categorizeOpportunity(a),
    buyer_metric_note: "service_buyer_instances sums per-service buyer counts; it is NOT deduplicated unique ecosystem users",
  })).sort((a, b) => b.opportunity_score - a.opportunity_score);

  return {
    generated_at: new Date().toISOString(),
    market: {
      online_services_seen: serviceViews.length,
      detail_enrichment: raw.enrichment,
      measured_services: measured.length,
      services_with_30d_buyers: activePaid.length,
      source_meta: raw.meta,
      provenance: raw.provenance,
      attribution: "Data: x402-list.com (CC BY 4.0)",
    },
    scoring: {
      goal: "favor distributed repeat demand over headline volume",
      signals: ["unique_buyers_30d", "tx_per_buyer", "top_buyer_share_30d", "trend_7d_vs_30d", "volume_usd_30d", "price_fit"],
      caveat: "benchmark services anchor measurement but do not determine product choice; rotating discovery is used to find white space",
    },
    top_broad_demand: topBroad,
    broad_benchmarks: topBroad.filter((s) => s.top_buyer_share_30d === null || s.top_buyer_share_30d < 0.5).slice(0, 15),
    concentration_warnings: topBroad.filter((s) => s.top_buyer_share_30d !== null && s.top_buyer_share_30d >= 0.8).slice(0, 15),
    category_opportunity: categories,
    monetization_state: {
      paid_routes_active: false,
      wallet_bound: false,
      money_movement: false,
      next_gate: "SELECT_PRODUCT_FROM_DEMAND_AND_WHITE_SPACE_THEN_BIND_SECURE_RECEIVE_ADDRESS",
    },
  };
}

function newState(body = {}) {
  const monetaryBudget = num(body.monetary_budget, 0);
  if (monetaryBudget !== 0) throw new Error("zero_cost_only");
  const cadenceMs = clamp(num(body.cadence_ms, DEFAULT_CADENCE_MS), MIN_CADENCE_MS, MAX_CADENCE_MS);
  const maxCycles = clamp(num(body.max_cycles, MAX_CYCLES), 1, MAX_CYCLES);
  const now = new Date().toISOString();
  return {
    radar_id: RADAR_ID, version: VERSION, status: "ACTIVE", cadence_ms: cadenceMs, max_cycles: maxCycles,
    cycle_count: 0, monetary_budget: 0, production_actions: false, paid_routes_active: false,
    money_movement: false, external_data_trust: "UNTRUSTED_DATA", started_at: now, updated_at: now,
    next_alarm_at: null, last_cycle: null,
  };
}

export class X402DemandState {
  constructor(ctx, env) { this.ctx = ctx; this.env = env; }

  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname.endsWith("/state")) {
      const state = await this.ctx.storage.get("state");
      return json({ ok: Boolean(state), state: state || null });
    }
    if (request.method === "POST" && url.pathname.endsWith("/start")) {
      let body = {}; try { body = await request.json(); } catch {}
      let state; try { state = newState(body); } catch (error) { return json({ ok: false, error: safeString(error?.message) }, 400); }
      const existing = await this.ctx.storage.get("state");
      if (existing?.status === "ACTIVE") return json({ ok: true, reused: true, state: existing });
      const next = Date.now() + 1000;
      state.next_alarm_at = new Date(next).toISOString();
      await this.ctx.storage.put("state", state);
      await this.ctx.storage.setAlarm(next);
      return json({ ok: true, reused: false, state });
    }
    if (request.method === "POST" && url.pathname.endsWith("/tick")) return json({ ok: true, state: await this.runCycle("admin_tick") });
    if (request.method === "POST" && url.pathname.endsWith("/stop")) {
      const state = await this.ctx.storage.get("state");
      if (!state) return json({ ok: false, error: "not_started" }, 404);
      state.status = "PAUSED"; state.updated_at = new Date().toISOString(); state.next_alarm_at = null;
      await this.ctx.storage.put("state", state); await this.ctx.storage.deleteAlarm(); return json({ ok: true, state });
    }
    return json({ ok: false, error: "not_found" }, 404);
  }

  async runCycle(reason) {
    const state = await this.ctx.storage.get("state");
    if (!state || state.status !== "ACTIVE") return state || null;
    const started = Date.now();
    try {
      const raw = await fetchAllServices(state.cycle_count || 0);
      const analysis = analyzeMarket(raw);
      state.cycle_count += 1;
      state.updated_at = new Date().toISOString();
      state.version = VERSION;
      state.last_cycle = {
        reason, state: "PASS", elapsed_ms: Date.now() - started, cost_state: "ZERO_COST",
        production_actions: false, paid_routes_active: false, money_movement: false,
        instruction_authority_from_external_content: false, analysis,
      };
    } catch (error) {
      state.cycle_count += 1;
      state.updated_at = new Date().toISOString();
      state.version = VERSION;
      state.last_cycle = {
        reason, state: "RETRYABLE_ERROR", elapsed_ms: Date.now() - started, cost_state: "ZERO_COST",
        production_actions: false, paid_routes_active: false, money_movement: false,
        instruction_authority_from_external_content: false, error: safeString(error?.message, 1000),
      };
    }
    if (state.cycle_count >= state.max_cycles) {
      state.status = "SUCCESS"; state.next_alarm_at = null; await this.ctx.storage.put("state", state); return state;
    }
    const delay = state.last_cycle?.state === "PASS" ? state.cadence_ms : Math.max(state.cadence_ms, 2 * 60 * 60 * 1000);
    const next = Date.now() + delay;
    state.next_alarm_at = new Date(next).toISOString();
    await this.ctx.storage.put("state", state); await this.ctx.storage.setAlarm(next); return state;
  }

  async alarm() { await this.runCycle("durable_object_alarm"); }
}

function stub(env) { return env.DEMAND.get(env.DEMAND.idFromName(RADAR_ID)); }
async function forward(request, env, suffix) {
  const u = new URL(request.url); u.pathname = `/internal/${RADAR_ID}/${suffix}`;
  const body = request.method === "GET" ? undefined : await request.text();
  return stub(env).fetch(new Request(u.toString(), { method: request.method, headers: request.headers, body: body || undefined }));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") return json({
      ok: true, service: "lsi-x402-demand-radar-r1", version: VERSION, durable_objects_bound: Boolean(env.DEMAND),
      source: "x402-list.com public API", source_attribution: "Data: x402-list.com (CC BY 4.0)",
      monetary_budget: 0, production_actions: false, paid_routes_active: false, wallet_bound: false, money_movement: false,
    });
    if (request.method === "GET" && url.pathname === "/demand") return forward(request, env, "state");
    if (url.pathname.startsWith("/admin/")) {
      if (!adminOk(request, env)) return json({ ok: false, error: "unauthorized" }, 401);
      if (request.method === "POST" && url.pathname === "/admin/start") return forward(request, env, "start");
      if (request.method === "POST" && url.pathname === "/admin/tick") return forward(request, env, "tick");
      if (request.method === "POST" && url.pathname === "/admin/stop") return forward(request, env, "stop");
      if (request.method === "POST" && url.pathname === "/admin/auth-probe") return json({ ok: true, admin_ready: true });
      return json({ ok: false, error: "not_found" }, 404);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};