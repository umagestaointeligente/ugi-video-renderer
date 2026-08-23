const PROJECT = "UGI";
const OWNER = "umagestaointeligente";
const REPO = "ugi-video-renderer";
const DEFAULT_BRANCH = "main";
const ALLOWED_WORKFLOWS = new Set([
  "actions-health.yml",
  "ugi-growth-policy-smoke.yml",
  "render-video.yml",
  "deploy-cloudflare-worker.yml",
  "deploy-ugi-admin-bridge.yml"
]);
const GITHUB_API = "https://api.github.com";
const USER_AGENT = "lola-github-admin-bridge-ugi/1.1";
const UPSTREAM_TIMEOUT_MS = 15000;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff"
    }
  });
}

function redact(message) {
  return String(message || "error")
    .replace(/Bearer\s+[A-Za-z0-9._~+\/-]+/gi, "Bearer [REDACTED]")
    .replace(/-----BEGIN[\s\S]*?-----END[^-]*-----/g, "[REDACTED_KEY]")
    .slice(0, 1200);
}

function b64urlBytes(bytes) {
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function b64urlText(text) {
  return b64urlBytes(new TextEncoder().encode(text));
}

function pemBodyToBytes(pem, label) {
  const clean = String(pem || "")
    .replace(`-----BEGIN ${label}-----`, "")
    .replace(`-----END ${label}-----`, "")
    .replace(/\s+/g, "");
  const raw = atob(clean);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
  return bytes;
}

function derLength(n) {
  if (n < 128) return Uint8Array.of(n);
  const out = [];
  let v = n;
  while (v > 0) { out.unshift(v & 255); v >>= 8; }
  return Uint8Array.of(0x80 | out.length, ...out);
}

function der(tag, body) {
  const len = derLength(body.length);
  const out = new Uint8Array(1 + len.length + body.length);
  out[0] = tag;
  out.set(len, 1);
  out.set(body, 1 + len.length);
  return out;
}

function concatBytes(...parts) {
  const total = parts.reduce((n, p) => n + p.length, 0);
  const out = new Uint8Array(total);
  let off = 0;
  for (const p of parts) { out.set(p, off); off += p.length; }
  return out;
}

function pkcs1ToPkcs8(pkcs1) {
  const version = Uint8Array.of(0x02, 0x01, 0x00);
  const rsaAlgId = Uint8Array.of(
    0x30, 0x0d,
    0x06, 0x09, 0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x01,
    0x05, 0x00
  );
  const privateKey = der(0x04, pkcs1);
  return der(0x30, concatBytes(version, rsaAlgId, privateKey));
}

function pemToPkcs8ArrayBuffer(pem) {
  const text = String(pem || "").trim();
  if (text.includes("-----BEGIN PRIVATE KEY-----")) {
    return pemBodyToBytes(text, "PRIVATE KEY").buffer;
  }
  if (text.includes("-----BEGIN RSA PRIVATE KEY-----")) {
    return pkcs1ToPkcs8(pemBodyToBytes(text, "RSA PRIVATE KEY")).buffer;
  }
  throw new Error("unsupported GitHub App private key format");
}

async function timingSafeEqual(a, b) {
  const x = new TextEncoder().encode(String(a || ""));
  const y = new TextEncoder().encode(String(b || ""));
  if (x.length !== y.length) return false;
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

async function requireAuth(request, env) {
  const header = request.headers.get("authorization") || "";
  if (!header.startsWith("Bearer ")) return false;
  return timingSafeEqual(header.slice(7), env.BRIDGE_AUTH_SECRET || "");
}

function requiredSecretState(env) {
  return {
    GITHUB_APP_ID: Boolean(env.GITHUB_APP_ID),
    GITHUB_INSTALLATION_ID: Boolean(env.GITHUB_INSTALLATION_ID),
    GITHUB_APP_PRIVATE_KEY: Boolean(env.GITHUB_APP_PRIVATE_KEY),
    BRIDGE_AUTH_SECRET: Boolean(env.BRIDGE_AUTH_SECRET)
  };
}

async function githubJwt(env) {
  if (!env.GITHUB_APP_ID || !env.GITHUB_APP_PRIVATE_KEY) {
    throw new Error("required GitHub App credentials are not configured");
  }
  const now = Math.floor(Date.now() / 1000);
  const header = b64urlText(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const payload = b64urlText(JSON.stringify({ iat: now - 30, exp: now + 540, iss: String(env.GITHUB_APP_ID) }));
  const unsigned = `${header}.${payload}`;
  const key = await crypto.subtle.importKey(
    "pkcs8",
    pemToPkcs8ArrayBuffer(env.GITHUB_APP_PRIVATE_KEY),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign(
    { name: "RSASSA-PKCS1-v1_5" },
    key,
    new TextEncoder().encode(unsigned)
  );
  return `${unsigned}.${b64urlBytes(new Uint8Array(signature))}`;
}

async function ghFetch(url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), UPSTREAM_TIMEOUT_MS);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    const text = await response.text();
    let body = null;
    try { body = text ? JSON.parse(text) : null; } catch { body = { raw: text.slice(0, 500) }; }
    return { response, body };
  } finally {
    clearTimeout(timer);
  }
}

async function installationToken(env) {
  if (!env.GITHUB_INSTALLATION_ID) throw new Error("GITHUB_INSTALLATION_ID not configured");
  const jwt = await githubJwt(env);
  const { response, body } = await ghFetch(
    `${GITHUB_API}/app/installations/${encodeURIComponent(env.GITHUB_INSTALLATION_ID)}/access_tokens`,
    {
      method: "POST",
      headers: {
        authorization: `Bearer ${jwt}`,
        accept: "application/vnd.github+json",
        "x-github-api-version": "2022-11-28",
        "user-agent": USER_AGENT
      }
    }
  );
  if (!response.ok || !body?.token) {
    throw new Error(`installation token failed: ${response.status} ${JSON.stringify(body)}`);
  }
  return body.token;
}

async function repoRequest(env, path, init = {}) {
  const token = await installationToken(env);
  return ghFetch(`${GITHUB_API}/repos/${OWNER}/${REPO}${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${token}`,
      accept: "application/vnd.github+json",
      "x-github-api-version": "2022-11-28",
      "user-agent": USER_AGENT,
      ...(init.headers || {})
    }
  });
}

