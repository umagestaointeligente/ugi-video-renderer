#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "control-plane" / "publisher-hub" / "media-queue"
RECEIPTS = ROOT / "control-plane" / "publisher-hub" / "media-receipts"
CIRCUIT = ROOT / "control-plane" / "observability" / "buffer-circuit.json"
DISTRIBUTION = ROOT / "config" / "ugi" / "distribution-state.json"
DEFAULT_WORKER_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe(value: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in value)


def parse_due(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def distribution_allows(platform: str) -> bool:
    if not DISTRIBUTION.exists():
        return False
    state = load_json(DISTRIBUTION)
    buffer_state = state.get("buffer") or {}
    active = {str(x).lower() for x in (buffer_state.get("active_platforms") or [])}
    paused = {str(x).lower() for x in (buffer_state.get("paused_platforms") or [])}
    return platform not in paused and platform in active


def circuit_allows() -> bool:
    if not CIRCUIT.exists():
        return False
    state = load_json(CIRCUIT)
    return state.get("state") == "CLOSED" and state.get("mutationAllowed") is True


def validate_item(item: dict[str, Any], path: Path) -> None:
    if item.get("project") != "UGI":
        raise RuntimeError(f"PROJECT_ISOLATION_FAIL:{path}")
    if item.get("enabled") is not True:
        raise RuntimeError(f"ITEM_DISABLED:{path}")
    platform = str(item.get("platform") or "").lower()
    if platform not in {"linkedin", "instagram", "tiktok"}:
        raise RuntimeError(f"PLATFORM_NOT_ALLOWED:{platform}")
    if not distribution_allows(platform):
        raise RuntimeError(f"PLATFORM_PAUSED_OR_INACTIVE:{platform}")
    media_type = str(item.get("mediaType") or "").lower()
    if media_type not in {"image", "video"}:
        raise RuntimeError("MEDIA_TYPE_INVALID")
    if platform == "tiktok" and media_type != "video":
        raise RuntimeError("TIKTOK_MEDIA_V1_REQUIRES_VIDEO")
    media_url = str(item.get("mediaUrl") or "")
    if not media_url.startswith("https://"):
        raise RuntimeError("MEDIA_URL_MUST_BE_STABLE_HTTPS")
    mode = str(item.get("mode") or "customScheduled")
    if mode not in {"shareNow", "customScheduled", "addToQueue"}:
        raise RuntimeError("MODE_INVALID")
    if mode == "customScheduled":
        due = parse_due(str(item.get("dueAt") or ""))
        if due is None or due <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=2):
            raise RuntimeError("DUE_AT_INVALID_OR_TOO_SOON")
    if platform == "linkedin":
        if str(item.get("target") or "") != "UGI — Uma Gestão Inteligente":
            raise RuntimeError("LINKEDIN_COMPANY_PAGE_TARGET_REQUIRED")
        if item.get("personalProfileTargetAllowed") is not False:
            raise RuntimeError("LINKEDIN_PERSONAL_PROFILE_GUARD_REQUIRED")
        if not str(item.get("text") or "").strip():
            raise RuntimeError("LINKEDIN_TEXT_REQUIRED")


def receipt_path(item: dict[str, Any]) -> Path:
    return RECEIPTS / f"{safe(str(item['id']))}.json"


def already_created(item: dict[str, Any]) -> bool:
    p = receipt_path(item)
    if not p.exists():
        return False
    old = load_json(p)
    return old.get("bufferMutationPerformed") is True and bool(((old.get("publication") or {}).get("bufferPostId")))


def choose_one() -> tuple[Path, dict[str, Any]] | None:
    if not QUEUE.exists():
        return None
    candidates: list[tuple[dt.datetime, Path, dict[str, Any]]] = []
    for path in sorted(QUEUE.glob("*.json")):
        item = load_json(path)
        if item.get("enabled") is not True or item.get("project") != "UGI":
            continue
        if already_created(item):
            continue
        due = parse_due(str(item.get("dueAt") or "")) or dt.datetime.max.replace(tzinfo=dt.timezone.utc)
        candidates.append((due, path, item))
    if not candidates:
        return None
    _, path, item = sorted(candidates, key=lambda x: x[0])[0]
    return path, item


def post_worker(item: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    if not key:
        raise RuntimeError("UGI_WORKER_COMMAND_KEY_MISSING")
    url = os.getenv("WORKER_URL", DEFAULT_WORKER_URL).rstrip("/") + "/api/editorial-media-publish"
    payload = {
        "platform": item["platform"],
        "mediaType": item["mediaType"],
        "mediaUrl": item["mediaUrl"],
        "text": item.get("text", ""),
        "format": item.get("format", ""),
        "mode": item.get("mode", "customScheduled"),
        "dueAt": item.get("dueAt"),
    }
    p = subprocess.run([
        "curl", "--silent", "--show-error", "--location", "--max-time", "90",
        "-H", f"x-lola-command-key: {key}",
        "-H", "accept: application/json",
        "-H", "content-type: application/json",
        "--data-binary", json.dumps(payload, ensure_ascii=False),
        url,
    ], text=True, capture_output=True)
    try:
        result = json.loads(p.stdout)
    except Exception:
        result = {"ok": False, "error": p.stdout[:1000] or p.stderr[:1000], "bufferMutationPerformed": "unknown"}
    return result


def main() -> int:
    chosen = choose_one()
    if chosen is None:
        print(json.dumps({"ok": True, "state": "NO_PENDING_MEDIA_ITEMS"}))
        return 0
    path, item = chosen
    validate_item(item, path)
    if not circuit_allows():
        print(json.dumps({"ok": True, "state": "BUFFER_CIRCUIT_BLOCKED_NO_CALL", "id": item["id"]}))
        return 0

    result = post_worker(item)
    receipt = {
        "project": "UGI",
        "route": "EDITORIAL_MEDIA_V1",
        "queuePath": str(path.relative_to(ROOT)),
        "id": item["id"],
        "platform": item["platform"],
        "format": item.get("format"),
        "mediaType": item["mediaType"],
        "mediaUrl": item["mediaUrl"],
        "requestedDueAt": item.get("dueAt"),
        "ok": result.get("ok") is True,
        "bufferMutationPerformed": result.get("bufferMutationPerformed", False),
        "publication": result.get("publication"),
        "target": result.get("target"),
        "workerVersion": result.get("version"),
        "workerRoute": result.get("route"),
        "error": result.get("error"),
        "timestamp": now_iso(),
    }
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    receipt_path(item).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if result.get("ok") is not True:
        print(json.dumps(receipt, ensure_ascii=False))
        return 2

    if item.get("mode") == "customScheduled":
        requested = parse_due(str(item.get("dueAt") or ""))
        actual = parse_due(str(((result.get("publication") or {}).get("dueAt")) or ""))
        status = str(((result.get("publication") or {}).get("bufferStatus")) or "").lower()
        if not requested or not actual or requested != actual or status != "scheduled":
            receipt["ok"] = False
            receipt["error"] = "BUFFER_CREATE_RETURN_DID_NOT_PROVE_EXACT_SCHEDULE"
            receipt_path(item).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(receipt, ensure_ascii=False))
            return 3

    print(json.dumps(receipt, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
