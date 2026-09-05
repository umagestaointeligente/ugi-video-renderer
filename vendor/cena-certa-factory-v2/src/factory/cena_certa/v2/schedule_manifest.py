#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re
from datetime import timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from .common import contract, safe_id, sha256
from .fingerprint import dispatch_fingerprint, schedule_fingerprint
from .preflight import validate_batch, schedule_instant

SHA256_RE=re.compile(r'^[0-9a-f]{64}$')


def _find_media(obj):
    if isinstance(obj,dict):
        if obj.get('videoUrl') and obj.get('videoKey'):
            return {'videoUrl':obj['videoUrl'],'videoKey':obj['videoKey']}
        for v in obj.values():
            found=_find_media(v)
            if found:
                return found
    elif isinstance(obj,list):
        for v in obj:
            found=_find_media(v)
            if found:
                return found
    return None


def build_expected_placements(rid,idempotency_key,networks):
    rid=safe_id(rid)
    rows=[]
    seen=set()
    for network in networks:
        n=str(network).lower().strip()
        key=f'{idempotency_key}:{n}'
        if not n or key in seen:
            raise RuntimeError('SCHEDULE_PLACEMENT_DUPLICATE')
        seen.add(key)
        rows.append({'network':n,'placementKey':key})
    return rows


def _metricool_info(c,item,video_url):
    s=item['schedule']
    local=schedule_instant(c,s['date']).astimezone(ZoneInfo(c['scheduler']['timezone']))
    providers=[{'network':x} for x in c['scheduler']['networks']]
    flags=s['ai_flags']
    return {
        'autoPublish':True,'draft':False,'descendants':[],'firstCommentText':'',
        'hasNotReadNotes':False,'media':[video_url],'mediaAltText':[],
        'providers':providers,
        'publicationDate':{'dateTime':local.strftime('%Y-%m-%dT%H:%M:%S'),'timezone':c['scheduler']['timezone']},
        'shortener':False,'smartLinkData':{'ids':[]},'text':s['text'],
        'facebookData':{'type':'REEL','title':s.get('facebook_title','')},
        'instagramData':{'type':'REEL','collaborators':[],'showReelOnFeed':True,'isAiGenerated':flags['instagram']},
        'tiktokData':{'disableComment':False,'disableDuet':False,'disableStitch':False,
                      'privacyOption':'PUBLIC_TO_EVERYONE','commercialContentThirdParty':False,
                      'commercialContentOwnBrand':False,'title':s.get('tiktok_title',s['youtube_title']),
                      'autoAddMusic':False,'photoCoverIndex':0,'isAigc':flags['tiktok']},
        'youtubeData':{'title':s['youtube_title'],'type':'short','privacy':'public',
                       'tags':s.get('youtube_tags',[]),'madeForKids':s['made_for_kids'],
                       'isAiGeneratedContent':flags['youtube']}
    }


