#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_RELATIVE_PATH = "config/ugi/growth-policy.json"
POLICY_PATH = REPO_ROOT / POLICY_RELATIVE_PATH
POLICY_REQUIRED = True
EXPECTED_POLICY_ID = "ugi-growth-engine"

REQUIRED_KEYS = [
    "schema_version",
    "policy_id",
    "effective_date",
    "north_star",
    "optimization_priority",
    "pre_generation_inputs",
    "platform_independence",
    "tiktok",
    "instagram",
    "youtube",
    "creative_novelty",
    "commerce_gate",
    "publication_evidence",
    "experiment_loop",
    "lifecycle_events",
]


class GrowthPolicyError(RuntimeError):
    pass


def load_growth_policy() -> tuple[dict, str]:
    """Fail-closed loader for UGI only. No fallback/default policy is allowed."""
    if not POLICY_PATH.is_file():
        raise GrowthPolicyError(f"POLICY_REQUIRED=true POLICY_LOADED=false policy_missing={POLICY_RELATIVE_PATH}")
    raw = POLICY_PATH.read_bytes()
    try:
        policy = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise GrowthPolicyError(f"POLICY_REQUIRED=true POLICY_LOADED=false invalid_json={exc}") from exc
    missing = [key for key in REQUIRED_KEYS if key not in policy]
    if missing:
        raise GrowthPolicyError(f"POLICY_REQUIRED=true POLICY_LOADED=false missing={','.join(missing)}")
    if policy.get("policy_id") != EXPECTED_POLICY_ID:
        raise GrowthPolicyError(
            f"POLICY_REQUIRED=true POLICY_LOADED=false unexpected_policy_id={policy.get('policy_id')}"
        )
    return policy, hashlib.sha256(raw).hexdigest()


def load_distribution_state(policy: dict) -> tuple[dict, str, str]:
    """Load the operational distribution state referenced by policy, fail-closed."""
    ref = policy.get("distribution", {}).get("state_ref")
    if not isinstance(ref, str) or not ref:
        raise GrowthPolicyError("DISTRIBUTION_STATE_REQUIRED")
    path = (REPO_ROOT / ref).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise GrowthPolicyError("DISTRIBUTION_STATE_OUTSIDE_REPOSITORY") from exc
    if not path.is_file():
        raise GrowthPolicyError(f"DISTRIBUTION_STATE_MISSING:{ref}")
    raw = path.read_bytes()
    try:
        state = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise GrowthPolicyError(f"DISTRIBUTION_STATE_INVALID_JSON:{exc}") from exc
    if not isinstance(state, dict) or state.get("project") != "UGI":
        raise GrowthPolicyError("DISTRIBUTION_STATE_INVALID_PROJECT")
    buffer = state.get("buffer", {})
    active = buffer.get("active_platforms")
    paused = buffer.get("paused_platforms")
    if buffer.get("publisher") != "buffer":
        raise GrowthPolicyError("DISTRIBUTION_STATE_BUFFER_PROVIDER_LOCK")
    if not isinstance(active, list) or not isinstance(paused, list):
        raise GrowthPolicyError("DISTRIBUTION_STATE_PLATFORM_LISTS_REQUIRED")
    active_set = {str(item).lower() for item in active}
    paused_set = {str(item).lower() for item in paused}
    allowed = {"linkedin", "instagram", "tiktok", "youtube"}
    if not active_set or not active_set <= allowed or not paused_set <= allowed:
        raise GrowthPolicyError("DISTRIBUTION_STATE_INVALID_PLATFORMS")
    if active_set & paused_set:
        raise GrowthPolicyError("DISTRIBUTION_STATE_ACTIVE_PAUSED_CONFLICT")
    if int(buffer.get("active_channel_count", -1)) != len(active_set):
        raise GrowthPolicyError("DISTRIBUTION_STATE_ACTIVE_COUNT_MISMATCH")
    if "youtube" not in paused_set or buffer.get("youtube_buffer_status") != "PAUSED":
        raise GrowthPolicyError("DISTRIBUTION_STATE_YOUTUBE_PAUSE_LOCK")
    return state, hashlib.sha256(raw).hexdigest(), ref


