#!/usr/bin/env python3
"""Fail-closed validator for VSA final-master release receipts.

The scheduler is allowed to see only the exact final master whose SHA-256 is
bound to a validated release token.  A render, TTS or generator output is an
intermediate asset until this validator passes.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import sys
import tempfile
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "config/vsa/VSA_VISUAL_STORY_ENGINE_V1.json"


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_receipt(policy: dict[str, Any], receipt: dict[str, Any], master_path: pathlib.Path | None = None) -> list[str]:
    errors: list[str] = []
    fail = errors.append

    if receipt.get("schema") != policy["release"]["release_receipt_schema"]:
        fail("RECEIPT_SCHEMA_MISMATCH")
    if receipt.get("policy_id") != policy["schema"]:
        fail("POLICY_ID_MISMATCH")

    channel = receipt.get("channel", {})
    if channel.get("youtube_channel_id") != policy["channel"]["youtube_channel_id"]:
        fail("CHANNEL_ISOLATION_FAIL")
    if channel.get("name") != policy["channel"]["name"]:
        fail("CHANNEL_NAME_FAIL")

    scheduler = receipt.get("scheduler", {})
    if scheduler.get("publisher") != policy["channel"]["official_publisher"]:
        fail("OFFICIAL_PUBLISHER_FAIL")
    if int(scheduler.get("metricool_brand_id", -1)) != int(policy["channel"]["metricool_brand_id"]):
        fail("METRICOOL_BRAND_LOCK_FAIL")
    if scheduler.get("youtube_channel_id") != policy["channel"]["youtube_channel_id"]:
        fail("SCHEDULER_CHANNEL_LOCK_FAIL")

    build = receipt.get("build", {})
    if build.get("fresh_build") is not True:
        fail("MASTER_NOT_FRESH_BUILD")
    if build.get("prior_final_master_used") is not False:
        fail("PRIOR_FINAL_MASTER_REUSE_FORBIDDEN")
    if build.get("workdir_reused") is not False:
        fail("STALE_WORKDIR_REUSE_FORBIDDEN")

    master = receipt.get("master", {})
    declared_sha = str(master.get("sha256", "")).lower()
    token = receipt.get("release_token", {})
    token_sha = str(token.get("master_sha256", "")).lower()
    if len(declared_sha) != 64:
        fail("MASTER_SHA256_MISSING")
    if token.get("status") != "PASS":
        fail("SCHEDULER_RELEASE_TOKEN_FAIL")
    if token_sha != declared_sha:
        fail("RELEASE_TOKEN_MASTER_HASH_MISMATCH")
    if master_path is not None:
        if not master_path.is_file():
            fail("FINAL_MASTER_FILE_MISSING")
        else:
            actual_sha = sha256_file(master_path)
            if actual_sha != declared_sha:
                fail("FINAL_MASTER_HASH_MISMATCH")
            if actual_sha != token_sha:
                fail("FINAL_MASTER_TOKEN_HASH_MISMATCH")

    voice = receipt.get("voice", {})
    approved_profiles = set(policy["voice"]["approved_profiles"])
    if voice.get("language") != "pt-BR":
        fail("VOICE_LANGUAGE_FAIL")
    if voice.get("profile_id") not in approved_profiles:
        fail("VOICE_PROFILE_NOT_APPROVED")
    if voice.get("neutral_ptbr_gate") != "PASS":
        fail("VOICE_PTBR_NEUTRAL_FAIL")
    if voice.get("foreign_accent_detected") is not False:
        fail("FOREIGN_ACCENT_FAIL")

    mask = receipt.get("mask", {})
    if mask.get("version") != policy["mask"]["canonical_version"]:
        fail("CANONICAL_MASK_VERSION_FAIL")
    if mask.get("sha256") != policy["mask"]["sha256"]:
        fail("CANONICAL_MASK_HASH_FAIL")
    if mask.get("applied_to_final_master") is not True:
        fail("MASTER_CANONICAL_MASK_FAIL")
    if mask.get("safe_zone_gate") != "PASS":
        fail("MASK_SAFE_ZONE_FAIL")

    shots = receipt.get("shot_map")
    if not isinstance(shots, list) or len(shots) < int(policy["story_contract"]["minimum_shots"]):
        fail("SHOT_MAP_MISSING_OR_TOO_SHORT")
        shots = []

    allowed_roles = {"EVIDENCE", "CAUSE", "MECHANISM", "CONSEQUENCE", "PROOF", "CONTEXT"}
    real_count = 0
    shot_ids: set[str] = set()
    identifiable_human_seconds = 0.0
    target_human_seconds = 0.0
    content_class = receipt.get("content_class")
    expected_subject = str(receipt.get("expected_subject", "")).strip()

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
        if shot.get("visual_role") not in allowed_roles:
            fail(f"{prefix}_VISUAL_ROLE_INVALID")

        media_type = shot.get("media_type")
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
                if asset.get("expected_subject") != expected_subject:
                    fail(f"{prefix}_EXPECTED_SUBJECT_MISMATCH")
                is_human = asset.get("identifiable_human") is True
                duration = float(asset.get("duration_seconds", 0) or 0)
                if is_human:
                    identifiable_human_seconds += duration
                    if asset.get("asset_subject") == expected_subject:
                        target_human_seconds += duration
                    elif asset.get("asset_role") != "EXPLICIT_CONTEXT" or asset.get("explicit_script_reference") is not True:
                        fail(f"{prefix}_UNRELATED_PERSON_FOOTAGE_FAIL")
        elif media_type == "ANIMATION":
            if shot.get("visual_role") != "MECHANISM":
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

    if content_class == "PERSON_PROFILE":
        if not expected_subject:
            fail("PERSON_EXPECTED_SUBJECT_MISSING")
        if identifiable_human_seconds <= 0:
            fail("PERSON_IDENTIFIABLE_FOOTAGE_MISSING")
        else:
            share = target_human_seconds / identifiable_human_seconds
            if share < float(policy["entity_integrity"]["minimum_target_share_of_identifiable_human_footage"]):
                fail("PERSON_TARGET_SCREEN_SHARE_FAIL")

    tail = receipt.get("tail_integrity", {})
    if tail.get("pre_cta_contamination_gate") != "PASS":
        fail("PRE_CTA_CONTAMINATION_FAIL")
    if tail.get("unrelated_or_legacy_frame_detected") is not False:
        fail("LEGACY_OR_UNRELATED_FRAME_BEFORE_CTA")
    if tail.get("cta_first_frame_matches_canonical") is not True:
        fail("CTA_FIRST_FRAME_MISMATCH")

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
    elif any(not isinstance(x, dict) or x.get("visible") is not True or x.get("inside_safe_zone") is not True for x in samples):
        fail("CC_VISIBILITY_OR_SAFE_ZONE_PROOF_FAIL")
    if int(cc.get("maximum_lines_observed", 99)) > int(policy["captions"]["maximum_lines"]):
        fail("CC_MAX_LINES_FAIL")

    title = receipt.get("title", {})
    if int(title.get("layer_count", -1)) != int(policy["title"]["maximum_layers"]):
        fail("SINGLE_TITLE_LAYER_FAIL")
    if title.get("ghost_duplicate_detected") is not False:
        fail("GHOST_TITLE_FAIL")
    if title.get("inside_safe_zone") is not True:
        fail("TITLE_SAFE_ZONE_FAIL")

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
    if proof.get("tail_window_sampled") is not True:
        fail("TAIL_VISUAL_PROOF_MISSING")

    if policy["release"].get("human_review_required"):
        review = receipt.get("human_review", {})
        if review.get("approved") is not True:
            fail("HUMAN_REVIEW_REQUIRED")
    if receipt.get("release_eligible") is not True:
        fail("RELEASE_ELIGIBLE_FALSE")
    if receipt.get("schedule_mutated_before_gate") is not False:
        fail("SCHEDULE_MUTATED_BEFORE_GATE")

    return errors


def valid_self_test_receipt(policy: dict[str, Any], master_sha: str) -> dict[str, Any]:
    subject = "TEST_SUBJECT"
    def real(sid: str, role: str, link: str, action: str, duration: float = 4.0) -> dict[str, Any]:
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
                "rights_verified": True,
                "expected_subject": subject,
                "asset_subject": subject,
                "asset_role": "TARGET_SUBJECT",
                "identifiable_human": True,
                "duration_seconds": duration,
                "explicit_script_reference": True
            }
        }
    mechanism = {
        "id": "s2", "narration": "Mechanism narration", "media_type": "ANIMATION",
        "visual_role": "MECHANISM", "visual_description": "mechanism visibly unfolds",
        "visible_action": "mechanism visibly unfolds", "semantic_claim": "mechanism visibly unfolds",
        "semantic_match": "EXACT", "causal_link_id": "c1", "topic_only_match": False,
        "generic_filler": False, "reused_take_as_variety": False
    }
    return {
        "schema": policy["release"]["release_receipt_schema"], "policy_id": policy["schema"],
        "channel": {"name": policy["channel"]["name"], "youtube_channel_id": policy["channel"]["youtube_channel_id"]},
        "scheduler": {"publisher": "METRICOOL", "metricool_brand_id": policy["channel"]["metricool_brand_id"], "youtube_channel_id": policy["channel"]["youtube_channel_id"]},
        "build": {"fresh_build": True, "prior_final_master_used": False, "workdir_reused": False},
        "master": {"sha256": master_sha}, "release_token": {"status": "PASS", "master_sha256": master_sha},
        "voice": {"language": "pt-BR", "profile_id": policy["voice"]["approved_profiles"][0], "neutral_ptbr_gate": "PASS", "foreign_accent_detected": False},
        "mask": {"version": "V2", "sha256": policy["mask"]["sha256"], "applied_to_final_master": True, "safe_zone_gate": "PASS"},
        "content_class": "PERSON_PROFILE", "expected_subject": subject,
        "shot_map": [real("s1", "CAUSE", "c1", "real cause is visibly happening"), mechanism, real("s3", "CONSEQUENCE", "c1", "real consequence is visibly happening")],
        "tail_integrity": {"pre_cta_contamination_gate": "PASS", "unrelated_or_legacy_frame_detected": False, "cta_first_frame_matches_canonical": True},
        "gates": {g: True for g in policy["required_gates"]},
        "captions": {"burned_in_final_master": True, "maximum_lines_observed": 2, "visible_samples": [{"t": 5, "visible": True, "inside_safe_zone": True}, {"t": 15, "visible": True, "inside_safe_zone": True}, {"t": 25, "visible": True, "inside_safe_zone": True}]},
        "title": {"layer_count": 1, "ghost_duplicate_detected": False, "inside_safe_zone": True},
        "cta": {"lines": policy["cta"]["required_lines"]}, "format": dict(policy["format"]),
        "visual_proof": {"contact_sheet_generated": True, "all_story_blocks_sampled": True, "tail_window_sampled": True},
        "release_eligible": True, "schedule_mutated_before_gate": False
    }


def self_test(policy: dict[str, Any]) -> int:
    with tempfile.TemporaryDirectory() as td:
        master = pathlib.Path(td) / "final.mp4"
        master.write_bytes(b"VSA deterministic self-test final master")
        master_sha = sha256_file(master)
        base = valid_self_test_receipt(policy, master_sha)
        if validate_receipt(policy, base, master):
            print("SELF_TEST_VALID_RECEIPT_REJECTED", file=sys.stderr)
            return 1
        cases: list[tuple[str, dict[str, Any], pathlib.Path]] = []
        def add(name: str, mutator):
            x = copy.deepcopy(base); mutator(x); cases.append((name, x, master))
        add("foreign_accent", lambda r: r["voice"].update({"profile_id":"en-GB-RyanNeural", "neutral_ptbr_gate":"FAIL", "foreign_accent_detected":True}))
        add("missing_mask", lambda r: r["mask"].update({"applied_to_final_master":False}))
        add("wrong_mask_hash", lambda r: r["mask"].update({"sha256":"0"*64}))
        add("unrelated_person_elton_case", lambda r: r["shot_map"][2]["asset"].update({"asset_subject":"UNRELATED_CELEBRITY", "asset_role":"FILLER", "explicit_script_reference":False}))
        add("legacy_moon_before_cta", lambda r: r["tail_integrity"].update({"pre_cta_contamination_gate":"FAIL", "unrelated_or_legacy_frame_detected":True}))
        add("prior_master_reuse", lambda r: r["build"].update({"fresh_build":False, "prior_final_master_used":True}))
        add("wrong_metricool_brand", lambda r: r["scheduler"].update({"metricool_brand_id":6809869}))
        add("early_schedule", lambda r: r.__setitem__("schedule_mutated_before_gate", True))
        add("generic_filler", lambda r: r["shot_map"][0].__setitem__("generic_filler", True))
        add("caption_outside_zone", lambda r: r["captions"]["visible_samples"][0].__setitem__("inside_safe_zone", False))
        add("title_outside_zone", lambda r: r["title"].__setitem__("inside_safe_zone", False))
        add("release_gate_false", lambda r: r["gates"].__setitem__("FINAL_MASTER_QA_PASS", False))
        add("token_hash_mismatch", lambda r: r["release_token"].__setitem__("master_sha256", "f"*64))

        mutated = pathlib.Path(td) / "mutated.mp4"
        mutated.write_bytes(master.read_bytes() + b"changed-after-QA")
        cases.append(("master_changed_after_qa", copy.deepcopy(base), mutated))

        accepted = [name for name, receipt, path in cases if not validate_receipt(policy, receipt, path)]
        if accepted:
            print("SELF_TEST_INVALID_RECEIPTS_ACCEPTED=" + ",".join(accepted), file=sys.stderr)
            return 1
        print(f"VSA_PREVENTIVE_RELEASE_SELF_TEST_PASS invalid_cases_blocked={len(cases)}")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    ap.add_argument("--receipt")
    ap.add_argument("--master")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    policy = load_json(pathlib.Path(args.policy))
    if args.self_test:
        return self_test(policy)
    if not args.receipt or not args.master:
        print("RECEIPT_AND_MASTER_REQUIRED", file=sys.stderr)
        return 2
    receipt = load_json(pathlib.Path(args.receipt))
    master = pathlib.Path(args.master)
    errors = validate_receipt(policy, receipt, master)
    if errors:
        print("VSA_RELEASE_BLOCKED")
        for error in errors:
            print(error)
        return 1
    print("VSA_RELEASE_GATE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
