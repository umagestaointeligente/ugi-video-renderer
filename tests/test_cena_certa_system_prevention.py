import copy
from datetime import datetime, timezone
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cena_certa_media_safety import overlay_textfile
from cena_certa_render_evidence_guard import validate_pack, validate_fingerprint_files
from check_cena_certa_release_barriers import check
from cena_certa_source_probe import validate_metadata
import test_cena_certa_render_evidence as fixtures


class SystemPreventionTests(unittest.TestCase):
    def test_probe_requires_exact_identity_and_full_requested_window(self):
        item = {"source_id": "123", "source_start": 4, "source_end": 38}
        self.assertIsNone(validate_metadata(item, {"id": "123", "duration": 69}))
        self.assertEqual(validate_metadata(item, {"id": "456", "duration": 69}), "SOURCE_IDENTITY_MISMATCH")
        self.assertEqual(validate_metadata(item, {"id": "123", "duration": 30}), "SOURCE_WINDOW_OUT_OF_RANGE")

    def test_execution_receipt_and_network_subdirectory(self):
        fixture = fixtures.EvidenceTests(); fixture.setUp()
        item = dict(fixture.item, network="instagram")
        context = dict(run_id="100", run_attempt="2", commit="a" * 40)
        receipt = dict(fixture.receipt, **context)
        with tempfile.TemporaryDirectory() as d:
            Path(d, "instagram").mkdir()
            Path(d, "instagram", item["id"] + ".mp4").write_bytes(b"test master")
            self.assertEqual(validate_pack({"items": [item]}, {item["id"]: receipt}, d, fixture.now, context)["status"], "PASS")
            for key in context:
                bad = dict(receipt, **{key: "wrong"})
                result = validate_pack({"items": [item]}, {item["id"]: bad}, d, fixture.now, context)
                self.assertEqual(result["status"], "BLOCK")
                self.assertIn("RECEIPT_EXECUTION_MISMATCH", result["items"][0]["errors"])

    def test_invalid_inputs_replace_stale_approval(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d, "preflight.json"); output.write_text('{"status":"PASS"}')
            summary = Path(d, "summary.json"); summary.write_text("broken json")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/cena_certa_render_evidence_guard.py"), str(summary), str(Path(d, "missing.json")), str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(output.read_text())["status"], "BLOCK")

    def test_literal_overlay_survives_real_ffmpeg(self):
        with tempfile.TemporaryDirectory() as d:
            text = "Tio 'perfeito': 100% [sim]; não, por quê? \\ %{n}"
            file = overlay_textfile(text, d)
            self.assertEqual(Path(file).read_text(), text)
            result = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=s=160x90:d=0.1", "-vf", f"drawtext=textfile='{file}':expansion=none:fontsize=12", "-frames:v", "1", "-f", "null", "-"], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_all_benchmark_renderers_reject_incomplete_history_and_overruns(self):
        for day in ("05", "06", "07", "08", "09", "11"):
            module = importlib.import_module("cena_certa_oct" + day + "_pack")
            with self.subTest(day=day), tempfile.TemporaryDirectory() as d:
                history = Path(d, "history.json")
                history.write_text(json.dumps({"items": [{"status": "PUBLISHED", "media": "fixture.mp4"}]}))
                with patch.object(module, "HISTORY", history), patch.object(module, "OUT", Path(d)), patch.object(module, "dhashes_center", return_value=[]):
                    with self.assertRaisesRegex(RuntimeError, "HISTORY_FINGERPRINT_COVERAGE_FAIL"):
                        module.history_index()
                with self.assertRaisesRegex(RuntimeError, "END_FAIL"):
                    module.normalized_segments({"id": "X", "source_start": 0, "source_end": 50}, 30)
                with self.assertRaisesRegex(RuntimeError, "END_FAIL"):
                    module.normalized_segments({"id": "X", "segments": [[0, 50]]}, 30)

    def test_detection_failures_raise_instead_of_passing(self):
        for day in ("05", "06", "07", "08", "09", "11"):
            module = importlib.import_module("cena_certa_oct" + day + "_pack")
            with self.subTest(day=day):
                result = subprocess.CompletedProcess(["ffmpeg"], 1, b"", b"decoder failed")
                with patch.object(module.subprocess, "run", return_value=result):
                    with self.assertRaises(RuntimeError):
                        module.run(["ffmpeg", "bad-source"])

    def test_repeat_receipt_preserves_frames_and_master_binding(self):
        module = importlib.import_module("cena_certa_oct11_pack")
        with tempfile.TemporaryDirectory() as d:
            media = Path(d, "X.mp4"); media.write_bytes(b"final master")
            with patch.object(module, "OUT", Path(d)), patch.object(module, "dhashes_center", return_value=[1] * 20):
                with self.assertRaisesRegex(RuntimeError, "SCENE_SEQUENCE_GATE_FAIL"):
                    module.visual_gate([({"id": "X"}, media)], [({"id": "H"}, [1] * 20)])
            receipt = json.loads(Path(d, "candidate-fingerprints.json").read_text())
            self.assertEqual(receipt["items"][0]["frames"], [1] * 20)
            self.assertTrue(receipt["items"][0]["master_sha256"])
            self.assertTrue(receipt["violations"])

    def test_comments_skips_and_wrong_order_do_not_authorize_releases(self):
        base = """jobs:
  release:
    steps:
      - run: |
          set -euo pipefail
          python scripts/cena_certa_render_evidence_guard.py summary receipts result
      - run: gh release upload tag video.mp4
"""
        self.assertEqual(check(base), [])
        self.assertTrue(check(base.replace("python scripts/", "# python scripts/")))
        self.assertTrue(check(base.replace("      - run: |", "      - continue-on-error: true\n        run: |")))
        self.assertTrue(check(base.replace("      - run: |", "      - if: always()\n        run: |")))
        self.assertTrue(check(base.replace("          set -euo pipefail\n", "")))
        self.assertTrue(check(base.replace("video.mp4", "video.mp4 --clobber")))
        self.assertTrue(check(base.replace("          set -euo pipefail", "          set -euo pipefail\n          if false; then")))

    def test_fingerprint_file_changes_and_wrong_master_block(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            history = root / "history-fingerprints.json"
            candidate = root / "candidate-fingerprints.json"
            history.write_text(json.dumps({"eligible_count": 1, "coverage": 1.0, "items": [{"id": "H", "frames": [1]}]}))
            candidate.write_text(json.dumps({"items": [{"id": "X", "master_sha256": "a" * 64, "frames": [1]}], "violations": []}))
            summary = {"items": [{"id": "X", "sha256": "a" * 64}],
                "history_fingerprint_receipt_sha256": hashlib.sha256(history.read_bytes()).hexdigest(),
                "candidate_fingerprint_receipt_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest()}
            self.assertEqual(validate_fingerprint_files(summary, root), [])
            changed = copy.deepcopy(summary); changed["items"][0]["sha256"] = "b" * 64
            self.assertTrue(validate_fingerprint_files(changed, root))
            history.write_text('{}')
            self.assertTrue(validate_fingerprint_files(summary, root))


if __name__ == "__main__":
    unittest.main()
