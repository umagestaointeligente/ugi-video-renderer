#!/usr/bin/env python3
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import os
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict

API_BASE = "https://x402-list.com/api/v1/services"
USER_AGENT = "LSI-x402-Deep-Market-Scan/1.0 (+public-market-research)"
MAX_REQUESTS_PER_SECOND = 2.8
CONCURRENCY = 6
TIMEOUT = 25
WINDOW = 30

_rate_lock = threading.Lock()
_last_request = 0.0


def rate_wait():
    global _last_request
    min_gap = 1.0 / MAX_REQUESTS_PER_SECOND
    with _rate_lock:
        now = time.monotonic()
        wait = min_gap - (now - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.monotonic()


def fetch_json(url):
    rate_wait()
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def num(v, default=0.0):
    try:
        x = float(v)
        return x if math.isfinite(x) else default
    except Exception:
        return default


def last_n(rows, count=WINDOW):
    return (rows if isinstance(rows, list) else [])[-count:]


def metric_from_series(meta, buyers_payload, volume_payload):
    buyers = last_n((buyers_payload or {}).get("data"))
    volumes = last_n((volume_payload or {}).get("data"))
    buyer_days = sum(num(x.get("unique_buyers")) for x in buyers)
    active_buyer_days = sum(1 for x in buyers if num(x.get("unique_buyers")) > 0)
    peak_daily_buyers = max([num(x.get("unique_buyers")) for x in buyers] or [0])
    tx_count = sum(num(x.get("tx_count")) for x in volumes)
    volume_usd = sum(num(x.get("volume_usd")) for x in volumes)
    active_volume_days = sum(1 for x in volumes if num(x.get("tx_count")) > 0)
    tx_per_buyer_day = tx_count / buyer_days if buyer_days else 0
    price = num(meta.get("min_price_usd"), 0)
    text = " ".join(str(meta.get(k) or "") for k in ("name", "description", "category")).lower()
    upstream_risk = any(k in text for k in ("search", "scrap", "crawl", "video", "image", "llm", "openai", "anthropic", "exa", "serp", "maps", "geocod", "weather"))

    def log_score(v, scale, cap):
        return min(cap, math.log1p(v) * scale) if v > 0 else 0

    score = 0
    score += log_score(buyer_days, 5.4, 30)
    score += log_score(tx_count, 3.1, 24)
    score += min(15, active_buyer_days / WINDOW * 15)
    score += log_score(volume_usd, 2.4, 10)
    score += log_score(tx_per_buyer_day, 3.6, 12)
    score += 5 if 0 < price <= 0.05 else 3 if price <= 0.25 else 1
    if upstream_risk:
        score -= 5
    score = round(max(0, min(100, score)), 1)

    fingerprint_payload = {
        "buyers": [[x.get("date"), x.get("unique_buyers")] for x in buyers],
        "volume": [[x.get("date"), x.get("volume_usd"), x.get("tx_count")] for x in volumes],
    }
    fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    return {
        "slug": str(meta.get("slug") or "")[:160],
        "name": str(meta.get("name") or meta.get("slug") or "")[:240],
        "category": str(meta.get("category") or "Other")[:100],
        "description": str(meta.get("description") or "")[:700],
        "payment_ready": bool(meta.get("payment_ready")),
        "min_price_usd": price if price > 0 else None,
        "endpoint_count": int(num(meta.get("endpoint_count"), 0)),
        "uptime_24h": num(meta.get("uptime_24h"), 0),
        "buyer_days_30d": int(buyer_days),
        "active_buyer_days_30d": active_buyer_days,
        "peak_daily_buyers_30d": int(peak_daily_buyers),
        "tx_count_30d": int(tx_count),
        "volume_usd_30d": round(volume_usd, 6),
        "active_volume_days_30d": active_volume_days,
        "tx_per_buyer_day_30d": round(tx_per_buyer_day, 3),
        "demand_score": score,
        "upstream_paid_dependency_risk": upstream_risk,
        "series_fingerprint": fingerprint,
        "source_url": f"https://x402-list.com/services/{urllib.parse.quote(str(meta.get('slug') or ''))}",
    }


def fetch_catalog():
    first = fetch_json(f"{API_BASE}?status=online&per_page=100&page=1")
    pages = min(int(num((first.get("meta") or {}).get("total_pages"), 1)), 20)
    rows = list(first.get("data") or [])
    for page in range(2, pages + 1):
        payload = fetch_json(f"{API_BASE}?status=online&per_page=100&page={page}")
        rows.extend(payload.get("data") or [])
    unique = {}
    for row in rows:
        slug = str(row.get("slug") or "")
        if slug:
            unique[slug] = row
    return list(unique.values()), first.get("meta") or {}, first.get("provenance") or {}


def fetch_one(meta):
    slug = str(meta.get("slug") or "")
    try:
        b = fetch_json(f"{API_BASE}/{urllib.parse.quote(slug)}/buyers")
        v = fetch_json(f"{API_BASE}/{urllib.parse.quote(slug)}/volume")
        return metric_from_series(meta, b, v), None
    except Exception as e:
        return None, f"{slug}:{type(e).__name__}:{str(e)[:180]}"


def cluster_rows(rows):
    clusters = defaultdict(list)
    for row in rows:
        clusters[row["series_fingerprint"]].append(row)
    out = []
    for fp, members in clusters.items():
        ordered = sorted(members, key=lambda x: (x["demand_score"], x["tx_count_30d"], x["volume_usd_30d"]), reverse=True)
        rep = dict(ordered[0])
        rep["cluster_size"] = len(members)
        rep["cluster_slugs"] = [m["slug"] for m in ordered[:50]]
        rep["cluster_categories"] = sorted(set(m["category"] for m in members))
        rep["shared_series_warning"] = len(members) > 1
        out.append(rep)
    return sorted(out, key=lambda x: (x["demand_score"], x["tx_count_30d"], x["volume_usd_30d"]), reverse=True)


def category_summary(clusters):
    data = defaultdict(lambda: {"unique_clusters": 0, "clusters_with_activity": 0, "buyer_days_30d": 0, "tx_count_30d": 0, "volume_usd_30d": 0.0})
    for c in clusters:
        cat = c.get("category") or "Other"
        d = data[cat]
        d["unique_clusters"] += 1
        if c["tx_count_30d"] > 0:
            d["clusters_with_activity"] += 1
        d["buyer_days_30d"] += c["buyer_days_30d"]
        d["tx_count_30d"] += c["tx_count_30d"]
        d["volume_usd_30d"] += c["volume_usd_30d"]
    result = []
    for cat, d in data.items():
        result.append({"category": cat, **d, "volume_usd_30d": round(d["volume_usd_30d"], 6)})
    return sorted(result, key=lambda x: (x["tx_count_30d"], x["buyer_days_30d"]), reverse=True)


def main():
    started = time.time()
    catalog, meta, provenance = fetch_catalog()
    print(f"CATALOG={len(catalog)}", flush=True)
    rows, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = [pool.submit(fetch_one, m) for m in catalog]
        for idx, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            row, err = fut.result()
            if row:
                rows.append(row)
            if err:
                errors.append(err)
            if idx % 50 == 0:
                print(f"PROGRESS={idx}/{len(catalog)} success={len(rows)} errors={len(errors)}", flush=True)

    clusters = cluster_rows(rows)
    active_clusters = [c for c in clusters if c["tx_count_30d"] > 0 and c["buyer_days_30d"] > 0]
    duplicate_members = sum(max(0, c["cluster_size"] - 1) for c in clusters)
    output = {
        "schema_version": "1.0",
        "project": "LSI_X402_DEEP_MARKET_SCAN",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "x402-list.com public API",
        "attribution": "Data: x402-list.com (CC BY 4.0)",
        "methodology": {
            "window": "last 30 rows from daily /buyers and /volume series",
            "buyer_metric": "buyer_days_30d",
            "buyer_warning": "buyer-days are summed daily distinct buyers, NOT 30-day unique buyers",
            "deduplication": "identical 30-day buyers+volume series are clustered by SHA-256 fingerprint; cluster metrics are never summed across identical series",
            "monetary_budget": 0,
            "production_actions": False,
            "money_movement": False,
        },
        "market": {
            "catalog_services": len(catalog),
            "series_success": len(rows),
            "series_errors": len(errors),
            "unique_series_clusters": len(clusters),
            "duplicate_series_members": duplicate_members,
            "active_unique_clusters": len(active_clusters),
            "elapsed_seconds": round(time.time() - started, 2),
            "source_meta": meta,
            "provenance": provenance,
        },
        "top_unique_demand": active_clusters[:75],
        "category_summary_unique_clusters": category_summary(clusters)[:50],
        "sample_errors": errors[:30],
    }
    os.makedirs("generated/evidence", exist_ok=True)
    out_path = "generated/evidence/lsi-x402-deep-market-scan.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(json.dumps({
        "ok": True,
        "catalog": len(catalog),
        "success": len(rows),
        "clusters": len(clusters),
        "active_clusters": len(active_clusters),
        "duplicate_members": duplicate_members,
        "top": [{"name": x["name"], "score": x["demand_score"], "tx": x["tx_count_30d"], "buyer_days": x["buyer_days_30d"], "cluster_size": x["cluster_size"]} for x in active_clusters[:10]],
    }, ensure_ascii=False), flush=True)
    if len(rows) < max(50, int(len(catalog) * 0.75)):
        raise SystemExit("insufficient_series_coverage")
    if not active_clusters:
        raise SystemExit("no_active_clusters")


if __name__ == "__main__":
    main()
