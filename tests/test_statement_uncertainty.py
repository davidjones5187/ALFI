"""Tests for isolated explicit uncertainty recognition."""

import unittest
from dataclasses import FrozenInstanceError

from statement_uncertainty import assess_statement_uncertainty


class StatementUncertaintyTests(unittest.TestCase):

    def test_i_think(self):
        result = assess_statement_uncertainty(
            "I think the backup completed."
        )
        self.assertTrue(result.detected)
        self.assertEqual(result.expression, "i think")

    def test_maybe(self):
        result = assess_statement_uncertainty(
            "Maybe the server restarted."
        )
        self.assertTrue(result.detected)
        self.assertEqual(result.expression, "maybe")

    def test_not_sure(self):
        result = assess_statement_uncertainty(
            "I'm not sure the files were saved."
        )
        self.assertTrue(result.detected)
        self.assertEqual(result.expression, "not sure")

    def test_uncertain_belief(self):
        result = assess_statement_uncertainty(
            "I believe the process finished."
        )
        self.assertTrue(result.detected)

    def test_possibly(self):
        self.assertTrue(
            assess_statement_uncertainty(
                "The backup possibly completed."
            ).detected
        )

    def test_might(self):
        self.assertTrue(
            assess_statement_uncertainty(
                "The server might be offline."
            ).detected
        )

    def test_definite_statement(self):
        result = assess_statement_uncertainty(
            "The backup completed."
        )
        self.assertFalse(result.detected)
        self.assertIsNone(result.expression)

    def test_ordinary_question(self):
        result = assess_statement_uncertainty(
            "Explain how backups work."
        )
        self.assertFalse(result.detected)

    def test_case_insensitive(self):
        result = assess_statement_uncertainty(
            "MAYBE the server restarted."
        )
        self.assertTrue(result.detected)

    def test_word_boundaries(self):
        result = assess_statement_uncertainty(
            "The word maybeish is not a qualifier."
        )
        self.assertFalse(result.detected)

    def test_earliest_expression(self):
        result = assess_statement_uncertainty(
            "Perhaps it worked, but I think it failed."
        )
        self.assertEqual(result.expression, "perhaps")

    def test_invalid_type(self):
        for value in (None, 42, [], {}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    assess_statement_uncertainty(value)

    def test_empty_message(self):
        for value in ("", "   "):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    assess_statement_uncertainty(value)

    def test_immutable_result(self):
        result = assess_statement_uncertainty("Maybe.")
        with self.assertRaises(FrozenInstanceError):
            result.detected = False


if __name__ == "__main__":
    unittest.main()
