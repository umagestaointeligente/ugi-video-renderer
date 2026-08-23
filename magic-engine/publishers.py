#!/usr/bin/env python3
from __future__ import annotations
import json, mimetypes, os, urllib.request
from pathlib import Path
from youtube_oauth import refresh_access_token

YOUTUBE_UPLOAD_INIT = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"


def _result(platform, status, **extra):
    return {"platform": platform, "status": status, **extra}


def youtube_ready() -> bool:
    return bool(os.getenv("YOUTUBE_CLIENT_ID") and os.getenv("YOUTUBE_CLIENT_SECRET") and os.getenv("YOUTUBE_REFRESH_TOKEN"))


def meta_ready() -> bool:
    return bool(os.getenv("META_ACCESS_TOKEN") and os.getenv("META_IG_USER_ID") and os.getenv("META_FB_PAGE_ID"))


def _youtube_access_token() -> str:
    return refresh_access_token(
        os.environ["YOUTUBE_CLIENT_ID"],
        os.environ["YOUTUBE_CLIENT_SECRET"],
        os.environ["YOUTUBE_REFRESH_TOKEN"],
    )


def publish_youtube(video_path: str, metadata: dict) -> dict:
    if not youtube_ready():
        return _result("youtube", "NOT_CONFIGURED", hard_stop=True, missing="OAuth secrets")
    path = Path(video_path)
    if not path.exists() or path.stat().st_size <= 0:
        return _result("youtube", "HARD_STOP_VIDEO_MISSING", hard_stop=True, video=video_path)
    if metadata.get("rights_gate") != "GREEN" or metadata.get("fact_gate") != "PASS" or metadata.get("qa_gate") != "PASS" or metadata.get("cost_gate") != "PASS":
        return _result("youtube", "HARD_STOP_GATES", hard_stop=True, metadata=metadata)

    access = _youtube_access_token()
    title = str(metadata.get("title") or "Lola Magic Engine").strip()[:100]
    description = str(metadata.get("description") or "").strip()[:5000]
    tags = [str(x)[:500] for x in (metadata.get("tags") or [])][:30]
    privacy = str(metadata.get("privacy_status") or "private").strip().lower()
    if privacy not in {"private", "unlisted", "public"}:
        privacy = "private"

    body = json.dumps({
        "snippet": {"title": title, "description": description, "tags": tags, "categoryId": str(metadata.get("category_id") or "22")},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }).encode()
    init_req = urllib.request.Request(
        YOUTUBE_UPLOAD_INIT,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {access}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(path.stat().st_size),
            "X-Upload-Content-Type": mimetypes.guess_type(path.name)[0] or "video/mp4",
        },
    )
    with urllib.request.urlopen(init_req, timeout=60) as r:
        upload_url = r.headers.get("Location")
    if not upload_url:
        return _result("youtube", "HARD_STOP_NO_RESUMABLE_URL", hard_stop=True)

    data = path.read_bytes()
    upload_req = urllib.request.Request(
        upload_url,
        data=data,
        method="PUT",
        headers={
            "Authorization": f"Bearer {access}",
            "Content-Type": mimetypes.guess_type(path.name)[0] or "video/mp4",
            "Content-Length": str(len(data)),
        },
    )
    with urllib.request.urlopen(upload_req, timeout=900) as r:
        response = json.loads(r.read().decode())
    video_id = response.get("id")
    return _result("youtube", "PUBLISHED" if video_id else "UPLOAD_RESPONSE_NO_ID", hard_stop=not bool(video_id), video_id=video_id, privacy_status=privacy)


def publish_instagram(video_url: str, caption: str) -> dict:
    if not meta_ready():
        return _result("instagram", "NOT_CONFIGURED", hard_stop=True, missing="Meta token/user/page")
    return _result("instagram", "AUTH_READY_PUBLISH_ADAPTER_PENDING", hard_stop=True, video_url=video_url)


def publish_facebook(video_url: str, caption: str) -> dict:
    if not meta_ready():
        return _result("facebook", "NOT_CONFIGURED", hard_stop=True, missing="Meta token/user/page")
    return _result("facebook", "AUTH_READY_PUBLISH_ADAPTER_PENDING", hard_stop=True, video_url=video_url)


def auth_matrix() -> dict:
    return {
        "youtube": "READY" if youtube_ready() else "PENDING",
        "instagram": "READY" if meta_ready() else "PENDING",
        "facebook": "READY" if meta_ready() else "PENDING"
    }

if __name__ == "__main__":
    print(json.dumps(auth_matrix(), indent=2))
