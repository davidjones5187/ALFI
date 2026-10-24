"""Isolated CAR pilot tests. Standard library only; no Ollama required."""
import tempfile
import unittest
from pathlib import Path
from experiments.car_v2_pilot import CARPilot


class CARPilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "car_pilot.sqlite3"
        self.pilot = CARPilot(self.path)
        self.addCleanup(self.pilot.close)

    def propose(self, **overrides):
        values = dict(context="User corrected an answer", goal="Recall current decision",
                      action="Answered using outdated value", result="Correction received",
                      evidence=["test:turn-1"], correction="Use SQLite",
                      lesson="Check accepted decision before follow-up")
        values.update(overrides)
        return self.pilot.propose(**values)

    def test_proposal_is_unverified_and_not_retrieved(self):
        eid = self.propose()
        self.assertEqual(self.pilot.get(eid)["status"], "unverified")
        self.assertEqual(self.pilot.retrieved_lessons("decision"), [])

    def test_restart_retains_proposal_and_correction(self):
        eid = self.propose()
        second = CARPilot(self.path)
        try:
            self.assertEqual(second.get(eid)["correction"], "Use SQLite")
            self.assertEqual(second.get(eid)["evidence"], ["test:turn-1"])
        finally:
            second.close()

    def test_cross_scope_isolation(self):
        eid = self.propose()
        other = CARPilot(self.path, scope="different")
        try:
            with self.assertRaises(ValueError):
                other.get(eid)
            self.assertEqual(other.candidates(), [])
        finally:
            other.close()

    def test_no_evidence_rejected_without_partial_write(self):
        with self.assertRaises(ValueError):
            self.propose(evidence=[])
        self.assertEqual(self.pilot.candidates(), [])

    def test_model_cannot_confirm(self):
        eid = self.propose()
        with self.assertRaises(PermissionError):
            self.pilot.confirm(eid, verifier="model")
        self.assertEqual(self.pilot.get(eid)["status"], "unverified")

    def test_no_lesson_has_no_candidate(self):
        eid = self.propose(lesson=None)
        self.assertEqual(self.pilot.get(eid)["status"], "not_applicable")
        self.assertEqual(self.pilot.candidates(), [])

    def test_database_path_restrictions(self):
        with self.assertRaises(ValueError):
            CARPilot(Path(self.temp.name) / "structured_memory.json")

    def test_oversized_evidence_rejected(self):
        with self.assertRaises(ValueError):
            self.propose(evidence=["x" * 5000])
        self.assertEqual(self.pilot.candidates(), [])


if __name__ == "__main__":
    unittest.main()
