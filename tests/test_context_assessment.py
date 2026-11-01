"""Focused tests for A.L.F.I. 2.0 context assessment."""

import unittest
from dataclasses import FrozenInstanceError

from context_assessment import assess_context


class ContextAssessmentTests(unittest.TestCase):

    def test_complete(self):
        result = assess_context(
            ["framework"],
            [{"field": "framework", "value": "unittest",
              "source": "maintainer"}],
        )
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.missing, ())
        self.assertEqual(result.conflicts, ())

    def test_missing_field(self):
        result = assess_context(["framework", "version"], [
            {"field": "framework", "value": "unittest",
             "source": "maintainer"}
        ])
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(result.missing, ("version",))

    def test_empty_information(self):
        result = assess_context(["framework"], [])
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(result.missing, ("framework",))

    def test_explicit_conflict(self):
        result = assess_context(["framework"], [
            {"field": "framework", "value": "unittest",
             "source": "maintainer"},
            {"field": "framework", "value": "pytest",
             "source": "reviewer"},
        ])
        self.assertEqual(result.status, "conflicting")
        self.assertEqual(len(result.conflicts), 1)
        self.assertEqual(result.conflicts[0].field, "framework")
        self.assertEqual(
            [item.value for item in result.conflicts[0].entries],
            ["unittest", "pytest"],
        )

    def test_conflict_preserves_sources(self):
        result = assess_context([], [
            {"field": "framework", "value": "unittest",
             "source": "maintainer"},
            {"field": "framework", "value": "pytest",
             "source": "reviewer"},
        ])
        self.assertEqual(
            [item.source for item in result.conflicts[0].entries],
            ["maintainer", "reviewer"],
        )

    def test_same_value_no_conflict(self):
        result = assess_context(["framework"], [
            {"field": "framework", "value": "unittest",
             "source": "maintainer"},
            {"field": "framework", "value": "unittest",
             "source": "reviewer"},
        ])
        self.assertEqual(result.status, "complete")

    def test_missing_and_conflict_prioritizes_conflict(self):
        result = assess_context(["framework", "version"], [
            {"field": "framework", "value": "unittest",
             "source": "maintainer"},
            {"field": "framework", "value": "pytest",
             "source": "reviewer"},
        ])
        self.assertEqual(result.status, "conflicting")
        self.assertEqual(result.missing, ("version",))

    def test_duplicate_required_fields(self):
        result = assess_context(["version", "version"], [])
        self.assertEqual(result.missing, ("version",))

    def test_trims_whitespace(self):
        result = assess_context([" framework "], [
            {"field": " framework ", "value": " unittest ",
             "source": " maintainer "}
        ])
        self.assertEqual(result.status, "complete")

    def test_immutable_result(self):
        result = assess_context([], [])
        with self.assertRaises(FrozenInstanceError):
            result.status = "conflicting"

    def test_immutable_conflict_entries(self):
        result = assess_context([], [
            {"field": "x", "value": "a", "source": "one"},
            {"field": "x", "value": "b", "source": "two"},
        ])
        with self.assertRaises(FrozenInstanceError):
            result.conflicts[0].entries[0].value = "changed"

    def test_rejects_invalid_required_container(self):
        with self.assertRaises(ValueError):
            assess_context("framework", [])

    def test_rejects_invalid_supplied_container(self):
        with self.assertRaises(ValueError):
            assess_context([], "framework")

    def test_rejects_empty_required_field(self):
        with self.assertRaises(ValueError):
            assess_context(["  "], [])

    def test_rejects_non_dictionary_item(self):
        with self.assertRaises(ValueError):
            assess_context([], ["framework"])

    def test_rejects_missing_item_key(self):
        with self.assertRaises(ValueError):
            assess_context([], [{"field": "x", "value": "a"}])

    def test_rejects_extra_item_key(self):
        with self.assertRaises(ValueError):
            assess_context([], [
                {"field": "x", "value": "a", "source": "s",
                 "verified": True}
            ])

    def test_rejects_empty_item_value(self):
        with self.assertRaises(ValueError):
            assess_context([], [
                {"field": "x", "value": " ", "source": "s"}
            ])

    def test_rejects_empty_source(self):
        with self.assertRaises(ValueError):
            assess_context([], [
                {"field": "x", "value": "a", "source": ""}
            ])

    def test_does_not_infer_semantic_equivalence(self):
        result = assess_context(["framework"], [
            {"field": "framework", "value": "unittest",
             "source": "one"},
            {"field": "framework", "value": "Python unittest",
             "source": "two"},
        ])
        self.assertEqual(result.status, "conflicting")


if __name__ == "__main__":
    unittest.main()
