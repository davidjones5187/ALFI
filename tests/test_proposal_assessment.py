"""Tests for A.L.F.I. 2.0 supervised proposal readiness."""

import unittest
from dataclasses import FrozenInstanceError

from proposal_assessment import assess_proposal_readiness


class ProposalReadinessTests(unittest.TestCase):

    def test_complete_information_is_ready(self):
        result = assess_proposal_readiness(
            ["framework"],
            [{"field": "framework", "value": "unittest",
              "source": "maintainer"}],
        )
        self.assertTrue(result.ready)
        self.assertEqual(result.assessment.status, "complete")

    def test_missing_information_is_not_ready(self):
        result = assess_proposal_readiness(
            ["framework", "version"],
            [{"field": "framework", "value": "unittest",
              "source": "maintainer"}],
        )
        self.assertFalse(result.ready)
        self.assertEqual(result.assessment.missing, ("version",))

    def test_conflicting_information_is_not_ready(self):
        result = assess_proposal_readiness(
            ["framework"],
            [
                {"field": "framework", "value": "unittest",
                 "source": "maintainer"},
                {"field": "framework", "value": "pytest",
                 "source": "reviewer"},
            ],
        )
        self.assertFalse(result.ready)
        self.assertEqual(result.assessment.status, "conflicting")

    def test_missing_and_conflicting_information(self):
        result = assess_proposal_readiness(
            ["framework", "version"],
            [
                {"field": "framework", "value": "unittest",
                 "source": "maintainer"},
                {"field": "framework", "value": "pytest",
                 "source": "reviewer"},
            ],
        )
        self.assertFalse(result.ready)
        self.assertEqual(result.assessment.missing, ("version",))
        self.assertEqual(len(result.assessment.conflicts), 1)

    def test_matching_sources_are_not_conflicting(self):
        result = assess_proposal_readiness(
            ["framework"],
            [
                {"field": "framework", "value": "unittest",
                 "source": "maintainer"},
                {"field": "framework", "value": "unittest",
                 "source": "reviewer"},
            ],
        )
        self.assertTrue(result.ready)

    def test_conflict_preserves_source_attribution(self):
        result = assess_proposal_readiness(
            ["framework"],
            [
                {"field": "framework", "value": "unittest",
                 "source": "maintainer"},
                {"field": "framework", "value": "pytest",
                 "source": "reviewer"},
            ],
        )
        entries = result.assessment.conflicts[0].entries
        self.assertEqual(
            [(item.value, item.source) for item in entries],
            [("unittest", "maintainer"), ("pytest", "reviewer")],
        )

    def test_empty_requirements_are_vacuously_ready(self):
        result = assess_proposal_readiness([], [])
        self.assertTrue(result.ready)
        self.assertEqual(result.assessment.status, "complete")

    def test_invalid_information_is_rejected(self):
        with self.assertRaises(ValueError):
            assess_proposal_readiness(
                ["framework"],
                [{"field": "framework", "value": "",
                  "source": "maintainer"}],
            )

    def test_result_is_immutable(self):
        result = assess_proposal_readiness([], [])
        with self.assertRaises(FrozenInstanceError):
            result.ready = False

    def test_no_execution_or_approval_interface(self):
        result = assess_proposal_readiness([], [])
        for name in ("execute", "approve", "run"):
            self.assertFalse(hasattr(result, name))


if __name__ == "__main__":
    unittest.main()
