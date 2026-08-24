import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ugi_autonomous_watchdog.py"
SPEC = importlib.util.spec_from_file_location("ugi_autonomous_watchdog", MODULE_PATH)
WATCHDOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WATCHDOG)


class UgiAutonomousWatchdogTest(unittest.TestCase):
    def fixture(self, root):
        policy_path = root / "config" / "ugi" / "growth-policy.json"
        policy_path.parent.mkdir(parents=True)
        policy = {
            "integration_roles": {
                "publisher": {"primary": "buffer", "metricool_allowed": False},
                "analytics": {"primary": "metricool", "publishing_allowed": False},
            },
            "publication_recovery": {"publisher": "buffer", "metricool_retry_forbidden": True, "max_attempts_total": 4},
        }
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        growth = root / "control-plane" / "receipts" / "ugi-growth-engine" / "latest.json"
        growth.parent.mkdir(parents=True)
        growth.write_text(json.dumps({"SMOKE_TEST_PASS": True, "policy_sha256": hashlib.sha256(policy_path.read_bytes()).hexdigest()}), encoding="utf-8")
        return policy_path

    def test_healthy_policy_preserves_buffer_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            status = WATCHDOG.build_status(root)
            self.assertEqual(status["status"], "HEALTHY")
            self.assertEqual(status["publication_provider"], "BUFFER")
            self.assertFalse(status["metricool_publication_allowed"])

    def test_metricool_publication_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.fixture(Path(directory))
            policy = json.loads(path.read_text())
            policy["integration_roles"]["publisher"]["metricool_allowed"] = True
            path.write_text(json.dumps(policy))
            with self.assertRaises(SystemExit):
                WATCHDOG.build_status(Path(directory))

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


if __name__ == "__main__":
    unittest.main()
