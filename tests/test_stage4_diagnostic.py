"""Offline regression tests for the Stage 4 diagnostic runner."""
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "stage4_history_diagnostic.py"
spec = importlib.util.spec_from_file_location("stage4_history_diagnostic", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Stage4DiagnosticTests(unittest.TestCase):
    def test_direct_script_help_from_outside_repo(self):
        with tempfile.TemporaryDirectory() as folder:
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--help"],
                cwd=folder, capture_output=True, text=True, timeout=15)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("--output", completed.stdout)

    def test_snapshot_reads_without_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "history.json"
            original = '[{"user":"old question","assistant":"old answer"}]'
            path.write_text(original, encoding="utf-8")
            self.assertEqual(len(module.history_snapshot(path)), 1)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_counterbalanced_runs_do_not_record(self):
        with patch.object(module.ALFI, "generate", return_value="The total is unknown.") as generate, \
             patch.object(module.ALFI, "record", side_effect=AssertionError("must not record")):
            results = module.run_trials(module.CASES[:2],
                                        [{"user": "private", "assistant": "reply"}],
                                        "gemma3:4b", "http://127.0.0.1:11434/api/chat")
        self.assertEqual([x["condition"] for x in results],
                         ["normal", "excluded", "excluded", "normal"])
        self.assertEqual(generate.call_count, 4)
        self.assertEqual(len(results), 4)


if __name__ == "__main__":
    unittest.main()
