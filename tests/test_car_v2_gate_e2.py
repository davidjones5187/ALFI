"""Gate E-2 offline counterbalance and routing checks."""
import tempfile
import unittest
from pathlib import Path

from experiments.car_v2_gate_d_fixture import create_fixture
from experiments.car_v2_gate_e2 import evaluate
from experiments.car_v2_review import ReviewedCARPilot


class GateE2Tests(unittest.TestCase):
    def test_counterbalanced_order_and_no_topic_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "fixture"
            create_fixture(folder)
            store = ReviewedCARPilot(folder / "synthetic_car.sqlite3")
            try:
                cases = [{"id": "color", "question": "Which color did Orion select?",
                          "expected_decision": "lookup", "expected_topic_key": "orion_color"}]
                result = evaluate(store, cases, lambda _: "answer")
            finally:
                store.close()
            self.assertEqual([r["order"] for r in result],
                             [["baseline", "car"], ["car", "baseline"]])
            self.assertTrue(all(r["routing"]["topic_key"] == "orion_color" for r in result))
            self.assertEqual(len(result), 2)

    def test_abstention_skips_only_car_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "fixture"
            create_fixture(folder)
            store = ReviewedCARPilot(folder / "synthetic_car.sqlite3")
            calls = []
            try:
                cases = [{"id": "slogan", "question": "What is Orion's slogan?",
                          "expected_decision": "abstain", "expected_topic_key": None}]
                result = evaluate(store, cases, lambda m: calls.append(m) or "guess")
            finally:
                store.close()
            self.assertEqual(len(calls), 2)
            self.assertTrue(all(r["model_calls_by_arm"] == {"baseline": 1, "car": 0}
                                for r in result))
            self.assertTrue(all(r["routing"]["reason"] == "no_approved_record" for r in result))

    def test_unrelated_passes_both_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "fixture"
            create_fixture(folder)
            store = ReviewedCARPilot(folder / "synthetic_car.sqlite3")
            calls = []
            try:
                cases = [{"id": "rain", "question": "How do clouds produce rain?",
                          "expected_decision": "outside_scope", "expected_topic_key": None}]
                result = evaluate(store, cases, lambda m: calls.append(m) or "rain")
            finally:
                store.close()
            self.assertEqual(len(calls), 4)
            self.assertTrue(all(r["routing"]["decision"] == "outside_scope" for r in result))

    def test_repeats_required(self):
        with self.assertRaises(ValueError):
            evaluate(None, [], lambda _: "", repeats=1)
