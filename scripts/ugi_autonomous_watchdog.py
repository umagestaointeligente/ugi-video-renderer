#!/usr/bin/env python3
"""Read-only UGI continuity watchdog: policy, runtime receipts and publisher gates."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPOSITORY = "umagestaointeligente/ugi-video-renderer"


def stop(message: str) -> None:
    raise SystemExit("HARD_STOP_UGI:" + message)


def load_optional(path: Path) -> dict | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        stop(f"INVALID_RECEIPT:{path.name}")
    return value


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def build_status(root: Path) -> dict:
    policy_path = root / "config" / "ugi" / "growth-policy.json"
    if not policy_path.is_file():
        stop("GROWTH_POLICY_MISSING")
    policy_bytes = policy_path.read_bytes()
    policy = json.loads(policy_bytes)
    roles = policy.get("integration_roles", {})
    publisher = roles.get("publisher", {})
    analytics = roles.get("analytics", {})
    if publisher.get("primary") != "buffer" or publisher.get("metricool_allowed") is not False:
        stop("BUFFER_PUBLICATION_LOCK")
    if analytics.get("primary") != "metricool" or analytics.get("publishing_allowed") is not False:
        stop("METRICOOL_READONLY_LOCK")
    recovery = policy.get("publication_recovery", {})
    if recovery.get("publisher") != "buffer" or recovery.get("metricool_retry_forbidden") is not True:
        stop("RECOVERY_PROVIDER_LOCK")
    if int(recovery.get("max_attempts_total", 0)) < 1:
        stop("RECOVERY_ATTEMPT_POLICY")

    growth = load_optional(root / "control-plane" / "receipts" / "ugi-growth-engine" / "latest.json")
    buffer_today = load_optional(root / "control-plane" / "receipts" / "ugi-buffer" / "today.json")
    generation = load_optional(root / "control-plane" / "receipts" / "ugi-today" / "generation.json")
    incidents: list[dict] = []
    policy_hash = hashlib.sha256(policy_bytes).hexdigest()
    if growth is None:
        incidents.append({"class": "GROWTH_RUNTIME_EVIDENCE_MISSING", "severity": "high"})
    elif growth.get("SMOKE_TEST_PASS") is not True:
        incidents.append({"class": "GROWTH_RUNTIME_SMOKE_FAILED", "severity": "high"})
    elif growth.get("policy_sha256") != policy_hash:
        incidents.append({"class": "GROWTH_RUNTIME_POLICY_HASH_STALE", "severity": "high"})

    if buffer_today and buffer_today.get("ok") is False:
        incidents.append({
            "class": "BUFFER_AUTH_OR_READBACK_UNAVAILABLE",
            "severity": "high",
            "error": str(buffer_today.get("error", "UNKNOWN"))[:180],
        })

    results = generation.get("results", []) if generation else []
    forbidden = [row for row in results if "403" in str(row.get("error", ""))]
    generation_time = parse_timestamp(generation.get("generated_at")) if generation else None
    buffer_time = parse_timestamp(buffer_today.get("timestamp")) if buffer_today else None
    newer_auth_proof = bool(
        buffer_today
        and buffer_today.get("ok") is True
        and buffer_today.get("drafts_http") == 200
        and buffer_today.get("channels_http") == 200
        and buffer_time
        and generation_time
        and buffer_time >= generation_time
    )
    if forbidden and not newer_auth_proof:
        incidents.append({
            "class": "WORKER_COMMAND_AUTH_REJECTED",
            "severity": "high",
            "platforms": sorted({str(row.get("platform")) for row in forbidden}),
        })

    return {
        "schema_version": "1.0",
        "project": "UGI",
        "repository_lock": REPOSITORY,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "DEGRADED" if incidents else "HEALTHY",
        "publication_provider": "BUFFER",
        "analytics_provider": "METRICOOL",
        "metricool_publication_allowed": False,
        "public_publish_triggered": False,
        "payment_triggered": False,
        "growth_runtime_evidence_present": growth is not None,
        "growth_policy_sha256": policy_hash,
        "recovery_max_attempts": recovery["max_attempts_total"],
        "current_readonly_auth_verified": newer_auth_proof,
        "multi_ai_existing": (root / "magic-engine" / "multi_ai_council.py").is_file(),
        "incidents": incidents,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=None)
    arguments = parser.parse_args()
    if os.getenv("GITHUB_REPOSITORY") not in (None, REPOSITORY):
        stop("RUNTIME_REPOSITORY_LOCK")
    root = arguments.root.resolve()
    payload = build_status(root)
    path = arguments.output or root / "output" / "ugi" / "autonomous-watchdog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
