from __future__ import annotations

import json
import os
import re
import secrets
import time
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

import requests

STATUS = Path('cloudflare/status/r44-5-18-final.txt')
WORKER_NAME = 'lola-operacional-ugi'
WORKER_ORIGIN = 'https://lola-operacional-ugi.umagestaointeligente.workers.dev'
PUBLIC_URL = WORKER_ORIGIN + '/priorizacao'
OLD_VERSION = 'lola-v8-r44-5-17-permanent-commerce-entrypoint-2026-08-21'
NEW_VERSION = 'lola-v8-r44-5-18-permanent-publication-link-policy-2026-08-21'
STABLE_VERSION_ID = '35dc7be4-2d9e-479d-8f27-39e726e0b58f'
POSTS = {
    'instagram': '6a87d61b1b38003a90c37507',
    'tiktok': '6a87d61f1b38003a90c3752d',
    'youtube': '6a87d6231b38003a90c3755b',
}


def write(lines):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def cf_headers(token):
    return {'Authorization': f'Bearer {token}'}


def extract_source(resp):
    ctype = resp.headers.get('content-type', '')
    if 'multipart/' not in ctype.lower():
        return resp.content.decode('utf-8')
    env = (f'Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n'.encode() + resp.content)
    msg = BytesParser(policy=default).parsebytes(env)
    candidates = []
    for part in msg.iter_parts():
        ptype = (part.get_content_type() or '').lower()
        fn = (part.get_filename() or '').lower()
        payload = part.get_payload(decode=True) or b''
        if 'javascript' in ptype or fn.endswith(('.js', '.mjs')):
            candidates.append(payload)
    if not candidates:
        raise RuntimeError('No JS module in Cloudflare response')
    return max(candidates, key=len).decode('utf-8')


def strip_temp_routes(text):
    patterns = [
        r'\n\s*// BEGIN_R44_5_18_ONE_SHOT_REPAIR.*?// END_R44_5_18_ONE_SHOT_REPAIR\s*\n',
        r'\n\s*// BEGIN_R44_5_18_DIAGNOSTIC.*?// END_R44_5_18_DIAGNOSTIC\s*\n',
        r'\n\s*// BEGIN_R44_5_18_REPAIR_V2.*?// END_R44_5_18_REPAIR_V2\s*\n',
    ]
    for pat in patterns:
        text = re.sub(pat, '\n', text, flags=re.S)
    return text


def patch_policy(source):
    text = strip_temp_routes(source)
    if f'var VERSION = "{NEW_VERSION}";' in text:
        if 'permanentCommercePublicationLinkPolicy: true' not in text:
            raise RuntimeError('R44.5.18 live but policy flag missing')
        return text

    old = f'var VERSION = "{OLD_VERSION}";'
    if text.count(old) != 1:
        raise RuntimeError(f'old version anchor count={text.count(old)}')
    text = text.replace(old, f'var VERSION = "{NEW_VERSION}";', 1)

    const_anchor = 'var VIDEO_UPLOAD_MAX_BYTES = 50 * 1024 * 1024;\n'
    if text.count(const_anchor) != 1:
        raise RuntimeError('VIDEO_UPLOAD_MAX_BYTES anchor mismatch')
    text = text.replace(const_anchor, const_anchor + 'var PERMANENT_COMMERCE_PUBLIC_URL = ' + json.dumps(PUBLIC_URL) + ';\n', 1)

    helper_anchor = 'async function createBufferPlatformVideoPost(draft, platform, mode, dueAt, env) {\n'
    if text.count(helper_anchor) != 1:
        raise RuntimeError('Buffer helper anchor mismatch')
    helper = r'''function permanentCommercePublicationText(draft = {}) {
  const original = String(draft?.text || "");
  const commerce = draft?.commerce || {};
  const productId = String(draft?.productId || commerce?.productId || "");
  const materialId = String(draft?.materialId || commerce?.materialId || "");
  const commercial = draft?.commercialOffer === true || commerce?.required === true;
  if (!commercial) return original;
  if (productId !== "UGI-MATERIAL-PRIORIDADES-001" && materialId !== "UGI-KIT-PRIORIZACAO-001") return original;
  let next = original.replace(/https:\/\/(?:www\.)?asaas\.com\/checkoutSession\/show(?:\/[A-Za-z0-9_-]+|\?id=[^\s]+)/gi, PERMANENT_COMMERCE_PUBLIC_URL);
  if (!next.includes(PERMANENT_COMMERCE_PUBLIC_URL)) {
    next = next.trim() + "\n\nKit UGI — Priorização Inteligente: R$ 14,99. Acesse: " + PERMANENT_COMMERCE_PUBLIC_URL;
  }
  return next;
}
__name(permanentCommercePublicationText, "permanentCommercePublicationText");
'''
    text = text.replace(helper_anchor, helper + helper_anchor, 1)

    old_line = '          text: ${JSON.stringify(String(draft.text || ""))}\n'
    new_line = '          text: ${JSON.stringify(permanentCommercePublicationText(draft))}\n'
    if text.count(old_line) != 1:
        raise RuntimeError('createPost text anchor mismatch')
    text = text.replace(old_line, new_line, 1)

    health_anchor = '            permanentCommerceEntrypoint: true,\n'
    if text.count(health_anchor) != 1:
        raise RuntimeError('health anchor mismatch')
    text = text.replace(
        health_anchor,
        health_anchor
        + '            permanentCommercePublicationLinkPolicy: true,\n'
        + '            directAsaasCheckoutInPublicTextBlocked: true,\n'
        + '            permanentCommercePublicUrl: PERMANENT_COMMERCE_PUBLIC_URL,\n',
        1,
    )
    return text


