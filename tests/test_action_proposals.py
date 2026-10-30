"""Tests for A.L.F.I. supervised action proposals."""

import unittest
from dataclasses import FrozenInstanceError

from action_proposals import ActionProposal, create_action_proposal


class ActionProposalTests(unittest.TestCase):

    def test_valid_proposal(self):
        proposal = create_action_proposal(
            "Review Python test coverage",
            "Identify modules requiring additional tests",
            ["Coverage data may be incomplete"],
        )

        self.assertEqual(proposal.status, "proposed")
        self.assertTrue(proposal.requires_approval)
        self.assertEqual(
            proposal.action,
            "Review Python test coverage",
        )
        self.assertEqual(
            proposal.risks,
            ("Coverage data may be incomplete",),
        )

    def test_empty_action_rejected(self):
        with self.assertRaises(ValueError):
            create_action_proposal(
                " ",
                "Useful improvement",
                ["Possible uncertainty"],
            )

    def test_empty_justification_rejected(self):
        with self.assertRaises(ValueError):
            create_action_proposal(
                "Review tests",
                "",
                ["Possible uncertainty"],
            )

    def test_missing_risks_rejected(self):
        with self.assertRaises(ValueError):
            create_action_proposal(
                "Review tests",
                "Improve reliability",
                [],
            )

    def test_invalid_risk_rejected(self):
        with self.assertRaises(ValueError):
            create_action_proposal(
                "Review tests",
                "Improve reliability",
                ["Valid risk", ""],
            )

    def test_immutable_proposal(self):
        proposal = create_action_proposal(
            "Review tests",
            "Improve reliability",
            ["Incomplete results"],
        )

        with self.assertRaises(FrozenInstanceError):
            proposal.status = "approved"

    def test_risks_are_immutable(self):
        risks = ["Incomplete results"]

        proposal = create_action_proposal(
            "Review tests",
            "Improve reliability",
            risks,
        )

        risks.append("New risk")

        self.assertEqual(
            proposal.risks,
            ("Incomplete results",),
        )

    def test_no_execution_interface(self):
        proposal = create_action_proposal(
            "Review tests",
            "Improve reliability",
            ["Incomplete results"],
        )

        self.assertFalse(hasattr(proposal, "execute"))
        self.assertFalse(hasattr(proposal, "approve"))
        self.assertFalse(hasattr(proposal, "run"))

    def test_whitespace_normalization(self):
        proposal = create_action_proposal(
            "  Review tests  ",
            "  Improve reliability  ",
            ["  Incomplete results  "],
        )

        self.assertEqual(proposal.action, "Review tests")
        self.assertEqual(
            proposal.justification,
            "Improve reliability",
        )
        self.assertEqual(
            proposal.risks,
            ("Incomplete results",),
        )


if __name__ == "__main__":
    unittest.main()
