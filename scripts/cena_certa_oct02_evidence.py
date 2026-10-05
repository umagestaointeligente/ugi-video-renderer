"""Oct02 production evidence must be bound to this execution and actual bytes."""
import json
import sys
from pathlib import Path
from cena_certa_render_evidence_guard import validate_pack

NETWORKS = {"youtube", "facebook", "instagram", "tiktok"}
EXECUTION = {"run_id", "run_attempt", "head_sha", "job_id"}

def reconcile(summary, receipts, media_dir, history, expected):
    result = validate_pack(summary, receipts, media_dir)
    errors = []
    items = summary.get("items", [])
    if {i.get("network") for i in items} != NETWORKS:
        errors.append("NETWORK_BATCH_INCOMPLETE")
    if not all(expected.get(k) for k in EXECUTION):
        errors.append("EXECUTION_IDENTITY_MISSING")
    for item in items:
        rec = receipts.get(item["id"], {})
        if item.get("execution") != expected or rec.get("execution") != expected:
            errors.append("EXECUTION_MISMATCH:" + item["id"])
        # Existing issued evidence is a reservation, not proof of publication.
        # Re-encoding an overlapping source cannot become a new scene approval.
        for old in history.get("items", []):
            if old.get("source_id") == item.get("source_id"):
                a, b = item.get("source_start_sec"), item.get("source_end_sec")
                c, d = old.get("source_start_sec"), old.get("source_end_sec")
                if not all(isinstance(v, (int, float)) for v in (a,b,c,d)):
                    errors.append("SCENE_RANGE_MISSING:" + item["id"])
                elif max(a,c) < min(b,d):
                    errors.append("PRIOR_SCENE_RESERVATION:" + item["id"])
        # Bind the full history used by the checker to its exact serialized bytes.
        import hashlib
        digest = hashlib.sha256(json.dumps(history, sort_keys=True).encode()).hexdigest()
        if rec.get("anti_repeat", {}).get("reservation_history_sha256") != digest:
            errors.append("HISTORY_BINDING_MISMATCH:" + item["id"])
    result["execution"] = expected
    result["errors"] = errors
    if errors:
        result["status"] = "BLOCK"
        for row in result["items"]:
            row["status"] = "BLOCK"
            row["errors"].append("BATCH_RECONCILIATION_FAILED")
    result["publication_status"] = "NOT_VERIFIED"
    return result

def main():
    import os
    root = Path(sys.argv[1])
    receipts = json.loads(Path(sys.argv[2]).read_text())
    history = json.loads(Path(sys.argv[3]).read_text())
    expected = dict(zip(("run_id","run_attempt","head_sha","job_id"),
                        (os.getenv("GITHUB_RUN_ID"),os.getenv("GITHUB_RUN_ATTEMPT"),
                         os.getenv("GITHUB_SHA"),os.getenv("GITHUB_JOB"))))
    result = reconcile(json.loads((root/"summary.json").read_text()), receipts, root, history, expected)
    (root/"preflight.json").write_text(json.dumps(result, indent=2))
    print("CENA_CERTA_PREFLIGHT=" + result["status"])
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
