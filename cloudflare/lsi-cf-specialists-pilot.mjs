function txt(result) {
  const raw = result?.response ?? result?.result?.response ?? result?.result ?? result ?? '';
  return typeof raw === 'string' ? raw : JSON.stringify(raw);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== '/probe') return new Response('not found', { status: 404 });
    try {
      const started = Date.now();
      const [glm, gemma, flux] = await Promise.all([
        env.AI.run('@cf/zai-org/glm-4.7-flash', {
          messages: [{ role: 'user', content: 'Return exactly CF_GLM_OK' }],
          max_tokens: 32,
          temperature: 0,
        }),
        env.AI.run('@cf/google/gemma-4-26b-a4b-it', {
          messages: [{ role: 'user', content: 'Return exactly CF_GEMMA_OK' }],
          max_tokens: 32,
          temperature: 0,
        }),
        env.AI.run('@cf/black-forest-labs/flux-1-schnell', {
          prompt: 'minimal abstract sunrise gradient, no text',
          steps: 4,
        }),
      ]);
      const glmText = txt(glm);
      const gemmaText = txt(gemma);
      const fluxImage = flux?.image ?? flux?.result?.image ?? '';
      const out = {
        ok: glmText.includes('CF_GLM_OK') && gemmaText.includes('CF_GEMMA_OK') && String(fluxImage).length > 1000,
        glm_ok: glmText.includes('CF_GLM_OK'),
        gemma_ok: gemmaText.includes('CF_GEMMA_OK'),
        flux_ok: String(fluxImage).length > 1000,
        elapsed_ms: Date.now() - started,
        external_paid_provider: false,
      };
      return new Response(JSON.stringify(out), { status: out.ok ? 200 : 502, headers: { 'content-type': 'application/json' } });
    } catch (e) {
      return new Response(JSON.stringify({ ok: false, error: String(e?.message ?? e).slice(0, 500) }), { status: 502, headers: { 'content-type': 'application/json' } });
    }
  },
};
