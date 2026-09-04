#!/usr/bin/env python3
"""UGI Publisher Hub.

Canonical publication orchestrator for UGI. It owns manifest validation,
Buffer scheduling through the deployed UGI Worker, live readback and receipts.

The script is intentionally fail-closed:
- project must be UGI;
- Buffer must remain the exclusive publisher;
- Metricool must remain analytics-only;
- Worker health must be proven before mutation; Buffer is proven on the actual per-post create/readback path;
- content -> render -> draft correlation must be proven before approval;
- a publication is successful only after Buffer readback returns a post id,
  scheduled state and the exact requested slot.
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
RENDER_STATE = ROOT / "control-plane" / "publisher-hub" / "render-state"
RECEIPTS = ROOT / "control-plane" / "publisher-hub" / "receipts"
STATUS = ROOT / "control-plane" / "publisher-hub" / "status" / "latest.json"
GROWTH_POLICY = ROOT / "config" / "ugi" / "growth-policy.json"
ROUTING_POLICY = ROOT / "config" / "ugi" / "integration-routing.json"
DISTRIBUTION_STATE = ROOT / "config" / "ugi" / "distribution-state.json"

DEFAULT_WORKER_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
STALE_QUEUE_HOURS = int(os.getenv("UGI_QUEUE_STALE_HOURS", "6"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value)


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
            "-A", "UGI-Publisher-Hub/1.1",
            "-H", f"x-lola-command-key: {self.key}",
            "-H", "accept: application/json",
            self.base_url + path,
        ])

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._run([
            "curl", "--silent", "--show-error", "--location", "--max-time", "90",
            "-A", "UGI-Publisher-Hub/1.1",
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


def _due_at(value: Any) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def manifest_is_stale(path: Path) -> bool:
    try:
        rows = (load_json(path).get("posts") or [])
    except Exception:
        return False
    dues = [_due_at(row.get("dueAt")) for row in rows]
    dues = [x for x in dues if x is not None]
    if not dues:
        return False
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=max(1, STALE_QUEUE_HOURS))
    return max(dues) < cutoff


def discover_manifests(explicit: str | None) -> list[Path]:
    if explicit:
        p = (ROOT / explicit).resolve() if not Path(explicit).is_absolute() else Path(explicit)
        if ROOT not in p.parents:
            raise SystemExit("MANIFEST_OUTSIDE_REPO")
        if not p.exists():
            raise SystemExit(f"MANIFEST_NOT_FOUND:{p}")
        return [p]

    # Canonical queue is authoritative. Once it exists, never fall back to the
    # legacy chat queue. Expired manifests remain durable history but are not
    # allowed to block or trigger unattended late publication.
    if CANONICAL_QUEUE.exists():
        canonical = sorted(CANONICAL_QUEUE.glob("*.json"))
        return [p for p in canonical if not manifest_is_stale(p)]
    return sorted(LEGACY_QUEUE.glob("*.json")) if LEGACY_QUEUE.exists() else []


def receipt_path(data: dict[str, Any], manifest: Path) -> Path:
    rid = str(data.get("batchId") or manifest.stem)
    return RECEIPTS / f"{safe_name(rid)}.json"


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


def _target_from_render_state(
    client: WorkerClient,
    content_id: str,
    platform: str,
) -> dict[str, Any] | None:
    state_file = RENDER_STATE / f"{safe_name(content_id)}.json"
    if not state_file.exists():
        return None

    state = load_json(state_file)
    render_id = str(state.get("workerRenderId") or "").strip()
    expected_draft_id = str(state.get("approvalDraftId") or "").strip()
    if not render_id or not expected_draft_id:
        return None

    video = client.get("/api/video-result/" + urllib.parse.quote(render_id))
    asset = ((video.get("assets") or {}).get(platform) or {})
    if not (
        video.get("ok") is True
        and video.get("allPlatformsReady") is True
        and asset.get("ready") is True
        and asset.get("videoUrl")
    ):
        return None

    # Strict video/copy QA proof before any approval mutation.
    if video.get("semanticValidationRequired") is True:
        if video.get("semanticValidationAvailable") is not True:
            return None
        if ((video.get("semanticValidation") or {}).get("pass")) is not True:
            raise RuntimeError(f"SEMANTIC_VALIDATION_FAIL:{content_id}")
    if ((video.get("copyLock") or {}).get("enabled")) is True:
        if ((video.get("copyLockValidation") or {}).get("pass")) is not True:
            raise RuntimeError(f"COPY_LOCK_VALIDATION_FAIL:{content_id}")
    if video.get("legacyContentLeakDetected") is True:
        raise RuntimeError(f"LEGACY_CONTENT_LEAK_FAIL:{content_id}")

    # Correlate contentId -> draftId via the paginated Worker lookup rather
    # than /api/drafts, whose collection endpoint is capped.
    lookup = client.get(
        "/api/draft-lookup?content_id=" + urllib.parse.quote(content_id)
    )
    if lookup.get("ok") is not True or lookup.get("found") is not True:
        return None

    live_draft_id = str(lookup.get("draftId") or "").strip()
    if not live_draft_id:
        return None
    if live_draft_id != expected_draft_id:
        raise RuntimeError(
            f"DRAFT_CORRELATION_MISMATCH:{content_id}:{expected_draft_id}:{live_draft_id}"
        )

    eligibility = client.get(
        "/api/platform-publication-eligibility/" + urllib.parse.quote(live_draft_id)
    )
    if eligibility.get("ok") is not True:
        return None
    pstate = ((eligibility.get("platformStates") or {}).get(platform) or {})
    if pstate.get("assetExists") is not True or pstate.get("ready") is not True:
        return None

    return {
        "id": live_draft_id,
        "renderId": render_id,
        "eligibility": pstate,
        "videoStatus": video.get("status"),
        "allPlatformsReady": video.get("allPlatformsReady") is True,
    }


def resolve_ready_drafts(
    client: WorkerClient,
    rows: list[dict[str, Any]],
    wait_seconds: int,
) -> tuple[bool, dict[str, dict[str, Any]]]:
    deadline = time.time() + max(0, wait_seconds)
    first = True
    last: dict[str, dict[str, Any]] = {}

    while first or time.time() < deadline:
        first = False
        resolved: dict[str, dict[str, Any]] = {}
        ready = True

        for row in rows:
            cid = str(row["contentId"])
            plat = str(row["platform"]).lower()
            target = _target_from_render_state(client, cid, plat)
            if target is None:
                ready = False
                continue
            resolved[cid] = target

        last = resolved
        if ready and len(resolved) == len(rows):
            return True, resolved
        if time.time() >= deadline:
            break
        time.sleep(min(20, max(1, deadline - time.time())))

    return False, last


def _scheduled_readback_pass(readback: dict[str, Any], requested_due: str) -> tuple[bool, dict[str, Any]]:
    publication = readback.get("publication") or {}
    status = str(publication.get("status") or "").lower()

    # Buffer can return the same scheduled instant in UTC (Z) while the
    # canonical manifest keeps America/Sao_Paulo (-03:00). Compare absolute
    # instants, never wall-clock strings, so 09:00-03:00 == 12:00Z.
    requested_instant = _due_at(requested_due)
    buffer_instant = _due_at(publication.get("dueAt"))
    exact_instant = (
        requested_instant is not None
        and buffer_instant is not None
        and requested_instant == buffer_instant
    )

    passed = (
        readback.get("ok") is True
        and bool(publication.get("bufferPostId"))
        and exact_instant
        and status == "scheduled"
    )
    return passed, publication



def _filter_distribution_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Allow publication only to currently active Buffer distribution platforms.

    Paused platforms are intentionally skipped without blocking active platforms in
    the same historical manifest. Unknown platforms fail closed by being skipped
    whenever an explicit active set exists.
    """
    if not DISTRIBUTION_STATE.exists():
        return rows, []
    state = load_json(DISTRIBUTION_STATE)
    buffer_state = state.get("buffer") or {}
    active = {str(x).lower() for x in (buffer_state.get("active_platforms") or [])}
    paused = {str(x).lower() for x in (buffer_state.get("paused_platforms") or [])}
    allowed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for row in rows:
        platform = str(row.get("platform") or "").lower()
        if platform in paused or (active and platform not in active):
            skipped.append({
                "contentId": row.get("contentId"),
                "platform": platform,
                "dueAt": row.get("dueAt"),
                "reason": "PLATFORM_DISTRIBUTION_PAUSED_OR_INACTIVE",
            })
            continue
        allowed.append(row)
    return allowed, skipped

