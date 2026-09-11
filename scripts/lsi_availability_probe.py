#!/usr/bin/env python3
"""Fail-closed availability probe for the Cloudflare/GitHub LSI fallback."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


BROKER = "https://lsi-zero-cost-broker.umagestaointeligente.workers.dev"
CORE = "https://lsi-hyperwork-core.umagestaointeligente.workers.dev"
OUTPUT = Path("generated/evidence/lsi-availability-latest.json")


def request_json(url: str, *, method: str = "GET", body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "User-Agent": "LSIAvailabilityProbe/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        payload = json.loads(error.read().decode("utf-8"))
        return error.code, payload


def main() -> int:
    checked_at = datetime.now(timezone.utc).isoformat()
    checks: dict[str, dict] = {}
    errors: list[str] = []

    try:
        status, payload = request_json(f"{BROKER}/health")
        passed = (
            status == 200
            and payload.get("ok") is True
            and payload.get("workers_ai_bound") is True
            and payload.get("broker_key_configured") is True
            and payload.get("external_paid_provider") is False
        )
        checks["broker_health"] = {"pass": passed, "http": status, "version": payload.get("version")}
        if not passed:
            errors.append("broker_health_failed")
    except Exception as error:  # network/JSON errors are availability failures
        checks["broker_health"] = {"pass": False, "error": type(error).__name__}
        errors.append("broker_health_unavailable")

    try:
        status, payload = request_json(f"{CORE}/health")
        passed = (
            status == 200
            and payload.get("ok") is True
            and payload.get("durable_objects_bound") is True
            and payload.get("workers_ai_bound") is True
            and payload.get("security_sentinel") is True
            and payload.get("background_engine") is True
            and payload.get("zero_cost_policy") is True
            and payload.get("production_actions") is False
            and payload.get("external_paid_provider") is False
            and payload.get("auth") == "github_oidc"
        )
        checks["core_health"] = {"pass": passed, "http": status, "version": payload.get("version")}
        if not passed:
            errors.append("core_health_failed")
    except Exception as error:
        checks["core_health"] = {"pass": False, "error": type(error).__name__}
        errors.append("core_health_unavailable")

    try:
        status, payload = request_json(
            f"{BROKER}/v1/execute",
            method="POST",
            body={"mission_id": "availability-auth-gate"},
        )
        passed = status == 401 and payload.get("error") == "oidc_denied"
        checks["broker_auth_gate"] = {
            "pass": passed,
            "http": status,
            "expected": "github_oidc_required",
        }
        if not passed:
            errors.append("broker_auth_gate_failed")
    except Exception as error:
        checks["broker_auth_gate"] = {"pass": False, "error": type(error).__name__}
        errors.append("broker_auth_gate_unavailable")

    result = {
        "schema_version": "1.0",
        "checked_at": checked_at,
        "status": "PASS" if not errors else "FAIL",
        "scope": "fallback_cloudflare_github",
        "checks": checks,
        "execution_access": "github_actions_oidc_only",
        "chat_direct_connector": False,
        "canonical_productos_status": "not_checked_by_this_probe",
        "production_actions": False,
        "errors": errors,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"LSI_FALLBACK_AVAILABILITY={result['status']}")
    print(f"LSI_EXECUTION_ACCESS={result['execution_access']}")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
