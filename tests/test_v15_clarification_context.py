import unittest

from conversational_intelligence import select_stage5_r2_history


class ClarificationContextTests(unittest.TestCase):
    def setUp(self):
        self.history = [
            {
                "user": "In this fictional scenario, the Orion device has a green crystal.",
                "assistant": "Acknowledged.",
            },
            {
                "user": "The fictional Vega device has a red crystal.",
                "assistant": "Acknowledged.",
            },
            {
                "user": "What color is its crystal?",
                "assistant": "Please specify the device.",
            },
        ]

    def test_clarification_retrieves_orion(self):
        selected, mode = select_stage5_r2_history(
            "I mean the Orion device. What color is its crystal?",
            self.history,
        )
        self.assertEqual(mode, "clarified_subject")
        self.assertEqual(len(selected), 1)
        self.assertIn("green crystal", selected[0]["user"])

    def test_clarification_retrieves_vega(self):
        selected, mode = select_stage5_r2_history(
            "I mean the Vega device. What color is its crystal?",
            self.history,
        )
        self.assertEqual(mode, "clarified_subject")
        self.assertEqual(len(selected), 1)
        self.assertIn("red crystal", selected[0]["user"])

    def test_unknown_subject_does_not_guess(self):
        selected, mode = select_stage5_r2_history(
            "I mean the Atlas device. What color is its crystal?",
            self.history,
        )
        self.assertEqual(mode, "clarified_subject_missing")
        self.assertEqual(selected, [])

    def test_unrelated_question_remains_independent(self):
        selected, mode = select_stage5_r2_history(
            "What is Python?",
            self.history,
        )
        self.assertEqual(mode, "independent")
        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
