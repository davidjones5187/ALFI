"""P1 persistence regression checks; no Ollama required."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from first_ai import ALFI


class PersistenceReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def make_ai(self, name):
        return ALFI(memory_file=self.root / name / "ai_memory.json", use_ollama=False)

    def test_history_isolation_between_memory_directories(self):
        first = self.make_ai("one")
        second = self.make_ai("two")
        first.record("question", "answer")
        self.assertEqual(second.history, [])
        self.assertEqual(self.make_ai("one").history[-1]["assistant"], "answer")
        self.assertEqual(self.make_ai("two").history, [])

    def test_clearhistory_only_removes_instance_history(self):
        first, second = self.make_ai("one"), self.make_ai("two")
        first.record("a", "one")
        second.record("b", "two")
        first.clear_history()
        self.assertEqual(self.make_ai("one").history, [])
        self.assertEqual(len(self.make_ai("two").history), 1)

    def test_history_failed_write_keeps_previous_state(self):
        ai = self.make_ai("one")
        ai.record("before", "saved")
        original = ai.history[:]
        with patch.object(ai, "_atomic_json_write", side_effect=OSError("simulated disk failure")):
            with self.assertRaises(OSError):
                ai.record("after", "not saved")
        self.assertEqual(ai.history, original)
        self.assertEqual(self.make_ai("one").history, original)

    def test_taught_memory_save_failure_rolls_back(self):
        ai = self.make_ai("one")
        before = json.dumps(ai.data, sort_keys=True)
        with patch.object(ai, "save", side_effect=OSError("simulated disk failure")):
            with self.assertRaises(OSError):
                ai.teach("new topic", "question", "answer")
        self.assertEqual(json.dumps(ai.data, sort_keys=True), before)

    def test_forget_failure_rolls_back(self):
        ai = self.make_ai("one")
        ai.teach("new topic", "question", "answer")
        with patch.object(ai, "save", side_effect=OSError("simulated disk failure")):
            with self.assertRaises(OSError):
                ai.forget_topic("new topic")
        self.assertIn("new_topic", ai.data)

    def test_active_taught_topic_followup_precedes_clarification(self):
        ai = self.make_ai("one")
        ai.teach("project", "what is project inception?", "First phase.")
        self.assertEqual(ai.respond("what is project inception?"), "First phase.")
        self.assertIn("First phase.", ai.respond("tell me more"))

    def test_no_active_topic_still_clarifies(self):
        ai = self.make_ai("one")
        self.assertEqual(ai.respond("tell me more"), "What topic would you like me to explain?")

    def test_generated_followup_does_not_use_taught_topic(self):
        ai = self.make_ai("one")
        ai.teach("project", "what is project inception?", "First phase.")
        ai.respond("what is project inception?")
        ai.last_source = "generated"
        ai.history = [{"user": "Explain the weather.", "assistant": "Clouds form."}]
        with patch.object(ai, "generate", return_value="More on clouds.") as generated:
            self.assertEqual(ai.respond("tell me more"), "More on clouds.")
            generated.assert_called_once_with("tell me more")

    def test_atomic_replace_failure_preserves_previous_file(self):
        ai = self.make_ai("one")
        ai.record("before", "saved")
        original = ai.history_file.read_bytes()
        with patch("first_ai.os.replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(OSError):
                ai.record("after", "not saved")
        self.assertEqual(ai.history_file.read_bytes(), original)
        self.assertEqual(list(ai.history_file.parent.glob(".conversation_history.json.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
