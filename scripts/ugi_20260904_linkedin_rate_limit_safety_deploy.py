from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

import requests
import r45_instagram_multiformat_deploy as base

NEW_VERSION = "lola-v8-r45-7-linkedin-buffer-rate-limit-safe-2026-09-04"
STATUS = Path("cloudflare/status/ugi-linkedin-buffer-rate-limit-safe.txt")


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
    current = re.search(r'var VERSION = "([^"]+)";', source)
    current_version = current.group(1) if current else "unknown"
    lines = [f"BASE_VERSION={current_version}", "OK=false"]
    write_status(lines)

    if current_version == NEW_VERSION:
        lines += ["ALREADY_DEPLOYED=true", "OK=true"]
        write_status(lines)
        return
    if "/api/linkedin-text-publish" not in source:
        raise RuntimeError("LinkedIn Buffer route missing from live Worker")

    bindings, binding_version = base.resolve_bindings(api_base, headers)
    lines += [f"BINDING_SOURCE_VERSION_ID={binding_version}", f"BINDING_COUNT={len(bindings)}"]

    patched, n = re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW_VERSION}";', source, count=1)
    if n != 1:
        raise RuntimeError(f"VERSION anchor count={n}")

    old = 'const mutationState = stage === "channel_discovery" || stage === "channel_validation" ? false : "unknown";'
    new = '''const rateLimitedBeforeMutation = Number(error?.bufferDiagnostics?.httpStatus || 0) === 429 || String(error?.message || "").includes("429");
          const mutationState = stage === "channel_discovery" || stage === "channel_validation" || rateLimitedBeforeMutation ? false : "unknown";'''
    if patched.count(old) != 1:
        raise RuntimeError(f"mutation-state anchor count={patched.count(old)}")
    patched = patched.replace(old, new, 1)

    # Return 503 for all proven rate-limit rejections so callers may retry only
    # when Buffer explicitly rejected the request before any mutation occurred.
    old_return = '}, stage === "channel_discovery" ? 503 : 400);'
    new_return = '}, (stage === "channel_discovery" || rateLimitedBeforeMutation) ? 503 : 400);'
    if patched.count(old_return) != 1:
        raise RuntimeError(f"route-status anchor count={patched.count(old_return)}")
    patched = patched.replace(old_return, new_return, 1)

    required = [NEW_VERSION, "rateLimitedBeforeMutation", "bufferMutationPerformed:mutationState", "/api/linkedin-text-publish"]
    missing = [x for x in required if x not in patched]
    if missing:
        raise RuntimeError("rate-limit patch markers missing: " + ",".join(missing))

    probe = Path("/tmp/ugi-linkedin-rate-limit-safe-worker.mjs")
    probe.write_text(patched, encoding="utf-8")
    check = subprocess.run(["node", "--check", str(probe)], text=True, capture_output=True)
    if check.returncode != 0:
        lines += ["NODE_CHECK=false", "NODE_ERROR=" + (check.stderr or check.stdout)[-1800:].replace("\n", " ")]
        write_status(lines)
        raise SystemExit(check.returncode)
    lines += ["NODE_CHECK=true", f"PATCHED_SOURCE_BYTES={len(patched.encode('utf-8'))}"]
    write_status(lines)

    version_id = base.create_version(api_base, headers, patched, bindings)
    deployment_id = base.deploy_version(api_base, headers, version_id)
    lines += [f"VERSION_ID={version_id}", f"DEPLOYMENT_ID={deployment_id}"]
    last = {}
    for _ in range(20):
        try:
            r = requests.get(base.WORKER_ORIGIN + "/api/health", timeout=15)
            if r.status_code == 200:
                last = r.json()
                if last.get("ok") is True and last.get("version") == NEW_VERSION:
                    lines += [f"LIVE_VERSION={last.get('version')}", "HEALTH_OK=true", "OK=true"]
                    write_status(lines)
                    return
        except Exception:
            pass
        time.sleep(3)
    lines += ["HEALTH_OK=false", "LAST_HEALTH=" + json.dumps(last, ensure_ascii=False)[:800]]
    write_status(lines)
    raise RuntimeError("LinkedIn Buffer rate-limit safety deploy health timeout")


if __name__ == "__main__":
    main()
