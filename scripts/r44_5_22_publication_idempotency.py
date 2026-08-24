from __future__ import annotations
import json, os, re, time
from pathlib import Path
import requests
import scripts.r44_5_18_repair_v2 as base

STATUS=Path('cloudflare/status/r44-5-22-publication-idempotency.txt')
WORKER='lola-operacional-ugi'
ORIGIN='https://lola-operacional-ugi.umagestaointeligente.workers.dev'
NEW='lola-v8-r44-5-22-publication-idempotency-2026-08-24'


def write(lines):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text('\n'.join(lines)+'\n', encoding='utf-8')


def fetch_live(api,h):
    r=requests.get(api+'/content/v2',headers=h,timeout=45)
    r.raise_for_status()
    return base.extract_source(r)


def active_bindings(api,h):
    """Recover bindings from the exact version currently receiving 100% traffic."""
    r=requests.get(api+'/deployments',headers=h,timeout=30)
    r.raise_for_status()
    deployments=((r.json().get('result') or {}).get('deployments') or [])
    if not deployments:
        raise RuntimeError('no active Worker deployment returned')
    versions=deployments[0].get('versions') or []
    active=next((v for v in versions if float(v.get('percentage') or 0) >= 99.9), None) or (versions[0] if versions else None)
    if not active or not active.get('version_id'):
        raise RuntimeError('active Worker version id missing')
    version_id=str(active['version_id'])
    vr=requests.get(api+f'/versions/{version_id}',headers=h,timeout=30)
    vr.raise_for_status()
    restored=base.restored_bindings(vr.json())
    return version_id, restored


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise RuntimeError(f'{label} anchor count={text.count(old)}')
    return text.replace(old,new,1)


