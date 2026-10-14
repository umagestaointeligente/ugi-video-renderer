#!/usr/bin/env python3
"""2026-10-15 read-only source discovery; does not render, publish or schedule."""
from __future__ import annotations
from pathlib import Path
import json
import cena_certa_oct13_discover as discover

ROOT = Path(__file__).resolve().parents[1]
discover.EDITORIAL = ROOT / "ops/cena-certa-oct15/editorial-metricool-v1.json"
discover.OUTPUT = ROOT / "out/cena-certa-oct15"
discover.CURATED = ROOT / "ops/cena-certa-oct15/source-candidate-leads.json"

def main():
    editorial = json.loads(discover.EDITORIAL.read_text(encoding="utf-8"))
    if editorial.get("date") != "2026-10-15" or editorial.get("metricool_brand_id") != "6809869":
        raise SystemExit("EDITORIAL_BRAND_OR_DATE_MISMATCH")
    if {network: sum(item.get("network") == network for item in editorial.get("items", []))
        for network in ("tiktok", "instagram", "facebook", "youtube")} != {
            "tiktok": 3, "instagram": 3, "facebook": 3, "youtube": 3}:
        raise SystemExit("NETWORK_COUNT_FAIL")
    discover.main()

if __name__ == "__main__":
    main()
