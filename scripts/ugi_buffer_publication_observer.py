from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
WORKER = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
OUT = ROOT / "control-plane" / "observability" / "buffer-publication" / "latest.json"
DELIVERY = ROOT / "control-plane" / "delivery-proof" / "latest.json"
RECEIPTS = ROOT / "control-plane" / "publisher-hub" / "receipts"


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def safe_gateway_probe(key: str) -> dict[str, Any]:
    if not key:
        return {"ok": False, "httpStatus": 0, "state": "AUTH_MISSING"}
    try:
        r = requests.get(
            WORKER + "/api/buffer/channels",
            headers={"x-lola-command-key": key, "accept": "application/json"},
            timeout=30,
        )
        try:
            body = r.json()
        except Exception:
            body = {}
        diag = body.get("bufferDiagnostics") or {}
        errors = diag.get("graphqlErrors") or body.get("errors") or []
        first = errors[0] if errors and isinstance(errors[0], dict) else {}
        ext = first.get("extensions") or {}
        return {
            "ok": r.status_code == 200 and body.get("ok") is True,
            "httpStatus": r.status_code,
            "state": "READY" if r.status_code == 200 and body.get("ok") is True else "BLOCKED",
            "error": body.get("error") or first.get("message"),
            "rateLimitRemaining": diag.get("rateLimitRemaining"),
            "rateLimitCode": ext.get("code"),
            "rateLimitWindow": ext.get("window"),
            "requestId": diag.get("requestId"),
        }
    except Exception as exc:
        return {"ok": False, "httpStatus": 0, "state": "PROBE_FAILED", "error": str(exc)}


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc)
    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    gateway = safe_gateway_probe(key)
    delivery = load(DELIVERY)

    receipt_rows: list[dict[str, Any]] = []
    receipt_contradictions: list[dict[str, Any]] = []
    linkedin_receipt: dict[str, Any] | None = None

    if RECEIPTS.exists():
        for path in sorted(RECEIPTS.glob("*.json")):
            data = load(path)
            if not data:
                continue
            if path.name == "UGI-20260904-LI-EDITORIAL-001.json":
                linkedin_receipt = {
                    "file": path.name,
                    "ok": data.get("ok"),
                    "state": data.get("state"),
                    "platform": data.get("platform"),
                    "target": data.get("target"),
                    "timestamp": data.get("timestamp"),
                    "publicationTriggered": (data.get("create") or {}).get("publicationTriggered"),
                    "bufferMutationPerformed": (data.get("create") or {}).get("bufferMutationPerformed"),
                    "error": (data.get("create") or {}).get("error"),
                    "bufferDiagnostics": (data.get("create") or {}).get("bufferDiagnostics"),
                }
            if data.get("state") == "PROVEN_SCHEDULED" and data.get("publicationTriggered") is False:
                receipt_contradictions.append({
                    "file": path.name,
                    "issue": "PROVEN_SCHEDULED_WITH_PUBLICATION_TRIGGERED_FALSE",
                    "timestamp": data.get("timestamp"),
                })
            for row in data.get("results") or []:
                if not isinstance(row, dict):
                    continue
                receipt_rows.append({
                    "file": path.name,
                    "contentId": row.get("contentId"),
                    "platform": row.get("platform"),
                    "draftId": row.get("draftId"),
                    "bufferPostId": row.get("bufferPostId"),
                    "status": row.get("status") or row.get("bufferStatus"),
                    "dueAt": row.get("dueAt") or row.get("dueAtReadback") or row.get("dueAtRequested"),
                    "readbackPass": row.get("readbackPass"),
                })

    delivery_rows = delivery.get("results") or []
    by_content = {str(x.get("contentId")): x for x in delivery_rows if x.get("contentId")}
    mismatches: list[dict[str, Any]] = []
    for row in receipt_rows:
        cid = str(row.get("contentId") or "")
        if not cid or not row.get("bufferPostId"):
            continue
        live = by_content.get(cid)
        if not live:
            continue
        if not live.get("bufferPostId") or int(live.get("readbackHttp") or 0) >= 400:
            mismatches.append({
                "contentId": cid,
                "platform": row.get("platform"),
                "receiptBufferPostId": row.get("bufferPostId"),
                "receiptStatus": row.get("status"),
                "liveReadbackHttp": live.get("readbackHttp"),
                "liveBufferPostId": live.get("bufferPostId"),
                "liveState": live.get("state"),
                "issue": "RECEIPT_AND_LIVE_READBACK_DISAGREE",
            })

    root_causes: list[str] = []
    if gateway.get("httpStatus") == 429 or gateway.get("rateLimitCode") == "RATE_LIMIT_EXCEEDED":
        root_causes.append("BUFFER_API_RATE_LIMIT_ACTIVE")
    if receipt_contradictions:
        root_causes.append("CANONICAL_RECEIPT_FALSE_POSITIVE_RISK")
    if mismatches:
        root_causes.append("BUFFER_ID_READBACK_MISMATCH")
    if delivery.get("delivered") == 0 and (delivery.get("late") or 0) > 0:
        root_causes.append("DELIVERY_VERIFIER_CONFIRMS_ZERO_DELIVERED")

    payload = {
        "project": "UGI",
        "component": "BUFFER-PUBLICATION-OBSERVER",
        "checkedAt": now.isoformat(),
        "publicationProvider": "BUFFER",
        "publicationMutationPerformed": False,
        "gateway": gateway,
        "deliverySummary": {
            "checkedAt": delivery.get("checkedAt"),
            "delivered": delivery.get("delivered"),
            "pendingWithinGrace": delivery.get("pendingWithinGrace"),
            "late": delivery.get("late"),
            "failed": delivery.get("failed"),
            "state": delivery.get("state"),
        },
        "linkedinEditorial001": linkedin_receipt,
        "receiptContradictions": receipt_contradictions,
        "readbackMismatches": mismatches,
        "rootCauseFlags": root_causes,
        "state": "HEALTHY" if not root_causes else "BLOCKED",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
