from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path

import requests
import scripts.r44_5_18_repair_v2 as base

WORKER = "lola-operacional-ugi"
ORIGIN = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
NEW_VERSION = "lola-v8-r44-5-23-lsi-fiat-rail-r1-2026-08-30"
STATUS = Path("cloudflare/status/lsi-fiat-rail-r1.json")


def cf_api(account: str) -> str:
    return f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{WORKER}"


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def fetch_live(api: str, h: dict[str, str]) -> str:
    r = requests.get(api + "/content/v2", headers=h, timeout=45)
    r.raise_for_status()
    return base.extract_source(r)


def active_version_and_bindings(api: str, h: dict[str, str]):
    r = requests.get(api + "/deployments", headers=h, timeout=30)
    r.raise_for_status()
    deployments = ((r.json().get("result") or {}).get("deployments") or [])
    if not deployments:
        raise RuntimeError("no_active_deployment")
    versions = deployments[0].get("versions") or []
    active = next((v for v in versions if float(v.get("percentage") or 0) >= 99.9), None) or (versions[0] if versions else None)
    if not active or not active.get("version_id"):
        raise RuntimeError("active_version_missing")
    version_id = str(active["version_id"])
    vr = requests.get(api + f"/versions/{version_id}", headers=h, timeout=30)
    vr.raise_for_status()
    return version_id, base.restored_bindings(vr.json())


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}_anchor_count={count}")
    return text.replace(old, new, 1)


