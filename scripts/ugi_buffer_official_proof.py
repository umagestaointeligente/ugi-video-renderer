#!/usr/bin/env python3
"""Read-only live proof for the UGI 2026-09-04 Buffer agenda.

This verifier never creates, edits, approves or republishes content. It reads the
existing Buffer publication state through the canonical UGI Worker and marks the
batch BUFFER_SCHEDULED only when every post has a real Buffer id, scheduled
state and an exact due instant after timezone normalization.
"""

# live-readback trigger: 2026-09-04T07:48-03:00

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import urllib.parse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "control-plane/publisher-hub/queue/ugi-20260904-full-agenda-r1.json"
RENDER_STATE = ROOT / "control-plane/publisher-hub/render-state"
PROOF = ROOT / "control-plane/publisher-hub/receipts/UGI-20260904-OFFICIAL-BUFFER-PROOF.json"
WORKER_URL = os.getenv("WORKER_URL", "https://lola-operacional-ugi.umagestaointeligente.workers.dev").rstrip("/")
KEY = os.getenv("UGI_WORKER_COMMAND_KEY", "")


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value)


def parse_due(value: Any) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def worker_get(path: str) -> dict[str, Any]:
    p = subprocess.run(
        [
            "curl", "--silent", "--show-error", "--location", "--max-time", "90",
            "-A", "UGI-Buffer-Official-Proof/1.0",
            "-H", f"x-lola-command-key: {KEY}",
            "-H", "accept: application/json",
            WORKER_URL + path,
        ],
        text=True,
        capture_output=True,
    )
    try:
        data = json.loads(p.stdout)
    except Exception:
        return {"ok": False, "raw": p.stdout[:1200], "stderr": p.stderr[:800], "returncode": p.returncode}
    if p.returncode != 0:
        data["ok"] = False
        data["returncode"] = p.returncode
    return data


def main() -> int:
    if not KEY:
        raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = manifest.get("posts") or []
    results: list[dict[str, Any]] = []

    for row in rows:
        cid = str(row["contentId"])
        platform = str(row["platform"]).lower()
        requested_due_raw = str(row["dueAt"])
        requested_due = parse_due(requested_due_raw)
        state_file = RENDER_STATE / f"{safe_name(cid)}.json"

        if not state_file.exists():
            results.append({"contentId": cid, "platform": platform, "ok": False, "reason": "RENDER_STATE_MISSING"})
            continue

        state = json.loads(state_file.read_text(encoding="utf-8"))
        draft_id = str(state.get("approvalDraftId") or "").strip()
        if not draft_id:
            results.append({"contentId": cid, "platform": platform, "ok": False, "reason": "DRAFT_ID_MISSING"})
            continue

        rb = worker_get(
            "/api/platform-publication-status?id=" + urllib.parse.quote(draft_id)
            + "&platform=" + urllib.parse.quote(platform)
        )
        publication = rb.get("publication") or {}
        actual_due_raw = str(publication.get("dueAt") or "")
        actual_due = parse_due(actual_due_raw)
        status = str(publication.get("status") or "").lower()
        buffer_status = str(publication.get("bufferStatus") or "").lower()
        buffer_post_id = str(publication.get("bufferPostId") or "").strip()

        exact_instant = bool(requested_due and actual_due and requested_due == actual_due)
        passed = (
            rb.get("ok") is True
            and bool(buffer_post_id)
            and status == "scheduled"
            and buffer_status == "scheduled"
            and exact_instant
        )

        results.append(
            {
                "contentId": cid,
                "platform": platform,
                "draftId": draft_id,
                "requestedDueAt": requested_due_raw,
                "bufferDueAt": actual_due_raw,
                "requestedDueUtc": requested_due.isoformat() if requested_due else None,
                "bufferDueUtc": actual_due.isoformat() if actual_due else None,
                "bufferPostId": buffer_post_id or None,
                "status": status or None,
                "bufferStatus": buffer_status or None,
                "readbackOk": rb.get("ok") is True,
                "exactInstant": exact_instant,
                "readbackPass": passed,
                "ok": passed,
            }
        )

    ok = len(results) == len(rows) and bool(rows) and all(x.get("ok") is True for x in results)
    out = {
        "project": "UGI",
        "batchId": manifest.get("batchId"),
        "publisher": "BUFFER",
        "verificationMode": "READ_ONLY_LIVE_READBACK",
        "mutationTriggered": False,
        "expectedTargets": len(rows),
        "provenTargets": sum(1 for x in results if x.get("ok") is True),
        "ok": ok,
        "state": "BUFFER_SCHEDULED" if ok else "NOT_PROVEN",
        "results": results,
        "verifiedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    PROOF.parent.mkdir(parents=True, exist_ok=True)
    PROOF.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
