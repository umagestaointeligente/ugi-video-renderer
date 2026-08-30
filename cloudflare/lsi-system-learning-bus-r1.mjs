const VERSION = "lsi-system-learning-bus-r1-2026-08-30";
const OIDC_ISSUER = "https://token.actions.githubusercontent.com";
const OIDC_AUDIENCE = "lsi-system-learning-bus";
const ALLOWED_REPOSITORY = "umagestaointeligente/ugi-video-renderer";
const GLOBAL_ID = "lsi-system-learning-global-r1";
const MAX_EVENTS = 10000;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-lsi-learning-bus-version": VERSION } });
}
function safe(v, n = 160) { return String(v ?? "").slice(0, n); }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, Number(v))); }
function round(v, d = 6) { const p = 10 ** d; return Math.round(Number(v || 0) * p) / p; }
function b64urlToBytes(v) { const b = v.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - v.length % 4) % 4); const r = atob(b), o = new Uint8Array(r.length); for (let i = 0; i < r.length; i++) o[i] = r.charCodeAt(i); return o; }
function decodeJwtPart(p) { return JSON.parse(new TextDecoder().decode(b64urlToBytes(p))); }

function allowedRef(ref) {
  const prefixes = ["refs/heads/lsi-", "refs/heads/ugi-", "refs/heads/orbit-", "refs/heads/recruiter-", "refs/heads/bfy-", "refs/heads/lola-"];
  return ref === "refs/heads/main" || prefixes.some(p => ref.startsWith(p));
}

async function verifyGithubOidc(request) {
  const auth = request.headers.get("authorization") || "";
  if (!auth.startsWith("Bearer ")) throw new Error("missing_bearer");
  const token = auth.slice(7).trim();
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("invalid_jwt");
  const header = decodeJwtPart(parts[0]);
  const claims = decodeJwtPart(parts[1]);
  if (header.alg !== "RS256" || !header.kid) throw new Error("unsupported_jwt_header");
  const cfgResp = await fetch(`${OIDC_ISSUER}/.well-known/openid-configuration`, { cf: { cacheTtl: 3600 } });
  if (!cfgResp.ok) throw new Error("oidc_config_unavailable");
  const cfg = await cfgResp.json();
  const jwksResp = await fetch(cfg.jwks_uri, { cf: { cacheTtl: 3600 } });
  if (!jwksResp.ok) throw new Error("oidc_jwks_unavailable");
  const jwks = await jwksResp.json();
  const jwk = (jwks.keys || []).find(k => k.kid === header.kid);
  if (!jwk) throw new Error("oidc_kid_not_found");
  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const signatureOk = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, b64urlToBytes(parts[2]), new TextEncoder().encode(`${parts[0]}.${parts[1]}`));
  if (!signatureOk) throw new Error("oidc_signature_invalid");
  const now = Math.floor(Date.now() / 1000);
  const aud = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (claims.iss !== OIDC_ISSUER) throw new Error("oidc_issuer_invalid");
  if (!aud.includes(OIDC_AUDIENCE)) throw new Error("oidc_audience_invalid");
  if (!claims.exp || claims.exp < now - 30) throw new Error("oidc_expired");
  if (claims.repository !== ALLOWED_REPOSITORY) throw new Error("oidc_repository_denied");
  const ref = safe(claims.ref, 300);
  if (!allowedRef(ref)) throw new Error("oidc_ref_denied");
  const eventName = safe(claims.event_name, 80);
  if (eventName && !["push", "workflow_dispatch", "schedule"].includes(eventName)) throw new Error("oidc_event_denied");
  return { repository: claims.repository, ref, run_id: claims.run_id || null, workflow_ref: safe(claims.workflow_ref, 500), event_name: eventName };
}

