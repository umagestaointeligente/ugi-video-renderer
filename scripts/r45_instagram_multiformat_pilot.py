from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

import requests
from PIL import Image

WORKER = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"


def parse_time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def same_instant(a: str | None, b: str | None, tolerance_seconds: int = 90) -> bool:
    if not a or not b:
        return False
    try:
        return abs((parse_time(a).astimezone(dt.timezone.utc) - parse_time(b).astimezone(dt.timezone.utc)).total_seconds()) <= tolerance_seconds
    except Exception:
        return False


class Client:
    def __init__(self, key: str) -> None:
        self.key = key
        self.headers = {"x-lola-command-key": key, "accept": "application/json"}

    def post(self, path: str, payload: dict[str, Any], timeout: int = 600) -> tuple[int, dict[str, Any]]:
        r = requests.post(WORKER + path, headers={**self.headers, "content-type": "application/json"}, json=payload, timeout=timeout)
        try:
            data = r.json()
        except Exception:
            data = {"ok": False, "raw": r.text[:2000]}
        return r.status_code, data

    def get(self, path: str, timeout: int = 120) -> tuple[int, dict[str, Any]]:
        r = requests.get(WORKER + path, headers=self.headers, timeout=timeout)
        try:
            data = r.json()
        except Exception:
            data = {"ok": False, "raw": r.text[:2000]}
        return r.status_code, data


def image_dimensions(url: str) -> tuple[int, int, int]:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    raw = r.content
    with Image.open(BytesIO(raw)) as im:
        return int(im.width), int(im.height), len(raw)


