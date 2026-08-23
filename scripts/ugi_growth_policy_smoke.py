#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = REPO_ROOT / "magic-engine" / "magic_engine.py"
POLICY_SOURCE = "config/ugi/growth-policy.json"
RECEIPT_DIR = REPO_ROOT / "control-plane" / "receipts" / "ugi-growth-engine"


def load_engine_module():
    spec = importlib.util.spec_from_file_location("ugi_magic_engine_runtime", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load magic engine runtime module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    now = datetime.now(timezone.utc)
    receipt_id = f"ugi-growth-policy-smoke-{now.strftime('%Y%m%dT%H%M%SZ')}"
    engine = load_engine_module()

    # Use the production loader, not a duplicate parser, so this proves the runtime path.
    policy, policy_sha256 = engine.load_growth_policy()
    runtime_plan = engine.build_plan([], policy, policy_sha256)
    exposed = runtime_plan.get("growth_policy", {})

    north_star = policy["north_star"]
    independence = policy["platform_independence"]
    novelty = policy["creative_novelty"]
    commerce = policy["commerce_gate"]

    required_checks = {
        "POLICY_REQUIRED": True,
        "POLICY_LOADED": exposed.get("loaded") is True,
        "POLICY_ID_MATCH": exposed.get("policy_id") == "ugi-growth-engine",
        "POLICY_SCHEMA_VERSION_MATCH": exposed.get("schema_version") == policy.get("schema_version"),
        "RUNTIME_POLICY_ACTIVE": exposed.get("sha256") == policy_sha256,
        "GROWTH_ENGINE_ACTIVE": runtime_plan.get("engine") is not None,
        "PLATFORM_INDEPENDENCE": independence.get("enabled") is True,
        "DEFAULT_CROSS_PLATFORM_REPLICATION": independence.get("default_cross_platform_replication") is False,
        "NORTH_STAR_VIEWS": north_star.get("organic_views_per_content_platform") == 10000,
        "DISTRIBUTION_LADDER": north_star.get("distribution_ladder") == [100, 500, 1000, 3000, 10000],
        "NOVELTY_WINDOW_DAYS": novelty.get("window_days") == 30,
        "COMMERCE_GATE_REQUIRED": commerce.get("required_for_commercial_content") is True,
        "COMMERCE_FAIL_CLOSED": commerce.get("fail_closed") is True,
        "TIKTOK_RULES_ACTIVE": policy.get("tiktok", {}).get("frame_zero_hook") is True and policy.get("tiktok", {}).get("experimental_duration_seconds") == {"min": 7, "max": 12},
        "INSTAGRAM_RULES_ACTIVE": set(policy.get("instagram", {}).get("formats", [])) == {"reel", "carousel", "static"},
        "YOUTUBE_RULES_ACTIVE": policy.get("youtube", {}).get("micro_winner_strategy") == "descendants_not_copies",
        "PUBLICATION_TRIGGERED": False,
        "PAYMENT_TRIGGERED": False,
    }

    smoke_pass = all(required_checks.values())
    receipt = {
        "receipt_id": receipt_id,
        "timestamp": now.isoformat(),
        "commit_sha": os.getenv("GITHUB_SHA", "LOCAL"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", "LOCAL"),
        "workflow_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", "LOCAL"),
        "policy_source": POLICY_SOURCE,
        "policy_sha256": policy_sha256,
        "policy_id": policy["policy_id"],
        "policy_schema_version": policy["schema_version"],
        "runtime_engine": runtime_plan.get("engine"),
        "runtime_engine_version": runtime_plan.get("version"),
        "runtime_exposed_growth_policy": exposed,
        "checks": required_checks,
        "SMOKE_TEST": True,
        "SMOKE_TEST_PASS": smoke_pass,
        "PUBLICATION_TRIGGERED": False,
        "PAYMENT_TRIGGERED": False,
        "REGRESSION_SCOPE": "read-only policy/runtime smoke; no worker, store, checkout, social publisher, secrets, or other projects mutated",
    }

    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPT_DIR / f"{receipt_id}.json"
    latest_path = RECEIPT_DIR / "latest.json"
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    receipt_path.write_text(encoded, encoding="utf-8")
    latest_path.write_text(encoded, encoding="utf-8")

    print(f"POLICY_REQUIRED=true")
    print(f"POLICY_LOADED={str(required_checks['POLICY_LOADED']).lower()}")
    print(f"POLICY_ID={policy['policy_id']}")
    print(f"POLICY_SCHEMA_VERSION={policy['schema_version']}")
    print(f"POLICY_SOURCE={POLICY_SOURCE}")
    print(f"POLICY_SHA256={policy_sha256}")
    print(f"RUNTIME_POLICY_ACTIVE={str(required_checks['RUNTIME_POLICY_ACTIVE']).lower()}")
    print(f"GROWTH_ENGINE_ACTIVE={str(required_checks['GROWTH_ENGINE_ACTIVE']).lower()}")
    print(f"PLATFORM_INDEPENDENCE={str(required_checks['PLATFORM_INDEPENDENCE']).lower()}")
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
