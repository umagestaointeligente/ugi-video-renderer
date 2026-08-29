const MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";
const VERSION = "lsi-zero-cost-broker-pilot-2026-08-28";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function authorized(request, env) {
  if (!env.PILOT_TOKEN) return false;
  return request.headers.get("authorization") === `Bearer ${env.PILOT_TOKEN}`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({
        ok: true,
        service: "lsi-zero-cost-broker-pilot",
        version: VERSION,
        workers_ai_bound: Boolean(env.AI),
        model: MODEL,
        production_publication: false,
        external_paid_provider: false,
      });
    }

    if (request.method === "POST" && url.pathname === "/probe") {
      if (!authorized(request, env)) {
        return json({ ok: false, error: "unauthorized" }, 401);
      }
      if (!env.AI) {
        return json({ ok: false, error: "workers_ai_binding_missing" }, 503);
      }

      const started = Date.now();
      try {
        const result = await env.AI.run(MODEL, {
          messages: [
            {
              role: "system",
              content: "You are a connectivity probe. Answer with exactly LSI_CF_AI_OK and nothing else.",
            },
            {
              role: "user",
              content: "Connectivity check.",
            },
          ],
          temperature: 0,
          max_tokens: 32,
        });

        const text = String(result?.response ?? result?.result?.response ?? "").trim();
        return json({
          ok: true,
          probe: "LSI_CF_AI_OK",
          provider: "cloudflare_workers_ai",
          model: MODEL,
          model_response_nonempty: text.length > 0,
          model_response_matches: text.includes("LSI_CF_AI_OK"),
          latency_ms: Date.now() - started,
          production_publication: false,
          secret_exposed: false,
        });
      } catch (error) {
        return json({
          ok: false,
          error: "workers_ai_probe_failed",
          message: String(error?.message ?? error).slice(0, 500),
          latency_ms: Date.now() - started,
        }, 502);
      }
    }

    return json({ ok: false, error: "not_found" }, 404);
  },
};
