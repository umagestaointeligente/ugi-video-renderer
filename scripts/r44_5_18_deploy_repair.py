from __future__ import annotations

import json
import os
import re
import secrets
import sys
import time
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

import requests

REPO_STATUS = Path("cloudflare/status/r44-5-18-final.txt")
WORKER_NAME = "lola-operacional-ugi"
OLD_VERSION = "lola-v8-r44-5-17-permanent-commerce-entrypoint-2026-08-21"
NEW_VERSION = "lola-v8-r44-5-18-permanent-publication-link-policy-2026-08-21"
STABLE_VERSION_ID = "35dc7be4-2d9e-479d-8f27-39e726e0b58f"
PUBLIC_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev/priorizacao"
WORKER_ORIGIN = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
SLOT02_POST_IDS = [
    "6a87d61b1b38003a90c37507",  # instagram
    "6a87d61f1b38003a90c3752d",  # tiktok
    "6a87d6231b38003a90c3755b",  # youtube
]


def status_write(lines: list[str]) -> None:
    REPO_STATUS.parent.mkdir(parents=True, exist_ok=True)
    REPO_STATUS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fail(lines: list[str], stage: str, exc: Exception | str) -> None:
    lines.append(f"FAILED_STAGE={stage}")
    lines.append(f"ERROR={str(exc).replace(chr(10), ' ')[:2000]}")
    lines.append("OK=false")
    status_write(lines)
    raise SystemExit(1)


def cf_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def extract_worker_source(resp: requests.Response) -> str:
    ctype = resp.headers.get("content-type", "")
    body = resp.content
    if "multipart/" not in ctype.lower():
        return body.decode("utf-8")

    envelope = (
        f"Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n".encode()
        + body
    )
    msg = BytesParser(policy=default).parsebytes(envelope)
    candidates: list[bytes] = []
    if msg.is_multipart():
        for part in msg.iter_parts():
            ptype = (part.get_content_type() or "").lower()
            filename = (part.get_filename() or "").lower()
            payload = part.get_payload(decode=True) or b""
            if "javascript" in ptype or filename.endswith((".js", ".mjs")):
                candidates.append(payload)
    if not candidates:
        raise RuntimeError("No JavaScript module found in Cloudflare multipart response")
    return max(candidates, key=len).decode("utf-8")


def patch_final_source(source: str) -> str:
    version_anchor = f'var VERSION = "{OLD_VERSION}";'
    if source.count(version_anchor) != 1:
        raise RuntimeError(f"version anchor count={source.count(version_anchor)}")
    text = source.replace(version_anchor, f'var VERSION = "{NEW_VERSION}";', 1)

    const_anchor = "var VIDEO_UPLOAD_MAX_BYTES = 50 * 1024 * 1024;\n"
    if text.count(const_anchor) != 1:
        raise RuntimeError(f"const anchor count={text.count(const_anchor)}")
    text = text.replace(
        const_anchor,
        const_anchor + "var PERMANENT_COMMERCE_PUBLIC_URL = " + json.dumps(PUBLIC_URL) + ";\n",
        1,
    )

    helper_anchor = "async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {\n"
    if text.count(helper_anchor) != 1:
        raise RuntimeError(f"buffer helper anchor count={text.count(helper_anchor)}")

    helper = r'''function permanentCommercePublicationText(draft = {}) {
  const original = String(draft?.text || "");
  const commerce = draft?.commerce || {};
  const productId = String(draft?.productId || commerce?.productId || "");
  const materialId = String(draft?.materialId || commerce?.materialId || "");
  const commercial = draft?.commercialOffer === true || commerce?.required === true;
  if (!commercial) return original;
  if (productId !== "UGI-MATERIAL-PRIORIDADES-001" && materialId !== "UGI-KIT-PRIORIZACAO-001") return original;
  let next = original.replace(/https:\/\/(?:www\.)?asaas\.com\/checkoutSession\/show(?:\/[A-Za-z0-9_-]+|\?id=[^\s]+)/gi, PERMANENT_COMMERCE_PUBLIC_URL);
  if (!next.includes(PERMANENT_COMMERCE_PUBLIC_URL)) {
    next = next.trim() + "\n\nKit UGI — Priorização Inteligente: R$ 14,99. Acesse: " + PERMANENT_COMMERCE_PUBLIC_URL;
  }
  return next;
}
__name(permanentCommercePublicationText, "permanentCommercePublicationText");
'''
    text = text.replace(helper_anchor, helper + helper_anchor, 1)

    old_text = '          text: ${JSON.stringify(String(draft.text || ""))}\n'
    new_text = '          text: ${JSON.stringify(permanentCommercePublicationText(draft))}\n'
    if text.count(old_text) != 1:
        raise RuntimeError(f"createPost text anchor count={text.count(old_text)}")
    text = text.replace(old_text, new_text, 1)

    health_anchor = "            permanentCommerceEntrypoint: true,\n"
    if text.count(health_anchor) != 1:
        raise RuntimeError(f"health anchor count={text.count(health_anchor)}")
    flags = (
        "            permanentCommercePublicationLinkPolicy: true,\n"
        "            directAsaasCheckoutInPublicTextBlocked: true,\n"
        "            permanentCommercePublicUrl: PERMANENT_COMMERCE_PUBLIC_URL,\n"
    )
    text = text.replace(health_anchor, health_anchor + flags, 1)
    return text


