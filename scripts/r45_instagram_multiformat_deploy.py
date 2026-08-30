from __future__ import annotations

import json
import os
import re
import time
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

import requests

WORKER_NAME = "lola-operacional-ugi"
WORKER_ORIGIN = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
NEW_VERSION = "lola-v8-r45-0-instagram-multiformat-2026-08-30"
STATUS = Path("cloudflare/status/r45-instagram-multiformat.txt")
FALLBACK_BINDING_VERSION = "35dc7be4-2d9e-479d-8f27-39e726e0b58f"


def write_status(lines: list[str]) -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def api_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def extract_worker_source(resp: requests.Response) -> str:
    ctype = resp.headers.get("content-type", "")
    body = resp.content
    if "multipart/" not in ctype.lower():
        return body.decode("utf-8")
    envelope = f"Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
    msg = BytesParser(policy=default).parsebytes(envelope)
    candidates: list[bytes] = []
    for part in msg.iter_parts():
        ptype = (part.get_content_type() or "").lower()
        filename = (part.get_filename() or "").lower()
        payload = part.get_payload(decode=True) or b""
        if "javascript" in ptype or filename.endswith((".js", ".mjs")):
            candidates.append(payload)
    if not candidates:
        raise RuntimeError("No JS module in live Worker response")
    return max(candidates, key=len).decode("utf-8")


