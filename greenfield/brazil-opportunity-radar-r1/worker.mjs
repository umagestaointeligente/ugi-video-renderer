const VERSION = 'lsi-brazil-opportunity-radar-r1';
const COMPRAS_BASE = 'https://dadosabertos.compras.gov.br/modulo-contratacoes/1_consultarContratacoes_PNCP_14133';
const PNCP_OPEN_BASE = 'https://pncp.gov.br/api/consulta/v1/contratacoes/proposta';
const MELI_BASE = 'https://api.mercadolibre.com';

const PRICE_HINTS = {
  procurement_opportunity_feed_usd: 0.02,
  procurement_keyword_match_usd: 0.03,
  mercadolivre_trends_usd: 0.01
};

function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'access-control-allow-origin': '*',
      ...headers
    }
  });
}

function clampInt(value, min, max, fallback) {
  const n = Number.parseInt(String(value ?? ''), 10);
  return Number.isFinite(n) ? Math.max(min, Math.min(max, n)) : fallback;
}

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function compactDate(date) {
  return isoDate(date).replaceAll('-', '');
}

function shiftedDate(days) {
  const d = new Date();
  d.setUTCDate(d.getUTCDate() + days);
  return d;
}

function startDate(days) {
  return shiftedDate(-Math.max(0, days - 1));
}

function text(value) {
  return String(value ?? '').trim();
}

function numberFrom(row, keys) {
  for (const key of keys) {
    const value = row?.[key];
    const n = Number(value);
    if (Number.isFinite(n)) return n;
  }
  return null;
}

function first(row, keys) {
  for (const key of keys) {
    const value = row?.[key];
    if (value !== undefined && value !== null && text(value)) return value;
  }
  return null;
}

function extractRows(payload) {
  if (Array.isArray(payload)) return payload;
  const candidates = [payload?.resultado, payload?.resultados, payload?.results, payload?.data, payload?.content];
  for (const candidate of candidates) if (Array.isArray(candidate)) return candidate;
  return [];
}

function normalizedProcurement(row, source = 'Compras.gov.br / PNCP') {
  const object = first(row, ['objetoCompra', 'objeto', 'descricao', 'descricaoCompra', 'informacaoComplementar']);
  const estimated = numberFrom(row, ['valorTotalEstimado', 'valorEstimado', 'valorTotal', 'valorGlobal']);
  const published = first(row, ['dataPublicacaoPncp', 'dataPublicacao', 'dataAtualizacaoPncp']);
  const deadline = first(row, ['dataEncerramentoProposta', 'dataFimProposta', 'dataAberturaProposta']);
  const uf = first(row, ['unidadeOrgaoUfSigla', 'uf', 'ufSigla']) || row?.unidadeOrgao?.ufSigla || null;
  const org = first(row, ['orgaoEntidadeRazaoSocial', 'orgaoRazaoSocial', 'nomeOrgao']) || row?.orgaoEntidade?.razaoSocial || null;
  const unit = first(row, ['unidadeOrgaoNomeUnidade', 'nomeUnidade']) || row?.unidadeOrgao?.nomeUnidade || null;
  const modality = first(row, ['modalidadeNome', 'nomeModalidade', 'codigoModalidade']) || row?.modalidadeNome || null;
  const id = first(row, ['idCompra', 'numeroControlePNCP', 'numeroCompra']);
  const sourceUrl = first(row, ['linkSistemaOrigem', 'linkProcessoEletronico', 'urlCompra']);

  return {
    id,
    object,
    estimatedValueBRL: estimated,
    publishedAt: published,
    deadlineAt: deadline,
    uf,
    organization: org,
    unit,
    modality,
    sourceUrl,
    source
  };
}

function scoreOpportunity(item, query = '') {
  let score = 25;
  if (item.estimatedValueBRL && item.estimatedValueBRL > 0) score += Math.min(25, Math.log10(item.estimatedValueBRL + 1) * 5);
  if (item.deadlineAt) score += 10;
  if (item.sourceUrl) score += 5;
  if (item.source === 'PNCP — propostas abertas') score += 8;
  const q = text(query).toLowerCase();
  if (q) {
    const hay = `${item.object || ''} ${item.organization || ''} ${item.unit || ''}`.toLowerCase();
    const terms = q.split(/\s+/).filter(Boolean);
    const hitRatio = terms.length ? terms.filter(term => hay.includes(term)).length / terms.length : 0;
    score += hitRatio * 35;
  }
  return Math.round(Math.max(0, Math.min(100, score)));
}