def add_temp_repair_route(final_source: str, path: str, token: str) -> str:
    anchor = '      if (path === "/approve") {'
    if final_source.count(anchor) != 1:
        raise RuntimeError(f"repair route anchor count={final_source.count(anchor)}")

    route = r'''      // BEGIN_R44_5_18_ONE_SHOT_REPAIR
      if (request.method === "POST" && path === __REPAIR_PATH__ && url.searchParams.get("token") === __REPAIR_TOKEN__) {
        const ids = [
          "6a87d61b1b38003a90c37507",
          "6a87d61f1b38003a90c3752d",
          "6a87d6231b38003a90c3755b"
        ];
        const results = [];
        for (const id of ids) {
          const before = await getBufferPostStatus(id, env);
          const beforePost = before.post || {};
          const beforeDueAt = beforePost.dueAt || null;
          if (beforePost.sentAt || String(beforePost.status || "").toLowerCase() === "sent") {
            results.push({ id, ok:false, error:"already_sent", status:beforePost.status || null, dueAt:beforeDueAt });
            continue;
          }
          const original = String(beforePost.text || "");
          let repaired = original.replace(/https:\/\/(?:www\.)?asaas\.com\/checkoutSession\/show(?:\/[A-Za-z0-9_-]+|\?id=[^\s]+)/gi, PERMANENT_COMMERCE_PUBLIC_URL);
          if (!repaired.includes(PERMANENT_COMMERCE_PUBLIC_URL)) {
            repaired = repaired.trim() + "\n\nKit UGI — Priorização Inteligente: R$ 14,99. Acesse: " + PERMANENT_COMMERCE_PUBLIC_URL;
          }
          const query = "mutation { editPost(input: { id: " + JSON.stringify(id) + ", text: " + JSON.stringify(repaired) + ", aiAssisted: true }) { __typename ... on PostActionSuccess { post { id text status dueAt sentAt externalLink } } ... on MutationError { message } } }";
          const edited = await bufferGraphQL(query, env);
          const payload = edited?.data?.editPost;
          if (!payload?.post?.id) {
            results.push({ id, ok:false, error:payload?.message || "edit_failed", diagnostics:edited?.__bufferDiagnostics || null });
            continue;
          }
          const after = await getBufferPostStatus(id, env);
          const afterPost = after?.post || {};
          const afterText = String(afterPost.text || "");
          results.push({
            id,
            ok: afterText.includes(PERMANENT_COMMERCE_PUBLIC_URL) && !/asaas\.com\/checkoutSession\/show/i.test(afterText) && (afterPost.dueAt || null) === beforeDueAt,
            status: afterPost.status || null,
            dueAt: afterPost.dueAt || null,
            sentAt: afterPost.sentAt || null,
            schedulePreserved: (afterPost.dueAt || null) === beforeDueAt,
            permanentUrlPresent: afterText.includes(PERMANENT_COMMERCE_PUBLIC_URL),
            temporaryCheckoutAbsent: !/asaas\.com\/checkoutSession\/show/i.test(afterText)
          });
        }
        return json({ ok: results.every(x => x.ok), version: VERSION, publicUrl: PERMANENT_COMMERCE_PUBLIC_URL, results, mutationPerformed:true, bufferMutation:true });
      }
      // END_R44_5_18_ONE_SHOT_REPAIR

'''
    route = route.replace("__REPAIR_PATH__", json.dumps(path)).replace(
        "__REPAIR_TOKEN__", json.dumps(token)
    )
    return final_source.replace(anchor, route + anchor, 1)