def qa_draft(row: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    expected = str(row["type"])
    actual = str(draft.get("type") or "")
    issues: list[str] = []
    if actual != expected:
        issues.append(f"type_mismatch:{actual}")
    if draft.get("renderStatus") != "ready":
        issues.append(f"render_not_ready:{draft.get('renderStatus')}")
    if draft.get("semanticValidationRequired") is True and ((draft.get("semanticValidation") or {}).get("pass")) is not True:
        issues.append("semantic_validation_failed")
    if draft.get("legacyContentLeakDetected") is True:
        issues.append("legacy_content_leak")
    if (draft.get("copyLock") or {}).get("enabled") is True and ((draft.get("copyLockValidation") or {}).get("pass")) is not True:
        issues.append("copy_lock_failed")

    dimensions: list[dict[str, Any]] = []
    if actual == "carousel":
        urls = list(draft.get("imageUrls") or [])
        if not 4 <= len(urls) <= 10:
            issues.append(f"carousel_asset_count:{len(urls)}")
        for idx, url in enumerate(urls, 1):
            w, h, size = image_dimensions(url)
            dimensions.append({"index": idx, "width": w, "height": h, "bytes": size})
            if (w, h) != (1080, 1350):
                issues.append(f"carousel_dimension_{idx}:{w}x{h}")
            if size < 5000:
                issues.append(f"carousel_small_{idx}:{size}")
    else:
        url = str(draft.get("imageUrl") or "")
        if not url:
            issues.append("image_url_missing")
        else:
            w, h, size = image_dimensions(url)
            dimensions.append({"index": 1, "width": w, "height": h, "bytes": size})
            expected_size = (1080, 1920) if actual == "story_image" else (1080, 1350)
            if (w, h) != expected_size:
                issues.append(f"image_dimension:{w}x{h}:expected:{expected_size[0]}x{expected_size[1]}")
            if size < 5000:
                issues.append(f"image_small:{size}")

    return {"pass": not issues, "issues": issues, "dimensions": dimensions}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("manifest")
    p.add_argument("--receipt", default="control-plane/r45/receipts/pilot-latest.json")
    args = p.parse_args()

    key = os.environ.get("UGI_WORKER_COMMAND_KEY", "")
    if not key:
        raise SystemExit("UGI_WORKER_COMMAND_KEY missing")
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("project") != "UGI":
        raise SystemExit("PROJECT_ISOLATION_FAIL")
    rows = manifest.get("posts") or []
    if not rows:
        raise SystemExit("NO_POSTS")

    client = Client(key)
    results: list[dict[str, Any]] = []
    hard_fail = False

    for row in rows:
        cid = str(row.get("contentId") or "")
        item: dict[str, Any] = {"contentId": cid, "type": row.get("type"), "publish": row.get("publish") is True}
        try:
            payload = {
                "source": "UGI-R45-PILOT",
                "type": row["type"],
                "content_id": cid,
                "experiment_id": manifest.get("batchId"),
                "variant": row.get("variant", "A"),
                "topic": row["topic"],
                "objective": row.get("objective", "human_utility_first"),
                "audience": row.get("audience", "gestores e profissionais que usam IA no trabalho"),
                "hook": row.get("hook", ""),
                "key_message": row.get("key_message", ""),
                "instructions": row.get("instructions", ""),
                "cta": row.get("cta", ""),
                "slides": row.get("slides", 7),
                "editorial_mode": "human_utility_first",
                "commercial_offer": False,
            }
            code, generated = client.post("/api/r45/generate", payload, timeout=900)
            item["generateHttp"] = code
            item["generationOk"] = generated.get("ok") is True
            item["workerVersion"] = generated.get("version")
            draft = generated.get("draft") or {}
            item["draftId"] = draft.get("id")
            item["assetUrls"] = draft.get("imageUrls") or ([draft.get("imageUrl")] if draft.get("imageUrl") else [])
            if code != 200 or generated.get("ok") is not True or not draft.get("id"):
                raise RuntimeError("GENERATE_FAIL:" + json.dumps(generated, ensure_ascii=False)[:1600])

            qa = qa_draft(row, draft)
            item["qa"] = qa
            if not qa["pass"]:
                raise RuntimeError("QA_FAIL:" + "|".join(qa["issues"]))

            if row.get("publish") is not True:
                item["state"] = "ASSET_READY_NOT_PUBLISHED"
                item["ok"] = True
                results.append(item)
                continue

            code, approval = client.post("/api/r45/static-approval", {"id": draft["id"], "decision": "approved"}, timeout=120)
            item["approvalHttp"] = code
            item["approvalOk"] = approval.get("ok") is True
            if code != 200 or approval.get("ok") is not True:
                raise RuntimeError("APPROVAL_FAIL:" + json.dumps(approval, ensure_ascii=False)[:1600])

            due_at = str(row["dueAt"])
            code, published = client.post("/api/r45/static-publish", {"id": draft["id"], "mode": "customScheduled", "dueAt": due_at}, timeout=180)
            item["publishHttp"] = code
            item["publishResponse"] = published
            if code != 200 or published.get("ok") is not True:
                raise RuntimeError("PUBLISH_FAIL:" + json.dumps(published, ensure_ascii=False)[:2200])

            code, readback = client.get("/api/r45/static-publication-status?id=" + requests.utils.quote(str(draft["id"]), safe=""), timeout=120)
            item["readbackHttp"] = code
            publication = readback.get("publication") or {}
            buffer_id = publication.get("bufferPostId")
            status = str(publication.get("status") or "").lower()
            due_match = same_instant(publication.get("dueAt"), due_at)
            readback_pass = code == 200 and readback.get("ok") is True and bool(buffer_id) and status == "scheduled" and due_match
            item.update({
                "bufferPostId": buffer_id,
                "bufferStatus": publication.get("bufferStatus"),
                "publicationStatus": publication.get("status"),
                "dueAtRequested": due_at,
                "dueAtReadback": publication.get("dueAt"),
                "dueAtMatch": due_match,
                "externalLink": publication.get("externalLink"),
                "readbackPass": readback_pass,
                "state": "PROVEN_SCHEDULED" if readback_pass else "READBACK_FAILED",
                "ok": readback_pass,
            })
            if not readback_pass:
                raise RuntimeError("READBACK_FAIL:" + json.dumps(readback, ensure_ascii=False)[:1600])
        except Exception as exc:
            hard_fail = True
            item.setdefault("ok", False)
            item["error"] = f"{type(exc).__name__}:{exc}"
            item.setdefault("state", "FAILED")
        results.append(item)

    receipt = {
        "ok": not hard_fail and all(x.get("ok") is True for x in results),
        "project": "UGI",
        "component": "R45-INSTAGRAM-MULTIFORMAT-PILOT",
        "batchId": manifest.get("batchId"),
        "results": results,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    out = Path(args.receipt)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
