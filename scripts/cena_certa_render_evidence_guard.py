#!/usr/bin/env python3
"""Fail closed on missing, stale or mismatched Cena Certa render receipts.

This validates evidence structure and bindings; it does not manufacture visual,
rights or history approval. Receipts must come from the corresponding checks.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import os

CONTRACT = "CENA_CERTA_RENDER_EVIDENCE_V1"
POSITIONS = {"0s", "1.5s", "first_third", "midpoint", "last_third", "last_frame"}
LAYERS = {"normalized_title", "source_id", "master_sha256", "perceptual_frames", "temporal_overlap"}

def _date(value):
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return result if result.tzinfo else None
    except (ValueError, TypeError):
        return None

def validate_receipt(item, receipt, now=None):
    now = now or datetime.now(timezone.utc)
    errors = []
    if not isinstance(receipt, dict):
        return ["RENDER_RECEIPT_MISSING"]
    master = item.get("sha256", item.get("final_render_media_id_or_hash", ""))
    master = str(master).removeprefix("sha256:")
    if not re.fullmatch(r"[0-9a-f]{64}", master):
        errors.append("MASTER_SHA256_INVALID")
    if receipt.get("contract") != CONTRACT:
        errors.append("EVIDENCE_CONTRACT_MISMATCH")
    if receipt.get("master_sha256") != master:
        errors.append("EVIDENCE_MASTER_MISMATCH")
    if receipt.get("content_id") != item.get("id", item.get("content_id")):
        errors.append("EVIDENCE_CONTENT_MISMATCH")
    checked = _date(receipt.get("checked_at"))
    if checked is None or checked > now or now - checked > timedelta(hours=24):
        errors.append("EVIDENCE_STALE_OR_INVALID")
    source = receipt.get("source", {})
    if not isinstance(source, dict):
        source = {}
    source_id = item.get("source_id")
    if not source_id or str(source.get("extracted_id", "")) != str(source_id):
        errors.append("SOURCE_ID_NOT_VERIFIED")
    if source.get("url") != item.get("source") or source.get("identity_pass") is not True or not source.get("metadata_receipt"):
        errors.append("SOURCE_IDENTITY_NOT_PROVEN")
    for gate in ("rights", "visual", "transformation", "cta"):
        entry = receipt.get(gate)
        if not isinstance(entry, dict) or entry.get("status") != "PASS" or not entry.get("evidence"):
            errors.append(gate.upper() + "_EVIDENCE_NOT_PROVEN")
    visual = receipt.get("visual", {})
    if not isinstance(visual, dict):
        visual = {}
    frames = visual.get("frames", {})
    if not isinstance(frames, dict) or not all(frames.get(p) for p in POSITIONS):
        errors.append("REPRESENTATIVE_FRAMES_INCOMPLETE")
    if visual.get("exact_subject_match") is not True or visual.get("source_cta_removed") is not True:
        errors.append("VISUAL_SUBJECT_OR_SOURCE_CTA_NOT_PROVEN")
    repeat = receipt.get("anti_repeat", {})
    if not isinstance(repeat, dict):
        repeat = {}
    start, end = _date(repeat.get("history_start")), _date(repeat.get("history_end"))
    if start is None or end is None or end > now or end - start < timedelta(days=60) or now - end > timedelta(hours=24):
        errors.append("ANTI_REPEAT_HISTORY_INCOMPLETE_OR_STALE")
    if repeat.get("status") != "PASS" or repeat.get("history_complete") is not True or not repeat.get("history_receipt"):
        errors.append("ANTI_REPEAT_NOT_PROVEN")
    if not LAYERS.issubset(set(repeat.get("comparison_layers", []))) or not repeat.get("fingerprint_receipt") or repeat.get("scene_overlap_detected") is not False:
        errors.append("PERCEPTUAL_ANTI_REPEAT_NOT_PROVEN")
    if item.get("kind") == "humor":
        src, out = item.get("source_duration_sec"), item.get("duration_sec")
        if not isinstance(src, (int, float)) or src <= 0 or not isinstance(out, (int, float)):
            errors.append("SOURCE_DURATION_MISSING")
        elif out / src >= 0.9:
            exception = receipt.get("near_full_source_exception", {})
            if not isinstance(exception, dict) or exception.get("approved_by") != "Paulo" or not exception.get("evidence") or exception.get("master_sha256") != master:
                errors.append("NEAR_FULL_SOURCE_EXCEPTION_MISSING")
    return errors

def validate_pack(summary, receipts, media_dir, now=None, execution=None):
    rows = []
    if not isinstance(summary, dict) or not isinstance(receipts, dict):
        return {"status": "BLOCK", "errors": ["PACK_OR_RECEIPTS_INVALID"], "items": []}
    items = summary.get("items", [])
    if not isinstance(items, list) or not items:
        return {"status": "BLOCK", "errors": ["PACK_EMPTY"], "items": []}
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            rows.append({"content_id": None, "status": "BLOCK", "errors": ["ITEM_INVALID"]})
            continue
        ident = item.get("id", "")
        errors = validate_receipt(item, receipts.get(ident), now)
        if execution:
            receipt = receipts.get(ident)
            if not isinstance(receipt, dict) or any(not value or receipt.get(key) != value for key, value in execution.items()):
                errors.append("RECEIPT_EXECUTION_MISMATCH")
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", ident) or ident in seen:
            errors.append("ITEM_ID_INVALID_OR_DUPLICATE")
        else:
            path = Path(media_dir) / (ident + ".mp4")
            network = item.get("network")
            if network in {"tiktok", "instagram", "youtube", "facebook"} and not path.is_file():
                path = Path(media_dir) / network / (ident + ".mp4")
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
                errors.append("FINAL_FILE_HASH_MISMATCH")
        seen.add(ident)
        if item.get("technical_status") != "PASS":
            errors.append("TECHNICAL_QA_NOT_PROVEN")
        rows.append({"content_id": ident, "status": "BLOCK" if errors else "PASS", "errors": errors})
    blocked = any(row["errors"] for row in rows)
    if blocked:
        for row in rows:
            if row["status"] == "PASS":
                row["status"] = "BLOCK"
                row["errors"].append("BATCH_SIBLING_REVALIDATION_REQUIRED")
    return {"contract": CONTRACT, "status": "BLOCK" if blocked else "PASS", "publication_status": "NOT_VERIFIED", "items": rows}


def validate_fingerprint_files(summary, root):
    errors = []
    documents = {}
    for name, field in (("history-fingerprints.json", "history_fingerprint_receipt_sha256"),
                        ("candidate-fingerprints.json", "candidate_fingerprint_receipt_sha256")):
        path = root / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != summary.get(field):
            errors.append("FINGERPRINT_FILE_MISSING_OR_CHANGED:" + name)
            continue
        documents[name] = json.loads(path.read_text())
    candidates = documents.get("candidate-fingerprints.json", {})
    rows = candidates.get("items", [])
    expected = {item["id"]: item["sha256"] for item in summary.get("items", [])}
    if len(rows) != len(expected) or {row.get("id"): row.get("master_sha256") for row in rows} != expected:
        errors.append("CANDIDATE_FINGERPRINT_MASTER_BINDING_MISMATCH")
    if candidates.get("violations") or any(not row.get("frames") for row in rows):
        errors.append("CANDIDATE_FINGERPRINT_REPEAT_OR_MISSING")
    history = documents.get("history-fingerprints.json", {})
    eligible = history.get("eligible_count")
    if history.get("coverage") != 1.0 or not isinstance(eligible, int) or eligible < 1 or len(history.get("items", [])) != eligible:
        errors.append("HISTORY_FINGERPRINT_COVERAGE_INCOMPLETE")
    return errors

def main():
    summary_path, receipt_path, output_path = map(Path, sys.argv[1:4])
    execution = {key: os.environ.get(env) for key, env in (
        ("run_id", "GITHUB_RUN_ID"), ("run_attempt", "GITHUB_RUN_ATTEMPT"), ("commit", "GITHUB_SHA"))}
    try:
        summary = json.loads(summary_path.read_text())
        receipts = json.loads(receipt_path.read_text()) if receipt_path.is_file() else {}
        result = validate_pack(summary, receipts, summary_path.parent, execution=execution)
        if re.match(r"CENA_CERTA_OCT(?:05|06|07|08|09|11)_DELIVERY", str(summary.get("schema", ""))):
            fingerprint_errors = validate_fingerprint_files(summary, summary_path.parent)
            if fingerprint_errors:
                result["status"] = "BLOCK"
                result["errors"] = fingerprint_errors
        result["summary_sha256"] = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
        result = {"status": "BLOCK", "errors": ["EVIDENCE_INPUT_INVALID"], "detail": str(exc)[:500]}
    result.update(execution, publication_status="NOT_VERIFIED")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2))
    temporary.replace(output_path)
    print("CENA_CERTA_PREFLIGHT=" + result["status"])
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
