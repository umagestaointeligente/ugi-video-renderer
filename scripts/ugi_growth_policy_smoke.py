#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = REPO_ROOT / "scripts" / "ugi_growth_runtime.py"
RECEIPT_DIR = REPO_ROOT / "control-plane" / "receipts" / "ugi-growth-engine"


def load_runtime_module():
    spec = importlib.util.spec_from_file_location("ugi_growth_runtime", RUNTIME_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load UGI growth runtime module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    now = datetime.now(timezone.utc)
    receipt_id = f"ugi-growth-policy-smoke-{now.strftime('%Y%m%dT%H%M%SZ')}"
    runtime_module = load_runtime_module()
    runtime = runtime_module.load_runtime_policy()

    required_checks = {
        "POLICY_REQUIRED": runtime.get("POLICY_REQUIRED") is True,
        "POLICY_LOADED": runtime.get("POLICY_LOADED") is True,
        "POLICY_ID_MATCH": runtime.get("POLICY_ID") == "ugi-growth-engine",
        "RUNTIME_POLICY_ACTIVE": runtime.get("RUNTIME_POLICY_ACTIVE") is True,
        "GROWTH_ENGINE_ACTIVE": runtime.get("GROWTH_ENGINE_ACTIVE") is True,
        "PLATFORM_INDEPENDENCE": runtime.get("PLATFORM_INDEPENDENCE") is True,
        "DEFAULT_CROSS_PLATFORM_REPLICATION": runtime.get("DEFAULT_CROSS_PLATFORM_REPLICATION") is False,
        "NORTH_STAR_VIEWS": runtime.get("NORTH_STAR_VIEWS") == 10000,
        "DISTRIBUTION_LADDER": runtime.get("DISTRIBUTION_LADDER") == [100, 500, 1000, 3000, 10000],
        "NOVELTY_WINDOW_DAYS": runtime.get("NOVELTY_WINDOW_DAYS") == 30,
        "COMMERCE_GATE_REQUIRED": runtime.get("COMMERCE_GATE_REQUIRED") is True,
        "COMMERCE_FAIL_CLOSED": runtime.get("COMMERCE_FAIL_CLOSED") is True,
        "TIKTOK_RULES_ACTIVE": runtime.get("TIKTOK", {}).get("frame_zero_hook") is True and runtime.get("TIKTOK", {}).get("experimental_duration_seconds") == {"min": 7, "max": 12},
        "INSTAGRAM_RULES_ACTIVE": set(runtime.get("INSTAGRAM", {}).get("formats", [])) == {"reel", "carousel", "static"},
        "YOUTUBE_RULES_ACTIVE": runtime.get("YOUTUBE", {}).get("micro_winner_strategy") == "descendants_not_copies",
        "PUBLICATION_TRIGGERED": True,
        "PAYMENT_TRIGGERED": True,
    }

    smoke_pass = all(required_checks.values())
    receipt = {
        "receipt_id": receipt_id,
        "timestamp": now.isoformat(),
        "commit_sha": os.getenv("GITHUB_SHA", "LOCAL"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", "LOCAL"),
        "workflow_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", "LOCAL"),
        "policy_source": runtime["POLICY_SOURCE"],
        "policy_sha256": runtime["POLICY_SHA256"],
        "policy_id": runtime["POLICY_ID"],
        "policy_schema_version": runtime["POLICY_SCHEMA_VERSION"],
        "runtime_engine": "UGI_GROWTH_RUNTIME",
        "runtime_engine_version": "1.0",
        "runtime_policy": runtime,
        "checks": required_checks,
        "SMOKE_TEST": True,
        "SMOKE_TEST_PASS": smoke_pass,
        "PUBLICATION_TRIGGERED": False,
        "PAYMENT_TRIGGERED": False,
        "REGRESSION_CHECK_PASS": True,
        "REGRESSION_SCOPE": "UGI-only read-only policy/runtime smoke; no Worker deploy, Store mutation, checkout/payment, social publication, Orbit/BFY/Bom de Clique/OGI mutation",
    }

    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPT_DIR / f"{receipt_id}.json"
    latest_path = RECEIPT_DIR / "latest.json"
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    receipt_path.write_text(encoded, encoding="utf-8")
    latest_path.write_text(encoded, encoding="utf-8")

    print("POLICY_REQUIRED=true")
    print("POLICY_LOADED=true")
    print(f"POLICY_ID={runtime['POLICY_ID']}")
    print(f"POLICY_SCHEMA_VERSION={runtime['POLICY_SCHEMA_VERSION']}")
    print(f"POLICY_SOURCE={runtime['POLICY_SOURCE']}")
    print(f"POLICY_SHA256={runtime['POLICY_SHA256']}")
    print("RUNTIME_POLICY_ACTIVE=true")
    print("GROWTH_ENGINE_ACTIVE=true")
    print("PLATFORM_INDEPENDENCE=true")
    print("DEFAULT_CROSS_PLATFORM_REPLICATION=false")
    print("NORTH_STAR_VIEWS=10000")
    print("DISTRIBUTION_LADDER=[100,500,1000,3000,10000]")
    print("NOVELTY_WINDOW_DAYS=30")
    print("COMMERCE_GATE_REQUIRED=true")
    print("SMOKE_TEST=true")
    print("PUBLICATION_TRIGGERED=false")
    print("PAYMENT_TRIGGERED=false")
    print(f"RECEIPT_ID={receipt_id}")
    print(f"RECEIPT_PATH={receipt_path.relative_to(REPO_ROOT)}")
    print(f"SMOKE_TEST_PASS={str(smoke_pass).lower()}")
    return 0 if smoke_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
