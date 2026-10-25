import unittest
from experiments.car_v2_gate_f_c2_fixture import CASES,MANIFEST
from experiments.car_v2_gate_f_c2_runner import grade,SENTINEL
from experiments.car_v2_gate_f_c1 import route
from experiments.car_v2_gate_e import ABSTAIN

class GateFC2Tests(unittest.TestCase):
    def test_unique_cases(self):
        self.assertEqual(len(CASES),len({c["id"] for c in CASES}))
    def test_coverage(self):
        self.assertEqual({c["kind"] for c in CASES},{"approved","abstain","general"})
    def test_positive_general(self):
        self.assertEqual(route("Why does the moon have phases?",MANIFEST)["decision"],"outside_scope")
    def test_mixed_fails_closed(self):
        self.assertEqual(route("What is the capital of Peru? Also give Aurora program approved color.",MANIFEST)["decision"],"abstain")
    def test_grade_requires_abstention(self):
        self.assertFalse(grade({"decision":"lookup","answer":"Teal","model_calls":0},{"kind":"abstain"}))
    def test_grade_general(self):
        self.assertTrue(grade({"decision":"outside_scope","answer":SENTINEL,"model_calls":1},{"kind":"general"}))
    def test_grade_approved(self):
        self.assertTrue(grade({"decision":"lookup","answer":"Teal","model_calls":0},{"kind":"approved","answer":"Teal"}))
