#!/usr/bin/env python3
import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location("longform_renderer_v1", HERE / "longform_renderer_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

GATES = [
    "topic_history_gate",
    "voice_ptbr_native_gate",
    "voice_neutral_accent_gate",
    "real_footage_gate",
    "longform_real_footage_gate",
    "semantic_visual_match_gate",
    "causal_animation_gate",
    "no_repeated_animation_pattern_gate",
    "no_prolonged_clip_loop_gate",
    "longform_retention_gate",
    "music_composition_gate",
    "music_theme_match_gate",
    "music_audibility_gate",
    "music_rights_gate",
    "rights_manifest_gate",
    "paulo_voice_approval_gate",
]

def rights(url):
    return {
        "source_url": url,
        "credit": "test credit",
        "usage_basis": "test rights basis",
        "rights_status": "PASS",
    }

def valid_job():
    timeline = []
    families = sorted(MOD.CAUSAL_FAMILIES)
    ai = 0
    for i in range(90):
        cls = ["REAL", "ANIMATION", "REAL", "DATA"][i % 4]
        if cls == "ANIMATION":
            family = families[ai % len(families)]
            seg = {
                "class": cls,
                "duration": 6.0,
                "generator": "internal_causal_v1",
                "animation_family": family,
                "label": f"mechanism {family}",
                "rights_status": "PASS_INTERNAL_GENERATED",
            }
            ai += 1
        else:
            seg = {
                **rights(f"https://example.invalid/asset-{i}.mp4"),
                "class": cls,
                "start": float(i),
                "duration": 6.0,
            }
        timeline.append(seg)
    job = {
        "project": "ORBIT/VSA",
        "channel_id": MOD.CHANNEL_ID,
        "format": "LONGFORM_16_9",
        "publication": False,
        "schedule": False,
        "voice_id": "pt-BR-AntonioNeural",
        "voice_approval_receipt": "PAULO_APPROVED_SAMPLE_TEST",
        "timeline": timeline,
        "music_playlist": [
            {**rights("https://example.invalid/music-a.ogg"), "instrumental": True},
            {**rights("https://example.invalid/music-b.ogg"), "instrumental": True},
            {**rights("https://example.invalid/music-c.ogg"), "instrumental": True},
        ],
    }
    for gate in GATES:
        job[gate] = "PASS"
    return job

class LongformGuardTests(unittest.TestCase):
    def test_valid_job_passes(self):
        result = MOD.validate_job(valid_job())
        self.assertEqual(result["timeline_seconds"], 540.0)
        self.assertEqual(result["real_seconds"], 270.0)
        self.assertEqual(result["real_moments"], 45)
        self.assertEqual(result["music_tracks"], 3)
        self.assertGreaterEqual(result["animation_families"], 3)

    def test_paulo_voice_gate_fails_closed(self):
        job = valid_job()
        job["paulo_voice_approval_gate"] = "PENDING"
        with self.assertRaisesRegex(MOD.GateError, "paulo_voice_approval_gate"):
            MOD.validate_job(job)

    def test_publication_is_forbidden(self):
        job = valid_job()
        job["publication"] = True
        with self.assertRaisesRegex(MOD.GateError, "PUBLISH_OR_SCHEDULE_FORBIDDEN"):
            MOD.validate_job(job)

    def test_duplicate_source_moment_is_rejected(self):
        job = valid_job()
        job["timeline"][4] = dict(job["timeline"][0])
        with self.assertRaisesRegex(MOD.GateError, "REPEATED_SOURCE_MOMENT"):
            MOD.validate_job(job)

    def test_adjacent_same_external_source_is_rejected(self):
        job = valid_job()
        job["timeline"][3]["source_url"] = job["timeline"][2]["source_url"]
        job["timeline"][3]["start"] = 99.0
        with self.assertRaisesRegex(MOD.GateError, "ADJACENT_SOURCE_REPEAT"):
            MOD.validate_job(job)

    def test_unknown_internal_animation_is_rejected(self):
        job = valid_job()
        job["timeline"][1]["animation_family"] = "generic_zoom_arrows"
        with self.assertRaisesRegex(MOD.GateError, "UNKNOWN_ANIMATION_FAMILY"):
            MOD.validate_job(job)

    def test_external_animation_generator_is_rejected(self):
        job = valid_job()
        job["timeline"][1]["generator"] = "external_template"
        with self.assertRaisesRegex(MOD.GateError, "ANIMATION_GENERATOR_FAIL"):
            MOD.validate_job(job)

    def test_repeated_music_track_is_rejected(self):
        job = valid_job()
        job["music_playlist"][1]["source_url"] = job["music_playlist"][0]["source_url"]
        with self.assertRaisesRegex(MOD.GateError, "MUSIC_TRACK_REPEAT"):
            MOD.validate_job(job)

    def test_non_instrumental_music_is_rejected(self):
        job = valid_job()
        job["music_playlist"][0]["instrumental"] = False
        with self.assertRaisesRegex(MOD.GateError, "MUSIC_NOT_INSTRUMENTAL"):
            MOD.validate_job(job)

if __name__ == "__main__":
    unittest.main()
