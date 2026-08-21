from pathlib import Path
import sys

if len(sys.argv) != 3:
    raise SystemExit('usage: patch-r44-5-17.py <input.mjs> <output.mjs>')

src = Path(sys.argv[1])
out = Path(sys.argv[2])
text = src.read_text(encoding='utf-8')

old_v = 'const VERSION = "lola-v8-r44-5-16-commerce-publication-gate-fix-2026-08-21";'
new_v = 'const VERSION = "lola-v8-r44-5-17-permanent-commerce-entrypoint-2026-08-21";'
if text.count(old_v) != 1:
    raise SystemExit(f'expected exactly one R44.5.16 version, found {text.count(old_v)}')
text = text.replace(old_v, new_v, 1)

anchor = '// R44.5.16 COMMERCE PUBLICATION GATE FIX:\n'
if anchor not in text:
    raise SystemExit('R44.5.16 banner anchor missing')
banner = '''// R44.5.17 PERMANENT COMMERCE ENTRYPOINT:\n// - preserva integralmente R44.5.16\n// - adiciona URL comercial permanente /priorizacao\n// - GET /priorizacao nunca cria checkout\n// - POST /comprar/priorizacao cria checkout Asaas just-in-time\n// - checkout expirado/cancelado retorna ao permalink permanente\n// - mantém Product/Material gates, preço travado, webhook, fulfillment e entrega tokenizada\n//\n'''
text = text.replace(anchor, banner + anchor, 1)

const_anchor = 'const DELIVERY_TOKEN_TTL_MS = 7 * 24 * 60 * 60 * 1000;\n'
if const_anchor not in text:
    raise SystemExit('delivery ttl anchor missing')
text = text.replace(const_anchor, const_anchor + '''const COMMERCE_PERMALINKS = {\n  priorizacao: {\n    productId: "UGI-MATERIAL-PRIORIDADES-001",\n    materialId: "UGI-KIT-PRIORIZACAO-001",\n    title: "Kit UGI — Priorização Inteligente",\n    shortTitle: "Priorização Inteligente"\n  }\n};\n''', 1)

helper_anchor = 'async function createProviderCheckout(env, provider, product, material, body, origin) {'
if helper_anchor not in text:
    raise SystemExit('createProviderCheckout anchor missing')
helpers = r'''function escapeCommerceHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function resolveCommercePermalink(slug) {
  return COMMERCE_PERMALINKS[String(slug || "").trim().toLowerCase()] || null;
}

function commercePermalinkHtml(origin, slug, product, material, notice = "") {
  const safeTitle = escapeCommerceHtml(product?.title || material?.title || "Material UGI");
  const safeDescription = escapeCommerceHtml(product?.description || material?.description || "Material prático UGI.");
  const price = Number(product?.price || 0);
  const priceText = Number.isFinite(price) && price > 0 ? `R$ ${price.toFixed(2).replace(".", ",")}` : "";
  const noticeHtml = notice ? `<div class="notice">${escapeCommerceHtml(notice)}</div>` : "";
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${safeTitle}</title><style>
  body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#061A2B;color:#fff}
  .wrap{max-width:720px;margin:0 auto;padding:28px 20px 48px}.brand{color:#E7A72C;font-weight:800}
  .card{margin-top:20px;background:#fff;color:#182433;border-radius:22px;padding:26px}h1{font-size:30px;margin:0 0 12px}
  .price{font-size:28px;font-weight:800;margin:18px 0}.desc{line-height:1.55;color:#44505f}
  .buy{width:100%;border:0;border-radius:14px;background:#E7A72C;color:#061A2B;font-size:18px;font-weight:800;padding:16px}
  .note{font-size:13px;color:#697586;margin-top:14px}.notice{margin-bottom:18px;padding:12px;border-radius:12px;background:#fff4d6;color:#6b4d00}
  </style></head><body><main class="wrap"><div class="brand">UGI · UMA GESTÃO INTELIGENTE</div><section class="card">${noticeHtml}<h1>${safeTitle}</h1><p class="desc">${safeDescription}</p><div class="price">${priceText}</div><form method="post" action="${origin}/comprar/${encodeURIComponent(slug)}"><button class="buy" type="submit">Comprar agora</button></form><p class="note">Pagamento seguro via Asaas. O checkout é criado no momento da compra.</p></section></main></body></html>`;
}

'''
text = text.replace(helper_anchor, helpers + helper_anchor, 1)

cb_anchor = '    const callbackBase = `${origin}/api/commerce/checkout-return`;\n'
if cb_anchor not in text:
    raise SystemExit('callback base anchor missing')
text = text.replace(cb_anchor, cb_anchor + '    const permanentPath = String(body?.permanentPath || "").trim();\n    const permanentUrl = permanentPath.startsWith("/") ? `${origin}${permanentPath}` : null;\n', 1)

