import unittest

from conversational_intelligence import select_stage5_r2_history


class TestV15CorrectionContext(unittest.TestCase):
    def setUp(self):
        self.history = [
            {
                "user": "For this fictional scenario, the Orion device uses a blue crystal.",
                "assistant": "The Orion device uses a blue crystal.",
            },
            {
                "user": "Correction: The fictional Orion device uses a green crystal, not a blue crystal.",
                "assistant": "Acknowledged. The Orion device uses a green crystal.",
            },
            {
                "user": "What color crystal does the fictional Orion device use?",
                "assistant": "The Orion device uses a violet crystal.",
            },
        ]

    def test_corrected_subject_is_available(self):
        selected, mode = select_stage5_r2_history(
            "What color crystal does the fictional Orion device use?",
            self.history[:2],
        )
        self.assertEqual(mode, "recent_correction")
        self.assertEqual(len(selected), 1)
        self.assertIn("green crystal", selected[0]["user"])

    def test_answer_change_includes_previous_exchange(self):
        selected, mode = select_stage5_r2_history(
            "Why did your answer change?",
            self.history,
        )
        self.assertEqual(mode, "answer_change")
        self.assertEqual(len(selected), 3)

    def test_unrelated_question_remains_independent(self):
        selected, mode = select_stage5_r2_history(
            "What is Python?",
            self.history,
        )
        self.assertEqual(mode, "independent")
        self.assertEqual(selected, [])

    def test_unrelated_device_does_not_receive_correction(self):
        selected, mode = select_stage5_r2_history(
            "What color crystal does the fictional Vega device use?",
            self.history,
        )
        self.assertEqual(mode, "independent")
        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
