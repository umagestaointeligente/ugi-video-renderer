#!/usr/bin/env python3
import importlib.util
import json
import os
import shutil
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PILOT_PATH = ROOT / "experiments/ugi-growth-v2/pilot-003-stable.json"
OUTPUT = ROOT / "output"
MEDIA = OUTPUT / "media"
PILOT_OUT = OUTPUT / "growth-v2-pilot3"


def get_json(url, **kwargs):
    last = None
    for n in range(3):
        try:
            r = requests.get(url, timeout=(10, 90), **kwargs)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last = exc
            time.sleep(2 * (n + 1))
    raise last


def download(url, target: Path):
    last = None
    for n in range(3):
        try:
            with requests.get(url, timeout=(10, 120), stream=True) as r:
                r.raise_for_status()
                with open(target, "wb") as fh:
                    for chunk in r.iter_content(1024 * 1024):
                        if chunk:
                            fh.write(chunk)
            if target.stat().st_size < 50000:
                raise RuntimeError(f"media too small: {target}")
            return
        except Exception as exc:
            last = exc
            time.sleep(2 * (n + 1))
    raise last


def select_media(scene, used, pexels_key, pixabay_key):
    queries = [scene["pexels_query"], scene["visual_intent"]]

    if pexels_key:
        for q in queries:
            try:
                data = get_json(
                    "https://api.pexels.com/v1/videos/search",
                    headers={"Authorization": pexels_key},
                    params={"query": q, "orientation": "portrait", "per_page": 20},
                )
                for item in data.get("videos", []):
                    uid = f"pexels:{item.get('id')}"
                    if uid in used:
                        continue
                    variants = [
                        x for x in item.get("video_files", [])
                        if x.get("file_type") == "video/mp4" and x.get("link")
                    ]
                    variants.sort(
                        key=lambda x: (
                            int(x.get("height") or 0) > int(x.get("width") or 0),
                            int(x.get("height") or 0),
                        ),
                        reverse=True,
                    )
                    if variants:
                        return {
                            "provider": "Pexels",
                            "uid": uid,
                            "provider_video_id": item.get("id"),
                            "provider_page_url": item.get("url"),
                            "query": q,
                            "download_url": variants[0]["link"],
                        }
            except Exception:
                pass

    if pixabay_key:
        for q in queries:
            try:
                data = get_json(
                    "https://pixabay.com/api/videos/",
                    params={
                        "key": pixabay_key,
                        "q": q,
                        "video_type": "film",
                        "safesearch": "true",
                        "per_page": 20,
                    },
                )
                for item in data.get("hits", []):
                    uid = f"pixabay:{item.get('id')}"
                    if uid in used:
                        continue
                    variants = item.get("videos") or {}
                    chosen = (
                        variants.get("large")
                        or variants.get("medium")
                        or variants.get("small")
                        or {}
                    )
                    if chosen.get("url"):
                        return {
                            "provider": "Pixabay",
                            "uid": uid,
                            "provider_video_id": item.get("id"),
                            "provider_page_url": item.get("pageURL"),
                            "query": q,
                            "download_url": chosen["url"],
                        }
            except Exception:
                pass

    return None


