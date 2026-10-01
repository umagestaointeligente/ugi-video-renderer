import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from cena_certa_render_evidence_guard import CONTRACT, LAYERS, POSITIONS, validate_pack, validate_receipt

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
        self.sha = hashlib.sha256(b"test master").hexdigest()
        self.item = dict(id="CC-TEST", source_id="123", source="https://example.invalid/123",
                         sha256=self.sha, technical_status="PASS", kind="humor",
                         source_duration_sec=100, duration_sec=58)
        self.receipt = dict(contract=CONTRACT, content_id="CC-TEST", master_sha256=self.sha,
            checked_at=self.now.isoformat(),
            source=dict(extracted_id="123", url=self.item["source"], identity_pass=True, metadata_receipt="fixture-metadata"),
            rights=dict(status="PASS", evidence="fixture-rights"),
            transformation=dict(status="PASS", evidence="fixture-edit"),
            cta=dict(status="PASS", evidence="fixture-final-frame"),
            visual=dict(status="PASS", evidence="fixture-review", exact_subject_match=True,
                        source_cta_removed=True, frames={p:"fixture-frame" for p in POSITIONS}),
            anti_repeat=dict(status="PASS", history_complete=True, history_receipt="fixture-history",
                history_start=(self.now-timedelta(days=60)).isoformat(), history_end=self.now.isoformat(),
                comparison_layers=list(LAYERS), fingerprint_receipt="fixture-fingerprints", scene_overlap_detected=False))

    def test_complete_bound_receipt(self):
        self.assertEqual(validate_receipt(self.item, self.receipt, self.now), [])

    def test_sep30_claims_cannot_substitute_receipts(self):
        self.assertIn("RENDER_RECEIPT_MISSING", validate_receipt(self.item, None, self.now))

    def test_each_required_gate_fails_closed(self):
        for gate in ("rights", "visual", "transformation", "cta", "anti_repeat", "source"):
            with self.subTest(gate=gate):
                receipt=copy.deepcopy(self.receipt); receipt.pop(gate)
                self.assertTrue(validate_receipt(self.item, receipt, self.now))

    def test_stale_history_and_reencoded_same_scene_block(self):
        for change in (dict(history_complete=False), dict(scene_overlap_detected=True),
                       dict(comparison_layers=["master_sha256"]),
                       dict(history_end=(self.now-timedelta(days=2)).isoformat())):
            receipt=copy.deepcopy(self.receipt); receipt["anti_repeat"].update(change)
            self.assertTrue(validate_receipt(self.item, receipt, self.now))

    def test_master_and_source_mismatch_block(self):
        receipt=copy.deepcopy(self.receipt); receipt["master_sha256"]="f"*64
        self.assertIn("EVIDENCE_MASTER_MISMATCH", validate_receipt(self.item, receipt, self.now))
        receipt=copy.deepcopy(self.receipt); receipt["source"]["extracted_id"]="456"
        self.assertIn("SOURCE_ID_NOT_VERIFIED", validate_receipt(self.item, receipt, self.now))

    def test_cta_and_frame_missing_block(self):
        receipt=copy.deepcopy(self.receipt); receipt["cta"]["status"]="NOT_VERIFIED"
        receipt["visual"]["frames"].pop("last_frame")
        errors=validate_receipt(self.item, receipt, self.now)
        self.assertIn("CTA_EVIDENCE_NOT_PROVEN", errors)
        self.assertIn("REPRESENTATIVE_FRAMES_INCOMPLETE", errors)

    def test_near_full_source_requires_bound_exception(self):
        item=dict(self.item, duration_sec=95)
        self.assertIn("NEAR_FULL_SOURCE_EXCEPTION_MISSING", validate_receipt(item, self.receipt, self.now))

    def test_changed_final_bytes_block_entire_batch(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root,"CC-TEST.mp4").write_bytes(b"test master")
            sibling=dict(self.item, id="CC-SIBLING")
            receipt=copy.deepcopy(self.receipt); receipt["content_id"]="CC-SIBLING"
            Path(root,"CC-SIBLING.mp4").write_bytes(b"different master")
            result=validate_pack({"items":[self.item,sibling]}, {"CC-TEST":self.receipt,"CC-SIBLING":receipt}, root, self.now)
            self.assertEqual(result["status"], "BLOCK")
            self.assertTrue(all(row["status"]=="BLOCK" for row in result["items"]))
            self.assertEqual(result["publication_status"], "NOT_VERIFIED")

    def test_validator_does_not_require_legacy_mask(self):
        path=Path(__file__).resolve().parents[1]/"scripts"/"cena_certa_social_publish_preflight.py"
        if not path.exists():
            path=Path(__file__).with_name("cena_certa_social_publish_preflight.py")
        if not path.exists():
            self.skipTest("renderer repository has no social validator")
        spec=importlib.util.spec_from_file_location("preflight",path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        item={"content_id":"X","format":"YOUTUBE_SHORT","topic":"test","media_kind":"VIDEO",
            "media_urls":["fixture"],"subject_asset_present":True,"exact_subject_visual_match":"PASS",
            "template_only":False,"generic_background_main_visual":False,"final_media_inspected_after_render":True,
            "source_provenance":"fixture","rights_status":"PASS","visual_qa_status":"PASS",
            "final_render_media_id_or_hash":self.sha,"cross_modal_alignment_pass":"PASS",
            "representative_frame_receipt":{},"no_legacy_mask_pass":True,"canonical_mask_present":False}
        errors=module.validate_item(item)
        self.assertNotIn("SHORT_CANONICAL_MASK_MISSING",errors)
        self.assertNotIn("SHORT_LEGACY_MASK_FORBIDDEN",errors)
        item["canonical_mask_present"]=True
        self.assertIn("SHORT_LEGACY_MASK_FORBIDDEN",module.validate_item(item))

if __name__ == "__main__":
    unittest.main()