def restored_bindings(stable: dict) -> list[dict]:
    bindings = ((stable.get("result") or {}).get("resources") or {}).get("bindings") or []
    if len(bindings) != 19:
        raise RuntimeError(f"stable binding count={len(bindings)}")
    result = []
    for binding in bindings:
        if binding.get("type") == "secret_text":
            result.append({"name": binding["name"], "type": "inherit", "version_id": "latest"})
        else:
            result.append(binding)
    return result


def create_version(base: str, headers: dict, source: str, bindings: list[dict], tag: str) -> str:
    metadata = {
        "main_module": "worker.js",
        "compatibility_date": "2026-08-20",
        "annotations": {
            "workers/message": tag,
            "workers/tag": tag.replace(" ", "-")[:64],
        },
        "bindings": bindings,
    }
    resp = requests.post(
        base + "/versions?bindings_inherit=strict",
        headers=headers,
        files={
            "metadata": (None, json.dumps(metadata, ensure_ascii=False, separators=(",", ":")), "application/json"),
            "worker.js": ("worker.js", source.encode("utf-8"), "application/javascript+module"),
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"version create HTTP {resp.status_code}: {resp.text[:1200]}")
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"version create failed: {json.dumps(data.get('errors'))[:1200]}")
    version_id = (data.get("result") or {}).get("id")
    if not version_id:
        raise RuntimeError("version id missing")
    return version_id


