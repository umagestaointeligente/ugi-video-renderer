#!/usr/bin/env python3
"""Fail-closed adapter: the user-approved Oct13 editorial is the ONLY source of truth.

Compiles source-verified editorial into the FFmpeg renderer's operational manifest.
Never fabricates licensed media, clips, rights proof, source timestamps or approvals.
No network, downloads, publication or scheduling.
"""
from __future__ import annotations
import argparse
import ipaddress
import json
import pathlib
import re
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
EDITORIAL = ROOT / "ops/cena-certa-oct13/editorial-v2-9-proposed.json"
MANIFEST = ROOT / "ops/cena-certa-oct13/manifest.json"
NETWORKS = {"tiktok": 3, "instagram": 3, "facebook": 3, "youtube": 3}
LICENSE_SCOPES = {"SOCIAL_REPUBLISH", "PUBLIC_DOMAIN", "CC_BY", "CC_BY_SA"}
LOCAL_HOSTS = {"localhost", "localhost.localdomain", "metadata.google.internal"}

def safe_https(value):
    if not isinstance(value, str):
        return False
    u = urlparse(value)
    host = (u.hostname or "").lower()
    if u.scheme != "https" or not host or u.username or u.password or host in LOCAL_HOSTS:
        return False
    if host.endswith((".local", ".internal", ".localhost")):
        return False
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            return False
    except ValueError:
        pass
    return True

def validate_segments(value, target, key, errors):
    if not isinstance(value, list) or not value:
        errors.append(key + ":SOURCE_SEGMENTS_MISSING")
        return None
    spans = []
    for part in value:
        if (not isinstance(part, list) or len(part) != 2 or
            not all(type(t) in (int, float) and 0 <= t <= 21600 for t in part) or
            float(part[1]) <= float(part[0])):
            errors.append(key + ":SOURCE_WINDOW_INVALID")
            return None
        start, end = map(float, part)
        if end-start < 4.0:
            errors.append(key + ":SOURCE_SEGMENT_TOO_SHORT")
            return None
        spans.append([start, end])
    if len(spans) == 1 and spans[0][1]-spans[0][0] < 12:
        errors.append(key + ":SOURCE_WINDOW_TOO_SHORT")
    length = sum(e-s for s, e in spans)
    if length < 12 or length > 60:
        errors.append(key + ":OUTPUT_DURATION_OUTSIDE_12_60S")
    if not isinstance(target, dict) or not all(type(target.get(k)) in (int, float) for k in ("min", "max")):
        errors.append(key + ":TARGET_DURATION_MISSING")
    elif length < target["min"] - 1 or length > target["max"] + 1:
        errors.append(key + ":SCENE_DURATION_DOES_NOT_MATCH_EDITORIAL")
    return spans