def patch(source: str) -> str:
    t = re.sub(
        r"\n\s*// BEGIN_LSI_FIAT_RAIL_R1.*?// END_LSI_FIAT_RAIL_R1\s*\n",
        "\n",
        source,
        flags=re.S,
    )
    t = re.sub(
        r"\n\s*// BEGIN_LSI_FIAT_WEBHOOK_R1.*?// END_LSI_FIAT_WEBHOOK_R1\s*\n",
        "\n",
        t,
        flags=re.S,
    )

    t, n = re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW_VERSION}";', t, count=1)
    if n != 1:
        raise RuntimeError("version_anchor_mismatch")

    const_anchor = 'var DELIVERY_PREFIX = "lola/commerce/deliveries/";\n'
    constants = r'''// BEGIN_LSI_FIAT_RAIL_R1
var LSI_ORDER_PREFIX = "lsi/commerce/orders/";
var LSI_FIAT_OIDC_ISSUER = "https://token.actions.githubusercontent.com";
var LSI_FIAT_OIDC_AUDIENCE = "lsi-fiat-rail";
var LSI_FIAT_ALLOWED_REPOSITORY = "umagestaointeligente/ugi-video-renderer";
var LSI_FIAT_OFFER_CODE = "pipeline-sprint-24h";
var LSI_FIAT_OFFER_PRICE = 497;
// END_LSI_FIAT_RAIL_R1
'''
    t = replace_once(t, const_anchor, const_anchor + constants, "delivery_prefix")

    helper_anchor = "async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {\n"
    helpers = r'''// BEGIN_LSI_FIAT_RAIL_R1
function lsiB64urlToBytes(value) {
  const base64 = String(value || "").replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (String(value || "").length % 4)) % 4);
  const raw = atob(base64);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}
__name(lsiB64urlToBytes, "lsiB64urlToBytes");

function lsiDecodeJwtPart(part) {
  return JSON.parse(new TextDecoder().decode(lsiB64urlToBytes(part)));
}
__name(lsiDecodeJwtPart, "lsiDecodeJwtPart");

async function verifyLsiFiatGithubOidc(request) {
  const auth = request.headers.get("authorization") || "";
  if (!auth.startsWith("Bearer ")) throw new Error("missing_bearer");
  const token = auth.slice(7).trim();
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("invalid_jwt");
  const header = lsiDecodeJwtPart(parts[0]);
  const claims = lsiDecodeJwtPart(parts[1]);
  if (header.alg !== "RS256" || !header.kid) throw new Error("unsupported_jwt_header");
  const configResp = await fetch(`${LSI_FIAT_OIDC_ISSUER}/.well-known/openid-configuration`, { cf: { cacheTtl: 3600 } });
  if (!configResp.ok) throw new Error("oidc_config_unavailable");
  const config = await configResp.json();
  const jwksResp = await fetch(config.jwks_uri, { cf: { cacheTtl: 3600 } });
  if (!jwksResp.ok) throw new Error("oidc_jwks_unavailable");
  const jwks = await jwksResp.json();
  const jwk = (jwks.keys || []).find((key) => key.kid === header.kid);
  if (!jwk) throw new Error("oidc_kid_not_found");
  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const signed = new TextEncoder().encode(`${parts[0]}.${parts[1]}`);
  const verified = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, lsiB64urlToBytes(parts[2]), signed);
  if (!verified) throw new Error("oidc_signature_invalid");
  const now = Math.floor(Date.now() / 1000);
  if (claims.iss !== LSI_FIAT_OIDC_ISSUER) throw new Error("oidc_issuer_invalid");
  const aud = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!aud.includes(LSI_FIAT_OIDC_AUDIENCE)) throw new Error("oidc_audience_invalid");
  if (!claims.exp || claims.exp < now - 30) throw new Error("oidc_expired");
  if (claims.nbf && claims.nbf > now + 30) throw new Error("oidc_not_yet_valid");
  if (claims.repository !== LSI_FIAT_ALLOWED_REPOSITORY) throw new Error("oidc_repository_denied");
  const ref = String(claims.ref || "");
  const deployRef = ref.startsWith("refs/heads/lsi-fiat-rail-deploy-");
  const checkoutRef = ref.startsWith("refs/heads/lsi-fiat-checkout-");
  if (!deployRef && !checkoutRef) throw new Error("oidc_ref_denied");
  if (claims.event_name && claims.event_name !== "push") throw new Error("oidc_event_denied");
  return { repository: claims.repository, ref, runId: claims.run_id || null, deployRef, checkoutRef };
}
__name(verifyLsiFiatGithubOidc, "verifyLsiFiatGithubOidc");

function lsiFiatOffer(code) {
  if (String(code || "") !== LSI_FIAT_OFFER_CODE) return null;
  return {
    code: LSI_FIAT_OFFER_CODE,
    title: "Pipeline Sprint 24h",
    description: "Pesquisa e priorização de contas B2B, mensagens outbound e plano de abordagem, com entrega em até 24 horas após briefing aceito.",
    amount: LSI_FIAT_OFFER_PRICE,
    currency: "BRL"
  };
}
__name(lsiFiatOffer, "lsiFiatOffer");

async function createLsiFiatCheckout(env, offer, origin) {
  if (!env.ASAAS_API_KEY) throw new Error("asaas_api_key_missing");
  if (!env.MEDIA) throw new Error("r2_media_missing");
  const referenceId = `lsi-pipeline-${crypto.randomUUID()}`;
  const callbackBase = `${origin}/lsi/payment`;
  const payload = {
    billingTypes: ["PIX", "CREDIT_CARD"],
    chargeTypes: ["DETACHED"],
    minutesToExpire: 1440,
    externalReference: referenceId,
    callback: {
      successUrl: `${callbackBase}/success?referenceId=${encodeURIComponent(referenceId)}`,
      cancelUrl: `${callbackBase}/cancel?referenceId=${encodeURIComponent(referenceId)}`,
      expiredUrl: `${callbackBase}/expired?referenceId=${encodeURIComponent(referenceId)}`
    },
    items: [{
      externalReference: offer.code,
      name: offer.title,
      description: offer.description,
      quantity: 1,
      value: Number(offer.amount.toFixed(2))
    }]
  };
  const endpoint = `${String(env.ASAAS_API_BASE || "https://api.asaas.com/v3").replace(/\/$/, "")}/checkouts`;
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/json", access_token: env.ASAAS_API_KEY },
    body: JSON.stringify(payload)
  });
  const raw = await response.text();
  let data = null;
  try { data = JSON.parse(raw); } catch { data = {}; }
  if (!response.ok) {
    const error = new Error(`asaas_checkout_failed_${response.status}`);
    error.providerStatus = response.status;
    throw error;
  }
  const providerId = String(data?.id || data?.checkoutId || data?.checkout_id || "").trim();
  if (!providerId) throw new Error("asaas_checkout_id_missing");
  const checkoutUrl = String(data?.url || data?.link || data?.checkoutUrl || data?.checkout_url || `https://asaas.com/checkoutSession/show?id=${encodeURIComponent(providerId)}`).trim();
  const now = new Date().toISOString();
  const order = {
    schemaVersion: "1.0",
    project: "LSI",
    offerCode: offer.code,
    title: offer.title,
    amount: offer.amount,
    currency: offer.currency,
    provider: "asaas",
    providerCheckoutId: providerId,
    checkoutUrl,
    referenceId,
    orderStatus: "awaiting_payment",
    paymentStatus: "pending",
    paidAt: null,
    fulfillmentTriggered: false,
    ugiMaterialFulfillmentAllowed: false,
    createdAt: now,
    updatedAt: now
  };
  await putJsonR2(env, `${LSI_ORDER_PREFIX}${referenceId}.json`, order);
  return order;
}
__name(createLsiFiatCheckout, "createLsiFiatCheckout");

function lsiFiatPaid(body, normalized) {
  const event = String(body?.event || "").trim().toUpperCase();
  const checkoutStatus = String(body?.checkout?.status || "").trim().toUpperCase();
  return normalized?.paid === true || event === "CHECKOUT_PAID" || checkoutStatus === "PAID";
}
__name(lsiFiatPaid, "lsiFiatPaid");
// END_LSI_FIAT_RAIL_R1

'''
    t = replace_once(t, helper_anchor, helpers + helper_anchor, "buffer_helper")

    webhook_anchor = '      if (request.method === "POST" && path === "/api/commerce/webhook/asaas") {'
    if t.count(webhook_anchor) != 1:
        raise RuntimeError(f"webhook_anchor_count={t.count(webhook_anchor)}")

    routes = r'''      // BEGIN_LSI_FIAT_RAIL_R1
      if (request.method === "GET" && path === "/api/lsi/fiat-health") {
        return json({
          ok: Boolean(env.ASAAS_API_KEY && env.MEDIA),
          service: "lsi-fiat-rail",
          version: VERSION,
          provider: "asaas",
          pix: true,
          creditCard: true,
          oidcRequiredForMutation: true,
          arbitraryAmountAllowed: false,
          allowedOfferCodes: [LSI_FIAT_OFFER_CODE],
          ugiMaterialFulfillmentAllowed: false,
          bufferMutationAllowed: false,
          publicationAllowed: false
        }, env.ASAAS_API_KEY && env.MEDIA ? 200 : 503);
      }

      if (request.method === "POST" && path === "/api/lsi/checkout") {
        let identity;
        try { identity = await verifyLsiFiatGithubOidc(request); }
        catch (error) { return json({ok:false,errorClass:"lsi_oidc_denied",detail:String(error?.message || error)},401); }
        const body = await request.json().catch(() => null);
        if (!body) return json({ok:false,errorClass:"invalid_json"},400);
        const offer = lsiFiatOffer(body.offerCode || body.offer_code);
        if (!offer) return json({ok:false,errorClass:"offer_not_allowed",mutationPerformed:false},400);
        if (body.dryRun === true) {
          return json({ok:true,dryRun:true,offer,identity:{repository:identity.repository,ref:identity.ref,runId:identity.runId},mutationPerformed:false});
        }
        if (!identity.checkoutRef) return json({ok:false,errorClass:"checkout_branch_required",mutationPerformed:false},403);
        try {
          const order = await createLsiFiatCheckout(env, offer, url.origin);
          return json({
            ok:true,
            offerCode:order.offerCode,
            amount:order.amount,
            currency:order.currency,
            referenceId:order.referenceId,
            checkoutUrl:order.checkoutUrl,
            provider:"asaas",
            paymentStatus:"pending",
            mutationPerformed:true,
            paymentConfirmed:false,
            fulfillmentTriggered:false
          },201);
        } catch (error) {
          return json({ok:false,errorClass:String(error?.message || error),providerStatus:Number(error?.providerStatus || 0) || null,mutationPerformed:false,paymentConfirmed:false,fulfillmentTriggered:false},502);
        }
      }

      if (request.method === "GET" && path.startsWith("/api/lsi/order/")) {
        try { await verifyLsiFiatGithubOidc(request); }
        catch (error) { return json({ok:false,errorClass:"lsi_oidc_denied",detail:String(error?.message || error)},401); }
        const referenceId = String(path.slice("/api/lsi/order/".length) || "").trim();
        if (!/^lsi-pipeline-[a-f0-9-]{36}$/i.test(referenceId)) return json({ok:false,errorClass:"reference_invalid"},400);
        const order = await getJsonR2(env, `${LSI_ORDER_PREFIX}${referenceId}.json`);
        if (!order) return json({ok:false,errorClass:"lsi_order_not_found"},404);
        return json({ok:true,order:{referenceId:order.referenceId,offerCode:order.offerCode,amount:order.amount,currency:order.currency,paymentStatus:order.paymentStatus,paidAt:order.paidAt || null,fulfillmentTriggered:false}});
      }

      if (request.method === "GET" && path.startsWith("/lsi/payment/")) {
        const outcome = String(path.slice("/lsi/payment/".length) || "");
        if (!["success","cancel","expired"].includes(outcome)) return new Response("Not found",{status:404});
        const title = outcome === "success" ? "Retorno recebido" : outcome === "cancel" ? "Checkout cancelado" : "Checkout expirado";
        const message = outcome === "success"
          ? "O checkout foi concluído no navegador. A confirmação financeira é processada separadamente pelo webhook do provedor."
          : outcome === "cancel" ? "Nenhuma confirmação de pagamento foi registrada por este retorno." : "Este checkout expirou; um novo link pode ser gerado.";
        return new Response(`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title></head><body style="font-family:system-ui;max-width:720px;margin:48px auto;padding:24px"><h1>${title}</h1><p>${message}</p></body></html>`,{status:200,headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store","Content-Security-Policy":"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'"}});
      }
      // END_LSI_FIAT_RAIL_R1

'''
    t = t.replace(webhook_anchor, routes + webhook_anchor, 1)

    normalized_anchor = "        const normalized = normalizeAsaasWebhook(body);\n"
    if t.count(normalized_anchor) != 1:
        raise RuntimeError(f"normalized_anchor_count={t.count(normalized_anchor)}")
    lsi_webhook = r'''        // BEGIN_LSI_FIAT_WEBHOOK_R1
        if (normalized?.referenceId && String(normalized.referenceId).startsWith("lsi-pipeline-")) {
          const lsiOrder = await getJsonR2(env, `${LSI_ORDER_PREFIX}${normalized.referenceId}.json`);
          if (!lsiOrder) return json({ok:true,ignored:true,reason:"lsi_order_not_found"},202);
          const now = new Date().toISOString();
          const paid = lsiFiatPaid(body, normalized);
          const next = {
            ...lsiOrder,
            providerEvent: String(body?.event || normalized?.event || "").slice(0,120),
            providerPaymentId: normalized?.paymentId || lsiOrder.providerPaymentId || null,
            paymentStatus: paid ? "paid" : (normalized?.status || lsiOrder.paymentStatus || "pending"),
            orderStatus: paid ? "paid" : (lsiOrder.orderStatus || "awaiting_payment"),
            paidAt: paid ? (lsiOrder.paidAt || now) : (lsiOrder.paidAt || null),
            fulfillmentTriggered: false,
            ugiMaterialFulfillmentAllowed: false,
            updatedAt: now
          };
          await putJsonR2(env, `${LSI_ORDER_PREFIX}${normalized.referenceId}.json`, next);
          return json({ok:true,version:VERSION,project:"LSI",referenceId:normalized.referenceId,paymentStatus:next.paymentStatus,paymentConfirmed:paid,fulfillmentTriggered:false,publicationTriggered:false,bufferMutationPerformed:false});
        }
        // END_LSI_FIAT_WEBHOOK_R1
'''
    t = t.replace(normalized_anchor, normalized_anchor + lsi_webhook, 1)

    health_anchor = "            commerceBridge: true,\n"
    health_insert = (
        health_anchor
        + "            lsiFiatRail: true,\n"
        + "            lsiFiatRailOidc: true,\n"
        + "            lsiFiatRailFixedOfferOnly: true,\n"
        + "            lsiFiatRailUgiFulfillmentBlocked: true,\n"
    )
    t = replace_once(t, health_anchor, health_insert, "health_commerce")

    marked = re.search(r"// BEGIN_LSI_FIAT_RAIL_R1(.*?)// END_LSI_FIAT_RAIL_R1", t, flags=re.S)
    if not marked:
        raise RuntimeError("lsi_marker_missing")
    marker_text = marked.group(1)
    if "body.amount" in marker_text or "body.price" in marker_text or "body.value" in marker_text:
        raise RuntimeError("arbitrary_amount_input_detected")
    if "fulfillPaidOrder" in lsi_webhook:
        raise RuntimeError("ugi_fulfillment_leak")
    if "bufferGraphQL" in routes or "createBuffer" in routes:
        raise RuntimeError("buffer_mutation_leak")

    # Idempotency: applying the patch to its own output must preserve a single rail marker set.
    if t.count('var LSI_ORDER_PREFIX = "lsi/commerce/orders/";') != 1:
        raise RuntimeError("lsi_order_prefix_duplicate")
    return t


