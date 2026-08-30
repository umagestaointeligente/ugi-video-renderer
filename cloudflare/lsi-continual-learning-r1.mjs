const VERSION = "lsi-continual-learning-r1-2026-08-30";
const ENGINE_ID = "lsi-continual-learning-global-r1";
const DEFAULT_CADENCE_MS = 10 * 60 * 1000;
const MIN_CADENCE_MS = 5 * 60 * 1000;
const MAX_CADENCE_MS = 24 * 60 * 60 * 1000;
const MAX_PUBLIC_EVENTS = 50;
const MAX_EVENT_HISTORY = 5000;

const SOURCES = {
  packvalue_tools_metrics: "https://lsi-packvalue-tools-r1.umagestaointeligente.workers.dev/metrics",
  packvalue_mcp_health: "https://lsi-packvalue-mcp-r1.umagestaointeligente.workers.dev/health",
  packvalue402_health: "https://lsi-packvalue402-r1.umagestaointeligente.workers.dev/health",
  revenue_radar_state: "https://lsi-revenue-radar-r1.umagestaointeligente.workers.dev/radar",
};

const ROUTE_SEEDS = [
  { route_id: "x402_agent_micropayments", class: "machine_micropayments", blocked: true, block_reason: "APPROVED_BASE_RECEIVE_ADDRESS_REQUIRED" },
  { route_id: "packvalue_tools_organic", class: "organic_utility", blocked: false },
  { route_id: "packvalue_mcp_distribution", class: "agent_distribution", blocked: false },
  { route_id: "verified_code_bounties", class: "bounty", blocked: false },
  { route_id: "html5_game_distribution", class: "ad_supported_distribution", blocked: false },
  { route_id: "greenfield_brl_checkout", class: "checkout_rail", blocked: true, block_reason: "ISOLATED_APPROVED_RAIL_NOT_PROVEN" },
];

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-lsi-learning-version": VERSION,
    },
  });
}

function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }
function safe(v, max = 500) { return String(v ?? "").slice(0, max); }
function nowIso() { return new Date().toISOString(); }
function round(n, d = 4) { const p = 10 ** d; return Math.round(Number(n || 0) * p) / p; }

function adminOk(request, env) {
  const expected = safe(env.ADMIN_TOKEN, 512);
  if (!expected) return false;
  const auth = request.headers.get("authorization") || "";
  return auth === `Bearer ${expected}`;
}

function evidenceWeight(level) {
  const map = { E0: 0.1, E1: 0.3, E2: 0.55, E3: 0.8, E4: 1.0 };
  return map[safe(level, 2).toUpperCase()] ?? 0.1;
}

function normalizeEvent(input = {}) {
  const routeId = safe(input.route_id, 120).trim();
  if (!/^[a-z0-9._-]{3,120}$/i.test(routeId)) throw new Error("route_id_invalid");
  const outcome = safe(input.outcome, 32).toUpperCase();
  if (!["SUCCESS", "FAILURE", "NEUTRAL", "BLOCKED", "REVENUE"].includes(outcome)) throw new Error("outcome_invalid");
  const evidenceLevel = safe(input.evidence_level || "E0", 2).toUpperCase();
  if (!/^E[0-4]$/.test(evidenceLevel)) throw new Error("evidence_level_invalid");
  const revenueUsd = Number(input.revenue_usd || 0);
  const costUsd = Number(input.cost_usd || 0);
  const elapsedMs = Number(input.elapsed_ms || 0);
  const quality = clamp(Number(input.quality_score ?? 0.5), 0, 1);
  const risk = clamp(Number(input.risk_score ?? 0), 0, 1);
  const revenueVerified = input.revenue_verified === true;
  if (![revenueUsd, costUsd, elapsedMs, quality, risk].every(Number.isFinite)) throw new Error("numeric_field_invalid");
  if (revenueUsd < 0 || costUsd < 0 || elapsedMs < 0) throw new Error("negative_metric_invalid");
  if (revenueUsd > 0 && !revenueVerified) {
    // Unverified money is retained as a claim signal only and can never increase verified revenue.
  }
  return {
    event_id: crypto.randomUUID(),
    timestamp: nowIso(),
    mission_id: safe(input.mission_id || "lsi-autolearn", 120),
    project_id: safe(input.project_id || "LSI", 120),
    route_id: routeId,
    event_type: safe(input.event_type || "observation", 80),
    outcome,
    evidence_level: evidenceLevel,
    evidence_weight: evidenceWeight(evidenceLevel),
    revenue_usd_claimed: round(revenueUsd, 8),
    revenue_usd_verified: revenueVerified ? round(revenueUsd, 8) : 0,
    cost_usd: round(costUsd, 8),
    elapsed_ms: Math.round(elapsedMs),
    quality_score: round(quality),
    risk_score: round(risk),
    reason_code: safe(input.reason_code || "UNSPECIFIED", 120).replace(/[^A-Za-z0-9._-]/g, "_"),
    source_ref: safe(input.source_ref || "", 500),
    verified: input.verified === true,
    instruction_authority: false,
    raw_external_content_stored: false,
  };
}

