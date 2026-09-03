from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import requests

import r45_instagram_multiformat_deploy as base

NEW_VERSION = "lola-v8-r45-4-story-video-buffer-direct-2026-09-03"
STATUS = Path("cloudflare/status/ugi-20260903-worker-recovery.txt")
CHANNELS = {
    "BUFFER_CHANNEL_INSTAGRAM": "6a7896cdb2d9d57743457e33",
    "BUFFER_CHANNEL_TIKTOK": "6a789721b2d9d5774345839d",
    "BUFFER_CHANNEL_YOUTUBE": "6a78974ab2d9d577434584b7",
}


def write_status(lines: list[str]) -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    token = os.environ.get("CF_API_TOKEN", "")
    account = os.environ.get("CF_ACCOUNT_ID", "")
    if not token or not account:
        raise SystemExit("Cloudflare credentials missing")

    headers = base.api_headers(token)
    api_base = f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{base.WORKER_NAME}"
    live = requests.get(api_base + "/content/v2", headers=headers, timeout=45)
    live.raise_for_status()
    source = base.extract_worker_source(live)
    current_match = re.search(r'var VERSION = "([^"]+)";', source)
    current_version = current_match.group(1) if current_match else "unknown"

    lines = [
        "UGI_20260903_WORKER_RECOVERY",
        f"BASE_VERSION={current_version}",
        f"BASE_SOURCE_BYTES={len(source.encode('utf-8'))}",
        "OK=false",
    ]
    write_status(lines)

    # Preserve the exact live worker and patch only two operational contracts:
    # 1) IG video drafts whose contentId explicitly contains -IG-STORY- publish as Story;
    # 2) canonical Buffer channel IDs are bound as Worker vars, eliminating discovery calls.
    patched, n = re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW_VERSION}";', source, count=1)
    if n != 1:
        raise RuntimeError("VERSION anchor missing")

    ig_anchor = 'if (platform === "instagram") {\n    return `\n      metadata: {\n        instagram: {\n          type: reel\n          shouldShareToFeed: true'
    if ig_anchor not in patched:
        raise RuntimeError("Instagram metadata anchor missing")
    ig_replacement = 'if (platform === "instagram") {\n    const instagramStory = /-IG-STORY-/i.test(String(draft?.contentId || "")) || ["story", "story_image", "story_video"].includes(String(draft?.type || "").toLowerCase());\n    return `\n      metadata: {\n        instagram: {\n          type: ${instagramStory ? "story" : "reel"}\n          shouldShareToFeed: ${instagramStory ? "false" : "true"}'
    patched = patched.replace(ig_anchor, ig_replacement, 1)

    probe = Path("/tmp/ugi-20260903-worker.mjs")
    probe.write_text(patched, encoding="utf-8")
    check = subprocess.run(["node", "--check", str(probe)], text=True, capture_output=True)
    if check.returncode != 0:
        lines += ["NODE_CHECK=false", "NODE_ERROR=" + (check.stderr or check.stdout)[-1800:].replace("\n", " ")]
        write_status(lines)
        raise SystemExit(check.returncode)
    lines.append("NODE_CHECK=true")

    bindings, binding_version = base.resolve_bindings(api_base, headers)
    bindings = [b for b in bindings if b.get("name") not in CHANNELS]
    for name, value in CHANNELS.items():
        bindings.append({"name": name, "type": "plain_text", "text": value})
    lines += [f"BINDING_SOURCE_VERSION_ID={binding_version}", "CANONICAL_BUFFER_CHANNEL_BINDINGS=3"]

    version_id = base.create_version(api_base, headers, patched, bindings)
    deployment_id = base.deploy_version(api_base, headers, version_id)
    health = base.wait_health()
    if health.get("version") != NEW_VERSION or health.get("ok") is not True:
        raise RuntimeError(f"Unexpected live health: {health}")

    lines += [
        f"VERSION_ID={version_id}",
        f"DEPLOYMENT_ID={deployment_id}",
        f"LIVE_VERSION={health.get('version')}",
        "STORY_VIDEO_ROUTING=true",
        "DIRECT_CANONICAL_BUFFER_CHANNELS=true",
        "OK=true",
    ]
    write_status(lines)


if __name__ == "__main__":
    main()
