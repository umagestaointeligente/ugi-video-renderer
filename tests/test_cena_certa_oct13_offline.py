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


class SourceAccessRegressionTests(unittest.TestCase):
    def test_youtube_bot_confirmation_is_non_retryable(self):
        from unittest.mock import patch
        sample = "ERROR: [youtube] AQmiLNr4BVY: Sign in to confirm you’re not a bot."
        item = {
            "id": "SYNTHETIC_FIXTURE_ONLY",
            "source": "https://www.youtube.com/watch?v=AQmiLNr4BVY",
            "source_id": "TEST_FIXTURE_YOUTUBE",
            "segments": [[0, 25]],
        }
        with tempfile.TemporaryDirectory() as d:
            with patch.object(pipeline, "WORK", pathlib.Path(d)), \
                 patch.object(pipeline, "run", side_effect=RuntimeError(sample)) as runner, \
                 patch.object(pipeline.time, "sleep", side_effect=AssertionError("No retry permitted")):
                with self.assertRaisesRegex(RuntimeError, "SOURCE_AUTH_REQUIRED:YTDLP_NON_RETRYABLE"):
                    pipeline.download_source(item, {})
                self.assertEqual(runner.call_count, 1)

    def test_direct_cdn_auth_denied_is_non_retryable(self):
        from unittest.mock import patch
        item = {
            "id": "SYNTHETIC_FIXTURE_ONLY",
            "source": "https://media.example.test/licensed-scene.mp4",
            "source_id": "TEST_FIXTURE_DIRECT",
            "segments": [[0, 25]],
        }
        with tempfile.TemporaryDirectory() as d:
            with patch.object(pipeline, "WORK", pathlib.Path(d)), \
                 patch.object(pipeline, "run", side_effect=RuntimeError("HTTP Error 403")) as runner, \
                 patch.object(pipeline.time, "sleep", side_effect=AssertionError("No retry permitted")):
                with self.assertRaisesRegex(RuntimeError, "SOURCE_AUTH_REQUIRED:DIRECT_MEDIA_NON_RETRYABLE"):
                    pipeline.download_source(item, {})
                self.assertEqual(runner.call_count, 1)

    def test_authorized_direct_media_keeps_ffmpeg_path_without_ytdlp(self):
        from unittest.mock import patch
        item = {
            "id": "SYNTHETIC_FIXTURE_ONLY",
            "source": "https://licensed.example.test/media/cut.mp4?signature=fixture",
            "source_id": "TEST_FIXTURE_DIRECT_PASS",
            "segments": [[0, 25]],
        }
        def fake_run(command, **kwargs):
            self.assertEqual(command[0], "ffmpeg")
            pathlib.Path(command[-1]).write_bytes(b"x" * 250001)
        fake_probe = {"streams": [{"codec_type": "video"}, {"codec_type": "audio"}]}
        with tempfile.TemporaryDirectory() as d:
            with patch.object(pipeline, "WORK", pathlib.Path(d)), \
                 patch.object(pipeline, "run", side_effect=fake_run) as calls, \
                 patch.object(pipeline, "probe", return_value=fake_probe):
                cache = {}
                output = pipeline.download_source(item, cache)
                self.assertTrue(output.exists())
                self.assertEqual(output.suffix, ".mkv")
                self.assertEqual(calls.call_count, 1)
                self.assertEqual(cache[item["source_id"]], output)

    def test_network_timeouts_remain_retryable_but_not_licensed(self):
        self.assertIsNone(pipeline.permanent_source_failure(RuntimeError("timed out")))
        self.assertEqual(pipeline.permanent_source_failure(RuntimeError("HTTP Error 404")),
                         "SOURCE_NOT_AVAILABLE")
        self.assertEqual(pipeline.permanent_source_failure(RuntimeError("private video")),
                         "SOURCE_AUTH_REQUIRED")

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
