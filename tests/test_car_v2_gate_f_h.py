import unittest
from experiments.car_v2_gate_f_h_fixture import MANIFEST, CASES
from experiments.car_v2_gate_f import validate_manifest
from experiments.car_v2_gate_f_h import assess_holdout


class GateFHTests(unittest.TestCase):
    def test_holdout_manifest(self):
        validate_manifest(MANIFEST)
        self.assertEqual(len(MANIFEST),3)

    def test_holdout_cases_unique(self):
        self.assertEqual(len(CASES),len({c["id"] for c in CASES}))
        self.assertGreaterEqual(len(CASES),12)

    def test_abstention_answer_is_scored(self):
        rows=[{"id":"x","repeat":1,"expected_decision":"abstain",
               "expected_topic_key":None,"routing":{"decision":"abstain"},
               "answers":{"car":"wrong"},"model_calls_by_arm":{"car":0}}]
        self.assertEqual(len(assess_holdout(rows)["abstention_failures"]),1)
