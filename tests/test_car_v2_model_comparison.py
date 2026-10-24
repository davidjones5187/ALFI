import unittest
from experiments.car_v2_model_comparison import make_messages, run_pairs


class FakeStore:
    def retrieved_lessons(self, key):
        if key == "project":
            return [{"id": 1, "lesson": "Use milestone B", "status": "approved"}]
        return []


class CARModelComparisonTests(unittest.TestCase):
    def test_same_question_in_both_arms(self):
        calls = []
        def model(messages):
            calls.append(messages)
            return "response " + str(len(messages))
        results = run_pairs(FakeStore(), [{"id": "p", "topic_key": "project",
                                           "question": "What is the milestone?"}], model)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][-1], calls[1][-1])
        self.assertEqual(len(calls[0]), 2)
        self.assertEqual(len(calls[1]), 3)
        self.assertTrue(results[0]["guidance_applied"])

    def test_unrelated_question_has_no_guidance(self):
        calls = []
        def model(messages):
            calls.append(messages)
            return "same"
        results = run_pairs(FakeStore(), [{"id": "w", "topic_key": "weather",
                                           "question": "What causes rain?"}], model)
        self.assertEqual(calls[0], calls[1])
        self.assertFalse(results[0]["guidance_applied"])

    def test_no_automatic_quality_claim(self):
        results = run_pairs(FakeStore(), [{"id": "p", "topic_key": "project",
                                           "question": "Milestone?"}], lambda _: "same")
        self.assertFalse(results[0]["changed"])
        self.assertIsNone(results[0]["human_accuracy"])
        self.assertIsNone(results[0]["human_contamination"])

    def test_context_builder_is_off_by_default(self):
        self.assertEqual(len(make_messages("Question?")), 2)

    def test_approved_guidance_is_labeled(self):
        result = []
        run_pairs(FakeStore(), [{"id": "p", "topic_key": "project",
                                 "question": "Milestone?"}],
                  lambda messages: result.append(messages) or "answer")
        self.assertIn("not independently verified facts", result[1][1]["content"])


if __name__ == "__main__":
    unittest.main()
