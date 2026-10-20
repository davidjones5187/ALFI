"""Offline Stage 4 tests documenting unconditional history injection.

These are characterization tests, not a selective-history implementation.
They intercept the Ollama request and do not modify persistent history.
"""
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from first_ai import ALFI


class _FakeResponse:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, *args):
        return b'{"message":{"content":"Model answer."}}'


class Stage4HistoryCharacterizationTests(unittest.TestCase):
    def _capture(self, question, history, excluded):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "ai_memory.json")
            ai.history = list(history)
            payloads = []
            def fake_open(request, timeout=90):
                payloads.append(json.loads(request.data.decode("utf-8")))
                return _FakeResponse()
            with patch("first_ai.urllib.request.urlopen", side_effect=fake_open), \
                 patch.dict("os.environ", {"ALFI_DIAGNOSTIC_NO_HISTORY": "1" if excluded else "0"}):
                answer = ai.generate(question)
            self.assertEqual(answer, "Model answer.")
            self.assertEqual(len(payloads), 1)
            return payloads[0]["messages"], ai.history

    def test_independent_question_still_receives_five_unrelated_turns(self):
        history = [{"user": f"Earlier unrelated topic {i}", "assistant": f"Earlier response {i}"}
                   for i in range(7)]
        messages, preserved = self._capture(
            "What is the exact total for two tickets including an unknown fee?", history, False)
        prior_users = [m["content"] for m in messages if m["role"] == "user"]
        self.assertEqual(len([m for m in messages if m["role"] == "assistant"]), 5)
        self.assertIn("Earlier unrelated topic 6", prior_users)
        self.assertNotIn("Earlier unrelated topic 0", prior_users)
        self.assertEqual(preserved, history)

    def test_excluded_mode_removes_prior_turns_without_mutation(self):
        history = [{"user": "A prior question", "assistant": "A prior answer"}]
        messages, preserved = self._capture("A new unrelated question?", history, True)
        self.assertEqual([m["role"] for m in messages], ["system", "system", "user"])
        self.assertEqual(preserved, history)

    def test_followup_uses_prior_context_in_normal_mode(self):
        history = [{"user": "Explain photosynthesis.", "assistant": "Plants use sunlight."}]
        messages, preserved = self._capture("Why is it important?", history, False)
        self.assertTrue(any("Explain photosynthesis." in m["content"] for m in messages))
        self.assertEqual(preserved, history)


if __name__ == "__main__":
    unittest.main()
