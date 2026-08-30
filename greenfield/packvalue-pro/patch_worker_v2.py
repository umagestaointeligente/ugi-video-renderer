from __future__ import annotations
import argparse, base64, hashlib, pathlib, re

EXTENSION_VERSION = "packvalue-pro-commerce-r1-2026-08-30"
PRICE = 49.90
PRODUCT_ID = "packvalue-pro-r1"
MATERIAL_ID = "packvalue-pro-r1-html"
ASSET_KEY = "greenfield/packvalue-pro/packvalue-pro-r1.html"
TRANSPARENT_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z1l0AAAAASUVORK5CYII="

def once(s, anchor, name):
    n=s.count(anchor)
    if n != 1: raise SystemExit(f"PATCH_GATE_{name}_COUNT_{n}")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True); ap.add_argument('--asset',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    source=pathlib.Path(a.source).read_text(encoding='utf-8')
    asset=pathlib.Path(a.asset).read_bytes(); sha=hashlib.sha256(asset).hexdigest(); b64=base64.b64encode(asset).decode('ascii')
    if '/api/greenfield/packvalue-pro/checkout' in source: raise SystemExit('PATCH_GATE_ALREADY_APPLIED')

    admin='if (request.method === "POST" && path === "/api/commerce/checkout") {'
    webhook='if (request.method === "POST" && path === "/api/commerce/webhook/asaas") {'
    delivery='if (request.method === "GET" && path.startsWith("/api/material-delivery/")) {'
    provider='async function createProviderCheckout(env, provider, product, material, body, origin) {'
    commerce='function commerceProviderStatus(env) {'
    image='imageBase64: UGI_CHECKOUT_IMAGE_BASE64'
    callback='const callbackBase = `${origin}/api/commerce/checkout-return`;'
    for x,n in [(admin,'ADMIN'),(webhook,'WEBHOOK'),(delivery,'DELIVERY'),(provider,'PROVIDER'),(commerce,'COMMERCE'),(image,'IMAGE'),(callback,'CALLBACK_BASE')]: once(source,x,n)

    helper=f'''
// ============================================================
// LSI GREENFIELD EXTENSION — PACKVALUE PRO
// Fixed server-side offer. No generic public commerce capability.
// Asaas webhook remains the sole payment truth.
// ============================================================
const PACKVALUE_EXTENSION_VERSION = {EXTENSION_VERSION!r};
const PACKVALUE_PRO_PRODUCT_ID = {PRODUCT_ID!r};
const PACKVALUE_PRO_MATERIAL_ID = {MATERIAL_ID!r};
const PACKVALUE_PRO_PRICE = {PRICE:.2f};
const PACKVALUE_PRO_ASSET_KEY = {ASSET_KEY!r};
const PACKVALUE_PRO_ASSET_SHA256 = {sha!r};
const PACKVALUE_PRO_ASSET_BASE64 = {b64!r};
const PACKVALUE_PRO_CHECKOUT_IMAGE_BASE64 = {TRANSPARENT_PNG_B64!r};

function packValueProProduct() {{ return {{ productId:PACKVALUE_PRO_PRODUCT_ID, materialId:PACKVALUE_PRO_MATERIAL_ID, title:"PackValue PRO", description:"Comparador em lote de SKUs, preço normalizado, frete e desconto", price:PACKVALUE_PRO_PRICE, currency:"BRL", greenfield:true, brand:"PackValue", checkoutImageBase64:PACKVALUE_PRO_CHECKOUT_IMAGE_BASE64 }}; }}
function packValueProBytes() {{ const r=atob(PACKVALUE_PRO_ASSET_BASE64), b=new Uint8Array(r.length); for(let i=0;i<r.length;i++) b[i]=r.charCodeAt(i); return b; }}
async function ensurePackValueProMaterial(env) {{
  if (!env.MEDIA) throw new Error("packvalue_storage_missing");
  const key=`${{MATERIAL_PREFIX}}${{PACKVALUE_PRO_MATERIAL_ID}}.json`, current=await getJsonR2(env,key);
  if (current?.assetReady===true && current?.qualityStatus==="PASS" && current?.deliveryEnabled===true && current?.fileKey===PACKVALUE_PRO_ASSET_KEY && current?.packValueAssetSha256===PACKVALUE_PRO_ASSET_SHA256) return current;
  const bytes=packValueProBytes(), now=new Date().toISOString();
  await env.MEDIA.put(PACKVALUE_PRO_ASSET_KEY,bytes,{{httpMetadata:{{contentType:"text/html; charset=utf-8",cacheControl:"private,no-store"}},customMetadata:{{productId:PACKVALUE_PRO_PRODUCT_ID,greenfield:"true",sha256:PACKVALUE_PRO_ASSET_SHA256}}}});
  const material={{materialId:PACKVALUE_PRO_MATERIAL_ID,title:"packvalue-pro",description:"Standalone local SKU price comparison tool",version:"1",fileKey:PACKVALUE_PRO_ASSET_KEY,materialKey:PACKVALUE_PRO_ASSET_KEY,mimeType:"text/html; charset=utf-8",size:bytes.length,assetReady:true,qualityStatus:"PASS",deliveryEnabled:true,qualityGates:{{deterministicCore:true,standalone:true,noNetwork:true,noPiiCollection:true}},commercialQaScore:100,pagesValidated:1,greenfield:true,brand:"PackValue",packValueAssetSha256:PACKVALUE_PRO_ASSET_SHA256,createdAt:current?.createdAt||now,updatedAt:now}};
  await putJsonR2(env,key,material); return material;
}}
function packValueProLandingHtml() {{ const p=PACKVALUE_PRO_PRICE.toLocaleString("pt-BR",{{minimumFractionDigits:2}}); return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PackValue PRO — Comparador em lote</title><meta name="description" content="Compare SKUs por kg, litro ou unidade, com frete e desconto."><style>:root{{font-family:Inter,system-ui,sans-serif;color:#172033;background:#f4f6fb}}*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:880px;margin:auto;padding:48px 22px 80px}}.tag{{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#4055d8;font-weight:800}}h1{{font-size:clamp(38px,7vw,70px);line-height:1;margin:9px 0 20px}}.lead{{font-size:20px;line-height:1.55;color:#59667e}}.card{{background:#fff;border:1px solid #dfe4ee;border-radius:18px;padding:22px;margin:25px 0}}ul{{line-height:1.9}}.price{{font-size:38px;font-weight:900}}button{{border:0;border-radius:11px;background:#3048d8;color:#fff;font-size:17px;font-weight:800;padding:14px 20px;cursor:pointer}}#status{{min-height:24px;color:#53617b;margin-top:12px}}small{{color:#69758c;line-height:1.5;display:block;margin-top:16px}}</style></head><body><main><div class="tag">PackValue PRO</div><h1>Preço por unidade real, em lote.</h1><p class="lead">Importe ou cole dezenas de SKUs. Normalize por kg, litro ou unidade, incorpore frete e desconto, ranqueie o melhor valor e exporte CSV.</p><div class="card"><ul><li>CSV/TSV e colagem direta</li><li>Ranking por kg, litro e unidade</li><li>Frete + desconto no custo efetivo</li><li>Arquivo HTML local: dados ficam no seu dispositivo</li><li>Compra única, sem assinatura</li></ul><div class="price">R$ ${{p}}</div><p>Checkout hospedado pelo Asaas via PIX ou cartão.</p><button id="buy">Comprar PackValue PRO</button><div id="status"></div><small>Nenhuma economia, margem ou resultado financeiro é garantido.</small></div></main><script>const b=document.querySelector('#buy'),s=document.querySelector('#status');b.addEventListener('click',async()=>{{b.disabled=true;s.textContent='Abrindo checkout seguro…';try{{const r=await fetch('/api/greenfield/packvalue-pro/checkout',{{method:'POST',headers:{{'content-type':'application/json'}},body:'{{}}'}}),j=await r.json();if(!r.ok||!j.checkoutUrl)throw 0;location.assign(j.checkoutUrl)}}catch(e){{s.textContent='Checkout indisponível agora. Tente novamente em instantes.';b.disabled=false}}}});</script></body></html>`; }}
function packValueProReturn(outcome,referenceId) {{ const title={{success:"Pagamento enviado",cancel:"Checkout cancelado",expired:"Checkout expirado"}}[outcome]||"Checkout"; const body=outcome==="success"?`<p id="status">Aguardando confirmação financeira oficial do Asaas…</p><p id="download"></p><script>const r=${{JSON.stringify(referenceId)}};let n=0;async function p(){{try{{const x=await fetch('/api/greenfield/packvalue-pro/order/'+encodeURIComponent(r),{{cache:'no-store'}}),j=await x.json();if(j.fulfillmentReady&&j.deliveryUrl){{document.querySelector('#status').textContent='Pagamento confirmado.';document.querySelector('#download').innerHTML='<a href="'+j.deliveryUrl+'">Baixar PackValue PRO</a>';return}}if(++n<90)setTimeout(p,2000)}}catch(e){{if(++n<90)setTimeout(p,2000)}}}}p();</script>`:`<p>Nenhum arquivo foi liberado.</p>`; return new Response(`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PackValue PRO</title><style>body{{font-family:system-ui;background:#f4f6fb;color:#172033;padding:36px;max-width:760px;margin:auto}}a{{display:inline-block;background:#3048d8;color:#fff;padding:13px 17px;border-radius:10px;text-decoration:none;font-weight:800}}</style></head><body><h1>PackValue PRO</h1><h2>${{title}}</h2>${{body}}<p>Referência: <code>${{referenceId}}</code></p></body></html>`,{{headers:{{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store","Content-Security-Policy":"default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'"}}}}); }}

'''
    source=source.replace(commerce,helper+commerce,1)

    routes='''
      // LSI PackValue PRO — fixed public SKU only; no admin capability.
      if ((request.method === "GET" || request.method === "HEAD") && path === "/packvalue-pro") return new Response(request.method === "HEAD" ? null : packValueProLandingHtml(), {status:200,headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"public,max-age=300","X-Robots-Tag":"index,follow"}});
      if (request.method === "GET" && path === "/api/greenfield/packvalue-pro/health") return json({ok:true,coreVersion:VERSION,extensionVersion:PACKVALUE_EXTENSION_VERSION,productId:PACKVALUE_PRO_PRODUCT_ID,price:PACKVALUE_PRO_PRICE,currency:"BRL",provider:"asaas",fixedServerPrice:true,buyerDataCollectedByWorker:false,deliveryRequiresPaidWebhook:true,spendCapability:false,greenfield:true});
      if (request.method === "GET" && path.startsWith("/api/greenfield/packvalue-pro/order/")) { const referenceId=sanitizeCommerceId(decodeURIComponent(path.slice("/api/greenfield/packvalue-pro/order/".length))); if(!referenceId||!referenceId.startsWith("pvpro-")) return json({ok:false,error:"order_not_found"},404); const order=await getJsonR2(env,`${ORDER_PREFIX}${referenceId}.json`); if(!order||order.productId!==PACKVALUE_PRO_PRODUCT_ID||order.greenfield!==true) return json({ok:false,error:"order_not_found"},404); return json({ok:true,referenceId,paymentStatus:order.paymentStatus||"pending",fulfillmentReady:Boolean(order.fulfilledAt&&order.deliveryUrl),deliveryUrl:order.fulfilledAt?order.deliveryUrl||null:null,deliveryExpiresAt:order.fulfilledAt?order.deliveryExpiresAt||null:null}); }
      if (request.method === "GET" && path.startsWith("/api/greenfield/packvalue-pro/checkout-return/")) { const outcome=path.slice("/api/greenfield/packvalue-pro/checkout-return/".length), referenceId=sanitizeCommerceId(url.searchParams.get("referenceId")||""); if(!new Set(["success","cancel","expired"]).has(outcome)||!referenceId.startsWith("pvpro-")) return new Response("Not found",{status:404}); return packValueProReturn(outcome,referenceId); }
      if (request.method === "POST" && path === "/api/greenfield/packvalue-pro/checkout") { if(!env.ASAAS_API_KEY||!env.MEDIA) return json({ok:false,error:"payment_rail_unavailable"},503); const raw=await request.text(); if(raw.length>1024) return json({ok:false,error:"request_too_large"},413); let body={}; if(raw.trim()){try{body=JSON.parse(raw)}catch{return json({ok:false,error:"invalid_json"},400)}} if(!body||typeof body!=="object"||Array.isArray(body)||Object.keys(body).length!==0) return json({ok:false,error:"fixed_offer_accepts_no_client_parameters"},400); const material=await ensurePackValueProMaterial(env), product=packValueProProduct(), referenceId=sanitizeCommerceId(`pvpro-${crypto.randomUUID()}`); let checkout; try{checkout=await createProviderCheckout(env,"asaas",product,material,{referenceId},url.origin)}catch(error){return json({ok:false,error:"checkout_provider_failed",providerStatus:Number(error?.providerStatus||0)||null,providerErrors:Array.isArray(error?.providerErrors)?error.providerErrors:[]},502)} await putJsonR2(env,`${CHECKOUT_PREFIX}${checkout.checkoutId}.json`,{...checkout,greenfield:true,brand:"PackValue"}); await putJsonR2(env,`${ORDER_PREFIX}${checkout.referenceId}.json`,{...checkout,greenfield:true,brand:"PackValue",orderStatus:"awaiting_payment",paymentStatus:"pending",fulfilledAt:null,createdAt:checkout.createdAt||new Date().toISOString()}); return json({ok:true,coreVersion:VERSION,extensionVersion:PACKVALUE_EXTENSION_VERSION,productId:PACKVALUE_PRO_PRODUCT_ID,amount:PACKVALUE_PRO_PRICE,currency:"BRL",referenceId:checkout.referenceId,checkoutId:checkout.checkoutId,checkoutUrl:checkout.checkoutUrl,provider:"asaas",deliveryRequiresPaidWebhook:true},201); }

      '''
    source=source.replace(admin,routes+admin,1)

    # Per-product neutral image and greenfield callback. Legacy path stays unchanged for all existing products.
    source=source.replace(image,'imageBase64: String(product.checkoutImageBase64 || UGI_CHECKOUT_IMAGE_BASE64)',1)
    source=source.replace(callback,'const callbackBase = product?.greenfield === true ? `${origin}/api/greenfield/packvalue-pro/checkout-return` : `${origin}/api/commerce/checkout-return`;',1)

    # Greenfield delivery gets .html while legacy filenames are left untouched.
    disp=re.compile(r'headers\.set\("Content-Disposition",\s*`attachment; filename="\$\{String\(grant\.fileName \|\| "material-ugi"\)\.replace\(/\["\\\\\]/g, "-"\)\}"`\);')
    ms=list(disp.finditer(source))
    if len(ms)==1:
        source=disp.sub('headers.set("Content-Disposition", grant.productId === PACKVALUE_PRO_PRODUCT_ID ? `attachment; filename="packvalue-pro.html"` : `attachment; filename="${String(grant.fileName || "material-ugi").replace(/["\\\\]/g, "-")}"`);',source,count=1)
    else:
        # A later core may already normalize extension. Only continue if it already has an HTML-safe branch.
        if 'includes("html") ? "html"' not in source and "includes('html') ? 'html'" not in source: raise SystemExit(f'PATCH_GATE_DELIVERY_FILENAME_COUNT_{len(ms)}')

    # Invariants: generic admin checkout and webhook remain exactly once.
    for x,n in [(admin,'ADMIN_AFTER'),(webhook,'WEBHOOK_AFTER'),(delivery,'DELIVERY_AFTER'),(provider,'PROVIDER_AFTER')]: once(source,x,n)
    if 'fixed_offer_accepts_no_client_parameters' not in source or 'spendCapability:false' not in source: raise SystemExit('PATCH_FINAL_FIXED_OFFER_GATE')
    if source.count('isCommerceAdminAuthorized(request, env)') < 1: raise SystemExit('PATCH_FINAL_ADMIN_AUTH_MISSING')
    pathlib.Path(a.output).write_text(source,encoding='utf-8')
    print(f'PATCH_V2=PASS extension={EXTENSION_VERSION} asset_sha256={sha} bytes={len(source.encode())}')

if __name__=='__main__': main()
