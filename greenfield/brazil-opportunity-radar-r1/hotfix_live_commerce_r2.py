from __future__ import annotations
import argparse, pathlib, re

INDEXNOW_KEY = "b71c8a3f6e2d4c1590af7381d9e64b2c"
RADAR_HOST = "lola-operacional-ugi.umagestaointeligente.workers.dev"


def once(text, token, name):
    n=text.count(token)
    if n!=1: raise SystemExit(f"HOTFIX_{name}_COUNT_{n}")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    src=pathlib.Path(a.source).read_text(encoding='utf-8')
    once(src,'const RADAR_PNCP_OPEN_BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta";','PNCP_CONST')
    once(src,'async function radarLiveFeed(url) {','LIVE_FEED')
    once(src,'// LSI Brazil Opportunity Radar — fixed Founder Pass; live data entitlement.','ROUTE_MARKER')
    if 'RADAR_COMMERCE_PERF_R2' in src: raise SystemExit('HOTFIX_ALREADY_APPLIED')

    src=src.replace(
      'const RADAR_PNCP_OPEN_BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta";',
      'const RADAR_PNCP_OPEN_BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta";\nconst RADAR_COMPRAS_BASE = "https://dadosabertos.compras.gov.br/modulo-contratacoes/1_consultarContratacoes_PNCP_14133";\nconst RADAR_COMMERCE_PERF_R2 = "parallel-official-data-2026-08-31";',1)

    replacement=r'''async function radarLiveFeed(url) {
  const started=Date.now();
  const limit=Math.max(1,Math.min(50,Number.parseInt(url.searchParams.get("limit")||"25",10)||25));
  const q=radarText(url.searchParams.get("q")).slice(0,120);
  const uf=radarText(url.searchParams.get("uf")).toUpperCase().slice(0,2);
  const all=[], upstream=[];
  const timeoutMs=5500;
  const timedFetch=async(endpoint)=>{const c=new AbortController(),timer=setTimeout(()=>c.abort(),timeoutMs);try{return await fetch(endpoint,{headers:{accept:"application/json"},signal:c.signal,cf:{cacheTtl:900,cacheEverything:true}})}finally{clearTimeout(timer)}};
  const end=new Date(); end.setUTCDate(end.getUTCDate()+45);
  const today=new Date(); const from=new Date(); from.setUTCDate(from.getUTCDate()-30);
  const compact=d=>d.toISOString().slice(0,10).replaceAll("-","");
  const iso=d=>d.toISOString().slice(0,10);

  const directTasks=["8","6","4"].map(async modality=>{
    const p=new URLSearchParams({dataFinal:compact(end),codigoModalidadeContratacao:modality,pagina:"1"}); if(uf)p.set("uf",uf);
    try{const r=await timedFetch(`${RADAR_PNCP_OPEN_BASE}?${p}`);let rows=[];if(r.ok){try{rows=radarRows(await r.json())}catch{}}return {provider:"PNCP propostas abertas",modality,status:r.status,rows};}catch(e){return {provider:"PNCP propostas abertas",modality,status:0,timeout:e?.name==="AbortError",rows:[]};}
  });
  const comprasTasks=["4","6","8"].map(async modality=>{
    const p=new URLSearchParams({pagina:"1",tamanhoPagina:"100",dataPublicacaoPncpInicial:iso(from),dataPublicacaoPncpFinal:iso(today),codigoModalidade:modality}); if(uf)p.set("unidadeOrgaoUfSigla",uf);
    try{const r=await timedFetch(`${RADAR_COMPRAS_BASE}?${p}`);let rows=[];if(r.ok){try{rows=radarRows(await r.json())}catch{}}return {provider:"Compras.gov.br",modality,status:r.status,rows};}catch(e){return {provider:"Compras.gov.br",modality,status:0,timeout:e?.name==="AbortError",rows:[]};}
  });
  const results=await Promise.all([...directTasks,...comprasTasks]);
  const now=Date.now();
  for(const result of results){
    upstream.push({provider:result.provider,modality:result.modality,status:result.status,timeout:Boolean(result.timeout)});
    for(const row of result.rows.slice(0,100)){
      const item=radarNormalize(row);
      item.source=result.provider==="Compras.gov.br"?"Compras.gov.br / PNCP":"PNCP — propostas abertas";
      if(item.deadlineAt){const deadline=Date.parse(item.deadlineAt);if(Number.isFinite(deadline)&&deadline+86400000<now)continue;}
      all.push(item);
    }
  }
  const unique=new Map();for(const item of all){const k=radarText(item.id)||`${item.object}|${item.organization}|${item.publishedAt}`;if(!unique.has(k))unique.set(k,item);}
  const opportunities=[...unique.values()].filter(x=>radarMatch(x,q,uf)).map(x=>({...x,opportunityScore:radarScore(x,q)})).sort((a,b)=>b.opportunityScore-a.opportunityScore||(b.estimatedValueBRL||0)-(a.estimatedValueBRL||0)).slice(0,limit);
  return {ok:true,version:RADAR_COMMERCE_EXTENSION_VERSION,performanceVersion:RADAR_COMMERCE_PERF_R2,provider:"PNCP + Compras.gov.br",query:q||null,uf:uf||null,count:opportunities.length,opportunities,upstream,elapsedMs:Date.now()-started,upstreamTimeoutMs:timeoutMs,access:"founder_pass",financialOutcomeGuaranteed:false};
}

async function radarGrant'''
    src,n=re.subn(r'async function radarLiveFeed\(url\) \{.*?\n\}\n\nasync function radarGrant',replacement,src,count=1,flags=re.S)
    if n!=1: raise SystemExit('HOTFIX_FEED_REPLACE_FAILED')

    # Improve search/social metadata without altering checkout behavior.
    meta_old='<title>LSI Brazil Opportunity Radar</title><meta name="description" content="Oportunidades públicas em aberto, filtradas e priorizadas em um radar vivo.">'
    meta_new='<title>Radar de Licitações e Oportunidades Públicas | LSI</title><meta name="description" content="Radar vivo de licitações, contratações e propostas abertas no Brasil. Filtre oportunidades públicas por palavra-chave e UF."><link rel="canonical" href="https://'+RADAR_HOST+'/brazil-opportunity-radar"><meta property="og:title" content="LSI Brazil Opportunity Radar"><meta property="og:description" content="Encontre licitações e oportunidades públicas antes do prazo."><meta property="og:type" content="website"><meta property="og:url" content="https://'+RADAR_HOST+'/brazil-opportunity-radar"><script type="application/ld+json">{"@context":"https://schema.org","@type":"SoftwareApplication","name":"LSI Brazil Opportunity Radar","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"19.90","priceCurrency":"BRL","description":"Founder Pass de 30 dias, sem renovação automática"}}</script>'
    once(src,meta_old,'LANDING_META')
    src=src.replace(meta_old,meta_new,1)

    marker='// LSI Brazil Opportunity Radar — fixed Founder Pass; live data entitlement.'
    extra=f'''// LSI Brazil Opportunity Radar — fixed Founder Pass; live data entitlement.\n      if (request.method === "GET" && path === "/{INDEXNOW_KEY}.txt") return new Response("{INDEXNOW_KEY}",{{status:200,headers:{{"Content-Type":"text/plain; charset=utf-8","Cache-Control":"public,max-age=86400"}}}});\n      if (request.method === "GET" && path === "/brazil-opportunity-radar-sitemap.xml") return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://{RADAR_HOST}/brazil-opportunity-radar</loc><changefreq>daily</changefreq><priority>0.9</priority></url></urlset>`,{{status:200,headers:{{"Content-Type":"application/xml; charset=utf-8","Cache-Control":"public,max-age=3600"}}}});\n      if (request.method === "GET" && path === "/greenfield/brazil-opportunity-radar/source-health") {{ try{{const probe=new URL(url);probe.search="?limit=3";const x=await radarLiveFeed(probe);return json({{ok:true,performanceVersion:x.performanceVersion,count:x.count,upstream:x.upstream,elapsedMs:x.elapsedMs,upstreamTimeoutMs:x.upstreamTimeoutMs}})}}catch(error){{return json({{ok:false,error:"source_probe_failed",detail:String(error?.message||error).slice(0,100)}},502)}} }}'''
    src=src.replace(marker,extra,1)

    for token in ['CHECKOUT_PAID','ASAAS_WEBHOOK_TOKEN','/api/commerce/webhook/asaas','/greenfield/packvalue-pro/checkout','RADAR_PRICE_BRL = 19.90','RADAR_ACCESS_TTL_MS = 30 * 24 * 60 * 60 * 1000']:
        if token not in src: raise SystemExit('HOTFIX_INVARIANT_MISSING:'+token)
    for token in ['RADAR_COMMERCE_PERF_R2','/greenfield/brazil-opportunity-radar/source-health',f'/{INDEXNOW_KEY}.txt','application/ld+json']:
        if token not in src: raise SystemExit('HOTFIX_NEW_GATE_MISSING:'+token)

    pathlib.Path(a.output).write_text(src,encoding='utf-8')
    print('RADAR_COMMERCE_PERFORMANCE_HOTFIX=PASS')
    print('PARALLEL_OFFICIAL_SOURCES=PASS')
    print('SOURCE_TIMEOUT_MS=5500')
    print('SEO_STRUCTURED_DATA=PASS')
    print('INDEXNOW_KEY_ROUTE=PASS')

if __name__=='__main__': main()
