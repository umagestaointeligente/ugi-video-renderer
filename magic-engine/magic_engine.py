#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, re, sys, time, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
GROWTH_POLICY_PATH = REPO_ROOT / "config" / "ugi" / "growth-policy.json"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 LolaMagicEngine/1.1"


def load_growth_policy() -> tuple[dict, str]:
    if not GROWTH_POLICY_PATH.exists():
        raise RuntimeError(f"growth policy missing: {GROWTH_POLICY_PATH}")
    raw = GROWTH_POLICY_PATH.read_bytes()
    policy = json.loads(raw.decode("utf-8"))
    required = ["schema_version", "policy_id", "north_star", "optimization_priority", "platform_independence", "creative_novelty", "commerce_gate", "experiment_loop"]
    missing = [k for k in required if k not in policy]
    if missing:
        raise RuntimeError(f"growth policy invalid; missing={missing}")
    if policy.get("policy_id") != "ugi-growth-engine":
        raise RuntimeError("unexpected growth policy id")
    return policy, hashlib.sha256(raw).hexdigest()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def google_trends(geo: str) -> list[dict]:
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    root = ET.fromstring(fetch(url))
    items=[]
    for idx, item in enumerate(root.findall(".//item"), start=1):
        title=(item.findtext("title") or "").strip()
        pub=(item.findtext("pubDate") or "").strip()
        if title:
            items.append({"title": title, "geo": geo, "position": idx, "published": pub, "source": "google_trends_rss"})
    return items


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()


def contains_any(text: str, kws: list[str]) -> bool:
    t=norm(text)
    return any(norm(k) in t for k in kws)


def classify(title: str) -> str:
    if contains_any(title, CONFIG["sports_keywords"]): return "universo_esportes"
    if contains_any(title, CONFIG["podcast_keywords"]): return "podcast_intelligence"
    if contains_any(title, CONFIG["cinema_keywords"]): return "cinema_transformativo"
    return "curiosidades"


def audience_fit_score(title: str, channel: str) -> int:
    t = norm(title)
    keyword_sets = {
        "curiosidades": CONFIG["curiosity_keywords"],
        "cinema_transformativo": CONFIG["cinema_keywords"],
        "universo_esportes": CONFIG["sports_keywords"],
        "podcast_intelligence": CONFIG["podcast_keywords"],
        "sleep_focus": ["sleep", "sono", "relax", "focus", "foco", "noise", "rain", "chuva"]
    }
    kws = keyword_sets.get(channel, [])
    if contains_any(t, kws): return 92
    if len(t.split()) >= 4: return 72
    return 60


def trend_score(item: dict, cross_geo_count: int) -> int:
    channel=classify(item["title"])
    position=max(0, 100 - (item["position"]-1)*4)
    kw=85 if channel != "curiosidades" else 70
    freshness=90
    cross=min(100, 55 + 22*max(0, cross_geo_count-1))
    audience=audience_fit_score(item["title"], channel)
    w=CONFIG["scoring"]["trend"]
    return round(position*w["position"] + kw*w["keyword_match"] + freshness*w["freshness"] + cross*w["cross_geo"] + audience*w.get("audience_fit",0))


def visual_strength_score(title: str, channel: str) -> int:
    strong=["vulcao","vulcão","space","espaço","explosion","explosão","record","recorde","final","movie","filme","nba","f1","ufc"]
    if contains_any(title,strong): return 90
    if channel in {"cinema_transformativo","universo_esportes"}: return 82
    return 70


def virality_score(title: str, channel: str) -> int:
    t=norm(title)
    curiosity_words=["why","por que","como","misterio","mistério","mystery","segredo","descoberta","revealed","surpreendente","incrivel","incrível"]
    urgency_words=["hoje","today","agora","now","final","breaking","novo","new"]
    emotion_words=["chocante","shocking","incrivel","incrível","amazing","historic","historico","histórico","recorde","record"]
    curiosity=85 if contains_any(t, curiosity_words) else 62
    urgency=82 if contains_any(t, urgency_words) else 58
    specificity=78 if re.search(r"\d", t) or len(t.split()) >= 4 else 60
    emotion=82 if contains_any(t, emotion_words) else 60
    series=88 if channel in {"cinema_transformativo","podcast_intelligence","universo_esportes"} else 72
    visual=visual_strength_score(title,channel)
    w=CONFIG["scoring"]["virality"]
    return round(curiosity*w["curiosity"] + urgency*w["urgency"] + specificity*w["specificity"] + emotion*w["emotion"] + series*w["series_potential"] + visual*w.get("visual_strength",0))


