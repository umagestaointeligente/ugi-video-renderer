from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

import requests

import r45_instagram_multiformat_deploy as base

NEW_VERSION = "lola-v8-r45-5-manifest-format-contract-2026-09-04"
STATUS = Path("cloudflare/status/ugi-story-format-contract.txt")


def wait_health():
    last = {}
    for _ in range(35):
        try:
            r = requests.get(base.WORKER_ORIGIN + "/api/health", timeout=15)
            last = r.json()
            if r.ok and last.get("ok") is True and last.get("version") == NEW_VERSION:
                return last
        except Exception as exc:
            last = {"error": str(exc)}
        time.sleep(2)
    raise RuntimeError(f"health mismatch: {last}")


def main():
    token = os.environ.get("CF_API_TOKEN", "")
    account = os.environ.get("CF_ACCOUNT_ID", "")
    if not token or not account:
        raise SystemExit("Cloudflare credentials missing")

    headers = base.api_headers(token)
    api_base = f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{base.WORKER_NAME}"
    live = requests.get(api_base + "/content/v2", headers=headers, timeout=45)
    live.raise_for_status()
    source = base.extract_worker_source(live)

    text, n = re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW_VERSION}";', source, count=1)
    if n != 1:
        raise RuntimeError("VERSION anchor missing")

    route_anchor = 'if (path === "/api/platform-publish" && request.method === "POST")'
    route_i = text.find(route_anchor)
    if route_i < 0:
        raise RuntimeError("platform-publish route anchor missing")

    commerce_anchor = '        const commerceReasons = commerceGateReasons(draft);'
    insert_i = text.find(commerce_anchor, route_i)
    if insert_i < 0:
        raise RuntimeError("commerce gate anchor missing after platform-publish")

    contract = '''        // UGI native-format contract: the canonical manifest can explicitly
        // carry the intended Instagram format. This survives draft-type loss and
        // prevents a Story from silently degrading into a Reel.
        const requestedFormat = String(body?.format || "").trim().toLowerCase();
        if (platform === "instagram" && requestedFormat) {
          const supportedInstagramVideoFormats = new Set([
            "story", "story_video", "reel", "reel_fallback_from_carousel"
          ]);
          if (!supportedInstagramVideoFormats.has(requestedFormat)) {
            return json({
              ok:false, version:VERSION, route:"/api/platform-publish",
              errorClass:"instagram_format_contract_invalid",
              error:`Formato Instagram não suportado nesta rota: ${requestedFormat}`,
              requestedFormat,
              publicationTriggered:false,
              bufferMutationPerformed:false
            },400);
          }
          draft.type = requestedFormat;
          draft.expectedNativeFormat = requestedFormat.startsWith("story") ? "story" : "reel";
        }
'''
    if 'errorClass:"instagram_format_contract_invalid"' not in text:
        text = text[:insert_i] + contract + text[insert_i:]

    # Verify the Story metadata function is still present and uses draft.type.
    if '["story", "story_image", "story_video"].includes(String(draft?.type || "").toLowerCase())' not in text:
        raise RuntimeError("Story metadata draft.type contract missing")

    probe = Path('/tmp/ugi-story-format-contract.mjs')
    probe.write_text(text, encoding='utf-8')
    check = subprocess.run(['node', '--check', str(probe)], text=True, capture_output=True)
    if check.returncode != 0:
        raise RuntimeError((check.stderr or check.stdout)[-2500:])

    bindings, binding_version = base.resolve_bindings(api_base, headers)
    version_id = base.create_version(api_base, headers, text, bindings)
    deployment_id = base.deploy_version(api_base, headers, version_id)
    health = wait_health()

    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text('\n'.join([
        'UGI_STORY_FORMAT_CONTRACT',
        f'BINDING_SOURCE_VERSION_ID={binding_version}',
        f'VERSION_ID={version_id}',
        f'DEPLOYMENT_ID={deployment_id}',
        f'LIVE_VERSION={health.get("version")}',
        'MANIFEST_FORMAT_OVERRIDE=instagram',
        'STORY_TO_REEL_SILENT_DOWNGRADE=blocked_when_format_present',
        'FAIL_CLOSED_INVALID_FORMAT=true',
        'OK=true',
    ]) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