def expose_runtime_policy(
    policy: dict,
    sha256: str,
    distribution_state: dict,
    distribution_state_sha256: str,
    distribution_state_source: str,
) -> dict:
    """Compact policy surface consumed by UGI generation/runtime gates."""
    return {
        "POLICY_REQUIRED": True,
        "POLICY_LOADED": True,
        "POLICY_ID": policy["policy_id"],
        "POLICY_SCHEMA_VERSION": policy["schema_version"],
        "POLICY_SOURCE": POLICY_RELATIVE_PATH,
        "POLICY_SHA256": sha256,
        "RUNTIME_POLICY_ACTIVE": True,
        "GROWTH_ENGINE_ACTIVE": True,
        "DISTRIBUTION_STATE_SOURCE": distribution_state_source,
        "DISTRIBUTION_STATE_SHA256": distribution_state_sha256,
        "DISTRIBUTION_STATE": distribution_state,
        "EFFECTIVE_ACTIVE_PLATFORMS": distribution_state["buffer"]["active_platforms"],
        "EFFECTIVE_PAUSED_PLATFORMS": distribution_state["buffer"]["paused_platforms"],
        "NORTH_STAR_VIEWS": policy["north_star"]["organic_views_per_content_platform"],
        "DISTRIBUTION_LADDER": policy["north_star"]["distribution_ladder"],
        "OPTIMIZATION_PRIORITY": policy["optimization_priority"],
        "PRE_GENERATION_INPUTS": policy["pre_generation_inputs"],
        "PLATFORM_INDEPENDENCE": policy["platform_independence"]["enabled"],
        "DEFAULT_CROSS_PLATFORM_REPLICATION": policy["platform_independence"]["default_cross_platform_replication"],
        "TIKTOK": policy["tiktok"],
        "INSTAGRAM": policy["instagram"],
        "YOUTUBE": policy["youtube"],
        "NOVELTY_WINDOW_DAYS": policy["creative_novelty"]["window_days"],
        "CREATIVE_NOVELTY": policy["creative_novelty"],
        "COMMERCE_GATE_REQUIRED": policy["commerce_gate"]["required_for_commercial_content"],
        "COMMERCE_FAIL_CLOSED": policy["commerce_gate"]["fail_closed"],
        "PUBLICATION_EVIDENCE": policy["publication_evidence"],
        "EXPERIMENT_LOOP": policy["experiment_loop"],
        "LIFECYCLE_EVENTS": policy["lifecycle_events"],
    }


def validate_runtime_contract(runtime: dict) -> None:
    failures = []
    checks = {
        "POLICY_REQUIRED": runtime.get("POLICY_REQUIRED") is True,
        "POLICY_LOADED": runtime.get("POLICY_LOADED") is True,
        "POLICY_ID": runtime.get("POLICY_ID") == EXPECTED_POLICY_ID,
        "RUNTIME_POLICY_ACTIVE": runtime.get("RUNTIME_POLICY_ACTIVE") is True,
        "GROWTH_ENGINE_ACTIVE": runtime.get("GROWTH_ENGINE_ACTIVE") is True,
        "PLATFORM_INDEPENDENCE": runtime.get("PLATFORM_INDEPENDENCE") is True,
        "DEFAULT_CROSS_PLATFORM_REPLICATION": runtime.get("DEFAULT_CROSS_PLATFORM_REPLICATION") is False,
        "NORTH_STAR_VIEWS": runtime.get("NORTH_STAR_VIEWS") == 10000,
        "DISTRIBUTION_LADDER": runtime.get("DISTRIBUTION_LADDER") == [100, 500, 1000, 3000, 10000],
        "NOVELTY_WINDOW_DAYS": runtime.get("NOVELTY_WINDOW_DAYS") == 30,
        "COMMERCE_GATE_REQUIRED": runtime.get("COMMERCE_GATE_REQUIRED") is True,
        "COMMERCE_FAIL_CLOSED": runtime.get("COMMERCE_FAIL_CLOSED") is True,
        "TIKTOK_RULES": runtime.get("TIKTOK", {}).get("frame_zero_hook") is True,
        "INSTAGRAM_RULES": {"reel", "carousel", "static"}.issubset(set(runtime.get("INSTAGRAM", {}).get("formats", []))),
        "YOUTUBE_RULES": runtime.get("YOUTUBE", {}).get("micro_winner_strategy") == "descendants_not_copies",
        "DISTRIBUTION_STATE_ACTIVE": isinstance(runtime.get("DISTRIBUTION_STATE_SHA256"), str)
            and len(runtime.get("DISTRIBUTION_STATE_SHA256", "")) == 64,
        "BUFFER_PROVIDER_LOCK": runtime.get("DISTRIBUTION_STATE", {}).get("buffer", {}).get("publisher") == "buffer",
        "YOUTUBE_PAUSED": "youtube" in set(runtime.get("EFFECTIVE_PAUSED_PLATFORMS", [])),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise GrowthPolicyError("UGI_GROWTH_RUNTIME_FAIL " + ",".join(failures))


def load_runtime_policy() -> dict:
    policy, sha256 = load_growth_policy()
    state, state_sha256, state_source = load_distribution_state(policy)
    runtime = expose_runtime_policy(policy, sha256, state, state_sha256, state_source)
    validate_runtime_contract(runtime)
    return runtime


def main() -> int:
    runtime = load_runtime_policy()
    print(json.dumps(runtime, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
