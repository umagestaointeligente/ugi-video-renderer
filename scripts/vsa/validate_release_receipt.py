#!/usr/bin/env python3
"""Fail-closed validator for VSA visual-story release receipts."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "config/vsa/VSA_VISUAL_STORY_ENGINE_V1.json"


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_receipt(policy: dict[str, Any], receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fail = errors.append

    if receipt.get("schema") != policy["release"]["release_receipt_schema"]:
        fail("RECEIPT_SCHEMA_MISMATCH")
    if receipt.get("policy_id") != policy["schema"]:
        fail("POLICY_ID_MISMATCH")
    if receipt.get("channel", {}).get("youtube_channel_id") != policy["channel"]["youtube_channel_id"]:
        fail("CHANNEL_ISOLATION_FAIL")
    if receipt.get("channel", {}).get("name") != policy["channel"]["name"]:
        fail("CHANNEL_NAME_FAIL")

    shots = receipt.get("shot_map")
    if not isinstance(shots, list) or len(shots) < int(policy["story_contract"]["minimum_shots"]):
        fail("SHOT_MAP_MISSING_OR_TOO_SHORT")
        shots = []

    allowed_roles = {"EVIDENCE", "CAUSE", "MECHANISM", "CONSEQUENCE", "PROOF", "CONTEXT"}
    real_count = 0
    shot_ids: set[str] = set()
    for i, shot in enumerate(shots):
        prefix = f"SHOT_{i+1}"
        if not isinstance(shot, dict):
            fail(f"{prefix}_INVALID")
            continue
        sid = str(shot.get("id", "")).strip()
        if not sid or sid in shot_ids:
            fail(f"{prefix}_ID_INVALID_OR_DUPLICATE")
        shot_ids.add(sid)
        for field in ("narration", "visual_description", "visible_action", "semantic_claim"):
            if not str(shot.get(field, "")).strip():
                fail(f"{prefix}_{field.upper()}_MISSING")
        if shot.get("semantic_match") != "EXACT":
            fail(f"{prefix}_SEMANTIC_MATCH_NOT_EXACT")
        if shot.get("topic_only_match") is not False:
            fail(f"{prefix}_TOPIC_ONLY_MATCH_FORBIDDEN")
        if shot.get("generic_filler") is not False:
            fail(f"{prefix}_GENERIC_FILLER_FORBIDDEN")
        if shot.get("reused_take_as_variety") is not False:
            fail(f"{prefix}_REUSED_TAKE_FORBIDDEN")

        media_type = shot.get("media_type")
        role = shot.get("visual_role")
        if role not in allowed_roles:
            fail(f"{prefix}_VISUAL_ROLE_INVALID")

        if media_type == "REAL":
            real_count += 1
            asset = shot.get("asset")
            if not isinstance(asset, dict):
                fail(f"{prefix}_REAL_ASSET_METADATA_MISSING")
            else:
                for field in policy["real_asset_required_fields"]:
                    value = asset.get(field)
                    if value is None or (isinstance(value, str) and not value.strip()):
                        fail(f"{prefix}_REAL_ASSET_{field.upper()}_MISSING")
                if asset.get("rights_verified") is not True:
                    fail(f"{prefix}_RIGHTS_NOT_VERIFIED")
        elif media_type == "ANIMATION":
            if role != "MECHANISM":
                fail(f"{prefix}_ANIMATION_MUST_EXPLAIN_MECHANISM")
            link = str(shot.get("causal_link_id", "")).strip()
            if not link:
                fail(f"{prefix}_CAUSAL_LINK_MISSING")
            if i == 0 or shots[i - 1].get("media_type") != "REAL":
                fail(f"{prefix}_MECHANISM_NEEDS_REAL_LEAD_IN")
            elif shots[i - 1].get("causal_link_id") != link:
                fail(f"{prefix}_LEAD_IN_CAUSAL_LINK_MISMATCH")
            if i + 1 >= len(shots) or shots[i + 1].get("media_type") != "REAL":
                fail(f"{prefix}_MECHANISM_NEEDS_REAL_CONSEQUENCE")
            else:
                nxt = shots[i + 1]
                if nxt.get("visual_role") not in {"CONSEQUENCE", "PROOF"}:
                    fail(f"{prefix}_NEXT_REAL_MUST_BE_CONSEQUENCE_OR_PROOF")
                if nxt.get("causal_link_id") != link:
                    fail(f"{prefix}_CONSEQUENCE_CAUSAL_LINK_MISMATCH")
        else:
            fail(f"{prefix}_MEDIA_TYPE_INVALID")

    if real_count == 0:
        fail("AT_LEAST_ONE_REAL_SCENE_REQUIRED")

    gates = receipt.get("gates", {})
    for gate in policy["required_gates"]:
        if gates.get(gate) is not True:
            fail(f"GATE_FAIL:{gate}")

    cc = receipt.get("captions", {})
    samples = cc.get("visible_samples", [])
    if cc.get("burned_in_final_master") is not True:
        fail("CC_NOT_BURNED_IN_FINAL_MASTER")
    if not isinstance(samples, list) or len(samples) < int(policy["captions"]["minimum_visual_samples"]):
        fail("CC_VISIBLE_SAMPLE_COUNT_FAIL")
    elif any(not isinstance(x, dict) or x.get("visible") is not True for x in samples):
        fail("CC_VISIBILITY_PROOF_FAIL")
    if int(cc.get("maximum_lines_observed", 99)) > int(policy["captions"]["maximum_lines"]):
        fail("CC_MAX_LINES_FAIL")

    title = receipt.get("title", {})
    if int(title.get("layer_count", -1)) != int(policy["title"]["maximum_layers"]):
        fail("SINGLE_TITLE_LAYER_FAIL")
    if title.get("ghost_duplicate_detected") is not False:
        fail("GHOST_TITLE_FAIL")

    if receipt.get("cta", {}).get("lines") != policy["cta"]["required_lines"]:
        fail("CTA_CANONICAL_TEXT_FAIL")

    fmt = receipt.get("format", {})
    for key in ("width", "height", "fps", "video_codec", "pixel_format"):
        if fmt.get(key) != policy["format"][key]:
            fail(f"FORMAT_{key.upper()}_FAIL")

    proof = receipt.get("visual_proof", {})
    if proof.get("contact_sheet_generated") is not True:
        fail("VISUAL_CONTACT_SHEET_MISSING")
    if proof.get("all_story_blocks_sampled") is not True:
        fail("VISUAL_PROOF_INCOMPLETE")

    review = receipt.get("human_review", {})
    if policy["release"]["human_review_required"] and review.get("approved") is not True:
        fail("HUMAN_REVIEW_REQUIRED")
    if receipt.get("release_eligible") is not True:
        fail("RELEASE_ELIGIBLE_FALSE")
    if receipt.get("schedule_mutated_before_gate") is not False:
        fail("SCHEDULE_MUTATED_BEFORE_GATE")

    return errors


def valid_self_test_receipt(policy: dict[str, Any]) -> dict[str, Any]:
    def real(sid: str, role: str, link: str, action: str) -> dict[str, Any]:
        return {
            "id": sid,
            "narration": f"Narration {sid}",
            "media_type": "REAL",
            "visual_role": role,
            "visual_description": action,
            "visible_action": action,
            "semantic_claim": action,
            "semantic_match": "EXACT",
            "causal_link_id": link,
            "topic_only_match": False,
            "generic_filler": False,
            "reused_take_as_variety": False,
            "asset": {
                "event": "test event",
                "semantic_role": role,
                "visible_action": action,
                "source_url": "https://example.invalid/source",
                "license": "TEST_RIGHTS",
                "source_timestamp_seconds": 1.0,
                "rights_verified": True
            }
        }
    mechanism = {
        "id": "s2",
        "narration": "Mechanism narration",
        "media_type": "ANIMATION",
        "visual_role": "MECHANISM",
        "visual_description": "mechanism visibly unfolds",
        "visible_action": "mechanism visibly unfolds",
        "semantic_claim": "mechanism visibly unfolds",
        "semantic_match": "EXACT",
        "causal_link_id": "c1",
        "topic_only_match": False,
        "generic_filler": False,
        "reused_take_as_variety": False
    }
    return {
        "schema": policy["release"]["release_receipt_schema"],
        "policy_id": policy["schema"],
        "channel": {"name": policy["channel"]["name"], "youtube_channel_id": policy["channel"]["youtube_channel_id"]},
        "shot_map": [real("s1", "CAUSE", "c1", "real cause is visibly happening"), mechanism, real("s3", "CONSEQUENCE", "c1", "real consequence is visibly happening")],
        "gates": {g: True for g in policy["required_gates"]},
        "captions": {"burned_in_final_master": True, "maximum_lines_observed": 2, "visible_samples": [{"t": 5, "visible": True}, {"t": 15, "visible": True}, {"t": 25, "visible": True}]},
        "title": {"layer_count": 1, "ghost_duplicate_detected": False},
        "cta": {"lines": policy["cta"]["required_lines"]},
        "format": dict(policy["format"]),
        "visual_proof": {"contact_sheet_generated": True, "all_story_blocks_sampled": True},
        "human_review": {"approved": True, "reviewer": "self-test"},
        "release_eligible": True,
        "schedule_mutated_before_gate": False
    }


def self_test(policy: dict[str, Any]) -> int:
    import copy
    base = valid_self_test_receipt(policy)
    if validate_receipt(policy, base):
        print("SELF_TEST_VALID_RECEIPT_REJECTED", file=sys.stderr)
        return 1
    cases = []
    for name, mutate in [
        ("generic_filler", lambda r: r["shot_map"][2].__setitem__("generic_filler", True)),
        ("topic_only", lambda r: r["shot_map"][2].__setitem__("topic_only_match", True)),
        ("missing_cc", lambda r: r["captions"].__setitem__("visible_samples", [])),
        ("duplicate_title", lambda r: r["title"].__setitem__("layer_count", 2)),
        ("wrong_cta", lambda r: r["cta"].__setitem__("lines", ["wrong"])),
        ("no_rights", lambda r: r["shot_map"][0]["asset"].__setitem__("rights_verified", False)),
        ("no_human_review", lambda r: r["human_review"].__setitem__("approved", False)),
        ("gate_false", lambda r: r["gates"].__setitem__("REAL_ACTION_VISIBLE_PASS", False)),
        ("schedule_early", lambda r: r.__setitem__("schedule_mutated_before_gate", True)),
    ]:
        x = copy.deepcopy(base)
        mutate(x)
        cases.append((name, x))
    failed = [name for name, x in cases if not validate_receipt(policy, x)]
    if failed:
        print("SELF_TEST_INVALID_RECEIPTS_ACCEPTED=" + ",".join(failed), file=sys.stderr)
        return 1
    print(f"VSA_VISUAL_STORY_ENGINE_SELF_TEST_PASS invalid_cases_blocked={len(cases)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    ap.add_argument("--receipt")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    policy = load_json(pathlib.Path(args.policy))
    if args.self_test:
        return self_test(policy)
    if not args.receipt:
        print("RECEIPT_REQUIRED", file=sys.stderr)
        return 2
    receipt = load_json(pathlib.Path(args.receipt))
    errors = validate_receipt(policy, receipt)
    if errors:
        print("VSA_RELEASE_BLOCKED")
        for error in errors:
            print(error)
        return 1
    print("VSA_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
