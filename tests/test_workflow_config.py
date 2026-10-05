import sys
from pathlib import Path
import unittest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_workflow_config import validate_text

VALID = '''name: Fixture
on:
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: |
          python - <<'PY'
          print('ok')
          PY
'''


class WorkflowConfigTests(unittest.TestCase):
    def test_valid_heredoc(self):
        self.assertEqual(validate_text(VALID), {'yaml': 1, 'bash': 1, 'python': 1})

    def test_unindented_python_is_rejected(self):
        with self.assertRaises(yaml.YAMLError):
            validate_text(VALID.replace("          print('ok')", "print('ok')"))

    def test_duplicate_jobs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate YAML key'):
            validate_text(VALID + 'jobs: {}\n')

    def test_invalid_python_is_rejected(self):
        with self.assertRaises(SyntaxError):
            validate_text(VALID.replace("print('ok')", 'if True'))

    def test_invalid_shell_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_text(VALID.replace("python - <<'PY'", "if then\n          python - <<'PY'"))

    def test_unknown_dependency_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'invalid needs'):
            validate_text(VALID.replace('runs-on:', 'needs: absent\n    runs-on:'))

    def test_empty_jobs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing triggers or jobs'):
            validate_text('on: push\njobs: {}\n')

    def test_commands_are_never_executed(self):
        self.assertEqual(validate_text(VALID.replace("print('ok')", "raise RuntimeError('must not execute')"))['python'], 1)


if __name__ == '__main__':
    unittest.main()
