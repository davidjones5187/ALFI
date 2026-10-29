"""Regression tests for A.L.F.I.'s proposal-only planner."""

import unittest
from dataclasses import FrozenInstanceError

from planning import create_plan


class PlanningTests(unittest.TestCase):

    def test_structured_proposal(self):
        plan = create_plan(
            "Improve memory retrieval",
            [
                "Inspect current retrieval",
                "Measure retrieval accuracy",
                "Propose an improvement",
            ],
            assumptions=("Existing memory remains unchanged",),
            uncertainties=("Accuracy has not been measured",),
        )

        self.assertEqual(plan.objective, "Improve memory retrieval")
        self.assertEqual(plan.status, "proposed")
        self.assertEqual(len(plan.steps), 3)
        self.assertEqual([s.number for s in plan.steps], [1, 2, 3])
        self.assertTrue(all(s.requires_approval for s in plan.steps))
        self.assertEqual(
            plan.assumptions,
            ("Existing memory remains unchanged",),
        )
        self.assertEqual(len(plan.uncertainties), 1)

    def test_invalid_objective(self):
        with self.assertRaises(ValueError):
            create_plan("", ["Inspect memory"])

    def test_missing_steps(self):
        with self.assertRaises(ValueError):
            create_plan("Improve memory", [])

    def test_empty_step(self):
        with self.assertRaises(ValueError):
            create_plan("Improve memory", [""])

    def test_immutable_steps(self):
        plan = create_plan("Inspect memory", ["Review retrieval"])

        with self.assertRaises(FrozenInstanceError):
            plan.steps[0].description = "Execute without approval"

    def test_no_execution_interface(self):
        plan = create_plan("Inspect memory", ["Review retrieval"])

        self.assertFalse(hasattr(plan, "execute"))
        self.assertFalse(hasattr(plan, "run"))


    def test_metadata_validation(self):
        invalid_cases = [
            {"assumptions": "single string"},
            {"uncertainties": "single string"},
            {"assumptions": [""]},
            {"uncertainties": ["   "]},
            {"assumptions": [None]},
            {"uncertainties": [42]},
            {"assumptions": {"unexpected": "mapping"}},
            {"uncertainties": None},
        ]

        for metadata in invalid_cases:
            with self.subTest(metadata=metadata):
                with self.assertRaises(ValueError):
                    create_plan("Inspect memory", ["Review retrieval"], **metadata)

    def test_metadata_whitespace_normalization(self):
        plan = create_plan(
            "Inspect memory",
            ["Review retrieval"],
            assumptions=["  Existing records are preserved  "],
            uncertainties=("  Retrieval accuracy is unknown  ",),
        )

        self.assertEqual(
            plan.assumptions,
            ("Existing records are preserved",),
        )
        self.assertEqual(
            plan.uncertainties,
            ("Retrieval accuracy is unknown",),
        )

    def test_metadata_immutable(self):
        plan = create_plan(
            "Inspect memory",
            ["Review retrieval"],
            assumptions=["Existing records are preserved"],
        )

        with self.assertRaises(FrozenInstanceError):
            plan.assumptions = ("Changed assumption",)


if __name__ == "__main__":
    unittest.main()
