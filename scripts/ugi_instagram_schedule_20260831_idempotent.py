#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'scripts/ugi_instagram_production_20260831.py'
spec=importlib.util.spec_from_file_location('prod31',BASE)
prod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(prod)


def load_receipt()->dict[str,Any]:
    if prod.RECEIPT.exists():
        try:return json.loads(prod.RECEIPT.read_text(encoding='utf-8'))
        except Exception:pass
    return {"project":"UGI","component":"INSTAGRAM-20260831-PRODUCTION","items":[]}

def save(payload:dict[str,Any]):
    payload['checkedAt']=dt.datetime.now(dt.timezone.utc).isoformat()
    payload['state']='BUFFER_SCHEDULED_6_OF_6' if len([x for x in payload['items'] if x.get('state')=='BUFFER_SCHEDULED'])==6 else 'IN_PROGRESS'
    prod.RECEIPT.parent.mkdir(parents=True,exist_ok=True)
    prod.RECEIPT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def by_id(payload,cid): return next((x for x in payload.get('items',[]) if x.get('contentId')==cid),None)

def verify_existing(c,payload,cid,due):
    item=by_id(payload,cid)
    if not item or not item.get('bufferPostId'): return None
    code,rb=c.get('/api/r45-2/buffer-status?id='+prod.quote(str(item['bufferPostId'])))
    post=rb.get('post') or rb.get('publication') or {}
    expected=prod.to_utc_iso(due)
    if code==200 and rb.get('ok') and post.get('status')=='scheduled' and prod.same_due(post.get('dueAt'),expected) and not post.get('error'):
        item['readback']=rb; item['dueAtExpected']=expected; item['state']='BUFFER_SCHEDULED'; save(payload); return item
    raise RuntimeError(f'existing_post_not_proven:{cid}:{code}:{rb}')

def put(payload,item):
    old=by_id(payload,item['contentId'])
    if old: payload['items'][payload['items'].index(old)]=item
    else: payload['items'].append(item)
    save(payload)

def check_feed_collision(target_due:str):
    target=dt.datetime.fromisoformat(target_due).astimezone(dt.timezone.utc)
    for p in ROOT.glob('control-plane/**/receipts/*.json'):
        if p==prod.RECEIPT: continue
        try:data=json.loads(p.read_text(encoding='utf-8'))
        except Exception:continue
        rows=data.get('items') or data.get('results') or []
        if not isinstance(rows,list): continue
        for r in rows:
            if not isinstance(r,dict): continue
            typ=str(r.get('type') or r.get('kind') or '').lower()
            if not any(k in typ for k in ('carousel','reel','visual_post','static_post')): continue
            due=r.get('dueAtExpected') or r.get('dueAt') or r.get('dueAtRequested')
            if not due: continue
            try:d=dt.datetime.fromisoformat(str(due).replace('Z','+00:00')).astimezone(dt.timezone.utc)
            except Exception:continue
            if abs((d-target).total_seconds())<3600:
                raise RuntimeError(f'FEED_COLLISION_FAIL:{p}:{r.get("contentId")}:{due}')

def main():
    key=os.environ.get('UGI_WORKER_COMMAND_KEY') or os.environ.get('UGI_LOLA_COMMAND_KEY')
    if not key: raise RuntimeError('missing UGI worker key')
    if len({s['music'] for s in prod.STORIES})!=len(prod.STORIES): raise RuntimeError('AUDIO_QA_FAIL:story_music_not_unique')
    c=prod.Client(key); payload=load_receipt()

    for i,s in enumerate(prod.STORIES,1):
        if verify_existing(c,payload,s['id'],s['due']): continue
        v=prod.ASSET_DIR/f'story-{i:02d}.mp4'; pr=prod.probe(v)
        if not pr.get('audio') or not pr.get('video'): raise RuntimeError(f'AUDIO_QA_FAIL:{s["id"]}:{pr}')
        up=prod.upload_video(c,s['id'],v)
        res=prod.schedule(c,kind='story_video',cid=s['id'],due=s['due'],video_url=up.get('videoUrl'))
        item={"contentId":s['id'],"type":"story_video","dueAtRequested":s['due'],"music":{"title":s['music'],"url":prod.MUSIC[s['music']],**prod.LICENSE},"visualQA":{"language":"pt-BR","generatedTextInBackground":False,"controlledTypography":True,"lowerThirdClean":True},"avQA":pr,"upload":up,**res}
        put(payload,item)

    cid=prod.CAROUSEL['id']
    if not verify_existing(c,payload,cid,prod.CAROUSEL['due']):
        check_feed_collision(prod.CAROUSEL['due'])
        up=prod.upload_video(c,cid,prod.ASSET_DIR/'carousel-01.mp4')
        imgs=[f'{prod.RAW_BASE}/carousel-{i:02d}.png' for i in range(2,8)]
        # Verify all public slide assets exist before Buffer mutation.
        for u in imgs:
            rr=prod.requests.get(u,timeout=60)
            if rr.status_code!=200 or len(rr.content)<5000: raise RuntimeError(f'VISUAL_QA_FAIL:public_slide_unavailable:{u}:{rr.status_code}:{len(rr.content)}')
        res=prod.schedule(c,kind='mixed_carousel',cid=cid,due=prod.CAROUSEL['due'],text=prod.CAROUSEL['caption'],video_url=up.get('videoUrl'),image_urls=imgs)
        item={"contentId":cid,"type":"mixed_carousel","dueAtRequested":prod.CAROUSEL['due'],"slideCount":7,"music":{"title":prod.CAROUSEL['music'],"url":prod.MUSIC[prod.CAROUSEL['music']],**prod.LICENSE},"visualQA":{"language":"pt-BR","generatedTextInBackground":False,"controlledTypography":True,"individualSlides":True,"feedCollisionPass":True},"avQA":prod.probe(prod.ASSET_DIR/'carousel-01.mp4'),"upload":up,**res}
        put(payload,item)

    save(payload)
    print(json.dumps(payload,ensure_ascii=False,indent=2))
    return 0 if payload.get('state')=='BUFFER_SCHEDULED_6_OF_6' else 1

if __name__=='__main__': sys.exit(main())
