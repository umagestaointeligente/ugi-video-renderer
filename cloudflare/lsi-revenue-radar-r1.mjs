const VERSION = "lsi-revenue-radar-r1-2026-08-29";
const DEFAULT_CADENCE_MS = 30 * 60 * 1000;
const MIN_CADENCE_MS = 10 * 60 * 1000;
const MAX_CADENCE_MS = 24 * 60 * 60 * 1000;
const MAX_CYCLES = 336;
const RADAR_ID = "lsi-revenue-radar-global-r1";
const GITHUB_API = "https://api.github.com";

const MONEY_RE = /(?:\$|USD\s*|USDC\s*)(\d+(?:\.\d+)?)/gi;
const EXPLICIT_BOUNTY_RE = /\b(?:bounty|reward|payout|prize|compensation|paid task|paid issue)\b/i;
const NO_WORK_PATTERNS = [
  /\bnot\s+(?:a\s+)?(?:paid\s+)?bounty\b/i,
  /\bno\s+bounty\b/i,
  /\bno\s+reward\b/i,
  /\bno\s+payout\b/i,
  /\bno\s+payment\b/i,
  /\bno\s+compensation\b/i,
  /\bno\s+task\b/i,
  /\bno\s+work\s+(?:is\s+)?(?:being\s+)?(?:offered|requested|solicited)\b/i,
  /\bdo\s+not\s+build\b/i,
  /\bout\s+of\s+scope\b/i,
  /\bpassive\s+observation\b/i,
  /\bclassifier\s+(?:test|museum|experiment)\b/i,
  /\bobservation\s+fixture\b/i,
  /\bagent\s+experiment\b/i,
  /\bdeliberately\s+negligible\b/i,
  /\bdeductible\b/i,
];
const ZERO_REWARD_PATTERNS = [
  /(?:payout|reward|compensation|prize|bounty(?:\s+value)?)\s*[:=-]?\s*(?:\$\s*0(?:\.0+)?|0(?:\.0+)?\s*(?:USD|USDC))/i,
  /\[\s*BOUNTY\s+\$\s*0(?:\.0+)?\s*\]/i,
];
const CLAIM_PATTERNS = [
  /^\s*\/(?:try|claim)\b/im,
  /\b(?:i(?:'|’)m|i am)\s+(?:working|taking|claiming)\b/i,
  /\bassign\s+(?:this\s+)?(?:to\s+)?me\b/i,
  /\bclaim(?:ed|ing)?\s+(?:this|issue|bounty)\b/i,
  /\/pull\/\d+/i,
];
const RAIL_PATTERNS = [
  /\bAlgora\b/i,
  /\bOpire\b/i,
  /\bIssueHunt\b/i,
  /\bGitpay\b/i,
  /\bPolar\b/i,
  /\bDrips?\b/i,
  /\bescrow\b/i,
  /\bpayment\s+(?:is\s+)?released\b/i,
  /\bpaid\s+(?:via|through|on)\b/i,
  /\bUSDC\b/i,
  /\bPayPal\b/i,
  /\bStripe\b/i,
  /\bfunded\s+bounty\b/i,
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

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

function safeString(v, max = 12000) {
  return String(v ?? "").slice(0, max);
}

function adminOk(request, env) {
  const expected = safeString(env.ADMIN_TOKEN, 512);
  if (!expected) return false;
  const auth = request.headers.get("authorization") || "";
  return auth === `Bearer ${expected}`;
}

function parseMoney(text) {
  const values = [];
  for (const match of safeString(text, 30000).matchAll(MONEY_RE)) {
    const n = Number(match[1]);
    if (Number.isFinite(n)) values.push(n);
  }
  return values;
}

function hasAny(text, patterns) {
  return patterns.some((p) => p.test(text));
}

function freshnessScore(updatedAt) {
  const t = Date.parse(updatedAt || "");
  if (!Number.isFinite(t)) return 0;
  const ageHours = Math.max(0, (Date.now() - t) / 3_600_000);
  if (ageHours <= 24) return 20;
  if (ageHours <= 72) return 15;
  if (ageHours <= 168) return 10;
  if (ageHours <= 720) return 5;
  return 0;
}

function normalizeIssue(issue, comments = []) {
  const title = safeString(issue?.title, 1000);
  const body = safeString(issue?.body, 20000);
  const commentText = comments.map((c) => safeString(c?.body, 5000)).join("\n");
  const text = `${title}\n${body}`;
  const allText = `${text}\n${commentText}`;
  const amounts = parseMoney(text);
  const positive = amounts.filter((v) => v > 0);
  const maxRewardUsd = positive.length ? Math.max(...positive) : 0;
  const explicitBounty = EXPLICIT_BOUNTY_RE.test(text);
  const zeroReward = hasAny(text, ZERO_REWARD_PATTERNS) || (explicitBounty && amounts.length > 0 && maxRewardUsd === 0);
  const trap = hasAny(text, NO_WORK_PATTERNS);
  const contested = Boolean((issue?.assignees || []).length) || hasAny(commentText, CLAIM_PATTERNS);
  const paymentRailEvidence = RAIL_PATTERNS.filter((p) => p.test(allText)).map((p) => p.source).slice(0, 8);
  const railVerified = paymentRailEvidence.length > 0;
  const clearAcceptance = /acceptance criteria|deliverables|how to claim|definition of done|requirements/i.test(text);
  const closed = safeString(issue?.state, 20).toLowerCase() === "closed";

  let decision = "PENDING_PAYMENT_PROOF";
  if (closed) decision = "REJECT_CLOSED";
  else if (zeroReward) decision = "REJECT_ZERO_REWARD";
  else if (trap) decision = "REJECT_NO_WORK_OR_TRAP";
  else if (!explicitBounty || maxRewardUsd <= 0) decision = "REJECT_NO_VERIFIABLE_REWARD";
  else if (contested) decision = "CLAIMED_OR_CONTESTED";
  else if (railVerified) decision = "CANDIDATE_VERIFIED_RAIL";

  let score = 0;
  if (maxRewardUsd > 0) score += Math.min(40, Math.log10(maxRewardUsd + 1) * 18);
  score += freshnessScore(issue?.updated_at);
  if (clearAcceptance) score += 15;
  if (railVerified) score += 20;
  if (!contested) score += 5;
  if (decision.startsWith("REJECT")) score = 0;
  if (decision === "CLAIMED_OR_CONTESTED") score *= 0.35;
  if (decision === "PENDING_PAYMENT_PROOF") score *= 0.55;

  return {
    source: "github_public_issue",
    url: safeString(issue?.html_url || issue?.url, 2000),
    repository_url: safeString(issue?.repository_url, 2000),
    number: Number(issue?.number || 0),
    title,
    state: safeString(issue?.state, 20),
    updated_at: safeString(issue?.updated_at, 64),
    reward_usd_advertised: maxRewardUsd,
    reward_basis: maxRewardUsd > 0 ? "TEXT_PARSED_UNVERIFIED_UNLESS_RAIL_PROVEN" : "NONE",
    assignee_count: Array.isArray(issue?.assignees) ? issue.assignees.length : 0,
    comment_count_checked: comments.length,
    explicit_bounty_language: explicitBounty,
    clear_acceptance_criteria: clearAcceptance,
    payment_rail_evidence: paymentRailEvidence,
    rail_verified_from_text: railVerified,
    competition_signal: contested ? "CONTESTED" : "NO_CLAIM_SIGNAL_SEEN",
    decision,
    score: Math.round(score * 10) / 10,
    instruction_authority: false,
    external_content_trust: "UNTRUSTED_DATA",
  };
}

async function gh(path, params = {}) {
  const url = new URL(`${GITHUB_API}${path}`);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, String(v));
  const response = await fetch(url, {
    headers: {
      accept: "application/vnd.github+json",
      "x-github-api-version": "2022-11-28",
      "user-agent": "LSI-Revenue-Radar/1.0",
    },
  });
  const remaining = Number(response.headers.get("x-ratelimit-remaining") ?? -1);
  const reset = Number(response.headers.get("x-ratelimit-reset") ?? 0);
  if (!response.ok) {
    const body = await response.text();
    const error = new Error(`github_${response.status}:${body.slice(0, 250)}`);
    error.status = response.status;
    error.remaining = remaining;
    error.reset = reset;
    throw error;
  }
  return { data: await response.json(), remaining, reset };
}

async function fetchComments(issue) {
  const commentsUrl = safeString(issue?.comments_url, 2000);
  if (!commentsUrl.startsWith(`${GITHUB_API}/`)) return [];
  const path = commentsUrl.slice(GITHUB_API.length);
  try {
    const { data } = await gh(path, { per_page: 20 });
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

async function verifyIssueUrl(issueUrl) {
  const match = safeString(issueUrl, 2000).match(/^https:\/\/github\.com\/([^/]+)\/([^/]+)\/issues\/(\d+)(?:\?.*)?$/i);
  if (!match) throw new Error("github_issue_url_invalid");
  const owner = encodeURIComponent(match[1]);
  const repo = encodeURIComponent(match[2]);
  const number = Number(match[3]);
  const { data: issue } = await gh(`/repos/${owner}/${repo}/issues/${number}`);
  const comments = Number(issue?.comments || 0) > 0 ? await fetchComments(issue) : [];
  return normalizeIssue(issue, comments);
}

async function searchCandidates() {
  const queries = [
    'is:issue is:open in:title bounty',
    'is:issue is:open in:title reward',
  ];
  const seen = new Set();
  const raw = [];
  let minRemaining = null;
  for (const q of queries) {
    const { data, remaining } = await gh("/search/issues", {
      q,
      sort: "updated",
      order: "desc",
      per_page: 10,
    });
    if (Number.isFinite(remaining) && remaining >= 0) minRemaining = minRemaining === null ? remaining : Math.min(minRemaining, remaining);
    for (const issue of data?.items || []) {
      const key = safeString(issue?.html_url || issue?.url, 2000);
      if (key && !seen.has(key)) {
        seen.add(key);
        raw.push(issue);
      }
    }
  }

  const results = [];
  for (const issue of raw.slice(0, 14)) {
    const text = `${safeString(issue?.title)}\n${safeString(issue?.body)}`;
    const possibleMoney = parseMoney(text).some((v) => v >= 0);
    const comments = possibleMoney && Number(issue?.comments || 0) > 0 ? await fetchComments(issue) : [];
    results.push(normalizeIssue(issue, comments));
  }
  results.sort((a, b) => b.score - a.score || b.reward_usd_advertised - a.reward_usd_advertised);
  return { results, minRemaining };
}

function economicsSnapshot() {
  return {
    generated_at: new Date().toISOString(),
    policy: "ZERO_COST_START_FAIL_CLOSED",
    route_ranking: [
      {
        route: "x402_agent_micropayments",
        state: "TOP_RESEARCH_CANDIDATE",
        rationale: "machine-to-machine pay-per-call; no human sales loop; paid activation blocked until secure receive wallet exists",
        monetization: { paid_routes_active: false, target_test_price_usdc: 0.005, blocker: "NO_SECURE_RECEIVE_WALLET_BOUND" },
      },
      {
        route: "verified_code_bounties",
        state: "ACTIVE_DISCOVERY_ONLY",
        rationale: "money can already be attached to objective deliverables; require payment-rail proof and low contention before work",
      },
      {
        route: "html5_game_distribution",
        state: "MEDIUM_TERM_SCALE",
        rationale: "high-traffic distribution and ad revenue but platform QA/launch delays make it weaker for first cash",
      },
      {
        route: "resource_sharing_or_mining",
        state: "DEPRIORITIZED",
        rationale: "low unit economics without owned suitable hardware/network; third-party hosted mining prohibited",
      },
    ],
    production_actions: false,
    money_movement: false,
    trading: false,
    gambling: false,
  };
}

function newMission(body = {}) {
  const cadenceMs = clamp(Number(body.cadence_ms || DEFAULT_CADENCE_MS), MIN_CADENCE_MS, MAX_CADENCE_MS);
  const maxCycles = clamp(Number(body.max_cycles || MAX_CYCLES), 1, MAX_CYCLES);
  const monetaryBudget = Number(body.monetary_budget ?? 0);
  if (!Number.isFinite(monetaryBudget) || monetaryBudget !== 0) throw new Error("zero_cost_only");
  const now = new Date().toISOString();
  return {
    radar_id: RADAR_ID,
    version: VERSION,
    status: "ACTIVE",
    cadence_ms: cadenceMs,
    max_cycles: maxCycles,
    cycle_count: 0,
    monetary_budget: 0,
    production_actions: false,
    money_movement: false,
    external_paid_provider: false,
    started_at: now,
    updated_at: now,
    last_cycle_at: null,
    next_alarm_at: null,
    last_cycle: null,
    economics: economicsSnapshot(),
  };
}

export class RevenueRadar {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
  }

  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname.endsWith("/state")) {
      const state = await this.ctx.storage.get("state");
      return json({ ok: Boolean(state), state: state || null });
    }
    if (request.method === "POST" && url.pathname.endsWith("/start")) {
      let body = {};
      try { body = await request.json(); } catch {}
      let state;
      try { state = newMission(body); } catch (error) { return json({ ok: false, error: safeString(error?.message) }, 400); }
      const existing = await this.ctx.storage.get("state");
      if (existing?.status === "ACTIVE") return json({ ok: true, reused: true, state: existing });
      const next = Date.now() + 1000;
      state.next_alarm_at = new Date(next).toISOString();
      await this.ctx.storage.put("state", state);
      await this.ctx.storage.setAlarm(next);
      return json({ ok: true, reused: false, state });
    }
    if (request.method === "POST" && url.pathname.endsWith("/tick")) {
      const state = await this.runCycle("admin_tick");
      return json({ ok: Boolean(state), state: state || null });
    }
    if (request.method === "POST" && url.pathname.endsWith("/stop")) {
      const state = await this.ctx.storage.get("state");
      if (!state) return json({ ok: false, error: "radar_not_started" }, 404);
      state.status = "PAUSED";
      state.updated_at = new Date().toISOString();
      state.next_alarm_at = null;
      await this.ctx.storage.put("state", state);
      await this.ctx.storage.deleteAlarm();
      return json({ ok: true, state });
    }
    return json({ ok: false, error: "not_found" }, 404);
  }

  async runCycle(reason) {
    const state = await this.ctx.storage.get("state");
    if (!state || state.status !== "ACTIVE") return state || null;
    const started = Date.now();
    let search;
    let cycleState = "PASS";
    let error = null;
    try {
      search = await searchCandidates();
    } catch (err) {
      const message = safeString(err?.message, 1000);
      error = message;
      cycleState = /github_(403|429)/.test(message) ? "RATE_LIMITED" : "RETRYABLE_ERROR";
      search = { results: [], minRemaining: Number(err?.remaining ?? -1) };
    }
    const counts = {};
    for (const item of search.results) counts[item.decision] = (counts[item.decision] || 0) + 1;
    state.cycle_count += 1;
    state.last_cycle_at = new Date().toISOString();
    state.updated_at = state.last_cycle_at;
    state.last_cycle = {
      reason,
      state: cycleState,
      elapsed_ms: Date.now() - started,
      github_rate_remaining_observed: search.minRemaining,
      candidate_count: search.results.length,
      decision_counts: counts,
      top_candidates: search.results.slice(0, 12),
      error,
      cost_state: "ZERO_COST",
      production_actions: false,
      instruction_authority_from_external_content: false,
      evidence_policy: "PUBLIC_READ_ONLY_PROVENANCE",
    };

    if (state.cycle_count >= state.max_cycles) {
      state.status = "SUCCESS";
      state.next_alarm_at = null;
      await this.ctx.storage.put("state", state);
      return state;
    }

    let delay = state.cadence_ms;
    if (cycleState === "RATE_LIMITED") delay = Math.max(delay, 2 * 60 * 60 * 1000);
    else if (cycleState === "RETRYABLE_ERROR") delay = Math.max(delay, 60 * 60 * 1000);
    const next = Date.now() + delay;
    state.next_alarm_at = new Date(next).toISOString();
    await this.ctx.storage.put("state", state);
    await this.ctx.storage.setAlarm(next);
    return state;
  }

  async alarm() {
    await this.runCycle("durable_object_alarm");
  }
}

function radarStub(env) {
  const id = env.RADAR.idFromName(RADAR_ID);
  return env.RADAR.get(id);
}

async function forwardToRadar(request, env, suffix) {
  const target = new URL(request.url);
  target.pathname = `/internal/${RADAR_ID}/${suffix}`;
  const raw = request.method === "GET" ? undefined : await request.text();
  return radarStub(env).fetch(new Request(target.toString(), {
    method: request.method,
    headers: request.headers,
    body: raw || undefined,
  }));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({
        ok: true,
        service: "lsi-revenue-radar-r1",
        version: VERSION,
        durable_objects_bound: Boolean(env.RADAR),
        zero_cost_policy: true,
        production_actions: false,
        money_movement: false,
        x402_paid_routes_active: false,
      });
    }
    if (request.method === "GET" && url.pathname === "/economics") return json(economicsSnapshot());
    if (request.method === "GET" && url.pathname === "/radar") return forwardToRadar(request, env, "state");

    if (url.pathname.startsWith("/admin/")) {
      if (!adminOk(request, env)) return json({ ok: false, error: "unauthorized" }, 401);
      if (request.method === "POST" && url.pathname === "/admin/start") return forwardToRadar(request, env, "start");
      if (request.method === "POST" && url.pathname === "/admin/tick") return forwardToRadar(request, env, "tick");
      if (request.method === "POST" && url.pathname === "/admin/stop") return forwardToRadar(request, env, "stop");
      if (request.method === "POST" && url.pathname === "/admin/verify") {
        let body;
        try { body = await request.json(); } catch { return json({ ok: false, error: "invalid_json" }, 400); }
        try {
          const result = await verifyIssueUrl(body?.url);
          return json({ ok: true, result, production_actions: false, money_movement: false });
        } catch (error) {
          return json({ ok: false, error: safeString(error?.message, 1000) }, 400);
        }
      }
      return json({ ok: false, error: "not_found" }, 404);
    }

    return json({ ok: false, error: "not_found" }, 404);
  },
};