const EVIDENCE_WEIGHT = { E0: 0.1, E1: 0.3, E2: 0.55, E3: 0.8, E4: 1 };
function normalizeEvent(body, identity) {
  const projectId = safe(body?.project_id, 80).trim();
  const componentId = safe(body?.component_id, 100).trim();
  if (!/^[A-Za-z0-9._-]{2,80}$/.test(projectId)) throw new Error("project_id_invalid");
  if (!/^[A-Za-z0-9._-]{2,100}$/.test(componentId)) throw new Error("component_id_invalid");
  const outcome = safe(body?.outcome, 20).toUpperCase();
  if (!["SUCCESS", "FAILURE", "BLOCKED", "NEUTRAL", "REVENUE"].includes(outcome)) throw new Error("outcome_invalid");
  const evidenceLevel = safe(body?.evidence_level || "E0", 2).toUpperCase();
  if (!(evidenceLevel in EVIDENCE_WEIGHT)) throw new Error("evidence_level_invalid");
  const revenueUsd = Number(body?.revenue_usd || 0);
  const revenueVerified = body?.revenue_verified === true;
  const costUsd = Number(body?.cost_usd || 0);
  const elapsedMs = Number(body?.elapsed_ms || 0);
  const quality = clamp(body?.quality_score ?? 0.5, 0, 1);
  const risk = clamp(body?.risk_score ?? 0, 0, 1);
  if (![revenueUsd, costUsd, elapsedMs, quality, risk].every(Number.isFinite) || revenueUsd < 0 || costUsd < 0 || elapsedMs < 0) throw new Error("numeric_field_invalid");
  const lessonCode = safe(body?.lesson_code || "UNSPECIFIED", 120).replace(/[^A-Za-z0-9._-]/g, "_");
  return {
    event_id: crypto.randomUUID(), timestamp: new Date().toISOString(), project_id: projectId, component_id: componentId,
    model_key: `${projectId}::${componentId}`, outcome, evidence_level: evidenceLevel, evidence_weight: EVIDENCE_WEIGHT[evidenceLevel],
    revenue_usd_claimed: round(revenueUsd, 8), revenue_usd_verified: revenueVerified ? round(revenueUsd, 8) : 0,
    cost_usd: round(costUsd, 8), elapsed_ms: Math.round(elapsedMs), quality_score: round(quality), risk_score: round(risk),
    lesson_code: lessonCode, source_run_id: safe(identity.run_id, 80), source_ref: safe(body?.source_ref || "", 400),
    instruction_authority: false, raw_external_content_stored: false,
  };
}

function newModel(event) {
  return { project_id: event.project_id, component_id: event.component_id, model_key: event.model_key, trials: 0, successes: 0, failures: 0, blocked: 0,
    verified_revenue_usd: 0, claimed_unverified_revenue_usd: 0, verified_cost_usd: 0, elapsed_ms: 0,
    ema_signal: 0, ema_quality: 0.5, ema_risk: 0, lessons: { success: {}, failure: {}, blocked: {} }, recommendation: "EXPLORE", score: 0, last_event_at: null };
}

function recompute(model, totalEvents) {
  const trials = Math.max(1, model.trials);
  const successRate = model.successes / trials;
  const net = model.verified_revenue_usd - model.verified_cost_usd;
  const economics = Math.min(1, Math.log1p(Math.max(0, net)) / Math.log(11));
  const exploration = Math.min(1, Math.sqrt((2 * Math.log(Math.max(2, totalEvents + 1))) / Math.max(1, model.trials + 1)));
  const signal = clamp((model.ema_signal + 1) / 2, 0, 1);
  const score = clamp(economics * 40 + successRate * 25 + signal * 15 + exploration * 20 - model.ema_risk * 35, 0, 100);
  let recommendation = "EXPLORE";
  if (model.verified_revenue_usd > 0 && net > 0 && successRate >= 0.5 && model.ema_risk <= 0.35) recommendation = "ACCELERATE";
  else if (model.trials >= 12 && model.successes / model.trials < 0.2 && model.verified_revenue_usd === 0) recommendation = "KILL_CANDIDATE";
  else if (model.trials >= 6 && score < 35) recommendation = "HOLD";
  else if (score >= 60) recommendation = "KEEP_AND_OPTIMIZE";
  model.score = round(score, 2); model.recommendation = recommendation; model.success_rate = round(model.successes / trials, 4); model.net_verified_revenue_usd = round(net, 8);
}

