"""Regression tests for A.L.F.I. 1.6 follow-up resolution."""
import unittest
from conversational_intelligence import resolve_followup, response_guidance

class ConversationalIntelligenceTests(unittest.TestCase):
    def test_example_retains_subject(self):
        history = [{"user": "Explain supervised learning.", "assistant": "It uses labels."}]
        self.assertIn("Explain supervised learning.", resolve_followup("Give me an example.", history))

    def test_no_context_does_not_guess(self):
        self.assertIsNone(resolve_followup("Explain that.", []))

    def test_new_question_not_rewritten(self):
        history = [{"user": "Explain Python.", "assistant": "A language."}]
        self.assertIsNone(resolve_followup("Explain quantum computing.", history))

    def test_commands_untouched(self):
        self.assertIsNone(resolve_followup("/forgetmemory", [{"user": "Explain Python."}]))

    def test_bounded_history(self):
        history = [{"user": "Explain Python."}] + [{"user": "/help"}] * 5
        self.assertIsNone(resolve_followup("Give me an example.", history))

    def test_prior_followup_skipped(self):
        history = [{"user": "Explain supervised learning."}, {"user": "Give me an example."}]
        self.assertIn("supervised learning", resolve_followup("Tell me more.", history))

    def test_unrelated_pronoun_not_assumed(self):
        self.assertIsNone(resolve_followup("Is it raining tomorrow?", [{"user": "Explain Python."}]))

class ResponseIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.history = [{"user": "Explain supervised learning.", "assistant": "It learns from labeled data."}]

    def test_followup_avoids_repetition(self):
        guidance = response_guidance("Tell me more.", self.history)
        self.assertIn("without repeating", guidance)
        self.assertIn("NEW relevant insight", guidance)

    def test_example_is_concise(self):
        self.assertIn("2-4 sentences", response_guidance("Give me an example.", self.history))

    def test_explicit_detail_wins(self):
        self.assertIn("explain thoroughly", response_guidance("Explain that in detail.", self.history))

    def test_explicit_brevity_wins(self):
        self.assertIn("one or two sentences", response_guidance("Briefly explain that.", self.history))

    def test_topic_change_not_dragged_back(self):
        guidance = response_guidance("Explain quantum computing.", self.history)
        self.assertIn("different subject", guidance)
        self.assertNotIn("2-4 sentences", guidance)

    def test_history_not_modified(self):
        before = [dict(turn) for turn in self.history]
        response_guidance("Tell me more.", self.history)
        self.assertEqual(self.history, before)

    def test_no_context_guidance(self):
        self.assertIn("Be concise by default", response_guidance("Hello", []))


if __name__ == "__main__":
    unittest.main()
