import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("vsa_compliance", ROOT / "scripts/vsa/check_workflow_compliance.py")
checker = importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)


class VsaWorkflowTests(unittest.TestCase):
    def test_comment_does_not_satisfy_gate(self):
        text = "# VSA_VISUAL_STORY_ENGINE_V1\n# VSA_VISUAL_RELEASE_RECEIPT_V2\n# ./.github/actions/vsa-release-gate\n"
        with tempfile.TemporaryDirectory() as d:
            file = Path(d, "vsa-fixture.yml"); file.write_text(text)
            # The checker deliberately scopes to repository-relative VSA workflow paths.
            with patch.object(Path, "as_posix", return_value=".github/workflows/vsa-fixture.yml"):
                self.assertTrue(any("MISSING_CANONICAL_MARKER:./.github/actions" in e for e in checker.check(file)))

    def test_release_upload_before_actual_action_is_blocked(self):
        text = "# VSA_VISUAL_STORY_ENGINE_V1\n# VSA_VISUAL_RELEASE_RECEIPT_V2\njobs:\n  render:\n    steps:\n      - run: gh release upload tag master.mp4\n      - uses: ./.github/actions/vsa-release-gate\n"
        with tempfile.TemporaryDirectory() as d:
            file = Path(d, "vsa-fixture.yml"); file.write_text(text)
            with patch.object(Path, "as_posix", return_value=".github/workflows/vsa-fixture.yml"):
                self.assertTrue(any("RELEASE_GATE_MUST_PRECEDE" in e for e in checker.check(file)))
