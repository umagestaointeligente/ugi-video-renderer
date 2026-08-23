#!/usr/bin/env python3
from __future__ import annotations
import json, os, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)
KEY = (os.getenv("OPENROUTER_API_KEY") or "").strip()
BASE = "https://openrouter.ai/api/v1"
MAX_MODELS = int(os.getenv("MAGIC_COUNCIL_MAX_MODELS") or "3")


def req(url: str, method="GET", body=None):
    headers = {"User-Agent": "LolaMagicEngine/1.0", "Content-Type": "application/json"}
    if KEY:
        headers["Authorization"] = f"Bearer {KEY}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode())


def is_zero_price(model: dict) -> bool:
    p = model.get("pricing") or {}
    try:
        vals = [float(p.get(k) or 0) for k in ("prompt","completion","request","image","web_search")]
    except Exception:
        return False
    return all(v == 0 for v in vals)


def choose_free_models() -> list[str]:
    data = req(f"{BASE}/models")
    models = [m for m in data.get("data", []) if is_zero_price(m) and m.get("id")]
    # Favor useful text models while keeping provider/model diversity when available.
    scored=[]
    for m in models:
        mid=m["id"]
        ctx=int(m.get("context_length") or 0)
        name=(m.get("name") or mid).lower()
        score=min(ctx, 200000)
        for word in ("deepseek","qwen","gemini","llama","mistral","nemotron"):
            if word in name or word in mid.lower(): score += 50000
        scored.append((score, mid))
    scored.sort(reverse=True)
    picked=[]; providers=set()
    for _, mid in scored:
        provider=mid.split("/",1)[0]
        if provider in providers and len(scored) > MAX_MODELS: continue
        picked.append(mid); providers.add(provider)
        if len(picked) >= MAX_MODELS: break
    return picked


def ask(model: str, prompt: str) -> dict:
    body={
        "model": model,
        "messages": [
            {"role":"system","content":"You are one independent member of a decision council for an autonomous media business. Be concise, evidence-minded, challenge assumptions, flag legal/platform/monetization risks, and propose actionable improvements. Do not claim facts you cannot support."},
            {"role":"user","content": prompt},
        ],
        "temperature": 0.35,
        "max_tokens": 650,
    }
    data=req(f"{BASE}/chat/completions", method="POST", body=body)
    choice=(data.get("choices") or [{}])[0]
    text=((choice.get("message") or {}).get("content") or "").strip()
    usage=data.get("usage") or {}
    return {"model":model,"text":text,"usage":usage,"reported_cost":usage.get("cost",0)}


def main():
    now=datetime.now(timezone.utc).isoformat()
    if not KEY:
        result={"status":"HARD_STOP_NO_OPENROUTER_KEY","generated_at":now,"cost_gate":"PASS","calls":0}
        (OUT/"multi-ai-council-latest.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print("MULTI_AI_COUNCIL=HARD_STOP_NO_OPENROUTER_KEY")
        return 0

    plan_path=OUT/"latest.json"
    if not plan_path.exists():
        print("MULTI_AI_COUNCIL=SKIP_NO_PLAN")
        return 0
    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    proposals=(plan.get("proposals") or [])[:5]
    if not proposals:
        print("MULTI_AI_COUNCIL=SKIP_NO_PROPOSALS")
        return 0

    models=choose_free_models()
    if not models:
        result={"status":"HARD_STOP_NO_ZERO_COST_MODELS","generated_at":now,"cost_gate":"FAIL","calls":0}
        (OUT/"multi-ai-council-latest.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print("MULTI_AI_COUNCIL=HARD_STOP_NO_ZERO_COST_MODELS")
        return 0

    prompt=("Review these top Lola Magic Engine opportunities and recommend: (1) best item to produce now, "
            "(2) hook/format, (3) monetization angle, (4) rights/fact risk, (5) one reason NOT to publish. "
            "Return compact JSON-like prose. Opportunities:\n" + json.dumps(proposals,ensure_ascii=False))
    opinions=[]
    for model in models:
        try:
            opinions.append(ask(model,prompt))
        except Exception as e:
            opinions.append({"model":model,"error":str(e)[:300],"reported_cost":0})

    any_cost=False
    for x in opinions:
        try:
            if float(x.get("reported_cost") or 0) > 0: any_cost=True
        except Exception: pass
    result={
        "status":"PASS" if not any_cost else "HARD_STOP_COST_DETECTED",
        "generated_at":now,
        "cost_gate":"PASS" if not any_cost else "FAIL",
        "selected_zero_cost_models":models,
        "calls":len(opinions),
        "opinions":opinions,
        "note":"Council is advisory only. It cannot bypass RIGHTS/FACT/QA/COST gates or publish directly."
    }
    (OUT/"multi-ai-council-latest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"MULTI_AI_COUNCIL={result['status']} models={len(models)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
