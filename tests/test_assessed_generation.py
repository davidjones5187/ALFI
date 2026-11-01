"""Tests for A.L.F.I. 2.0 supervised proposal generation."""

import unittest
from unittest.mock import patch

from action_proposals import create_action_proposal
from proposal_assessment import generate_assessed_proposal
from verified_context import create_verified_context


class AssessedGenerationTests(unittest.TestCase):

    def setUp(self):
        self.items = [
            {"field": "framework", "value": "unittest",
             "source": "maintainer"}
        ]
        self.proposal = create_action_proposal(
            "Review test coverage",
            "Identify gaps before changing tests",
            ["Coverage information may be incomplete"],
        )

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_missing_information_blocks_model(self, mocked):
        readiness, proposal = generate_assessed_proposal(
            "Improve tests",
            ["framework", "python_version"],
            self.items,
        )
        self.assertFalse(readiness.ready)
        self.assertEqual(
            readiness.assessment.missing,
            ("python_version",),
        )
        self.assertIsNone(proposal)
        mocked.assert_not_called()

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_conflict_blocks_model(self, mocked):
        items = self.items + [
            {"field": "framework", "value": "pytest",
             "source": "reviewer"}
        ]
        readiness, proposal = generate_assessed_proposal(
            "Improve tests", ["framework"], items
        )
        self.assertFalse(readiness.ready)
        self.assertEqual(
            readiness.assessment.status, "conflicting"
        )
        self.assertIsNone(proposal)
        mocked.assert_not_called()

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_missing_and_conflict_block_model(self, mocked):
        items = self.items + [
            {"field": "framework", "value": "pytest",
             "source": "reviewer"}
        ]
        readiness, proposal = generate_assessed_proposal(
            "Improve tests",
            ["framework", "python_version"],
            items,
        )
        self.assertFalse(readiness.ready)
        self.assertEqual(
            readiness.assessment.missing,
            ("python_version",),
        )
        self.assertEqual(
            len(readiness.assessment.conflicts), 1
        )
        self.assertIsNone(proposal)
        mocked.assert_not_called()

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_complete_information_calls_model(self, mocked):
        mocked.return_value = self.proposal
        readiness, proposal = generate_assessed_proposal(
            "Improve tests",
            ["framework"],
            self.items,
            model="test-model",
        )
        self.assertTrue(readiness.ready)
        self.assertIs(proposal, self.proposal)
        mocked.assert_called_once_with(
            "Improve tests",
            context=None,
            model="test-model",
        )

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_verified_context_forwarded(self, mocked):
        mocked.return_value = self.proposal
        context = create_verified_context([
            {"statement": "Tests use unittest",
             "source": "maintainer"}
        ])
        readiness, proposal = generate_assessed_proposal(
            "Improve tests",
            ["framework"],
            self.items,
            context=context,
        )
        self.assertTrue(readiness.ready)
        self.assertIs(proposal, self.proposal)
        self.assertIs(
            mocked.call_args.kwargs["context"],
            context,
        )

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_invalid_objective_rejected_before_model(self, mocked):
        with self.assertRaises(ValueError):
            generate_assessed_proposal(
                "", ["framework"], self.items
            )
        mocked.assert_not_called()

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_invalid_context_rejected_before_model(self, mocked):
        with self.assertRaises(ValueError):
            generate_assessed_proposal(
                "Improve tests",
                ["framework"],
                self.items,
                context={"untrusted": "data"},
            )
        mocked.assert_not_called()

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_invalid_structured_data_rejected(self, mocked):
        with self.assertRaises(ValueError):
            generate_assessed_proposal(
                "Improve tests",
                ["framework"],
                [{"field": "framework", "value": "",
                  "source": "maintainer"}],
            )
        mocked.assert_not_called()

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_generated_proposal_still_requires_approval(self, mocked):
        mocked.return_value = self.proposal
        readiness, proposal = generate_assessed_proposal(
            "Improve tests", ["framework"], self.items
        )
        self.assertTrue(readiness.ready)
        self.assertTrue(proposal.requires_approval)
        self.assertEqual(proposal.status, "proposed")
        self.assertFalse(hasattr(proposal, "execute"))

    @patch("proposal_assessment.generate_model_action_proposal")
    def test_model_failure_propagates_without_execution(self, mocked):
        mocked.side_effect = OSError("Ollama unavailable")
        with self.assertRaises(OSError):
            generate_assessed_proposal(
                "Improve tests", ["framework"], self.items
            )
        mocked.assert_called_once()


if __name__ == "__main__":
    unittest.main()
