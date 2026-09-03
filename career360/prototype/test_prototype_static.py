#!/usr/bin/env python3

from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.scripts: list[str] = []
        self._in_script = False
        self._script_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if attrs_dict.get("id"):
            self.ids.add(attrs_dict["id"])
        if tag.lower() == "script" and "src" not in attrs_dict:
            self._in_script = True
            self._script_parts = []

    def handle_data(self, data):
        if self._in_script:
            self._script_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._in_script:
            self.scripts.append("".join(self._script_parts))
            self._in_script = False
            self._script_parts = []


class PrototypeStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = IdCollector()
        cls.parser.feed(HTML)
        cls.js = "\n".join(cls.parser.scripts)

    def test_critical_onboarding_ids_exist(self):
        required = {
            "onboarding", "step1", "step2", "confirmStep", "step3", "step4",
            "cv", "fileResult", "resumeConfirmList", "confirmModeNotice",
            "confirmDraftBtn", "continueNoDraftBtn", "syntheticBtn",
            "employed", "employer", "targetRole", "app", "bottom"
        }
        self.assertEqual(required - self.parser.ids, set())

    def test_resume_confirmation_functions_exist(self):
        for fn in (
            "openResumeConfirmation", "renderResumeDraft", "loadSyntheticDraft",
            "confirmResumeDraft", "continueWithoutDraft"
        ):
            self.assertRegex(self.js, rf"function\s+{fn}\s*\(")

    def test_synthetic_mode_is_explicit(self):
        self.assertIn("MODO QA", HTML)
        self.assertIn("100% sintéticos", HTML)
        self.assertIn("resumeDraftSynthetic", self.js)

    def test_no_remote_upload_or_api_call_in_prototype(self):
        # O protótipo local não pode ganhar fetch/XHR/WebSocket silenciosamente.
        forbidden_patterns = [
            r"\bfetch\s*\(",
            r"XMLHttpRequest",
            r"new\s+WebSocket\s*\(",
            r"navigator\.sendBeacon\s*\(",
        ]
        for pattern in forbidden_patterns:
            self.assertIsNone(re.search(pattern, self.js), pattern)

    def test_file_input_restricted_to_pdf_docx(self):
        match = re.search(r'<input[^>]+id="cv"[^>]+accept="([^"]+)"', HTML)
        self.assertIsNotNone(match)
        accept = match.group(1).lower()
        self.assertIn(".pdf", accept)
        self.assertIn(".docx", accept)
        self.assertNotIn(".doc,", accept)

    def test_parser_truth_copy_present(self):
        self.assertIn("parser real já existe e passou em CI", HTML)
        self.assertIn("arquivo ainda não é enviado", HTML)

    def test_no_claim_that_synthetic_data_is_customer_data(self):
        self.assertIn("Eles nunca serão gravados como dados do cliente", HTML)


if __name__ == "__main__":
    unittest.main()
