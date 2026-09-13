import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import ugi_autonomous_watchdog as WATCHDOG


class UgiAutonomousWatchdogTest(unittest.TestCase):
    def fixture(self, root):
        policy_path = root / "config" / "ugi" / "growth-policy.json"
        policy_path.parent.mkdir(parents=True)
        policy = {
            "integration_roles": {
                "publisher": {"primary": "metricool", "metricool_allowed": True},
                "analytics": {"primary": "metricool", "publishing_allowed": True},
            },
            "distribution": {
                "state_ref": "config/ugi/distribution-state.json",
                "active_distribution_channel_count": 4,
                "active_platforms": ["youtube", "linkedin", "instagram", "tiktok"],
            },
            "publication_evidence": {"publisher_source": "metricool"},
            "publication_recovery": {
                "publisher": "buffer",
                "metricool_retry_forbidden": True,
                "max_attempts_total": 4,
                "active_platforms_only": True,
                "paused_platform_retry_forbidden": True,
                "pre_retry_checks": [
                    "verify_not_already_published",
                    "verify_no_duplicate_post_exists",
                    "verify_asset_unchanged",
                    "verify_caption_unchanged",
                    "verify_platform_is_active_distribution_channel",
                ],
                "success_stop_condition": "published_and_verified_readback",
            },
        }
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        state_path = root / "config" / "ugi" / "distribution-state.json"
        state = {
            "project": "UGI",
            "publisher_routing": {
                "primary": "metricool",
                "fallback": "certified_native_direct_route_only",
                "fallback_condition": "PROVEN_CAPABILITY_GAP_OR_HARD_ERROR_ONLY",
                "ambiguous_result_policy": "READBACK_BEFORE_ANY_RETRY_OR_FALLBACK",
                "duplicate_mutation_policy": "FORBIDDEN",
                "fail_closed": True,
            },
            "metricool": {
                "status": "ACTIVE_PRIMARY",
                "networks": {"youtube": "yt", "linkedin": "li", "instagram": "ig", "tiktok": "tt"},
            },
            "buffer": {
                "publisher": "buffer_legacy",
                "active_platforms": ["instagram"],
                "paused_platforms": ["linkedin", "tiktok", "youtube"],
                "active_channel_count": 1,
            },
            "channels": {"youtube": {"metricool_status": "ACTIVE_LONGFORM_WEEKLY_HARD_GATED"}},
            "distribution_priority": ["youtube", "linkedin", "instagram", "tiktok"],
        }
        state_path.write_text(json.dumps(state), encoding="utf-8")
        growth = root / "control-plane" / "receipts" / "ugi-growth-engine" / "latest.json"
        growth.parent.mkdir(parents=True)
        growth.write_text(json.dumps({"SMOKE_TEST_PASS": True, "policy_sha256": hashlib.sha256(policy_path.read_bytes()).hexdigest()}), encoding="utf-8")
        return policy_path

    def test_healthy_policy_preserves_metricool_primary_and_legacy_buffer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            status = WATCHDOG.build_status(root)
            self.assertEqual(status["status"], "HEALTHY")
            self.assertEqual(status["publication_provider"], "METRICOOL")
            self.assertTrue(status["metricool_publication_allowed"])
            self.assertEqual(status["fallback_provider"], "certified_native_direct_route_only")

    def test_buffer_primary_policy_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.fixture(Path(directory))
            policy = json.loads(path.read_text())
            policy["integration_roles"]["publisher"]["primary"] = "buffer"
            path.write_text(json.dumps(policy))
            with self.assertRaises(SystemExit):
                WATCHDOG.build_status(Path(directory))

    def test_policy_state_provider_drift_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            state_path = root / "config" / "ugi" / "distribution-state.json"
            state = json.loads(state_path.read_text())
            state["publisher_routing"]["primary"] = "buffer"
            state_path.write_text(json.dumps(state))
            with self.assertRaises(SystemExit):
                WATCHDOG.build_status(root)

    def test_existing_auth_failures_become_actionable_incidents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / "control-plane" / "receipts" / "ugi-buffer" / "today.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"ok": False, "error": "AUTH_MISSING"}))
            status = WATCHDOG.build_status(root)
            self.assertEqual(status["status"], "DEGRADED")
            self.assertEqual(status["incidents"][0]["class"], "BUFFER_AUTH_OR_READBACK_UNAVAILABLE")

    def test_newer_verified_auth_supersedes_historical_generation_403(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            buffer_path = root / "control-plane" / "receipts" / "ugi-buffer" / "today.json"
            generation_path = root / "control-plane" / "receipts" / "ugi-today" / "generation.json"
            buffer_path.parent.mkdir(parents=True)
            generation_path.parent.mkdir(parents=True)
            buffer_path.write_text(json.dumps({"ok": True, "drafts_http": 200, "channels_http": 200, "timestamp": "2026-08-24T05:22:00+00:00"}))
            generation_path.write_text(json.dumps({"generated_at": "2026-08-23T23:36:00+00:00", "results": [{"platform": "instagram", "error": "HTTP Error 403: Forbidden"}]}))
            status = WATCHDOG.build_status(root)
            self.assertEqual(status["status"], "HEALTHY")
            self.assertTrue(status["current_readonly_auth_verified"])


if __name__ == "__main__":
    unittest.main()
