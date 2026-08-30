from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import requests

import r45_instagram_multiformat_deploy as base


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
        "R45_STAGE=FETCHED",
        f"BASE_VERSION={current_version}",
        f"BASE_SOURCE_BYTES={len(source.encode('utf-8'))}",
        "OK=false",
    ]
    base.write_status(lines)

    if current_version == base.NEW_VERSION:
        health = requests.get(base.WORKER_ORIGIN + "/api/health", timeout=15).json()
        lines += ["ALREADY_DEPLOYED=true", f"LIVE_VERSION={health.get('version')}", "OK=true"]
        base.write_status(lines)
        return

    bindings, binding_version = base.resolve_bindings(api_base, headers)
    lines += [f"BINDING_SOURCE_VERSION_ID={binding_version}", f"BINDING_COUNT={len(bindings)}"]

    patched, notes = base.patch_source(source)
    # Safety correction: the live Worker does not expose a JS WORKER_ORIGIN constant.
    bad = 'if (value.startsWith(WORKER_ORIGIN || "") && value.includes(mediaMarker)) return {ok:true,source:"worker_media"};'
    good = 'if (value.includes("lola-operacional-ugi.umagestaointeligente.workers.dev/media/")) return {ok:true,source:"worker_media"};'
    if bad not in patched:
        raise RuntimeError("R45 image validator safety anchor missing")
    patched = patched.replace(bad, good, 1)
    if "WORKER_ORIGIN ||" in patched:
        raise RuntimeError("R45 undefined JS WORKER_ORIGIN leaked into patch")

    lines += notes + ["IMAGE_VALIDATOR_SAFETY_FIX=1", f"PATCHED_SOURCE_BYTES={len(patched.encode('utf-8'))}"]
    probe = Path("/tmp/ugi-r45-worker.mjs")
    probe.write_text(patched, encoding="utf-8")
    check = subprocess.run(["node", "--check", str(probe)], text=True, capture_output=True)
    if check.returncode != 0:
        lines += ["NODE_CHECK=false", "NODE_ERROR=" + (check.stderr or check.stdout)[-1800:].replace("\n", " ")]
        base.write_status(lines)
        raise SystemExit(check.returncode)
    lines.append("NODE_CHECK=true")
    base.write_status(lines)

    version_id = base.create_version(api_base, headers, patched, bindings)
    lines += [f"R45_VERSION_ID={version_id}", "CLOUDFLARE_VERSION_CREATED=true"]
    base.write_status(lines)

    deployment_id = base.deploy_version(api_base, headers, version_id)
    lines += [f"R45_DEPLOYMENT_ID={deployment_id}"]
    health = base.wait_health()
    lines += [f"LIVE_VERSION={health.get('version')}", "HEALTH_OK=true", "OK=true"]
    base.write_status(lines)


if __name__ == "__main__":
    main()
