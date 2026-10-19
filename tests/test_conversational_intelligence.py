"""Regression tests for A.L.F.I. 1.6 follow-up resolution."""
import unittest
from conversational_intelligence import resolve_followup

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

if __name__ == "__main__":
    unittest.main()
