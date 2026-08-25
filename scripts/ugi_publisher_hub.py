#!/usr/bin/env python3
"""UGI Publisher Hub.

Canonical publication orchestrator for UGI. It owns manifest validation,
Buffer scheduling through the deployed UGI Worker, live readback and receipts.

The script is intentionally fail-closed:
- project must be UGI;
- Buffer must remain the exclusive publisher;
- Metricool must remain analytics-only;
- Worker health and Buffer channels must be proven before mutation;
- a publication is successful only after Buffer readback returns a post id and slot.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import time
import urllib.parse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_QUEUE = ROOT / "control-plane" / "publisher-hub" / "queue"
LEGACY_QUEUE = ROOT / "control-plane" / "chat-publication"
RECEIPTS = ROOT / "control-plane" / "publisher-hub" / "receipts"
STATUS = ROOT / "control-plane" / "publisher-hub" / "status" / "latest.json"
GROWTH_POLICY = ROOT / "config" / "ugi" / "growth-policy.json"
ROUTING_POLICY = ROOT / "config" / "ugi" / "integration-routing.json"

DEFAULT_WORKER_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
                "raw": p.stdout[:1600],
                "stderr": p.stderr[:800],
                "returncode": p.returncode,
            }
        if p.returncode != 0 and data.get("ok") is not False:
            data["ok"] = False
            data["returncode"] = p.returncode
            data["stderr"] = p.stderr[:800]
        return data

    def get(self, path: str) -> dict[str, Any]:
        return self._run([
            "curl", "--silent", "--show-error", "--location", "--max-time", "90",
            "-A", "UGI-Publisher-Hub/1.0",
            "-H", f"x-lola-command-key: {self.key}",
            "-H", "accept: application/json",
            self.base_url + path,
        ])

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._run([
            "curl", "--silent", "--show-error", "--location", "--max-time", "90",
            "-A", "UGI-Publisher-Hub/1.0",
            "-H", f"x-lola-command-key: {self.key}",
            "-H", "accept: application/json",
            "-H", "content-type: application/json",
            "--data-binary", json.dumps(payload, ensure_ascii=False),
            self.base_url + path,
        ])


def validate_global_policy() -> tuple[dict[str, Any], dict[str, Any]]:
    growth = load_json(GROWTH_POLICY)
    routing = load_json(ROUTING_POLICY)

    if growth.get("project") not in (None, "UGI"):
        raise SystemExit("GROWTH_POLICY_PROJECT_ISOLATION_FAIL")
    pub = ((routing.get("routing_policy") or {}).get("publishing") or {})
    analytics = ((routing.get("routing_policy") or {}).get("analytics") or {})
    if str(pub.get("provider", "")).lower() != "buffer" or pub.get("exclusive") is not True:
        raise SystemExit("BUFFER_ROUTING_POLICY_FAIL")
    if pub.get("fail_closed_if_unavailable") is not True:
        raise SystemExit("BUFFER_FAIL_CLOSED_POLICY_FAIL")
    if str(analytics.get("provider", "")).lower() == "metricool" and analytics.get("read_only") is not True:
        raise SystemExit("METRICOOL_READ_ONLY_POLICY_FAIL")

    integration = growth.get("integration_roles") or {}
    primary = ((integration.get("publisher") or {}).get("primary"))
    if primary is not None and str(primary).lower() != "buffer":
        raise SystemExit("GROWTH_POLICY_BUFFER_FAIL")

    analytics_role = integration.get("analytics") or {}
    if analytics_role.get("publishing_allowed") not in (None, False):
        raise SystemExit("GROWTH_POLICY_METRICOOL_FAIL")

    return growth, routing


def validate_manifest(data: dict[str, Any], manifest: Path) -> list[dict[str, Any]]:
    if data.get("project") != "UGI":
        raise SystemExit(f"PROJECT_ISOLATION_FAIL:{manifest}")
    rows = data.get("posts") or []
    if not isinstance(rows, list) or not rows:
        raise SystemExit(f"NO_POSTS:{manifest}")

    seen: set[tuple[str, str]] = set()
    required = {"contentId", "platform", "dueAt"}
    for idx, row in enumerate(rows):
        missing = required - set(row)
        if missing:
            raise SystemExit(f"MANIFEST_FIELDS_MISSING:{manifest}:{idx}:{sorted(missing)}")
        slot = (str(row["platform"]).lower(), str(row["dueAt"]))
        if slot in seen:
            raise SystemExit(f"MANIFEST_DUPLICATE_SLOT:{manifest}:{slot}")
        seen.add(slot)
    return rows


def discover_manifests(explicit: str | None) -> list[Path]:
    if explicit:
        p = (ROOT / explicit).resolve() if not Path(explicit).is_absolute() else Path(explicit)
        if ROOT not in p.parents:
            raise SystemExit("MANIFEST_OUTSIDE_REPO")
        if not p.exists():
            raise SystemExit(f"MANIFEST_NOT_FOUND:{p}")
        return [p]

    candidates: list[Path] = []
    for folder in (CANONICAL_QUEUE, LEGACY_QUEUE):
        if folder.exists():
            candidates.extend(sorted(folder.glob("*.json")))
    return candidates


def receipt_path(data: dict[str, Any], manifest: Path) -> Path:
    rid = str(data.get("batchId") or manifest.stem)
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in rid)
    return RECEIPTS / f"{safe}.json"


def is_terminal_success(path: Path, manifest_hash: str) -> bool:
    if not path.exists():
        return False
    try:
        old = load_json(path)
    except Exception:
        return False
    return (
        old.get("ok") is True
        and old.get("manifestSha256") == manifest_hash
        and all(x.get("readbackPass") is True for x in (old.get("results") or []))
    )


def resolve_ready_drafts(client: WorkerClient, rows: list[dict[str, Any]], wait_seconds: int) -> tuple[bool, dict[str, dict[str, Any]]]:
    deadline = time.time() + max(0, wait_seconds)
    first = True
    last: dict[str, dict[str, Any]] = {}
    while first or time.time() < deadline:
        first = False
        drafts_resp = client.get("/api/drafts")
        if not drafts_resp.get("ok") and "drafts" not in drafts_resp:
            return False, {}
        drafts = drafts_resp.get("drafts") or []
        resolved: dict[str, dict[str, Any]] = {}
        ready = True
        for row in rows:
            cid = str(row["contentId"])
            plat = str(row["platform"]).lower()
            matches = [d for d in drafts if str(d.get("contentId") or d.get("content_id") or "") == cid]
            matches.sort(key=lambda d: str(d.get("updatedAt") or d.get("createdAt") or ""), reverse=True)
            if not matches:
                ready = False
                continue
            draft = matches[0]
            resolved[cid] = draft
            asset = (draft.get("assets") or {}).get(plat) or {}
            if not (draft.get("allPlatformsReady") is True and asset.get("ready") is True and asset.get("videoUrl")):
                ready = False
        last = resolved
        if ready:
            return True, resolved
        if time.time() >= deadline:
            break
        time.sleep(min(20, max(1, deadline - time.time())))
    return False, last


def process_manifest(client: WorkerClient, manifest: Path, growth: dict[str, Any], routing: dict[str, Any], wait_seconds: int) -> dict[str, Any]:
    data = load_json(manifest)
    rows = validate_manifest(data, manifest)
    mf_hash = canonical_hash(manifest)
    receipt = receipt_path(data, manifest)

    if is_terminal_success(receipt, mf_hash):
        previous = load_json(receipt)
        previous["skippedAsAlreadyProven"] = True
        return previous

    health = client.get("/api/health")
    if not health.get("ok"):
        raise RuntimeError("WORKER_HEALTH_FAIL")

    channels = client.get("/api/buffer/channels")
    if not channels.get("ok"):
        raise RuntimeError("BUFFER_CHANNELS_FAIL")

    ready, resolved = resolve_ready_drafts(client, rows, wait_seconds)
    if not ready:
        result = {
            "ok": False,
            "retryable": True,
            "state": "WAITING_FOR_RENDER",
            "project": "UGI",
            "publisher": "BUFFER",
            "manifest": str(manifest.relative_to(ROOT)),
            "manifestSha256": mf_hash,
            "policyId": growth.get("policy_id"),
            "policySchema": growth.get("schema_version"),
            "policySha256": canonical_hash(GROWTH_POLICY),
            "routingSha256": canonical_hash(ROUTING_POLICY),
            "publicationTriggered": False,
            "paymentTriggered": False,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "results": [],
        }
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result

    results: list[dict[str, Any]] = []
    for row in rows:
        cid = str(row["contentId"])
        plat = str(row["platform"]).lower()
        due = str(row["dueAt"])
        draft = resolved[cid]
        draft_id = str(draft["id"])
        asset = (draft.get("assets") or {}).get(plat) or {}
        existing = asset.get("publication") or {}

        if existing.get("bufferPostId") and str(existing.get("status", "")).lower() not in {"error", "cancelled"}:
            publish = {"ok": True, "publication": existing, "alreadyActive": True}
        else:
            approval = client.post("/api/platform-approval", {"id": draft_id, "platform": plat, "decision": "approved"})
            if not approval.get("ok"):
                results.append({"contentId": cid, "platform": plat, "ok": False, "gate": "APPROVAL", "detail": approval})
                continue

            eligibility = client.get("/api/platform-publication-eligibility/" + urllib.parse.quote(draft_id))
            state = ((eligibility.get("platformStates") or {}).get(plat) or {})
            if not state.get("eligible"):
                results.append({"contentId": cid, "platform": plat, "ok": False, "gate": "ELIGIBILITY", "detail": state})
                continue

            publish = client.post("/api/platform-publish", {"id": draft_id, "platform": plat, "mode": "customScheduled", "dueAt": due})

        if not publish.get("ok"):
            results.append({"contentId": cid, "platform": plat, "ok": False, "gate": "BUFFER_CREATE", "detail": publish})
            continue

        readback = client.get(
            "/api/platform-publication-status?id=" + urllib.parse.quote(draft_id)
            + "&platform=" + urllib.parse.quote(plat)
        )
        publication = readback.get("publication") or publish.get("publication") or {}
        passed = bool(publication.get("bufferPostId")) and str(publication.get("dueAt") or "")[:16] == due[:16]
        results.append({
            "contentId": cid,
            "platform": plat,
            "draftId": draft_id,
            "dueAt": publication.get("dueAt"),
            "bufferPostId": publication.get("bufferPostId"),
            "status": publication.get("bufferStatus") or publication.get("status"),
            "externalLink": publication.get("externalLink"),
            "readbackPass": passed,
            "ok": passed,
        })

    ok = bool(results) and all(x.get("ok") for x in results)
    out = {
        "ok": ok,
        "retryable": not ok,
        "state": "PROVEN_SCHEDULED" if ok else "DEGRADED",
        "project": "UGI",
        "publisher": "BUFFER",
        "publisherHub": "UGI-PUBLISHER-HUB",
        "metricoolPublicationAllowed": False,
        "manifest": str(manifest.relative_to(ROOT)),
        "manifestSha256": mf_hash,
        "policyId": growth.get("policy_id"),
        "policySchema": growth.get("schema_version"),
        "policySha256": canonical_hash(GROWTH_POLICY),
        "routingSchema": routing.get("schema_version"),
        "routingSha256": canonical_hash(ROUTING_POLICY),
        "publicationTriggered": True,
        "paymentTriggered": False,
        "results": results,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def write_status(results: list[dict[str, Any]]) -> None:
    proven = sum(1 for x in results if x.get("ok") is True)
    waiting = sum(1 for x in results if x.get("state") == "WAITING_FOR_RENDER")
    degraded = sum(1 for x in results if x.get("ok") is not True and x.get("state") != "WAITING_FOR_RENDER")
    state = "READY" if degraded == 0 and waiting == 0 else ("WAITING" if degraded == 0 else "DEGRADED")
    payload = {
        "project": "UGI",
        "component": "UGI-PUBLISHER-HUB",
        "state": state,
        "manifestsSeen": len(results),
        "proven": proven,
        "waitingForRender": waiting,
        "degraded": degraded,
        "publisher": "BUFFER",
        "metricoolPublicationAllowed": False,
        "chatRuntimeRequired": False,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", help="repo-relative manifest path")
    parser.add_argument("--wait-seconds", type=int, default=int(os.getenv("UGI_PUBLISHER_WAIT_SECONDS", "0")))
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    growth, routing = validate_global_policy()
    manifests = discover_manifests(args.manifest)

    if args.validate_only:
        for manifest in manifests:
            validate_manifest(load_json(manifest), manifest)
        print(json.dumps({
            "ok": True,
            "project": "UGI",
            "component": "UGI-PUBLISHER-HUB",
            "manifestsValidated": len(manifests),
            "publisher": "BUFFER",
            "chatRuntimeRequired": False,
        }))
        return 0

    key = os.getenv("UGI_LOLA_COMMAND_KEY", "")
    if not key:
        raise SystemExit("UGI_LOLA_COMMAND_KEY_MISSING")
    client = WorkerClient(os.getenv("WORKER_URL", DEFAULT_WORKER_URL), key)

    results: list[dict[str, Any]] = []
    hard_fail = False
    for manifest in manifests:
        try:
            result = process_manifest(client, manifest, growth, routing, max(0, args.wait_seconds))
        except Exception as exc:
            result = {
                "ok": False,
                "retryable": True,
                "state": "DEGRADED",
                "project": "UGI",
                "publisher": "BUFFER",
                "manifest": str(manifest.relative_to(ROOT)),
                "publicationTriggered": False,
                "paymentTriggered": False,
                "error": f"{type(exc).__name__}:{exc}",
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            hard_fail = True
            try:
                data = load_json(manifest)
                receipt = receipt_path(data, manifest)
                receipt.parent.mkdir(parents=True, exist_ok=True)
                receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            except Exception:
                pass
        results.append(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    write_status(results)

    if hard_fail or any(r.get("ok") is not True and r.get("state") != "WAITING_FOR_RENDER" for r in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