def main():
    payload = json.loads(PILOT_PATH.read_text(encoding="utf-8"))
    safety = payload["safety"]
    assert safety["render_only"] is True
    assert safety["publication"] is False
    assert safety["buffer_mutation"] is False
    assert safety["checkout"] is False
    assert safety["r2_upload"] is False
    assert payload["creative_contract"]["use_stable_ugi_renderer"] is True
    assert payload["creative_contract"]["real_video_background_required"] is True
    assert payload["creative_contract"]["still_image_montage_forbidden"] is True

    OUTPUT.mkdir(exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    PILOT_OUT.mkdir(parents=True, exist_ok=True)

    for old in MEDIA.glob("scene-*.mp4"):
        old.unlink()

    pexels_key = (os.getenv("PEXELS_API_KEY") or "").strip()
    pixabay_key = (os.getenv("PIXABAY_API_KEY") or "").strip()
    if not (pexels_key or pixabay_key):
        raise RuntimeError("No media provider key available")

    used = set()
    attribution = []
    for idx, scene in enumerate(payload["scenes"], start=1):
        selected = select_media(scene, used, pexels_key, pixabay_key)
        if not selected:
            raise RuntimeError(f"No real video found for scene {idx}")
        target = MEDIA / f"scene-{idx}.mp4"
        download(selected["download_url"], target)
        used.add(selected["uid"])
        selected = {k: v for k, v in selected.items() if k != "download_url"}
        selected["scene"] = idx
        selected["local_file"] = str(target.relative_to(ROOT))
        attribution.append(selected)

    if len(attribution) != len(payload["scenes"]):
        raise RuntimeError("All pilot scenes must use real video media")

    (PILOT_OUT / "media-attribution.json").write_text(
        json.dumps({"items": attribution}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    os.environ.update({
        "VIDEO_TITLE": payload["title"],
        "VIDEO_RENDER_ID": payload["pilot_id"],
        "VIDEO_CONTENT_ID": payload["pilot_id"],
        "VIDEO_EXPERIMENT_ID": "UGI-GROWTH-V2",
        "VIDEO_VARIANT": "PILOT-003-STABLE",
        "VIDEO_COMMERCIAL_INTENT": payload["commercial_intent"],
        "VIDEO_SCENES_JSON": json.dumps(payload, ensure_ascii=False),
        "VIDEO_CTA": payload["cta"],
        "VIDEO_ALLOW_LEGACY_SCENES": "false",
        "VIDEO_SMOKE_TEST": "false",
        "VIDEO_MUSIC_ENABLED": "true",
        "VIDEO_MUSIC_FAMILY": "innovation",
        "VIDEO_BRAND_OPACITY": "0.66",
        "VIDEO_BRAND_LOGO_WIDTH": "54",
        "VIDEO_BRAND_TOP": "78",
        "VIDEO_BRAND_RIGHT_MARGIN": "58",
    })

    module_name = "ugi_stable_renderer"
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "render-reel.py")
    renderer = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = renderer
    spec.loader.exec_module(renderer)

    if renderer.WORK.exists():
        shutil.rmtree(renderer.WORK)
    renderer.WORK.mkdir(parents=True, exist_ok=True)
    renderer.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = renderer.render_platform("instagram")
    src = OUTPUT / "instagram-reel.mp4"
    dst = PILOT_OUT / "UGI_Growth_V2_Pilot_003_Corrected.mp4"
    dst.write_bytes(src.read_bytes())

    storyboard_path = OUTPUT / "r42-storyboard-instagram.json"
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    if storyboard.get("qa", {}).get("quality_status") != "pass":
        raise RuntimeError("Stable renderer QA failed")
    scene_media = [s.get("media_kind") for s in storyboard.get("scenes", [])]
    if not scene_media or any(kind != "video" for kind in scene_media):
        raise RuntimeError(f"Pilot must be real moving video in every scene: {scene_media}")

    evidence = {
        "pilotId": payload["pilot_id"],
        "renderer": "render-reel.py stable UGI renderer / instagram master only",
        "durationSeconds": result.get("actual_duration"),
        "realVideoScenes": len(scene_media),
        "mediaKinds": scene_media,
        "brandSignatureRequired": True,
        "brandAsset": "assets/branding/ugi-symbol-transparent.png",
        "brandPosition": "upper_right",
        "publicationTriggered": False,
        "bufferMutationPerformed": False,
        "r2UploadPerformed": False,
        "checkoutTriggered": False,
        "ctaNarration": payload["creative_contract"]["full_cta_narration"],
        "visualCtaButton": payload["cta"],
        "qa": storyboard.get("qa"),
    }
    (PILOT_OUT / "UGI_Growth_V2_Pilot_003_EVIDENCE.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("UGI_GROWTH_V2_PILOT_003_STABLE_PASS")
    print(dst)


if __name__ == "__main__":
    main()