def process_manifest(
    client: WorkerClient,
    manifest: Path,
    growth: dict[str, Any],
    routing: dict[str, Any],
    wait_seconds: int,
) -> dict[str, Any]:
    data = load_json(manifest)
    rows = validate_manifest(data, manifest)
    mf_hash = canonical_hash(manifest)
    receipt = receipt_path(data, manifest)

    rows, distribution_skipped = _filter_distribution_rows(rows)
    if not rows:
        result = {
            "ok": True,
            "retryable": False,
            "state": "SKIPPED_BY_DISTRIBUTION_POLICY",
            "project": "UGI",
            "publisher": "BUFFER",
            "manifest": str(manifest.relative_to(ROOT)),
            "manifestSha256": mf_hash,
            "publicationTriggered": False,
            "paymentTriggered": False,
            "expectedTargets": 0,
            "results": [],
            "distributionSkipped": distribution_skipped,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result

    if is_terminal_success(receipt, mf_hash):
        previous = load_json(receipt)
        previous["skippedAsAlreadyProven"] = True
        return previous

    health = client.get("/api/health")
    if not health.get("ok"):
        raise RuntimeError("WORKER_HEALTH_FAIL")

    # Buffer channel discovery is not a global hard gate. The Worker owns
    # canonical channel resolution; the authoritative proof is the actual
    # per-post /api/platform-publish response followed by scheduled readback.
    # A real Buffer create/readback failure still fails closed below.

    ready, resolved = resolve_ready_drafts(client, rows, wait_seconds)
    if not ready:
        result = {
            "ok": False,
            "retryable": True,
            "state": "WAITING_FOR_RENDER_OR_DRAFT",
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
            "resolvedTargets": len(resolved),
            "expectedTargets": len(rows),
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "results": [],
        }
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result

    results: list[dict[str, Any]] = []
    any_mutation = False

    for row in rows:
        cid = str(row["contentId"])
        plat = str(row["platform"]).lower()
        due = str(row["dueAt"])
        target = resolved[cid]
        draft_id = str(target["id"])
        pre = target.get("eligibility") or {}

        # Exactly-once: if Worker already reports an active Buffer post, do not
        # approve or create another one; prove the existing post by readback.
        active_id = str(pre.get("bufferPostId") or "").strip()
        active_status = str(pre.get("publicationStatus") or "").lower()
        if active_id and active_status not in {"error", "cancelled"}:
            readback = client.get(
                "/api/platform-publication-status?id=" + urllib.parse.quote(draft_id)
                + "&platform=" + urllib.parse.quote(plat)
            )
            passed, publication = _scheduled_readback_pass(readback, due)
            results.append({
                "contentId": cid,
                "platform": plat,
                "draftId": draft_id,
                "renderId": target.get("renderId"),
                "dueAt": publication.get("dueAt"),
                "bufferPostId": publication.get("bufferPostId"),
                "status": publication.get("status"),
                "bufferStatus": publication.get("bufferStatus"),
                "externalLink": publication.get("externalLink"),
                "alreadyActive": True,
                "readbackPass": passed,
                "ok": passed,
            })
            continue

        # Before approval, only pending_approval is acceptable as a blocker.
        pre_reasons = set(pre.get("reasons") or [])
        unexpected_pre = pre_reasons - {"pending_approval"}
        if unexpected_pre:
            results.append({
                "contentId": cid,
                "platform": plat,
                "draftId": draft_id,
                "ok": False,
                "gate": "PRE_APPROVAL_ELIGIBILITY",
                "detail": pre,
            })
            continue

        if str(pre.get("approvalStatus") or "").lower() != "approved":
            approval = client.post(
                "/api/platform-approval",
                {"id": draft_id, "platform": plat, "decision": "approved"},
            )
            if not approval.get("ok"):
                results.append({
                    "contentId": cid,
                    "platform": plat,
                    "draftId": draft_id,
                    "ok": False,
                    "gate": "APPROVAL",
                    "detail": approval,
                })
                continue
            any_mutation = True

        eligibility = client.get(
            "/api/platform-publication-eligibility/" + urllib.parse.quote(draft_id)
        )
        state = ((eligibility.get("platformStates") or {}).get(plat) or {})

        # Another exactly-once check after approval, before create.
        if state.get("bufferPostId") and str(state.get("publicationStatus") or "").lower() not in {"error", "cancelled"}:
            readback = client.get(
                "/api/platform-publication-status?id=" + urllib.parse.quote(draft_id)
                + "&platform=" + urllib.parse.quote(plat)
            )
            passed, publication = _scheduled_readback_pass(readback, due)
            results.append({
                "contentId": cid,
                "platform": plat,
                "draftId": draft_id,
                "renderId": target.get("renderId"),
                "dueAt": publication.get("dueAt"),
                "bufferPostId": publication.get("bufferPostId"),
                "status": publication.get("status"),
                "bufferStatus": publication.get("bufferStatus"),
                "externalLink": publication.get("externalLink"),
                "alreadyActive": True,
                "readbackPass": passed,
                "ok": passed,
            })
            continue

        if eligibility.get("ok") is not True or not state.get("eligible"):
            results.append({
                "contentId": cid,
                "platform": plat,
                "draftId": draft_id,
                "ok": False,
                "gate": "ELIGIBILITY",
                "detail": state,
            })
            continue

        publish = client.post(
            "/api/platform-publish",
            {
                "id": draft_id,
                "platform": plat,
                "format": row.get("format"),
                "mode": "customScheduled",
                "dueAt": due,
            },
        )
        if not publish.get("ok"):
            results.append({
                "contentId": cid,
                "platform": plat,
                "draftId": draft_id,
                "ok": False,
                "gate": "BUFFER_CREATE",
                "detail": publish,
            })
            continue
        any_mutation = True

        readback = client.get(
            "/api/platform-publication-status?id=" + urllib.parse.quote(draft_id)
            + "&platform=" + urllib.parse.quote(plat)
        )
        passed, publication = _scheduled_readback_pass(readback, due)
        results.append({
            "contentId": cid,
            "platform": plat,
            "draftId": draft_id,
            "renderId": target.get("renderId"),
            "dueAt": publication.get("dueAt"),
            "bufferPostId": publication.get("bufferPostId"),
            "status": publication.get("status"),
            "bufferStatus": publication.get("bufferStatus"),
            "externalLink": publication.get("externalLink"),
            "alreadyActive": False,
            "readbackPass": passed,
            "ok": passed,
        })

    ok = len(results) == len(rows) and all(x.get("ok") for x in results)
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
        "publicationTriggered": any_mutation,
        "paymentTriggered": False,
        "results": results,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def write_status(results: list[dict[str, Any]]) -> None:
    proven = sum(1 for x in results if x.get("ok") is True)
    waiting = sum(
        1 for x in results
        if x.get("state") in {"WAITING_FOR_RENDER", "WAITING_FOR_RENDER_OR_DRAFT"}
    )
    degraded = sum(
        1 for x in results
        if x.get("ok") is not True
        and x.get("state") not in {"WAITING_FOR_RENDER", "WAITING_FOR_RENDER_OR_DRAFT"}
    )
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

    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY", "")
    if not key:
        raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")
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

    waiting_states = {"WAITING_FOR_RENDER", "WAITING_FOR_RENDER_OR_DRAFT"}
    if hard_fail or any(r.get("ok") is not True and r.get("state") not in waiting_states for r in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