export class GlobalLearningState {
  constructor(ctx, env) { this.ctx = ctx; this.env = env; }
  async state() {
    let s = await this.ctx.storage.get("state");
    if (!s) {
      s = { version: VERSION, global_id: GLOBAL_ID, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), generation: 1, event_count: 0,
        policy: { oidc_required: true, project_isolation: true, revenue_requires_verified_evidence: true, unverified_revenue_promotes_model: false, external_instruction_authority: false, autonomous_spend: false, autonomous_payment_activation: false }, models: {} };
      await this.ctx.storage.put("state", s);
    }
    return s;
  }
  async ingest(event) {
    const s = await this.state();
    const model = s.models[event.model_key] || newModel(event);
    const alpha = 0.2 * event.evidence_weight;
    let signal = 0;
    if (event.outcome === "SUCCESS") signal = 0.6;
    if (event.outcome === "REVENUE") signal = 1;
    if (event.outcome === "FAILURE") signal = -0.7;
    if (event.outcome === "BLOCKED") signal = -0.35;
    if (event.outcome !== "NEUTRAL") model.trials += 1;
    if (["SUCCESS", "REVENUE"].includes(event.outcome)) model.successes += 1;
    if (event.outcome === "FAILURE") model.failures += 1;
    if (event.outcome === "BLOCKED") model.blocked += 1;
    model.verified_revenue_usd = round(model.verified_revenue_usd + event.revenue_usd_verified, 8);
    model.claimed_unverified_revenue_usd = round(model.claimed_unverified_revenue_usd + Math.max(0, event.revenue_usd_claimed - event.revenue_usd_verified), 8);
    model.verified_cost_usd = round(model.verified_cost_usd + event.cost_usd, 8);
    model.elapsed_ms += event.elapsed_ms;
    model.ema_signal = round((1 - alpha) * model.ema_signal + alpha * signal, 4);
    model.ema_quality = round((1 - alpha) * model.ema_quality + alpha * event.quality_score, 4);
    model.ema_risk = round((1 - alpha) * model.ema_risk + alpha * event.risk_score, 4);
    model.last_event_at = event.timestamp;
    const bucket = event.outcome === "FAILURE" ? model.lessons.failure : event.outcome === "BLOCKED" ? model.lessons.blocked : ["SUCCESS", "REVENUE"].includes(event.outcome) ? model.lessons.success : null;
    if (bucket) bucket[event.lesson_code] = Number(bucket[event.lesson_code] || 0) + 1;
    s.event_count += 1; s.generation += 1; s.updated_at = event.timestamp; s.models[event.model_key] = model; recompute(model, s.event_count);
    await this.ctx.storage.put("state", s);
    const seq = String(s.event_count).padStart(12, "0"); await this.ctx.storage.put(`event:${seq}`, event);
    if (s.event_count > MAX_EVENTS) await this.ctx.storage.delete(`event:${String(s.event_count - MAX_EVENTS).padStart(12, "0")}`);
    return { state: s, model };
  }
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname.endsWith("/state")) return json({ ok: true, state: await this.state() });
    if (request.method === "POST" && url.pathname.endsWith("/event")) {
      const body = await request.json().catch(() => null); if (!body) return json({ ok: false, error: "invalid_json" }, 400);
      const identity = body.__identity || {}; delete body.__identity;
      try { const event = normalizeEvent(body, identity); const result = await this.ingest(event); return json({ ok: true, event, model: result.model, generation: result.state.generation, event_count: result.state.event_count }); }
      catch (e) { return json({ ok: false, error: safe(e?.message, 300) }, 400); }
    }
    return json({ ok: false, error: "not_found" }, 404);
  }
}

function stub(env) { const id = env.GLOBAL_LEARNING.idFromName(GLOBAL_ID); return env.GLOBAL_LEARNING.get(id); }

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") return json({ ok: true, service: "lsi-system-learning-bus-r1", version: VERSION, oidc_required_for_ingest: true, project_isolation: true, online_event_learning: true, persistent_lessons: true, revenue_requires_verified_evidence: true, money_movement: false, production_actions: false });
    if (request.method === "GET" && url.pathname === "/state") return stub(env).fetch(new Request(`https://internal/${GLOBAL_ID}/state`));
    if (request.method === "POST" && url.pathname === "/v1/events") {
      let identity; try { identity = await verifyGithubOidc(request); } catch (e) { return json({ ok: false, error: "oidc_denied", detail: safe(e?.message, 200) }, 401); }
      const body = await request.json().catch(() => null); if (!body) return json({ ok: false, error: "invalid_json" }, 400);
      body.__identity = identity;
      const response = await stub(env).fetch(new Request(`https://internal/${GLOBAL_ID}/event`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }));
      const data = await response.json(); return json({ ...data, identity: { repository: identity.repository, ref: identity.ref, run_id: identity.run_id }, production_actions: false, money_movement: false }, response.status);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
