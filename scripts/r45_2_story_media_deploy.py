from __future__ import annotations

import os, re, subprocess, time
from pathlib import Path
import requests
import r45_instagram_multiformat_deploy as base

NEW_VERSION = "lola-v8-r45-2-story-video-mixed-carousel-2026-08-30"
STATUS = Path("cloudflare/status/r45-2-story-media.txt")


def write(lines):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text("\n".join(lines)+"\n", encoding="utf-8")


def wait_health(expected, seconds=180):
    deadline=time.time()+seconds
    last={}
    while time.time()<deadline:
        try:
            r=requests.get(base.WORKER_ORIGIN+"/api/health", timeout=15)
            if r.status_code==200:
                last=r.json()
                if last.get("ok") is True and last.get("version")==expected:
                    return last
        except Exception:
            pass
        time.sleep(5)
    return last


def main():
    token=os.environ.get("CF_API_TOKEN","")
    account=os.environ.get("CF_ACCOUNT_ID","")
    if not token or not account:
        raise SystemExit("Cloudflare credentials missing")
    headers=base.api_headers(token)
    api_base=f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{base.WORKER_NAME}"
    live=requests.get(api_base+"/content/v2",headers=headers,timeout=45)
    live.raise_for_status()
    source=base.extract_worker_source(live)
    current=re.search(r'var VERSION = "([^"]+)";', source)
    lines=[f"BASE_VERSION={current.group(1) if current else 'unknown'}", "OK=false"]
    write(lines)
    bindings,binding_version=base.resolve_bindings(api_base,headers)
    lines += [f"BINDING_SOURCE_VERSION_ID={binding_version}",f"BINDING_COUNT={len(bindings)}"]

    patched,n=re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW_VERSION}";', source, count=1)
    if n!=1: raise RuntimeError("VERSION anchor missing")

    helper_anchor='async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {'
    if helper_anchor not in patched: raise RuntimeError("video helper anchor missing")
    helper=r'''
function r452DecodeBase64(value) {
  const raw = atob(String(value || "").replace(/^data:video\/mp4;base64,/, ""));
  const out = new Uint8Array(raw.length);
  for (let i=0;i<raw.length;i++) out[i]=raw.charCodeAt(i);
  return out;
}
__name(r452DecodeBase64, "r452DecodeBase64");

async function r452StoreMp4(env, origin, contentId, videoBase64) {
  const bytes=r452DecodeBase64(videoBase64);
  if (bytes.length < 20000) throw new Error("R45.2 MP4 too small");
  const head=new TextDecoder("latin1").decode(bytes.slice(0,64));
  if (!head.includes("ftyp")) throw new Error("R45.2 invalid MP4 signature");
  const safe=sanitizeCommerceId(String(contentId || crypto.randomUUID()));
  const key=`geradas/r45-2/${Date.now()}-${safe}.mp4`;
  await env.MEDIA.put(key,bytes,{httpMetadata:{contentType:"video/mp4",cacheControl:"public,max-age=31536000,immutable"}});
  const obj=await env.MEDIA.head(key);
  if (!obj || Number(obj.size||0)<=0) throw new Error("R45.2 R2 store failed");
  return {videoKey:key,videoUrl:`${origin}/media/${key}`,videoBytes:Number(obj.size||bytes.length)};
}
__name(r452StoreMp4,"r452StoreMp4");

async function r452CreateInstagramPost(env, kind, text, videoUrl, imageUrls) {
  const channel=await resolveBufferChannel("instagram",env);
  const parts=[];
  if (videoUrl) parts.push(`{ video: { url: ${JSON.stringify(videoUrl)} } }`);
  for (const u of (Array.isArray(imageUrls)?imageUrls:[])) parts.push(`{ image: { url: ${JSON.stringify(u)} } }`);
  if (!parts.length) throw new Error("R45.2 assets missing");
  const story=kind === "story_video";
  const metadata=`metadata: { instagram: { type: ${story ? "story" : "post"} shouldShareToFeed: ${story ? "false" : "true"} } }`;
  const query=`mutation { createPost(input:{ text:${JSON.stringify(story ? "" : String(text || ""))} channelId:${JSON.stringify(channel.id)} schedulingType:automatic mode:shareNow aiAssisted:true assets:[${parts.join(",")}] ${metadata} }) { __typename ... on PostActionSuccess { post { id text status dueAt sentAt externalLink sharedNow shareMode channelService error { message rawError supportUrl } } } ... on MutationError { message } } }`;
  const result=await bufferGraphQL(query,env);
  const created=result?.data?.createPost;
  if (!created?.post) {
    const e=new Error(created?.message || firstGraphQLError(result) || "R45.2 Buffer create failed");
    e.payload=result;
    throw e;
  }
  return {post:created.post,channel};
}
__name(r452CreateInstagramPost,"r452CreateInstagramPost");

'''
    patched=patched.replace(helper_anchor, helper+helper_anchor, 1)

    route_anchor='      if (path === "/api/r45/generate" && request.method === "POST") {'
    if route_anchor not in patched: raise RuntimeError("R45 route anchor missing")
    routes=r'''
      if (path === "/api/r45-2/media-upload" && request.method === "POST") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const body=await readBody(request);
        const contentId=String(body?.contentId || "").trim();
        const videoBase64=String(body?.videoBase64 || "");
        if (!contentId || !videoBase64) return json({ok:false,error:"contentId/videoBase64 required"},400);
        try {
          const stored=await r452StoreMp4(env,url.origin,contentId,videoBase64);
          return json({ok:true,version:VERSION,route:"/api/r45-2/media-upload",contentId,...stored,smokeOnly:true});
        } catch(e) { return json({ok:false,error:e?.message || String(e),smokeOnly:true},400); }
      }

      if (path === "/api/r45-2/instagram-publish" && request.method === "POST") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const body=await readBody(request);
        const kind=String(body?.kind || "");
        if (!["story_video","mixed_carousel"].includes(kind)) return json({ok:false,error:"kind invalid"},400);
        try {
          const created=await r452CreateInstagramPost(env,kind,body?.text,body?.videoUrl,body?.imageUrls);
          return json({ok:true,version:VERSION,route:"/api/r45-2/instagram-publish",kind,post:created.post,channel:created.channel,smokeOnly:true});
        } catch(e) { return json({ok:false,error:e?.message || String(e),payload:e?.payload || null,smokeOnly:true},400); }
      }

      if (path === "/api/r45-2/buffer-status" && request.method === "GET") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const id=String(url.searchParams.get("id") || "").trim();
        if (!id) return json({ok:false,error:"id required"},400);
        const live=await getBufferPostStatus(id,env);
        return json({ok:true,version:VERSION,route:"/api/r45-2/buffer-status",post:live.post,smokeOnly:true});
      }

'''
    patched=patched.replace(route_anchor, routes+route_anchor, 1)

    marker='            r45InstagramStoryImage: true,'
    if marker in patched:
        patched=patched.replace(marker, marker+'\n            r452StoryVideoSmoke: true,\n            r452MixedCarouselSmoke: true,',1)

    probe=Path('/tmp/ugi-r45-2-worker.mjs'); probe.write_text(patched,encoding='utf-8')
    check=subprocess.run(['node','--check',str(probe)],text=True,capture_output=True)
    if check.returncode!=0:
        lines += ["NODE_CHECK=false","NODE_ERROR="+(check.stderr or check.stdout)[-1500:].replace('\n',' ')]
        write(lines); raise SystemExit(check.returncode)
    lines.append("NODE_CHECK=true"); write(lines)

    version_id=base.create_version(api_base,headers,patched,bindings)
    deployment_id=base.deploy_version(api_base,headers,version_id)
    lines += [f"R45_2_VERSION_ID={version_id}",f"R45_2_DEPLOYMENT_ID={deployment_id}"]
    health=wait_health(NEW_VERSION)
    ok=health.get('version')==NEW_VERSION and health.get('ok') is True
    lines += [f"LIVE_VERSION={health.get('version')}",f"HEALTH_VERSION_MATCH={str(ok).lower()}",f"OK={str(ok).lower()}"]
    write(lines)
    if not ok: raise RuntimeError("R45.2 did not become live")

if __name__=='__main__': main()
