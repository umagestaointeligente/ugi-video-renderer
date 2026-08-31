#!/usr/bin/env python3
"""UGI hard anti-repeat gate for queued video publications.

Fail closed before render/Buffer mutation when a queued video is exact or near-
duplicate of recent UGI video command content. The gate compares content, not
CONTENT_ID alone.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "control-plane" / "publisher-hub" / "queue"
COMMANDS = ROOT / "control-plane" / "commands"
OUT = ROOT / "control-plane" / "anti-repeat" / "latest.json"
WINDOW_DAYS = 15
STALE_QUEUE_HOURS = 6


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(payload: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def norm(s: Any) -> str:
    text = str(s or "").lower()
    text = re.sub(r"[^a-z0-9áàâãéêíóôõúç]+", " ", text, flags=re.I)
    return " ".join(text.split())


def content_date(cid: str) -> dt.date | None:
    m = re.search(r"UGI-(20\d{6})", cid)
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
    except Exception:
        return None


def scene_package(command: dict[str, Any]) -> list[dict[str, Any]]:
    pack = command.get("scenes_json") or command.get("scenesJson") or command.get("scenes") or {}
    if isinstance(pack, dict):
        rows = pack.get("scenes") or []
    else:
        rows = pack
    return rows if isinstance(rows, list) else []


def signature(command: dict[str, Any]) -> dict[str, Any]:
    scenes = scene_package(command)
    text_parts = [command.get("title")]
    hooks: list[str] = []
    visuals: list[str] = []
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        ov = sc.get("overlay") or {}
        sup = sc.get("support") or {}
        nar = sc.get("narration") or {}
        for obj in (ov, sup, nar):
            if isinstance(obj, dict):
                for value in obj.values():
                    text_parts.append(value)
        if str(sc.get("role") or "").lower() == "hook":
            if isinstance(ov, dict): hooks.extend(str(v) for v in ov.values())
            if isinstance(nar, dict): hooks.extend(str(v) for v in nar.values())
        visuals.extend([str(sc.get("pexels_query") or ""), str(sc.get("visual_intent") or "")])
    text = norm(" ".join(str(x or "") for x in text_parts))
    hook = norm(" ".join(hooks))
    vis = sorted({norm(v) for v in visuals if norm(v)})
    exact_payload = {
        "title": norm(command.get("title")),
        "scenes": scenes,
        "cta": (command.get("scenes_json") or {}).get("cta") if isinstance(command.get("scenes_json"), dict) else None,
    }
    exact_hash = hashlib.sha256(json.dumps(exact_payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return {
        "text": text,
        "hook": hook,
        "visuals": vis,
        "exactHash": exact_hash,
        "renderId": str(command.get("render_id") or command.get("renderId") or ""),
        "draftId": str(command.get("draft_id") or command.get("draftId") or ""),
    }


def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio() if a and b else 0.0


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def active_queue_ids() -> list[str]:
    now = dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(hours=STALE_QUEUE_HOURS)
    ids: list[str] = []
    seen: set[str] = set()
    for path in sorted(QUEUE.glob("*.json")):
        data = load(path)
        if data.get("project") != "UGI":
            continue
        for row in data.get("posts") or []:
            try:
                due = dt.datetime.fromisoformat(str(row.get("dueAt") or "").replace("Z", "+00:00")).astimezone(dt.timezone.utc)
            except Exception:
                due = now
            if due < cutoff:
                continue
            cid = str(row.get("contentId") or "").strip()
            if cid and cid not in seen:
                seen.add(cid); ids.append(cid)
    return ids


def commands_by_id() -> dict[str, tuple[Path, dict[str, Any]]]:
    out: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in sorted(COMMANDS.glob("*.json")):
        try:
            data = load(path)
        except Exception:
            continue
        cid = str(data.get("content_id") or data.get("contentId") or "").strip()
        if cid:
            out[cid] = (path, data)
    return out


def main() -> int:
    queued = active_queue_ids()
    all_cmd = commands_by_id()
    results: list[dict[str, Any]] = []
    hard_block = False

    for cid in queued:
        if cid not in all_cmd:
            results.append({"contentId": cid, "decision": "ANTI_REPEAT_REVIEW_REQUIRED", "reason": "command_missing"})
            hard_block = True
            continue
        cpath, cmd = all_cmd[cid]
        sig = signature(cmd)
        cdate = content_date(cid) or dt.datetime.now(dt.timezone.utc).date()
        closest: dict[str, Any] | None = None
        decision = "ANTI_REPEAT_PASS"
        reasons: list[str] = []

        for prior_id, (ppath, pcmd) in all_cmd.items():
            if prior_id == cid or prior_id in queued:
                continue
            pdate = content_date(prior_id)
            if pdate and abs((cdate - pdate).days) > WINDOW_DAYS:
                continue
            psig = signature(pcmd)
            text_sim = ratio(sig["text"], psig["text"])
            hook_sim = ratio(sig["hook"], psig["hook"])
            visual_sim = jaccard(sig["visuals"], psig["visuals"])
            score = 0.55 * text_sim + 0.25 * hook_sim + 0.20 * visual_sim
            cand = {
                "priorContentId": prior_id,
                "priorCommand": str(ppath.relative_to(ROOT)),
                "textSimilarity": round(text_sim, 4),
                "hookSimilarity": round(hook_sim, 4),
                "visualSimilarity": round(visual_sim, 4),
                "combinedSimilarity": round(score, 4),
            }
            if closest is None or cand["combinedSimilarity"] > closest["combinedSimilarity"]:
                closest = cand

            exact = sig["exactHash"] == psig["exactHash"] or (sig["renderId"] and sig["renderId"] == psig["renderId"]) or (sig["draftId"] and sig["draftId"] == psig["draftId"])
            near = score >= 0.84 or (text_sim >= 0.90 and hook_sim >= 0.82) or (hook_sim >= 0.92 and visual_sim >= 0.60)
            if exact:
                decision = "ANTI_REPEAT_BLOCK_EXACT"; reasons.append(f"exact_match:{prior_id}"); hard_block = True; break
            if near:
                decision = "ANTI_REPEAT_BLOCK_NEAR"; reasons.append(f"near_match:{prior_id}"); hard_block = True; break

        results.append({
            "contentId": cid,
            "command": str(cpath.relative_to(ROOT)),
            "windowDays": WINDOW_DAYS,
            "decision": decision,
            "reasons": reasons,
            "closest": closest,
            "signature": {"exactHash": sig["exactHash"], "renderId": sig["renderId"], "draftId": sig["draftId"]},
        })

    payload = {
        "project": "UGI",
        "component": "ANTI-REPEAT-GATE",
        "windowDays": WINDOW_DAYS,
        "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "queuedCount": len(queued),
        "blocked": sum(1 for r in results if str(r.get("decision", "")).startswith("ANTI_REPEAT_BLOCK") or r.get("decision") == "ANTI_REPEAT_REVIEW_REQUIRED"),
        "state": "BLOCKED" if hard_block else "PASS",
        "results": results,
    }
    save(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if hard_block else 0

if __name__ == "__main__":
    raise SystemExit(main())
