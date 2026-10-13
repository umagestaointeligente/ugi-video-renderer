#!/usr/bin/env python3
"""Cena Certa: restore October 8–12 order: source discovery -> source probe -> gates -> FFmpeg.

Metadata discovery only. NEVER auto-licenses or auto-approves copyrighted sources.
No video download, manifest mutation, publication or scheduling.
"""
from __future__ import annotations
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
EDITORIAL = ROOT / "ops/cena-certa-oct13/editorial-v2-9-proposed.json"
OUTPUT = ROOT / "out/cena-certa-oct13"
SKIP_WORDS = ("trailer", "teaser", "fan made", "fanmade", "reaction", "review", "analysis", "breakdown", "explained", "recap", "compilation")


def search_term(item):
    title = item.get("canonical_english") or item.get("title") or ""
    title = re.sub(r"\s*\(20\d\d\)", "", title).strip()
    return f"{title} 2025 official scene clip"


def acceptable_candidate(result, title):
    name = str(result.get("title") or "")
    low = name.casefold()
    if any(x in low for x in SKIP_WORDS) or not result.get("id") or not name or len(name) > 240:
        return False
    tokens = [x for x in re.findall(r"[\w]+", title.casefold())
              if len(x) >= 4 and x not in ("2025", "film", "movie", "the")]
    return bool(tokens) and any(x in low for x in tokens)


def yt_search(item, timeout=42):
    query = search_term(item)
    command = [
        "yt-dlp", "--flat-playlist", "--dump-single-json", "--skip-download",
        "--no-warnings", "--socket-timeout", "12", "--retries", "1",
        f"ytsearch5:{query}",
    ]
    try:
        p = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"query": query, "status": "PROBE_UNAVAILABLE", "error": str(exc)[:250], "candidates": []}
    if p.returncode != 0:
        return {"query": query, "status": "PROBE_FAILED", "error": p.stderr[-450:], "candidates": []}
    try:
        data = json.loads(p.stdout)
    except (ValueError, TypeError):
        return {"query": query, "status": "PROBE_INVALID_JSON", "candidates": []}
    title = item.get("canonical_english") or item.get("title") or ""
    candidates = []
    for result in (data.get("entries") or []):
        if not isinstance(result, dict) or not acceptable_candidate(result, title):
            continue
        video_id = str(result["id"])
        url = result.get("webpage_url") or result.get("url") or ""
        if not isinstance(url, str) or not url.startswith("https://"):
            url = ("https://www.youtube.com/watch?v=" + video_id) if re.fullmatch(r"[a-zA-Z0-9_-]{11}", video_id) else ""
        if not url:
            continue
        candidates.append({
            "url": url, "source_id": video_id, "title": result.get("title"),
            "uploader": result.get("uploader") or result.get("channel"),
            "duration": result.get("duration"),
            "source_usable": "UNVERIFIED", "rights_to_republish": "UNVERIFIED",
            "exact_scene_window": "NOT_SELECTED",
        })
    return {"query": query,
            "status": "CANDIDATES_TO_REVIEW" if candidates else "NO_MATCHING_SCENE_CANDIDATES",
            "candidates": candidates[:5]}


def main():
    document = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    entries = document.get("items") or []
    if len(entries) != 12:
        raise SystemExit("EDITORIAL_ITEM_COUNT_FAIL")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(yt_search, entries))
    items = [{"id": item.get("id"), "network": item.get("network"),
              "title": item.get("title"), "slot": item.get("slot"),
              **result} for item, result in zip(entries, results)]
    output = {
        "schema": "CENA_CERTA_LEGACY_YTDLP_DISCOVERY_V1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "reference": "Oct12 run 38196309142: source probes -> manifest -> FFmpeg -> media gates -> releases",
        "automatic_download": False, "automatic_approval": False,
        "publishing": False, "scheduled": False, "items": items,
        "candidate_count": sum(len(i["candidates"]) for i in items),
        "rights_verified_count": 0, "masters_count": 0,
        "status": "CANDIDATE_DISCOVERY_NOT_SOURCE_APPROVAL",
    }
    path = OUTPUT / "source-discovery.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Cena Certa — descoberta de fontes (método de 12/10)", "",
             "Fontes encontradas são **candidatas**: não possuem aprovação de direitos nem trechos definidos.",
             "", "| Rede | Filme/série | Resultado | Candidatos |", "|---|---|---|---:|"]
    for x in items:
        lines.append(f'| {x["network"]} | {x["title"].replace("|", "/")} | {x["status"]} | {len(x["candidates"])} |')
    lines += ["", "Próximo passo: validar fonte, licença, segmento, áudio, anti-repeat 60d e render.", ""]
    summary = "\n".join(lines)
    (OUTPUT / "source-discovery.md").write_text(summary, encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(summary)
    print(f'CENA_CERTA_LEGACY_DISCOVERY=PASS candidates={output["candidate_count"]} items={len(items)}')
    print(f"CENA_CERTA_SOURCE_DISCOVERY={path}")


if __name__ == "__main__":
    main()
