#!/usr/bin/env python3
from __future__ import annotations
import json, os, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)
TOKEN_URL = "https://oauth2.googleapis.com/token"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true"


def post_form(url: str, form: dict) -> dict:
    data = urllib.parse.urlencode(form).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def get_json(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    cid=(os.getenv("YOUTUBE_CLIENT_ID") or "").strip()
    csec=(os.getenv("YOUTUBE_CLIENT_SECRET") or "").strip()
    rt=(os.getenv("YOUTUBE_REFRESH_TOKEN") or "").strip()
    result={"checked_at":now,"platform":"youtube","auth_status":"PENDING","token_refresh":"NOT_RUN","channel_access":"NOT_RUN","hard_stop":True}
    if not (cid and csec and rt):
        result["reason"]="missing_oauth_secrets"
    else:
        try:
            token_payload=post_form(TOKEN_URL,{"client_id":cid,"client_secret":csec,"refresh_token":rt,"grant_type":"refresh_token"})
            access=str(token_payload.get("access_token") or "").strip()
            if not access:
                result.update({"auth_status":"FAIL","token_refresh":"FAIL","reason":"no_access_token_returned"})
            else:
                result["token_refresh"]="PASS"
                channels=get_json(CHANNELS_URL, access)
                items=channels.get("items") or []
                if items:
                    ch=items[0]
                    result.update({
                        "auth_status":"READY",
                        "channel_access":"PASS",
                        "hard_stop":False,
                        "channel_id":ch.get("id"),
                        "channel_title":((ch.get("snippet") or {}).get("title") or ""),
                    })
                else:
                    result.update({"auth_status":"FAIL","channel_access":"FAIL","reason":"no_channel_for_authorized_account"})
        except urllib.error.HTTPError as e:
            body=e.read().decode(errors="replace")[:1000]
            result.update({"auth_status":"FAIL","reason":f"http_{e.code}","details":body})
        except Exception as e:
            result.update({"auth_status":"FAIL","reason":type(e).__name__,"details":str(e)[:1000]})
    path=OUT/"youtube-auth-health.json"
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:result.get(k) for k in ("auth_status","token_refresh","channel_access","hard_stop","reason","channel_id","channel_title")},ensure_ascii=False))
    return 0 if result.get("auth_status")=="READY" else 2

if __name__=="__main__":
    raise SystemExit(main())
