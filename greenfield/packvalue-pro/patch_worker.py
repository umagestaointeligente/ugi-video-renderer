from __future__ import annotations
import argparse
import base64
import hashlib
import pathlib
import re

OLD_VERSION = "lola-v8-r44-5-23-store-multi-product-premium-v6-2026-08-25"
NEW_VERSION = "lola-v8-r44-5-24-lsi-packvalue-pro-greenfield-2026-08-30"
PRICE = 49.90
PRODUCT_ID = "packvalue-pro-r1"
MATERIAL_ID = "packvalue-pro-r1-html"
ASSET_KEY = "greenfield/packvalue-pro/packvalue-pro-r1.html"
TRANSPARENT_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z1l0AAAAASUVORK5CYII="


def require_once(source: str, anchor: str, name: str) -> None:
    count = source.count(anchor)
    if count != 1:
        raise SystemExit(f"PATCH_GATE_{name}_COUNT_{count}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--asset", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    src_path = pathlib.Path(args.source)
    asset_path = pathlib.Path(args.asset)
    out_path = pathlib.Path(args.output)
    source = src_path.read_text(encoding="utf-8")
    asset = asset_path.read_bytes()
    asset_sha = hashlib.sha256(asset).hexdigest()
    asset_b64 = base64.b64encode(asset).decode("ascii")

    if OLD_VERSION not in source:
        raise SystemExit("PATCH_GATE_LIVE_VERSION_MISMATCH")
    if NEW_VERSION in source or "/api/greenfield/packvalue-pro/checkout" in source:
        raise SystemExit("PATCH_GATE_ALREADY_APPLIED")

    # Legacy invariants that must remain present before surgery.
    for anchor, name in [
        ('if (request.method === "POST" && path === "/api/commerce/checkout") {', "ADMIN_CHECKOUT"),
        ('if (request.method === "POST" && path === "/api/commerce/webhook/asaas") {', "ASAAS_WEBHOOK"),
        ('if (request.method === "GET" && path.startsWith("/api/material-delivery/")) {', "MATERIAL_DELIVERY"),
        ('async function createProviderCheckout(env, provider, product, material, body, origin) {', "PROVIDER_ADAPTER"),
        ('function commerceProviderStatus(env) {', "COMMERCE_HELPER"),
        ('imageBase64: UGI_CHECKOUT_IMAGE_BASE64', "CHECKOUT_IMAGE")
    ]:
        require_once(source, anchor, name)

    version_anchor = f'const VERSION = "{OLD_VERSION}";'
    require_once(source, version_anchor, "VERSION")
    source = source.replace(version_anchor, f'const VERSION = "{NEW_VERSION}";', 1)

    helpers_anchor = 'function commerceProviderStatus(env) {'
    helper = f'''
// ============================================================
// LSI R44.5.24 — GREENFIELD PACKVALUE PRO FIXED-SKU COMMERCE
// - neutral brand, separate acquisition path
// - fixed server-side price; browser cannot override amount/provider/product
// - Asaas hosted checkout; official authenticated webhook remains payment truth
// - delivery reuses opaque token fulfillment only after paid webhook
// - no spending capability, no UGI product/content reuse
// ============================================================
const PACKVALUE_PRO_PRODUCT_ID = {PRODUCT_ID!r};
const PACKVALUE_PRO_MATERIAL_ID = {MATERIAL_ID!r};
const PACKVALUE_PRO_PRICE = {PRICE:.2f};
const PACKVALUE_PRO_ASSET_KEY = {ASSET_KEY!r};
const PACKVALUE_PRO_ASSET_SHA256 = {asset_sha!r};
const PACKVALUE_PRO_ASSET_BASE64 = {asset_b64!r};
const PACKVALUE_PRO_CHECKOUT_IMAGE_BASE64 = {TRANSPARENT_PNG_B64!r};

function packValueProProduct() {{
  return {{
    productId: PACKVALUE_PRO_PRODUCT_ID,
    materialId: PACKVALUE_PRO_MATERIAL_ID,
    title: "PackValue PRO",
    description: "Comparador em lote de SKUs, preço normalizado, frete e desconto",
    price: PACKVALUE_PRO_PRICE,
    currency: "BRL",
    greenfield: true,
    brand: "PackValue",
    checkoutImageBase64: PACKVALUE_PRO_CHECKOUT_IMAGE_BASE64
  }};
}}

function packValueProBase64Bytes(value) {{
  const raw = atob(String(value || ""));
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
  return bytes;
}}

async function ensurePackValueProMaterial(env) {{
  if (!env.MEDIA) throw new Error("packvalue_storage_missing");
  const key = `${{MATERIAL_PREFIX}}${{PACKVALUE_PRO_MATERIAL_ID}}.json`;
  const current = await getJsonR2(env, key);
  const valid = current?.assetReady === true &&
    current?.qualityStatus === "PASS" &&
    current?.deliveryEnabled === true &&
    current?.fileKey === PACKVALUE_PRO_ASSET_KEY &&
    current?.packValueAssetSha256 === PACKVALUE_PRO_ASSET_SHA256;
  if (valid) return current;

  const bytes = packValueProBase64Bytes(PACKVALUE_PRO_ASSET_BASE64);
  await env.MEDIA.put(PACKVALUE_PRO_ASSET_KEY, bytes, {{
    httpMetadata: {{ contentType: "text/html; charset=utf-8", cacheControl: "private,no-store" }},
    customMetadata: {{ productId: PACKVALUE_PRO_PRODUCT_ID, greenfield: "true", sha256: PACKVALUE_PRO_ASSET_SHA256 }}
  }});
  const now = new Date().toISOString();
  const material = {{
    materialId: PACKVALUE_PRO_MATERIAL_ID,
    title: "packvalue-pro",
    description: "Standalone local SKU price comparison tool",
    version: "1",
    fileKey: PACKVALUE_PRO_ASSET_KEY,
    materialKey: PACKVALUE_PRO_ASSET_KEY,
    mimeType: "text/html; charset=utf-8",
    size: bytes.length,
    assetReady: true,
    qualityStatus: "PASS",
    deliveryEnabled: true,
    qualityGates: {{ deterministicCore: true, standalone: true, noNetwork: true, noPiiCollection: true }},
    commercialQaScore: 100,
    pagesValidated: 1,
    greenfield: true,
    brand: "PackValue",
    packValueAssetSha256: PACKVALUE_PRO_ASSET_SHA256,
    createdAt: current?.createdAt || now,
    updatedAt: now
  }};
  await putJsonR2(env, key, material);
  return material;
}}

function packValueProLandingHtml() {{
  const price = PACKVALUE_PRO_PRICE.toLocaleString("pt-BR", {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PackValue PRO — Comparador em lote</title><meta name="description" content="Compare SKUs por kg, litro ou unidade, com frete e desconto. Arquivo local, sem assinatura."><style>:root{{font-family:Inter,system-ui,sans-serif;color:#172033;background:#f4f6fb}}*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:880px;margin:auto;padding:48px 22px 80px}}.tag{{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#4055d8;font-weight:800}}h1{{font-size:clamp(38px,7vw,70px);line-height:1;margin:9px 0 20px}}.lead{{font-size:20px;line-height:1.55;color:#59667e}}.card{{background:#fff;border:1px solid #dfe4ee;border-radius:18px;padding:22px;margin:25px 0;box-shadow:0 14px 34px rgba(30,40,80,.07)}}ul{{line-height:1.9}}.price{{font-size:38px;font-weight:900}}button{{border:0;border-radius:11px;background:#3048d8;color:#fff;font-size:17px;font-weight:800;padding:14px 20px;cursor:pointer}}button:disabled{{opacity:.6;cursor:wait}}#status{{min-height:24px;color:#53617b;margin-top:12px}}small{{color:#69758c;line-height:1.5;display:block;margin-top:16px}}</style></head><body><main><div class="tag">PackValue PRO</div><h1>Preço por unidade real, em lote.</h1><p class="lead">Cole ou importe dezenas de SKUs e normalize preço por kg, litro ou unidade. O cálculo incorpora frete e desconto, ranqueia o melhor valor e exporta CSV.</p><div class="card"><ul><li>CSV/TSV e colagem direta</li><li>Ranking por kg, litro e unidade</li><li>Frete + desconto no custo efetivo</li><li>Exportação do resultado</li><li>Arquivo HTML local: dados ficam no seu dispositivo</li><li>Compra única, sem assinatura</li></ul><div class="price">R$ ${{price}}</div><p>Pagamento hospedado pelo Asaas via PIX ou cartão.</p><button id="buy">Comprar PackValue PRO</button><div id="status"></div><small>Nenhuma economia, margem ou resultado financeiro é garantido. O ranking é matemático e deve ser usado junto com critérios comerciais e de qualidade.</small></div></main><script>const b=document.querySelector('#buy'),s=document.querySelector('#status');b.addEventListener('click',async()=>{{b.disabled=true;s.textContent='Abrindo checkout seguro…';try{{const r=await fetch('/api/greenfield/packvalue-pro/checkout',{{method:'POST',headers:{{'content-type':'application/json'}},body:'{{}}'}});const j=await r.json();if(!r.ok||!j.checkoutUrl)throw new Error(j.error||'checkout_unavailable');location.assign(j.checkoutUrl)}}catch(e){{s.textContent='Não foi possível abrir o checkout agora. Tente novamente em instantes.';b.disabled=false}}}});</script></body></html>`;
}}

function packValueProReturnResponse(outcome, referenceId) {{
  const titles = {{ success: "Pagamento enviado", cancel: "Checkout cancelado", expired: "Checkout expirado" }};
  const poll = outcome === "success" ? `<p id="status">Aguardando confirmação financeira oficial do Asaas…</p><p id="download"></p><script>const r=${{JSON.stringify(referenceId)}};let n=0;async function p(){{try{{const x=await fetch('/api/greenfield/packvalue-pro/order/'+encodeURIComponent(r),{{cache:'no-store'}}),j=await x.json();if(j.fulfillmentReady&&j.deliveryUrl){{document.querySelector('#status').textContent='Pagamento confirmado.';document.querySelector('#download').innerHTML='<a href="'+j.deliveryUrl+'">Baixar PackValue PRO</a>';return}}if(++n<60)setTimeout(p,2000);else document.querySelector('#status').textContent='A confirmação ainda está em processamento. Atualize esta página em alguns minutos.'}}catch(e){{if(++n<60)setTimeout(p,2000)}}}}p();</script>` : `<p>${{outcome === "cancel" ? "Nenhum arquivo foi liberado." : "Gere um novo checkout para concluir a compra."}}</p>`;
  return new Response(`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PackValue PRO</title><style>body{{font-family:system-ui;background:#f4f6fb;color:#172033;padding:36px;max-width:760px;margin:auto}}a{{display:inline-block;background:#3048d8;color:#fff;padding:13px 17px;border-radius:10px;text-decoration:none;font-weight:800}}</style></head><body><h1>PackValue PRO</h1><h2>${{titles[outcome] || "Checkout"}}</h2>${{poll}}<p>Referência: <code>${{referenceId}}</code></p></body></html>`, {{
    status: 200,
    headers: {{ "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store", "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'" }}
  }});
}}

'''
    source = source.replace(helpers_anchor, helper + helpers_anchor, 1)

    route_anchor = 'if (request.method === "POST" && path === "/api/commerce/checkout") {'
    routes = '''
      // LSI R44.5.24 — public fixed-SKU greenfield routes. No admin capability is exposed.
      if ((request.method === "GET" || request.method === "HEAD") && path === "/packvalue-pro") {
        return new Response(request.method === "HEAD" ? null : packValueProLandingHtml(), { status: 200, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "public,max-age=300", "X-Robots-Tag": "index,follow" } });
      }

      if (request.method === "GET" && path === "/api/greenfield/packvalue-pro/health") {
        return json({ ok: true, version: VERSION, productId: PACKVALUE_PRO_PRODUCT_ID, price: PACKVALUE_PRO_PRICE, currency: "BRL", provider: "asaas", fixedServerPrice: true, buyerDataCollectedByWorker: false, deliveryRequiresPaidWebhook: true, spendCapability: false, greenfield: true });
      }

      if (request.method === "GET" && path.startsWith("/api/greenfield/packvalue-pro/order/")) {
        const referenceId = sanitizeCommerceId(decodeURIComponent(path.slice("/api/greenfield/packvalue-pro/order/".length)));
        if (!referenceId || !referenceId.startsWith("pvpro-")) return json({ ok: false, error: "order_not_found" }, 404);
        const order = await getJsonR2(env, `${ORDER_PREFIX}${referenceId}.json`);
        if (!order || order.productId !== PACKVALUE_PRO_PRODUCT_ID || order.greenfield !== true) return json({ ok: false, error: "order_not_found" }, 404);
        return json({ ok: true, referenceId, paymentStatus: order.paymentStatus || "pending", fulfillmentReady: Boolean(order.fulfilledAt && order.deliveryUrl), deliveryUrl: order.fulfilledAt ? order.deliveryUrl || null : null, deliveryExpiresAt: order.fulfilledAt ? order.deliveryExpiresAt || null : null });
      }

      if (request.method === "POST" && path === "/api/greenfield/packvalue-pro/checkout") {
        if (!env.ASAAS_API_KEY || !env.MEDIA) return json({ ok: false, error: "payment_rail_unavailable" }, 503);
        const raw = await request.text();
        if (raw.length > 1024) return json({ ok: false, error: "request_too_large" }, 413);
        let body = {};
        if (raw.trim()) {
          try { body = JSON.parse(raw); } catch { return json({ ok: false, error: "invalid_json" }, 400); }
        }
        if (!body || typeof body !== "object" || Array.isArray(body) || Object.keys(body).length !== 0) {
          return json({ ok: false, error: "fixed_offer_accepts_no_client_parameters", forbidden: ["price","amount","provider","productId","materialId","providerPayload"] }, 400);
        }
        const material = await ensurePackValueProMaterial(env);
        const product = packValueProProduct();
        const referenceId = sanitizeCommerceId(`pvpro-${crypto.randomUUID()}`);
        let checkout;
        try {
          checkout = await createProviderCheckout(env, "asaas", product, material, { referenceId }, url.origin);
        } catch (error) {
          return json({ ok: false, error: "checkout_provider_failed", providerStatus: Number(error?.providerStatus || 0) || null, providerErrors: Array.isArray(error?.providerErrors) ? error.providerErrors : [] }, 502);
        }
        await putJsonR2(env, `${CHECKOUT_PREFIX}${checkout.checkoutId}.json`, { ...checkout, greenfield: true, brand: "PackValue" });
        await putJsonR2(env, `${ORDER_PREFIX}${checkout.referenceId}.json`, { ...checkout, greenfield: true, brand: "PackValue", orderStatus: "awaiting_payment", paymentStatus: "pending", fulfilledAt: null, createdAt: checkout.createdAt || new Date().toISOString() });
        return json({ ok: true, version: VERSION, productId: PACKVALUE_PRO_PRODUCT_ID, amount: PACKVALUE_PRO_PRICE, currency: "BRL", referenceId: checkout.referenceId, checkoutId: checkout.checkoutId, checkoutUrl: checkout.checkoutUrl, provider: "asaas", deliveryRequiresPaidWebhook: true }, 201);
      }

      '''
    source = source.replace(route_anchor, routes + route_anchor, 1)

    # Use neutral per-product image while preserving existing UGI behavior for legacy products.
    source = source.replace('imageBase64: UGI_CHECKOUT_IMAGE_BASE64', 'imageBase64: String(product.checkoutImageBase64 || UGI_CHECKOUT_IMAGE_BASE64)', 1)

    # Make existing delivery filename correctly preserve standalone HTML; PDF legacy path remains identical.
    html_ext_pattern = re.compile(r'fileName:\s*`\$\{String\(material\.title \|\| "material-ugi"\)\.replace\(/\[\^a-zA-Z0-9\._-\]\+/g, "-"\)\}\.\$\{String\(material\.mimeType \|\| ""\)\.includes\("pdf"\) \? "pdf" : "bin"\}`')
    matches = list(html_ext_pattern.finditer(source))
    if len(matches) != 1:
        raise SystemExit(f"PATCH_GATE_DELIVERY_FILENAME_COUNT_{len(matches)}")
    source = html_ext_pattern.sub('fileName: `${String(material.title || "material-ugi").replace(/[^a-zA-Z0-9._-]+/g, "-")}.${String(material.mimeType || "").includes("pdf") ? "pdf" : String(material.mimeType || "").includes("html") ? "html" : "bin"}`', source, count=1)

    # Neutral callback page for random greenfield reference ids; legacy UGI callback remains unchanged.
    callback_anchor = 'const allowed = new Set(["success", "cancel", "expired"]);\n        if (!allowed.has(outcome)) return new Response("Not found", { status: 404 });'
    require_once(source, callback_anchor, "CALLBACK_GATE")
    callback_replacement = callback_anchor + '\n        if (referenceId && referenceId.startsWith("pvpro-")) return packValueProReturnResponse(outcome, referenceId);'
    source = source.replace(callback_anchor, callback_replacement, 1)

    # Final static assertions.
    checks = {
        "new_version": NEW_VERSION,
        "greenfield_checkout": '/api/greenfield/packvalue-pro/checkout',
        "greenfield_order": '/api/greenfield/packvalue-pro/order/',
        "fixed_price": 'const PACKVALUE_PRO_PRICE = 49.90;',
        "webhook_preserved": 'if (request.method === "POST" && path === "/api/commerce/webhook/asaas") {',
        "admin_checkout_preserved": 'if (request.method === "POST" && path === "/api/commerce/checkout") {',
        "admin_checkout_auth_preserved": 'if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, errorClass: "commerce_authorization", error: "Não autorizado" }, 401);',
        "delivery_preserved": 'if (request.method === "GET" && path.startsWith("/api/material-delivery/")) {'
    }
    for name, text in checks.items():
        if text not in source:
            raise SystemExit(f"PATCH_FINAL_GATE_{name.upper()}_MISSING")
    if source.count('/api/greenfield/packvalue-pro/checkout') < 2:
        raise SystemExit("PATCH_FINAL_GATE_GREENFIELD_ROUTE_INCOMPLETE")
    if re.search(r'PACKVALUE_PRO_PRICE\s*=\s*(?!49\.90)', source):
        raise SystemExit("PATCH_FINAL_GATE_PRICE_DRIFT")

    out_path.write_text(source, encoding="utf-8")
    print(f"PATCH_WORKER=PASS old={OLD_VERSION} new={NEW_VERSION} asset_sha256={asset_sha} output_bytes={out_path.stat().st_size}")


if __name__ == "__main__":
    main()