def deploy_version(base: str, headers: dict, version_id: str, message: str) -> str:
    payload = {
        "strategy": "percentage",
        "versions": [{"version_id": version_id, "percentage": 100}],
        "annotations": {"workers/message": message},
    }
    resp = requests.post(
        base + "/deployments",
        headers={**headers, "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"deploy HTTP {resp.status_code}: {resp.text[:1200]}")
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"deploy failed: {json.dumps(data.get('errors'))[:1200]}")
    return str((data.get("result") or {}).get("id") or "")


def wait_health(expected_version: str, require_policy: bool) -> dict:
    last = {}
    for _ in range(12):
        try:
            r = requests.get(WORKER_ORIGIN + "/api/health", timeout=15)
            if r.status_code == 200:
                last = r.json()
                caps = last.get("capabilities") or {}
                binds = last.get("bindings") or {}
                ok = (
                    last.get("ok") is True
                    and last.get("version") == expected_version
                    and binds.get("MEDIA_R2") is True
                    and binds.get("BUFFER_API_KEY") is True
                    and binds.get("ASAAS_API_KEY") is True
                )
                if require_policy:
                    ok = ok and caps.get("permanentCommercePublicationLinkPolicy") is True and caps.get("directAsaasCheckoutInPublicTextBlocked") is True
                if ok:
                    return last
        except Exception:
            pass
        time.sleep(4)
    raise RuntimeError("health gate timed out: " + json.dumps(last, ensure_ascii=False)[:1200])


def main() -> None:
    lines = ["R44.5.18_STAGE=AUTONOMOUS_DEPLOY_AND_SLOT02_REPAIR"]
    status_write(lines + ["OK=false", "STATE=STARTED"])

    token = os.environ.get("CF_API_TOKEN", "")
    account_id = os.environ.get("CF_ACCOUNT_ID", "")
    if not token or not account_id:
        fail(lines, "ENV", "Cloudflare token/account missing")

    headers = cf_headers(token)
    base = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{WORKER_NAME}"

    try:
        health = requests.get(WORKER_ORIGIN + "/api/health", timeout=15).json()
        if health.get("version") != OLD_VERSION:
            if health.get("version") == NEW_VERSION:
                lines.append("PREEXISTING_R44_5_18=true")
            else:
                raise RuntimeError(f"unexpected live version {health.get('version')}")
        else:
            lines.append("PREEXISTING_R44_5_18=false")
    except Exception as exc:
        fail(lines, "PRECHECK", exc)

    try:
        live_resp = requests.get(base + "/content/v2", headers=headers, timeout=30)
        live_resp.raise_for_status()
        source = extract_worker_source(live_resp)
        stable_resp = requests.get(base + f"/versions/{STABLE_VERSION_ID}", headers=headers, timeout=30)
        stable_resp.raise_for_status()
        stable = stable_resp.json()
        bindings = restored_bindings(stable)
        lines.append(f"BASE_SOURCE_BYTES={len(source.encode('utf-8'))}")
        lines.append("BINDING_BASELINE=19")
    except Exception as exc:
        fail(lines, "FETCH_SOURCE_BINDINGS", exc)

    try:
        if f'var VERSION = "{NEW_VERSION}";' in source:
            final_source = source
            lines.append("POLICY_SOURCE_ALREADY_PRESENT=true")
        else:
            final_source = patch_final_source(source)
            lines.append("POLICY_SOURCE_ALREADY_PRESENT=false")
        if f'var VERSION = "{NEW_VERSION}";' not in final_source:
            raise RuntimeError("new version marker missing after patch")
        if "permanentCommercePublicationLinkPolicy: true" not in final_source:
            raise RuntimeError("policy capability missing after patch")
    except Exception as exc:
        fail(lines, "PATCH_FINAL_SOURCE", exc)

    repair_path = "/__ugi_repair_slot02_" + secrets.token_hex(12)
    repair_token = secrets.token_urlsafe(32)

    try:
        temp_source = add_temp_repair_route(final_source, repair_path, repair_token)
        temp_vid = create_version(base, headers, temp_source, bindings, "r44-5-18-temp-slot02-repair")
        temp_deploy = deploy_version(base, headers, temp_vid, "UGI R44.5.18 temporary Slot02 repair")
        lines.append(f"TEMP_VERSION_ID={temp_vid}")
        lines.append(f"TEMP_DEPLOYMENT_ID={temp_deploy}")
        wait_health(NEW_VERSION, require_policy=True)
    except Exception as exc:
        fail(lines, "DEPLOY_TEMP_REPAIR", exc)

    try:
        repair_resp = requests.post(
            WORKER_ORIGIN + repair_path,
            params={"token": repair_token},
            timeout=45,
        )
        if repair_resp.status_code != 200:
            raise RuntimeError(f"repair HTTP {repair_resp.status_code}: {repair_resp.text[:1200]}")
        repair = repair_resp.json()
        rows = repair.get("results") or []
        if not repair.get("ok") or len(rows) != 3:
            raise RuntimeError("repair failed: " + json.dumps(repair, ensure_ascii=False)[:1800])
        for row in rows:
            if not row.get("ok") or not row.get("schedulePreserved") or not row.get("permanentUrlPresent") or not row.get("temporaryCheckoutAbsent"):
                raise RuntimeError("repair invariant failed: " + json.dumps(row, ensure_ascii=False))
        lines.append("SLOT02_REPAIR_OK=true")
        for row in rows:
            lines.append(
                "BUFFER_POST=" + str(row.get("id"))
                + " STATUS=" + str(row.get("status"))
                + " DUE_AT=" + str(row.get("dueAt"))
                + " SCHEDULE_PRESERVED=true PERMANENT_URL=true TEMP_CHECKOUT_ABSENT=true"
            )
    except Exception as exc:
        fail(lines, "BUFFER_SLOT02_REPAIR", exc)

    try:
        final_vid = create_version(base, headers, final_source, bindings, "r44-5-18-permanent-link-final")
        final_deploy = deploy_version(base, headers, final_vid, "UGI R44.5.18 permanent publication link policy")
        lines.append(f"FINAL_VERSION_ID={final_vid}")
        lines.append(f"FINAL_DEPLOYMENT_ID={final_deploy}")
        final_health = wait_health(NEW_VERSION, require_policy=True)
        page = requests.get(PUBLIC_URL, timeout=20)
        if page.status_code != 200 or "Comprar agora" not in page.text:
            raise RuntimeError(f"permalink validation failed HTTP={page.status_code}")
        if "BEGIN_R44_5_18_ONE_SHOT_REPAIR" in final_source:
            raise RuntimeError("temporary repair route leaked into final source")
        lines.extend(
            [
                "PUBLIC_COMMERCE_URL=" + PUBLIC_URL,
                "PERMALINK_HTTP=200",
                "PERMANENT_PUBLICATION_LINK_POLICY=true",
                "DIRECT_ASAAS_CHECKOUT_IN_PUBLIC_TEXT_BLOCKED=true",
                "TEMP_REPAIR_ENDPOINT_REMOVED=true",
                "BINDINGS_PRESERVED=19",
                "OK=true",
            ]
        )
        status_write(lines)
    except Exception as exc:
        fail(lines, "DEPLOY_FINAL_VALIDATE", exc)


if __name__ == "__main__":
    main()
