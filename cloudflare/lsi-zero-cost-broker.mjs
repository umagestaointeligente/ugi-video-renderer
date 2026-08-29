const MODEL_ROUTES = Object.freeze({
  cheap_text: "@cf/meta/llama-3.1-8b-instruct-fast",
  fast_text: "@cf/zai-org/glm-4.7-flash",
  structured_json: "@cf/zai-org/glm-4.7-flash",
  deep_text: "@cf/google/gemma-4-26b-a4b-it",
});
const DEFAULT_ROLE = "cheap_text";
const VERSION = "lsi-zero-cost-broker-r2-specialist-router-2026-08-29";
const OIDC_ISSUER = "https://token.actions.githubusercontent.com";
const OIDC_AUDIENCE = "lsi-zero-cost-broker";
const ALLOWED_REPOSITORY = "umagestaointeligente/ugi-video-renderer";
const MAX_TASKS = 8;
const MAX_PROMPT_CHARS = 16000;
const MAX_OUTPUT_TOKENS = 900;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function b64urlToBytes(value) {
  const base64 = value.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (value.length % 4)) % 4);
  const raw = atob(base64);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}

function bytesToB64url(bytes) {
  let raw = "";
  const view = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  for (let i = 0; i < view.length; i++) raw += String.fromCharCode(view[i]);
  return btoa(raw).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function decodeJwtPart(part) {
  return JSON.parse(new TextDecoder().decode(b64urlToBytes(part)));
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
  const configResp = await fetch(`${OIDC_ISSUER}/.well-known/openid-configuration`, { cf: { cacheTtl: 3600 } });
  if (!configResp.ok) throw new Error("oidc_config_unavailable");
  const config = await configResp.json();
  const jwksResp = await fetch(config.jwks_uri, { cf: { cacheTtl: 3600 } });
  if (!jwksResp.ok) throw new Error("oidc_jwks_unavailable");
  const jwks = await jwksResp.json();
  const jwk = (jwks.keys || []).find((key) => key.kid === header.kid);
  if (!jwk) throw new Error("oidc_kid_not_found");
  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const signed = new TextEncoder().encode(`${parts[0]}.${parts[1]}`);
  const signature = b64urlToBytes(parts[2]);
  const verified = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, signature, signed);
  if (!verified) throw new Error("oidc_signature_invalid");
  const now = Math.floor(Date.now() / 1000);
  if (claims.iss !== OIDC_ISSUER) throw new Error("oidc_issuer_invalid");
  const aud = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!aud.includes(OIDC_AUDIENCE)) throw new Error("oidc_audience_invalid");
  if (!claims.exp || claims.exp < now - 30) throw new Error("oidc_expired");
  if (claims.nbf && claims.nbf > now + 30) throw new Error("oidc_not_yet_valid");
  if (claims.repository !== ALLOWED_REPOSITORY) throw new Error("oidc_repository_denied");
  if (!String(claims.ref || "").startsWith("refs/heads/lsi-broker-job-")) throw new Error("oidc_ref_denied");
  if (claims.event_name && claims.event_name !== "push") throw new Error("oidc_event_denied");
  return { repository: claims.repository, ref: claims.ref, run_id: claims.run_id || null };
}

async function importBrokerPrivateKey(env) {
  if (!env.BROKER_PRIVATE_JWK) throw new Error("broker_private_key_missing");
  const jwk = JSON.parse(env.BROKER_PRIVATE_JWK);
  return crypto.subtle.importKey("jwk", jwk, { name: "RSA-OAEP", hash: "SHA-256" }, false, ["decrypt"]);
}

async function decryptEnvelope(envelope, env) {
  if (!envelope || envelope.alg !== "RSA-OAEP-256+A256GCM") throw new Error("envelope_alg_invalid");
  const privateKey = await importBrokerPrivateKey(env);
  const aesRaw = await crypto.subtle.decrypt({ name: "RSA-OAEP" }, privateKey, b64urlToBytes(envelope.wrapped_key));
  const aesKey = await crypto.subtle.importKey("raw", aesRaw, { name: "AES-GCM" }, false, ["decrypt"]);
  const aad = b64urlToBytes(envelope.aad || "");
  const plaintext = await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64urlToBytes(envelope.iv), additionalData: aad, tagLength: 128 }, aesKey, b64urlToBytes(envelope.ciphertext));
  return JSON.parse(new TextDecoder().decode(plaintext));
}

async function encryptEnvelope(payload, responsePublicJwk, aadText) {
  const publicKey = await crypto.subtle.importKey("jwk", responsePublicJwk, { name: "RSA-OAEP", hash: "SHA-256" }, false, ["encrypt"]);
  const aesRaw = crypto.getRandomValues(new Uint8Array(32));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const aad = new TextEncoder().encode(aadText);
  const aesKey = await crypto.subtle.importKey("raw", aesRaw, { name: "AES-GCM" }, false, ["encrypt"]);
  const plaintext = new TextEncoder().encode(JSON.stringify(payload));
  const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv, additionalData: aad, tagLength: 128 }, aesKey, plaintext);
  const wrapped = await crypto.subtle.encrypt({ name: "RSA-OAEP" }, publicKey, aesRaw);
  return { alg: "RSA-OAEP-256+A256GCM", wrapped_key: bytesToB64url(wrapped), iv: bytesToB64url(iv), aad: bytesToB64url(aad), ciphertext: bytesToB64url(ciphertext) };
}

