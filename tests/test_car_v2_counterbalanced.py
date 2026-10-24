import unittest
from experiments.car_v2_counterbalanced import compare


class Store:
    def retrieved_lessons(self, key):
        if key == "project":
            return [{"id": 1, "status": "approved", "lesson": "The synthetic answer is violet."}]
        return []


class CounterbalancedTests(unittest.TestCase):
    def test_ab_ba_order_and_repeat(self):
        calls = []
        def model(messages):
            calls.append(messages)
            return "ok"
        rows = compare(Store(), [{"id": "x", "topic_key": "project",
                                  "question": "What is the synthetic answer?"}], model)
        self.assertEqual([r["order"] for r in rows],
                         [["baseline", "car"], ["car", "baseline"]])
        self.assertEqual(len(calls), 4)
        self.assertEqual([m[-1] for m in calls], [calls[0][-1]] * 4)

    def test_unrelated_topic_same_prompts(self):
        calls = []
        compare(Store(), [{"id": "control", "topic_key": "weather",
                           "question": "Why rain?"}],
                lambda messages: calls.append(messages) or "ok")
        self.assertEqual(calls[0], calls[1])
        self.assertEqual(calls[2], calls[3])

    def test_no_verdict(self):
        rows = compare(Store(), [{"id": "x", "topic_key": "project",
                                  "question": "Question?"}], lambda _: "same")
        self.assertTrue(all(row["human_review"] is None for row in rows))

    def test_requires_repeats(self):
        with self.assertRaises(ValueError):
            compare(Store(), [], lambda _: "x", repeats=1)


if __name__ == "__main__":
    unittest.main()