def preflight_health() -> dict:
    r = requests.get(ORIGIN + "/api/health", timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("ok") is not True:
        raise RuntimeError("preflight_health_not_ok")
    c = data.get("capabilities") or {}
    b = data.get("bindings") or {}
    required_caps = [
        "commerceBridge",
        "commerceWebhookFailClosed",
        "publicationExactlyOnceGuard",
        "permanentCommercePublicationLinkPolicy",
        "directAsaasCheckoutInPublicTextBlocked",
    ]
    missing_caps = [k for k in required_caps if c.get(k) is not True]
    if missing_caps:
        raise RuntimeError("preflight_capabilities_missing:" + ",".join(missing_caps))
    for key in ["MEDIA_R2", "BUFFER_API_KEY", "ASAAS_API_KEY", "ASAAS_WEBHOOK_TOKEN"]:
        if b.get(key) is not True:
            raise RuntimeError(f"preflight_binding_missing:{key}")
    return data


def wait_health() -> dict:
    last = {}
    for _ in range(30):
        try:
            r = requests.get(ORIGIN + "/api/health", timeout=15)
            if r.status_code == 200:
                last = r.json()
                c = last.get("capabilities") or {}
                b = last.get("bindings") or {}
                if (
                    last.get("ok") is True
                    and last.get("version") == NEW_VERSION
                    and c.get("lsiFiatRail") is True
                    and c.get("lsiFiatRailOidc") is True
                    and c.get("lsiFiatRailFixedOfferOnly") is True
                    and c.get("lsiFiatRailUgiFulfillmentBlocked") is True
                    and c.get("publicationExactlyOnceGuard") is True
                    and c.get("permanentCommercePublicationLinkPolicy") is True
                    and c.get("directAsaasCheckoutInPublicTextBlocked") is True
                    and b.get("MEDIA_R2") is True
                    and b.get("BUFFER_API_KEY") is True
                    and b.get("ASAAS_API_KEY") is True
                    and b.get("ASAAS_WEBHOOK_TOKEN") is True
                ):
                    return last
        except Exception:
            pass
        time.sleep(3)
    raise RuntimeError("postdeploy_health_timeout:" + json.dumps(last, ensure_ascii=False)[:1200])


def main():
    mode = os.environ.get("LSI_FIAT_MODE", "shadow").strip().lower()
    if mode not in {"shadow", "deploy"}:
        raise SystemExit("LSI_FIAT_MODE must be shadow or deploy")
    token = os.environ["CF_API_TOKEN"]
    account = os.environ["CF_ACCOUNT_ID"]
    h = headers(token)
    api = cf_api(account)

    pre = preflight_health()
    source = fetch_live(api, h)
    active_id, bindings = active_version_and_bindings(api, h)
    patched = patch(source)
    source_sha = hashlib.sha256(source.encode()).hexdigest()
    patched_sha = hashlib.sha256(patched.encode()).hexdigest()

    candidate_id = base.create_version(api, h, patched, bindings, "LSI fiat rail R1 candidate")
    deployed = False
    rollback = False
    post = None
    try:
        if mode == "deploy":
            base.deploy(api, h, candidate_id, "LSI fiat rail R1 guarded deployment")
            deployed = True
            post = wait_health()
    except Exception:
        if deployed:
            try:
                base.deploy(api, h, active_id, "ROLLBACK LSI fiat rail R1")
                rollback = True
            finally:
                time.sleep(2)
        raise
    finally:
        receipt = {
            "schema_version": "1.0",
            "project": "LSI_FIAT_RAIL_R1",
            "mode": mode,
            "worker": WORKER,
            "active_version_before": active_id,
            "candidate_version": candidate_id,
            "deployed": deployed,
            "rollback_performed": rollback,
            "source_sha256": source_sha,
            "patched_sha256": patched_sha,
            "pre_version": pre.get("version"),
            "post_version": (post or {}).get("version"),
            "offer_code": "pipeline-sprint-24h",
            "offer_amount_brl": 497,
            "arbitrary_amount_allowed": False,
            "oidc_required": True,
            "ugi_fulfillment_allowed": False,
            "buffer_mutation_allowed": False,
            "payment_created": False,
            "secrets_exposed": False,
        }
        STATUS.parent.mkdir(parents=True, exist_ok=True)
        STATUS.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
