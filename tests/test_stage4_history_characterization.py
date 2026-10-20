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
from conversational_intelligence import select_stage4_history


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

    def test_selector_excludes_independent_question(self):
        history = [{"user": "Explain planets.", "assistant": "Planets orbit stars."}]
        selected, mode = select_stage4_history("What is 3 plus 4?", history)
        self.assertEqual((selected, mode), ([], "independent"))
        self.assertEqual(len(history), 1)

    def test_selector_preserves_explicit_followup(self):
        history = [{"user": "Explain photosynthesis.", "assistant": "Plants use sunlight."}]
        selected, mode = select_stage4_history("Why is it important?", history)
        self.assertEqual(mode, "referential")
        self.assertEqual(selected, history)

    def test_selector_recognizes_explicit_previous_answer_requests(self):
        history = [{"user": "Three lockers cost $24 plus an unknown fee.",
                    "assistant": "The exact total is unknown."}]
        for question in ("Explain your answer.", "Explain that last answer.",
                         "explain your answer!", "Please explain your answer."):
            with self.subTest(question=question):
                selected, mode = select_stage4_history(question, history)
                self.assertEqual(mode, "referential")
                self.assertEqual(selected, history)

    def test_selector_does_not_include_history_for_new_explanation(self):
        history = [{"user": "Explain clouds.", "assistant": "Condensation."}]
        selected, mode = select_stage4_history("Explain how batteries work.", history)
        self.assertEqual((selected, mode), ([], "independent"))

    def test_previous_answer_request_includes_context_in_prompt(self):
        history = [{"user": "Three lockers cost $24 plus an unknown fee.",
                    "assistant": "The exact total is unknown."}]
        with patch.dict("os.environ", {"ALFI_STAGE4_SELECTIVE_HISTORY": "1"}):
            messages, preserved = self._capture("Explain your answer.", history, False)
        self.assertEqual(len([m for m in messages if m["role"] == "assistant"]), 1)
        self.assertEqual(preserved, history)

    def test_selector_missing_referent_does_not_invent_history(self):
        selected, mode = select_stage4_history("Tell me more about that.", [])
        self.assertEqual((selected, mode), ([], "referential_missing"))

    def test_selector_bounds_referential_history(self):
        history = [{"user": str(i), "assistant": str(i)} for i in range(12)]
        selected, mode = select_stage4_history("Explain that.", history)
        self.assertEqual(len(selected), 5)
        self.assertEqual(selected[0]["user"], "7")

    def test_selector_is_opt_in_and_changes_prompt_only(self):
        history = [{"user": "Unrelated previous question", "assistant": "An old answer"}]
        with patch.dict("os.environ", {"ALFI_STAGE4_SELECTIVE_HISTORY": "1"}):
            messages, preserved = self._capture("What is 2 plus 2?", history, False)
        self.assertEqual([m["role"] for m in messages], ["system", "system", "user"])
        self.assertEqual(preserved, history)

    def test_selector_followup_includes_context_when_enabled(self):
        history = [{"user": "Explain photosynthesis.", "assistant": "Plants use sunlight."}]
        with patch.dict("os.environ", {"ALFI_STAGE4_SELECTIVE_HISTORY": "1"}):
            messages, preserved = self._capture("Why is it important?", history, False)
        self.assertEqual(len([m for m in messages if m["role"] == "assistant"]), 1)
        self.assertEqual(preserved, history)

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
