const SLUGS = ['nansen','anyspend','x402engine','coinmarketcap'];
export default {
  async fetch() {
    const out = [];
    for (const slug of SLUGS) {
      try {
        const r = await fetch(`https://x402-list.com/api/v1/services/${slug}`, {
          headers: { accept: 'application/json', 'user-agent': 'LSI-x402-Traction-Probe/1.0' }
        });
        const j = await r.json();
        const d = j?.data || {};
        const t = d?.assessment?.traction || {};
        out.push({
          slug,
          http: r.status,
          status: t.status ?? null,
          buyers30d: t.unique_buyers_30d ?? null,
          tx30d: t.tx_count_30d ?? null,
          volume30d: t.volume_usd_30d ?? null,
          topBuyerShare30d: t.top_buyer_share_30d ?? null,
          trend7dVs30d: t.trend_7d_vs_30d ?? null
        });
      } catch (e) {
        out.push({ slug, error: String(e?.message || e).slice(0,300) });
      }
    }
    return new Response(JSON.stringify({ok:true, source:'x402-list', samples:out}), {
      headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}
    });
  }
};