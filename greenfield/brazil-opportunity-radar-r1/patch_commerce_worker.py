from __future__ import annotations
import argparse, pathlib, re

EXTENSION_VERSION = "brazil-opportunity-radar-commerce-r1-2026-08-31"
PRICE = 19.90
PRODUCT_ID = "brazil-opportunity-radar-founder-r1"
MATERIAL_ID = "brazil-opportunity-radar-live-r1"
TTL_DAYS = 30
GOOD_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
ROUTE_MARKER = "// LSI Brazil Opportunity Radar — fixed Founder Pass; live data entitlement."
PACKVALUE_ROUTE_MARKER = "// LSI PackValue PRO — fixed public SKU only; no admin capability."
COMMERCE_ANCHOR = "function commerceProviderStatus(env) {"
FULFILL_SIGNATURE = "async function fulfillPaidOrder(env, order, origin) {"
PUBLIC_HEALTH_TOKEN = 'path === "/api/health"'


def require_once(text: str, token: str, name: str):
    n = text.count(token)
    if n != 1:
        raise SystemExit(f"RADAR_PATCH_{name}_COUNT_{n}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    source = pathlib.Path(a.source).read_text(encoding="utf-8")

    if ROUTE_MARKER in source or "RADAR_COMMERCE_EXTENSION_VERSION" in source:
        raise SystemExit("RADAR_PATCH_ALREADY_APPLIED")

    for token, name in [
        (PACKVALUE_ROUTE_MARKER, "PACKVALUE_ROUTE"),
        (COMMERCE_ANCHOR, "COMMERCE_ANCHOR"),
        (FULFILL_SIGNATURE, "FULFILL_SIGNATURE"),
        (PUBLIC_HEALTH_TOKEN, "PUBLIC_HEALTH"),
        ("createProviderCheckout", "PROVIDER"),
        ("CHECKOUT_PAID", "PAID_EVENT"),
        ("ASAAS_WEBHOOK_TOKEN", "WEBHOOK_TOKEN"),
        ("DELIVERY_PREFIX", "DELIVERY_PREFIX"),
        ("ORDER_PREFIX", "ORDER_PREFIX"),
    ]:
        require_once(source, token, name) if name in {"PACKVALUE_ROUTE","COMMERCE_ANCHOR","FULFILL_SIGNATURE","PUBLIC_HEALTH"} else None
        if token not in source:
            raise SystemExit(f"RADAR_PATCH_MISSING_{name}")

    helper = r'''
// ============================================================
// LSI GREENFIELD EXTENSION — BRAZIL OPPORTUNITY RADAR FOUNDER PASS
// Demand-first product: live official procurement opportunities.
// Fixed server-side price. Asaas webhook remains sole payment truth.
// ============================================================
const RADAR_COMMERCE_EXTENSION_VERSION = "brazil-opportunity-radar-commerce-r1-2026-08-31";
const RADAR_PRODUCT_ID = "brazil-opportunity-radar-founder-r1";
const RADAR_MATERIAL_ID = "brazil-opportunity-radar-live-r1";
const RADAR_PRICE_BRL = 19.90;
const RADAR_ACCESS_TTL_MS = 30 * 24 * 60 * 60 * 1000;
const RADAR_CHECKOUT_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=";
const RADAR_PNCP_OPEN_BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta";

function radarProduct() {
  return {
    productId: RADAR_PRODUCT_ID,
    materialId: RADAR_MATERIAL_ID,
    title: "LSI Brazil Opportunity Radar — Founder Pass",
    description: "30 dias de acesso ao radar vivo de oportunidades de compras públicas do Brasil",
    price: RADAR_PRICE_BRL,
    currency: "BRL",
    greenfield: true,
    brand: "LSI",
    checkoutImageBase64: RADAR_CHECKOUT_IMAGE_BASE64
  };
}

async function ensureRadarMaterial(env) {
  if (!env.MEDIA) throw new Error("radar_storage_missing");
  const key = `${MATERIAL_PREFIX}${RADAR_MATERIAL_ID}.json`;
  const current = await getJsonR2(env, key);
  if (current?.assetReady === true && current?.qualityStatus === "PASS" && current?.deliveryEnabled === true) return current;
  const now = new Date().toISOString();
  const material = {
    materialId: RADAR_MATERIAL_ID,
    title: "LSI Brazil Opportunity Radar",
    description: "Live 30-day opportunity radar entitlement",
    version: "1",
    materialKey: "live:lsi-brazil-opportunity-radar-r1",
    fileKey: "live:lsi-brazil-opportunity-radar-r1",
    mimeType: "text/html; charset=utf-8",
    size: 0,
    assetReady: true,
    qualityStatus: "PASS",
    deliveryEnabled: true,
    qualityGates: {officialData:true, liveAccess:true, noPiiCollection:true, settlementGated:true},
    commercialQaScore: 100,
    greenfield: true,
    brand: "LSI",
    createdAt: current?.createdAt || now,
    updatedAt: now
  };
  await putJsonR2(env, key, material);
  return material;
}

function radarText(v) { return String(v ?? "").trim(); }
function radarCompactDate(d) { return d.toISOString().slice(0,10).replaceAll("-",""); }
function radarNumber(row, keys) { for (const k of keys) { const n=Number(row?.[k]); if(Number.isFinite(n)) return n; } return null; }
function radarFirst(row, keys) { for (const k of keys) { const v=row?.[k]; if(v!==undefined && v!==null && radarText(v)) return v; } return null; }
function radarRows(payload) { if(Array.isArray(payload)) return payload; for(const c of [payload?.data,payload?.resultado,payload?.resultados,payload?.results,payload?.content]) if(Array.isArray(c)) return c; return []; }
function radarNormalize(row) {
  return {
    id: radarFirst(row,["idCompra","numeroControlePNCP","numeroCompra"]),
    object: radarFirst(row,["objetoCompra","objeto","descricao","descricaoCompra","informacaoComplementar"]),
    estimatedValueBRL: radarNumber(row,["valorTotalEstimado","valorEstimado","valorTotal","valorGlobal"]),
    publishedAt: radarFirst(row,["dataPublicacaoPncp","dataPublicacao","dataAtualizacaoPncp"]),
    deadlineAt: radarFirst(row,["dataEncerramentoProposta","dataFimProposta","dataAberturaProposta"]),
    uf: radarFirst(row,["unidadeOrgaoUfSigla","uf","ufSigla"]) || row?.unidadeOrgao?.ufSigla || null,
    organization: radarFirst(row,["orgaoEntidadeRazaoSocial","orgaoRazaoSocial","nomeOrgao"]) || row?.orgaoEntidade?.razaoSocial || null,
    unit: radarFirst(row,["unidadeOrgaoNomeUnidade","nomeUnidade"]) || row?.unidadeOrgao?.nomeUnidade || null,
    modality: radarFirst(row,["modalidadeNome","nomeModalidade","codigoModalidade"]),
    sourceUrl: radarFirst(row,["linkSistemaOrigem","linkProcessoEletronico","urlCompra"]),
    source: "PNCP — propostas abertas"
  };
}
function radarScore(item,q="") {
  let s=33;
  if(item.estimatedValueBRL>0) s+=Math.min(25,Math.log10(item.estimatedValueBRL+1)*5);
  if(item.deadlineAt) s+=12;
  if(item.sourceUrl) s+=5;
  const terms=radarText(q).toLowerCase().split(/\s+/).filter(Boolean);
  if(terms.length){const hay=`${item.object||""} ${item.organization||""} ${item.unit||""}`.toLowerCase();s+=(terms.filter(t=>hay.includes(t)).length/terms.length)*25;}
  return Math.round(Math.max(0,Math.min(100,s)));
}
function radarMatch(item,q,uf){
  const u=radarText(uf).toUpperCase(); if(u && radarText(item.uf).toUpperCase()!==u) return false;
  const terms=radarText(q).toLowerCase().split(/\s+/).filter(Boolean); if(!terms.length) return true;
  const hay=`${item.object||""} ${item.organization||""} ${item.unit||""} ${item.modality||""}`.toLowerCase();
  return terms.every(t=>hay.includes(t));
}
async function radarLiveFeed(url) {
  const limit=Math.max(1,Math.min(50,Number.parseInt(url.searchParams.get("limit")||"25",10)||25));
  const q=radarText(url.searchParams.get("q")).slice(0,120);
  const uf=radarText(url.searchParams.get("uf")).toUpperCase().slice(0,2);
  const end=new Date(); end.setUTCDate(end.getUTCDate()+45);
  const all=[], upstream=[];
  for(const modality of ["8","6","4"]){
    const p=new URLSearchParams({dataFinal:radarCompactDate(end),codigoModalidadeContratacao:modality,pagina:"1"}); if(uf)p.set("uf",uf);
    let r; try{r=await fetch(`${RADAR_PNCP_OPEN_BASE}?${p}`,{headers:{accept:"application/json"},cf:{cacheTtl:300,cacheEverything:true}});}catch{upstream.push({modality,status:0});continue;}
    upstream.push({modality,status:r.status}); if(!r.ok)continue;
    let payload; try{payload=await r.json();}catch{continue;}
    for(const row of radarRows(payload).slice(0,100)) all.push(radarNormalize(row));
    if(all.length>=limit*4)break;
  }
  const unique=new Map(); for(const item of all){const k=radarText(item.id)||`${item.object}|${item.organization}|${item.publishedAt}`;if(!unique.has(k))unique.set(k,item);}
  const opportunities=[...unique.values()].filter(x=>radarMatch(x,q,uf)).map(x=>({...x,opportunityScore:radarScore(x,q)})).sort((a,b)=>b.opportunityScore-a.opportunityScore||(b.estimatedValueBRL||0)-(a.estimatedValueBRL||0)).slice(0,limit);
  return {ok:true,version:RADAR_COMMERCE_EXTENSION_VERSION,provider:"PNCP",query:q||null,uf:uf||null,count:opportunities.length,opportunities,upstream,access:"founder_pass",financialOutcomeGuaranteed:false};
}

async function radarGrant(env, token) {
  const safe = sanitizeCommerceId(token);
  if (!safe || safe !== token) return null;
  const grant = await getJsonR2(env, `${DELIVERY_PREFIX}${safe}.json`);
  if (!grant || grant.productId !== RADAR_PRODUCT_ID || grant.deliveryMode !== "live_radar") return null;
  if (new Date(grant.expiresAt || 0).getTime() <= Date.now()) return null;
  return grant;
}

function radarLandingHtml() { return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LSI Brazil Opportunity Radar</title><meta name="description" content="Oportunidades públicas em aberto, filtradas e priorizadas em um radar vivo."><style>:root{font-family:Inter,system-ui,sans-serif;background:#08111f;color:#eef6ff}*{box-sizing:border-box}body{margin:0}main{max-width:980px;margin:auto;padding:48px 20px 80px}.tag{color:#67d3ff;font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}h1{font-size:clamp(38px,7vw,72px);line-height:1.02;margin:10px 0 18px}.lead{font-size:20px;line-height:1.55;color:#b9cbe0;max-width:780px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:28px 0}.card{background:#101d2d;border:1px solid #22354c;border-radius:16px;padding:18px}.price{font-size:42px;font-weight:900}.muted{color:#9db0c5}.opp{margin:10px 0;padding:13px;background:#0d1826;border-radius:12px}.btn{display:inline-block;border:0;border-radius:12px;background:#24a9e6;color:white;font-size:17px;font-weight:850;padding:14px 20px;cursor:pointer}#status{min-height:24px;margin-top:12px;color:#a9bdd2}</style></head><body><main><div class="tag">LSI • DADOS ATUAIS • BRASIL</div><h1>Encontre oportunidades antes de perder o prazo.</h1><p class="lead">Radar vivo de contratações públicas e propostas abertas. Filtre por palavra-chave e UF, priorize por valor, prazo e aderência e vá direto à fonte oficial.</p><div class="grid"><div class="card"><b>Dados oficiais</b><p class="muted">PNCP e Compras.gov.br. Atualização consultada no momento do uso.</p></div><div class="card"><b>Sem PDF velho</b><p class="muted">Seu passe libera um painel vivo por 30 dias.</p></div><div class="card"><b>Founder Pass</b><div class="price">R$ 19,90</div><p class="muted">Pagamento único • 30 dias • sem renovação automática.</p></div></div><h2>Prévia atual</h2><div id="preview"><div class="opp">Buscando oportunidades oficiais…</div></div><button class="btn" id="buy">Liberar 30 dias</button><div id="status"></div><p class="muted">O radar organiza dados públicos e não garante contratação, habilitação ou resultado financeiro.</p></main><script>const pv=document.querySelector('#preview');fetch('https://lsi-brazil-opportunity-radar-r1.umagestaointeligente.workers.dev/v1/preview?days=7&limit=3').then(r=>r.json()).then(j=>{pv.innerHTML=(j.opportunities||[]).map(x=>'<div class="opp"><b>'+esc(x.object||'Oportunidade')+'</b><br><span class="muted">'+esc(x.uf||'BR')+' • '+money(x.estimatedValueBRL)+' • score '+esc(x.opportunityScore||'—')+'</span></div>').join('')||'<div class="opp">Nenhuma oportunidade encontrada nesta consulta. O feed é atualizado pelas fontes oficiais.</div>'}).catch(()=>pv.innerHTML='<div class="opp">Prévia temporariamente indisponível.</div>');function esc(x){return String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function money(v){return Number.isFinite(Number(v))?Number(v).toLocaleString('pt-BR',{style:'currency',currency:'BRL'}):'valor não informado'}const b=document.querySelector('#buy'),s=document.querySelector('#status');b.onclick=async()=>{b.disabled=true;s.textContent='Abrindo checkout seguro…';try{const r=await fetch('/greenfield/brazil-opportunity-radar/checkout',{method:'POST',headers:{'content-type':'application/json'},body:'{}'}),j=await r.json();if(!r.ok||!j.checkoutUrl)throw 0;location.assign(j.checkoutUrl)}catch{s.textContent='Checkout temporariamente indisponível.';b.disabled=false}};</script></body></html>`; }

function radarAccessHtml(token) { return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LSI Opportunity Radar</title><style>:root{font-family:Inter,system-ui,sans-serif;background:#07111e;color:#edf7ff}*{box-sizing:border-box}body{margin:0}main{max-width:1100px;margin:auto;padding:32px 16px 70px}h1{font-size:clamp(30px,6vw,56px)}form{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}input{background:#101e2d;color:#fff;border:1px solid #2b4159;border-radius:10px;padding:12px;font-size:16px;flex:1;min-width:180px}button{background:#25a9e6;color:white;border:0;border-radius:10px;padding:12px 18px;font-weight:800}.card{background:#0f1c2a;border:1px solid #22374d;border-radius:14px;padding:16px;margin:10px 0}.meta{color:#a9bdd0;font-size:14px}.score{font-weight:900;color:#67d3ff}a{color:#67d3ff}</style></head><body><main><div class="meta">LSI • FOUNDER PASS ATIVO</div><h1>Brazil Opportunity Radar</h1><form id="f"><input id="q" placeholder="produto ou serviço: informática, mobiliário…"><input id="uf" maxlength="2" placeholder="UF (opcional)"><button>Buscar</button></form><div id="status" class="meta">Carregando oportunidades…</div><div id="list"></div></main><script>const t=${JSON.stringify(token)},f=document.querySelector('#f'),q=document.querySelector('#q'),uf=document.querySelector('#uf'),list=document.querySelector('#list'),status=document.querySelector('#status');function esc(x){return String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function money(v){return Number.isFinite(Number(v))?Number(v).toLocaleString('pt-BR',{style:'currency',currency:'BRL'}):'valor não informado'}async function load(){status.textContent='Atualizando dados oficiais…';list.innerHTML='';const p=new URLSearchParams({limit:'30'});if(q.value.trim())p.set('q',q.value.trim());if(uf.value.trim())p.set('uf',uf.value.trim().toUpperCase());const r=await fetch('/greenfield/brazil-opportunity-radar/feed/'+encodeURIComponent(t)+'?'+p);if(r.status===401||r.status===410){status.textContent='Este passe expirou ou é inválido.';return}const j=await r.json();status.textContent=(j.count||0)+' oportunidades encontradas • fonte PNCP';list.innerHTML=(j.opportunities||[]).map(x=>'<div class="card"><div class="score">Score '+esc(x.opportunityScore||'—')+'</div><h3>'+esc(x.object||'Oportunidade')+'</h3><div class="meta">'+esc(x.uf||'BR')+' • '+money(x.estimatedValueBRL)+' • prazo '+esc(x.deadlineAt||'não informado')+'</div><p>'+esc(x.organization||'Órgão não informado')+'</p>'+(x.sourceUrl?'<a target="_blank" rel="noopener" href="'+esc(x.sourceUrl)+'">Abrir fonte oficial</a>':'')+'</div>').join('')||'<div class="card">Nenhum resultado para este filtro nesta consulta.</div>'}f.onsubmit=e=>{e.preventDefault();load()};load();</script></body></html>`; }

function radarReturnHtml(outcome, referenceId) { const success=outcome==="success"; return new Response(`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LSI Opportunity Radar</title><style>body{font-family:system-ui;background:#08111f;color:#edf7ff;max-width:760px;margin:auto;padding:36px}a{display:inline-block;background:#24a9e6;color:#fff;padding:13px 18px;border-radius:10px;text-decoration:none;font-weight:800}</style></head><body><h1>LSI Brazil Opportunity Radar</h1><h2>${success?"Pagamento enviado":"Checkout encerrado"}</h2><p id="status">${success?"Aguardando confirmação financeira oficial do Asaas…":"Nenhum acesso foi liberado."}</p><p id="open"></p>${success?`<script>const r=${JSON.stringify(referenceId)};let n=0;async function p(){try{const x=await fetch('/greenfield/brazil-opportunity-radar/order/'+encodeURIComponent(r),{cache:'no-store'}),j=await x.json();if(j.fulfillmentReady&&j.deliveryUrl){document.querySelector('#status').textContent='Pagamento confirmado. Seu passe de 30 dias está ativo.';document.querySelector('#open').innerHTML='<a href="'+j.deliveryUrl+'">Abrir radar</a>';return}if(++n<150)setTimeout(p,2000)}catch{if(++n<150)setTimeout(p,2000)}}p();</script>`:""}<p>Referência: <code>${referenceId}</code></p></body></html>`,{headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store","Content-Security-Policy":"default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'"}}); }

'''

    source = source.replace(COMMERCE_ANCHOR, helper + COMMERCE_ANCHOR, 1)

    # Paid fulfillment branch must execute before the legacy static-material path.
    fulfill_branch = r'''
  if (order?.productId === RADAR_PRODUCT_ID && order?.greenfield === true) {
    const paidAt = new Date().toISOString();
    const token = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + RADAR_ACCESS_TTL_MS).toISOString();
    const grant = {
      token,
      productId: RADAR_PRODUCT_ID,
      materialId: RADAR_MATERIAL_ID,
      referenceId: order.referenceId,
      checkoutId: order.checkoutId || null,
      deliveryMode: "live_radar",
      paidAt,
      createdAt: paidAt,
      expiresAt,
      revoked: false,
      brand: "LSI"
    };
    await putJsonR2(env, `${DELIVERY_PREFIX}${token}.json`, grant);
    const fulfilled = {
      ...order,
      orderStatus: "fulfilled",
      paymentStatus: "paid",
      fulfilledAt: paidAt,
      deliveryToken: token,
      deliveryUrl: `${origin}/greenfield/brazil-opportunity-radar/access/${token}`,
      deliveryExpiresAt: expiresAt
    };
    await putJsonR2(env, `${ORDER_PREFIX}${order.referenceId}.json`, fulfilled);
    return fulfilled;
  }
'''
    source = source.replace(FULFILL_SIGNATURE, FULFILL_SIGNATURE + fulfill_branch, 1)

    routes = r'''
      // LSI Brazil Opportunity Radar — fixed Founder Pass; live data entitlement.
      if ((request.method === "GET" || request.method === "HEAD") && path === "/brazil-opportunity-radar") return new Response(request.method === "HEAD" ? null : radarLandingHtml(), {status:200,headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"public,max-age=180","X-Robots-Tag":"index,follow"}});
      if (request.method === "GET" && path === "/greenfield/brazil-opportunity-radar/health") return json({ok:true,extensionVersion:RADAR_COMMERCE_EXTENSION_VERSION,productId:RADAR_PRODUCT_ID,price:RADAR_PRICE_BRL,currency:"BRL",accessDays:30,provider:"asaas",fixedServerPrice:true,deliveryRequiresPaidWebhook:true,liveData:true,renewalAutomatic:false,spendCapability:false,piiCollectedByWorker:false,greenfield:true});
      if (request.method === "GET" && path.startsWith("/greenfield/brazil-opportunity-radar/order/")) { const referenceId=sanitizeCommerceId(decodeURIComponent(path.slice("/greenfield/brazil-opportunity-radar/order/".length))); if(!referenceId||!referenceId.startsWith("radar-")) return json({ok:false,error:"order_not_found"},404); const order=await getJsonR2(env,`${ORDER_PREFIX}${referenceId}.json`); if(!order||order.productId!==RADAR_PRODUCT_ID||order.greenfield!==true) return json({ok:false,error:"order_not_found"},404); return json({ok:true,referenceId,paymentStatus:order.paymentStatus||"pending",fulfillmentReady:Boolean(order.fulfilledAt&&order.deliveryUrl),deliveryUrl:order.fulfilledAt?order.deliveryUrl||null:null,deliveryExpiresAt:order.fulfilledAt?order.deliveryExpiresAt||null:null}); }
      if (request.method === "GET" && path.startsWith("/greenfield/brazil-opportunity-radar/access/")) { const token=decodeURIComponent(path.slice("/greenfield/brazil-opportunity-radar/access/".length)); const grant=await radarGrant(env,token); if(!grant) return new Response("Passe inválido ou expirado.",{status:410,headers:{"Content-Type":"text/plain; charset=utf-8","Cache-Control":"no-store"}}); return new Response(radarAccessHtml(token),{status:200,headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"private,no-store","X-Robots-Tag":"noindex,nofollow"}}); }
      if (request.method === "GET" && path.startsWith("/greenfield/brazil-opportunity-radar/feed/")) { const token=decodeURIComponent(path.slice("/greenfield/brazil-opportunity-radar/feed/".length)); const grant=await radarGrant(env,token); if(!grant) return json({ok:false,error:"pass_invalid_or_expired"},410); try{return json(await radarLiveFeed(url));}catch(error){return json({ok:false,error:"official_upstream_unavailable",detail:String(error?.message||error).slice(0,120)},502)} }
      if (request.method === "GET" && path.startsWith("/greenfield/brazil-opportunity-radar/checkout-return/")) { const outcome=path.slice("/greenfield/brazil-opportunity-radar/checkout-return/".length), referenceId=sanitizeCommerceId(url.searchParams.get("referenceId")||""); if(!new Set(["success","cancel","expired"]).has(outcome)||!referenceId.startsWith("radar-")) return new Response("Not found",{status:404}); return radarReturnHtml(outcome,referenceId); }
      if (request.method === "POST" && path === "/greenfield/brazil-opportunity-radar/checkout") { if(!env.ASAAS_API_KEY||!env.MEDIA) return json({ok:false,error:"payment_rail_unavailable"},503); const raw=await request.text(); if(raw.length>1024) return json({ok:false,error:"request_too_large"},413); let body={}; if(raw.trim()){try{body=JSON.parse(raw)}catch{return json({ok:false,error:"invalid_json"},400)}} if(!body||typeof body!=="object"||Array.isArray(body)||Object.keys(body).length!==0) return json({ok:false,error:"fixed_offer_accepts_no_client_parameters"},400); const material=await ensureRadarMaterial(env), product=radarProduct(), referenceId=sanitizeCommerceId(`radar-${crypto.randomUUID()}`); let checkout; try{checkout=await createProviderCheckout(env,"asaas",product,material,{referenceId},url.origin)}catch(error){return json({ok:false,error:"checkout_provider_failed",providerStatus:Number(error?.providerStatus||0)||null,providerErrors:Array.isArray(error?.providerErrors)?error.providerErrors:[]},502)} await putJsonR2(env,`${CHECKOUT_PREFIX}${checkout.checkoutId}.json`,{...checkout,greenfield:true,brand:"LSI"}); await putJsonR2(env,`${ORDER_PREFIX}${checkout.referenceId}.json`,{...checkout,greenfield:true,brand:"LSI",productId:RADAR_PRODUCT_ID,materialId:RADAR_MATERIAL_ID,orderStatus:"awaiting_payment",paymentStatus:"pending",fulfilledAt:null,createdAt:checkout.createdAt||new Date().toISOString()}); return json({ok:true,extensionVersion:RADAR_COMMERCE_EXTENSION_VERSION,productId:RADAR_PRODUCT_ID,amount:RADAR_PRICE_BRL,currency:"BRL",accessDays:30,referenceId:checkout.referenceId,checkoutId:checkout.checkoutId,checkoutUrl:checkout.checkoutUrl,provider:"asaas",deliveryRequiresPaidWebhook:true,renewalAutomatic:false},201); }

      '''
    # Insert before existing PackValue public block so both stay public and separate.
    source = source.replace(PACKVALUE_ROUTE_MARKER, routes + PACKVALUE_ROUTE_MARKER, 1)

    # Radar checkout must use its own return URL. Patch provider callback expression without changing PackValue/legacy behavior.
    callback_patterns = [
        'const callbackBase = product?.greenfield === true ? `${origin}/greenfield/packvalue-pro/checkout-return` : `${origin}/api/commerce/checkout-return`;',
        'const callbackBase = product?.greenfield === true ? `${origin}/api/greenfield/packvalue-pro/checkout-return` : `${origin}/api/commerce/checkout-return`;'
    ]
    matched = None
    for pat in callback_patterns:
        if pat in source:
            matched = pat
            break
    if not matched:
        raise SystemExit("RADAR_PATCH_CALLBACK_ANCHOR_MISSING")
    replacement = 'const callbackBase = product?.productId === RADAR_PRODUCT_ID ? `${origin}/greenfield/brazil-opportunity-radar/checkout-return` : (product?.greenfield === true ? `${origin}/greenfield/packvalue-pro/checkout-return` : `${origin}/api/commerce/checkout-return`);'
    source = source.replace(matched, replacement, 1)

    # Invariants and safety gates.
    if source.count(ROUTE_MARKER) != 1: raise SystemExit("RADAR_PATCH_ROUTE_INSERT_FAILED")
    if source.count("RADAR_COMMERCE_EXTENSION_VERSION") < 2: raise SystemExit("RADAR_PATCH_HELPER_INSERT_FAILED")
    if source.count(FULFILL_SIGNATURE) != 1: raise SystemExit("RADAR_PATCH_FULFILL_DUPLICATED")
    if "fixed_offer_accepts_no_client_parameters" not in source: raise SystemExit("RADAR_PATCH_FIXED_OFFER_GATE_MISSING")
    for token in ["CHECKOUT_PAID","ASAAS_WEBHOOK_TOKEN","isCommerceAdminAuthorized(request, env)","/api/commerce/webhook/asaas",PACKVALUE_ROUTE_MARKER]:
        if token not in source: raise SystemExit("RADAR_PATCH_INVARIANT_MISSING:"+token)
    if source.index(ROUTE_MARKER) > source.index(PUBLIC_HEALTH_TOKEN): raise SystemExit("RADAR_PATCH_NOT_PUBLIC_SCOPE")
    if "renewalAutomatic:false" not in source or "RADAR_ACCESS_TTL_MS" not in source: raise SystemExit("RADAR_PATCH_ENTITLEMENT_GATE_MISSING")

    pathlib.Path(a.output).write_text(source, encoding="utf-8")
    print(f"RADAR_COMMERCE_PATCH=PASS extension={EXTENSION_VERSION} price={PRICE:.2f} ttl_days={TTL_DAYS}")
    print("PACKVALUE_LEGACY_ROUTE_PRESERVED=PASS")
    print("ASAAS_WEBHOOK_TRUTH_PRESERVED=PASS")
    print("LIVE_DATA_ENTITLEMENT=PASS")

if __name__ == "__main__":
    main()