def restored_bindings(stable):
    arr = ((stable.get('result') or {}).get('resources') or {}).get('bindings') or []
    if len(arr) != 19:
        raise RuntimeError(f'expected 19 bindings, got {len(arr)}')
    out = []
    for b in arr:
        out.append({'name': b['name'], 'type': 'inherit', 'version_id': 'latest'} if b.get('type') == 'secret_text' else b)
    return out


def create_version(base, headers, source, bindings, tag):
    meta = {
        'main_module': 'worker.js',
        'compatibility_date': '2026-08-20',
        'annotations': {'workers/message': tag, 'workers/tag': tag.replace(' ', '-')[:64]},
        'bindings': bindings,
    }
    r = requests.post(
        base + '/versions?bindings_inherit=strict',
        headers=headers,
        files={
            'metadata': (None, json.dumps(meta, ensure_ascii=False, separators=(',', ':')), 'application/json'),
            'worker.js': ('worker.js', source.encode('utf-8'), 'application/javascript+module'),
        },
        timeout=60,
    )
    data = r.json()
    if r.status_code != 200 or not data.get('success'):
        raise RuntimeError(f'version create failed HTTP={r.status_code} body={r.text[:1200]}')
    vid = (data.get('result') or {}).get('id')
    if not vid:
        raise RuntimeError('version id missing')
    return vid


def deploy(base, headers, vid, msg):
    payload = {'strategy': 'percentage', 'versions': [{'version_id': vid, 'percentage': 100}], 'annotations': {'workers/message': msg}}
    r = requests.post(base + '/deployments', headers={**headers, 'Content-Type': 'application/json'}, json=payload, timeout=30)
    data = r.json()
    if r.status_code != 200 or not data.get('success'):
        raise RuntimeError(f'deploy failed HTTP={r.status_code} body={r.text[:1200]}')
    return str((data.get('result') or {}).get('id') or '')


def wait_health():
    last = {}
    for _ in range(15):
        try:
            r = requests.get(WORKER_ORIGIN + '/api/health', timeout=12)
            if r.status_code == 200:
                last = r.json()
                c = last.get('capabilities') or {}
                b = last.get('bindings') or {}
                if (last.get('ok') is True and last.get('version') == NEW_VERSION
                    and c.get('permanentCommercePublicationLinkPolicy') is True
                    and c.get('directAsaasCheckoutInPublicTextBlocked') is True
                    and b.get('MEDIA_R2') is True and b.get('BUFFER_API_KEY') is True and b.get('ASAAS_API_KEY') is True):
                    return last
        except Exception:
            pass
        time.sleep(3)
    raise RuntimeError('health timeout ' + json.dumps(last, ensure_ascii=False)[:1000])


