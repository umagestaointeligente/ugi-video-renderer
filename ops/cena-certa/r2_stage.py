#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request


def _auth_headers(key: str) -> dict[str, str]:
    return {
        'x-ugi-video-upload-key': key,
        'User-Agent': 'CenaCertaFactoryV2/2',
    }


def _json_request(req: urllib.request.Request, timeout: float) -> dict:
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        if not 200 <= int(r.status) < 300:
            raise RuntimeError(f'HTTP_STATUS_FAIL {r.status}')
    return json.loads(body.decode('utf-8'))


def _walk_media(obj):
    if isinstance(obj, dict):
        if obj.get('videoUrl') and obj.get('videoKey'):
            return str(obj['videoUrl']), str(obj['videoKey'])
        for v in obj.values():
            found = _walk_media(v)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _walk_media(v)
            if found:
                return found
    return None


def _poll_url(obj):
    if isinstance(obj, dict):
        for k in ('statusUrl', 'status_url', 'pollUrl', 'poll_url'):
            if obj.get(k):
                return str(obj[k])
        for v in obj.values():
            x = _poll_url(v)
            if x:
                return x
    elif isinstance(obj, list):
        for v in obj:
            x = _poll_url(v)
            if x:
                return x
    return None


def _public_url(base: str, storage_rid: str) -> tuple[str, str]:
    # Live Worker canonical storage contract. Keep this deterministic so a lost
    # POST response can be reconciled with a public HEAD instead of re-sending.
    key = f'geradas/videos/{storage_rid}/instagram.mp4'
    return f"{base.rstrip('/')}/media/{urllib.parse.quote(key, safe='')}", key


def _head_exact(url: str, expected_size: int, attempts: int = 8) -> bool:
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'CenaCertaFactoryV2/2'})
            with urllib.request.urlopen(req, timeout=15) as r:
                size = int(r.headers.get('Content-Length') or 0)
                ctype = (r.headers.get('Content-Type') or '').lower()
                if 200 <= int(r.status) < 300 and size == expected_size and ('video/mp4' in ctype or ctype == 'application/octet-stream'):
                    return True
        except Exception:
            pass
        if attempt + 1 < attempts:
            time.sleep(2)
    return False


def _http_error_detail(error: urllib.error.HTTPError) -> str:
    try:
        body = error.read().decode('utf-8', 'replace').strip()
    except Exception:
        body = ''
    if len(body) > 240:
        body = body[:240]
    return body


def stage(base: str, key: str, rid: str, batch_sha: str, mp4: pathlib.Path, duration: float, out: pathlib.Path) -> dict:
    if len(batch_sha) != 64 or any(c not in '0123456789abcdef' for c in batch_sha.lower()):
        raise RuntimeError('BATCH_SHA256_INVALID')
    if not mp4.is_file() or mp4.stat().st_size <= 1024:
        raise RuntimeError('R2_LOCAL_MEDIA_INVALID')
    storage_rid = f'{rid}-{batch_sha[:12]}'
    deterministic_url, deterministic_key = _public_url(base, storage_rid)
    size = mp4.stat().st_size
    upload_url = f"{base.rstrip('/')}/api/video-upload?renderId={urllib.parse.quote(storage_rid)}&duration={duration:.3f}"
    data = mp4.read_bytes()
    headers = _auth_headers(key)
    headers.update({
        'Content-Type': 'video/mp4',
        'Content-Length': str(size),
    })
    req = urllib.request.Request(upload_url, data=data, method='POST', headers=headers)

    response = None
    post_state = 'NOT_SENT'
    try:
        response = _json_request(req, timeout=120)
        post_state = 'RESPONSE_RECEIVED'
    except urllib.error.HTTPError as e:
        detail = _http_error_detail(e)
        raise RuntimeError(f'R2_POST_EXPLICIT_HTTP_FAIL status={e.code} detail={detail!r}') from e
    except Exception as e:
        # Transport failure may have happened after provider accepted all bytes.
        # Reconcile by deterministic public object before deciding anything else.
        post_state = f'RESPONSE_LOST:{type(e).__name__}'
        if not _head_exact(deterministic_url, size):
            raise RuntimeError(f'R2_POST_AMBIGUOUS_NOT_RECONCILED {post_state}') from e

    media = _walk_media(response) if response is not None else None
    poll = _poll_url(response) if response is not None else None
    if not media and poll:
        for _ in range(12):
            time.sleep(2)
            try:
                preq = urllib.request.Request(poll, headers=_auth_headers(key))
                p = _json_request(preq, timeout=10)
                media = _walk_media(p)
                if media:
                    break
            except Exception:
                continue

    video_url, video_key = media if media else (deterministic_url, deterministic_key)
    if video_key != deterministic_key:
        raise RuntimeError(f'R2_VIDEO_KEY_MISMATCH got={video_key} want={deterministic_key}')
    if not _head_exact(video_url, size):
        raise RuntimeError('R2_PUBLIC_HEAD_SIZE_RECONCILIATION_FAIL')

    receipt = {
        'schema': 'CENA_CERTA_R2_RECEIPT_V2',
        'id': rid,
        'storageRenderId': storage_rid,
        'batchSha256': batch_sha,
        'status': 'ready',
        'public_probe_pass': True,
        'public_head_size_match': True,
        'localSizeBytes': size,
        'videoUrl': video_url,
        'videoKey': video_key,
        'postState': post_state,
        'authMode': 'x-ugi-video-upload-key',
        'storageContract': 'geradas/videos/{storageRenderId}/instagram.mp4',
        'blind_retry_used': False,
        'contentSha256': hashlib.sha256(data).hexdigest(),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + '.tmp')
    tmp.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, out)
    print('R2_STAGE_RECONCILED_PASS', rid, storage_rid, post_state, size)
    return receipt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--auth-key', required=True)
    ap.add_argument('--id', required=True)
    ap.add_argument('--batch-sha256', required=True)
    ap.add_argument('--mp4', required=True)
    ap.add_argument('--duration', required=True, type=float)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    stage(a.base_url, a.auth_key, a.id, a.batch_sha256.lower(), pathlib.Path(a.mp4), a.duration, pathlib.Path(a.out))


if __name__ == '__main__':
    main()
