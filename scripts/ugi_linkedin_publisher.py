from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "control-plane" / "publisher-hub" / "linkedin-queue"
RECEIPTS = ROOT / "control-plane" / "publisher-hub" / "receipts"
STATUS = ROOT / "control-plane" / "publisher-hub" / "linkedin-status" / "latest.json"
BREAKER = ROOT / "control-plane" / "observability" / "buffer-circuit.json"
DISTRIBUTION = ROOT / "config" / "ugi" / "distribution-state.json"
WORKER = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
TARGET_PAGE = "UGI — Uma Gestão Inteligente"
COOLDOWN_HOURS = int(os.getenv("UGI_BUFFER_COOLDOWN_HOURS", "6"))


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_time(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def validate_distribution() -> None:
    state = load(DISTRIBUTION)
    active = {str(x).lower() for x in ((state.get("buffer") or {}).get("active_platforms") or [])}
    li = (state.get("channels") or {}).get("linkedin") or {}
    if "linkedin" not in active or str(li.get("status", "")).upper() != "ACTIVE":
        raise SystemExit("LINKEDIN_DISTRIBUTION_NOT_ACTIVE")
    if li.get("company_page_only") is not True or li.get("personal_profile_publication_forbidden") is not True:
        raise SystemExit("LINKEDIN_COMPANY_PAGE_ISOLATION_NOT_PROVEN")
    if li.get("page_name") != TARGET_PAGE:
        raise SystemExit("LINKEDIN_TARGET_PAGE_MISMATCH")


def worker_call(method: str, path: str, key: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    headers = {"x-lola-command-key": key, "accept": "application/json"}
    if payload is not None:
        headers["content-type"] = "application/json"
    try:
        r = requests.request(method, WORKER + path, headers=headers, json=payload, timeout=90)
        try:
            body = r.json()
        except Exception:
            body = {"ok": False, "raw": r.text[:1500]}
        return r.status_code, body
    except Exception as exc:
        return 0, {"ok": False, "error": str(exc)}


def is_rate_limited(code: int, body: dict[str, Any]) -> bool:
    diag = body.get("bufferDiagnostics") or {}
    errors = diag.get("graphqlErrors") or body.get("errors") or []
    if code == 429 or int(diag.get("httpStatus") or 0) == 429:
        return True
    if "429" in str(body.get("error") or ""):
        return True
    for err in errors:
        if not isinstance(err, dict):
            continue
        ext = err.get("extensions") or {}
        if ext.get("code") == "RATE_LIMIT_EXCEEDED":
            return True
    return False


def breaker_open(now: dt.datetime) -> tuple[bool, dict[str, Any]]:
    data = load(BREAKER)
    if data.get("state") != "OPEN":
        return False, data
    next_probe = parse_time(data.get("nextProbeAt"))
    return bool(next_probe and now < next_probe), data


def open_breaker(now: dt.datetime, body: dict[str, Any], reason: str) -> None:
    diag = body.get("bufferDiagnostics") or {}
    save(BREAKER, {
        "project": "UGI",
        "provider": "BUFFER",
        "state": "OPEN",
        "reason": reason,
        "openedAt": now.isoformat(),
        "nextProbeAt": (now + dt.timedelta(hours=COOLDOWN_HOURS)).isoformat(),
        "cooldownHours": COOLDOWN_HOURS,
        "rateLimitWindow": next(((((e.get("extensions") or {}).get("window"))) for e in (diag.get("graphqlErrors") or []) if isinstance(e, dict)), None),
        "requestId": diag.get("requestId"),
        "mutationAllowed": False,
    })


def close_breaker(now: dt.datetime) -> None:
    save(BREAKER, {
        "project": "UGI",
        "provider": "BUFFER",
        "state": "CLOSED",
        "closedAt": now.isoformat(),
        "nextProbeAt": None,
        "mutationAllowed": True,
    })


def receipt_path(item: dict[str, Any], queue_path: Path) -> Path:
    name = str(item.get("receiptName") or (queue_path.stem + ".json"))
    if "/" in name or "\\" in name:
        raise SystemExit("LINKEDIN_RECEIPT_NAME_INVALID")
    return RECEIPTS / name


def publication_id(receipt: dict[str, Any]) -> str:
    candidates = [
        (receipt.get("publication") or {}).get("bufferPostId"),
        ((receipt.get("create") or {}).get("publication") or {}).get("bufferPostId"),
    ]
    return next((str(x) for x in candidates if x), "")


def is_proven(receipt: dict[str, Any]) -> bool:
    return receipt.get("ok") is True and receipt.get("state") in {"PROVEN_PUBLISHED", "DELIVERED"} and bool(publication_id(receipt))


def load_queue(now: dt.datetime) -> list[tuple[Path, dict[str, Any], Path]]:
    rows: list[tuple[Path, dict[str, Any], Path]] = []
    if not QUEUE.exists():
        return rows
    for path in sorted(QUEUE.glob("*.json")):
        item = load(path)
        if not item or item.get("enabled") is False:
            continue
        if str(item.get("project")) != "UGI" or str(item.get("platform")).lower() != "linkedin":
            continue
        if item.get("target") != TARGET_PAGE or item.get("personalProfileTargetAllowed") is not False:
            continue
        if str(item.get("format") or "text").lower() != "text":
            continue
        not_before = parse_time(item.get("notBefore"))
        if not_before and now < not_before:
            continue
        rp = receipt_path(item, path)
        if is_proven(load(rp)):
            continue
        rows.append((path, item, rp))
    rows.sort(key=lambda x: (parse_time(x[1].get("notBefore")) or dt.datetime.min.replace(tzinfo=dt.timezone.utc), str(x[1].get("id") or x[0].stem)))
    return rows


def persist_status(now: dt.datetime, state: str, item: dict[str, Any] | None, detail: dict[str, Any]) -> None:
    save(STATUS, {
        "project": "UGI",
        "component": "LINKEDIN-PUBLISHER-ADAPTER",
        "checkedAt": now.isoformat(),
        "state": state,
        "provider": "BUFFER",
        "platform": "linkedin",
        "target": TARGET_PAGE,
        "personalProfileTargetAllowed": False,
        "queueId": (item or {}).get("id"),
        "detail": detail,
    })


def main() -> int:
    validate_distribution()
    key = os.getenv("UGI_LOLA_COMMAND_KEY") or os.getenv("UGI_WORKER_COMMAND_KEY") or ""
    if not key:
        raise SystemExit("UGI_LOLA_COMMAND_KEY_MISSING")

    now = now_utc()
    blocked, breaker = breaker_open(now)
    if blocked:
        print(json.dumps({"state": "CIRCUIT_OPEN_NO_BUFFER_CALL", "nextProbeAt": breaker.get("nextProbeAt")}, ensure_ascii=False))
        return 0

    queue = load_queue(now)
    if not queue:
        print(json.dumps({"state": "NO_DUE_LINKEDIN_EDITORIAL", "bufferCalls": 0}, ensure_ascii=False))
        return 0

    queue_path, item, rp = queue[0]
    receipt = load(rp)
    post_id = publication_id(receipt)

    # At most one Buffer-backed Worker call per workflow run.
    if post_id:
        code, body = worker_call("GET", "/api/linkedin-publication-status?postId=" + requests.utils.quote(post_id, safe=""), key)
        if is_rate_limited(code, body):
            open_breaker(now, body, "BUFFER_RATE_LIMIT_DURING_LINKEDIN_READBACK")
            persist_status(now, "WAITING_BUFFER_RATE_LIMIT", item, {"bufferCalls": 1, "postIdPreserved": post_id})
            return 0

        if code == 200 and body.get("ok") is True:
            close_breaker(now)
            pub = body.get("publication") or {}
            status = str(pub.get("status") or "").lower()
            final = bool(pub.get("bufferPostId") and (pub.get("externalLink") or pub.get("sentAt") or pub.get("sharedNow") is True or status in {"sent", "posted", "published", "success", "complete", "completed"}))
            out = {
                "ok": final,
                "state": "PROVEN_PUBLISHED" if final else "BUFFER_CREATED_READBACK_PENDING",
                "retryable": not final,
                "provider": "BUFFER",
                "platform": "linkedin",
                "target": TARGET_PAGE,
                "personalProfileTargetAllowed": False,
                "queueId": item.get("id"),
                "queueFile": str(queue_path.relative_to(ROOT)),
                "create": receipt.get("create"),
                "readback": body,
                "publication": pub,
                "timestamp": now.isoformat(),
            }
            save(rp, out)
            persist_status(now, out["state"], item, {"bufferCalls": 1, "bufferPostId": pub.get("bufferPostId"), "externalLink": pub.get("externalLink")})
            return 0

        persist_status(now, "READBACK_FAILED_FAIL_CLOSED", item, {"bufferCalls": 1, "http": code, "error": body.get("error")})
        return 2

    payload = {
        "mode": str(item.get("mode") or "shareNow"),
        "text": str(item.get("text") or "").strip(),
    }
    if not payload["text"]:
        persist_status(now, "QUEUE_INVALID_EMPTY_TEXT", item, {"bufferCalls": 0})
        return 2
    if item.get("dueAt"):
        payload["dueAt"] = item.get("dueAt")

    code, body = worker_call("POST", "/api/linkedin-text-publish", key, payload)
    if is_rate_limited(code, body):
        open_breaker(now, body, "BUFFER_RATE_LIMIT_DURING_LINKEDIN_CREATE")
        out = {
            "ok": False,
            "state": "WAITING_BUFFER_RATE_LIMIT",
            "retryable": True,
            "provider": "BUFFER",
            "platform": "linkedin",
            "target": TARGET_PAGE,
            "personalProfileTargetAllowed": False,
            "queueId": item.get("id"),
            "queueFile": str(queue_path.relative_to(ROOT)),
            "create": body,
            "readback": None,
            "publication": None,
            "timestamp": now.isoformat(),
        }
        save(rp, out)
        persist_status(now, out["state"], item, {"bufferCalls": 1, "nextProbeAt": load(BREAKER).get("nextProbeAt")})
        return 0

    pub = body.get("publication") or {}
    created_id = str(pub.get("bufferPostId") or "")
    if code == 200 and body.get("ok") is True and created_id:
        close_breaker(now)
        out = {
            "ok": False,
            "state": "BUFFER_CREATED_READBACK_PENDING",
            "retryable": True,
            "provider": "BUFFER",
            "platform": "linkedin",
            "target": TARGET_PAGE,
            "personalProfileTargetAllowed": False,
            "queueId": item.get("id"),
            "queueFile": str(queue_path.relative_to(ROOT)),
            "create": body,
            "readback": None,
            "publication": pub,
            "timestamp": now.isoformat(),
        }
        # Durable ID before any future readback guarantees exactly-once create.
        save(rp, out)
        persist_status(now, out["state"], item, {"bufferCalls": 1, "bufferPostId": created_id})
        return 0

    out = {
        "ok": False,
        "state": "CREATE_FAILED_FAIL_CLOSED",
        "retryable": False,
        "provider": "BUFFER",
        "platform": "linkedin",
        "target": TARGET_PAGE,
        "personalProfileTargetAllowed": False,
        "queueId": item.get("id"),
        "queueFile": str(queue_path.relative_to(ROOT)),
        "create": body,
        "readback": None,
        "publication": pub or None,
        "timestamp": now.isoformat(),
    }
    save(rp, out)
    persist_status(now, out["state"], item, {"bufferCalls": 1, "http": code, "error": body.get("error")})
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
