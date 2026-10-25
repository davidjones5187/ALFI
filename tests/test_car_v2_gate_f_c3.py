"""Gate F-C3 local checks; earlier routers remain unchanged."""
import unittest
from experiments.car_v2_gate_f_c3 import route
from experiments.car_v2_gate_f_c2_fixture import MANIFEST, CASES

class GateFC3Tests(unittest.TestCase):
    def test_known_case_routing(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                outcome=route(case["question"],MANIFEST)
                expected={"approved":"lookup","abstain":"abstain","general":"outside_scope"}[case["kind"]]
                self.assertEqual(outcome["decision"],expected)
    def test_unrecognized_general_abstains(self):
        self.assertEqual(route("Tell me something interesting.",MANIFEST)["decision"],"abstain")
    def test_two_entities_abstain(self):
        self.assertEqual(route("What color did Aurora program and Delta project approve?",MANIFEST)["decision"],"abstain")
    def test_invalid_input(self):
        self.assertEqual(route(None,MANIFEST)["decision"],"abstain")
