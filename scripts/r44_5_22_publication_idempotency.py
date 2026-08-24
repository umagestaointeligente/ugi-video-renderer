from __future__ import annotations
import json, os, re, time
from pathlib import Path
import requests
import scripts.r44_5_18_repair_v2 as base

STATUS=Path('cloudflare/status/r44-5-22-publication-idempotency.txt')
WORKER='lola-operacional-ugi'
ORIGIN='https://lola-operacional-ugi.umagestaointeligente.workers.dev'
NEW='lola-v8-r44-5-22-publication-idempotency-2026-08-23'


def write(lines):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text('\n'.join(lines)+'\n', encoding='utf-8')


def fetch_live(api,h):
    r=requests.get(api+'/content/v2',headers=h,timeout=45)
    r.raise_for_status()
    return base.extract_source(r)


def bindings(api,h):
    r=requests.get(api+f'/versions/{base.STABLE_VERSION_ID}',headers=h,timeout=30)
    r.raise_for_status()
    return base.restored_bindings(r.json())


def patch(src):
    t=base.strip_temp_routes(src)
    # idempotent cleanup of any prior R44.5.22 block
    t=re.sub(r'\n\s*// BEGIN_R44_5_22_PUBLICATION_IDEMPOTENCY.*?// END_R44_5_22_PUBLICATION_IDEMPOTENCY\s*\n','\n',t,flags=re.S)
    t=re.sub(r'\n\s*// BEGIN_R44_5_22_LOCK_ROUTES.*?// END_R44_5_22_LOCK_ROUTES\s*\n','\n',t,flags=re.S)

    # version is operational metadata only; preserve architecture and live source.
    t,n=re.subn(r'var VERSION = "[^"]+";', f'var VERSION = "{NEW}";', t, count=1)
    if n != 1:
        raise RuntimeError('VERSION anchor mismatch')

    const_anchor='var DELIVERY_PREFIX = "lola/commerce/deliveries/";\n'
    if t.count(const_anchor)!=1:
        raise RuntimeError('DELIVERY_PREFIX anchor mismatch')
    t=t.replace(const_anchor,const_anchor+'var PUBLICATION_LOCK_PREFIX = "lola/publication-locks/";\n',1)

    helper_anchor='async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {\n'
    if t.count(helper_anchor)!=1:
        raise RuntimeError('createBufferPlatformVideoPost anchor mismatch')
    helper=r'''// BEGIN_R44_5_22_PUBLICATION_IDEMPOTENCY
function publicationLockKey(draft, platform, mode, dueAt) {
  const p = String(platform || "unknown").toLowerCase();
  const m = String(mode || "unknown");
  const scheduled = m === "customScheduled" && dueAt
    ? String(new Date(dueAt).toISOString())
    : String(draft?.renderId || draft?.contentId || draft?.id || "unknown");
  return PUBLICATION_LOCK_PREFIX + encodeURIComponent(p) + "/" + encodeURIComponent(m) + "/" + encodeURIComponent(scheduled) + ".json";
}
__name(publicationLockKey, "publicationLockKey");

async function readPublicationLock(env, key) {
  if (!env.MEDIA) return null;
  const obj = await env.MEDIA.get(key);
  if (!obj) return null;
  try { return await obj.json(); } catch { return { key, state: "unreadable" }; }
}
__name(readPublicationLock, "readPublicationLock");

async function acquirePublicationLock(env, draft, platform, mode, dueAt) {
  if (!env.MEDIA) throw new Error("R2 MEDIA não conectado para publication lock");
  const key = publicationLockKey(draft, platform, mode, dueAt);
  const token = crypto.randomUUID();
  const value = {
    schemaVersion: "1.0",
    key,
    token,
    state: "creating",
    project: "UGI",
    draftId: draft?.id || null,
    renderId: draft?.renderId || null,
    contentId: draft?.contentId || null,
    platform,
    mode,
    dueAt: dueAt || null,
    requestedAt: new Date().toISOString(),
    bufferPostId: null
  };
  const created = await env.MEDIA.put(key, JSON.stringify(value, null, 2), {
    onlyIf: { etagDoesNotMatch: "*" },
    httpMetadata: { contentType: "application/json" }
  });
  if (!created) return { acquired: false, key, existing: await readPublicationLock(env, key) };
  return { acquired: true, key, token, value };
}
__name(acquirePublicationLock, "acquirePublicationLock");

async function updatePublicationLock(env, lock, patch) {
  if (!env.MEDIA || !lock?.key) return null;
  const current = (await readPublicationLock(env, lock.key)) || {};
  if (lock.token && current.token && current.token !== lock.token) {
    throw new Error("publication_lock_owner_mismatch");
  }
  const next = { ...current, ...patch, updatedAt: new Date().toISOString() };
  await env.MEDIA.put(lock.key, JSON.stringify(next, null, 2), {
    httpMetadata: { contentType: "application/json" }
  });
  return next;
}
__name(updatePublicationLock, "updatePublicationLock");
// END_R44_5_22_PUBLICATION_IDEMPOTENCY

'''
    t=t.replace(helper_anchor,helper+helper_anchor,1)

    route_anchor='''        const requestedAt =\n          new Date().toISOString();\n        try {\n'''
    if t.count(route_anchor)!=1:
        raise RuntimeError('platform publish requestedAt anchor mismatch')
    route_repl='''        // R44.5.22 — atomic-ish R2 slot lock BEFORE any Buffer mutation.\n        // For customScheduled the key is platform+exact dueAt, so even two different\n        // drafts cannot create two posts for the same UGI platform slot.\n        const publicationLock = await acquirePublicationLock(\n          env, draft, platform, mode, dueAt\n        );\n        if (!publicationLock.acquired) {\n          return json({\n            ok: false,\n            version: VERSION,\n            route: "/api/platform-publish",\n            errorClass: "publication_idempotency_lock_exists",\n            error: `Slot ${platform} já possui publication lock; criação Buffer bloqueada.`,\n            publicationLockKey: publicationLock.key,\n            existingLock: publicationLock.existing || null,\n            publicationTriggered: false,\n            bufferMutationPerformed: false\n          }, 409);\n        }\n\n        const requestedAt =\n          new Date().toISOString();\n        try {\n'''
    t=t.replace(route_anchor,route_repl,1)

    success_anchor='''          const saved =\n            await saveLocalDraft(\n              env,\n              draft\n            );\n\n          await syncPlatformApprovalToVideoResult(\n'''
    if t.count(success_anchor)!=1:
        raise RuntimeError('platform publish save success anchor mismatch')
    success_repl='''          const saved =\n            await saveLocalDraft(\n              env,\n              draft\n            );\n\n          await updatePublicationLock(env, publicationLock, {\n            state: "confirmed",\n            bufferPostId: publication.bufferPostId || null,\n            bufferStatus: publication.bufferStatus || null,\n            dueAt: publication.dueAt || dueAt || null,\n            externalLink: publication.externalLink || null\n          });\n\n          await syncPlatformApprovalToVideoResult(\n'''
    t=t.replace(success_anchor,success_repl,1)

    catch_anchor='''        } catch (error) {\n          const failedAt =\n            new Date().toISOString();\n'''
    if t.count(catch_anchor)!=1:
        raise RuntimeError('platform publish catch anchor mismatch')
    catch_repl='''        } catch (error) {\n          const failedAt =\n            new Date().toISOString();\n          // Never release an uncertain lock automatically. A timeout may have\n          // created a Buffer post even when the response was lost. Keeping the\n          // lock forces readback/reconciliation instead of duplicate creation.\n          try {\n            await updatePublicationLock(env, publicationLock, {\n              state: "uncertain",\n              failureAt: failedAt,\n              error: error?.message || String(error)\n            });\n          } catch (_) {}\n'''
    t=t.replace(catch_anchor,catch_repl,1)

    health_anchor='            multiPlatformPublishing: true,\n'
    if t.count(health_anchor)!=1:
        raise RuntimeError('health multiPlatformPublishing anchor mismatch')
    t=t.replace(health_anchor,health_anchor+'            publicationExactlyOnceGuard: true,\n            publicationSlotLockR2: true,\n            publicationRetryCreateBlockedOnUncertain: true,\n',1)

    routes_anchor='''      // ========================================================\n      // R44.4 — PLATFORM PUBLICATION STATUS\n      // ========================================================\n'''
    if t.count(routes_anchor)!=1:
        raise RuntimeError('publication status route anchor mismatch')
    routes=r'''      // BEGIN_R44_5_22_LOCK_ROUTES
      if (path === "/api/publication-lock-status" && request.method === "GET") {
        if (!isAdminAuthorized(request, env) && !isLolaUGIAuthorized(request, env)) {
          return json({ ok:false, error:"Não autorizado" }, 401);
        }
        const id = String(url.searchParams.get("id") || "").trim();
        const platform = normalizeApprovalPlatform(url.searchParams.get("platform"));
        const mode = normalizePublishMode(url.searchParams.get("mode") || "customScheduled");
        const dueAtRaw = String(url.searchParams.get("dueAt") || "").trim();
        const draft = id ? await getLocalDraft(env, id) : null;
        if (!draft || !platform || !mode) return json({ok:false,error:"id/platform/mode inválidos"},400);
        const dueAt = mode === "customScheduled" && dueAtRaw ? new Date(dueAtRaw).toISOString() : null;
        const key = publicationLockKey(draft, platform, mode, dueAt);
        return json({ok:true,version:VERSION,key,lock:await readPublicationLock(env,key),publicationTriggered:false,bufferMutationPerformed:false});
      }

      if (path === "/api/publication-lock-backfill" && request.method === "POST") {
        if (!isAdminAuthorized(request, env) && !isLolaUGIAuthorized(request, env)) {
          return json({ ok:false, error:"Não autorizado" }, 401);
        }
        const body = await readBody(request);
        const id = String(body?.id || "").trim();
        const platform = normalizeApprovalPlatform(body?.platform);
        const draft = id ? await getLocalDraft(env,id) : null;
        const asset = draft?.assets?.[platform];
        const pub = asset?.publication || null;
        if (!draft || !platform || !pub?.bufferPostId) {
          return json({ok:false,error:"existing active Buffer publication required",publicationTriggered:false,bufferMutationPerformed:false},409);
        }
        const mode = normalizePublishMode(pub.mode || "customScheduled") || "customScheduled";
        const dueAt = pub.dueAt || null;
        const lock = await acquirePublicationLock(env,draft,platform,mode,dueAt);
        if (lock.acquired) {
          const finalLock = await updatePublicationLock(env,lock,{state:"backfilled_confirmed",bufferPostId:pub.bufferPostId,bufferStatus:pub.bufferStatus||pub.status||null,dueAt});
          return json({ok:true,created:true,key:lock.key,lock:finalLock,publicationTriggered:false,bufferMutationPerformed:false});
        }
        return json({ok:true,created:false,key:lock.key,lock:lock.existing||null,publicationTriggered:false,bufferMutationPerformed:false});
      }
      // END_R44_5_22_LOCK_ROUTES

'''
    t=t.replace(routes_anchor,routes+routes_anchor,1)

    # Allow Lola operational auth on the two new non-public routes.
    auth_anchor='''        "/api/platform-publication-status",\n        "/api/carousel-slide-recovery"\n'''
    auth_repl='''        "/api/platform-publication-status",\n        "/api/carousel-slide-recovery",\n        "/api/publication-lock-status",\n        "/api/publication-lock-backfill"\n'''
    if t.count(auth_anchor)!=1:
        raise RuntimeError('LOLA_OPERATIONAL_ROUTES anchor mismatch')
    t=t.replace(auth_anchor,auth_repl,1)
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
                    and c.get('publicationSlotLockR2') is True
                    and b.get('MEDIA_R2') is True and b.get('BUFFER_API_KEY') is True):
                    return last
        except Exception: pass
        time.sleep(3)
    raise RuntimeError('health timeout '+json.dumps(last,ensure_ascii=False)[:1400])


