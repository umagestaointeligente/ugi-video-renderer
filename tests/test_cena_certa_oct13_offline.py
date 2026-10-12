#!/usr/bin/env python3
"""Low-cost regression checks for the Oct13 Cena Certa pipeline (no publishing)."""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/cena_certa_oct13_pack.py"
EDITORIAL = ROOT / "ops/cena-certa-oct13/editorial-v2-9-proposed.json"

spec = importlib.util.spec_from_file_location("cena_certa_oct13_pack", SCRIPT)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)
pipeline.EDITORIAL = EDITORIAL


class EditorialPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.approved = json.loads(EDITORIAL.read_text(encoding="utf-8"))["items"]

    def test_exact_approved_slots_and_titles_are_accepted(self):
        records = [{"network": p["network"], "slot": p["slot"], "title": p["title"]}
                   for p in self.approved]
        self.assertTrue(pipeline.editorial_alignment_gate(records))

    def test_changed_legacy_title_is_rejected(self):
        records = [{"network": p["network"], "slot": p["slot"], "title": p["title"]}
                   for p in self.approved]
        records[0]["title"] = "UNAPPROVED REPLACEMENT"
        with self.assertRaisesRegex(RuntimeError, "EDITORIAL_V29_DRIFT_FAIL"):
            pipeline.editorial_alignment_gate(records)

    def test_duplicate_slot_is_rejected(self):
        records = [{"network": p["network"], "slot": p["slot"], "title": p["title"]}
                   for p in self.approved]
        records[1]["slot"] = records[0]["slot"]
        with self.assertRaisesRegex(RuntimeError, "EDITORIAL_DUPLICATE_SLOT"):
            pipeline.editorial_alignment_gate(records)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg unavailable")
class VP9OpusRemuxTests(unittest.TestCase):
    def test_vp9_opus_webm_remux_into_matroska(self):
        with tempfile.TemporaryDirectory() as root:
            source = pathlib.Path(root) / "fixture.webm"
            target = pathlib.Path(root) / "fixture.mkv"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", "testsrc2=size=160x288:rate=15",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
                "-t", "1.2", "-c:v", "libvpx-vp9", "-b:v", "100k",
                "-c:a", "libopus", "-b:a", "32k", "-shortest", "-y", str(source)
            ], check=True, capture_output=True)
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-i", str(source), "-c", "copy", "-y", str(target)
            ], check=True, capture_output=True)
            data = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "stream=codec_name,codec_type",
                "-of", "json", str(target)
            ], check=True, capture_output=True, text=True)
            codecs = {(s["codec_type"], s["codec_name"]) for s in json.loads(data.stdout)["streams"]}
            self.assertIn(("video", "vp9"), codecs)
            self.assertIn(("audio", "opus"), codecs)


if __name__ == "__main__":
    unittest.main()