def add_diag_route(source, path, token):
    anchor = '      if (path === "/approve") {'
    if source.count(anchor) != 1:
        raise RuntimeError('route anchor mismatch')
    ids = json.dumps(POSTS)
    route = r'''      // BEGIN_R44_5_18_DIAGNOSTIC
      if (request.method === "GET" && path === __PATH__ && url.searchParams.get("token") === __TOKEN__) {
        const ids = __IDS__;
        const results = {};
        for (const [platform,id] of Object.entries(ids)) {
          const baseQuery = `query { post(input:{id:${JSON.stringify(id)}}) { id text status dueAt sentAt externalLink assets { id type mimeType source ... on VideoAsset { video { thumbnailOffset title } } } metadata { type } } }`;
          const base = await bufferGraphQL(baseQuery, env);
          let detailQuery = null;
          if (platform === "instagram") detailQuery = `query { post(input:{id:${JSON.stringify(id)}}) { metadata { ... on InstagramPostMetadata { type shouldShareToFeed isAiGenerated } } } }`;
          if (platform === "tiktok") detailQuery = `query { post(input:{id:${JSON.stringify(id)}}) { metadata { ... on TiktokPostMetadata { type isAiGenerated title } } } }`;
          if (platform === "youtube") detailQuery = `query { post(input:{id:${JSON.stringify(id)}}) { metadata { ... on YoutubePostMetadata { type title category { categoryId title } privacy license madeForKids notifySubscribers embeddable isAiGenerated } } } }`;
          const detail = detailQuery ? await bufferGraphQL(detailQuery, env) : null;
          results[platform] = { base, detail };
        }
        return json({ok:true,version:VERSION,results});
      }
      // END_R44_5_18_DIAGNOSTIC

'''
    route = route.replace('__PATH__', json.dumps(path)).replace('__TOKEN__', json.dumps(token)).replace('__IDS__', ids)
    return source.replace(anchor, route + anchor, 1)


def parse_diag(diag):
    out = {}
    for platform, wrapper in (diag.get('results') or {}).items():
        base = (((wrapper.get('base') or {}).get('data') or {}).get('post') or {})
        detail = (((wrapper.get('detail') or {}).get('data') or {}).get('post') or {})
        errs = ((wrapper.get('base') or {}).get('errors') or []) + ((wrapper.get('detail') or {}).get('errors') or [])
        if errs:
            raise RuntimeError(f'{platform} GraphQL diagnostic errors: {json.dumps(errs)[:1200]}')
        if not base.get('id'):
            raise RuntimeError(f'{platform} post not returned')
        if base.get('sentAt') or str(base.get('status') or '').lower() == 'sent':
            raise RuntimeError(f'{platform} already sent; refusing mutation')
        videos = [a for a in (base.get('assets') or []) if str(a.get('type') or '').lower() == 'video']
        if len(videos) != 1 or not videos[0].get('source'):
            raise RuntimeError(f'{platform} expected exactly one video asset')
        out[platform] = {
            'id': base['id'],
            'text': str(base.get('text') or ''),
            'status': base.get('status'),
            'dueAt': base.get('dueAt'),
            'video': videos[0],
            'metadata': detail.get('metadata') or base.get('metadata') or {},
        }
    if set(out) != {'instagram','tiktok','youtube'}:
        raise RuntimeError('diagnostic platform set incomplete')
    return out


def gql_input_value(v):
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int,float)):
        return str(v)
    return json.dumps(str(v), ensure_ascii=False)


def build_platform_metadata(platform, meta):
    if platform == 'instagram':
        ptype = str(meta.get('type') or 'reel')
        share = bool(meta.get('shouldShareToFeed', True))
        ai = bool(meta.get('isAiGenerated', False))
        return f'metadata:{{instagram:{{type:{ptype},shouldShareToFeed:{str(share).lower()},isAiGenerated:{str(ai).lower()}}}}}'
    if platform == 'tiktok':
        ai = bool(meta.get('isAiGenerated', False))
        return f'metadata:{{tiktok:{{isAiGenerated:{str(ai).lower()}}}}}'
    if platform == 'youtube':
        title = meta.get('title')
        cat = (meta.get('category') or {}).get('categoryId')
        if not title or not cat:
            raise RuntimeError('youtube title/category missing from diagnostic')
        return 'metadata:{youtube:{title:' + gql_input_value(title) + ',categoryId:' + gql_input_value(cat) + '}}'
    raise RuntimeError('unknown platform')


