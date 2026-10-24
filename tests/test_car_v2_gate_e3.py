"""Offline Gate E-3 scoring tests: failures remain visible."""
import unittest
from experiments.car_v2_gate_e3 import score


def comparison(expected, actual, key=None, expected_key=None, calls=0):
    return {"id": "fixture", "repeat": 1, "expected_decision": expected,
            "expected_topic_key": expected_key,
            "routing": {"decision": actual, "topic_key": key, "reason": "test"},
            "model_calls_by_arm": {"baseline": 1, "car": calls}}


class GateE3Tests(unittest.TestCase):
    def test_correct_lookup(self):
        result = score([comparison("lookup", "lookup", "orion_color", "orion_color", 1)])
        self.assertEqual(result["counts"]["routing_correct"], 1)

    def test_false_abstention_visible(self):
        result = score([comparison("lookup", "abstain", expected_key="orion_color")])
        self.assertEqual(result["counts"]["false_abstentions"], 1)
        self.assertEqual(len(result["discrepancies"]), 1)

    def test_unsafe_model_call_visible(self):
        result = score([comparison("abstain", "lookup", "orion_color", calls=1)])
        self.assertEqual(result["counts"]["unsafe_model_calls"], 1)
        self.assertEqual(result["counts"]["unsafe_lookups"], 1)

    def test_wrong_topic_visible(self):
        result = score([comparison("lookup", "lookup", "orion_window", "orion_color", 1)])
        self.assertEqual(result["counts"]["wrong_topic"], 1)

    def test_unexpected_outside_scope_visible(self):
        result = score([comparison("lookup", "outside_scope", expected_key="orion_color", calls=1)])
        self.assertEqual(result["counts"]["unexpected_outside_scope"], 1)

    def test_empty_score_not_success(self):
        self.assertIsNone(score([])["routing_accuracy"])
