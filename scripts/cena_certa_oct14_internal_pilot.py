#!/usr/bin/env python3
"""Internal QA-only first-frame cinematic pilot from a studio-published scene.

This intentionally does NOT constitute a license or approval to repost.
Never publish, schedule, or create a public GitHub Release from this script.
"""
from __future__ import annotations
import base64
import hashlib
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cena_certa_oct13_pack as pack

OUT = ROOT / "out/cena-certa-oct14/pilot"
WORK = ROOT / "tmp/cena-certa-oct14/pilot"
LOGO = ROOT / "assets/cena-certa-logo.png.b64"
MANIFEST = ROOT / "ops/cena-certa-oct14/editorial-v3-0.json"
EXPECTED_TITLE = "Corra que a Polícia Vem Aí! (2025)"
EXPECTED_SCENE = "https://www.youtube.com/watch?v=AQmiLNr4BVY"

def main():
    editorial = json.loads(MANIFEST.read_text(encoding="utf-8"))
    row = editorial["items"][0]
    if row["title"] != EXPECTED_TITLE or row["network"] != "tiktok":
        raise SystemExit("EDITORIAL_SOURCE_MISMATCH")
    if row.get("master_mp4_url") or row.get("metricool_status") != "NOT_SCHEDULED":
        raise SystemExit("PILOT_MUST_BE_UNPUBLISHED")
    if not LOGO.exists():
        raise SystemExit("LOGO_MISSING")
    pack.WORK = WORK
    pack.OUT = OUT
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    logo = WORK / "logo.png"
    logo.write_bytes(base64.b64decode("".join(LOGO.read_text().split())))
    item = {
        "id": "CC-OCT14-TT-NAKEDGUN-INTERNAL-PILOT",
        "network": "tiktok",
        "format": "film_comedy_conflict",
        "source": EXPECTED_SCENE,
        "source_id": "AQmiLNr4BVY",
        "segments": [[12, 40]],
        "hook": "O DISFARCE DESSE POLICIAL E ABSURDO",
        "cta": "VOCE CONSEGUIU FICAR SERIO?",
        "audio_mode": "ORIGINAL_ENGLISH_STUDIO_CLIP",
    }
    source = pack.download_source(item, {})
    output, start, end, duration, segments = pack.render_item(item, source, logo, None)
    sha = hashlib.sha256(output.read_bytes()).hexdigest()
    report = {
        "schema": "CENA_CERTA_INTERNAL_PREVIEW_V1",
        "date": "2026-10-14",
        "editorial_title": EXPECTED_TITLE,
        "source": EXPECTED_SCENE,
        "publisher": "Paramount Movies official YouTube clip",
        "source_segment": segments,
        "duration_sec": duration,
        "sha256": sha,
        "bytes": output.stat().st_size,
        "path": output.name,
        "network": "tiktok",
        "technical_qa": "PASS",
        "redistribution_license": "NOT_VERIFIED",
        "content_editorial_qa": "PENDING_MANUAL_SCENE_REVIEW",
        "anti_repeat_180d": "NOT_VERIFIED",
        "release_allowed": False,
        "publish_allowed": False,
        "metricool_scheduling_allowed": False,
        "purpose": "internal QA preview only, not final publishable master",
    }
    (OUT / "internal-preview.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("INTERNAL_CENA_CERTA_PILOT=PASS")
    print("SHA256=" + sha)
    print("FILE=" + str(output))

if __name__ == "__main__":
    main()