def patch(src):
    t=base.strip_temp_routes(src)
    t=re.sub(r'\n\s*// BEGIN_R44_5_22_PUBLICATION_IDEMPOTENCY.*?// END_R44_5_22_PUBLICATION_IDEMPOTENCY\s*\n','\n',t,flags=re.S)
    t=re.sub(r'\n\s*// BEGIN_R44_5_22_LOCK_ROUTES.*?// END_R44_5_22_LOCK_ROUTES\s*\n','\n',t,flags=re.S)

    t,n=re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW}";', t, count=1)
    if n != 1:
        raise RuntimeError('VERSION anchor mismatch')

    const_anchor='var DELIVERY_PREFIX = "lola/commerce/deliveries/";\n'
    t=replace_once(t,const_anchor,const_anchor+'var PUBLICATION_LOCK_PREFIX = "lola/publication-locks/";\n','DELIVERY_PREFIX')

    helper_anchor='async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {\n'
    helper=r'''// BEGIN_R44_5_22_PUBLICATION_IDEMPOTENCY
function publicationIdentity(draft) {
  return String(draft?.contentId || draft?.content_id || draft?.renderId || draft?.id || "unknown");
}
__name(publicationIdentity, "publicationIdentity");

function publicationAssetLockKey(draft, platform) {
  const p = String(platform || "unknown").toLowerCase();
  return PUBLICATION_LOCK_PREFIX + "asset/" + encodeURIComponent(p) + "/" + encodeURIComponent(publicationIdentity(draft)) + ".json";
}
__name(publicationAssetLockKey, "publicationAssetLockKey");

function publicationSlotLockKey(platform, mode, dueAt) {
  const p = String(platform || "unknown").toLowerCase();
  const m = String(mode || "unknown");
  const slot = m === "customScheduled" && dueAt
    ? String(new Date(dueAt).toISOString())
    : "immediate";
  return PUBLICATION_LOCK_PREFIX + "slot/" + encodeURIComponent(p) + "/" + encodeURIComponent(m) + "/" + encodeURIComponent(slot) + ".json";
}
__name(publicationSlotLockKey, "publicationSlotLockKey");

async function readPublicationLock(env, key) {
  if (!env.MEDIA) return null;
  const obj = await env.MEDIA.get(key);
  if (!obj) return null;
  try { return await obj.json(); } catch { return { key, state: "unreadable" }; }
}
__name(readPublicationLock, "readPublicationLock");

async function createPublicationLock(env, key, value) {
  const created = await env.MEDIA.put(key, JSON.stringify(value, null, 2), {
    onlyIf: { etagDoesNotMatch: "*" },
    httpMetadata: { contentType: "application/json" }
  });
  if (!created) return { acquired:false, key, existing:await readPublicationLock(env,key) };
  return { acquired:true, key, token:value.token, value };
}
__name(createPublicationLock, "createPublicationLock");

async function acquirePublicationLocks(env, draft, platform, mode, dueAt) {
  if (!env.MEDIA) throw new Error("R2 MEDIA não conectado para publication lock");
  const token = crypto.randomUUID();
  const requestedAt = new Date().toISOString();
  const common = {
    schemaVersion:"1.1", token, state:"creating", project:"UGI",
    draftId:draft?.id || null, renderId:draft?.renderId || null,
    contentId:draft?.contentId || draft?.content_id || null,
    platform, mode, dueAt:dueAt || null, requestedAt, bufferPostId:null
  };
  const assetKey = publicationAssetLockKey(draft, platform);
  const asset = await createPublicationLock(env, assetKey, {...common, lockType:"asset", key:assetKey});
  if (!asset.acquired) return { acquired:false, failedType:"asset", existing:asset.existing, locks:[asset] };
  const slotKey = publicationSlotLockKey(platform, mode, dueAt);
  const slot = await createPublicationLock(env, slotKey, {...common, lockType:"slot", key:slotKey});
  if (!slot.acquired) {
    await updatePublicationLock(env, asset, {state:"blocked_by_existing_slot", blockedBy:slotKey});
    return { acquired:false, failedType:"slot", existing:slot.existing, locks:[asset,slot] };
  }
  return { acquired:true, token, locks:[asset,slot], assetKey, slotKey };
}
__name(acquirePublicationLocks, "acquirePublicationLocks");

async function updatePublicationLock(env, lock, patch) {
  if (!env.MEDIA || !lock?.key) return null;
  const current = (await readPublicationLock(env, lock.key)) || {};
  if (lock.token && current.token && current.token !== lock.token) throw new Error("publication_lock_owner_mismatch");
  const next = { ...current, ...patch, updatedAt:new Date().toISOString() };
  await env.MEDIA.put(lock.key, JSON.stringify(next, null, 2), { httpMetadata:{contentType:"application/json"} });
  return next;
}
__name(updatePublicationLock, "updatePublicationLock");

async function updatePublicationLocks(env, group, patch) {
  const results=[];
  for (const lock of group?.locks || []) if (lock?.acquired) results.push(await updatePublicationLock(env,lock,patch));
  return results;
}
__name(updatePublicationLocks, "updatePublicationLocks");
// END_R44_5_22_PUBLICATION_IDEMPOTENCY

'''
    t=replace_once(t,helper_anchor,helper+helper_anchor,'createBufferPlatformVideoPost')

    route_start=t.find('      if (path === "/api/platform-publish" && request.method === "POST") {')
    route_end=t.find('      if (path.startsWith("/api/platform-publication-eligibility/")', route_start)
    if route_start < 0 or route_end < 0:
        raise RuntimeError('platform publish route bounds missing')
    route=t[route_start:route_end]

    requested_candidates=[
        '        const requestedAt = (/* @__PURE__ */ new Date()).toISOString();\n        try {',
        '        const requestedAt = new Date().toISOString();\n        try {'
    ]
    requested_anchor=next((x for x in requested_candidates if route.count(x)==1),None)
    if not requested_anchor:
        raise RuntimeError('platform publish requestedAt anchor mismatch')
    requested_repl='''        // R44.5.22 — exactly-once gate before any Buffer mutation.\n        // Asset lock blocks repeated publication of the same UGI content on the same platform.\n        // Slot lock blocks different drafts from occupying the same platform/time slot.\n        const publicationLocks = await acquirePublicationLocks(env, draft, platform, mode, dueAt);\n        if (!publicationLocks.acquired) {\n          return json({\n            ok:false, version:VERSION, route:"/api/platform-publish",\n            errorClass:"publication_idempotency_lock_exists",\n            error:`Publicação ${platform} bloqueada por exactly-once lock (${publicationLocks.failedType}).`,\n            lockType:publicationLocks.failedType, existingLock:publicationLocks.existing || null,\n            publicationTriggered:false, bufferMutationPerformed:false\n          },409);\n        }\n\n''' + requested_anchor
    route=route.replace(requested_anchor,requested_repl,1)

    success_anchor='''          const saved = await saveLocalDraft(\n            env,\n            draft\n          );\n          await syncPlatformApprovalToVideoResult(\n'''
    if route.count(success_anchor)!=1:
        raise RuntimeError(f'platform publish success anchor count={route.count(success_anchor)}')
    success_repl='''          const saved = await saveLocalDraft(\n            env,\n            draft\n          );\n          await updatePublicationLocks(env, publicationLocks, {\n            state:"confirmed", bufferPostId:publication.bufferPostId || null,\n            bufferStatus:publication.bufferStatus || null, dueAt:publication.dueAt || dueAt || null,\n            externalLink:publication.externalLink || null\n          });\n          await syncPlatformApprovalToVideoResult(\n'''
    route=route.replace(success_anchor,success_repl,1)

    catch_candidates=[
        '        } catch (error) {\n          const failedAt = (/* @__PURE__ */ new Date()).toISOString();',
        '        } catch (error) {\n          const failedAt = new Date().toISOString();'
    ]
    catch_anchor=next((x for x in catch_candidates if route.count(x)==1),None)
    if not catch_anchor:
        raise RuntimeError('platform publish catch anchor mismatch')
    catch_repl=catch_anchor+'''\n          // Fail closed: never release locks after an uncertain Buffer failure.\n          // A timeout can mean the remote post was created but the response was lost.\n          try {\n            await updatePublicationLocks(env, publicationLocks, {\n              state:"uncertain", failureAt:failedAt, error:error?.message || String(error)\n            });\n          } catch (_) {}'''
    route=route.replace(catch_anchor,catch_repl,1)
    t=t[:route_start]+route+t[route_end:]

    health_pat=r'(\n\s*multiPlatformPublishing: true,\n)'
    if len(re.findall(health_pat,t))!=1:
        raise RuntimeError('health multiPlatformPublishing anchor mismatch')
    t=re.sub(health_pat,r'\1            publicationExactlyOnceGuard: true,\n            publicationAssetLockR2: true,\n            publicationSlotLockR2: true,\n            publicationRetryCreateBlockedOnUncertain: true,\n',t,count=1)

    insert_anchor='      if (path.startsWith("/api/platform-publication-eligibility/")'
    if t.count(insert_anchor)!=1:
        raise RuntimeError('publication eligibility route anchor mismatch')
    routes=r'''      // BEGIN_R44_5_22_LOCK_ROUTES
      if (path === "/api/publication-lock-status" && request.method === "GET") {
        if (!isAdminAuthorized(request, env) && !isLolaUGIAuthorized(request, env)) return json({ok:false,error:"Não autorizado"},401);
        const id=String(url.searchParams.get("id") || "").trim();
        const platform=normalizeApprovalPlatform(url.searchParams.get("platform"));
        const mode=normalizePublishMode(url.searchParams.get("mode") || "customScheduled");
        const dueAtRaw=String(url.searchParams.get("dueAt") || "").trim();
        const draft=id ? await getLocalDraft(env,id) : null;
        if (!draft || !platform || !mode) return json({ok:false,error:"id/platform/mode inválidos"},400);
        const dueAt=mode === "customScheduled" && dueAtRaw ? new Date(dueAtRaw).toISOString() : null;
        const assetKey=publicationAssetLockKey(draft,platform);
        const slotKey=publicationSlotLockKey(platform,mode,dueAt);
        return json({ok:true,version:VERSION,assetKey,slotKey,assetLock:await readPublicationLock(env,assetKey),slotLock:await readPublicationLock(env,slotKey),publicationTriggered:false,bufferMutationPerformed:false});
      }

      if (path === "/api/publication-lock-backfill" && request.method === "POST") {
        if (!isAdminAuthorized(request, env) && !isLolaUGIAuthorized(request, env)) return json({ok:false,error:"Não autorizado"},401);
        const body=await readBody(request);
        const id=String(body?.id || "").trim();
        const platform=normalizeApprovalPlatform(body?.platform);
        const draft=id ? await getLocalDraft(env,id) : null;
        const asset=draft?.assets?.[platform];
        const pub=asset?.publication || null;
        if (!draft || !platform || !pub?.bufferPostId) return json({ok:false,error:"existing active Buffer publication required",publicationTriggered:false,bufferMutationPerformed:false},409);
        const mode=normalizePublishMode(pub.mode || "customScheduled") || "customScheduled";
        const dueAt=pub.dueAt || null;
        const group=await acquirePublicationLocks(env,draft,platform,mode,dueAt);
        if (group.acquired) {
          const locks=await updatePublicationLocks(env,group,{state:"backfilled_confirmed",bufferPostId:pub.bufferPostId,bufferStatus:pub.bufferStatus || pub.status || null,dueAt});
          return json({ok:true,created:true,locks,publicationTriggered:false,bufferMutationPerformed:false});
        }
        return json({ok:true,created:false,failedType:group.failedType,existingLock:group.existing || null,publicationTriggered:false,bufferMutationPerformed:false});
      }
      // END_R44_5_22_LOCK_ROUTES

'''
    t=t.replace(insert_anchor,routes+insert_anchor,1)
    return t