function baseRoute(seed) {
  return {
    route_id: seed.route_id,
    class: seed.class,
    blocked: Boolean(seed.blocked),
    block_reason: seed.block_reason || null,
    trials: 0,
    successes: 0,
    failures: 0,
    blocked_events: 0,
    verified_revenue_usd: 0,
    claimed_unverified_revenue_usd: 0,
    verified_cost_usd: 0,
    ema_signal: 0,
    ema_quality: 0.5,
    ema_risk: seed.blocked ? 0.5 : 0,
    last_outcome: null,
    last_event_at: null,
    lessons: { success: {}, failure: {}, blocked: {} },
    recommendation: seed.blocked ? "BLOCKED" : "EXPLORE",
    score: 0,
  };
}

function lessonBucket(model, outcome) {
  if (outcome === "SUCCESS" || outcome === "REVENUE") return model.lessons.success;
  if (outcome === "FAILURE") return model.lessons.failure;
  if (outcome === "BLOCKED") return model.lessons.blocked;
  return null;
}

function computeRecommendation(model, totalEvents) {
  const trials = Math.max(0, model.trials);
  const successRate = trials ? model.successes / trials : 0;
  const revenue = Number(model.verified_revenue_usd || 0);
  const cost = Number(model.verified_cost_usd || 0);
  const net = revenue - cost;
  const exploration = Math.sqrt((2 * Math.log(Math.max(2, totalEvents + 1))) / Math.max(1, trials + 1));
  const economics = Math.min(1, Math.log1p(Math.max(0, net)) / Math.log(11));
  const evidenceSignal = clamp((model.ema_signal + 1) / 2, 0, 1);
  const riskPenalty = clamp(model.ema_risk, 0, 1);
  const raw = (economics * 45) + (successRate * 25) + (evidenceSignal * 15) + (Math.min(1, exploration) * 15) - (riskPenalty * 35);
  const score = round(clamp(raw, 0, 100), 2);

  let recommendation = "EXPLORE";
  if (model.blocked) recommendation = "BLOCKED";
  else if (revenue > 0 && net > 0 && successRate >= 0.5 && riskPenalty <= 0.35) recommendation = "ACCELERATE";
  else if (trials >= 12 && revenue === 0 && successRate < 0.2) recommendation = "KILL_CANDIDATE";
  else if (trials >= 6 && score < 35) recommendation = "HOLD";
  else if (score >= 60) recommendation = "KEEP_AND_OPTIMIZE";

  return { score, recommendation, success_rate: round(successRate), net_verified_revenue_usd: round(net, 8), exploration_bonus: round(exploration) };
}

async function fetchJson(url, timeoutMs = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { signal: controller.signal, headers: { "user-agent": "LSI-Continual-Learning-R1/1.0" } });
    const text = await response.text();
    let body = null;
    try { body = JSON.parse(text); } catch {}
    return { ok: response.ok, status: response.status, body };
  } catch (error) {
    return { ok: false, status: 0, error: safe(error?.message, 300), body: null };
  } finally {
    clearTimeout(timer);
  }
}

export class LearningState {
  constructor(ctx, env) { this.ctx = ctx; this.env = env; }

