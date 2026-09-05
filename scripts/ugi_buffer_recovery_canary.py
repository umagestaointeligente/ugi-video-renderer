#!/usr/bin/env python3
"""Perform at most one Buffer-backed recovery readback for UGI.

The canary runs only after the canonical circuit's nextProbeAt. It selects one
previously known Buffer publication from receipts and performs exactly one
live publication-status request through the authoritative UGI Worker. Success
closes the circuit; rate limit or indeterminate failure keeps it fail-closed.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CIRCUIT = ROOT / "control-plane" / "observability" / "buffer-circuit.json"
RECEIPTS = ROOT / "control-plane" / "publisher-hub" / "receipts"
WORKER = os.getenv("WORKER_URL", "https://lola-operacional-ugi.umagestaointeligente.workers.dev").rstrip("/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_time(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def candidate() -> dict[str, str] | None:
    rows: list[tuple[dt.datetime, dict[str, str]]] = []
    if not RECEIPTS.exists():
        return None
    for path in RECEIPTS.glob("*.json"):
        try:
            data = load_json(path)
        except Exception:
            continue
        for row in data.get("results") or []:
            draft_id = str(row.get("draftId") or "").strip()
            buffer_id = str(row.get("bufferPostId") or "").strip()
            platform = str(row.get("platform") or "").strip().lower()
            due = parse_time(row.get("dueAt") or row.get("dueAtReadback") or row.get("dueAtRequested"))
            if not draft_id or not buffer_id or platform not in {"linkedin", "instagram", "tiktok"} or due is None:
                continue
            rows.append((due, {
                "draftId": draft_id,
                "bufferPostId": buffer_id,
                "platform": platform,
                "receipt": str(path.relative_to(ROOT)),
            }))
    if not rows:
        return None
    rows.sort(key=lambda item: item[0], reverse=True)
    return rows[0][1]


def retry_after_seconds(body: dict[str, Any]) -> int | None:
    for key in ("retryAfterSeconds", "retry_after", "retryAfter"):
        value = body.get(key)
        try:
            if value is not None:
                return max(60, int(value))
        except Exception:
            pass
    return None


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc)
    circuit = load_json(CIRCUIT) if CIRCUIT.exists() else {}
    state = str(circuit.get("state") or "CLOSED").upper()
    next_probe = parse_time(circuit.get("nextProbeAt"))

    if state != "OPEN" and circuit.get("mutationAllowed") is not False:
        print(json.dumps({"ok": True, "state": "CLOSED", "bufferCallsMade": 0}))
        return 0
    if next_probe is not None and now < next_probe:
        print(json.dumps({
            "ok": False,
            "state": "WAITING_RATE_LIMIT",
            "nextProbeAt": next_probe.isoformat(),
            "bufferCallsMade": 0,
        }))
        return 0

    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    if not key:
        raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")

    pick = candidate()
    if not pick:
        circuit.update({
            "state": "OPEN",
            "mutationAllowed": False,
            "reason": "BUFFER_CANARY_NO_KNOWN_PUBLICATION",
            "lastCanaryAt": now.isoformat(),
            "nextProbeAt": (now + dt.timedelta(hours=1)).isoformat(),
        })
        write_json(CIRCUIT, circuit)
        print(json.dumps({"ok": False, "state": "OPEN", "reason": circuit["reason"], "bufferCallsMade": 0}))
        return 0

    query = urllib.parse.urlencode({"id": pick["draftId"], "platform": pick["platform"]})
    url = WORKER + "/api/platform-publication-status?" + query
    req = urllib.request.Request(url, headers={
        "x-lola-command-key": key,
        "accept": "application/json",
        "user-agent": "UGI-Buffer-Recovery-Canary/1.0",
    })

    http_code = 0
    body: dict[str, Any] = {}
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            http_code = int(response.status)
            raw = response.read().decode("utf-8", errors="replace")
            body = json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        http_code = int(exc.code)
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else {}
        except Exception:
            body = {"ok": False, "raw": raw[:1200]}
    except Exception as exc:
        body = {"ok": False, "error": f"{type(exc).__name__}:{exc}"}

    serialized = json.dumps(body, ensure_ascii=False).lower()
    publication = body.get("publication") or {}
    proven = (
        http_code == 200
        and body.get("ok") is True
        and bool(publication.get("bufferPostId"))
        and bool(publication.get("status") or publication.get("bufferStatus"))
    )

    if proven:
        circuit.update({
            "state": "CLOSED",
            "mutationAllowed": True,
            "reason": "BUFFER_CANARY_RECOVERED",
            "closedAt": now.isoformat(),
            "lastCanaryAt": now.isoformat(),
            "lastCanary": {
                **pick,
                "httpStatus": http_code,
                "status": publication.get("status"),
                "bufferStatus": publication.get("bufferStatus"),
            },
        })
        write_json(CIRCUIT, circuit)
        print(json.dumps({"ok": True, "state": "CLOSED", "bufferCallsMade": 1, "candidate": pick}))
        return 0

    limited = http_code == 429 or "rate limit" in serialized or "too many" in serialized or "429" in serialized
    delay = retry_after_seconds(body) if limited else None
    if delay is None:
        delay = 6 * 3600 if limited else 3600
    circuit.update({
        "state": "OPEN",
        "mutationAllowed": False,
        "reason": "BUFFER_CANARY_RATE_LIMITED" if limited else "BUFFER_CANARY_NOT_PROVEN",
        "lastCanaryAt": now.isoformat(),
        "nextProbeAt": (now + dt.timedelta(seconds=delay)).isoformat(),
        "lastCanary": {
            **pick,
            "httpStatus": http_code,
            "responseOk": body.get("ok"),
        },
    })
    write_json(CIRCUIT, circuit)
    print(json.dumps({
        "ok": False,
        "state": "OPEN",
        "reason": circuit["reason"],
        "nextProbeAt": circuit["nextProbeAt"],
        "bufferCallsMade": 1,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
