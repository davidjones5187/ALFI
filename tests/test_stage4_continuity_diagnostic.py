"""Offline tests for Stage 4 multi-turn diagnostic harness."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "stage4_continuity_diagnostic.py"
spec = importlib.util.spec_from_file_location("stage4_continuity_diagnostic", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Stage4ContinuityDiagnosticTests(unittest.TestCase):
    def test_help_direct_launch_outside_repo(self):
        with tempfile.TemporaryDirectory() as folder:
            completed = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                                       cwd=folder, capture_output=True, text=True, timeout=15)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--output", completed.stdout)

    def test_counterbalanced_sequences_and_no_record(self):
        scenarios = [
            {"id": "A", "kind": "followup", "turns": ["Explain trees.", "Why is it important?"]},
            {"id": "B", "kind": "topic_shift", "turns": ["Explain clouds.", "What is 2 plus 2?"]},
        ]
        with patch.object(module.ALFI, "generate", return_value="A test answer.") as generate, \
             patch.object(module.ALFI, "record", side_effect=AssertionError("no persistent record")):
            runs = module.run_scenarios(scenarios, "gemma3:4b", "http://127.0.0.1:11434/api/chat")
        self.assertEqual([(r["scenario"], r["condition"]) for r in runs],
                         [("A", "normal"), ("A", "selective"), ("B", "selective"), ("B", "normal")])
        self.assertEqual(generate.call_count, 8)
        self.assertTrue(all(len(r["turns"]) == 2 for r in runs))

    def test_rejects_model_unavailable_instead_of_reporting_success(self):
        scenarios = [{"id": "A", "kind": "followup", "turns": ["Explain trees."]}]
        with patch.object(module.ALFI, "generate", return_value="I couldn't reach my local AI engine."):
            with self.assertRaises(RuntimeError):
                module.run_scenarios(scenarios, "gemma3:4b", "http://127.0.0.1:11434/api/chat")


if __name__ == "__main__":
    unittest.main()
