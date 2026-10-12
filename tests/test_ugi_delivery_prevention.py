import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock
from scripts import ugi_delivery_verifier as verifier


class DeliveryPreventionTests(unittest.TestCase):
    def test_current_legacy_observer_preserves_metricool_primary(self):
        self.assertEqual(verifier.load_active_platforms(), {"instagram"})

    def test_wrong_legacy_route_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "state.json")
            path.write_text(json.dumps({"buffer": {"publisher": "buffer_legacy", "status": "ACTIVE", "active_platforms": ["instagram"]}}))
            with patch.object(verifier, "DISTRIBUTION_STATE", path), self.assertRaises(SystemExit):
                verifier.load_active_platforms()

    def test_http_errors_are_not_publication_proof(self):
        for status in (200, 403, 404, 429, 500):
            with self.subTest(status=status), patch.object(verifier.requests, "get", return_value=Mock(status_code=status, url="https://example.invalid/post")):
                proof = verifier.external_proof("https://example.invalid/post")
                self.assertEqual(proof["ok"], status == 200)
                self.assertEqual(proof["scope"], "HTTP_REACHABILITY_ONLY")

    def test_ambiguous_time_is_not_assigned_runner_timezone(self):
        self.assertIsNone(verifier.parse_time("2026-10-10T12:00:00"))
        self.assertIsNotNone(verifier.parse_time("2026-10-10T12:00:00-03:00"))
