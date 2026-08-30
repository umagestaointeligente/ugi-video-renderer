const VERSION = "lsi-revenue-velocity-r1-2026-08-30";
const LEARNING_EVENTS = "https://lsi-continual-learning-r1.umagestaointeligente.workers.dev/events";
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

async function fetchEvents() {
  const response = await fetch(LEARNING_EVENTS, {
    headers: { "user-agent": "LSI-Revenue-Velocity-R1/1.0" },
  });
  if (!response.ok) throw new Error(`learning_events_${response.status}`);
  const body = await response.json();
  if (!body?.ok || !Array.isArray(body.events)) throw new Error("learning_events_invalid");
  return body.events;
}

function aggregate(events) {
  const routes = new Map();
  for (const event of events) {
    const route = String(event?.route_id || "").slice(0, 120);
    if (!route) continue;
    if (!routes.has(route)) routes.set(route, {
      route_id: route,
      event_count: 0,
      timed_event_count: 0,
      verified_revenue_usd: 0,
      claimed_unverified_revenue_usd: 0,
      elapsed_ms: 0,
      revenue_event_count: 0,
    });
    const r = routes.get(route);
    r.event_count += 1;
    const verified = Math.max(0, Number(event?.revenue_usd_verified || 0));
    const claimed = Math.max(0, Number(event?.revenue_usd_claimed || 0));
    const elapsed = Math.max(0, Number(event?.elapsed_ms || 0));
    r.verified_revenue_usd += Number.isFinite(verified) ? verified : 0;
    r.claimed_unverified_revenue_usd += Number.isFinite(claimed - verified) ? Math.max(0, claimed - verified) : 0;
    if (elapsed > 0) {
      r.elapsed_ms += elapsed;
      r.timed_event_count += 1;
    }
    if (verified > 0) r.revenue_event_count += 1;
  }

  const ranked = [];
  for (const r of routes.values()) {
    const elapsedMinutes = r.elapsed_ms / 60000;
    const velocity = elapsedMinutes > 0 ? r.verified_revenue_usd / elapsedMinutes : 0;
    const targetRatio = TARGET_USD_PER_MINUTE > 0 ? velocity / TARGET_USD_PER_MINUTE : 0;
    const recurrence = r.event_count ? r.revenue_event_count / r.event_count : 0;
    ranked.push({
      ...r,
      verified_revenue_usd: round(r.verified_revenue_usd),
      claimed_unverified_revenue_usd: round(r.claimed_unverified_revenue_usd),
      elapsed_minutes_measured: round(elapsedMinutes, 4),
      verified_revenue_usd_per_minute: round(velocity),
      target_usd_per_minute: TARGET_USD_PER_MINUTE,
      target_ratio: round(targetRatio, 4),
      verified_revenue_recurrence: round(recurrence, 4),
      velocity_state: r.verified_revenue_usd <= 0 ? "NO_VERIFIED_REVENUE" : (elapsedMinutes <= 0 ? "REVENUE_VERIFIED_TIME_UNMEASURED" : (velocity >= TARGET_USD_PER_MINUTE ? "TARGET_MET_OR_EXCEEDED" : "BELOW_TARGET")),
      daily_projection_from_verified_velocity_usd: elapsedMinutes > 0 && r.verified_revenue_usd > 0 ? round(velocity * 1440, 4) : 0,
      projection_is_revenue: false,
    });
  }
  ranked.sort((a, b) => b.verified_revenue_usd_per_minute - a.verified_revenue_usd_per_minute || b.verified_revenue_usd - a.verified_revenue_usd);
  return ranked;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({
        ok: true,
        service: "lsi-revenue-velocity-r1",
        version: VERSION,
        target_usd_per_minute: TARGET_USD_PER_MINUTE,
        revenue_source: "VERIFIED_EVENTS_ONLY",
        projections_count_as_revenue: false,
        money_movement: false,
        production_actions: false,
      });
    }
    if (request.method === "GET" && url.pathname === "/velocity") {
      try {
        const events = await fetchEvents();
        const routes = aggregate(events);
        const best = routes[0] || null;
        return json({
          ok: true,
          measured_at: new Date().toISOString(),
          target_usd_per_minute: TARGET_USD_PER_MINUTE,
          event_window: events.length,
          best_route: best,
          routes,
          accounting_rule: "Only revenue_usd_verified contributes to velocity. Projections are not revenue.",
        });
      } catch (error) {
        return json({ ok: false, error: String(error?.message || error), money_movement: false }, 503);
      }
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
