import assert from 'node:assert/strict';
import worker from './worker.mjs';

const sampleProcurement = {
  resultado: [
    {
      numeroControlePNCP: '001/2026',
      objetoCompra: 'Aquisição de equipamentos de informática para unidades administrativas',
      valorTotalEstimado: 250000,
      dataPublicacaoPncp: '2026-08-30',
      dataEncerramentoProposta: '2026-09-05',
      unidadeOrgaoUfSigla: 'RJ',
      orgaoEntidadeRazaoSocial: 'Órgão Teste',
      unidadeOrgaoNomeUnidade: 'Unidade Teste',
      modalidadeNome: 'Pregão eletrônico',
      linkSistemaOrigem: 'https://example.gov.br/licitacao/1'
    },
    {
      numeroControlePNCP: '002/2026',
      objetoCompra: 'Serviços de manutenção predial',
      valorTotalEstimado: 80000,
      dataPublicacaoPncp: '2026-08-30',
      unidadeOrgaoUfSigla: 'SP',
      orgaoEntidadeRazaoSocial: 'Órgão Dois',
      modalidadeNome: 'Pregão eletrônico'
    }
  ]
};

const sampleOpenPncp = {
  data: [
    {
      numeroControlePNCP: '003/2026',
      objetoCompra: 'Aquisição de mobiliário corporativo',
      valorTotalEstimado: 480000,
      dataPublicacaoPncp: '2026-08-29',
      dataEncerramentoProposta: '2026-09-10',
      orgaoEntidade: { razaoSocial: 'Órgão PNCP' },
      unidadeOrgao: { ufSigla: 'MG', nomeUnidade: 'Unidade PNCP' },
      modalidadeNome: 'Concorrência',
      linkSistemaOrigem: 'https://example.gov.br/licitacao/3'
    }
  ]
};

const realFetch = globalThis.fetch;
globalThis.fetch = async (input, init = {}) => {
  const url = String(input);
  if (url.startsWith('https://dadosabertos.compras.gov.br/')) {
    return new Response(JSON.stringify(sampleProcurement), { status: 200, headers: { 'content-type': 'application/json' } });
  }
  if (url.startsWith('https://pncp.gov.br/api/consulta/v1/contratacoes/proposta')) {
    return new Response(JSON.stringify(sampleOpenPncp), { status: 200, headers: { 'content-type': 'application/json' } });
  }
  if (url.startsWith('https://api.mercadolibre.com/trends/')) {
    return new Response(JSON.stringify(Array.from({ length: 50 }, (_, i) => ({ keyword: `trend-${i + 1}`, url: `https://example.com/${i + 1}` }))), { status: 200, headers: { 'content-type': 'application/json' } });
  }
  return realFetch(input, init);
};

async function call(path, env = {}, headers = {}) {
  return worker.fetch(new Request(`https://local.test${path}`, { method: 'GET', headers }), env);
}

try {
  const health = await call('/health');
  assert.equal(health.status, 200);
  const h = await health.json();
  assert.equal(h.ok, true);
  assert.equal(h.version, 'lsi-brazil-opportunity-radar-r1');
  assert.equal(h.piiCollected, false);
  assert.equal(h.moneyMovement, false);

  const preview = await call('/v1/preview?days=2&limit=3&q=informática');
  assert.equal(preview.status, 200);
  const p = await preview.json();
  assert.equal(p.ok, true);
  assert.equal(p.count, 1);
  assert.match(p.opportunities[0].object, /informática/i);
  assert.equal(p.opportunities[0].estimatedValueBRL, 250000);
  assert.ok(p.opportunities[0].opportunityScore > 0);
  assert.ok(p.upstream.some(x => x.provider === 'PNCP consulta direta' && x.status === 200));

  const blocked = await call('/v1/procurement');
  assert.equal(blocked.status, 503);
  assert.equal((await blocked.json()).error, 'paid_access_not_configured');

  const authorized = await call('/v1/procurement?days=2&limit=5', { LSI_ACCESS_KEY: 'test-access-key' }, { 'x-lsi-access-key': 'test-access-key' });
  assert.equal(authorized.status, 200);
  const a = await authorized.json();
  assert.equal(a.ok, true);
  assert.ok(a.count >= 3);
  assert.ok(a.opportunities.some(x => x.source === 'PNCP — propostas abertas'));

  const unauthorized = await call('/v1/procurement', { LSI_ACCESS_KEY: 'test-access-key' }, { 'x-lsi-access-key': 'wrong' });
  assert.equal(unauthorized.status, 401);

  const meliMissing = await call('/v1/latam/trends', { LSI_ACCESS_KEY: 'test-access-key' }, { 'x-lsi-access-key': 'test-access-key' });
  assert.equal(meliMissing.status, 503);
  assert.equal((await meliMissing.json()).error, 'meli_access_token_not_configured');

  const meli = await call('/v1/latam/trends?site=MLB', { LSI_ACCESS_KEY: 'test-access-key', MELI_ACCESS_TOKEN: 'test-token' }, { 'x-lsi-access-key': 'test-access-key' });
  assert.equal(meli.status, 200);
  const m = await meli.json();
  assert.equal(m.total, 50);
  assert.equal(m.growth.length, 10);
  assert.equal(m.mostWanted.length, 20);
  assert.equal(m.popular.length, 20);

  const pricing = await call('/pricing');
  assert.equal(pricing.status, 200);
  const pr = await pricing.json();
  assert.match(pr.note, /not verified revenue/i);

  console.log('BRAZIL_OPPORTUNITY_RADAR_UNIT_QA=PASS');
  console.log('PNCP_OPEN_PROPOSAL_FALLBACK=PASS');
  console.log('FAIL_CLOSED_PAID_ACCESS=PASS');
  console.log('MELI_OAUTH_GATE=PASS');
  console.log('PII_COLLECTED=false');
  console.log('MONEY_MOVEMENT=false');
} finally {
  globalThis.fetch = realFetch;
}
