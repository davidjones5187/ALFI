import unittest

from conversational_intelligence import (
    resolve_followup,
    select_stage5_r2_history,
)


class ContextualContinuityV14Tests(unittest.TestCase):

    def setUp(self):
        self.history = [{
            "user": "Tell me about Mars.",
            "assistant": "Mars is the fourth planet from the Sun.",
        }]

    def test_referential_questions_retain_context(self):
        for question in (
            "How big is it?",
            "Compare it with Earth.",
            "What about its atmosphere?",
        ):
            with self.subTest(question=question):
                selected, mode = select_stage5_r2_history(
                    question, self.history
                )
                self.assertEqual(mode, "referential")
                self.assertEqual(selected, self.history)
                self.assertIsNotNone(
                    resolve_followup(question, self.history)
                )

    def test_independent_questions_remain_isolated(self):
        for question in (
            "Now tell me about Jupiter.",
            "What is Python?",
        ):
            with self.subTest(question=question):
                selected, mode = select_stage5_r2_history(
                    question, self.history
                )
                self.assertEqual(mode, "independent")
                self.assertEqual(selected, [])
                self.assertIsNone(
                    resolve_followup(question, self.history)
                )

    def test_missing_history_does_not_invent_context(self):
        selected, mode = select_stage5_r2_history(
            "How big is it?", []
        )
        self.assertEqual(selected, [])
        self.assertEqual(mode, "referential_missing")
        self.assertIsNone(
            resolve_followup("How big is it?", [])
        )

    def test_explicit_topic_change_isolated_after_followup(self):
        history = self.history + [{
            "user": "How big is it?",
            "assistant": "Mars is about 6,779 km in diameter.",
        }]
        selected, mode = select_stage5_r2_history(
            "Now tell me about Jupiter.", history
        )
        self.assertEqual(mode, "independent")
        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
