#!/usr/bin/env python3
from __future__ import annotations
import json, os, urllib.request, urllib.parse
from pathlib import Path


def _result(platform, status, **extra):
    return {"platform": platform, "status": status, **extra}


def youtube_ready() -> bool:
    return bool(os.getenv("YOUTUBE_CLIENT_ID") and os.getenv("YOUTUBE_CLIENT_SECRET") and os.getenv("YOUTUBE_REFRESH_TOKEN"))


def meta_ready() -> bool:
    return bool(os.getenv("META_ACCESS_TOKEN") and os.getenv("META_IG_USER_ID") and os.getenv("META_FB_PAGE_ID"))


def publish_youtube(video_path: str, metadata: dict) -> dict:
    if not youtube_ready():
        return _result("youtube", "NOT_CONFIGURED", hard_stop=True, missing="OAuth secrets")
    # Upload adapter intentionally fails closed until account OAuth is connected and tested.
    # The production adapter will use videos.insert with resumable upload after auth smoke.
    return _result("youtube", "AUTH_READY_UPLOAD_ADAPTER_PENDING", hard_stop=True, video=video_path, metadata=metadata)


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
