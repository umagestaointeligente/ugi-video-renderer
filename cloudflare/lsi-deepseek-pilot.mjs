const MODEL = "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b";

function normalize(result) {
  const direct = result?.response ?? result?.result?.response;
  if (typeof direct === "string" && direct.trim()) return direct.trim();
  const message = result?.choices?.[0]?.message ?? result?.result?.choices?.[0]?.message;
  if (typeof message?.content === "string" && message.content.trim()) return message.content.trim();
  try { return JSON.stringify(result); } catch { return String(result ?? ""); }
}

export default {
  async fetch(request, env) {
    if (!env.AI) return Response.json({ ok: false, error: "AI_BINDING_MISSING" }, { status: 503 });
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({ ok: true, service: "lsi-deepseek-pilot", model: MODEL, production: false });
    }
    if (request.method !== "POST" || url.pathname !== "/probe") {
      return Response.json({ ok: false, error: "NOT_FOUND" }, { status: 404 });
    }
    const started = Date.now();
    try {
      const result = await env.AI.run(MODEL, {
        messages: [
          { role: "system", content: "You are an isolated zero-cost connectivity probe. Follow the user instruction exactly." },
          { role: "user", content: "Reply with exactly DEEPSEEK_OK and nothing else." }
        ],
        max_tokens: 64,
        temperature: 0
      });
      const text = normalize(result);
      return Response.json({
        ok: text.includes("DEEPSEEK_OK"),
        marker: text.includes("DEEPSEEK_OK") ? "DEEPSEEK_OK" : null,
        model: MODEL,
        elapsed_ms: Date.now() - started,
        production: false,
        external_paid_provider: false
      });
    } catch (error) {
      return Response.json({ ok: false, model: MODEL, error: String(error?.message ?? error), production: false }, { status: 500 });
    }
  }
};
