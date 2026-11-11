import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from cena_certa_metricool_bridge import prepare, claim, reconcile, summary
from cena_certa_render_evidence_guard import CONTRACT, LAYERS, POSITIONS


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.now = datetime(2026, 11, 10, 12, tzinfo=timezone.utc)
        self.snapshot = dict(brand_id="6809869", checked_at=self.now.isoformat(), complete=True, posts=[])
        self.batch = dict(metricool_brand_id=6809869, timezone="America/Sao_Paulo",
                          publication_date="2026-11-10", items=[])
        self.receipts = {}
        for network in ("tiktok", "instagram", "facebook", "youtube"):
            for index in range(3):
                ident = f"CC-TEST-{network}-{index}"
                data = ident.encode()
                sha = hashlib.sha256(data).hexdigest()
                (self.root / (ident + ".mp4")).write_bytes(data)
                item = dict(id=ident, network=network, sha256=sha, technical_status="PASS",
                            source="https://example.invalid/source", source_id=ident,
                            slot=f"2026-11-10T{18+index}:00:00-03:00", title=ident, caption="fixture caption",
                            master_mp4_url=f"https://example.invalid/{ident}.mp4")
                self.batch["items"].append(item)
                receipt = dict(contract=CONTRACT, content_id=ident, master_sha256=sha,
                    checked_at=self.now.isoformat(),
                    source=dict(extracted_id=ident, url=item["source"], identity_pass=True, metadata_receipt="fixture"),
                    visual=dict(status="PASS", evidence="fixture", exact_subject_match=True,
                                source_cta_removed=True, frames={p:"fixture" for p in POSITIONS}),
                    anti_repeat=dict(status="PASS", history_complete=True, history_receipt="fixture",
                        history_start=(self.now-timedelta(days=180)).isoformat(), history_end=self.now.isoformat(),
                        comparison_layers=list(LAYERS), fingerprint_receipt="fixture", scene_overlap_detected=False),
                    uploaded_master=dict(url=item["master_mp4_url"], sha256=sha, downloaded_sha256=sha,
                                         checked_at=self.now.isoformat()))
                for gate in ("rights", "transformation", "cta", "audio_pt_br", "subtitles", "editorial"):
                    receipt[gate] = dict(status="PASS", evidence="fixture")
                self.receipts[ident] = receipt
        self.ledger = self.root / "ledger.json"

    def plan(self):
        return prepare(self.batch, self.receipts, self.root, self.snapshot, self.now)

    def test_ready_does_not_mean_scheduled(self):
        plan = self.plan()
        self.assertEqual(plan["state"], "READY_TO_SCHEDULE")
        self.assertFalse(plan["scheduled"])
        self.assertEqual(plan["confirmed_count"], 0)

    def test_old_candidate_without_release_receipts_blocks(self):
        self.receipts = {}
        self.assertEqual(self.plan()["state"], "BLOCKED")

    def test_changed_master_blocks(self):
        ident = self.batch["items"][0]["id"]
        (self.root / (ident + ".mp4")).write_bytes(b"changed after review")
        self.assertEqual(self.plan()["state"], "BLOCKED")

    def test_audio_subtitles_and_upload_required(self):
        ident = self.batch["items"][0]["id"]
        for gate in ("audio_pt_br", "subtitles", "editorial", "uploaded_master"):
            original = self.receipts[ident].pop(gate)
            self.assertEqual(self.plan()["state"], "BLOCKED", gate)
            self.receipts[ident][gate] = original

    def test_wrong_brand_stale_snapshot_and_past_slot_block(self):
        self.snapshot["brand_id"] = "6935441"
        self.assertEqual(self.plan()["state"], "BLOCKED")
        self.snapshot["brand_id"] = "6809869"
        self.snapshot["checked_at"] = (self.now-timedelta(minutes=16)).isoformat()
        self.assertEqual(self.plan()["state"], "BLOCKED")
        self.snapshot["checked_at"] = self.now.isoformat()
        self.batch["items"][0]["slot"] = "2026-11-10T08:00:00-03:00"
        self.assertEqual(self.plan()["state"], "BLOCKED")

    def test_existing_post_blocks_duplicate(self):
        self.snapshot["posts"].append(dict(media_url=self.batch["items"][0]["master_mp4_url"]))
        self.assertEqual(self.plan()["state"], "BLOCKED")

    def test_uncertain_create_cannot_retry_even_in_new_slot(self):
        plan = self.plan()
        row = claim(plan, plan["items"][0]["id"], self.ledger, self.now)
        self.assertEqual(row["state"], "UNKNOWN")
        plan["items"][0]["slot"] = "2026-11-10T23:00:00-03:00"
        with self.assertRaisesRegex(ValueError, "RECONCILE_BEFORE_RETRY"):
            claim(plan, plan["items"][0]["id"], self.ledger, self.now)

    def test_exact_readback_required(self):
        plan = self.plan()
        row = claim(plan, plan["items"][0]["id"], self.ledger, self.now)
        snapshot = copy.deepcopy(self.snapshot)
        post = dict(id="fixture-id", network=row["network"], slot=row["slot"],
                    media_url=row["media_url"], status="SCHEDULED",
                    planner_url="https://app.metricool.com/planner/fixture-id")
        snapshot["posts"] = [post]
        for field, wrong in (("network", "youtube"), ("media_url", "https://example.invalid/wrong.mp4"),
                             ("status", "ERROR"), ("slot", "2026-11-10T23:00:00-03:00")):
            original = post[field]
            post[field] = wrong
            with self.assertRaises(ValueError):
                reconcile(self.ledger, row["idempotency_key"], "fixture-id", snapshot, self.now)
            post[field] = original
        self.assertEqual(json.loads(self.ledger.read_text())[row["idempotency_key"]]["state"], "UNKNOWN")
        result = reconcile(self.ledger, row["idempotency_key"], "fixture-id", snapshot, self.now)
        self.assertEqual(result["state"], "SCHEDULE_CONFIRMED")
        self.assertEqual(result["metricool_id"], "fixture-id")

    def test_incomplete_daily_count_is_not_ready(self):
        self.batch["items"].pop()
        self.assertEqual(self.plan()["state"], "BLOCKED")

    def test_summary_never_counts_unknown_or_other_days(self):
        plan = self.plan()
        row = claim(plan, plan["items"][0]["id"], self.ledger, self.now)
        ledger = {row["idempotency_key"]: row}
        self.assertEqual(summary(ledger, "2026-11-10")["confirmed_count"], 0)
        row.update(state="SCHEDULE_CONFIRMED", metricool_id="fixture",
                   planner_url="https://app.metricool.com/planner/fixture")
        self.assertEqual(summary(ledger, "2026-11-10")["confirmed_count"], 1)
        self.assertEqual(summary(ledger, "2026-11-11")["confirmed_count"], 0)

    def test_preclaim_or_wrong_host_readback_cannot_confirm(self):
        plan = self.plan()
        row = claim(plan, plan["items"][0]["id"], self.ledger, self.now)
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["checked_at"] = (self.now-timedelta(seconds=1)).isoformat()
        snapshot["posts"] = [dict(id="fixture", network=row["network"], slot=row["slot"],
            media_url=row["media_url"], status="SCHEDULED", planner_url="https://example.invalid/fake")]
        with self.assertRaises(ValueError):
            reconcile(self.ledger, row["idempotency_key"], "fixture", snapshot, self.now)
        snapshot["checked_at"] = self.now.isoformat()
        with self.assertRaises(ValueError):
            reconcile(self.ledger, row["idempotency_key"], "fixture", snapshot, self.now)


if __name__ == "__main__":
    unittest.main()
