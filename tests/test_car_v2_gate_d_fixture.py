"""Offline Gate D fixture regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from experiments.car_v2_gate_d_fixture import create_fixture

class GateDFixtureTests(unittest.TestCase):
    def test_creation_restart_and_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fixture"
            report = create_fixture(target)
            self.assertEqual(report["status"], "validated_gate_d_fixture")
            self.assertTrue(report["verified_after_restart"])
            self.assertEqual(report["model_calls"], 0)
            cases = json.loads((target / "cases.json").read_text())
            self.assertEqual(len(cases), 8)
            self.assertEqual(len({c["id"] for c in cases}), 8)

    def test_refuses_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                create_fixture(Path(tmp))
