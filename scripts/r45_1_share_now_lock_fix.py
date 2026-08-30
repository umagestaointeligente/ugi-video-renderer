from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import requests

import r45_instagram_multiformat_deploy as base

NEW_VERSION = "lola-v8-r45-1-share-now-lock-fix-2026-08-30"
STATUS = Path("cloudflare/status/r45-1-share-now-lock-fix.txt")


def write(lines: list[str]) -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    token=os.environ.get("CF_API_TOKEN","")
    account=os.environ.get("CF_ACCOUNT_ID","")
    if not token or not account:
        raise SystemExit("Cloudflare credentials missing")
    headers=base.api_headers(token)
    api_base=f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{base.WORKER_NAME}"
    live=requests.get(api_base+"/content/v2",headers=headers,timeout=45)
    live.raise_for_status()
    source=base.extract_worker_source(live)
    current=re.search(r'var VERSION = "([^"]+)";',source)
    current_version=current.group(1) if current else "unknown"
    lines=[f"BASE_VERSION={current_version}",f"BASE_BYTES={len(source.encode('utf-8'))}","OK=false"]
    write(lines)

    bindings,binding_version=base.resolve_bindings(api_base,headers)
    lines += [f"BINDING_SOURCE_VERSION_ID={binding_version}",f"BINDING_COUNT={len(bindings)}"]

    patched,n=re.subn(r'var VERSION = "[^"]+";',f'var VERSION = "{NEW_VERSION}";',source,count=1)
    if n!=1: raise RuntimeError(f"VERSION_PATCH_COUNT={n}")

    pattern=r'function publicationSlotLockKey\(platform, mode, dueAt\) \{.*?\n\}\n__name\(publicationSlotLockKey, "publicationSlotLockKey"\);'
    replacement=r'''function publicationSlotLockKey(platform, mode, dueAt) {
  const normalizedPlatform = normalizeApprovalPlatform(platform) || String(platform || "unknown").trim().toLowerCase();
  const normalizedMode = normalizePublishMode(mode) || String(mode || "customScheduled").trim();
  let slot;
  if (normalizedMode === "shareNow") {
    // R45.1: shareNow is not one eternal slot. Asset locks remain the primary
    // exactly-once guard; the slot lock only prevents a same-minute collision.
    const minuteBucket = new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-");
    slot = `immediate-${minuteBucket}`;
  } else if (normalizedMode === "customScheduled" && dueAt) {
    const parsed = new Date(dueAt);
    slot = Number.isNaN(parsed.getTime()) ? String(dueAt) : parsed.toISOString();
  } else {
    slot = "queue";
  }
  return `${PUBLICATION_LOCK_PREFIX}slot/${normalizedPlatform}/${normalizedMode}/${sanitizeCommerceId(slot)}.json`;
}
__name(publicationSlotLockKey, "publicationSlotLockKey");'''
    patched,n=re.subn(pattern,replacement,patched,count=1,flags=re.S)
    if n!=1: raise RuntimeError(f"SLOT_LOCK_PATCH_COUNT={n}")
    lines += ["VERSION_PATCH=1","SHARE_NOW_MINUTE_BUCKET_PATCH=1",f"PATCHED_BYTES={len(patched.encode('utf-8'))}"]

    probe=Path('/tmp/ugi-r45-1-worker.mjs')
    probe.write_text(patched,encoding='utf-8')
    check=subprocess.run(['node','--check',str(probe)],text=True,capture_output=True)
    if check.returncode!=0:
        lines += ["NODE_CHECK=false","NODE_ERROR="+(check.stderr or check.stdout)[-1500:].replace('\n',' ')]
        write(lines)
        raise SystemExit(check.returncode)
    lines.append("NODE_CHECK=true"); write(lines)

    version_id=base.create_version(api_base,headers,patched,bindings)
    lines += [f"R45_1_VERSION_ID={version_id}","CLOUDFLARE_VERSION_CREATED=true"]
    write(lines)
    deployment_id=base.deploy_version(api_base,headers,version_id)
    lines += [f"R45_1_DEPLOYMENT_ID={deployment_id}"]
    health=base.wait_health()
    if health.get('version') != NEW_VERSION:
        lines += [f"LIVE_VERSION={health.get('version')}","HEALTH_VERSION_MATCH=false"]
        write(lines)
        raise RuntimeError("R45.1 health version mismatch")
    lines += [f"LIVE_VERSION={health.get('version')}","HEALTH_VERSION_MATCH=true","OK=true"]
    write(lines)

if __name__=='__main__':
    main()
