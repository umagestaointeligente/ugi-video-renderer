from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

import requests

import r45_instagram_multiformat_deploy as base

NEW_VERSION = "lola-v8-r45-3-instagram-scheduled-media-2026-08-30"
STATUS = Path("cloudflare/status/r45-3-instagram-scheduled-media.txt")


def write(lines: list[str]) -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def wait_health(expected: str, seconds: int = 180) -> dict:
    deadline = time.time() + seconds
    last: dict = {}
    while time.time() < deadline:
        try:
            r = requests.get(base.WORKER_ORIGIN + "/api/health", timeout=15)
            if r.status_code == 200:
                last = r.json()
                if last.get("ok") is True and last.get("version") == expected:
                    return last
        except Exception:
            pass
        time.sleep(5)
    return last


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
    match = re.search(r'var VERSION = "([^"]+)";', source)
    current = match.group(1) if match else "unknown"
    lines = [f"BASE_VERSION={current}", "OK=false"]
    write(lines)

    if current == NEW_VERSION:
        health = wait_health(NEW_VERSION, 60)
        ok = health.get("ok") is True and health.get("version") == NEW_VERSION
        lines += ["ALREADY_LIVE=true", f"LIVE_VERSION={health.get('version')}", f"OK={str(ok).lower()}"]
        write(lines)
        if not ok:
            raise RuntimeError("R45.3 marker live but health mismatch")
        return

    if "/api/r45-2/media-upload" not in source:
        raise RuntimeError("R45.2 media adapter must be live before R45.3")

    bindings, binding_version = base.resolve_bindings(api_base, headers)
    lines += [f"BINDING_SOURCE_VERSION_ID={binding_version}", f"BINDING_COUNT={len(bindings)}"]

    patched, n = re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW_VERSION}";', source, count=1)
    if n != 1:
        raise RuntimeError("VERSION anchor missing")

    helper_anchor = 'async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {'
    if helper_anchor not in patched:
        raise RuntimeError("video helper anchor missing")

    helpers = r'''
async function r453CreateInstagramPost(env, kind, text, videoUrl, imageUrls, mode, dueAt) {
  const channel=await resolveBufferChannel("instagram",env);
  const publishMode=["shareNow","customScheduled"].includes(String(mode || "")) ? String(mode) : "shareNow";
  let dueAtGraphQL="";
  if (publishMode === "customScheduled") {
    const parsed=new Date(String(dueAt || ""));
    if (!dueAt || Number.isNaN(parsed.getTime()) || parsed.getTime() <= Date.now()+60000) {
      throw new Error("R45.3 customScheduled exige dueAt futuro válido");
    }
    dueAtGraphQL=`dueAt: ${JSON.stringify(parsed.toISOString())}`;
  }
  const parts=[];
  if (videoUrl) parts.push(`{ video: { url: ${JSON.stringify(videoUrl)} } }`);
  for (const u of (Array.isArray(imageUrls)?imageUrls:[])) parts.push(`{ image: { url: ${JSON.stringify(u)} } }`);
  if (!parts.length) throw new Error("R45.3 assets missing");
  const story=kind === "story_video";
  const metadata=`metadata: { instagram: { type: ${story ? "story" : "post"} shouldShareToFeed: ${story ? "false" : "true"} } }`;
  const query=`mutation { createPost(input:{ text:${JSON.stringify(story ? "" : String(text || ""))} channelId:${JSON.stringify(channel.id)} schedulingType:automatic mode:${publishMode} ${dueAtGraphQL} aiAssisted:true assets:[${parts.join(",")}] ${metadata} }) { __typename ... on PostActionSuccess { post { id text status dueAt sentAt externalLink sharedNow shareMode channelService error { message rawError supportUrl } } } ... on MutationError { message } } }`;
  const result=await bufferGraphQL(query,env);
  const created=result?.data?.createPost;
  if (!created?.post) {
    const error=new Error(created?.message || firstGraphQLError(result) || "R45.3 Buffer create failed");
    error.payload=result;
    throw error;
  }
  return {post:created.post,channel};
}
__name(r453CreateInstagramPost,"r453CreateInstagramPost");

async function r453DeleteBufferPost(env, postId) {
  const id=String(postId || "").trim();
  if (!id) throw new Error("R45.3 postId required");
  const query=`mutation { deletePost(input:{ id:${JSON.stringify(id)} }) { __typename ... on DeletePostSuccess { id } ... on VoidMutationError { message } } }`;
  const result=await bufferGraphQL(query,env);
  const deleted=result?.data?.deletePost;
  if (deleted?.__typename !== "DeletePostSuccess" || !deleted?.id) {
    const error=new Error(deleted?.message || firstGraphQLError(result) || "R45.3 Buffer delete failed");
    error.payload=result;
    throw error;
  }
  return deleted;
}
__name(r453DeleteBufferPost,"r453DeleteBufferPost");

'''
    patched = patched.replace(helper_anchor, helpers + helper_anchor, 1)

    route_anchor = '      if (path === "/api/r45/generate" && request.method === "POST") {'
    if route_anchor not in patched:
        raise RuntimeError("R45 route anchor missing")

    routes = r'''
      if (path === "/api/r45-3/instagram-publish" && request.method === "POST") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const body=await readBody(request);
        const kind=String(body?.kind || "");
        const mode=String(body?.mode || "shareNow");
        if (!["story_video","mixed_carousel"].includes(kind)) return json({ok:false,error:"kind invalid"},400);
        if (!["shareNow","customScheduled"].includes(mode)) return json({ok:false,error:"mode invalid"},400);
        try {
          const created=await r453CreateInstagramPost(env,kind,body?.text,body?.videoUrl,body?.imageUrls,mode,body?.dueAt);
          return json({ok:true,version:VERSION,route:"/api/r45-3/instagram-publish",kind,mode,post:created.post,channel:created.channel});
        } catch(e) { return json({ok:false,error:e?.message || String(e),payload:e?.payload || null},400); }
      }

      if (path === "/api/r45-3/buffer-delete" && request.method === "POST") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const body=await readBody(request);
        try {
          const deleted=await r453DeleteBufferPost(env,body?.postId);
          return json({ok:true,version:VERSION,route:"/api/r45-3/buffer-delete",deleted});
        } catch(e) { return json({ok:false,error:e?.message || String(e),payload:e?.payload || null},400); }
      }

'''
    patched = patched.replace(route_anchor, routes + route_anchor, 1)

    marker = '            r452MixedCarouselSmoke: true,'
    if marker in patched:
        patched = patched.replace(marker, marker + '\n            r453ScheduledStoryVideo: true,\n            r453ScheduledMixedCarousel: true,\n            r453BufferDelete: true,', 1)

    probe = Path("/tmp/ugi-r45-3-worker.mjs")
    probe.write_text(patched, encoding="utf-8")
    check = subprocess.run(["node", "--check", str(probe)], text=True, capture_output=True)
    if check.returncode != 0:
        lines += ["NODE_CHECK=false", "NODE_ERROR=" + (check.stderr or check.stdout)[-1500:].replace("\n", " ")]
        write(lines)
        raise SystemExit(check.returncode)
    lines.append("NODE_CHECK=true")
    write(lines)

    version_id = base.create_version(api_base, headers, patched, bindings)
    deployment_id = base.deploy_version(api_base, headers, version_id)
    lines += [f"R45_3_VERSION_ID={version_id}", f"R45_3_DEPLOYMENT_ID={deployment_id}"]
    health = wait_health(NEW_VERSION)
    ok = health.get("ok") is True and health.get("version") == NEW_VERSION
    lines += [f"LIVE_VERSION={health.get('version')}", f"HEALTH_VERSION_MATCH={str(ok).lower()}", f"OK={str(ok).lower()}"]
    write(lines)
    if not ok:
        raise RuntimeError("R45.3 did not become live")


if __name__ == "__main__":
    main()