function validateWorkflowName(name) {
  const value = String(name || "").trim();
  if (!ALLOWED_WORKFLOWS.has(value)) throw new Error("workflow is not allowlisted");
  return value;
}

async function readJsonLimited(request) {
  const length = Number(request.headers.get("content-length") || 0);
  if (length > 12000) throw new Error("request body too large");
  const text = await request.text();
  if (text.length > 12000) throw new Error("request body too large");
  return text ? JSON.parse(text) : {};
}

async function diagnostics(env) {
  const token = await installationToken(env);
  const { response, body } = await ghFetch(`${GITHUB_API}/repos/${OWNER}/${REPO}`, {
    headers: {
      authorization: `Bearer ${token}`,
      accept: "application/vnd.github+json",
      "x-github-api-version": "2022-11-28",
      "user-agent": USER_AGENT
    }
  });
  if (!response.ok) throw new Error(`repository verification failed: ${response.status}`);
  const locked = body?.full_name === `${OWNER}/${REPO}` && body?.default_branch === DEFAULT_BRANCH;
  if (!locked) throw new Error("repository hard lock verification failed");
  return {
    ok: true,
    project: PROJECT,
    repository: `${OWNER}/${REPO}`,
    default_branch: DEFAULT_BRANCH,
    repository_lock_ok: true,
    installation_auth_ok: true,
    fail_closed: true,
    workflow_allowlist: [...ALLOWED_WORKFLOWS]
  };
}