def compile_editorial(approved):
    errors = []
    if approved.get("publication_date") != "2026-10-13" or approved.get("metricool_brand_id") != 6809869:
        errors.append("SCOPE_DATE_OR_BRAND_FAIL")
    if approved.get("timezone") != "America/Sao_Paulo":
        errors.append("TIMEZONE_FAIL")
    items = approved.get("items", [])
    if not isinstance(items, list) or len(items) != 12:
        errors.append("ITEM_COUNT_NOT_12")
        return None, errors
    counts, slots, compiled = {}, set(), []
    used_source_windows = []
    for entry in items:
        network, slot = entry.get("network"), entry.get("slot")
        key = str(entry.get("id") or (str(network)+"_"+str(slot)))
        counts[network] = counts.get(network, 0) + 1
        if (network, slot) in slots:
            errors.append(key + ":DUPLICATE_NETWORK_SLOT")
        slots.add((network, slot))
        if network not in NETWORKS or not isinstance(slot, str) or not re.fullmatch(r"2026-10-13T\d\d:\d\d:00-03:00", slot):
            errors.append(key + ":SLOT_INVALID")
        if not isinstance(entry.get("title"), str) or not entry.get("title").strip():
            errors.append(key + ":TITLE_MISSING")
        if "2025" not in str(entry.get("title")):
            errors.append(key + ":ONLY_2025_FILM_OR_SERIES_ALLOWED")
        if not entry.get("hook") or not entry.get("cta"):
            errors.append(key + ":HOOK_OR_CTA_MISSING")
        source_url = entry.get("source_url")
        source_id = entry.get("source_id")
        if not safe_https(source_url):
            errors.append(key + ":HTTPS_SOURCE_MISSING")
        if not isinstance(source_id, str) or not source_id.strip() or "/" in source_id or ".." in source_id:
            errors.append(key + ":SOURCE_ID_MISSING")
        rights = entry.get("rights_evidence") or {}
        if (rights.get("status") != "VERIFIED" or
            rights.get("scope") not in LICENSE_SCOPES or
            not safe_https(rights.get("proof_url"))):
            errors.append(key + ":SOCIAL_REPUBLISH_RIGHTS_MISSING")
        if entry.get("media_type") != "LIVE_ACTION":
            errors.append(key + ":LIVE_ACTION_EVIDENCE_MISSING")
        if network == "youtube" and "globoplay.globo.com" in str(source_url):
            errors.append(key + ":YOUTUBE_GLOBO_SOURCE_FORBIDDEN")
        spans = validate_segments(entry.get("source_segments"), entry.get("target_duration_sec"), key, errors)
        if spans and isinstance(source_id, str):
            for start, end in spans:
                for old_id, old_start, old_end, old_key in used_source_windows:
                    if source_id == old_id and max(start, old_start) < min(end, old_end):
                        errors.append(key + ":INTRA_PACK_SOURCE_OVERLAP:" + old_key)
                used_source_windows.append((source_id, start, end, key))
        compiled.append({
            "id": key, "network": network, "slot": slot, "title": entry.get("title"),
            "year": 2025, "format": "film_comedy_conflict" if entry.get("theme") == "humor" else "film_scene_editorial",
            "source": source_url, "source_id": source_id, "segments": spans,
            "hook": entry.get("hook"), "cta": entry.get("cta"),
            "caption": entry.get("caption") or (str(entry.get("title")) + " | Qual sua cena favorita? #CenaCerta #Cinema #Series"),
            "audio_mode": "ORIGINAL_SOURCE_DIALOGUE",
            "rights_evidence": rights, "media_type": entry.get("media_type"),
        })
    if counts != NETWORKS:
        errors.append("NETWORK_COUNTS_FAIL:" + repr(counts))
    return ({
        "schema": "CENA_CERTA_OCT13_COMPILED_V29",
        "timezone": "America/Sao_Paulo",
        "date": "2026-10-13",
        "objective": "Newer acclaimed live-action film and series 12-video pack",
        "benchmark_basis": "Cena Certa 2.9 approved editorial; no old Globo or outdated lineup",
        "editorial_rules": ["2025 films/series", "60d anti-repeat", "no Globo on YouTube", "no auto publish before gates"],
        "items": compiled
    } if not errors else None), errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-manifest", action="store_true", help="Overwrite operational manifest ONLY if all checks pass")
    args = ap.parse_args()
    editorial = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    compiled, failures = compile_editorial(editorial)
    if failures:
        print("CENA_CERTA_EDITORIAL_SOURCE_GATE=BLOCKED")
        print(json.dumps({"count":len(failures),"errors":failures},ensure_ascii=False,indent=2))
        raise SystemExit(2)
    if args.write_manifest:
        MANIFEST.write_text(json.dumps(compiled,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("CENA_CERTA_EDITORIAL_MANIFEST=COMPILED")
    else:
        print("CENA_CERTA_EDITORIAL_SOURCE_GATE=PASS (read-only)")

if __name__ == "__main__":
    main()