def add_repair_route(source, path, token, details):
    anchor = '      if (path === "/approve") {'
    if source.count(anchor) != 1:
        raise RuntimeError('repair anchor mismatch')

    plan = {}
    for platform, d in details.items():
        video = d['video']
        vm = video.get('video') or {}
        video_input = 'assets:[{video:{url:' + gql_input_value(video['source'])
        video_input += ',metadata:{thumbnailOffset:' + str(int(vm.get('thumbnailOffset') or 0))
        if vm.get('title'):
            video_input += ',title:' + gql_input_value(vm.get('title'))
        video_input += '}}}]'
        plan[platform] = {
            'id': d['id'],
            'beforeDueAt': d['dueAt'],
            'videoInput': video_input,
            'metadataInput': build_platform_metadata(platform, d['metadata']),
        }

    route = r'''      // BEGIN_R44_5_18_REPAIR_V2
      if (request.method === "POST" && path === __PATH__ && url.searchParams.get("token") === __TOKEN__) {
        const plan = __PLAN__;
        const results = [];
        for (const [platform,p] of Object.entries(plan)) {
          const before = await getBufferPostStatus(p.id, env);
          const bp = before.post || {};
          if (bp.sentAt || String(bp.status || "").toLowerCase() === "sent") {
            results.push({platform,id:p.id,ok:false,error:"already_sent"});
            continue;
          }
          const beforeDueAt = bp.dueAt || null;
          let repaired = String(bp.text || "").replace(/https:\/\/(?:www\.)?asaas\.com\/checkoutSession\/show(?:\/[A-Za-z0-9_-]+|\?id=[^\s]+)/gi, PERMANENT_COMMERCE_PUBLIC_URL);
          if (!repaired.includes(PERMANENT_COMMERCE_PUBLIC_URL)) repaired = repaired.trim() + "\n\nKit UGI — Priorização Inteligente: R$ 14,99. Acesse: " + PERMANENT_COMMERCE_PUBLIC_URL;
          const query = "mutation { editPost(input:{id:" + JSON.stringify(p.id) + ",text:" + JSON.stringify(repaired) + ",aiAssisted:true," + p.videoInput + "," + p.metadataInput + "}) { __typename ... on PostActionSuccess { post { id text status dueAt sentAt externalLink } } ... on MutationError { message } } }";
          const edited = await bufferGraphQL(query, env);
          const payload = edited?.data?.editPost;
          if (!payload?.post?.id) {
            results.push({platform,id:p.id,ok:false,error:payload?.message || "edit_failed",diagnostics:edited?.__bufferDiagnostics || null,raw:edited});
            continue;
          }
          const after = await getBufferPostStatus(p.id, env);
          const ap = after.post || {};
          const txt = String(ap.text || "");
          const ok = txt.includes(PERMANENT_COMMERCE_PUBLIC_URL) && !/asaas\.com\/checkoutSession\/show/i.test(txt) && (ap.dueAt || null) === beforeDueAt && !ap.sentAt;
          results.push({platform,id:p.id,ok,status:ap.status || null,dueAt:ap.dueAt || null,sentAt:ap.sentAt || null,schedulePreserved:(ap.dueAt || null) === beforeDueAt,permanentUrlPresent:txt.includes(PERMANENT_COMMERCE_PUBLIC_URL),temporaryCheckoutAbsent:!/asaas\.com\/checkoutSession\/show/i.test(txt)});
        }
        return json({ok:results.length===3 && results.every(x=>x.ok),version:VERSION,publicUrl:PERMANENT_COMMERCE_PUBLIC_URL,results,mutationPerformed:true,bufferMutation:true});
      }
      // END_R44_5_18_REPAIR_V2

'''
    route = route.replace('__PATH__', json.dumps(path)).replace('__TOKEN__', json.dumps(token)).replace('__PLAN__', json.dumps(plan, ensure_ascii=False))
    return source.replace(anchor, route + anchor, 1)


