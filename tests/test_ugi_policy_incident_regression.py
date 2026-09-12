from __future__ import annotations

import datetime as dt
import unittest

from scripts import ugi_delivery_verifier
from scripts import ugi_growth_runtime


class GrowthPolicyIncidentRegressionTest(unittest.TestCase):
    def test_schema_13_and_story_are_accepted(self) -> None:
        runtime = ugi_growth_runtime.load_runtime_policy()
        self.assertEqual(runtime["POLICY_SCHEMA_VERSION"], "1.3")
        self.assertIn("story", runtime["INSTAGRAM"]["formats"])
        self.assertEqual(len(runtime["POLICY_SHA256"]), 64)
        self.assertEqual(len(runtime["DISTRIBUTION_STATE_SHA256"]), 64)

    def test_operational_state_is_canonical_for_active_platforms(self) -> None:
        runtime = ugi_growth_runtime.load_runtime_policy()
        state = runtime["DISTRIBUTION_STATE"]
        self.assertEqual(runtime["EFFECTIVE_ACTIVE_PLATFORMS"], state["distribution_priority"])
        self.assertEqual(runtime["EFFECTIVE_PAUSED_PLATFORMS"], [])
        self.assertEqual(runtime["PRIMARY_PUBLISHER"], "metricool")
        self.assertEqual(state["buffer"]["publisher"], "buffer_legacy")
        self.assertEqual(
            state["metricool"]["networks"]["youtube"],
            state["channels"]["youtube"]["channel_id"],
        )

    def test_terminal_delivery_classification_stays_evidence_based(self) -> None:
        now = dt.datetime.now(dt.timezone.utc)
        due = now - dt.timedelta(hours=1)
        self.assertEqual(ugi_delivery_verifier.classify({"status": "published"}, due, now), "DELIVERED")
        self.assertEqual(ugi_delivery_verifier.classify({"status": "failed"}, due, now), "FAILED")


if __name__ == "__main__":
    unittest.main()