old_urls = '''      callback: {\n        successUrl: `${callbackBase}/success?referenceId=${encodeURIComponent(referenceId)}`,\n        cancelUrl: `${callbackBase}/cancel?referenceId=${encodeURIComponent(referenceId)}`,\n        expiredUrl: `${callbackBase}/expired?referenceId=${encodeURIComponent(referenceId)}`\n      },\n'''
new_urls = '''      callback: {\n        successUrl: `${callbackBase}/success?referenceId=${encodeURIComponent(referenceId)}`,\n        cancelUrl: permanentUrl ? `${permanentUrl}?checkout=cancelled` : `${callbackBase}/cancel?referenceId=${encodeURIComponent(referenceId)}`,\n        expiredUrl: permanentUrl ? `${permanentUrl}?checkout=expired` : `${callbackBase}/expired?referenceId=${encodeURIComponent(referenceId)}`\n      },\n'''
if old_urls not in text:
    raise SystemExit('callback urls anchor missing')
text = text.replace(old_urls, new_urls, 1)

route_anchor = '''      if (path === "/approve") {\n        return html(APP);\n      }\n\n'''
if route_anchor not in text:
    raise SystemExit('public route anchor missing')
routes = r'''      if (request.method === "GET" && path === "/priorizacao") {
        const config = resolveCommercePermalink("priorizacao");
        const product = await getJsonR2(env, `${PRODUCT_PREFIX}${config.productId}.json`);
        const material = await getJsonR2(env, `${MATERIAL_PREFIX}${config.materialId}.json`);
        if (!product || !material || product.status !== "active" || material.assetReady !== true || material.qualityStatus !== "PASS" || material.deliveryEnabled !== true) {
          return new Response("Material temporariamente indisponível.", { status: 503, headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" } });
        }
        const checkoutState = String(url.searchParams.get("checkout") || "").toLowerCase();
        const notice = checkoutState === "expired"
          ? "A sessão anterior expirou. Clique em Comprar agora para gerar uma nova sessão segura."
          : checkoutState === "cancelled"
          ? "A compra anterior foi cancelada. Você pode iniciar uma nova compra quando quiser."
          : "";
        return new Response(commercePermalinkHtml(url.origin, "priorizacao", product, material, notice), {
          status: 200,
          headers: {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
          }
        });
      }

      if (request.method === "POST" && path === "/comprar/priorizacao") {
        const config = resolveCommercePermalink("priorizacao");
        const product = await getJsonR2(env, `${PRODUCT_PREFIX}${config.productId}.json`);
        const material = await getJsonR2(env, `${MATERIAL_PREFIX}${config.materialId}.json`);
        if (!product || !material || product.status !== "active" || material.assetReady !== true || material.qualityStatus !== "PASS" || material.deliveryEnabled !== true) {
          return new Response("Produto indisponível.", { status: 503, headers: { "Cache-Control": "no-store" } });
        }
        const referenceId = `UGI-BUY-PRIORIDADES-${crypto.randomUUID()}`;
        try {
          const checkout = await createProviderCheckout(env, "asaas", product, material, { referenceId, permanentPath: "/priorizacao" }, url.origin);
          await putJsonR2(env, `${CHECKOUT_PREFIX}${checkout.checkoutId}.json`, checkout);
          await putJsonR2(env, `${ORDER_PREFIX}${checkout.referenceId}.json`, {
            ...checkout,
            orderStatus: "awaiting_payment",
            paymentStatus: "pending",
            fulfilledAt: null,
            permanentCommerceUrl: `${url.origin}/priorizacao`
          });
          return Response.redirect(checkout.checkoutUrl, 303);
        } catch (error) {
          console.log("R44.5.17 permalink checkout error:", error);
          return new Response("Não foi possível iniciar o pagamento agora. Tente novamente em instantes.", {
            status: 502,
            headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }
          });
        }
      }

'''
text = text.replace(route_anchor, route_anchor + routes, 1)

health_anchor = '            commercePublicationGateV2: true,\n'
if health_anchor not in text:
    raise SystemExit('health anchor missing')
text = text.replace(health_anchor, health_anchor + '''            permanentCommerceEntrypoint: true,\n            permanentCommerceUrlPrioritization: "/priorizacao",\n            justInTimeAsaasCheckout: true,\n            expiredCheckoutReturnsToPermalink: true,\n            directAsaasCheckoutPublishingDeprecated: true,\n''', 1)

if new_v not in text:
    raise SystemExit('new version missing after patch')
if 'path === "/priorizacao"' not in text or 'path === "/comprar/priorizacao"' not in text:
    raise SystemExit('permanent commerce routes missing after patch')

out.write_text(text, encoding='utf-8')
print('R44.5.17_PATCH_OK')
