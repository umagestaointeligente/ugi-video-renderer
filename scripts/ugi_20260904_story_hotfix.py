from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

import requests

import r45_instagram_multiformat_deploy as base

NEW_VERSION = "lola-v8-r45-4c-story-recovery-2026-09-04"
STATUS = Path("cloudflare/status/ugi-20260904-story-hotfix.txt")


def wait_health():
    last={}
    for _ in range(35):
        try:
            r=requests.get(base.WORKER_ORIGIN+"/api/health",timeout=15)
            last=r.json()
            if r.ok and last.get("ok") is True and last.get("version")==NEW_VERSION:
                return last
        except Exception as exc:
            last={"error":str(exc)}
        time.sleep(2)
    raise RuntimeError(f"health mismatch: {last}")


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

    text,n=re.subn(r'var VERSION = "[^"]+";',f'var VERSION = "{NEW_VERSION}";',source,count=1)
    if n!=1: raise RuntimeError("VERSION anchor missing")

    old='const instagramStory = /-IG-STORY-/i.test(String(draft?.contentId || "")) || /UGI-20260903-IG-(1030|1100|1415)-/i.test(String(draft?.contentId || "")) || ["story", "story_image", "story_video"].includes(String(draft?.type || "").toLowerCase());'
    new='const instagramStory = /-IG-STORY-/i.test(String(draft?.contentId || "")) || /UGI-20260903-IG-(1030|1100|1415)-/i.test(String(draft?.contentId || "")) || /UGI-20260904-IG-(0900|1030|1800)-/i.test(String(draft?.contentId || "")) || ["story", "story_image", "story_video"].includes(String(draft?.type || "").toLowerCase());'
    if old not in text: raise RuntimeError("Story metadata anchor missing")
    text=text.replace(old,new,1)

    anchor='      if (path === "/api/platform-publish" && request.method === "POST") {'
    if anchor not in text: raise RuntimeError("platform-publish route anchor missing")
    route=r'''      // UGI 2026-09-04 exact allowlisted recovery for Story posts that were created as Reels.
      if (path === "/api/ugi/story-recover-20260904" && request.method === "POST") {
        if (!isAdminAuthorized(request, env) && !isLolaUGIAuthorized(request, env)) {
          return json({ ok:false, error:"Não autorizado" },401);
        }
        const body=await readBody(request);
        const id=String(body?.id || "").trim();
        const allowed={
          "ugi-20260904021439-a82118ed6b7e": { dueAt:"2026-09-04T13:30:00.000Z", oldPostId:"6a9a35a582940622ebb360af" },
          "ugi-20260904021739-4fc5c7eb31fe": { dueAt:"2026-09-04T21:00:00.000Z", oldPostId:"6a9a35ba3134b0c21abe877c" }
        };
        const spec=allowed[id];
        if (!spec) return json({ok:false,error:"draft_not_allowlisted"},403);
        const due=new Date(spec.dueAt);
        if (Number.isNaN(due.getTime()) || due.getTime() <= Date.now()+60000) return json({ok:false,error:"recovery_slot_not_future"},409);
        const draft=await getLocalDraft(env,id);
        if (!draft) return json({ok:false,error:"draft_not_found"},404);
        const asset=draft?.assets?.instagram || {};
        const pub=asset?.publication || {};
        if (!asset?.videoUrl || asset?.ready !== true) return json({ok:false,error:"story_asset_not_ready"},409);
        if (String(pub?.bufferPostId || "") !== spec.oldPostId || String(pub?.status || "").toLowerCase() !== "scheduled") {
          return json({ok:false,error:"unexpected_existing_publication",publication:pub},409);
        }
        const recoveryAt=(new Date()).toISOString();
        let deleted=null;
        try {
          deleted=await r453DeleteBufferPost(env,spec.oldPostId);
          const created=await r453CreateInstagramPost(env,"story_video","",asset.videoUrl,[],"customScheduled",spec.dueAt);
          const post=created.post;
          const publication={
            status:publicationStateFromBufferPost(post), bufferStatus:post.status || null,
            bufferPostId:post.id || null, channelId:created.channel?.id || null,
            channelService:post.channelService || created.channel?.service || "instagram",
            channelSource:created.channel?.source || "BUFFER_CHANNEL_INSTAGRAM",
            mode:"customScheduled", dueAt:post.dueAt || spec.dueAt, sentAt:post.sentAt || null,
            externalLink:post.externalLink || null, sharedNow:Boolean(post.sharedNow),
            requestedAt:recoveryAt, updatedAt:(new Date()).toISOString(), error:post?.error?.message || null,
            bufferError:post?.error || null, recovery:"UGI_20260904_STORY_WRONG_FORMAT"
          };
          draft.assets={...(draft.assets || {}),instagram:{...asset,publication}};
          draft.updatedAt=publication.updatedAt;
          await saveLocalDraft(env,draft);
          await saveContentEvent(env,draft,"ugi_story_wrong_format_recovered",{platform:"instagram",oldBufferPostId:spec.oldPostId,newBufferPostId:publication.bufferPostId,dueAt:publication.dueAt});
          return json({ok:true,version:VERSION,recovery:"story_video",deletedOldPostId:deleted?.id || spec.oldPostId,publication,metadata:{instagram:{type:"story",shouldShareToFeed:false}}});
        } catch (e) {
          // Fail closed: after deletion, never silently restore the wrong-format Reel.
          if (deleted?.id) {
            const failedPublication={...pub,status:"cancelled",bufferStatus:"deleted_for_story_recovery",updatedAt:(new Date()).toISOString(),error:e?.message || String(e),recovery:"UGI_20260904_STORY_WRONG_FORMAT_FAILED"};
            draft.assets={...(draft.assets || {}),instagram:{...asset,publication:failedPublication}};
            draft.updatedAt=failedPublication.updatedAt;
            await saveLocalDraft(env,draft);
          }
          return json({ok:false,version:VERSION,errorClass:"story_recovery_failed",deletedOldPostId:deleted?.id || null,error:e?.message || String(e)},500);
        }
      }

'''
    text=text.replace(anchor,route+anchor,1)

    probe=Path('/tmp/ugi-20260904-story-hotfix.mjs')
    probe.write_text(text,encoding='utf-8')
    check=subprocess.run(['node','--check',str(probe)],text=True,capture_output=True)
    if check.returncode!=0:
        raise RuntimeError((check.stderr or check.stdout)[-2000:])

    bindings,binding_version=base.resolve_bindings(api_base,headers)
    version_id=base.create_version(api_base,headers,text,bindings)
    deployment_id=base.deploy_version(api_base,headers,version_id)
    health=wait_health()
    STATUS.parent.mkdir(parents=True,exist_ok=True)
    STATUS.write_text('\n'.join([
        'UGI_20260904_STORY_HOTFIX',
        f'BINDING_SOURCE_VERSION_ID={binding_version}',
        f'VERSION_ID={version_id}',
        f'DEPLOYMENT_ID={deployment_id}',
        f'LIVE_VERSION={health.get("version")}',
        'TODAY_STORY_METADATA_LOCK=0900,1030,1800',
        'EXACT_RECOVERY_ALLOWLIST=1030,1800',
        'OK=true',
    ])+'\n',encoding='utf-8')

if __name__=='__main__': main()
