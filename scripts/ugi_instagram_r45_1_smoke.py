from __future__ import annotations

import datetime as dt
import json
import os
import time
from pathlib import Path
from typing import Any

import requests

WORKER="https://lola-operacional-ugi.umagestaointeligente.workers.dev"
EXPECTED="lola-v8-r45-1-share-now-lock-fix-2026-08-30"
OUT=Path("control-plane/smoke/receipts/instagram-r45-1-smoke.json")

class Client:
    def __init__(self,key:str): self.h={"x-lola-command-key":key,"accept":"application/json"}
    def get(self,path:str,timeout:int=120)->tuple[int,dict[str,Any]]:
        r=requests.get(WORKER+path,headers=self.h,timeout=timeout)
        try:return r.status_code,r.json()
        except Exception:return r.status_code,{"ok":False,"raw":r.text[:2000]}
    def post(self,path:str,payload:dict[str,Any],timeout:int=900)->tuple[int,dict[str,Any]]:
        r=requests.post(WORKER+path,headers={**self.h,"content-type":"application/json"},json=payload,timeout=timeout)
        try:return r.status_code,r.json()
        except Exception:return r.status_code,{"ok":False,"raw":r.text[:2000]}

def now()->str:return dt.datetime.now(dt.timezone.utc).isoformat()

def wait_health(c:Client,seconds:int=150)->dict[str,Any]:
    deadline=time.time()+seconds; last={}
    while time.time()<deadline:
        _,last=c.get('/api/health')
        if last.get('ok') is True and last.get('version')==EXPECTED:return last
        time.sleep(5)
    return last

def public_proof(url:str|None)->dict[str,Any]:
    if not url:return {"attempted":False,"ok":False,"reason":"external_link_missing"}
    try:
        r=requests.get(url,timeout=30,allow_redirects=True,headers={"User-Agent":"Mozilla/5.0 UGI-Instagram-Smoke/1.0"})
        return {"attempted":True,"ok":r.status_code<500,"httpStatus":r.status_code,"finalUrl":r.url}
    except Exception as e:return {"attempted":True,"ok":False,"error":str(e)}

def main()->int:
    key=os.getenv('UGI_WORKER_COMMAND_KEY') or os.getenv('UGI_LOLA_COMMAND_KEY') or ''
    if not key: raise SystemExit('UGI_WORKER_COMMAND_KEY_MISSING')
    c=Client(key); receipt={"project":"UGI","component":"INSTAGRAM-R45.1-SMOKE","startedAt":now()}
    health=wait_health(c); receipt['health']=health
    if health.get('version')!=EXPECTED:
        receipt.update(ok=False,state='R45_1_NOT_LIVE',finishedAt=now()); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,ensure_ascii=False,indent=2)); return 1
    cid='UGI-SMOKE-20260830-INSTAGRAM-R45-1-RETRY2'
    payload={"source":"UGI-CONTROL-PLANE-SMOKE","type":"visual_post","content_id":cid,"experiment_id":"UGI-PRODUCTION-SMOKE-20260830","variant":"IG-R45-1","topic":"Prova real de publicação automática","objective":"validar publicação Instagram sem Lola 5.3","hook":"TESTE DE ENTREGA REAL","key_message":"Este post existe apenas para provar que o Control Plane da UGI consegue gerar, validar, publicar e confirmar a entrega no Instagram.","instructions":"Visual limpo, humano, sem estética de propaganda. Smoke test temporário.","cta":"Teste operacional — pode ser removido após a validação.","editorial_mode":"smoke_test","commercial_offer":False}
    code,gen=c.post('/api/r45/generate',payload); receipt.update(contentId=cid,generateHttp=code,generation=gen)
    draft=(gen.get('draft') or {}); did=str(draft.get('id') or ''); receipt['draftId']=did
    if code!=200 or gen.get('ok') is not True or not did:
        receipt.update(ok=False,state='GENERATION_FAILED',finishedAt=now()); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,ensure_ascii=False,indent=2)); return 1
    code,appr=c.post('/api/r45/static-approval',{"id":did,"decision":"approved"}); receipt.update(approvalHttp=code,approval=appr)
    if code!=200 or appr.get('ok') is not True:
        receipt.update(ok=False,state='APPROVAL_FAILED',finishedAt=now()); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,ensure_ascii=False,indent=2)); return 1
    code,pub=c.post('/api/r45/static-publish',{"id":did,"mode":"shareNow"}); receipt.update(publishHttp=code,publish=pub)
    if code!=200 or pub.get('ok') is not True:
        receipt.update(ok=False,state='PUBLISH_FAILED',finishedAt=now()); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,ensure_ascii=False,indent=2)); return 1
    deadline=time.time()+480; rb={}
    while time.time()<deadline:
        _,rb=c.get('/api/r45/static-publication-status?id='+requests.utils.quote(did,safe=''))
        p=rb.get('publication') or {}; s=str(p.get('status') or '').lower()
        if p.get('sentAt') or s in {'sent','published','complete','completed'}:break
        if s in {'error','failed','cancelled'}:break
        time.sleep(10)
    receipt['readback']=rb; p=rb.get('publication') or {}; receipt['externalProof']=public_proof(p.get('externalLink'))
    receipt['ok']=bool(p.get('bufferPostId')) and bool(p.get('sentAt')) and str(p.get('status') or '').lower() not in {'error','failed','cancelled'}
    receipt['state']='DELIVERED' if receipt['ok'] else 'DELIVERY_UNPROVEN'; receipt['finishedAt']=now()
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,ensure_ascii=False,indent=2)); return 0 if receipt['ok'] else 1

if __name__=='__main__': raise SystemExit(main())
