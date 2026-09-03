#!/usr/bin/env python3
"""UGI hard anti-repeat gate.

Two independent protections run before render/Buffer mutation:
1) exact / near media-command duplicate detection;
2) same-platform editorial topic cooldown (15 days), including Instagram Stories.

The topic-history registry is durable but not treated as the sole source of truth;
Control Plane workflows must backfill/reconcile it with publisher receipts/manifests.
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
TOPIC_HISTORY = ROOT / "control-plane" / "anti-repeat" / "platform-topic-history.json"
WINDOW_DAYS = 15
STALE_QUEUE_HOURS = 6
EXCEPTION_STATE = "EDITORIAL_REPEAT_EXCEPTION_BREAKING"

STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas",
    "um", "uma", "para", "por", "com", "sem", "que", "se", "ao", "aos", "à", "às", "mais", "menos",
    "sua", "seu", "suas", "seus", "como", "quando", "onde", "porque", "porquê", "isso", "essa", "esse",
    "esta", "este", "já", "não", "sim", "ugi", "gestão", "gestao", "inteligente", "story", "reel", "short",
    "video", "vídeo", "instagram", "tiktok", "youtube",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(payload: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def norm(s: Any) -> str:
    text = str(s or "").lower()
    text = re.sub(r"[^a-z0-9áàâãéêíóôõúç]+", " ", text, flags=re.I)
    return " ".join(text.split())


def tokens(s: Any) -> set[str]:
    return {x for x in norm(s).split() if len(x) >= 3 and x not in STOPWORDS}


def content_date(cid: str) -> dt.date | None:
    m = re.search(r"UGI-(20\d{6})", cid)
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
    except Exception:
        return None


def parse_date(value: Any) -> dt.date | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return dt.date.fromisoformat(raw[:10])
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
            if isinstance(ov, dict):
                hooks.extend(str(v) for v in ov.values())
            if isinstance(nar, dict):
                hooks.extend(str(v) for v in nar.values())
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


def jaccard(a: list[str] | set[str], b: list[str] | set[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def infer_platform(cid: str, command: dict[str, Any]) -> str:
    explicit = norm(
        command.get("platform")
        or command.get("network")
        or command.get("smoke_test_platform")
        or command.get("smokeTestPlatform")
    )
    aliases = {
        "ig": "instagram", "instagram": "instagram",
        "tt": "tiktok", "tiktok": "tiktok",
        "yt": "youtube", "youtube": "youtube",
        "li": "linkedin", "linkedin": "linkedin",
    }
    if explicit in aliases:
        return aliases[explicit]
    upper = cid.upper()
    for marker, platform in (("-IG-", "instagram"), ("-TT-", "tiktok"), ("-YT-", "youtube"), ("-LI-", "linkedin")):
        if marker in upper:
            return platform
    return "unknown"


def command_topic_text(command: dict[str, Any]) -> str:
    fields: list[Any] = [
        command.get("topic_key"), command.get("topicKey"), command.get("topic"), command.get("area"),
        command.get("event_or_case"), command.get("eventOrCase"), command.get("management_thesis"),
        command.get("managementThesis"), command.get("angle"), command.get("title"),
    ]
    scenes = scene_package(command)
    for sc in scenes:
        if not isinstance(sc, dict) or str(sc.get("role") or "").lower() != "hook":
            continue
        for key in ("overlay", "support", "narration"):
            obj = sc.get(key)
            if isinstance(obj, dict):
                fields.extend(obj.values())
    return norm(" ".join(str(x or "") for x in fields))


def command_topic_key(command: dict[str, Any]) -> str:
    return norm(command.get("topic_key") or command.get("topicKey") or command.get("topic") or command.get("title"))


def history_topic_text(row: dict[str, Any]) -> str:
    return norm(" ".join([
        str(row.get("topicKey") or ""),
        " ".join(str(x) for x in (row.get("primaryEntities") or [])),
        str(row.get("eventOrCase") or ""),
        str(row.get("managementThesis") or ""),
    ]))


def valid_breaking_exception(command: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    raw = command.get("repeat_exception") or command.get("repeatException") or {}
    if not isinstance(raw, dict):
        return False, {}
    if str(raw.get("state") or "") != EXCEPTION_STATE:
        return False, raw
    dims = raw.get("materiallyDifferentDimensions") or raw.get("differentDimensions") or []
    valid = bool(
        raw.get("priorContentId")
        and raw.get("newEventAt")
        and raw.get("rationale")
        and isinstance(dims, list)
        and len(set(str(x) for x in dims if str(x).strip())) >= 3
    )
    return valid, raw


def topic_history_decision(
    cid: str,
    command: dict[str, Any],
    history: dict[str, Any],
) -> tuple[str, list[str], list[dict[str, Any]]]:
    platform = infer_platform(cid, command)
    cdate = content_date(cid) or dt.datetime.now(dt.timezone.utc).date()
    ctext = command_topic_text(command)
    ckey = command_topic_key(command)
    ctokens = tokens(ctext)
    matches: list[dict[str, Any]] = []
    reasons: list[str] = []

    if platform == "unknown":
        return "ANTI_REPEAT_HISTORY_REVIEW_REQUIRED", ["platform_unknown"], []

    # Structured unresolved risks block fail-closed until backfilled.
    for risk in history.get("unresolvedRisks") or []:
        if not isinstance(risk, dict):
            continue
        entity = norm(risk.get("entity"))
        risk_platform = norm(risk.get("platform") or "unknown")
        if entity and entity in ctext and risk_platform in {"unknown", platform}:
            return "ANTI_REPEAT_HISTORY_REVIEW_REQUIRED", [f"unresolved_history:{entity}"], [risk]

    for row in history.get("entries") or []:
        if not isinstance(row, dict) or not row.get("cooldownEligible"):
            continue
        if norm(row.get("platform")) != platform:
            continue

        prior_ids = row.get("contentIds") or ([row.get("contentId")] if row.get("contentId") else [])
        # Idempotent reconciliation: a durable history record for the exact same
        # CONTENT_ID must not block its own later Publisher Hub readback/retry.
        if cid and cid in {str(x) for x in prior_ids if x}:
            continue

        prior_date = parse_date(row.get("audienceDate") or row.get("dueAt") or row.get("publishedAt"))
        if prior_date is None:
            continue
        age = (cdate - prior_date).days
        if age < 0 or age > WINDOW_DAYS:
            continue

        hkey = norm(row.get("topicKey"))
        htext = history_topic_text(row)
        htokens = tokens(htext)
        shared = ctokens & htokens
        jac = jaccard(ctokens, htokens)
        entity_hits = []
        for entity in row.get("primaryEntities") or []:
            en = norm(entity)
            if en and en in ctext:
                entity_hits.append(str(entity))

        exact_key = bool(ckey and hkey and ckey == hkey)
        semantic_topic = jac >= 0.34
        entity_cluster = bool(entity_hits) and len(shared) >= 2 and jac >= 0.10
        if exact_key or semantic_topic or entity_cluster:
            matches.append({
                "priorTopicKey": row.get("topicKey"),
                "priorContentIds": prior_ids,
                "priorDate": prior_date.isoformat(),
                "ageDays": age,
                "entityHits": entity_hits,
                "sharedTopicTokens": sorted(shared),
                "topicJaccard": round(jac, 4),
                "evidenceRef": row.get("evidenceRef"),
            })

    if not matches:
        return "ANTI_REPEAT_PASS", [], []

    exc_valid, exc = valid_breaking_exception(command)
    if exc_valid:
        reasons.append(f"breaking_exception:{exc.get('priorContentId')}")
        return EXCEPTION_STATE, reasons, matches

    reasons.extend(f"same_platform_topic_15d:{m.get('priorTopicKey')}" for m in matches)
    return "ANTI_REPEAT_BLOCK_TOPIC_15D", reasons, matches


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
                seen.add(cid)
                ids.append(cid)
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

    if not TOPIC_HISTORY.exists():
        payload = {
            "project": "UGI",
            "component": "ANTI-REPEAT-GATE",
            "windowDays": WINDOW_DAYS,
            "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
            "queuedCount": len(queued),
            "blocked": len(queued) or 1,
            "state": "BLOCKED",
            "results": [{"decision": "ANTI_REPEAT_HISTORY_REVIEW_REQUIRED", "reason": "platform_topic_history_missing"}],
        }
        save(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    try:
        history = load(TOPIC_HISTORY)
    except Exception as exc:
        payload = {
            "project": "UGI",
            "component": "ANTI-REPEAT-GATE",
            "windowDays": WINDOW_DAYS,
            "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
            "queuedCount": len(queued),
            "blocked": len(queued) or 1,
            "state": "BLOCKED",
            "results": [{"decision": "ANTI_REPEAT_HISTORY_REVIEW_REQUIRED", "reason": f"platform_topic_history_invalid:{exc}"}],
        }
        save(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    for cid in queued:
        if cid not in all_cmd:
            results.append({"contentId": cid, "decision": "ANTI_REPEAT_REVIEW_REQUIRED", "reason": "command_missing"})
            hard_block = True
            continue

        cpath, cmd = all_cmd[cid]
        sig = signature(cmd)
        platform = infer_platform(cid, cmd)
        cdate = content_date(cid) or dt.datetime.now(dt.timezone.utc).date()
        closest: dict[str, Any] | None = None
        media_decision = "ANTI_REPEAT_PASS"
        media_reasons: list[str] = []

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

            exact = (
                sig["exactHash"] == psig["exactHash"]
                or (sig["renderId"] and sig["renderId"] == psig["renderId"])
                or (sig["draftId"] and sig["draftId"] == psig["draftId"])
            )
            near = score >= 0.84 or (text_sim >= 0.90 and hook_sim >= 0.82) or (hook_sim >= 0.92 and visual_sim >= 0.60)
            if exact:
                media_decision = "ANTI_REPEAT_BLOCK_EXACT"
                media_reasons.append(f"exact_match:{prior_id}")
                break
            if near:
                media_decision = "ANTI_REPEAT_BLOCK_NEAR"
                media_reasons.append(f"near_match:{prior_id}")
                break

        topic_decision, topic_reasons, topic_matches = topic_history_decision(cid, cmd, history)

        if media_decision != "ANTI_REPEAT_PASS":
            decision = media_decision
            reasons = media_reasons
        elif topic_decision in {"ANTI_REPEAT_BLOCK_TOPIC_15D", "ANTI_REPEAT_HISTORY_REVIEW_REQUIRED"}:
            decision = topic_decision
            reasons = topic_reasons
        elif topic_decision == EXCEPTION_STATE:
            decision = EXCEPTION_STATE
            reasons = topic_reasons
        else:
            decision = "ANTI_REPEAT_PASS"
            reasons = []

        if decision.startswith("ANTI_REPEAT_BLOCK") or decision in {"ANTI_REPEAT_REVIEW_REQUIRED", "ANTI_REPEAT_HISTORY_REVIEW_REQUIRED"}:
            hard_block = True

        results.append({
            "contentId": cid,
            "platform": platform,
            "command": str(cpath.relative_to(ROOT)),
            "windowDays": WINDOW_DAYS,
            "decision": decision,
            "reasons": reasons,
            "mediaDecision": media_decision,
            "samePlatformTopicDecision": topic_decision,
            "samePlatformTopicMatches": topic_matches,
            "closest": closest,
            "signature": {
                "exactHash": sig["exactHash"],
                "renderId": sig["renderId"],
                "draftId": sig["draftId"],
            },
        })

    payload = {
        "project": "UGI",
        "component": "ANTI-REPEAT-GATE",
        "windowDays": WINDOW_DAYS,
        "topicCooldownScope": "PER_PLATFORM",
        "storiesIncluded": True,
        "historyRegistry": str(TOPIC_HISTORY.relative_to(ROOT)),
        "historyComplete": bool((history.get("historyQuality") or {}).get("complete")),
        "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "queuedCount": len(queued),
        "blocked": sum(
            1 for r in results
            if str(r.get("decision", "")).startswith("ANTI_REPEAT_BLOCK")
            or r.get("decision") in {"ANTI_REPEAT_REVIEW_REQUIRED", "ANTI_REPEAT_HISTORY_REVIEW_REQUIRED"}
        ),
        "state": "BLOCKED" if hard_block else "PASS",
        "results": results,
    }
    save(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if hard_block else 0


if __name__ == "__main__":
    raise SystemExit(main())