  async ensureState() {
    let state = await this.ctx.storage.get("state");
    if (state) return state;
    const routes = {};
    for (const seed of ROUTE_SEEDS) routes[seed.route_id] = baseRoute(seed);
    state = {
      engine_id: ENGINE_ID,
      version: VERSION,
      status: "PAUSED",
      generation: 1,
      cycle_count: 0,
      event_count: 0,
      cadence_ms: DEFAULT_CADENCE_MS,
      created_at: nowIso(),
      updated_at: nowIso(),
      next_alarm_at: null,
      last_cycle: null,
      exploration_floor: 0.05,
      policy: {
        zero_cost_default: true,
        revenue_requires_verified_evidence: true,
        unverified_revenue_promotes_route: false,
        autonomous_spend: false,
        autonomous_trading: false,
        autonomous_payment_activation: false,
        production_publish: false,
        immutable_learning_aggregates: true,
      },
      routes,
      observations: {},
    };
    await this.ctx.storage.put("state", state);
    return state;
  }

  async appendEvent(event, state) {
    let model = state.routes[event.route_id];
    if (!model) {
      model = baseRoute({ route_id: event.route_id, class: "discovered", blocked: false });
      state.routes[event.route_id] = model;
    }

    const alpha = 0.2 * event.evidence_weight;
    let signal = 0;
    if (event.outcome === "SUCCESS") signal = 0.6;
    else if (event.outcome === "REVENUE") signal = 1.0;
    else if (event.outcome === "FAILURE") signal = -0.7;
    else if (event.outcome === "BLOCKED") signal = -0.35;

    model.trials += event.outcome === "NEUTRAL" ? 0 : 1;
    if (event.outcome === "SUCCESS" || event.outcome === "REVENUE") model.successes += 1;
    if (event.outcome === "FAILURE") model.failures += 1;
    if (event.outcome === "BLOCKED") model.blocked_events += 1;
    model.verified_revenue_usd = round(model.verified_revenue_usd + event.revenue_usd_verified, 8);
    model.claimed_unverified_revenue_usd = round(model.claimed_unverified_revenue_usd + Math.max(0, event.revenue_usd_claimed - event.revenue_usd_verified), 8);
    model.verified_cost_usd = round(model.verified_cost_usd + event.cost_usd, 8);
    model.ema_signal = round((1 - alpha) * model.ema_signal + alpha * signal);
    model.ema_quality = round((1 - alpha) * model.ema_quality + alpha * event.quality_score);
    model.ema_risk = round((1 - alpha) * model.ema_risk + alpha * event.risk_score);
    model.last_outcome = event.outcome;
    model.last_event_at = event.timestamp;

    const bucket = lessonBucket(model, event.outcome);
    if (bucket) bucket[event.reason_code] = Number(bucket[event.reason_code] || 0) + 1;

    state.event_count += 1;
    const rec = computeRecommendation(model, state.event_count);
    model.score = rec.score;
    model.recommendation = rec.recommendation;
    model.success_rate = rec.success_rate;
    model.net_verified_revenue_usd = rec.net_verified_revenue_usd;
    model.exploration_bonus = rec.exploration_bonus;
    state.updated_at = nowIso();
    state.generation += 1;

    const seq = String(state.event_count).padStart(12, "0");
    await this.ctx.storage.put(`event:${seq}`, event);
    if (state.event_count > MAX_EVENT_HISTORY) {
      // Keep learned aggregates permanently; compact raw history only.
      const old = String(state.event_count - MAX_EVENT_HISTORY).padStart(12, "0");
      await this.ctx.storage.delete(`event:${old}`);
    }
    await this.ctx.storage.put("state", state);
    return { event, model };
  }

