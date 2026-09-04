from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

import requests
import r45_instagram_multiformat_deploy as base

NEW_VERSION = "lola-v8-r45-6-linkedin-buffer-text-2026-09-04"
STATUS = Path("cloudflare/status/ugi-linkedin-buffer-text.txt")


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

    if current_version == NEW_VERSION and "/api/linkedin-text-publish" in source:
        lines += ["ALREADY_DEPLOYED=true", "OK=true"]
        write_status(lines)
        return

    bindings, binding_version = base.resolve_bindings(api_base, headers)
    lines += [f"BINDING_SOURCE_VERSION_ID={binding_version}", f"BINDING_COUNT={len(bindings)}"]

    patched, n = re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW_VERSION}";', source, count=1)
    if n != 1:
        raise RuntimeError(f"VERSION anchor count={n}")

    helper_anchor = 'async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {'
    if patched.count(helper_anchor) != 1:
        raise RuntimeError(f"helper anchor count={patched.count(helper_anchor)}")
    helper = r'''async function createBufferLinkedInTextPost(text, mode, dueAt, env) {
  const channel = await resolveBufferChannel("linkedin", env);
  const service = String(channel?.service || "").toLowerCase();
  const identity = `${String(channel?.name || "")} ${String(channel?.displayName || "")}`.toLowerCase();
  if (service !== "linkedin") {
    const error = new Error(`Canal Buffer resolvido não é LinkedIn: ${service || "unknown"}`);
    error.stage = "channel_validation";
    throw error;
  }
  if (/paulo[- ]?oliveira/.test(identity)) {
    const error = new Error("Perfil pessoal Paulo Oliveira é destino proibido para UGI.");
    error.stage = "channel_validation";
    throw error;
  }
  if (identity && !/(ugi|uma[- ]gest[aã]o[- ]inteligente)/i.test(identity)) {
    const error = new Error(`Canal LinkedIn não corresponde à Company Page UGI: ${identity}`);
    error.stage = "channel_validation";
    throw error;
  }
  const dueAtGraphQL = mode === "customScheduled" ? `dueAt: ${JSON.stringify(dueAt)}` : "";
  const query = `mutation { createPost(input:{ text:${JSON.stringify(String(text || ""))} channelId:${JSON.stringify(channel.id)} schedulingType:automatic mode:${mode} ${dueAtGraphQL} aiAssisted:true }) { __typename ... on PostActionSuccess { post { id text status dueAt sentAt externalLink sharedNow shareMode channelService error { message rawError supportUrl } } } ... on MutationError { message } } }`;
  let result;
  try {
    result = await bufferGraphQL(query, env);
  } catch (error) {
    error.stage = error.stage || "create_post";
    throw error;
  }
  const created = result?.data?.createPost;
  if (!created?.post?.id) {
    const error = new Error(created?.message || firstGraphQLError(result) || "Buffer não criou o post LinkedIn.");
    error.stage = "create_post";
    error.bufferDiagnostics = result?.__bufferDiagnostics || null;
    error.bufferPayload = result;
    throw error;
  }
  return { post: created.post, channel, bufferDiagnostics: result?.__bufferDiagnostics || null };
}
__name(createBufferLinkedInTextPost, "createBufferLinkedInTextPost");

'''
    patched = patched.replace(helper_anchor, helper + helper_anchor, 1)

    route_anchor = 'if (path === "/api/platform-publish" && request.method === "POST") {'
    if patched.count(route_anchor) != 1:
        raise RuntimeError(f"route anchor count={patched.count(route_anchor)}")
    routes = r'''if (path === "/api/linkedin-text-publish" && request.method === "POST") {
        if (!isAdminAuthorized(request, env) && !isLolaUGIAuthorized(request, env)) {
          return json({ok:false,error:"Não autorizado",publicationTriggered:false,bufferMutationPerformed:false},401);
        }
        const body = await readBody(request);
        const text = String(body?.text || "").trim();
        const mode = normalizePublishMode(body?.mode || "shareNow");
        if (!text) return json({ok:false,error:"text ausente",publicationTriggered:false,bufferMutationPerformed:false},400);
        if (text.length > 3000) return json({ok:false,error:"text excede 3000 caracteres",publicationTriggered:false,bufferMutationPerformed:false},400);
        if (!mode || !["shareNow","customScheduled","addToQueue"].includes(mode)) return json({ok:false,error:"mode inválido",publicationTriggered:false,bufferMutationPerformed:false},400);
        let dueAt = null;
        if (mode === "customScheduled") {
          const parsed = new Date(String(body?.dueAt || ""));
          if (Number.isNaN(parsed.getTime()) || parsed.getTime() <= Date.now()+60000) return json({ok:false,error:"dueAt deve estar >1 minuto no futuro",publicationTriggered:false,bufferMutationPerformed:false},400);
          dueAt = parsed.toISOString();
        }
        let created;
        try {
          created = await createBufferLinkedInTextPost(text, mode, dueAt, env);
        } catch (error) {
          const stage = String(error?.stage || "channel_discovery");
          const mutationState = stage === "channel_discovery" || stage === "channel_validation" ? false : "unknown";
          return json({ok:false,version:VERSION,route:"/api/linkedin-text-publish",errorClass:"linkedin_buffer_publish_failed",stage,error:error?.message || String(error),bufferDiagnostics:error?.bufferDiagnostics || null,publicationTriggered:false,bufferMutationPerformed:mutationState}, stage === "channel_discovery" ? 503 : 400);
        }
        const post = created.post;
        return json({
          ok:true, version:VERSION, route:"/api/linkedin-text-publish", platform:"linkedin", mode,
          target:{type:"LinkedIn Page",pageName:"UGI — Uma Gestão Inteligente",channelId:created.channel?.id || null,channelName:created.channel?.name || created.channel?.displayName || null,channelService:created.channel?.service || "linkedin",personalProfileTargetAllowed:false},
          publication:{status:publicationStateFromBufferPost(post),bufferStatus:post.status || null,bufferPostId:post.id || null,dueAt:post.dueAt || dueAt || null,sentAt:post.sentAt || null,externalLink:post.externalLink || null,sharedNow:Boolean(post.sharedNow),error:post?.error?.message || null},
          publicationTriggered:true,bufferMutationPerformed:true
        });
      }

      if (path === "/api/linkedin-publication-status" && request.method === "GET") {
        if (!isAdminAuthorized(request, env) && !isLolaUGIAuthorized(request, env)) return json({ok:false,error:"Não autorizado"},401);
        const postId = String(url.searchParams.get("postId") || "").trim();
        if (!postId) return json({ok:false,error:"postId ausente"},400);
        try {
          const live = await getBufferPostStatus(postId, env);
          const post = live.post;
          return json({ok:true,version:VERSION,route:"/api/linkedin-publication-status",platform:"linkedin",publication:{status:publicationStateFromBufferPost(post),bufferStatus:post.status || null,bufferPostId:post.id || postId,dueAt:post.dueAt || null,sentAt:post.sentAt || null,externalLink:post.externalLink || null,sharedNow:Boolean(post.sharedNow),error:post?.error?.message || null}});
        } catch (error) {
          return json({ok:false,version:VERSION,route:"/api/linkedin-publication-status",error:error?.message || String(error),bufferDiagnostics:error?.bufferDiagnostics || null},400);
        }
      }

      '''
    patched = patched.replace(route_anchor, routes + route_anchor, 1)

    # Surface the capability in health output without touching existing behavior.
    health_anchor = 'supportedPublishModes: ["shareNow", "customScheduled", "addToQueue"],'
    if health_anchor in patched:
        patched = patched.replace(health_anchor, health_anchor + '\n            linkedinBufferTextPublishing: true,', 1)

    required = [NEW_VERSION, "/api/linkedin-text-publish", "/api/linkedin-publication-status", "createBufferLinkedInTextPost", "personalProfileTargetAllowed:false"]
    missing = [x for x in required if x not in patched]
    if missing:
        raise RuntimeError("LinkedIn patch markers missing: " + ",".join(missing))

    probe = Path("/tmp/ugi-linkedin-buffer-worker.mjs")
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
    lines += ["HEALTH_OK=false", "LAST_HEALTH=" + json.dumps(last,ensure_ascii=False)[:800]]
    write_status(lines)
    raise RuntimeError("LinkedIn Buffer Worker health timeout")


if __name__ == "__main__":
    main()
