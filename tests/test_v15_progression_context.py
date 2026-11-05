import unittest

from conversational_intelligence import select_stage5_r2_history


class ProgressionContextTests(unittest.TestCase):
    def setUp(self):
        self.history = [
            {
                "user": "Let's plan a fictional mission. Robot Atlas will explore a cave on Mars.",
                "assistant": "Acknowledged.",
            },
            {
                "user": "Atlas has a battery that lasts six hours.",
                "assistant": "Acknowledged.",
            },
            {
                "user": "The mission requires eight hours of exploration.",
                "assistant": "Acknowledged.",
            },
        ]

    def test_problem_retrieves_task_facts(self):
        selected, mode = select_stage5_r2_history(
            "What problem does Atlas face?", self.history
        )
        self.assertEqual(mode, "task_problem")
        self.assertEqual(len(selected), 3)
        self.assertIn("six hours", selected[1]["user"])
        self.assertIn("eight hours", selected[2]["user"])

    def test_unknown_subject_does_not_inherit_task(self):
        selected, mode = select_stage5_r2_history(
            "What problem does Vega face?", self.history
        )
        self.assertEqual(mode, "task_problem_missing")
        self.assertEqual(selected, [])

    def test_recommendation_after_problem(self):
        history = self.history + [{
            "user": "What problem does Atlas face?",
            "assistant": "The battery is too short for the mission.",
        }]
        selected, mode = select_stage5_r2_history(
            "What would you recommend?", history
        )
        self.assertEqual(mode, "task_recommendation")
        self.assertEqual(len(selected), 4)

    def test_unrelated_question_is_independent(self):
        selected, mode = select_stage5_r2_history(
            "What is Python?", self.history
        )
        self.assertEqual(mode, "independent")
        self.assertEqual(selected, [])

    def test_recommendation_without_task_context(self):
        selected, mode = select_stage5_r2_history(
            "What would you recommend?", []
        )
        self.assertEqual(mode, "independent")
        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