def wait_health(ver):
    last={}
    for _ in range(30):
        try:
            r=requests.get(ORIGIN+'/api/health',timeout=12)
            if r.status_code==200:
                last=r.json(); c=last.get('capabilities') or {}; b=last.get('bindings') or {}
                if (last.get('ok') is True and last.get('version')==ver
                    and c.get('publicationExactlyOnceGuard') is True
                    and c.get('publicationAssetLockR2') is True
                    and c.get('publicationSlotLockR2') is True
                    and c.get('publicationRetryCreateBlockedOnUncertain') is True
                    and b.get('MEDIA_R2') is True and b.get('BUFFER_API_KEY') is True):
                    return last
        except Exception:
            pass
        time.sleep(3)
    raise RuntimeError('health timeout '+json.dumps(last,ensure_ascii=False)[:1600])


def main():
    lines=['R44.5.22_STAGE=PUBLICATION_IDEMPOTENCY','OK=false','STATE=STARTED']
    write(lines)
    tok=os.environ['CF_API_TOKEN']; acct=os.environ['CF_ACCOUNT_ID']
    h={'Authorization':f'Bearer {tok}'}
    api=f'https://api.cloudflare.com/client/v4/accounts/{acct}/workers/scripts/{WORKER}'
    live=fetch_live(api,h)
    current_version,b=active_bindings(api,h)
    final=patch(live)
    lines += [f'BASE_SOURCE_BYTES={len(live.encode())}',f'PATCHED_SOURCE_BYTES={len(final.encode())}',f'ACTIVE_BASE_VERSION_ID={current_version}',f'BINDINGS_PRESERVED={len(b)}']
    v=base.create_version(api,h,final,b,'UGI R44.5.22 exactly-once Buffer guard')
    d=base.deploy(api,h,v,'UGI R44.5.22 exactly-once Buffer guard')
    wait_health(NEW)
    lines += ['FINAL_VERSION_ID='+v,'FINAL_DEPLOYMENT_ID='+d,'WORKER_HEALTH_PASS=true','PUBLICATION_EXACTLY_ONCE_GUARD=true','PUBLICATION_ASSET_LOCK_R2=true','PUBLICATION_SLOT_LOCK_R2=true','UNCERTAIN_RETRY_CREATE_BLOCKED=true','BUFFER_PROVIDER_UNCHANGED=true','METRICOOL_PUBLICATION_ALLOWED=false','PAYMENT_TRIGGERED=false','OK=true']
    write(lines)

if __name__=='__main__':
    try:
        main()
    except BaseException as e:
        try: x=STATUS.read_text(encoding='utf-8').splitlines() if STATUS.exists() else []
        except Exception: x=[]
        x += ['ERROR_TYPE='+type(e).__name__,'ERROR='+str(e).replace('\n',' ')[:3000],'OK=false']
        write(x)
        raise