def build(batch,staged_root,out):
    c=contract()
    items=validate_batch(batch,expect=int(c['scheduler']['daily_posts']))
    staged=Path(staged_root)
    rows=[]
    instants=set()
    networks=list(c['scheduler']['networks'])
    flat_expected=[]
    for item in items:
        rid=safe_id(item['id'])
        receipt_path=staged/f'{rid}.receipt.json'
        r2_path=staged/f'{rid}.r2.json'
        if not receipt_path.exists() or not r2_path.exists():
            raise RuntimeError(f'SCHEDULE_HANDOFF_MISSING {rid}')
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        if receipt.get('render_pass') is not True or receipt.get('qa_pass') is not True or receipt.get('state')!='PREVIEW_READY':
            raise RuntimeError(f'SCHEDULE_HANDOFF_QA_FAIL {rid}')
        if receipt.get('dispatch_fingerprint')!=dispatch_fingerprint(item):
            raise RuntimeError(f'SCHEDULE_DISPATCH_FINGERPRINT_FAIL {rid}')
        video_sha=str(receipt.get('video_sha256') or '').lower(); batch_sha=str(receipt.get('batch_sha256') or '').lower()
        if not SHA256_RE.fullmatch(video_sha) or not SHA256_RE.fullmatch(batch_sha):
            raise RuntimeError(f'SCHEDULE_RECEIPT_HASH_IDENTITY_FAIL {rid}')
        r2=json.loads(r2_path.read_text(encoding='utf-8'))
        if r2.get('schema')!='CENA_CERTA_R2_RECEIPT_V2' or r2.get('status')!='ready':
            raise RuntimeError(f'SCHEDULE_R2_RECEIPT_STATE_FAIL {rid}')
        if r2.get('public_probe_pass') is not True or r2.get('public_head_size_match') is not True or r2.get('blind_retry_used') is not False:
            raise RuntimeError(f'SCHEDULE_R2_RECONCILIATION_FAIL {rid}')
        r2_batch=str(r2.get('batchSha256') or '').lower(); r2_content=str(r2.get('contentSha256') or '').lower()
        if r2_batch!=batch_sha or r2_content!=video_sha:
            raise RuntimeError(f'SCHEDULE_MEDIA_CONTENT_CHAIN_FAIL {rid}')
        media=_find_media(r2)
        if not media:
            raise RuntimeError(f'SCHEDULE_HANDOFF_MEDIA_FAIL {rid}')
        local=schedule_instant(c,item['schedule']['date'])
        instant=local.astimezone(timezone.utc).replace(microsecond=0).isoformat()
        if instant in instants:
            raise RuntimeError('SCHEDULE_HANDOFF_DATE_COLLISION')
        instants.add(instant)
        info=_metricool_info(c,item,media['videoUrl'])
        idem=f"{c['scheduler']['brand_id']}:{rid}:{instant}"
        expected=build_expected_placements(rid,idem,networks)
        row={
            'id':rid,'brandId':str(c['scheduler']['brand_id']),'brandLabel':c['scheduler']['brand_label'],
            'timezone':c['scheduler']['timezone'],'date':local.isoformat(),'videoUrl':media['videoUrl'],
            'videoKey':media['videoKey'],'batchSha256':batch_sha,'videoSha256':video_sha,'r2ContentSha256':r2_content,
            'receiptSha256':sha256(receipt_path),'r2ReceiptSha256':sha256(r2_path),
            'dispatchFingerprint':dispatch_fingerprint(item),'scheduleFingerprint':schedule_fingerprint(item),
            'approvalRequired':True,'reconcileBeforeRetry':True,'idempotencyKey':idem,
            'expectedNetworks':networks,'expectedPlacements':expected,'expectedPlacementCount':len(expected),'info':info
        }
        rows.append(row)
        flat_expected.extend({'id':rid,'idempotencyKey':idem,**p} for p in expected)
    expected_posts=int(c['scheduler']['daily_posts'])
    expected_placements=int(c['scheduler']['expected_placements_per_batch'])
    if len(rows)!=expected_posts or len(flat_expected)!=expected_placements:
        raise RuntimeError('SCHEDULE_EXPECTED_PLACEMENTS_FAIL')
    keys=[x['placementKey'] for x in flat_expected]
    if len(keys)!=len(set(keys)):
        raise RuntimeError('SCHEDULE_EXPECTED_PLACEMENT_KEY_DUPLICATE')
    payload={
        'schema':'CENA_CERTA_METRICOOL_SCHEDULE_HANDOFF_V3','count':len(rows),
        'expectedScheduleObjects':expected_posts,'expectedNetworkPlacements':expected_placements,
        'networks':networks,'expectedPlacements':flat_expected,
        'schedule_gate':'BLOCKED_UNTIL_PRIVATE_PREVIEW_AND_HUMAN_APPROVAL',
        'live_brand_readback_required':True,'reconcile_before_retry':True,
        'scheduled_receipts_required':expected_posts,'network_placement_receipts_required':expected_placements,
        'media_content_chain_required':True,'items':rows
    }
    p=Path(out)
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+f'.tmp-{os.getpid()}')
    try:
        tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        os.replace(tmp,p)
    finally:
        tmp.unlink(missing_ok=True)
    print('FACTORY_V2_SCHEDULE_HANDOFF_PASS',len(rows),'posts',expected_placements,'placements',out)
    return payload


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--batch',required=True)
    ap.add_argument('--staged-root',required=True)
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    build(a.batch,a.staged_root,a.out)


if __name__=='__main__':
    main()