  async observeSources(state) {
    const [traffic, mcp, paid, radar] = await Promise.all([
      fetchJson(SOURCES.packvalue_tools_metrics),
      fetchJson(SOURCES.packvalue_mcp_health),
      fetchJson(SOURCES.packvalue402_health),
      fetchJson(SOURCES.revenue_radar_state),
    ]);
    const events = [];

    const trafficNow = Number(traffic?.body?.production_requests || 0);
    const trafficPrev = Number(state.observations?.packvalue_tools_requests || 0);
    const trafficDelta = Math.max(0, trafficNow - trafficPrev);
    state.observations.packvalue_tools_requests = trafficNow;
    if (traffic.ok) events.push(normalizeEvent({
      route_id: "packvalue_tools_organic", outcome: trafficDelta > 0 ? "SUCCESS" : "NEUTRAL", evidence_level: "E2",
      event_type: "aggregate_request_delta", quality_score: trafficDelta > 0 ? 0.7 : 0.5, risk_score: 0.05,
      reason_code: trafficDelta > 0 ? "NEW_AGGREGATE_REQUESTS" : "NO_NEW_REQUESTS", source_ref: SOURCES.packvalue_tools_metrics, verified: true,
    }));

    events.push(normalizeEvent({
      route_id: "packvalue_mcp_distribution", outcome: mcp.ok ? "SUCCESS" : "FAILURE", evidence_level: "E2",
      event_type: "health_probe", quality_score: mcp.ok ? 0.8 : 0.2, risk_score: mcp.ok ? 0.05 : 0.25,
      reason_code: mcp.ok ? "MCP_HEALTHY" : "MCP_HEALTH_FAILED", source_ref: SOURCES.packvalue_mcp_health, verified: true,
    }));

    const paymentsEnabled = paid?.body?.payments_enabled === true || paid?.body?.payment_enabled === true;
    events.push(normalizeEvent({
      route_id: "x402_agent_micropayments", outcome: paymentsEnabled ? "NEUTRAL" : "BLOCKED", evidence_level: "E2",
      event_type: "payment_state_probe", quality_score: paid.ok ? 0.8 : 0.3, risk_score: 0.1,
      reason_code: paymentsEnabled ? "PAYMENTS_ACTIVE_REQUIRES_SETTLEMENT_EVIDENCE" : "PAYMENTS_DISABLED_NO_APPROVED_ADDRESS", source_ref: SOURCES.packvalue402_health, verified: true,
    }));

    const candidates = Number(radar?.body?.state?.last_cycle?.candidate_count || 0);
    events.push(normalizeEvent({
      route_id: "verified_code_bounties", outcome: radar.ok && candidates > 0 ? "SUCCESS" : (radar.ok ? "NEUTRAL" : "FAILURE"), evidence_level: "E2",
      event_type: "radar_candidate_observation", quality_score: candidates > 0 ? 0.65 : 0.45, risk_score: 0.12,
      reason_code: candidates > 0 ? "RADAR_FOUND_CANDIDATES" : (radar.ok ? "RADAR_NO_CANDIDATES" : "RADAR_UNAVAILABLE"), source_ref: SOURCES.revenue_radar_state, verified: true,
    }));

    return { probes: { traffic, mcp, paid, radar }, events };
  }

  async runCycle(reason) {
    const state = await this.ensureState();
    if (state.status !== "ACTIVE") return state;
    const started = Date.now();
    let probeSummary = {};
    try {
      const observed = await this.observeSources(state);
      probeSummary = Object.fromEntries(Object.entries(observed.probes).map(([k, v]) => [k, { ok: Boolean(v.ok), status: Number(v.status || 0) }]));
      for (const event of observed.events) await this.appendEvent(event, state);
    } catch (error) {
      probeSummary = { error: safe(error?.message, 500) };
    }
    state.cycle_count += 1;
    state.last_cycle = {
      reason,
      started_at: new Date(started).toISOString(),
      ended_at: nowIso(),
      elapsed_ms: Date.now() - started,
      probes: probeSummary,
      cost_state: "ZERO_COST",
      money_movement: false,
      production_actions: false,
      learning_generation: state.generation,
    };
    const next = Date.now() + state.cadence_ms;
    state.next_alarm_at = new Date(next).toISOString();
    state.updated_at = nowIso();
    await this.ctx.storage.put("state", state);
    await this.ctx.storage.setAlarm(next);
    return state;
  }

