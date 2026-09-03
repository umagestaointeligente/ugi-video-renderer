#!/usr/bin/env python3
"""Backfill/update UGI per-platform topic history from proven Publisher Hub receipts.

Only rows with durable Buffer readback proof are eligible. The same contentId is
idempotent. Topic semantics are derived from the canonical content command.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from ugi_anti_repeat_gate import COMMANDS, ROOT, TOPIC_HISTORY, command_topic_key, load, norm, scene_package

RECEIPTS = ROOT / "control-plane" / "publisher-hub" / "receipts"
WINDOW_DAYS = 15


def command_index() -> dict[str, tuple[Path, dict[str, Any]]]:
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


def command_management_thesis(command: dict[str, Any], platform: str) -> str:
    explicit = command.get("management_thesis") or command.get("managementThesis") or command.get("angle")
    if explicit:
        return str(explicit)
    pack = command.get("scenes_json") or command.get("scenesJson") or {}
    if isinstance(pack, dict) and pack.get("cta"):
        return str(pack.get("cta"))
    for scene in scene_package(command):
        if not isinstance(scene, dict):
            continue
        if str(scene.get("role") or "").lower() not in {"turn", "result", "cta"}:
            continue
        narration = scene.get("narration") or {}
        if isinstance(narration, dict):
            value = narration.get(platform) or next(iter(narration.values()), None)
            if value:
                return str(value)
    return str(command.get("title") or "")


def command_entities(command: dict[str, Any]) -> list[str]:
    raw = command.get("primaryEntities") or command.get("entities") or []
    if isinstance(raw, list):
        return [str(x) for x in raw if str(x).strip()]
    return []


def parse_due(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def already_recorded(history: dict[str, Any], cid: str) -> bool:
    for row in history.get("entries") or []:
        ids = row.get("contentIds") or ([row.get("contentId")] if row.get("contentId") else [])
        if cid in {str(x) for x in ids if x}:
            return True
    return False


def valid_receipt_row(row: dict[str, Any]) -> bool:
    if row.get("ok") is not True or row.get("readbackPass") is not True:
        return False
    if not row.get("contentId") or not row.get("platform") or not row.get("bufferPostId") or not row.get("dueAt"):
        return False
    if str(row.get("status") or "").lower() != "scheduled":
        return False
    return True


def main() -> int:
    if not TOPIC_HISTORY.exists():
        raise SystemExit("TOPIC_HISTORY_MISSING")
    history = load(TOPIC_HISTORY)
    commands = command_index()
    added: list[dict[str, Any]] = []
    skipped_missing_command: list[str] = []

    for receipt_path in sorted(RECEIPTS.glob("*.json")):
        try:
            receipt = load(receipt_path)
        except Exception:
            continue
        if receipt.get("project") != "UGI" or str(receipt.get("publisher") or "").upper() != "BUFFER":
            continue
        for row in receipt.get("results") or []:
            if not isinstance(row, dict) or not valid_receipt_row(row):
                continue
            cid = str(row["contentId"])
            if already_recorded(history, cid):
                continue
            if cid not in commands:
                skipped_missing_command.append(cid)
                continue

            command_path, command = commands[cid]
            platform = norm(row.get("platform"))
            due_at = str(row["dueAt"])
            due = parse_due(due_at)
            audience_date = due.date()
            topic_key = command_topic_key(command) or norm(command.get("title") or cid)
            title = str(command.get("title") or topic_key)
            entry = {
                "platform": platform,
                "topicKey": topic_key,
                "primaryEntities": command_entities(command),
                "eventOrCase": str(command.get("event_or_case") or command.get("eventOrCase") or title),
                "managementThesis": command_management_thesis(command, platform),
                "formats": ["short" if platform == "youtube" else "video"],
                "contentIds": [cid],
                "audienceDate": audience_date.isoformat(),
                "dueAt": due_at,
                "state": "PROVEN_SCHEDULED",
                "bufferPostId": str(row["bufferPostId"]),
                "evidenceRef": str(receipt_path.relative_to(ROOT)),
                "commandRef": str(command_path.relative_to(ROOT)),
                "cooldownEligible": True,
                "cooldownUntil": (audience_date + dt.timedelta(days=WINDOW_DAYS)).isoformat() + "T23:59:59-03:00",
                "repeatException": command.get("repeat_exception") or command.get("repeatException"),
            }
            history.setdefault("entries", []).append(entry)
            added.append({"contentId": cid, "platform": platform, "topicKey": topic_key})

    history["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    history.setdefault("historyQuality", {})["lastReceiptSyncAt"] = history["updatedAt"]
    history["historyQuality"]["receiptSyncActive"] = True
    TOPIC_HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = {
        "ok": True,
        "project": "UGI",
        "component": "PLATFORM_TOPIC_HISTORY_SYNC",
        "added": added,
        "addedCount": len(added),
        "skippedMissingCommand": sorted(set(skipped_missing_command)),
        "historyPath": str(TOPIC_HISTORY.relative_to(ROOT)),
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
