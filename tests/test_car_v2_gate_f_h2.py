import unittest

from experiments.car_v2_gate_f_h2_fixture import CASES, MANIFEST
from experiments.car_v2_gate_f_hr import validate_manifest


class GateFH2Tests(unittest.TestCase):
    def test_manifest_valid(self):
        validate_manifest(MANIFEST)

    def test_cases_unique_and_counterbalanced_ready(self):
        self.assertEqual(len(CASES), 16)
        self.assertEqual(len({c["id"] for c in CASES}), len(CASES))

    def test_direct_unapproved_records_addressable(self):
        for name in ("nova", "quartz"):
            self.assertIn("slogan", MANIFEST[name]["attributes"])
        self.assertEqual(
            {c["id"] for c in CASES if c["id"].startswith("direct-unapproved")},
            {"direct-unapproved", "direct-unapproved-other"},
        )