  async fetch(request) {
    const url = new URL(request.url);
    const state = await this.ensureState();
    if (request.method === "GET" && url.pathname.endsWith("/state")) return json({ ok: true, state });
    if (request.method === "GET" && url.pathname.endsWith("/routes")) {
      const routes = Object.values(state.routes).sort((a, b) => b.score - a.score);
      return json({ ok: true, generation: state.generation, routes });
    }
    if (request.method === "GET" && url.pathname.endsWith("/events")) {
      const limit = clamp(Number(url.searchParams.get("limit") || 20), 1, MAX_PUBLIC_EVENTS);
      const start = Math.max(1, state.event_count - limit + 1);
      const events = [];
      for (let i = start; i <= state.event_count; i++) {
        const item = await this.ctx.storage.get(`event:${String(i).padStart(12, "0")}`);
        if (item) events.push(item);
      }
      return json({ ok: true, events });
    }
    if (request.method === "POST" && url.pathname.endsWith("/start")) {
      const body = await request.json().catch(() => ({}));
      state.status = "ACTIVE";
      state.cadence_ms = clamp(Number(body.cadence_ms || state.cadence_ms || DEFAULT_CADENCE_MS), MIN_CADENCE_MS, MAX_CADENCE_MS);
      state.updated_at = nowIso();
      const next = Date.now() + 1000;
      state.next_alarm_at = new Date(next).toISOString();
      await this.ctx.storage.put("state", state);
      await this.ctx.storage.setAlarm(next);
      return json({ ok: true, state });
    }
    if (request.method === "POST" && url.pathname.endsWith("/pause")) {
      state.status = "PAUSED";
      state.next_alarm_at = null;
      state.updated_at = nowIso();
      await this.ctx.storage.put("state", state);
      await this.ctx.storage.deleteAlarm();
      return json({ ok: true, state });
    }
    if (request.method === "POST" && url.pathname.endsWith("/event")) {
      const body = await request.json().catch(() => null);
      if (!body) return json({ ok: false, error: "invalid_json" }, 400);
      try {
        const event = normalizeEvent(body);
        const result = await this.appendEvent(event, state);
        return json({ ok: true, ...result, money_movement: false, production_actions: false });
      } catch (error) {
        return json({ ok: false, error: safe(error?.message, 300) }, 400);
      }
    }
    if (request.method === "POST" && url.pathname.endsWith("/tick")) return json({ ok: true, state: await this.runCycle("admin_tick") });
    return json({ ok: false, error: "not_found" }, 404);
  }

  async alarm() { await this.runCycle("durable_object_alarm"); }
}

function stub(env) {
  const id = env.LEARNING.idFromName(ENGINE_ID);
  return env.LEARNING.get(id);
}

async function forward(request, env, suffix) {
  const target = new URL(request.url);
  target.pathname = `/internal/${ENGINE_ID}/${suffix}`;
  const raw = request.method === "GET" ? undefined : await request.text();
  return stub(env).fetch(new Request(target.toString(), { method: request.method, headers: request.headers, body: raw || undefined }));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({
        ok: true,
        service: "lsi-continual-learning-r1",
        version: VERSION,
        durable_objects_bound: Boolean(env.LEARNING),
        online_learning: true,
        persistent_lessons: true,
        zero_cost_policy: true,
        revenue_requires_verified_evidence: true,
        unverified_revenue_promotes_route: false,
        money_movement: false,
        production_actions: false,
        autonomous_spend: false,
        autonomous_payment_activation: false,
      });
    }
    if (request.method === "GET" && url.pathname === "/state") return forward(request, env, "state");
    if (request.method === "GET" && url.pathname === "/routes") return forward(request, env, "routes");
    if (request.method === "GET" && url.pathname === "/events") return forward(request, env, `events${url.search}`);

    if (url.pathname.startsWith("/admin/")) {
      if (!adminOk(request, env)) return json({ ok: false, error: "unauthorized" }, 401);
      if (request.method === "POST" && url.pathname === "/admin/start") return forward(request, env, "start");
      if (request.method === "POST" && url.pathname === "/admin/pause") return forward(request, env, "pause");
      if (request.method === "POST" && url.pathname === "/admin/tick") return forward(request, env, "tick");
      if (request.method === "POST" && url.pathname === "/admin/event") return forward(request, env, "event");
      if (request.method === "POST" && url.pathname === "/admin/selftest") {
        const a = baseRoute({ route_id: "selftest", class: "test", blocked: false });
        a.trials = 6; a.successes = 5; a.verified_revenue_usd = 0.25; a.verified_cost_usd = 0; a.ema_signal = 0.7; a.ema_quality = 0.9; a.ema_risk = 0.05;
        const good = computeRecommendation(a, 20);
        const b = baseRoute({ route_id: "selftest_bad", class: "test", blocked: false });
        b.trials = 15; b.successes = 1; b.failures = 14; b.ema_signal = -0.8; b.ema_quality = 0.2; b.ema_risk = 0.4;
        const bad = computeRecommendation(b, 20);
        return json({ ok: good.recommendation === "ACCELERATE" && bad.recommendation === "KILL_CANDIDATE", good, bad, persisted: false });
      }
      return json({ ok: false, error: "not_found" }, 404);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