function matchesQuery(item, query) {
  const q = text(query).toLowerCase();
  if (!q) return true;
  const hay = `${item.object || ''} ${item.organization || ''} ${item.unit || ''} ${item.modality || ''}`.toLowerCase();
  return q.split(/\s+/).filter(Boolean).every(term => hay.includes(term));
}

async function fetchComprasGov({ from, to, limit, uf, modalities, all, upstream }) {
  for (const modality of modalities.length ? modalities : ['5']) {
    const p = new URLSearchParams({
      pagina: '1',
      tamanhoPagina: String(Math.min(100, Math.max(limit * 3, 30))),
      dataPublicacaoPncpInicial: from,
      dataPublicacaoPncpFinal: to,
      codigoModalidade: modality
    });
    if (uf) p.set('unidadeOrgaoUfSigla', uf);
    const endpoint = `${COMPRAS_BASE}?${p.toString()}`;
    let response;
    try {
      response = await fetch(endpoint, { headers: { accept: 'application/json' }, cf: { cacheTtl: 300, cacheEverything: true } });
    } catch {
      upstream.push({ provider: 'Compras.gov.br', modality, status: 0 });
      continue;
    }
    upstream.push({ provider: 'Compras.gov.br', modality, status: response.status });
    if (!response.ok) continue;
    let payload;
    try { payload = await response.json(); } catch { continue; }
    for (const row of extractRows(payload)) all.push(normalizedProcurement(row, 'Compras.gov.br / PNCP'));
  }
}

async function fetchPncpOpen({ limit, uf, all, upstream }) {
  const dataFinal = compactDate(shiftedDate(45));
  const pncpModalities = ['8', '6', '4'];
  for (const modality of pncpModalities) {
    const p = new URLSearchParams({
      dataFinal,
      codigoModalidadeContratacao: modality,
      pagina: '1'
    });
    if (uf) p.set('uf', uf);
    const endpoint = `${PNCP_OPEN_BASE}?${p.toString()}`;
    let response;
    try {
      response = await fetch(endpoint, { headers: { accept: 'application/json' }, cf: { cacheTtl: 300, cacheEverything: true } });
    } catch {
      upstream.push({ provider: 'PNCP consulta direta', modality, status: 0 });
      continue;
    }
    upstream.push({ provider: 'PNCP consulta direta', modality, status: response.status });
    if (!response.ok) continue;
    let payload;
    try { payload = await response.json(); } catch { continue; }
    const rows = extractRows(payload);
    for (const row of rows.slice(0, Math.max(30, limit * 4))) all.push(normalizedProcurement(row, 'PNCP — propostas abertas'));
    if (all.length >= Math.max(30, limit * 4)) break;
  }
}

async function fetchProcurement(url, preview = false) {
  const days = clampInt(url.searchParams.get('days'), 1, 7, 2);
  const limit = clampInt(url.searchParams.get('limit'), 1, preview ? 3 : 50, preview ? 3 : 25);
  const q = text(url.searchParams.get('q')).slice(0, 120);
  const uf = text(url.searchParams.get('uf')).toUpperCase().slice(0, 2);
  const modalities = text(url.searchParams.get('modalities') || url.searchParams.get('modality') || '5')
    .split(',').map(x => x.trim()).filter(x => /^\d{1,2}$/.test(x)).slice(0, 3);

  const from = isoDate(startDate(days));
  const to = isoDate(new Date());
  const all = [];
  const upstream = [];

  await fetchComprasGov({ from, to, limit, uf, modalities, all, upstream });
  if (all.length < limit) await fetchPncpOpen({ limit, uf, all, upstream });

  const unique = new Map();
  for (const item of all) {
    const key = text(item.id) || `${item.object}|${item.organization}|${item.publishedAt}`;
    if (!unique.has(key)) unique.set(key, item);
  }

  const opportunities = [...unique.values()]
    .filter(item => matchesQuery(item, q))
    .map(item => ({ ...item, opportunityScore: scoreOpportunity(item, q) }))
    .sort((a, b) => b.opportunityScore - a.opportunityScore || (b.estimatedValueBRL || 0) - (a.estimatedValueBRL || 0))
    .slice(0, limit);

  return {
    ok: true,
    version: VERSION,
    source: 'official_open_data',
    provider: 'Compras.gov.br / PNCP',
    window: { from, to, days, openProposalHorizonDays: 45 },
    filters: { q: q || null, uf: uf || null, modalities: modalities.length ? modalities : ['5'] },
    count: opportunities.length,
    opportunities,
    upstream,
    pricingHintUsdPerCall: PRICE_HINTS.procurement_opportunity_feed_usd,
    financialOutcomeGuaranteed: false
  };
}

