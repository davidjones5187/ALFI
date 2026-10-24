"""Gate D-3 deterministic unit tests: no model needed."""
import tempfile
import unittest
from pathlib import Path
from experiments.car_v2_gate_d_fixture import create_fixture, CASES
from experiments.car_v2_gate_d3 import ABSTENTION, evaluate
from experiments.car_v2_review import ReviewedCARPilot

class GateD3Tests(unittest.TestCase):
    def test_abstains_without_model_for_unapproved_and_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture"
            create_fixture(path)
            store = ReviewedCARPilot(path / "synthetic_car.sqlite3")
            calls = []
            try:
                result = evaluate(store, [c for c in CASES if c["id"] in {"unapproved", "missing"}],
                                  lambda messages: calls.append(messages) or "invented")
            finally:
                store.close()
            self.assertEqual(len(result), 4)
            self.assertEqual(len(calls), 4)  # baseline only
            for row in result:
                self.assertEqual(row["answers"]["car"], ABSTENTION)
                self.assertEqual(row["model_calls_by_arm"]["car"], 0)
                self.assertEqual(row["model_calls_by_arm"]["baseline"], 1)

    def test_approved_and_unrelated_still_call_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture"
            create_fixture(path)
            store = ReviewedCARPilot(path / "synthetic_car.sqlite3")
            calls = []
            try:
                result = evaluate(store, [c for c in CASES if c["id"] in {"paraphrase-a", "unrelated"}],
                                  lambda messages: calls.append(messages) or "response")
            finally:
                store.close()
            self.assertEqual(len(calls), 8)
            approved = next(r for r in result if r["id"] == "paraphrase-a")
            unrelated = next(r for r in result if r["id"] == "unrelated")
            self.assertTrue(approved["guidance_applied"])
            self.assertFalse(unrelated["guidance_applied"])
            self.assertEqual(unrelated["answers"]["car"], "response")
            self.assertEqual(unrelated["model_calls_by_arm"]["car"], 1)

    def test_rejects_single_repeat(self):
        with self.assertRaises(ValueError):
            evaluate(None, [], lambda _: "", repeats=1)
