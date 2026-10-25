import unittest
from pathlib import Path
from experiments.car_v2_gate_f_a import inspect_source


class GateFATests(unittest.TestCase):
    def test_required_functions(self):
        report = inspect_source(Path("experiments/car_v2_gate_f_h2r.py"))
        self.assertEqual(report["missing_functions"], [])

    def test_explicitly_nonsemantic(self):
        report = inspect_source(Path("experiments/car_v2_gate_f_h2r.py"))
        self.assertIn("Static inventory only", report["note"])
