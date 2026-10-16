#!/usr/bin/env python3
"""Offline tests: Oct16 editorial never claims release or Metricool scheduling."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cena_certa_oct16_discover as oct16
from cena_certa_oct13_compile import compile_editorial

EDITORIAL = ROOT / "ops/cena-certa-oct16/editorial-v1.json"
WORKFLOW = ROOT / ".github/workflows/cena-certa-oct16-source-discovery.yml"

class Oct16EditorialAndSourceResearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(EDITORIAL.read_text(encoding="utf-8"))

    def test_12_unique_popular_2000plus_items_and_network_quota(self):
        self.assertTrue(oct16.validate_editorial(self.doc))
        self.assertEqual(len({i["title"] for i in self.doc["items"]}), 12)
        self.assertTrue(all(i["year"] >= 2000 for i in self.doc["items"]))
        for network in ("tiktok","instagram","facebook","youtube"):
            self.assertEqual(sum(i["network"] == network for i in self.doc["items"]), 3)

    def test_no_master_no_rights_no_schedule_masquerading_as_ready(self):
        for item in self.doc["items"]:
            self.assertIsNone(item["source_url"])
            self.assertIsNone(item["source_segments"])
            self.assertIsNone(item["master_mp4_url"])
            self.assertEqual(item["rights_evidence"]["status"], "NOT_VERIFIED")
            self.assertEqual(item["metricool_status"], "NOT_SCHEDULED")
        compiled, errs = compile_editorial(self.doc, expected_date="2026-10-16")
        self.assertIsNone(compiled)
        self.assertEqual(sum("SOCIAL_REPUBLISH_RIGHTS_MISSING" in e for e in errs), 12)

    def test_anti_repeat_is_not_claimed_without_visual_history(self):
        self.assertTrue(all(item["anti_repeat_180d"]["status"] == "NOT_VERIFIED"
                            for item in self.doc["items"]))
        self.assertFalse(self.doc["metadata_title_repeat_scan"]["verified_visual_scene_uniqueness"])

    def test_movie_year_not_forced_to_2025(self):
        first = self.doc["items"][0]
        self.assertIn("White Chicks 2004 official scene clip", oct16.search_term(first))
        last = self.doc["items"][-1]
        self.assertIn("2018", oct16.search_term(last))

    def test_wrong_sequel_or_movie_rejected_in_discovery(self):
        cases = (
            ("Wonder", "Wonder Woman 2017 official scene"),
            ("Mean Girls", "Mean Girls 2024 official clip"),
            ("The Dark Knight", "The Dark Knight Rises official scene"),
        )
        for title, candidate in cases:
            with self.subTest(candidate=candidate):
                self.assertFalse(oct16.acceptable_candidate(
                    {"id":"ABCDEFGHIJK", "title":candidate}, title))

    def test_publication_gate_rejects_sources_suggested_as_verified(self):
        tampered = copy.deepcopy(self.doc)
        tampered["items"][0]["source_url"] = "https://example.com/clip.mp4"
        with self.assertRaisesRegex(ValueError, "SOURCE_DISCOVERY_MUST_NOT_CONFLATE_MEDIA_RELEASE"):
            oct16.validate_editorial(tampered)

    def test_youtube_titles_are_not_globo(self):
        yt = [i["title"] for i in self.doc["items"] if i["network"]=="youtube"]
        self.assertEqual(len(yt),3)
        self.assertTrue(all(x not in title.lower() for x in ("globoplay","tv globo","globo filmes") for title in yt))

    def test_research_workflow_cannot_publish(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("contents: read", text)
        self.assertIn("python scripts/cena_certa_oct16_discover.py", text)
        self.assertNotIn("gh release", text)
        self.assertNotIn("metricool.com", text)
        self.assertNotIn("push-to-social", text)

if __name__ == "__main__":
    unittest.main()
