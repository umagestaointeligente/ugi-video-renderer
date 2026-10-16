#!/usr/bin/env python3
"""Daily editorial source *research only* for Oct 16. No media ingestion or publication."""
from __future__ import annotations

import json
import pathlib
import re
import cena_certa_oct13_discover as discovery

ROOT = pathlib.Path(__file__).resolve().parents[1]
EDITORIAL = ROOT / "ops/cena-certa-oct16/editorial-v1.json"
OUT = ROOT / "out/cena-certa-oct16/source-discovery"
NETWORKS = {"tiktok": 3, "instagram": 3, "facebook": 3, "youtube": 3}


def validate_editorial(doc):
    if doc.get("publication_date") != "2026-10-16" or doc.get("metricool_brand_id") != 6809869:
        raise ValueError("DATE_OR_BRAND_SCOPE_FAIL")
    if doc.get("timezone") != "America/Sao_Paulo" or len(doc.get("items") or []) != 12:
        raise ValueError("ZONE_OR_ITEM_COUNT_FAIL")
    seen = set()
    counts = {}
    for item in doc["items"]:
        network = item.get("network")
        counts[network] = counts.get(network, 0) + 1
        ident = item.get("id")
        slot = item.get("slot")
        if not re.fullmatch(r"CC-OCT16-(TIKTOK|INSTAGRAM|FACEBOOK|YOUTUBE)-[0-9]{2}", str(ident)):
            raise ValueError("ITEM_ID_INVALID")
        if not re.fullmatch(r"2026-10-16T[0-9]{2}:[0-9]{2}:00-03:00", str(slot)):
            raise ValueError("SLOT_INVALID")
        if ident in seen or (network, slot) in seen:
            raise ValueError("DUPLICATE_ITEM_OR_SLOT")
        seen.add(ident)
        seen.add((network,slot))
        if item.get("source_url") or item.get("master_mp4_url") or item.get("metricool_status") != "NOT_SCHEDULED":
            raise ValueError("SOURCE_DISCOVERY_MUST_NOT_CONFLATE_MEDIA_RELEASE")
        if item.get("rights_evidence", {}).get("status") == "VERIFIED":
            raise ValueError("UNREVIEWED_RIGHTS_MARKED_VERIFIED")
        if network == "youtube" and item.get("distributor") == "Globo":
            raise ValueError("YOUTUBE_GLOBO_FORBIDDEN")
    if counts != NETWORKS:
        raise ValueError("NETWORK_COUNTS_INVALID")
    return True


def search_term(item):
    # The legacy October 13 lookup was tailored to 2025 titles; include the
    # correct title/year for this batch rather than searching every film as 2025.
    title = item.get("canonical_english") or item.get("title", "")
    year = item.get("year", "")
    if not title or not 1990 <= int(year) <= 2026:
        raise ValueError("TITLE_OR_YEAR_INVALID")
    return f"{title} {year} official scene clip"


def main():
    doc = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    validate_editorial(doc)
    discovery.EDITORIAL = EDITORIAL
    discovery.OUTPUT = OUT
    discovery.CURATED = ROOT / "ops/cena-certa-oct16/source-candidate-leads.json"
    discovery.search_term = search_term
    discovery.main()


if __name__ == "__main__":
    main()