def main():
    lines=['R44.5.22_STAGE=PUBLICATION_IDEMPOTENCY','OK=false','STATE=STARTED']
    write(lines)
    tok=os.environ['CF_API_TOKEN']; acct=os.environ['CF_ACCOUNT_ID']
    h={'Authorization':f'Bearer {tok}'}
    api=f'https://api.cloudflare.com/client/v4/accounts/{acct}/workers/scripts/{WORKER}'
    live=fetch_live(api,h)
    final=patch(live)
    b=bindings(api,h)
    lines += [f'BASE_SOURCE_BYTES={len(live.encode())}',f'PATCHED_SOURCE_BYTES={len(final.encode())}',f'BINDINGS_PRESERVED={len(b)}']
    v=base.create_version(api,h,final,b,'UGI R44.5.22 exactly-once Buffer guard')
    d=base.deploy(api,h,v,'UGI R44.5.22 exactly-once Buffer guard')
    wait_health(NEW)
    lines += ['FINAL_VERSION_ID='+v,'FINAL_DEPLOYMENT_ID='+d,'WORKER_HEALTH_PASS=true','PUBLICATION_EXACTLY_ONCE_GUARD=true','PUBLICATION_SLOT_LOCK_R2=true','UNCERTAIN_RETRY_CREATE_BLOCKED=true','BUFFER_PROVIDER_UNCHANGED=true','METRICOOL_PUBLICATION_ALLOWED=false','PAYMENT_TRIGGERED=false','OK=true']
    write(lines)

if __name__=='__main__':
    try: main()
    except BaseException as e:
        try: x=STATUS.read_text(encoding='utf-8').splitlines() if STATUS.exists() else []
        except Exception: x=[]
        x += ['ERROR_TYPE='+type(e).__name__,'ERROR='+str(e).replace('\n',' ')[:3000],'OK=false']
        write(x)
        raise
