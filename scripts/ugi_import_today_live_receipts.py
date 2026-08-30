from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

import requests

WORKER="https://lola-operacional-ugi.umagestaointeligente.workers.dev"
OUT=Path("control-plane/publisher-hub/receipts/UGI-20260830-LIVE-IMPORT.json")
TARGETS=[
    ("UGI-20260830-TT-01-MEETINGS","tiktok"),
    ("UGI-20260830-YT-01-RESULT-HOURS","youtube"),
    ("UGI-20260830-IG-01-CISCO-AGENTS","instagram"),
    ("UGI-20260830-TT-02-AI-JOBS","tiktok"),
    ("UGI-20260830-YT-02-MODEL-HARNESS","youtube"),
]

class Client:
    def __init__(self,key:str):
        self.h={"x-lola-command-key":key,"accept":"application/json"}
    def get(self,path:str)->tuple[int,dict[str,Any]]:
        r=requests.get(WORKER+path,headers=self.h,timeout=120)
        try:return r.status_code,r.json()
        except Exception:return r.status_code,{"ok":False,"raw":r.text[:1200]}

def main()->int:
    key=os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    if not key: raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")
    c=Client(key); results=[]
    for cid,platform in TARGETS:
        _,lookup=c.get("/api/draft-lookup?content_id="+requests.utils.quote(cid,safe=""))
        draft=str(lookup.get("draftId") or "")
        row={"contentId":cid,"platform":platform,"draftId":draft,"lookup":lookup}
        if draft:
            _,rb=c.get("/api/platform-publication-status?id="+requests.utils.quote(draft,safe="")+"&platform="+platform)
            pub=rb.get("publication") or {}
            row.update({"dueAt":pub.get("dueAt"),"bufferPostId":pub.get("bufferPostId"),"status":pub.get("status"),"bufferStatus":pub.get("bufferStatus"),"sentAt":pub.get("sentAt"),"externalLink":pub.get("externalLink"),"readback":rb,"readbackPass":rb.get("ok") is True and bool(pub.get("bufferPostId"))})
        results.append(row)
    payload={"ok":all(x.get("readbackPass") is True for x in results),"project":"UGI","batchId":"UGI-20260830-LIVE-IMPORT","publisher":"BUFFER","source":"live-worker-readback-import","results":results,"timestamp":dt.datetime.now(dt.timezone.utc).isoformat()}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,ensure_ascii=False,indent=2))
    return 0 if payload["ok"] else 1

if __name__=="__main__": raise SystemExit(main())
