#!/usr/bin/env python3
"""Fail-closed VSA canonical runtime guard.

This module does not replace the renderer. It is the mandatory policy gate that
resolves VSA canon, validates channel/account isolation, enforces the 60-day
semantic topic ledger, validates the thematic instrumental-music contract and
emits a canonical render/publish plan before downstream production or scheduling.
"""
from __future__ import annotations
import argparse, json, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT = ROOT / "canonical" / "vsa" / "CURRENT.json"
CONTRACT = ROOT / "canonical" / "vsa" / "v1" / "VSA_CANONICAL_PRODUCTION_CONTRACT_V1.json"
GUARDRAILS = ROOT / "canonical" / "vsa" / "v1" / "VSA_EDITORIAL_GUARDRAILS_V2.json"
TOPIC_LEDGER = ROOT / "canonical" / "vsa" / "v1" / "VSA_TOPIC_LEDGER_60D.json"
CENA_PREFIXES = ("canonical/cena-certa/", "ops/cena-certa-runtime/")
VSA_ALIASES = {"vsa", "voce sabia agora", "você sabia agora", "você sabia agora?", "voce sabia agora?"}

class GateError(RuntimeError):
    pass

def load_json(path: Path):
    if not path.exists():
        raise GateError(f"MISSING_CANONICAL_FILE:{path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))

def normalize_channel(value: str) -> str:
    return " ".join(value.strip().lower().split())

def assert_channel(channel: str):
    n = normalize_channel(channel)
    if n not in VSA_ALIASES:
        raise GateError(f"CHANNEL_LOCK_FAIL:{channel}")

def assert_path_isolation(paths):
    for raw in paths or []:
        p = str(raw).replace("\\", "/").lstrip("./")
        if any(p.startswith(prefix) for prefix in CENA_PREFIXES):
            raise GateError(f"CROSS_PROJECT_PATH_BLOCK:{p}")

def assert_account(account_id: int | None, contract):
    if account_id is None:
        return
    lock = contract["project_lock"]
    if account_id in set(lock["forbidden_account_ids"]):
        raise GateError(f"CENA_CERTA_ACCOUNT_BLOCK:{account_id}")
    approved_entry = lock.get("approved_post_bridge_account") or lock.get("historical_post_bridge_account")
    if not approved_entry or "id" not in approved_entry:
        raise GateError("VSA_ACCOUNT_MAPPING_MISSING")
    approved = approved_entry["id"]
    if int(account_id) != int(approved):
        raise GateError(f"UNVERIFIED_VSA_ACCOUNT:{account_id}")

def asset_fingerprint(contract):
    return {
        "mask": {"library_path": contract["mask"]["library_path"], "sha256": contract["mask"]["sha256"]},
        "cta": {"library_path": contract["cta"]["library_path"], "sha256": contract["cta"]["sha256"]},
    }

def canonical_plan(contract, guardrails):
    return {
        "status": "VSA_CANON_RESOLVED",
        "project": contract["project_lock"]["project"],
        "channel": contract["project_lock"]["channel_name"],
        "format": contract["format"],
        "music_policy": contract["music_policy"],
        "visual_sequence": contract["visual_grammar"]["preferred_sequence"],
        "mask_apply_stage": contract["mask"]["apply_stage"],
        "fixed_assets": asset_fingerprint(contract),
        "qa_workflow": contract["qa"]["workflow"],
        "topic_repeat_lock_days": guardrails["topic_repeat_lock"]["window_days"],
        "topic_ledger": str(TOPIC_LEDGER.relative_to(ROOT)),
        "people_biocuriosity": guardrails["people_biocuriosity"],
        "publishing_target": contract["publishing"]["current_verified_route"],
        "recovery_trigger": contract["recovery_trigger"],
    }

def _parse_local_date(raw: str, field: str) -> date:
    try:
        return date.fromisoformat(raw)
    except Exception as exc:
        raise GateError(f"INVALID_{field.upper()}:{raw}") from exc

def topic_collisions(job, guardrails):
    semantic_topic_id = str(job.get("semantic_topic_id") or "").strip()
    content_id = str(job.get("content_id") or "").strip()
    publish_date_raw = str(job.get("publish_date_local") or "").strip()
    if not semantic_topic_id:
        raise GateError("SEMANTIC_TOPIC_ID_MISSING")
    if not content_id:
        raise GateError("CONTENT_ID_MISSING")
    if not publish_date_raw:
        raise GateError("PUBLISH_DATE_LOCAL_MISSING")

    publish_date = _parse_local_date(publish_date_raw, "publish_date_local")
    ledger = load_json(TOPIC_LEDGER)
    window_days = int(guardrails["topic_repeat_lock"]["window_days"])
    collisions = []
    for entry in ledger.get("entries", []):
        if str(entry.get("semantic_topic_id") or "") != semantic_topic_id:
            continue
        if str(entry.get("content_id") or "") == content_id:
            continue
        entry_date_raw = str(entry.get("date_local") or "")
        if not entry_date_raw:
            continue
        entry_date = _parse_local_date(entry_date_raw, "ledger_date_local")
        age_days = (publish_date - entry_date).days
        if 0 <= age_days <= window_days:
            collisions.append({
                "content_id": entry.get("content_id"),
                "title": entry.get("title"),
                "date_local": entry_date_raw,
                "status": entry.get("status"),
                "age_days": age_days,
            })
    return collisions

def assert_topic_history(job, guardrails):
    collisions = topic_collisions(job, guardrails)
    if not collisions:
        return {"classification": "NEW_TOPIC", "collisions": []}

    if job.get("repeat_exception") is not True:
        ids = ",".join(str(x.get("content_id")) for x in collisions)
        raise GateError(f"BLOCK_TOPIC_REPEAT:{ids}")

    required_exception = ["repeat_exception_reason", "new_event_source", "new_event_date"]
    missing = [k for k in required_exception if not str(job.get(k) or "").strip()]
    if missing:
        raise GateError("REPEAT_EXCEPTION_FIELDS_MISSING:" + ",".join(missing))
    _parse_local_date(str(job["new_event_date"]), "new_event_date")
    return {"classification": "BREAKING_EXCEPTION", "collisions": collisions}

def assert_music_policy(job, contract):
    policy = contract.get("music_policy") or {}
    if policy.get("status") != "HARD_GATE" or policy.get("required") is not True:
        raise GateError("CANONICAL_MUSIC_POLICY_MISSING_OR_DISABLED")

    metadata_fields = ["music_track_title", "music_artist_or_composer", "music_source", "music_license_or_usage_basis", "music_editorial_class"]
    missing_metadata = [k for k in metadata_fields if not str(job.get(k) or "").strip()]
    if missing_metadata:
        raise GateError("MUSIC_METADATA_MISSING:" + ",".join(missing_metadata))

    required_gates = [
        "music_composition_gate",
        "music_theme_match_gate",
        "music_audibility_gate",
        "music_no_tone_or_game_style_gate",
        "music_rights_gate",
    ]
    failed = [k for k in required_gates if job.get(k) != "PASS"]
    if failed:
        raise GateError("MUSIC_GATE_NOT_PASS:" + ",".join(failed))

    forbidden_form = str(job.get("music_form") or "").strip().lower()
    forbidden = {str(x).strip().lower() for x in policy.get("forbidden_music_forms", [])}
    if forbidden_form and forbidden_form in forbidden:
        raise GateError(f"FORBIDDEN_MUSIC_FORM:{forbidden_form}")

    if job.get("music_has_vocals") is True:
        raise GateError("MUSIC_VOCALS_FORBIDDEN")

    return {
        "track_title": job["music_track_title"],
        "artist_or_composer": job["music_artist_or_composer"],
        "editorial_class": job["music_editorial_class"],
    }

def preflight(args):
    current = load_json(CURRENT)
    contract = load_json(CONTRACT)
    guardrails = load_json(GUARDRAILS)
    assert_channel(args.channel)
    assert_path_isolation(args.write_path)
    assert_account(args.account_id, contract)
    if current.get("contract") != "canonical/vsa/v1/VSA_CANONICAL_PRODUCTION_CONTRACT_V1.json":
        raise GateError("CURRENT_POINTER_MISMATCH")
    print(json.dumps(canonical_plan(contract, guardrails), ensure_ascii=False, indent=2))

def check_topic(args):
    guardrails = load_json(GUARDRAILS)
    job = {
        "semantic_topic_id": args.semantic_topic_id,
        "content_id": args.content_id,
        "publish_date_local": args.publish_date_local,
        "repeat_exception": args.repeat_exception,
        "repeat_exception_reason": args.repeat_exception_reason,
        "new_event_source": args.new_event_source,
        "new_event_date": args.new_event_date,
    }
    result = assert_topic_history(job, guardrails)
    print(json.dumps({"status": "PASS", **result}, ensure_ascii=False, indent=2))

def validate_job(args):
    contract = load_json(CONTRACT)
    guardrails = load_json(GUARDRAILS)
    job = json.loads(Path(args.job).read_text(encoding="utf-8"))
    assert_channel(job.get("channel", ""))
    assert_path_isolation(job.get("write_paths", []))
    assert_account(job.get("social_account_id"), contract)
    required = [
        "content_id", "title", "script", "semantic_map", "semantic_topic_id",
        "publish_date_local", "rights_manifest", "base_video_qa", "final_qa",
        "topic_history_gate", "music_track_title", "music_artist_or_composer",
        "music_source", "music_license_or_usage_basis", "music_editorial_class",
        "music_composition_gate", "music_theme_match_gate", "music_audibility_gate",
        "music_no_tone_or_game_style_gate", "music_rights_gate"
    ]
    missing = [k for k in required if not job.get(k)]
    if missing:
        raise GateError("JOB_REQUIRED_FIELDS_MISSING:" + ",".join(missing))
    topic_result = assert_topic_history(job, guardrails)
    music_result = assert_music_policy(job, contract)
    if job.get("topic_history_gate") != guardrails["job_requirements"]["topic_history_gate"]:
        raise GateError("TOPIC_HISTORY_GATE_NOT_PASS")
    if job.get("content_class") == "PERSON_PROFILE" and job.get("person_visual_reference_gate") != "PASS":
        raise GateError("PERSON_VISUAL_REFERENCE_GATE_NOT_PASS")
    if job.get("base_video_qa") != "PASS" or job.get("final_qa") != "PASS":
        raise GateError("QA_NOT_PASS")
    if job.get("rights_manifest") != "PASS":
        raise GateError("RIGHTS_GATE_NOT_PASS")
    print(json.dumps({
        "status": "VSA_JOB_RELEASE_ELIGIBLE",
        "title": job["title"],
        "topic_classification": topic_result["classification"],
        "music": music_result,
    }, ensure_ascii=False))

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("preflight")
    p.add_argument("--channel", required=True)
    p.add_argument("--account-id", type=int)
    p.add_argument("--write-path", action="append", default=[])
    p.set_defaults(func=preflight)

    t = sub.add_parser("check-topic")
    t.add_argument("--semantic-topic-id", required=True)
    t.add_argument("--content-id", required=True)
    t.add_argument("--publish-date-local", required=True)
    t.add_argument("--repeat-exception", action="store_true")
    t.add_argument("--repeat-exception-reason")
    t.add_argument("--new-event-source")
    t.add_argument("--new-event-date")
    t.set_defaults(func=check_topic)

    v = sub.add_parser("validate-job")
    v.add_argument("--job", required=True)
    v.set_defaults(func=validate_job)

    args = ap.parse_args()
    try:
        args.func(args)
    except GateError as e:
        print(json.dumps({"status":"BLOCKED","reason":str(e)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)

if __name__ == "__main__":
    main()
