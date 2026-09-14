#!/usr/bin/env python3
"""Fail-closed VSA canonical runtime guard.

Pre-production gate only. Final-master release is additionally enforced by
scripts/vsa/validate_release_receipt.py, which binds the exact MP4 SHA-256 to a
V2 release token before Metricool may receive it.
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
MASK_GUARD = ROOT / "canonical" / "vsa" / "v1" / "VSA_CLEAN_HEADER_GUARD_V1.json"
CENA_PREFIXES = ("canonical/cena-certa/", "ops/cena-certa-runtime/")
VSA_ALIASES = {"vsa", "voce sabia agora", "você sabia agora", "você sabia agora?", "voce sabia agora?"}

class GateError(RuntimeError):
    pass

def load_json(path: Path):
    if not path.exists():
        raise GateError(f"MISSING_CANONICAL_FILE:{path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))

def assert_channel(channel: str):
    n = " ".join(str(channel).strip().lower().split())
    if n not in VSA_ALIASES:
        raise GateError(f"CHANNEL_LOCK_FAIL:{channel}")

def assert_path_isolation(paths):
    for raw in paths or []:
        p = str(raw).replace("\\", "/").lstrip("./")
        if any(p.startswith(prefix) for prefix in CENA_PREFIXES):
            raise GateError(f"CROSS_PROJECT_PATH_BLOCK:{p}")

def assert_account(account_id: int | None, contract):
    """account_id is the Metricool brand id under the current canon."""
    if account_id is None:
        return
    lock = contract["project_lock"]
    forbidden = {int(x) for x in lock.get("forbidden_metricool_brand_ids", [])}
    if int(account_id) in forbidden:
        raise GateError(f"CROSS_PROJECT_METRICOOL_BRAND_BLOCK:{account_id}")
    approved = int(lock["approved_metricool_brand"]["id"])
    if int(account_id) != approved:
        raise GateError(f"UNVERIFIED_VSA_METRICOOL_BRAND:{account_id}")

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
        "voice_policy": contract["voice_policy"],
        "music_policy": contract["music_policy"],
        "visual_sequence": contract["visual_grammar"]["preferred_sequence"],
        "real_footage_alternation": guardrails["real_footage_alternation"],
        "fixed_assets": asset_fingerprint(contract),
        "qa_workflow": contract["qa"]["workflow"],
        "retry_policy": contract["retry_policy"],
        "topic_repeat_lock_days": guardrails["topic_repeat_lock"]["window_days"],
        "topic_ledger": str(TOPIC_LEDGER.relative_to(ROOT)),
        "people_biocuriosity": guardrails["people_biocuriosity"],
        "publishing_target": contract["publishing"]["current_verified_route"],
        "recovery_trigger": contract["recovery_trigger"],
    }

def parse_date(raw: str, field: str) -> date:
    try:
        return date.fromisoformat(raw)
    except Exception as exc:
        raise GateError(f"INVALID_{field.upper()}:{raw}") from exc

def topic_collisions(job, guardrails):
    semantic_topic_id = str(job.get("semantic_topic_id") or "").strip()
    content_id = str(job.get("content_id") or "").strip()
    publish_date_raw = str(job.get("publish_date_local") or "").strip()
    if not semantic_topic_id: raise GateError("SEMANTIC_TOPIC_ID_MISSING")
    if not content_id: raise GateError("CONTENT_ID_MISSING")
    if not publish_date_raw: raise GateError("PUBLISH_DATE_LOCAL_MISSING")
    publish_date = parse_date(publish_date_raw, "publish_date_local")
    ledger = load_json(TOPIC_LEDGER)
    window_days = int(guardrails["topic_repeat_lock"]["window_days"])
    collisions=[]
    for entry in ledger.get("entries", []):
        if str(entry.get("semantic_topic_id") or "") != semantic_topic_id: continue
        if str(entry.get("content_id") or "") == content_id: continue
        entry_date_raw = str(entry.get("date_local") or "")
        if not entry_date_raw: continue
        age=(publish_date-parse_date(entry_date_raw,"ledger_date_local")).days
        if 0 <= age <= window_days:
            collisions.append({"content_id":entry.get("content_id"),"title":entry.get("title"),"date_local":entry_date_raw,"status":entry.get("status"),"age_days":age})
    return collisions

def assert_topic_history(job, guardrails):
    collisions=topic_collisions(job,guardrails)
    if not collisions:
        return {"classification":"NEW_TOPIC","collisions":[]}
    if job.get("repeat_exception") is not True:
        raise GateError("BLOCK_TOPIC_REPEAT:"+",".join(str(x.get("content_id")) for x in collisions))
    required=["repeat_exception_reason","new_event_source","new_event_date"]
    missing=[k for k in required if not str(job.get(k) or "").strip()]
    if missing: raise GateError("REPEAT_EXCEPTION_FIELDS_MISSING:"+",".join(missing))
    parse_date(str(job["new_event_date"]),"new_event_date")
    return {"classification":"BREAKING_EXCEPTION","collisions":collisions}

def assert_music(job, contract):
    policy=contract["music_policy"]
    metadata=["music_track_title","music_artist_or_composer","music_source","music_license_or_usage_basis","music_editorial_class"]
    missing=[k for k in metadata if not str(job.get(k) or "").strip()]
    if missing: raise GateError("MUSIC_METADATA_MISSING:"+",".join(missing))
    gates=["music_composition_gate","music_theme_match_gate","music_audibility_gate","music_no_tone_or_game_style_gate","music_rights_gate"]
    failed=[k for k in gates if job.get(k)!="PASS"]
    if failed: raise GateError("MUSIC_GATE_NOT_PASS:"+",".join(failed))
    if job.get("music_has_vocals") is True: raise GateError("MUSIC_VOCALS_FORBIDDEN")
    if str(job.get("music_form") or "").strip().lower() in {str(x).lower() for x in policy.get("forbidden_music_forms",[])}:
        raise GateError("FORBIDDEN_MUSIC_FORM")
    return {"track_title":job["music_track_title"],"artist_or_composer":job["music_artist_or_composer"]}

def as_int(value, field):
    try: return int(value)
    except Exception as exc: raise GateError(f"INVALID_INTEGER_FIELD:{field}") from exc

def assert_footage(job, guardrails):
    applicability=str(job.get("real_footage_applicability") or "").strip().upper()
    if applicability not in {"REQUIRED","NOT_APPLICABLE"}: raise GateError("REAL_FOOTAGE_APPLICABILITY_MISSING_OR_INVALID")
    is_person=job.get("content_class")=="PERSON_PROFILE"
    if is_person and applicability!="REQUIRED": raise GateError("PERSON_PROFILE_REAL_FOOTAGE_REQUIRED")
    if applicability=="NOT_APPLICABLE":
        if not str(job.get("real_footage_not_applicable_reason") or "").strip(): raise GateError("REAL_FOOTAGE_NOT_APPLICABLE_REASON_MISSING")
        return {"applicability":applicability}
    if job.get("real_footage_gate")!="PASS": raise GateError("REAL_FOOTAGE_GATE_NOT_PASS")
    blocks=as_int(job.get("real_footage_block_count"),"real_footage_block_count")
    distinct=as_int(job.get("distinct_real_clip_count"),"distinct_real_clip_count")
    policy=guardrails["real_footage_alternation"]
    if blocks < int(policy.get("minimum_real_footage_blocks",3)): raise GateError(f"REAL_FOOTAGE_BLOCKS_TOO_FEW:{blocks}")
    if distinct < int(policy.get("minimum_distinct_real_clips_or_angles",2)): raise GateError(f"DISTINCT_REAL_CLIPS_TOO_FEW:{distinct}")
    result={"applicability":applicability,"blocks":blocks,"distinct_clips":distinct}
    if is_person:
        if job.get("person_visual_reference_gate")!="PASS": raise GateError("PERSON_VISUAL_REFERENCE_GATE_NOT_PASS")
        if job.get("person_real_video_segments_gate")!="PASS": raise GateError("PERSON_REAL_VIDEO_SEGMENTS_GATE_NOT_PASS")
        segments=as_int(job.get("person_real_video_segment_count"),"person_real_video_segment_count")
        if segments < int(guardrails["people_biocuriosity"].get("minimum_distinct_real_person_video_segments",2)):
            raise GateError(f"PERSON_REAL_VIDEO_SEGMENTS_TOO_FEW:{segments}")
        result["person_real_video_segments"]=segments
    return result

def assert_mask(job):
    guard=load_json(MASK_GUARD)
    expected=str(guard["mask"]["sha256"])
    if str(job.get("mask_sha256") or "")!=expected: raise GateError("CANONICAL_MASK_V2_HASH_MISMATCH")
    for k in ["clean_header_gate","clean_cc_zone_gate","single_title_render_gate","canonical_mask_v2_gate"]:
        if job.get(k)!="PASS": raise GateError(f"MASK_GATE_NOT_PASS:{k}")
    if job.get("legacy_v1_body_shell_used") is True: raise GateError("LEGACY_V1_MASK_FORBIDDEN")
    if job.get("header_cover_panel_used") is True: raise GateError("TITLE_OVER_TITLE")
    return {"mask_sha256":expected,"status":"PASS"}

def assert_preventive(job, contract):
    approved=set(contract["voice_policy"]["approved_profiles"])
    if job.get("voice_profile") not in approved or job.get("voice_ptbr_neutral_gate")!="PASS":
        raise GateError("VOICE_PTBR_NEUTRAL_FAIL")
    if job.get("fresh_build") is not True or job.get("prior_final_master_used") is not False:
        raise GateError("MASTER_FRESH_BUILD_FAIL")
    if job.get("pre_cta_contamination_gate")!="PASS" or job.get("legacy_or_unrelated_frame_before_cta") is not False:
        raise GateError("PRE_CTA_CONTAMINATION_FAIL")
    if job.get("final_master_qa_gate")!="PASS": raise GateError("FINAL_MASTER_QA_NOT_PASS")
    if job.get("scheduler_release_token_gate")!="PASS": raise GateError("SCHEDULER_RELEASE_TOKEN_NOT_PASS")
    if job.get("content_class")=="PERSON_PROFILE" and job.get("entity_integrity_gate")!="PASS":
        raise GateError("ENTITY_INTEGRITY_NOT_PASS")

def preflight(args):
    current=load_json(CURRENT); contract=load_json(CONTRACT); guardrails=load_json(GUARDRAILS)
    assert_channel(args.channel); assert_path_isolation(args.write_path); assert_account(args.account_id,contract)
    if current.get("contract")!="canonical/vsa/v1/VSA_CANONICAL_PRODUCTION_CONTRACT_V1.json": raise GateError("CURRENT_POINTER_MISMATCH")
    print(json.dumps(canonical_plan(contract,guardrails),ensure_ascii=False,indent=2))

def check_topic(args):
    guardrails=load_json(GUARDRAILS)
    job={"semantic_topic_id":args.semantic_topic_id,"content_id":args.content_id,"publish_date_local":args.publish_date_local,"repeat_exception":args.repeat_exception,"repeat_exception_reason":args.repeat_exception_reason,"new_event_source":args.new_event_source,"new_event_date":args.new_event_date}
    print(json.dumps({"status":"PASS",**assert_topic_history(job,guardrails)},ensure_ascii=False,indent=2))

def validate_job(args):
    contract=load_json(CONTRACT); guardrails=load_json(GUARDRAILS); job=json.loads(Path(args.job).read_text(encoding="utf-8"))
    assert_channel(job.get("channel","")); assert_path_isolation(job.get("write_paths",[])); assert_account(job.get("social_account_id"),contract)
    required=["content_id","title","script","semantic_map","semantic_topic_id","publish_date_local","rights_manifest","base_video_qa","final_qa","topic_history_gate","music_track_title","music_artist_or_composer","music_source","music_license_or_usage_basis","music_editorial_class","music_composition_gate","music_theme_match_gate","music_audibility_gate","music_no_tone_or_game_style_gate","music_rights_gate","real_footage_applicability","voice_profile","voice_ptbr_neutral_gate","fresh_build","prior_final_master_used","pre_cta_contamination_gate","legacy_or_unrelated_frame_before_cta","final_master_qa_gate","scheduler_release_token_gate","canonical_mask_v2_gate"]
    missing=[k for k in required if k not in job or job.get(k) is None or job.get(k)==""]
    if missing: raise GateError("JOB_REQUIRED_FIELDS_MISSING:"+",".join(missing))
    topic=assert_topic_history(job,guardrails); music=assert_music(job,contract); footage=assert_footage(job,guardrails); mask=assert_mask(job); assert_preventive(job,contract)
    if job.get("topic_history_gate")!="PASS": raise GateError("TOPIC_HISTORY_GATE_NOT_PASS")
    if job.get("base_video_qa")!="PASS" or job.get("final_qa")!="PASS": raise GateError("QA_NOT_PASS")
    if job.get("rights_manifest")!="PASS": raise GateError("RIGHTS_GATE_NOT_PASS")
    print(json.dumps({"status":"VSA_JOB_RELEASE_ELIGIBLE","title":job["title"],"topic_classification":topic["classification"],"music":music,"real_footage":footage,"mask":mask,"publisher":contract["publishing"]["current_verified_route"]},ensure_ascii=False))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("preflight"); p.add_argument("--channel",required=True); p.add_argument("--account-id",type=int); p.add_argument("--write-path",action="append",default=[]); p.set_defaults(func=preflight)
    t=sub.add_parser("check-topic"); t.add_argument("--semantic-topic-id",required=True); t.add_argument("--content-id",required=True); t.add_argument("--publish-date-local",required=True); t.add_argument("--repeat-exception",action="store_true"); t.add_argument("--repeat-exception-reason"); t.add_argument("--new-event-source"); t.add_argument("--new-event-date"); t.set_defaults(func=check_topic)
    v=sub.add_parser("validate-job"); v.add_argument("--job",required=True); v.set_defaults(func=validate_job)
    args=ap.parse_args()
    try: args.func(args)
    except GateError as e:
        print(json.dumps({"status":"BLOCKED","reason":str(e)},ensure_ascii=False),file=sys.stderr); raise SystemExit(2)

if __name__=="__main__": main()