def main():
    lines = ['R44.5.18_STAGE=ASSET_PRESERVING_SLOT02_REPAIR_V2']
    write(lines + ['OK=false','STATE=STARTED'])
    token = os.environ.get('CF_API_TOKEN','')
    account = os.environ.get('CF_ACCOUNT_ID','')
    if not token or not account:
        raise SystemExit('missing Cloudflare env')
    headers = cf_headers(token)
    base = f'https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{WORKER_NAME}'

    live = requests.get(base + '/content/v2', headers=headers, timeout=30)
    live.raise_for_status()
    source = extract_source(live)
    stable = requests.get(base + f'/versions/{STABLE_VERSION_ID}', headers=headers, timeout=30).json()
    bindings = restored_bindings(stable)
    final_source = patch_policy(source)
    final_source = strip_temp_routes(final_source)
    lines += [f'BASE_SOURCE_BYTES={len(source.encode("utf-8"))}','BINDINGS_PRESERVED=19','FINAL_SOURCE_TEMP_ROUTES_STRIPPED=true']

    cleanup_needed = False
    try:
        # Read-only Buffer diagnostic
        dpath = '/__ugi_diag_slot02_' + secrets.token_hex(12)
        dtoken = secrets.token_urlsafe(32)
        diag_source = add_diag_route(final_source, dpath, dtoken)
        dvid = create_version(base, headers, diag_source, bindings, 'r44-5-18-slot02-diagnostic')
        deploy(base, headers, dvid, 'UGI R44.5.18 Slot02 read-only diagnostic')
        cleanup_needed = True
        wait_health()
        dr = requests.get(WORKER_ORIGIN + dpath, params={'token': dtoken}, timeout=40)
        if dr.status_code != 200:
            raise RuntimeError(f'diagnostic HTTP {dr.status_code}: {dr.text[:1200]}')
        diag = dr.json()
        details = parse_diag(diag)
        lines.append('BUFFER_DIAGNOSTIC_PASS=true')
        for p,d in details.items():
            lines.append(f'DIAG_{p.upper()}_STATUS={d.get("status")} DUE_AT={d.get("dueAt")} VIDEO_SOURCE_PRESENT=true')

        # Asset-preserving edit in place
        rpath = '/__ugi_repair_slot02_v2_' + secrets.token_hex(12)
        rtoken = secrets.token_urlsafe(32)
        repair_source = add_repair_route(final_source, rpath, rtoken, details)
        rvid = create_version(base, headers, repair_source, bindings, 'r44-5-18-slot02-asset-preserving-repair')
        deploy(base, headers, rvid, 'UGI R44.5.18 Slot02 asset-preserving repair')
        wait_health()
        rr = requests.post(WORKER_ORIGIN + rpath, params={'token': rtoken}, timeout=60)
        if rr.status_code != 200:
            raise RuntimeError(f'repair HTTP {rr.status_code}: {rr.text[:1600]}')
        repair = rr.json()
        if not repair.get('ok'):
            raise RuntimeError('repair failed ' + json.dumps(repair, ensure_ascii=False)[:2200])
        rows = repair.get('results') or []
        if len(rows) != 3:
            raise RuntimeError('repair result count != 3')
        for row in rows:
            if not (row.get('ok') and row.get('schedulePreserved') and row.get('permanentUrlPresent') and row.get('temporaryCheckoutAbsent') and not row.get('sentAt')):
                raise RuntimeError('repair invariant failed ' + json.dumps(row, ensure_ascii=False))
        lines.append('SLOT02_REPAIR_PASS=true')
        for row in rows:
            lines.append('BUFFER_POST=' + str(row.get('id')) + ' PLATFORM=' + str(row.get('platform')) + ' STATUS=' + str(row.get('status')) + ' DUE_AT=' + str(row.get('dueAt')) + ' SCHEDULE_PRESERVED=true PERMANENT_URL_PRESENT=true TEMPORARY_CHECKOUT_ABSENT=true')

    finally:
        # Always restore clean final source without temporary endpoints.
        try:
            fvid = create_version(base, headers, final_source, bindings, 'r44-5-18-permanent-link-clean-final')
            fdep = deploy(base, headers, fvid, 'UGI R44.5.18 permanent publication link clean final')
            wait_health()
            page = requests.get(PUBLIC_URL, timeout=20)
            if page.status_code != 200 or 'Comprar agora' not in page.text:
                raise RuntimeError('permalink final validation failed')
            lines += [f'FINAL_VERSION_ID={fvid}',f'FINAL_DEPLOYMENT_ID={fdep}','TEMP_ENDPOINTS_REMOVED=true','PERMALINK_HTTP=200','PERMANENT_PUBLICATION_LINK_POLICY=true','DIRECT_ASAAS_CHECKOUT_IN_PUBLIC_TEXT_BLOCKED=true']
        except Exception as cleanup_exc:
            lines += ['CLEANUP_FAILED=true','CLEANUP_ERROR=' + str(cleanup_exc).replace('\n',' ')[:1200]]
            write(lines + ['OK=false'])
            raise

    lines += ['PUBLIC_COMMERCE_URL=' + PUBLIC_URL,'OK=true']
    write(lines)


if __name__ == '__main__':
    main()
