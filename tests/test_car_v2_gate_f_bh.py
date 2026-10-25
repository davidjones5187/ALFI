import unittest
from experiments.car_v2_gate_f_bh_fixture import CASES, MANIFEST
from experiments.car_v2_gate_f_bh_runner import grade, SENTINEL
from experiments.car_v2_gate_f_b import strict_route
from experiments.car_v2_gate_e import ABSTAIN

class GateFBHTests(unittest.TestCase):
    def test_unique_cases(self):
        self.assertEqual(len(CASES),len({case["id"] for case in CASES}))
    def test_all_classes(self):
        self.assertEqual({case["kind"] for case in CASES},{"approved","abstain","general"})
    def test_new_manifest(self):
        self.assertEqual(strict_route("What color did Solstice program approve?",MANIFEST)["topic_key"],"solstice_color")
    def test_abstain_grade(self):
        self.assertTrue(grade({"decision":"abstain","answer":ABSTAIN,"model_calls":0},{"kind":"abstain"}))
    def test_general_grade(self):
        self.assertTrue(grade({"decision":"outside_scope","answer":SENTINEL,"model_calls":1},{"kind":"general"}))