def rights_gate(channel: str) -> tuple[str,str]:
    if channel in {"curiosidades","sleep_focus"}:
        return "GREEN", "Use only original, public-domain or separately verified commercial-license assets."
    if channel == "universo_esportes":
        return "YELLOW", "Analysis may proceed, but broadcast footage/reuploads are blocked until a lawful rights basis is recorded."
    if channel == "podcast_intelligence":
        return "YELLOW", "Requires creator permission/license or separately reviewed materially transformative basis before publication."
    return "YELLOW", "Cinema topic may proceed only as original commentary/analysis; raw film/TV clip publication requires documented lawful rights basis."


def build_plan(items: list[dict], growth_policy: dict, growth_policy_sha256: str) -> dict:
    counts={}
    for i in items:
        counts[norm(i["title"])]=counts.get(norm(i["title"]),0)+1
    proposals=[]
    channel_counts={k:0 for k in CONFIG["channels"]}
    for i in items:
        ch=classify(i["title"])
        c=CONFIG["channels"][ch]
        if not c["enabled"] or channel_counts[ch] >= c["max_per_run"]: continue
        ts=trend_score(i, counts[norm(i["title"])])
        vs=virality_score(i["title"], ch)
        if ts < CONFIG["scan"]["min_trend_score"] or vs < CONFIG["scan"]["min_virality_score"]: continue
        gate, note=rights_gate(ch)
        proposals.append({
            "channel": ch,
            "public_name": c.get("public_name",ch),
            "topic": i["title"], "geo": i["geo"],
            "trend_score": ts, "virality_score": vs,
            "rights_gate": gate, "rights_note": note,
            "fact_gate": "PENDING", "qa_gate": "PENDING", "cost_gate": "PASS",
            "thumbnail_semantic_match": "PENDING",
            "thumbnail_policy": CONFIG.get("thumbnail_policy",{}),
            "platform_auth": "PENDING", "platforms": c["platforms"], "format": c["format"],
            "publish_ready": False, "source": i["source"],
            "status": "RESEARCH_REQUIRED"
        })
        channel_counts[ch]+=1
    proposals.sort(key=lambda x:(x["trend_score"]+x["virality_score"]), reverse=True)
    return {
        "engine": CONFIG["engine"], "version": CONFIG["version"],
        "brand": CONFIG.get("brand"),
        "generated_at": datetime.now(timezone.utc).isoformat(), "autonomous": True, "paid_fallback": False,
        "growth_policy": {
            "loaded": True,
            "path": "config/ugi/growth-policy.json",
            "policy_id": growth_policy["policy_id"],
            "schema_version": growth_policy["schema_version"],
            "sha256": growth_policy_sha256,
            "north_star": growth_policy["north_star"],
            "optimization_priority": growth_policy["optimization_priority"],
            "platform_independence": growth_policy["platform_independence"],
            "creative_novelty": growth_policy["creative_novelty"],
            "commerce_gate": growth_policy["commerce_gate"],
            "experiment_loop": growth_policy["experiment_loop"]
        },
        "proposals": proposals,
        "summary": {"total": len(proposals), "green": sum(p["rights_gate"]=="GREEN" for p in proposals), "yellow": sum(p["rights_gate"]=="YELLOW" for p in proposals), "red": sum(p["rights_gate"]=="RED" for p in proposals)}
    }


def main() -> int:
    growth_policy, growth_policy_sha256 = load_growth_policy()
    print(f"GROWTH_POLICY_LOADED=true policy_id={growth_policy['policy_id']} sha256={growth_policy_sha256}")
    all_items=[]; errors=[]
    for geo in CONFIG["scan"]["geos"]:
        try: all_items.extend(google_trends(geo)[:CONFIG["scan"]["max_topics_per_geo"]])
        except Exception as e: errors.append({"geo":geo,"error":str(e)})
    plan=build_plan(all_items, growth_policy, growth_policy_sha256)
    plan["discovery_errors"]=errors
    rid=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path=OUT / f"magic-plan-{rid}.json"
    path.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT / "latest.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(plan["summary"], ensure_ascii=False)); print(f"MAGIC_PLAN={path}")
    return 0 if all_items else 2

if __name__ == "__main__": raise SystemExit(main())