def resolve_bindings(base: str, headers: dict[str, str]) -> tuple[list[dict], str]:
    version_id = None
    try:
        r = requests.get(base + "/deployments", headers=headers, timeout=30)
        r.raise_for_status()
        payload = r.json()
        deployments = payload.get("result") or []
        if isinstance(deployments, dict):
            deployments = deployments.get("deployments") or deployments.get("items") or []
        for deployment in deployments:
            versions = deployment.get("versions") or []
            for version in versions:
                candidate = version.get("version_id") or version.get("versionId") or version.get("id")
                if candidate:
                    version_id = str(candidate)
                    break
            if version_id:
                break
    except Exception:
        version_id = None
    version_id = version_id or FALLBACK_BINDING_VERSION
    r = requests.get(base + f"/versions/{version_id}", headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    bindings = ((data.get("result") or {}).get("resources") or {}).get("bindings") or []
    if not bindings:
        raise RuntimeError(f"No bindings from Worker version {version_id}")
    normalized = []
    for binding in bindings:
        if binding.get("type") == "secret_text":
            normalized.append({"name": binding["name"], "type": "inherit", "version_id": "latest"})
        else:
            normalized.append(binding)
    return normalized, version_id


def patch_source(source: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    text, n = re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW_VERSION}";', source, count=1)
    if n != 1:
        raise RuntimeError(f"VERSION anchor count={n}")
    notes.append("VERSION_PATCH=1")

    old_allowed = 'const allowed = ["carousel", "post", "reel", "video"];'
    new_allowed = 'const allowed = ["carousel", "post", "visual_post", "story_image", "reel", "video"];'
    if text.count(old_allowed) != 1:
        raise RuntimeError(f"validateCommand allowed anchor count={text.count(old_allowed)}")
    text = text.replace(old_allowed, new_allowed, 1)
    old_msg = 'return "type deve ser \'post\', \'carousel\', \'reel\' ou \'video\'";'
    if old_msg in text:
        text = text.replace(old_msg, 'return "type deve ser post, carousel, visual_post, story_image, reel ou video";', 1)
    notes.append("COMMAND_TYPES_PATCH=1")

    gen_anchor = 'async function generateFromCommand(env, command, origin) {\n  if (command.type === "carousel") {'
    if text.count(gen_anchor) != 1:
        raise RuntimeError(f"generateFromCommand anchor count={text.count(gen_anchor)}")
    gen_replacement = '''async function generateFromCommand(env, command, origin) {
  if (command.type === "story_image") {
    return r45GenerateVisualStatic(env, command, origin, "story_image");
  }
  if (command.type === "visual_post") {
    return r45GenerateVisualStatic(env, command, origin, "visual_post");
  }
  if (command.type === "carousel") {'''
    text = text.replace(gen_anchor, gen_replacement, 1)
    notes.append("GENERATION_ROUTING_PATCH=1")

    helpers_anchor = 'async function generateCarousel(env, command, origin) {'
    if text.count(helpers_anchor) != 1:
        raise RuntimeError(f"generateCarousel anchor count={text.count(helpers_anchor)}")
    helpers = r'''function r45Esc(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
__name(r45Esc, "r45Esc");

function r45StaticAsset(draft) {
  if (!draft || !["post", "visual_post", "carousel", "story_image"].includes(String(draft.type || ""))) return null;
  if (draft.type === "carousel") {
    const urls = Array.isArray(draft.imageUrls) ? draft.imageUrls.filter(Boolean) : [];
    return urls.length >= 2 ? { kind:"carousel", ready:draft.renderStatus === "ready", imageUrls:urls } : null;
  }
  return draft.imageUrl ? { kind:draft.type === "story_image" ? "story_image" : "image", ready:draft.renderStatus === "ready", imageUrl:draft.imageUrl } : null;
}
__name(r45StaticAsset, "r45StaticAsset");

async function r45GenerateVisualStatic(env, command, origin, type) {
  if (!env.BROWSER) throw new Error("R45 exige BROWSER para visual_post/story_image");
  const id = crypto.randomUUID();
  const isStory = type === "story_image";
  const width = 1080;
  const height = isStory ? 1920 : 1350;
  const headline = sanitizeSlideText(command.hook || command.topic || "Gestão na prática").slice(0, 120);
  const body = sanitizeSlideText(command.keyMessage || command.instructions || command.objective || "Transforme a ideia em uma ação clara.").slice(0, 360);
  const cta = sanitizeSlideText(command.cta || (isStory ? "Veja mais no perfil" : "Salve para usar depois")).slice(0, 120);
  const slide = { number: 1, headline, body };
  const background = await generateCarouselVisualBackground(env, command, slide, 0);
  const bg = `data:image/jpeg;base64,${background.base64}`;
  const topPad = isStory ? 240 : 150;
  const bottomPad = isStory ? 260 : 160;
  const titleSize = isStory ? 74 : 64;
  const bodySize = isStory ? 42 : 36;
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    *{box-sizing:border-box}html,body{margin:0;width:${width}px;height:${height}px;font-family:Arial,Helvetica,sans-serif;background:#071528}
    #card{position:relative;width:${width}px;height:${height}px;overflow:hidden;background:#071528;color:#fff}
    .bg{position:absolute;inset:0;background-image:linear-gradient(180deg,rgba(4,17,29,.18) 0%,rgba(4,17,29,.48) 42%,rgba(4,17,29,.92) 100%),url('${bg}');background-size:cover;background-position:center}
    .grain{position:absolute;inset:0;background:linear-gradient(125deg,rgba(23,173,203,.16),transparent 34%,rgba(255,183,77,.10));mix-blend-mode:screen}
    .content{position:absolute;left:72px;right:72px;top:${topPad}px;bottom:${bottomPad}px;display:flex;flex-direction:column;justify-content:flex-end}
    .tag{display:inline-block;width:max-content;max-width:850px;padding:13px 22px;border-radius:999px;background:rgba(7,21,40,.72);border:1px solid rgba(255,255,255,.22);font-size:26px;font-weight:700;letter-spacing:.04em;margin-bottom:28px}
    h1{font-size:${titleSize}px;line-height:1.02;margin:0 0 30px;font-weight:800;letter-spacing:-.035em;text-shadow:0 3px 18px rgba(0,0,0,.5)}
    p{font-size:${bodySize}px;line-height:1.25;margin:0;color:#f4f7fa;font-weight:500;max-width:900px;text-shadow:0 2px 12px rgba(0,0,0,.5)}
    .cta{position:absolute;left:72px;right:72px;bottom:${isStory ? 110 : 78}px;padding-top:22px;border-top:2px solid rgba(255,255,255,.32);font-size:${isStory ? 32 : 29}px;font-weight:700;color:#d8f5ff}
    .brand{position:absolute;right:72px;top:${isStory ? 100 : 70}px;font-size:25px;font-weight:800;letter-spacing:.08em;color:white;opacity:.9}
  </style></head><body><div id="card"><div class="bg"></div><div class="grain"></div><div class="brand">UGI</div><div class="content"><div class="tag">UMA GESTÃO INTELIGENTE</div><h1>${r45Esc(headline)}</h1><p>${r45Esc(body)}</p></div><div class="cta">${r45Esc(cta)}</div></div></body></html>`;
  let shot = null;
  let last = null;
  for (let attempt=0; attempt<4; attempt++) {
    try {
      shot = await env.BROWSER.quickAction("screenshot", { html, selector:"#card", viewport:{width,height,deviceScaleFactor:1}, screenshotOptions:{type:"png",omitBackground:false} });
      if (shot?.ok) break;
      last = `HTTP ${shot?.status || "unknown"}`;
      await sleep(2500 * (attempt + 1));
    } catch (error) { last = error?.message || String(error); await sleep(2500 * (attempt + 1)); }
  }
  if (!shot?.ok) throw new Error(`R45 Browser render failed: ${last || shot?.status || "unknown"}`);
  const bytes = new Uint8Array(await shot.arrayBuffer());
  if (bytes.length < 5000) throw new Error("R45 static PNG invalid");
  const prefix = isStory ? "geradas/stories/" : "geradas/posts-visuais/";
  const key = `${prefix}${Date.now()}-${id}.png`;
  await env.MEDIA.put(key, bytes, {httpMetadata:{contentType:"image/png",cacheControl:"public,max-age=31536000,immutable"}});
  if (!await env.MEDIA.head(key)) throw new Error("R45 static R2 storage failed");
  const imageUrl = `${origin}/media/${key}`;
  const draft = {
    id, version:VERSION, type, commandId:command.id, contentId:command.contentId || id,
    experimentId:command.experimentId || null, variant:command.variant || null,
    commercialIntent:command.commercialIntent || null, commercialOffer:command.commercialOffer === true,
    editorialMode:command.editorialMode || "human_utility_first", copyLock:command.copyLock || {enabled:false},
    commerce:command.commerce || normalizeUGICommerce({}), topic:cleanTopic(command.topic), area:command.topic,
    angle:command.objective, hook:headline, cta, text:isStory ? "" : `${headline}\n\n${body}\n\n${cta}\n\n${BRAND_HASHTAG}`,
    imageUrl, imageKey:key, status:"draft", renderStatus:"ready", qualityStatus:"ready_for_review",
    qualityIssues:[], semanticValidationRequired:false, semanticValidationAvailable:true,
    semanticValidation:{pass:true,source:"r45_deterministic_visual_static",visualType:type},
    legacyContentLeakDetected:false, renderer:"r45-browser-human-utility", source:"r45-multiformat",
    createdAt:(new Date()).toISOString()
  };
  await saveLocalDraft(env,draft);
  await saveHistory(env,{briefId:`command-${command.id}`,topic:draft.topic,area:command.topic,angle:command.objective,type,createdAt:draft.createdAt});
  return draft;
}
__name(r45GenerateVisualStatic, "r45GenerateVisualStatic");

'''
    text = text.replace(helpers_anchor, helpers + helpers_anchor, 1)
    notes.append("STATIC_GENERATOR_INSERT=1")

    buffer_anchor = 'async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {'
    if text.count(buffer_anchor) != 1:
        raise RuntimeError(f"buffer video helper anchor count={text.count(buffer_anchor)}")
    buffer_helpers = r'''async function r45VerifyPublicImage(url, env) {
  const value=String(url || "").trim();
  if (!value) throw new Error("R45 image URL missing");
  const mediaMarker="/media/";
  if (value.startsWith(WORKER_ORIGIN || "") && value.includes(mediaMarker)) return {ok:true,source:"worker_media"};
  const response=await fetch(value,{method:"HEAD"});
  const ctype=String(response.headers.get("content-type") || "").toLowerCase();
  if (!response.ok || !ctype.startsWith("image/")) throw new Error(`R45 image validation failed HTTP=${response.status} type=${ctype}`);
  return {ok:true,source:"public_head",contentType:ctype};
}
__name(r45VerifyPublicImage, "r45VerifyPublicImage");

async function r45CreateBufferInstagramStaticPost(draft, mode, dueAt, env) {
  const asset=r45StaticAsset(draft);
  if (!asset?.ready) throw new Error("R45 static asset not ready");
  const channel=await resolveBufferChannel("instagram",env);
  const urls=asset.kind === "carousel" ? asset.imageUrls : [asset.imageUrl];
  for (const u of urls) await r45VerifyPublicImage(u,env);
  const assetGraphQL=urls.map(u=>`{ image: { url: ${JSON.stringify(u)} } }`).join(",");
  const dueAtGraphQL=mode === "customScheduled" ? `dueAt: ${JSON.stringify(dueAt)}` : "";
  const story=asset.kind === "story_image";
  const text=story ? "" : permanentCommercePublicationText(draft);
  const metadata=`metadata: { instagram: { type: ${story ? "story" : "post"} shouldShareToFeed: ${story ? "false" : "true"} } }`;
  const query=`mutation { createPost(input:{ text:${JSON.stringify(text)} channelId:${JSON.stringify(channel.id)} schedulingType:automatic mode:${mode} ${dueAtGraphQL} aiAssisted:true assets:[${assetGraphQL}] ${metadata} }) { __typename ... on PostActionSuccess { post { id text status dueAt sentAt externalLink sharedNow shareMode channelService error { message rawError supportUrl } } } ... on MutationError { message } } }`;
  const result=await bufferGraphQL(query,env);
  const created=result?.data?.createPost;
  if (!created?.post) {
    const error=new Error(created?.message || firstGraphQLError(result) || "Buffer did not create R45 static post");
    error.bufferDiagnostics={...(result?.__bufferDiagnostics || {}),responseType:created?.__typename || null,mutationMessage:created?.message || null};
    error.bufferPayload=result;
    throw error;
  }
  return {post:created.post,channel,assetValidation:{ok:true,kind:asset.kind,count:urls.length},bufferDiagnostics:{...(result?.__bufferDiagnostics || {}),responseType:created?.__typename || null,postError:created?.post?.error || null}};
}
__name(r45CreateBufferInstagramStaticPost, "r45CreateBufferInstagramStaticPost");

'''
    text = text.replace(buffer_anchor, buffer_helpers + buffer_anchor, 1)
    notes.append("STATIC_BUFFER_HELPER_INSERT=1")

    route_anchor = '      if (path === "/api/platform-publish" && request.method === "POST") {'
    if text.count(route_anchor) != 1:
        raise RuntimeError(f"platform publish route anchor count={text.count(route_anchor)}")
    routes = r'''      if (path === "/api/r45/generate" && request.method === "POST") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const body=await readBody(request);
        const error=validateCommand(body || {});
        if (error) return json({ok:false,error},400);
        const command=createCommand(body);
        await saveCommand(env,command);
        try {
          const draft=await generateFromCommand(env,command,url.origin);
          command.generationStatus="generated"; command.draftId=draft?.id || null; command.updatedAt=(new Date()).toISOString();
          await saveCommand(env,command);
          return json({ok:true,version:VERSION,route:"/api/r45/generate",commandId:command.id,draftId:draft?.id || null,contentId:draft?.contentId || command.contentId,type:draft?.type || command.type,draft,publicationTriggered:false});
        } catch (e) {
          command.generationStatus="failed"; command.generationError=e?.message || String(e); command.updatedAt=(new Date()).toISOString();
          await saveCommand(env,command);
          return json({ok:false,version:VERSION,route:"/api/r45/generate",errorClass:"r45_generation_failed",error:e?.message || String(e),commandId:command.id,publicationTriggered:false},500);
        }
      }

      if (path === "/api/r45/static-approval" && request.method === "POST") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const body=await readBody(request); const id=String(body?.id || "").trim();
        const decision=String(body?.decision || "").trim().toLowerCase();
        if (!id || !["approved","rejected"].includes(decision)) return json({ok:false,error:"id/decision invalid"},400);
        const draft=await getLocalDraft(env,id); if (!draft) return json({ok:false,error:"Rascunho não encontrado"},404);
        const descriptor=r45StaticAsset(draft); if (!descriptor?.ready) return json({ok:false,error:"R45 static asset not ready"},409);
        const current=draft.assets?.instagram || {};
        if (current?.publication?.bufferPostId && !["error","cancelled"].includes(String(current?.publication?.status || "").toLowerCase())) return json({ok:false,error:"R45 static already has active Buffer publication",publication:current.publication},409);
        const at=(new Date()).toISOString();
        draft.assets={...(draft.assets || {}),instagram:{...descriptor,...current,approvalStatus:decision,approvalDecisionAt:at}};
        draft.workflowStatus=decision === "approved" ? "approved" : "rejected"; draft.updatedAt=at;
        const saved=await saveLocalDraft(env,draft);
        await saveContentEvent(env,saved,decision === "approved" ? "r45_static_approved" : "r45_static_rejected",{platform:"instagram",type:draft.type});
        return json({ok:true,version:VERSION,route:"/api/r45/static-approval",draftId:id,platform:"instagram",decision,asset:saved.assets?.instagram,publicationTriggered:false});
      }

      if (path.startsWith("/api/r45/static-eligibility/") && request.method === "GET") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const id=decodeURIComponent(path.slice("/api/r45/static-eligibility/".length)); const draft=await getLocalDraft(env,id);
        if (!draft) return json({ok:false,error:"Rascunho não encontrado"},404);
        const descriptor=r45StaticAsset(draft); const current=draft.assets?.instagram || {};
        const reasons=[]; if (!descriptor) reasons.push("asset_missing"); else if (!descriptor.ready) reasons.push("asset_not_ready");
        if (normalizeAssetApprovalStatus(current.approvalStatus) !== "approved") reasons.push("pending_approval");
        reasons.push(...commerceGateReasons(draft),...semanticGateReasons(draft));
        return json({ok:true,version:VERSION,route:"/api/r45/static-eligibility",draftId:id,platformStates:{instagram:{assetExists:Boolean(descriptor),ready:Boolean(descriptor?.ready),kind:descriptor?.kind || null,approvalStatus:normalizeAssetApprovalStatus(current.approvalStatus),eligible:reasons.length===0,reasons,bufferPostId:current?.publication?.bufferPostId || null,publicationStatus:current?.publication?.status || null}},eligible:reasons.length===0,publicationTriggered:false});
      }

      if (path === "/api/r45/static-publish" && request.method === "POST") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const body=await readBody(request); const id=String(body?.id || "").trim(); const mode=normalizePublishMode(body?.mode);
        if (!id || !mode) return json({ok:false,error:"id/mode invalid"},400);
        let dueAt=null; if (mode === "customScheduled") { const parsed=new Date(body?.dueAt || ""); if (Number.isNaN(parsed.getTime()) || parsed.getTime() <= Date.now()+60000) return json({ok:false,error:"dueAt must be >1 minute in future"},400); dueAt=parsed.toISOString(); }
        const draft=await getLocalDraft(env,id); if (!draft) return json({ok:false,error:"Rascunho não encontrado"},404);
        const descriptor=r45StaticAsset(draft); const asset=draft.assets?.instagram || {};
        const gate=[...commerceGateReasons(draft),...semanticGateReasons(draft)]; if (gate.length) return json({ok:false,errorClass:"commerce_or_semantic_gate_blocked",reasons:gate,publicationTriggered:false},409);
        if (!descriptor?.ready || normalizeAssetApprovalStatus(asset.approvalStatus) !== "approved") return json({ok:false,error:"R45 static asset must be ready and approved"},409);
        if (asset?.publication?.bufferPostId && !["error","cancelled"].includes(String(asset?.publication?.status || "").toLowerCase())) return json({ok:false,error:"R45 static already has active Buffer publication",publication:asset.publication},409);
        const locks=await acquirePublicationLocks(env,draft,"instagram",mode,dueAt); if (!locks.acquired) return json({ok:false,errorClass:"publication_idempotency_lock_exists",lockType:locks.failedType,existingLock:locks.existing || null,publicationTriggered:false},409);
        const requestedAt=(new Date()).toISOString();
        try {
          const created=await r45CreateBufferInstagramStaticPost(draft,mode,dueAt,env); const post=created.post;
          const publication={status:publicationStateFromBufferPost(post),bufferStatus:post.status || null,bufferPostId:post.id || null,channelId:created.channel?.id || null,channelService:post.channelService || created.channel?.service || "instagram",channelSource:created.channel?.source || null,mode,dueAt:post.dueAt || dueAt || null,sentAt:post.sentAt || null,externalLink:post.externalLink || null,sharedNow:Boolean(post.sharedNow),requestedAt,updatedAt:(new Date()).toISOString(),error:post?.error?.message || null,bufferError:post?.error || null,bufferDiagnostics:created.bufferDiagnostics || null};
          draft.assets={...(draft.assets || {}),instagram:{...asset,...descriptor,publication}}; draft.updatedAt=publication.updatedAt; const saved=await saveLocalDraft(env,draft);
          await updatePublicationLocks(env,locks,{state:"confirmed",bufferPostId:publication.bufferPostId || null,bufferStatus:publication.bufferStatus || null,dueAt:publication.dueAt || dueAt || null,externalLink:publication.externalLink || null});
          await saveContentEvent(env,saved,mode === "shareNow" ? "r45_static_publish_requested" : "r45_static_scheduled",{platform:"instagram",type:draft.type,bufferPostId:publication.bufferPostId,dueAt:publication.dueAt});
          return json({ok:true,version:VERSION,route:"/api/r45/static-publish",platform:"instagram",type:draft.type,mode,publication,post,assetValidation:created.assetValidation,publicationTriggered:true});
        } catch (e) {
          try { await updatePublicationLocks(env,locks,{state:"uncertain",failureAt:(new Date()).toISOString(),error:e?.message || String(e)}); } catch (_) {}
          return json({ok:false,version:VERSION,route:"/api/r45/static-publish",errorClass:"r45_static_publish_failed",error:e?.message || String(e),bufferDiagnostics:e?.bufferDiagnostics || null,bufferPayload:e?.bufferPayload || null,publicationTriggered:false},400);
        }
      }

      if (path === "/api/r45/static-publication-status" && request.method === "GET") {
        if (!isAdminAuthorized(request,env) && !isLolaUGIAuthorized(request,env)) return json({ok:false,error:"Não autorizado"},401);
        const id=String(url.searchParams.get("id") || "").trim(); const draft=id ? await getLocalDraft(env,id) : null;
        const pub=draft?.assets?.instagram?.publication || null; if (!draft || !pub?.bufferPostId) return json({ok:false,error:"R45 static publication not found"},404);
        const live=await getBufferPostStatus(pub.bufferPostId,env); const post=live.post;
        const publication={...pub,status:publicationStateFromBufferPost(post),bufferStatus:post.status || null,dueAt:post.dueAt || pub.dueAt || null,sentAt:post.sentAt || null,externalLink:post.externalLink || null,sharedNow:Boolean(post.sharedNow),error:post?.error?.message || null,bufferError:post?.error || null,updatedAt:(new Date()).toISOString()};
        draft.assets={...(draft.assets || {}),instagram:{...draft.assets.instagram,publication}}; await saveLocalDraft(env,draft);
        return json({ok:true,version:VERSION,route:"/api/r45/static-publication-status",draftId:id,platform:"instagram",type:draft.type,publication});
      }

'''
    text = text.replace(route_anchor, routes + route_anchor, 1)
    notes.append("R45_ROUTES_INSERT=1")

    # Keep video functions and existing routes untouched. Health marker is additive only.
    marker = '            multiPlatformPublishing: true,'
    if marker in text:
        text = text.replace(marker, marker + '\n            r45InstagramMultiFormat: true,\n            r45InstagramCarousel: true,\n            r45InstagramVisualPost: true,\n            r45InstagramStoryImage: true,', 1)
        notes.append("HEALTH_CAPABILITY_PATCH=1")
    else:
        notes.append("HEALTH_CAPABILITY_PATCH=0")

    required = [
        NEW_VERSION, '"story_image"', '"visual_post"', '/api/r45/generate',
        '/api/r45/static-publish', '/api/r45/static-publication-status',
        'r45CreateBufferInstagramStaticPost', 'r45GenerateVisualStatic'
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError("R45 patch missing markers: " + ",".join(missing))
    return text, notes


def create_version(base: str, headers: dict[str, str], source: str, bindings: list[dict]) -> str:
    metadata = {
        "main_module": "worker.js",
        "compatibility_date": "2026-08-20",
        "annotations": {"workers/message": "UGI R45 Instagram MultiFormat", "workers/tag": "ugi-r45-instagram-multiformat"},
        "bindings": bindings,
    }
    r = requests.post(
        base + "/versions?bindings_inherit=strict",
        headers=headers,
        files={
            "metadata": (None, json.dumps(metadata, separators=(",", ":")), "application/json"),
            "worker.js": ("worker.js", source.encode("utf-8"), "application/javascript+module"),
        },
        timeout=90,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Cloudflare version create HTTP {r.status_code}: {r.text[:1600]}")
    data = r.json()
    if not data.get("success"):
        raise RuntimeError("Cloudflare version create failed: " + json.dumps(data.get("errors"))[:1600])
    vid = str((data.get("result") or {}).get("id") or "")
    if not vid:
        raise RuntimeError("Cloudflare version id missing")
    return vid


def deploy_version(base: str, headers: dict[str, str], version_id: str) -> str:
    payload = {
        "strategy": "percentage",
        "versions": [{"version_id": version_id, "percentage": 100}],
        "annotations": {"workers/message": "UGI R45 Instagram MultiFormat"},
    }
    r = requests.post(base + "/deployments", headers={**headers, "Content-Type": "application/json"}, json=payload, timeout=45)
    if r.status_code != 200:
        raise RuntimeError(f"Cloudflare deploy HTTP {r.status_code}: {r.text[:1600]}")
    data = r.json()
    if not data.get("success"):
        raise RuntimeError("Cloudflare deployment failed: " + json.dumps(data.get("errors"))[:1600])
    return str((data.get("result") or {}).get("id") or "")


def wait_health() -> dict:
    last = {}
    for _ in range(20):
        try:
            r = requests.get(WORKER_ORIGIN + "/api/health", timeout=15)
            if r.status_code == 200:
                last = r.json()
                if last.get("ok") is True and last.get("version") == NEW_VERSION:
                    return last
        except Exception:
            pass
        time.sleep(3)
    raise RuntimeError("R45 health timeout: " + json.dumps(last, ensure_ascii=False)[:1600])


def main() -> None:
    lines = ["R45_STAGE=START", "OK=false"]
    write_status(lines)
    token = os.environ.get("CF_API_TOKEN", "")
    account = os.environ.get("CF_ACCOUNT_ID", "")
    if not token or not account:
        raise SystemExit("Cloudflare credentials missing")
    headers = api_headers(token)
    base = f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{WORKER_NAME}"

    live = requests.get(base + "/content/v2", headers=headers, timeout=45)
    live.raise_for_status()
    source = extract_worker_source(live)
    current_match = re.search(r'var VERSION = "([^"]+)";', source)
    current_version = current_match.group(1) if current_match else "unknown"
    lines = ["R45_STAGE=FETCHED", f"BASE_VERSION={current_version}", f"BASE_SOURCE_BYTES={len(source.encode('utf-8'))}"]

    if current_version == NEW_VERSION:
        lines += ["ALREADY_DEPLOYED=true", "OK=true"]
        write_status(lines)
        return

    bindings, binding_version = resolve_bindings(base, headers)
    lines += [f"BINDING_SOURCE_VERSION_ID={binding_version}", f"BINDING_COUNT={len(bindings)}"]
    patched, notes = patch_source(source)
    lines += notes + [f"PATCHED_SOURCE_BYTES={len(patched.encode('utf-8'))}"]
    # Syntax smoke via Node is done by workflow before this script reaches deploy.
    version_id = create_version(base, headers, patched, bindings)
    lines += [f"R45_VERSION_ID={version_id}"]
    deployment_id = deploy_version(base, headers, version_id)
    lines += [f"R45_DEPLOYMENT_ID={deployment_id}"]
    health = wait_health()
    lines += [f"LIVE_VERSION={health.get('version')}", "HEALTH_OK=true", "OK=true"]
    write_status(lines)


if __name__ == "__main__":
    main()
