const VERSION = "lsi-revenue-velocity-r1-2026-08-30";
const TARGET_USD_PER_MINUTE = 0.10;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-lsi-velocity-version": VERSION,
    },
  });
}

function round(n, d = 8) {
  const p = 10 ** d;
  return Math.round(Number(n || 0) * p) / p;
}

async function fetchLearningState(env) {
  if (!env.LEARNING_SERVICE) throw new Error("learning_service_binding_missing");
  const response = await env.LEARNING_SERVICE.fetch(new Request("https://learning.internal/state", {
    method: "GET",
    headers: { "user-agent": "LSI-Revenue-Velocity-R1/1.0" },
  }));
  if (!response.ok) throw new Error(`learning_state_${response.status}`);
  const body = await response.json();
  if (!body?.ok || !body.state || typeof body.state.routes !== "object") throw new Error("learning_state_invalid");
  return body.state;
}

function aggregate(state) {
  const createdMs = Date.parse(state.created_at || "");
  const nowMs = Date.now();
  const observedMinutes = Number.isFinite(createdMs) && nowMs > createdMs ? (nowMs - createdMs) / 60000 : 0;
  const routes = [];

  for (const model of Object.values(state.routes || {})) {
    const verified = Math.max(0, Number(model?.verified_revenue_usd || 0));
    const claimedUnverified = Math.max(0, Number(model?.claimed_unverified_revenue_usd || 0));
    const cost = Math.max(0, Number(model?.verified_cost_usd || 0));
    const net = verified - cost;
    const velocity = observedMinutes > 0 ? verified / observedMinutes : 0;
    const netVelocity = observedMinutes > 0 ? net / observedMinutes : 0;
    const targetRatio = TARGET_USD_PER_MINUTE > 0 ? velocity / TARGET_USD_PER_MINUTE : 0;

    routes.push({
      route_id: String(model?.route_id || "").slice(0, 120),
      recommendation: model?.recommendation || "UNKNOWN",
      learning_score: Number(model?.score || 0),
      trials: Number(model?.trials || 0),
      successes: Number(model?.successes || 0),
      failures: Number(model?.failures || 0),
      blocked_events: Number(model?.blocked_events || 0),
      verified_revenue_usd: round(verified),
      claimed_unverified_revenue_usd: round(claimedUnverified),
      verified_cost_usd: round(cost),
      observed_minutes: round(observedMinutes, 4),
      verified_revenue_usd_per_minute: round(velocity),
      verified_net_revenue_usd_per_minute: round(netVelocity),
      target_usd_per_minute: TARGET_USD_PER_MINUTE,
      target_ratio: round(targetRatio, 4),
      velocity_state: verified <= 0 ? "NO_VERIFIED_REVENUE" : (observedMinutes <= 0 ? "REVENUE_VERIFIED_TIME_UNMEASURED" : (velocity >= TARGET_USD_PER_MINUTE ? "TARGET_MET_OR_EXCEEDED" : "BELOW_TARGET")),
      daily_projection_from_verified_velocity_usd: observedMinutes > 0 && verified > 0 ? round(velocity * 1440, 4) : 0,
      projection_is_revenue: false,
    });
  }

  routes.sort((a, b) => b.verified_revenue_usd_per_minute - a.verified_revenue_usd_per_minute || b.verified_revenue_usd - a.verified_revenue_usd || b.learning_score - a.learning_score);
  return { observedMinutes, routes };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({
        ok: true,
        service: "lsi-revenue-velocity-r1",
        version: VERSION,
        learning_service_bound: Boolean(env.LEARNING_SERVICE),
        target_usd_per_minute: TARGET_USD_PER_MINUTE,
        revenue_source: "VERIFIED_PERSISTENT_ROUTE_STATE_ONLY",
        projections_count_as_revenue: false,
        money_movement: false,
        production_actions: false,
      });
    }
    if (request.method === "GET" && url.pathname === "/velocity") {
      try {
        const state = await fetchLearningState(env);
        const result = aggregate(state);
        const best = result.routes[0] || null;
        return json({
          ok: true,
          measured_at: new Date().toISOString(),
          target_usd_per_minute: TARGET_USD_PER_MINUTE,
          learning_generation: Number(state.generation || 0),
          event_count: Number(state.event_count || 0),
          observed_minutes: round(result.observedMinutes, 4),
          best_route: best,
          routes: result.routes,
          accounting_rule: "Only verified_revenue_usd from persistent learning state contributes to velocity. Projections are not revenue.",
        });
      } catch (error) {
        return json({ ok: false, error: String(error?.message || error), money_movement: false }, 503);
      }
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
