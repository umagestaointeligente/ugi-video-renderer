#!/usr/bin/env python3
"""Fail-closed VSA canonical runtime guard.

This module does not replace the renderer. It is the mandatory policy gate that
resolves VSA canon, validates channel/account isolation and emits a canonical
render/publish plan before downstream production or scheduling.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT = ROOT / "canonical" / "vsa" / "CURRENT.json"
CONTRACT = ROOT / "canonical" / "vsa" / "v1" / "VSA_CANONICAL_PRODUCTION_CONTRACT_V1.json"
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
    approved = lock["approved_post_bridge_account"]["id"]
    if int(account_id) != int(approved):
        raise GateError(f"UNVERIFIED_VSA_ACCOUNT:{account_id}")

def asset_fingerprint(contract):
    return {
        "mask": {"library_path": contract["mask"]["library_path"], "sha256": contract["mask"]["sha256"]},
        "cta": {"library_path": contract["cta"]["library_path"], "sha256": contract["cta"]["sha256"]},
    }

def canonical_plan(contract):
    return {
        "status": "VSA_CANON_RESOLVED",
        "project": contract["project_lock"]["project"],
        "channel": contract["project_lock"]["channel_name"],
        "format": contract["format"],
        "visual_sequence": contract["visual_grammar"]["preferred_sequence"],
        "mask_apply_stage": contract["mask"]["apply_stage"],
        "fixed_assets": asset_fingerprint(contract),
        "qa_workflow": contract["qa"]["workflow"],
        "publishing_target": contract["publishing"]["current_verified_route"],
        "recovery_trigger": contract["recovery_trigger"],
    }

def preflight(args):
    current = load_json(CURRENT)
    contract = load_json(CONTRACT)
    assert_channel(args.channel)
    assert_path_isolation(args.write_path)
    assert_account(args.account_id, contract)
    if current.get("contract") != "canonical/vsa/v1/VSA_CANONICAL_PRODUCTION_CONTRACT_V1.json":
        raise GateError("CURRENT_POINTER_MISMATCH")
    print(json.dumps(canonical_plan(contract), ensure_ascii=False, indent=2))

def validate_job(args):
    contract = load_json(CONTRACT)
    job = json.loads(Path(args.job).read_text(encoding="utf-8"))
    assert_channel(job.get("channel", ""))
    assert_path_isolation(job.get("write_paths", []))
    assert_account(job.get("social_account_id"), contract)
    required = ["title", "script", "semantic_map", "rights_manifest", "base_video_qa", "final_qa"]
    missing = [k for k in required if not job.get(k)]
    if missing:
        raise GateError("JOB_REQUIRED_FIELDS_MISSING:" + ",".join(missing))
    if job.get("base_video_qa") != "PASS" or job.get("final_qa") != "PASS":
        raise GateError("QA_NOT_PASS")
    if job.get("rights_manifest") != "PASS":
        raise GateError("RIGHTS_GATE_NOT_PASS")
    print(json.dumps({"status":"VSA_JOB_RELEASE_ELIGIBLE","title":job["title"]}, ensure_ascii=False))

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight")
    p.add_argument("--channel", required=True)
    p.add_argument("--account-id", type=int)
    p.add_argument("--write-path", action="append", default=[])
    p.set_defaults(func=preflight)
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
