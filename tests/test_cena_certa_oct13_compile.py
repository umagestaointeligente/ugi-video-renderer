#!/usr/bin/env python3
"""Offline, synthetic regression tests. Test fixtures are NOT real media rights."""
import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts/cena_certa_oct13_compile.py"
EDITORIAL = ROOT / "ops/cena-certa-oct13/editorial-v2-9-proposed.json"
spec = importlib.util.spec_from_file_location("cena_certa_oct13_compile", MODULE)
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)


class TestUserEditorialSourceOfTruth(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(EDITORIAL.read_text(encoding="utf-8"))

    def fake_complete(self):
        # Synthetic URL/rights evidence in tests ONLY, never permitted in production file.
        doc = copy.deepcopy(self.document)
        for i, item in enumerate(doc["items"]):
            duration = (item["target_duration_sec"]["min"] + item["target_duration_sec"]["max"]) / 2
            item["source_url"] = "https://media.example.com/fixture-" + str(i) + ".mp4"
            item["source_id"] = "TEST_FIXTURE_" + str(i)
            item["source_segments"] = [[0, duration]]
            item["rights_evidence"] = {
                "status": "VERIFIED", "scope": "SOCIAL_REPUBLISH",
                "proof_url": "https://example.com/synthetic-license"
            }
            item["media_type"] = "LIVE_ACTION"
        return doc

    def test_real_canonical_editorial_fails_before_media_render(self):
        compiled, errors = compiler.compile_editorial(self.document)
        self.assertIsNone(compiled)
        self.assertGreaterEqual(len(errors), 12)
        self.assertTrue(any("HTTPS_SOURCE_MISSING" in e for e in errors))
        self.assertTrue(any("SOCIAL_REPUBLISH_RIGHTS_MISSING" in e for e in errors))

    def test_exact_twelve_2025_titles_and_slots_compile_with_synthetic_fixtures(self):
        compiled, errors = compiler.compile_editorial(self.fake_complete())
        self.assertFalse(errors, errors)
        self.assertEqual(len(compiled["items"]), 12)
        self.assertEqual(compiled["items"][0]["title"], "Corra que a Polícia Vem Aí! (2025)")
        self.assertEqual(compiled["items"][-1]["title"], "Uma Batalha Após a Outra (2025)")
        self.assertEqual({n: sum(x["network"] == n for x in compiled["items"])
                          for n in compiler.NETWORKS}, compiler.NETWORKS)

    def test_proof_of_rights_must_be_real_field_not_missing(self):
        doc = self.fake_complete()
        doc["items"][0]["rights_evidence"]["proof_url"] = None
        self.assertTrue(any("SOCIAL_REPUBLISH_RIGHTS_MISSING" in e
                            for e in compiler.compile_editorial(doc)[1]))

    def test_reject_duplicate_slots(self):
        doc = self.fake_complete()
        doc["items"][1]["slot"] = doc["items"][0]["slot"]
        self.assertTrue(any("DUPLICATE_NETWORK_SLOT" in e
                            for e in compiler.compile_editorial(doc)[1]))

    def test_reject_unsafe_url_and_missing_source_time(self):
        doc = self.fake_complete()
        doc["items"][0]["source_url"] = "http://127.0.0.1:8080/file.mp4"
        doc["items"][1]["source_segments"] = None
        failures = compiler.compile_editorial(doc)[1]
        self.assertTrue(any("HTTPS_SOURCE_MISSING" in e for e in failures))
        self.assertTrue(any("SOURCE_SEGMENTS_MISSING" in e for e in failures))

    def test_reject_intra_pack_duplicate_scene(self):
        doc = self.fake_complete()
        doc["items"][1]["source_id"] = doc["items"][0]["source_id"]
        doc["items"][1]["source_segments"] = [[3, 29]]
        self.assertTrue(any("INTRA_PACK_SOURCE_OVERLAP" in e
                            for e in compiler.compile_editorial(doc)[1]))

    def test_readiness_receipt_never_labels_unverified_sources_ready(self):
        # Exercise the user-facing intake receipt in a temporary directory;
        # test must never write to the production out/ tree.
        import sys
        import tempfile
        from unittest.mock import patch
        sys.path.insert(0, str(ROOT / "scripts"))
        import cena_certa_oct13_readiness as readiness
        with tempfile.TemporaryDirectory() as d:
            out = pathlib.Path(d)
            with patch.object(readiness, "OUT", out), \
                 patch.object(readiness, "OUTPUT", out / "source-readiness.json"), \
                 patch.object(readiness, "SUMMARY", out / "source-readiness.md"):
                result = readiness.generate()
                self.assertEqual(result["editorial_items"], 12)
                self.assertEqual(result["source_ready_count"], 0)
                self.assertEqual(result["existing_masters_count"], 0)
                self.assertFalse(result["release_allowed"])
                self.assertFalse(result["metricool_scheduling_allowed"])
                self.assertGreaterEqual(result["blocking_error_count"], 12)
                self.assertTrue((out / "source-readiness.json").exists())

    def test_no_globoplay_on_youtube(self):
        doc = self.fake_complete()
        yt = next(x for x in doc["items"] if x["network"] == "youtube")
        yt["source_url"] = "https://globoplay.globo.com/v/5584488/"
        self.assertTrue(any("YOUTUBE_GLOBO_SOURCE_FORBIDDEN" in e
                            for e in compiler.compile_editorial(doc)[1]))


if __name__ == "__main__":
    unittest.main()