export function resolveRole(role) {
  const normalized = String(role || DEFAULT_ROLE).trim().toLowerCase();
  const model = MODEL_ROUTES[normalized];
  if (!model) throw new Error(`task_role_not_allowed:${normalized || "empty"}`);
  return { role: normalized, model };
}

function validatePayload(payload) {
  if (!payload || !Array.isArray(payload.tasks)) throw new Error("tasks_required");
  if (payload.tasks.length < 1 || payload.tasks.length > MAX_TASKS) throw new Error("task_count_out_of_range");
  for (const task of payload.tasks) {
    if (!task || typeof task.id !== "string" || !task.id) throw new Error("task_id_required");
    if (Object.prototype.hasOwnProperty.call(task, "model")) throw new Error(`task_model_override_forbidden:${task.id}`);
    resolveRole(task.role);
    const system = String(task.system || "");
    const user = String(task.user || "");
    if (!user) throw new Error(`task_user_required:${task.id}`);
    if (system.length + user.length > MAX_PROMPT_CHARS) throw new Error(`task_prompt_too_large:${task.id}`);
    const maxTokens = Number(task.max_tokens ?? 500);
    if (!Number.isFinite(maxTokens) || maxTokens < 1 || maxTokens > MAX_OUTPUT_TOKENS) throw new Error(`task_max_tokens_invalid:${task.id}`);
  }
}

function normalizeModelOutput(result) {
  const direct = result?.response ?? result?.result?.response;
  if (typeof direct === "string" && direct.trim()) return direct.trim();

  const message = result?.choices?.[0]?.message ?? result?.result?.choices?.[0]?.message;
  if (message) {
    const content = message.content;
    if (typeof content === "string" && content.trim()) return content.trim();
    if (Array.isArray(content)) {
      const joined = content
        .map((part) => typeof part === "string" ? part : (part?.text ?? part?.content ?? ""))
        .filter(Boolean)
        .join("\n")
        .trim();
      if (joined) return joined;
    }
    return "";
  }

  const raw = result?.result ?? result ?? "";
  if (typeof raw === "string") return raw.trim();
  try { return JSON.stringify(raw); } catch { return String(raw); }
}

async function executeTask(task, env) {
  const started = Date.now();
  let route;
  try {
    route = resolveRole(task.role);
    const result = await env.AI.run(route.model, {
      messages: [...(task.system ? [{ role: "system", content: String(task.system) }] : []), { role: "user", content: String(task.user) }],
      temperature: Math.max(0, Math.min(1, Number(task.temperature ?? 0.2))),
      max_tokens: Math.min(MAX_OUTPUT_TOKENS, Number(task.max_tokens ?? 500)),
    });
    const text = normalizeModelOutput(result);
    if (!text) throw new Error("empty_model_output");
    return { id: task.id, ok: true, role: route.role, text, latency_ms: Date.now() - started, model: route.model };
  } catch (error) {
    return { id: task.id, ok: false, role: route?.role || String(task.role || DEFAULT_ROLE), error: String(error?.message ?? error).slice(0, 500), latency_ms: Date.now() - started, model: route?.model || null };
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, service: "lsi-zero-cost-broker", version: VERSION, workers_ai_bound: Boolean(env.AI), broker_key_configured: Boolean(env.BROKER_PRIVATE_JWK), default_role: DEFAULT_ROLE, role_models: MODEL_ROUTES, max_parallel_tasks: MAX_TASKS, production_publication: false, external_paid_provider: false });
    }
    if (request.method === "POST" && url.pathname === "/v1/execute") {
      if (!env.AI) return json({ ok: false, error: "workers_ai_binding_missing" }, 503);
      let identity;
      try { identity = await verifyGithubOidc(request); } catch (error) { return json({ ok: false, error: "oidc_denied", detail: String(error?.message ?? error) }, 401); }
      let body;
      try { body = await request.json(); } catch { return json({ ok: false, error: "invalid_json" }, 400); }
      const missionId = String(body?.mission_id || "");
      if (!/^[A-Za-z0-9._-]{8,120}$/.test(missionId)) return json({ ok: false, error: "mission_id_invalid" }, 400);
      if (!body?.response_public_jwk) return json({ ok: false, error: "response_public_jwk_required" }, 400);
      let payload;
      try { payload = await decryptEnvelope(body.encrypted, env); validatePayload(payload); } catch (error) { return json({ ok: false, error: "payload_decrypt_or_validate_failed", detail: String(error?.message ?? error) }, 400); }
      const started = Date.now();
      const results = await Promise.all(payload.tasks.map((task) => executeTask(task, env)));
      const modelsUsed = [...new Set(results.filter((x) => x.model).map((x) => x.model))];
      const responsePayload = { schema_version: "1.1", mission_id: missionId, provider: "cloudflare_workers_ai", router: "allowlisted_role_router", default_role: DEFAULT_ROLE, models_used: modelsUsed, zero_cost_route: true, external_paid_provider: false, identity: { repository: identity.repository, ref: identity.ref, run_id: identity.run_id }, task_count: results.length, success_count: results.filter((x) => x.ok).length, elapsed_ms: Date.now() - started, results };
      try {
        const encrypted = await encryptEnvelope(responsePayload, body.response_public_jwk, missionId);
        return json({ ok: true, schema_version: "1.1", mission_id: missionId, encrypted, plaintext_returned: false });
      } catch (error) {
        return json({ ok: false, error: "response_encrypt_failed", detail: String(error?.message ?? error) }, 500);
      }
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
