import json
import time
import traceback
import scripts.r44_5_18_repair_v2_runner3 as r3

job = r3.job
_orig_get = job.requests.get
_orig_post = job.requests.post


def _diag(source, path, token):
    anchor = '      if (request.method === "GET" && path === "/priorizacao") {'
    if source.count(anchor) != 1:
        raise RuntimeError('active commerce anchor mismatch')
    ids = json.dumps(job.POSTS)
    route = r'''      // BEGIN_R44_5_18_DIAGNOSTIC
      if (request.method === "GET" && path === __PATH__ && url.searchParams.get("token") === __TOKEN__) {
        const ids = __IDS__;
        const results = {};
        for (const [platform,id] of Object.entries(ids)) {
          const baseQuery = `query { post(input:{id:${JSON.stringify(id)}}) { id text status dueAt sentAt externalLink assets { id type mimeType source ... on VideoAsset { video { thumbnailOffset title } } } } }`;
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


def _get(url, *args, **kwargs):
    if '/__ugi_diag_slot02_' not in str(url):
        return _orig_get(url, *args, **kwargs)
    last = None
    for _ in range(20):
        last = _orig_get(url, *args, **kwargs)
        try:
            data = last.json()
            if isinstance(data, dict) and isinstance(data.get('results'), dict):
                return last
            if last.status_code >= 500 and 'Cannot query field' in last.text:
                return last
        except Exception:
            pass
        time.sleep(3)
    return last


def _post(url, *args, **kwargs):
    if '/__ugi_repair_slot02_v2_' not in str(url):
        return _orig_post(url, *args, **kwargs)
    last = None
    for _ in range(20):
        last = _orig_post(url, *args, **kwargs)
        try:
            data = last.json()
            if isinstance(data, dict) and isinstance(data.get('results'), list):
                return last
        except Exception:
            pass
        time.sleep(3)
    return last

job.add_diag_route = _diag
job.requests.get = _get
job.requests.post = _post

if __name__ == '__main__':
    try:
        job.main()
    except BaseException as exc:
        try:
            existing = job.STATUS.read_text(encoding='utf-8').splitlines() if job.STATUS.exists() else []
        except Exception:
            existing = []
        existing += [
            'WRAPPER6_FAILURE=true',
            'ERROR_TYPE=' + type(exc).__name__,
            'ERROR=' + str(exc).replace('\n',' ')[:5000],
            'TRACE=' + traceback.format_exc().replace('\n',' | ')[:9000],
            'OK=false',
        ]
        job.write(existing)
        raise
