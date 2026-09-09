from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
VIDEO_RECEIPTS = ROOT / "control-plane" / "publisher-hub" / "receipts"
STATIC_RECEIPTS = ROOT / "control-plane" / "r45" / "receipts"
R453_RECEIPTS = ROOT / "control-plane" / "instagram-r45-3" / "receipts"
OUT = ROOT / "control-plane" / "delivery-proof" / "latest.json"
WORKER = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
GRACE_MINUTES = 12
LOOKBACK_HOURS = 36
MAX_READBACKS = 25
DISTRIBUTION_STATE = ROOT / "config" / "ugi" / "distribution-state.json"


class Client:
    def __init__(self, key: str) -> None:
        self.headers = {"x-lola-command-key": key, "accept": "application/json"}

    def get(self, path: str, timeout: int = 120) -> tuple[int, dict[str, Any]]:
        r = requests.get(WORKER + path, headers=self.headers, timeout=timeout)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"ok": False, "raw": r.text[:1200]}


def parse_time(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def load_active_platforms() -> set[str]:
    data = json.loads(DISTRIBUTION_STATE.read_text(encoding="utf-8"))
    buffer = data.get("buffer", {})
    if buffer.get("publisher") != "buffer":
        raise SystemExit("DELIVERY_VERIFIER_PROVIDER_LOCK")
    active = {str(x).lower() for x in buffer.get("active_platforms", [])}
    paused = {str(x).lower() for x in buffer.get("paused_platforms", [])}
    if not active or active & paused:
        raise SystemExit("DELIVERY_VERIFIER_DISTRIBUTION_STATE_INVALID")
    return active


def external_proof(url: str | None) -> dict[str, Any]:
    if not url:
        return {"attempted": False, "ok": False, "reason": "external_link_missing"}
    try:
        r = requests.get(url, timeout=30, allow_redirects=True, headers={"User-Agent":"Mozilla/5.0 UGI-Delivery-Proof/1.0"})
        return {"attempted": True, "ok": r.status_code < 500, "httpStatus": r.status_code, "finalUrl": r.url}
    except Exception as exc:
        return {"attempted": True, "ok": False, "error": str(exc)}


def iter_receipts(root: Path, kind: str):
    if not root.exists():
        return
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for row in data.get("results") or []:
            yield kind, path, data, row


def classify(pub: dict[str, Any], due: dt.datetime, now: dt.datetime) -> str:
    status = str(pub.get("status") or pub.get("bufferStatus") or "").lower()
    if status in {"error", "failed", "cancelled"} or pub.get("error"):
        return "FAILED"
    if pub.get("sentAt") or status in {"sent", "published", "complete", "completed"}:
        return "DELIVERED"
    if now > due + dt.timedelta(minutes=GRACE_MINUTES):
        return "LATE"
    return "PENDING_WITHIN_GRACE"


def main() -> int:
    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    if not key:
        raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")
    client = Client(key)
    now = dt.datetime.now(dt.timezone.utc)
    lower = now - dt.timedelta(hours=LOOKBACK_HOURS)
    results: list[dict[str, Any]] = []
    active_platforms = load_active_platforms()
    seen: set[tuple[str, str]] = set()

    sources = (
        list(iter_receipts(VIDEO_RECEIPTS, "video") or [])
        + list(iter_receipts(STATIC_RECEIPTS, "static") or [])
        + list(iter_receipts(R453_RECEIPTS, "r453") or [])
    )

    for kind, path, receipt, row in sources:
        due_raw = row.get("dueAt") or row.get("dueAtReadback") or row.get("dueAtRequested")
        due = parse_time(due_raw)
        if not due or due > now or due < lower:
            continue

        platform = str(row.get("platform") or ("instagram" if kind in {"static", "r453"} else "")).lower()
        if platform not in active_platforms:
            continue

        buffer_id = str(row.get("bufferPostId") or "").strip()
        draft_id = str(row.get("draftId") or "").strip()
        identity_value = buffer_id or draft_id
        if not identity_value:
            continue
        dedupe_key = (platform, identity_value)
        if dedupe_key in seen:
            continue
        if len(seen) >= MAX_READBACKS:
            break
        seen.add(dedupe_key)

        if buffer_id:
            endpoint = "/api/r45-2/buffer-status?id=" + requests.utils.quote(buffer_id, safe="")
            code, rb = client.get(endpoint)
            pub = rb.get("post") or {}
        else:
            if kind == "r453":
                continue
            if kind == "static":
                endpoint = "/api/r45/static-publication-status?id=" + requests.utils.quote(draft_id, safe="")
            else:
                endpoint = "/api/platform-publication-status?id=" + requests.utils.quote(draft_id, safe="") + "&platform=" + requests.utils.quote(platform, safe="")
            code, rb = client.get(endpoint)
            pub = rb.get("publication") or {}
        identity = {"draftId": draft_id or None, "bufferPostId": buffer_id or pub.get("bufferPostId")}

        readback_ok = code == 200 and rb.get("ok") is True
        state = classify(pub, due, now) if readback_ok else "UNVERIFIABLE"
        results.append({
            "receipt": str(path.relative_to(ROOT)),
            "contentId": row.get("contentId"),
            "platform": platform,
            "kind": kind,
            **identity,
            "dueAt": due.isoformat(),
            "readbackHttp": code,
            "bufferStatus": pub.get("bufferStatus") or pub.get("status"),
            "status": pub.get("status"),
            "sentAt": pub.get("sentAt"),
            "externalLink": pub.get("externalLink"),
            "error": pub.get("error"),
            "readbackError": None if readback_ok else str(rb.get("error") or rb.get("message") or f"HTTP_{code}")[:300],
            "state": state,
            "externalProof": external_proof(pub.get("externalLink")) if state == "DELIVERED" else {"attempted": False},
        })

    delivered = sum(1 for x in results if x["state"] == "DELIVERED")
    pending = sum(1 for x in results if x["state"] == "PENDING_WITHIN_GRACE")
    late = sum(1 for x in results if x["state"] == "LATE")
    failed = sum(1 for x in results if x["state"] == "FAILED")
    unverifiable = sum(1 for x in results if x["state"] == "UNVERIFIABLE")
    payload = {
        "project":"UGI",
        "component":"DELIVERY-VERIFIER",
        "checkedAt":now.isoformat(),
        "lookbackHours":LOOKBACK_HOURS,
        "graceMinutes":GRACE_MINUTES,
        "delivered":delivered,
        "pendingWithinGrace":pending,
        "late":late,
        "failed":failed,
        "unverifiable":unverifiable,
        "activePlatformsChecked":sorted(active_platforms),
        "readbackLimit":MAX_READBACKS,
        "state":"HEALTHY" if late == 0 and failed == 0 and unverifiable == 0 else "ALERT",
        "results":results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if late == 0 and failed == 0 and unverifiable == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