export default {
  async fetch(request, env) {
    const requestId = crypto.randomUUID();
    const url = new URL(request.url);
    try {
      if (request.method === "GET" && url.pathname === "/health") {
        const secrets = requiredSecretState(env);
        const ok = Object.values(secrets).every(Boolean);
        return json({
          ok,
          project: PROJECT,
          worker: "lola-github-admin-bridge-ugi",
          repository: `${OWNER}/${REPO}`,
          default_branch: DEFAULT_BRANCH,
          required_secrets_configured: secrets,
          github_called: false,
          secrets_exposed: false,
          fail_closed: true,
          request_id: requestId
        }, ok ? 200 : 503);
      }

      if (!(await requireAuth(request, env))) {
        return json({ ok: false, error: "unauthorized", request_id: requestId }, 401);
      }

      if (request.method === "GET" && url.pathname === "/diagnostics") {
        return json({ ...(await diagnostics(env)), request_id: requestId });
      }

      if (request.method === "GET" && url.pathname === "/github/actions/status") {
        const { response, body } = await repoRequest(env, "/actions/permissions");
        return json({ ok: response.ok, repository: `${OWNER}/${REPO}`, status: body, request_id: requestId }, response.ok ? 200 : 502);
      }

      if (request.method === "GET" && url.pathname === "/github/workflows") {
        const { response, body } = await repoRequest(env, "/actions/workflows?per_page=100");
        return json({ ok: response.ok, repository: `${OWNER}/${REPO}`, workflows: body?.workflows || [], request_id: requestId }, response.ok ? 200 : 502);
      }

      if (request.method === "GET" && url.pathname === "/github/workflows/runs") {
        const { response, body } = await repoRequest(env, "/actions/runs?per_page=30");
        return json({ ok: response.ok, repository: `${OWNER}/${REPO}`, runs: body?.workflow_runs || [], request_id: requestId }, response.ok ? 200 : 502);
      }

      if (request.method === "GET" && url.pathname === "/github/workflows/jobs") {
        const runId = url.searchParams.get("run_id");
        if (!/^\d{1,20}$/.test(runId || "")) return json({ ok: false, error: "valid run_id required", request_id: requestId }, 400);
        const { response, body } = await repoRequest(env, `/actions/runs/${runId}/jobs?per_page=100`);
        return json({ ok: response.ok, run_id: runId, total_jobs: body?.total_count ?? null, jobs: body?.jobs || [], request_id: requestId }, response.ok ? 200 : 502);
      }

      if (request.method === "GET" && url.pathname === "/github/pipeline/health") {
        const diag = await diagnostics(env);
        const { response, body } = await repoRequest(env, "/actions/workflows/actions-health.yml/runs?per_page=1");
        const run = body?.workflow_runs?.[0] || null;
        return json({ ok: response.ok && Boolean(run), diagnostics: diag, latest_actions_health_run: run, request_id: requestId }, response.ok && run ? 200 : 503);
      }

      if (request.method === "POST" && url.pathname === "/github/actions/enable") {
        const { response, body } = await repoRequest(env, "/actions/permissions", {
          method: "PUT",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ enabled: true, allowed_actions: "all" })
        });
        return json({ ok: response.ok, repository: `${OWNER}/${REPO}`, result: body, request_id: requestId }, response.ok ? 200 : 502);
      }

      if (request.method === "POST" && url.pathname === "/github/workflows/dispatch") {
        const input = await readJsonLimited(request);
        const workflow = validateWorkflowName(input.workflow);
        const ref = String(input.ref || DEFAULT_BRANCH);
        if (ref !== DEFAULT_BRANCH) return json({ ok: false, error: "ref not allowed", request_id: requestId }, 400);
        const inputs = input.inputs && typeof input.inputs === "object" ? input.inputs : {};
        if (JSON.stringify(inputs).length > 8000) return json({ ok: false, error: "inputs too large", request_id: requestId }, 400);
        const { response, body } = await repoRequest(env, `/actions/workflows/${encodeURIComponent(workflow)}/dispatches`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ ref, inputs })
        });
        return json({ ok: response.status === 204, workflow, ref, dispatch_status: response.status, upstream: body, request_id: requestId }, response.status === 204 ? 202 : 502);
      }

      if (request.method === "POST" && url.pathname === "/github/recovery/repair") {
        const input = await readJsonLimited(request);
        const workflow = validateWorkflowName(input.workflow || "actions-health.yml");
        const { response, body } = await repoRequest(env, `/actions/workflows/${encodeURIComponent(workflow)}/dispatches`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ ref: DEFAULT_BRANCH, inputs: input.inputs && typeof input.inputs === "object" ? input.inputs : {} })
        });
        return json({ ok: response.status === 204, recovery: "controlled_workflow_dispatch", workflow, request_id: requestId, upstream: body }, response.status === 204 ? 202 : 502);
      }

      return json({ ok: false, error: "not_found", request_id: requestId }, 404);
    } catch (error) {
      return json({ ok: false, fail_closed: true, error: redact(error?.message || error), request_id: requestId }, 500);
    }
  }
};
