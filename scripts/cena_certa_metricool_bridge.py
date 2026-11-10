#!/usr/bin/env python3
"""Durable handoff to the Metricool connector; never claims to publish by itself.

Call prepare, persist a claim BEFORE createScheduledPost, then reconcile its ID
against a fresh Planner read. A timeout stays UNKNOWN and cannot be retried.
"""
import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from cena_certa_oct13_compile import safe_https
from cena_certa_render_evidence_guard import validate_pack

BRAND = "6809869"
NETWORKS = {"instagram", "facebook", "tiktok", "youtube"}
TZ = ZoneInfo("America/Sao_Paulo")


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else None
    except ValueError:
        return None


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fresh(value, now, minutes=15):
    checked = timestamp(value)
    return checked is not None and timedelta(0) <= now - checked <= timedelta(minutes=minutes)


def save(path, document):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        json.dump(document, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def prepare(batch, receipts, media_dir, snapshot, now=None):
    now = now or datetime.now(timezone.utc)
    items = batch.get("items", [])
    errors = []
    if str(batch.get("metricool_brand_id")) != BRAND or batch.get("timezone") != str(TZ):
        errors.append("BRAND_OR_TIMEZONE_MISMATCH")
    if len(items) != 12 or any(sum(x.get("network") == n for x in items) != 3 for n in NETWORKS):
        errors.append("REQUIRE_THREE_DIFFERENT_VIDEOS_PER_NETWORK")
    if (not isinstance(snapshot, dict) or str(snapshot.get("brand_id")) != BRAND
            or not fresh(snapshot.get("checked_at"), now)
            or snapshot.get("complete") is not True or not isinstance(snapshot.get("posts"), list)):
        errors.append("FRESH_COMPLETE_PLANNER_READ_REQUIRED")
    gate = validate_pack(batch, receipts, media_dir, now)
    if gate["status"] != "PASS":
        errors.append("RENDER_RELEASE_EVIDENCE_BLOCKED")
    rows, hashes, slots = [], set(), set()
    for item in items:
        ident = item.get("id", "")
        issues = []
        sha = item.get("sha256")
        network = item.get("network")
        slot = timestamp(item.get("slot"))
        if not slot or slot <= now or slot.astimezone(TZ).date().isoformat() != batch.get("publication_date"):
            issues.append("SLOT_NOT_FUTURE_OR_WRONG_DAY")
        if network not in NETWORKS or (network, slot) in slots:
            issues.append("NETWORK_OR_SLOT_INVALID")
        slots.add((network, slot))
        if sha in hashes:
            issues.append("SAME_MASTER_ACROSS_NETWORKS")
        hashes.add(sha)
        for name in ("audio_pt_br", "subtitles", "editorial"):
            entry = receipts.get(ident, {}).get(name, {})
            if entry.get("status") != "PASS" or not entry.get("evidence"):
                issues.append(name.upper() + "_REVIEW_REQUIRED")
        url = item.get("master_mp4_url")
        upload = receipts.get(ident, {}).get("uploaded_master", {})
        if (not safe_https(url) or upload.get("url") != url or upload.get("sha256") != sha
                or upload.get("downloaded_sha256") != sha or not fresh(upload.get("checked_at"), now)):
            issues.append("UPLOADED_BYTES_NOT_VERIFIED")
        for post in snapshot.get("posts", []) if isinstance(snapshot, dict) else []:
            if post.get("media_url") == url or post.get("master_sha256") == sha:
                issues.append("MASTER_ALREADY_IN_PLANNER")
            if post.get("network") == network and timestamp(post.get("slot")) == slot:
                issues.append("SLOT_ALREADY_IN_PLANNER")
        if not item.get("caption") or not item.get("title"):
            issues.append("TITLE_OR_CAPTION_MISSING")
        key = hashlib.sha256(f"{BRAND}:{network}:{sha}".encode()).hexdigest()
        rows.append({"id": ident, "network": network, "slot": item.get("slot"),
                     "master_sha256": sha, "media_url": url, "title": item.get("title"),
                     "caption": item.get("caption"), "idempotency_key": key,
                     "errors": issues, "state": "BLOCKED" if issues else "READY"})
    blocked = bool(errors) or any(r["errors"] for r in rows)
    return {"schema": "CENA_CERTA_METRICOOL_HANDOFF_V1", "brand_id": BRAND,
            "generated_at": now.isoformat(), "publication_date": batch.get("publication_date"),
            "state": "BLOCKED" if blocked else "READY_TO_SCHEDULE", "errors": errors,
            "release_evidence": gate, "items": rows, "confirmed_count": 0,
            "scheduled": False, "published": False}


def claim(plan, ident, ledger_path, now=None):
    """Claim once under an OS lock; interrupted/uncertain creates stay reserved."""
    now = now or datetime.now(timezone.utc)
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.with_suffix(".lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if plan.get("state") != "READY_TO_SCHEDULE" or not fresh(plan.get("generated_at"), now):
            raise ValueError("PLAN_BLOCKED_OR_STALE")
        row = next(x for x in plan["items"] if x["id"] == ident)
        if timestamp(row["slot"]) <= now:
            raise ValueError("SLOT_EXPIRED")
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
        key = row["idempotency_key"]
        if key in ledger:
            raise ValueError("ALREADY_CLAIMED_RECONCILE_BEFORE_RETRY")
        for old in ledger.values():
            if old["network"] == row["network"] and timestamp(old["slot"]) == timestamp(row["slot"]):
                raise ValueError("SLOT_ALREADY_CLAIMED")
        ledger[key] = dict(row, state="UNKNOWN", claimed_at=now.isoformat(), metricool_id=None)
        save(ledger_path, ledger)
        return ledger[key]


def reconcile(ledger_path, key, post_id, snapshot, now=None):
    now = now or datetime.now(timezone.utc)
    path = Path(ledger_path)
    with path.with_suffix(".lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        ledger = json.loads(path.read_text())
        row = ledger[key]
        if (str(snapshot.get("brand_id")) != BRAND or snapshot.get("complete") is not True
                or not fresh(snapshot.get("checked_at"), now)
                or timestamp(snapshot.get("checked_at")) < timestamp(row["claimed_at"])):
            raise ValueError("FRESH_COMPLETE_PLANNER_READ_REQUIRED")
        matches = [p for p in snapshot.get("posts", []) if str(p.get("id")) == str(post_id)]
        if len(matches) != 1:
            raise ValueError("POST_ID_NOT_UNIQUELY_CONFIRMED")
        post = matches[0]
        if (post.get("network") != row["network"] or timestamp(post.get("slot")) != timestamp(row["slot"])
                or post.get("media_url") != row["media_url"] or post.get("status") != "SCHEDULED"
                or not safe_https(post.get("planner_url"))
                or urlparse(post["planner_url"]).hostname not in {"app.metricool.com", "metricool.com"}):
            raise ValueError("PLANNER_READBACK_MISMATCH")
        row.update(state="SCHEDULE_CONFIRMED", metricool_id=str(post_id),
                   planner_url=post["planner_url"], confirmed_at=now.isoformat())
        save(path, ledger)
        return row


def summary(ledger, publication_date):
    confirmed = [x for x in ledger.values() if x.get("state") == "SCHEDULE_CONFIRMED"
                 and timestamp(x.get("slot"))
                 and timestamp(x["slot"]).astimezone(TZ).date().isoformat() == publication_date]
    return {"brand_id": BRAND, "publication_date": publication_date, "confirmed_count": len(confirmed),
            "counts_by_network": {n: sum(x["network"] == n for x in confirmed) for n in sorted(NETWORKS)},
            "published": False,
            "items": [{k: row[k] for k in ("id", "network", "slot", "metricool_id", "planner_url")}
                      for row in confirmed]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    for name in ("batch", "receipts", "media-dir", "snapshot", "out"):
        p.add_argument("--" + name, required=True)
    p = sub.add_parser("claim")
    for name in ("plan", "id", "ledger"):
        p.add_argument("--" + name, required=True)
    p = sub.add_parser("reconcile")
    for name in ("ledger", "key", "post-id", "snapshot"):
        p.add_argument("--" + name, required=True)
    args = parser.parse_args()
    read = lambda file: json.loads(Path(file).read_text())
    if args.command == "prepare":
        result = prepare(read(args.batch), read(args.receipts), args.media_dir, read(args.snapshot))
        save(args.out, result)
        print(json.dumps({"state": result["state"], "confirmed_count": 0, "errors": result["errors"]}))
        return int(result["state"] == "BLOCKED")
    if args.command == "claim":
        result = claim(read(args.plan), args.id, args.ledger)
    else:
        result = reconcile(args.ledger, args.key, args.post_id, read(args.snapshot))
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
