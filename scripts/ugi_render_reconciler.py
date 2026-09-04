#!/usr/bin/env python3
"""UGI Publisher Hub render reconciler.

Ensures every contentId in the canonical Publisher Hub queue has a render
created through the deployed UGI Worker `/api/video-render` bridge. That bridge
is the authority that creates/reuses the editorial draft and persists the
`approvalDraftId` mapping consumed by `/api/video-upload` and publication.

This script never publishes and never calls Buffer. It is idempotent through
per-content render-state receipts committed under Publisher Hub.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import urllib.parse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "control-plane" / "publisher-hub" / "queue"
COMMANDS = ROOT / "control-plane" / "commands"
STATE_DIR = ROOT / "control-plane" / "publisher-hub" / "render-state"
DEFAULT_WORKER_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
MAX_RENDER_ATTEMPTS = 3
STALE_QUEUE_HOURS = int(os.getenv("UGI_QUEUE_STALE_HOURS", "6"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


class WorkerClient:
    def __init__(self, base_url: str, key: str):
        self.base_url = base_url.rstrip("/")
        self.key = key

    def _run(self, args: list[str]) -> dict[str, Any]:
        p = subprocess.run(args, text=True, capture_output=True)
        try:
            data = json.loads(p.stdout)
        except Exception:
            data = {
                "ok": False,
                "raw": p.stdout[:2000],
                "stderr": p.stderr[:1000],
                "returncode": p.returncode,
            }
        if p.returncode != 0:
            data.setdefault("ok", False)
            data["returncode"] = p.returncode
            data.setdefault("stderr", p.stderr[:1000])
        return data

    def get(self, path: str) -> dict[str, Any]:
        return self._run([
            "curl", "--silent", "--show-error", "--location", "--max-time", "90",
            "-A", "UGI-Publisher-Hub-Render-Reconciler/1.1",
            "-H", f"x-lola-command-key: {self.key}",
            "-H", "accept: application/json",
            self.base_url + path,
        ])

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._run([
            "curl", "--silent", "--show-error", "--location", "--max-time", "120",
            "-A", "UGI-Publisher-Hub-Render-Reconciler/1.1",
            "-H", f"x-lola-command-key: {self.key}",
            "-H", "accept: application/json",
            "-H", "content-type: application/json",
            "--data-binary", json.dumps(payload, ensure_ascii=False),
            self.base_url + path,
        ])


def _queue_row_is_stale(row: dict[str, Any]) -> bool:
    try:
        due = dt.datetime.fromisoformat(str(row.get("dueAt") or "").replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return False
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=max(1, STALE_QUEUE_HOURS))
    return due < cutoff


def queued_content_ids() -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    if not QUEUE.exists():
        return ids
    for path in sorted(QUEUE.glob("*.json")):
        data = load_json(path)
        if data.get("project") != "UGI":
            raise SystemExit(f"PROJECT_ISOLATION_FAIL:{path}")
        for row in data.get("posts") or []:
            if _queue_row_is_stale(row):
                continue
            cid = str(row.get("contentId") or "").strip()
            if not cid:
                raise SystemExit(f"CONTENT_ID_MISSING:{path}")
            if cid not in seen:
                seen.add(cid)
                ids.append(cid)
    return ids


def fetch_drafts(client: WorkerClient) -> list[dict[str, Any]]:
    response = client.get("/api/drafts")
    if not response.get("ok") and "drafts" not in response:
        raise RuntimeError(f"DRAFT_READ_FAIL:{response}")
    return response.get("drafts") or []


def draft_for_content(drafts: list[dict[str, Any]], content_id: str) -> dict[str, Any] | None:
    matches = [
        d for d in drafts
        if str(d.get("contentId") or d.get("content_id") or "") == content_id
    ]
    matches.sort(key=lambda d: str(d.get("updatedAt") or d.get("createdAt") or ""), reverse=True)
    return matches[0] if matches else None


def command_for_content(content_id: str) -> tuple[Path, dict[str, Any]]:
    matches: list[tuple[Path, dict[str, Any]]] = []
    if COMMANDS.exists():
        for path in sorted(COMMANDS.glob("*.json")):
            try:
                data = load_json(path)
            except Exception:
                continue
            if str(data.get("content_id") or data.get("contentId") or "") == content_id:
                matches.append((path, data))
    if not matches:
        raise RuntimeError(f"COMMAND_NOT_FOUND:{content_id}")
    return matches[-1]


def state_path(content_id: str) -> Path:
    return STATE_DIR / f"{safe_name(content_id)}.json"


def write_state(content_id: str, payload: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"project": "UGI", "contentId": content_id, **payload, "updatedAt": now_iso()}
    state_path(content_id).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def is_draft_media_ready(draft: dict[str, Any] | None) -> bool:
    if not draft:
        return False
    assets = draft.get("assets") or {}
    return (
        draft.get("allPlatformsReady") is True
        and all(
            ((assets.get(p) or {}).get("ready") is True and (assets.get(p) or {}).get("videoUrl"))
            for p in ("instagram", "tiktok", "youtube")
        )
    )


def refresh_existing_state(
    client: WorkerClient,
    content_id: str,
    draft: dict[str, Any] | None,
) -> tuple[bool, bool]:
    """Return (handled, hard_failure).

    A prior dispatch that the Worker explicitly rejected is retryable. We never
    reinterpret a rejected dispatch as RENDER_IN_PROGRESS merely because it had
    a renderId allocated for diagnostics.
    """
    path = state_path(content_id)
    if not path.exists():
        return False, False

    try:
        old = load_json(path)
    except Exception:
        old = {}

    rid = str(old.get("workerRenderId") or "").strip()
    attempts = int(old.get("attempts") or 1)

    if is_draft_media_ready(draft):
        write_state(content_id, {
            **old,
            "state": "DRAFT_MEDIA_READY",
            "approvalDraftId": draft.get("id"),
            "allPlatformsReady": True,
            "attempts": attempts,
        })
        return True, False

    dispatch_response = old.get("dispatchResponse") or {}
    explicitly_rejected = (
        old.get("state") == "RENDER_DISPATCH_FAILED"
        or dispatch_response.get("ok") is False
        or ("githubAccepted" in dispatch_response and dispatch_response.get("githubAccepted") is False)
    )
    if explicitly_rejected:
        if attempts >= MAX_RENDER_ATTEMPTS:
            write_state(content_id, {
                **old,
                "state": "RENDER_FAILED_TERMINAL",
                "attempts": attempts,
                "failureReason": "previous_worker_dispatch_rejected",
            })
            return True, True
        return False, False

    if not rid:
        return False, False

    result = client.get("/api/video-result/" + urllib.parse.quote(rid))
    status = str(result.get("status") or "").lower()
    all_ready = result.get("allPlatformsReady") is True or result.get("ready") is True or status == "ready"
    approval_draft = result.get("approvalDraftId")

    if result.get("ok") is True and all_ready:
        write_state(content_id, {
            **old,
            "state": "MEDIA_READY_WAITING_DRAFT_READBACK",
            "workerRenderId": rid,
            "approvalDraftId": approval_draft,
            "allPlatformsReady": True,
            "attempts": attempts,
            "lastResult": result,
        })
        return True, False

    if status in {"failed", "error", "cancelled"} or (
        result.get("ok") is False and result.get("errorClass")
    ):
        if attempts >= MAX_RENDER_ATTEMPTS:
            write_state(content_id, {
                **old,
                "state": "RENDER_FAILED_TERMINAL",
                "workerRenderId": rid,
                "attempts": attempts,
                "lastResult": result,
            })
            return True, True
        return False, False

    write_state(content_id, {
        **old,
        "state": "RENDER_IN_PROGRESS",
        "workerRenderId": rid,
        "approvalDraftId": approval_draft or old.get("approvalDraftId"),
        "attempts": attempts,
        "lastKnownStatus": status or "unknown",
        "lastResult": result,
    })
    return True, False


def build_worker_payload(command: dict[str, Any], content_id: str) -> dict[str, Any]:
    """Translate the durable command schema into the live Worker schema.

    Durable commands store the full scene package under `scenes_json`. The live
    Worker `/api/video-render` intentionally validates `body.scenes` as a 4-10
    item array. Passing the package object as `scenes_json` makes the Worker
    fail closed with dynamic_video_scenes_required, so we unwrap it here.
    """
    scene_package = command.get("scenes_json") or command.get("scenesJson") or command.get("scenes")
    package_meta: dict[str, Any] = {}
    if isinstance(scene_package, dict):
        dynamic_scenes = scene_package.get("scenes")
        package_meta = scene_package
    else:
        dynamic_scenes = scene_package

    if not isinstance(dynamic_scenes, list) or not (4 <= len(dynamic_scenes) <= 10):
        raise RuntimeError(f"DYNAMIC_SCENES_INVALID_LOCAL:{content_id}")

    payload: dict[str, Any] = {
        "title": command.get("title"),
        "duration": command.get("duration"),
        "type": command.get("type") or package_meta.get("type") or "reel",
        "content_id": content_id,
        "experiment_id": command.get("experiment_id") or command.get("experimentId"),
        "variant": command.get("variant"),
        "commercial_intent": command.get("commercial_intent") or command.get("commercialIntent"),
        "scenes": dynamic_scenes,
        "smoke_test": bool(command.get("smoke_test", False)),
        "smoke_test_duration": command.get("smoke_test_duration", 4),
        "smoke_test_platform": command.get("smoke_test_platform", "instagram"),
    }

    for key in ("cta", "commercial_offer", "copy_lock", "exact_copy", "editorial_mode", "commerce"):
        value = command.get(key)
        if value is None:
            value = package_meta.get(key)
        if value is not None:
            payload[key] = value

    if command.get("draft_id") or command.get("draftId"):
        payload["draft_id"] = command.get("draft_id") or command.get("draftId")

    return payload


def dispatch_render(client: WorkerClient, content_id: str) -> bool:
    command_path, command = command_for_content(content_id)
    old: dict[str, Any] = {}
    path = state_path(content_id)
    if path.exists():
        try:
            old = load_json(path)
        except Exception:
            old = {}
    attempts = int(old.get("attempts") or 0) + 1

    try:
        payload = build_worker_payload(command, content_id)
    except Exception as exc:
        write_state(content_id, {
            "state": "RENDER_DISPATCH_FAILED",
            "workerRenderId": None,
            "approvalDraftId": None,
            "githubAccepted": False,
            "commandPath": str(command_path.relative_to(ROOT)),
            "attempts": attempts,
            "dispatchResponse": {
                "ok": False,
                "errorClass": "local_dynamic_scene_validation_failed",
                "error": str(exc),
            },
        })
        return False

    response = client.post("/api/video-render", payload)
    rid = str(response.get("renderId") or "").strip()
    accepted = response.get("ok") is True and response.get("githubAccepted") is True and bool(rid)

    write_state(content_id, {
        "state": "RENDER_DISPATCHED" if accepted else "RENDER_DISPATCH_FAILED",
        "workerRenderId": rid or None,
        "approvalDraftId": response.get("approvalDraftId"),
        "existingDraftReused": response.get("existingDraftReused"),
        "githubAccepted": response.get("githubAccepted"),
        "githubStatus": response.get("githubStatus"),
        "commandPath": str(command_path.relative_to(ROOT)),
        "attempts": attempts,
        "dispatchResponse": response,
    })
    return accepted


def main() -> int:
    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    if not key:
        raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")

    client = WorkerClient(os.getenv("WORKER_URL", DEFAULT_WORKER_URL), key)
    health = client.get("/api/health")
    if not health.get("ok"):
        raise SystemExit("WORKER_HEALTH_FAIL")

    content_ids = queued_content_ids()
    drafts = fetch_drafts(client)
    summary: list[dict[str, Any]] = []
    hard_failure = False

    for cid in content_ids:
        draft = draft_for_content(drafts, cid)
        if is_draft_media_ready(draft):
            write_state(cid, {
                "state": "DRAFT_MEDIA_READY",
                "approvalDraftId": draft.get("id"),
                "allPlatformsReady": True,
                "attempts": int((load_json(state_path(cid)) if state_path(cid).exists() else {}).get("attempts") or 0),
            })
            summary.append({"contentId": cid, "state": "DRAFT_MEDIA_READY", "mutated": False})
            continue

        handled, failed = refresh_existing_state(client, cid, draft)
        if failed:
            hard_failure = True
            summary.append({"contentId": cid, "state": "RENDER_FAILED_TERMINAL", "mutated": False})
            continue
        if handled:
            summary.append({"contentId": cid, "state": load_json(state_path(cid)).get("state"), "mutated": False})
            continue

        accepted = dispatch_render(client, cid)
        if not accepted:
            hard_failure = True
        summary.append({
            "contentId": cid,
            "state": "RENDER_DISPATCHED" if accepted else "RENDER_DISPATCH_FAILED",
            "mutated": accepted,
        })

    print(json.dumps({
        "ok": not hard_failure,
        "project": "UGI",
        "component": "UGI-PUBLISHER-HUB-RENDER-RECONCILER",
        "chatRuntimeRequired": False,
        "publicationTriggered": False,
        "contentCount": len(content_ids),
        "results": summary,
        "timestamp": now_iso(),
    }, ensure_ascii=False, indent=2))
    return 1 if hard_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