function timingSafeEqual(a, b) {
  const x = text(a), y = text(b);
  if (!x || x.length !== y.length) return false;
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x.charCodeAt(i) ^ y.charCodeAt(i);
  return diff === 0;
}

function paidAccessAuthorized(request, env) {
  const direct = text(env.LSI_ACCESS_KEY);
  const rapid = text(env.RAPIDAPI_PROXY_SECRET);
  const gotDirect = text(request.headers.get('x-lsi-access-key'));
  const gotRapid = text(request.headers.get('x-rapidapi-proxy-secret'));
  return (direct && timingSafeEqual(gotDirect, direct)) || (rapid && timingSafeEqual(gotRapid, rapid));
}

async function fetchMeliTrends(url, env) {
  const token = text(env.MELI_ACCESS_TOKEN);
  if (!token) return json({ ok: false, error: 'meli_access_token_not_configured', provider: 'Mercado Livre' }, 503);
  const site = text(url.searchParams.get('site') || 'MLB').toUpperCase();
  if (!/^ML[A-Z]$/.test(site)) return json({ ok: false, error: 'invalid_site' }, 400);
  const category = text(url.searchParams.get('category'));
  if (category && !/^ML[A-Z]\d+$/.test(category)) return json({ ok: false, error: 'invalid_category' }, 400);
  const endpoint = `${MELI_BASE}/trends/${site}${category ? `/${category}` : ''}`;
  const response = await fetch(endpoint, { headers: { Authorization: `Bearer ${token}`, accept: 'application/json' }, cf: { cacheTtl: 900, cacheEverything: true } });
  let payload = null;
  try { payload = await response.json(); } catch {}
  if (!response.ok) return json({ ok: false, error: 'meli_upstream_error', providerStatus: response.status }, 502);
  const rows = Array.isArray(payload) ? payload : [];
  return json({
    ok: true,
    version: VERSION,
    provider: 'Mercado Livre',
    site,
    category: category || null,
    updatedCadence: 'weekly_by_provider',
    total: rows.length,
    growth: rows.slice(0, 10),
    mostWanted: rows.slice(10, 30),
    popular: rows.slice(30, 50),
    pricingHintUsdPerCall: PRICE_HINTS.mercadolivre_trends_usd
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': 'content-type,x-lsi-access-key,x-rapidapi-proxy-secret', 'access-control-allow-methods': 'GET,OPTIONS' } });

    if (request.method === 'GET' && url.pathname === '/health') {
      return json({
        ok: true,
        service: 'LSI Brazil Opportunity Radar',
        version: VERSION,
        publicPreview: true,
        paidProcurementConfigured: Boolean(env.LSI_ACCESS_KEY || env.RAPIDAPI_PROXY_SECRET),
        mercadoLivreConfigured: Boolean(env.MELI_ACCESS_TOKEN),
        x402PayToConfigured: Boolean(env.X402_PAYTO),
        priceHints: PRICE_HINTS,
        piiCollected: false,
        moneyMovement: false
      });
    }

    if (request.method === 'GET' && url.pathname === '/v1/preview') {
      try { return json(await fetchProcurement(url, true)); }
      catch (error) { return json({ ok: false, error: 'upstream_unavailable', detail: String(error?.message || error).slice(0, 160) }, 502); }
    }

    if (request.method === 'GET' && url.pathname === '/v1/procurement') {
      if (!env.LSI_ACCESS_KEY && !env.RAPIDAPI_PROXY_SECRET) return json({ ok: false, error: 'paid_access_not_configured' }, 503);
      if (!paidAccessAuthorized(request, env)) return json({ ok: false, error: 'not_authorized' }, 401);
      try { return json(await fetchProcurement(url, false)); }
      catch (error) { return json({ ok: false, error: 'upstream_unavailable', detail: String(error?.message || error).slice(0, 160) }, 502); }
    }

    if (request.method === 'GET' && url.pathname === '/v1/latam/trends') {
      if (!paidAccessAuthorized(request, env)) {
        if (!env.LSI_ACCESS_KEY && !env.RAPIDAPI_PROXY_SECRET) return json({ ok: false, error: 'paid_access_not_configured' }, 503);
        return json({ ok: false, error: 'not_authorized' }, 401);
      }
      return fetchMeliTrends(url, env);
    }

    if (request.method === 'GET' && url.pathname === '/pricing') return json({ ok: true, version: VERSION, pricingHints: PRICE_HINTS, note: 'pricing targets are strategy metadata, not verified revenue' });

    return json({ ok: false, error: 'not_found' }, 404);
  }
};
