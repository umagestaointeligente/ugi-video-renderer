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
CURATED = ROOT / "ops/cena-certa-oct13/source-candidate-leads.json"
SKIP_WORDS = ("trailer", "teaser", "fan made", "fanmade", "reaction", "review", "analysis", "breakdown", "explained", "recap", "compilation")


def normalize_name(value):
    """Keep exact word/phrase boundaries across English and PT-BR titles."""
    import unicodedata
    ascii_name = unicodedata.normalize("NFKD", str(value or "")).encode(
        "ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_name.casefold()).strip()


def movie_identity(title):
    """2025 approved film/series aliases; never infer identity from 'studio' alone."""
    words = normalize_name(title)
    names = (
        ("corra que a policia vem ai", "the naked gun", "The Naked Gun 2025 Liam Neeson"),
        ("the naked gun", "the naked gun", "The Naked Gun 2025 Liam Neeson"),
        ("um filme minecraft", "a minecraft movie", "A Minecraft Movie 2025"),
        ("a minecraft movie", "a minecraft movie", "A Minecraft Movie 2025"),
        ("the studio", "the studio", "The Studio Seth Rogen 2025 Apple TV"),
        ("o estudio", "the studio", "The Studio Seth Rogen 2025 Apple TV"),
        ("f1 o filme", "f1", "F1 The Movie 2025 Brad Pitt"),
        ("pecadores", "sinners", "Sinners 2025 Warner Bros"),
        ("sinners", "sinners", "Sinners 2025 Warner Bros"),
        ("frankenstein", "frankenstein", "Frankenstein Guillermo del Toro 2025 Netflix"),
        ("adolescencia", "adolescence", "Adolescence 2025 Netflix"),
        ("adolescence", "adolescence", "Adolescence 2025 Netflix"),
        ("the pitt", "the pitt", "The Pitt 2025 HBO Max"),
        ("dna do crime", "dna do crime", "DNA do Crime season 2 Netflix 2025"),
        ("stranger things", "stranger things", "Stranger Things season 5 Netflix"),
        ("andor", "andor", "Andor season 2 Star Wars Disney"),
        ("uma batalha apos a outra", "one battle after another", "One Battle After Another 2025"),
        ("one battle after another", "one battle after another", "One Battle After Another 2025"),
    )
    for match, canonical, query in names:
        if re.search(r"\b" + re.escape(match) + r"\b", words):
            return canonical, query
    return words, str(title)


def search_term(item):
    _canonical, text = movie_identity(item.get("canonical_english") or item.get("title") or "")
    return f"{text} official movie scene clip"


def acceptable_candidate(result, title):
    name = str(result.get("title") or "")
    low = name.casefold()
    if any(x in low for x in SKIP_WORDS) or not result.get("id") or not name or len(name) > 240:
        return False
    candidate = normalize_name(name)
    canonical, _query = movie_identity(title)
    if not canonical:
        return False
    # Exact phrase, not substring: 'the studio' cannot match a music studio,
    # and 'andor' cannot match 'Pandora'.
    names = (canonical, "criminal code") if canonical == "dna do crime" else (canonical,)
    if not any(re.search(r"\b" + re.escape(value) + r"\b", candidate) for value in names):
        return False
    if canonical == "the naked gun" and any(word in candidate for word in ("1988", "1991", "1994", "trilogia", "trilogy")) and "2025" not in candidate:
        return False
    # F1 is an ambiguous sporting acronym; a race recap is not the film.
    if canonical == "f1" and not any(re.search(r"\b" + t + r"\b", candidate)
                                     for t in ("movie", "film", "brad pitt", "film clip", "2025")):
        return False
    return True


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
        bot_gate = "sign in to confirm you" in p.stderr.casefold() and "not a bot" in p.stderr.casefold()
        return {"query": query, "status": "PROBE_AUTH_REQUIRED" if bot_gate else "PROBE_FAILED",
                "error": p.stderr[-450:], "candidates": []}
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
    leads = json.loads(CURATED.read_text(encoding="utf-8")).get("items", []) if CURATED.exists() else []
    valid_ids = {entry.get("id") for entry in entries}
    if any(lead.get("editorial_id") not in valid_ids or
           not str(lead.get("source_url", "")).startswith("https://") or
           lead.get("verified_redistribution_rights") is not False
           for lead in leads):
        raise SystemExit("CURATED_CANDIDATE_INVALID_OR_UNAUTHORIZED")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(yt_search, entries))
    items = [{"id": item.get("id"), "network": item.get("network"),
              "title": item.get("title"), "slot": item.get("slot") or item.get("local_datetime"),
              **result} for item, result in zip(entries, results)]
    for item in items:
        item["curated_publisher_scene_leads"] = [
            {"source_url": lead["source_url"], "publisher": lead.get("publisher"),
             "source_page": lead.get("source_page"),
             "verified_redistribution_rights": False,
             "source_window": None, "status": "PUBLISHER_PAGE_NOT_REUSE_APPROVAL"}
            for lead in leads if lead.get("editorial_id") == item["id"]
        ]
    output = {
        "schema": "CENA_CERTA_LEGACY_YTDLP_DISCOVERY_V1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "reference": "Oct12 run 38196309142: source probes -> manifest -> FFmpeg -> media gates -> releases",
        "automatic_download": False, "automatic_approval": False,
        "publishing": False, "scheduled": False, "items": items,
        "candidate_count": sum(len(i["candidates"]) + len(i["curated_publisher_scene_leads"]) for i in items),
        "rights_verified_count": 0, "masters_count": 0,
        "status": "CANDIDATE_DISCOVERY_NOT_SOURCE_APPROVAL",
    }
    path = OUTPUT / "source-discovery.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Cena Certa — descoberta de fontes (método de 12/10)", "",
             "Fontes encontradas são **candidatas**: não possuem aprovação de direitos nem trechos definidos.",
             "", "| Rede | Filme/série | Resultado | Candidatos |", "|---|---|---|---:|"]
    for x in items:
        lines.append(f'| {x["network"]} | {x["title"].replace("|", "/")} | {x["status"]} | {len(x["candidates"]) + len(x["curated_publisher_scene_leads"])} |')
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
