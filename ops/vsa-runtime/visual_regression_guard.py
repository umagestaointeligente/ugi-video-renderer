#!/usr/bin/env python3
"""Fail-closed visual regression guard for Você Sabia Agora.

Blocks the exact regression seen in Sep10-13 batches: legacy carrier-frame shell,
placeholder title/caption leakage, generic static CAUSA/EFEITO cards, missing
closed captions, missing causal motion and non-canonical mask/CTA assets.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

MASK_SHA = "9f6ebae6742b007b1e660cd401b610933d0a06c2c3fee240220abf7215e1a4d9"
CTA_SHA = "6c064a533784f2c09b594095646aa538e07f77955ed348656c60e5d2795fa5a8"
FORBIDDEN_RENDERERS = {"legacy_carrier_shell", "static_cause_effect_card"}
FORBIDDEN_TOKENS = {"CAUSA", "EFEITO"}

class GateError(RuntimeError):
    pass

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()

def require(condition: bool, reason: str):
    if not condition:
        raise GateError(reason)

def validate(manifest: dict):
    require(manifest.get("project") == "ORBIT/VSA", "PROJECT_LOCK_FAIL")
    require(manifest.get("channel_id") == "UCm0UMO6lNWlr66YSIS1p4iQ", "CHANNEL_LOCK_FAIL")
    require(manifest.get("renderer") not in FORBIDDEN_RENDERERS, "LEGACY_RENDERER_BLOCK")
    require(manifest.get("legacy_carrier_frame") is False, "CARRIER_FRAME_FORBIDDEN")
    require(manifest.get("canonical_mask_sha256") == MASK_SHA, "CANONICAL_MASK_SHA_MISMATCH")
    require(manifest.get("canonical_cta_sha256") == CTA_SHA, "CANONICAL_CTA_SHA_MISMATCH")
    require(manifest.get("mask_variable_fields_cleaned") is True, "MASK_VARIABLE_FIELDS_NOT_CLEAN")
    require(manifest.get("title_collision_check") == "PASS", "TITLE_COLLISION_FAIL")
    require(manifest.get("closed_captions_burned") is True, "CAPTIONS_MISSING")
    require(manifest.get("caption_match") == "PASS", "CAPTION_MATCH_FAIL")
    require(int(manifest.get("caption_event_count", 0)) >= 8, "CAPTION_EVENT_COUNT_TOO_LOW")
    require(manifest.get("caption_zone_check") == "PASS", "CAPTION_ZONE_FAIL")
    require(manifest.get("scene_repeat_count") == 0, "SCENE_REPEAT_FAIL")
    require(int(manifest.get("distinct_real_moments", 0)) >= 3, "REAL_SCENE_DIVERSITY_FAIL")
    motion = manifest.get("causal_motion") or []
    require(len(set(motion)) >= 3, "CAUSAL_MOTION_TYPES_TOO_FEW")
    require(all(str(x).upper() not in FORBIDDEN_TOKENS for x in manifest.get("onscreen_generic_labels", [])), "GENERIC_CAUSE_EFFECT_LABEL_BLOCK")
    require(manifest.get("motion_state_change_gate") == "PASS", "STATIC_EXPLAINER_BLOCK")
    require(manifest.get("music_theme_match_gate") == "PASS", "MUSIC_THEME_MISMATCH")
    require(manifest.get("music_rights_gate") == "PASS", "MUSIC_RIGHTS_FAIL")
    require(manifest.get("thumbnail_ready") is True, "THUMBNAIL_MISSING")
    return {"status":"VSA_VISUAL_REGRESSION_PASS","renderer":manifest.get("renderer"),"motion_types":motion}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    args=ap.parse_args()
    try:
        m=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        print(json.dumps(validate(m), ensure_ascii=False))
    except GateError as e:
        print(json.dumps({"status":"BLOCKED","reason":str(e)}, ensure_ascii=False))
        raise SystemExit(2)

if __name__ == "__main__":
    main()
