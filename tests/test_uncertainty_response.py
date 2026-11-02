"""Tests for isolated context-sensitive uncertainty responses."""

import unittest
from dataclasses import FrozenInstanceError

from uncertainty_response import recommend_uncertainty_response


class UncertaintyResponseTests(unittest.TestCase):

    def test_ordinary_uncertainty(self):
        result = recommend_uncertainty_response(
            "Maybe the backup completed.",
            "ordinary",
        )
        self.assertEqual(result.recommendation, "acknowledge")
        self.assertTrue(result.uncertainty_detected)

    def test_ordinary_definite_statement(self):
        result = recommend_uncertainty_response(
            "The backup completed.",
            "ordinary",
        )
        self.assertEqual(result.recommendation, "respond")
        self.assertFalse(result.uncertainty_detected)

    def test_missing_information_with_uncertainty(self):
        result = recommend_uncertainty_response(
            "I think the date was Tuesday.",
            "missing_information",
        )
        self.assertEqual(result.recommendation, "clarify")

    def test_missing_information_without_uncertainty(self):
        result = recommend_uncertainty_response(
            "Please schedule the meeting.",
            "missing_information",
        )
        self.assertEqual(result.recommendation, "clarify")

    def test_consequential_uncertainty(self):
        result = recommend_uncertainty_response(
            "I think the backup completed.",
            "consequential_action",
        )
        self.assertEqual(result.recommendation, "verify")
        self.assertIn("Do not execute", result.guidance)

    def test_consequential_without_explicit_uncertainty(self):
        result = recommend_uncertainty_response(
            "The backup completed.",
            "consequential_action",
        )
        self.assertEqual(result.recommendation, "respond")

    def test_expression_preserved(self):
        result = recommend_uncertainty_response(
            "Perhaps the server restarted.",
            "ordinary",
        )
        self.assertEqual(result.expression, "perhaps")

    def test_invalid_situation(self):
        for situation in ("", "unknown", None, 42):
            with self.subTest(situation=situation):
                with self.assertRaises(ValueError):
                    recommend_uncertainty_response(
                        "Maybe it worked.",
                        situation,
                    )

    def test_invalid_message(self):
        for message in ("", None, 42):
            with self.subTest(message=message):
                with self.assertRaises(ValueError):
                    recommend_uncertainty_response(
                        message,
                        "ordinary",
                    )

    def test_immutable_result(self):
        result = recommend_uncertainty_response(
            "Maybe it worked.",
            "ordinary",
        )
        with self.assertRaises(FrozenInstanceError):
            result.recommendation = "verify"


if __name__ == "__main__":
    unittest.main()
