"""Tests for advisory consequential-action classification."""

import unittest

from consequential_action_classification import (
    classify_consequential_action,
)


class ConsequentialActionClassificationTests(unittest.TestCase):

    def test_explicit_delete_request(self):
        result = classify_consequential_action(
            "Delete the obsolete file."
        )
        self.assertEqual(result.category, "action_request")
        self.assertEqual(result.situation, "consequential_action")
        self.assertTrue(result.requires_approval)

    def test_explicit_send_request(self):
        result = classify_consequential_action(
            "Please send the message."
        )
        self.assertEqual(result.category, "action_request")
        self.assertTrue(result.requires_approval)

    def test_discussion_not_execution(self):
        result = classify_consequential_action(
            "Should I delete the file?"
        )
        self.assertEqual(result.category, "action_discussion")
        self.assertFalse(result.requires_approval)

    def test_ordinary_greeting(self):
        result = classify_consequential_action("Hello!")
        self.assertEqual(result.category, "ordinary")

    def test_ambiguous_statement(self):
        result = classify_consequential_action(
            "I think this file is obsolete."
        )
        self.assertEqual(result.category, "unknown")

    def test_unsupported_request(self):
        result = classify_consequential_action(
            "Transfer the money."
        )
        self.assertEqual(result.category, "unknown")

    def test_no_execution_or_authorization(self):
        result = classify_consequential_action(
            "Overwrite the configuration."
        )
        self.assertTrue(result.requires_approval)
        self.assertFalse(hasattr(result, "execute"))

    def test_request_after_uncertain_statement(self):
        result = classify_consequential_action(
            "I think this file is obsolete. Delete it."
        )
        self.assertEqual(result.category, "action_request")
        self.assertTrue(result.requires_approval)

    def test_polite_request_after_introductory_sentence(self):
        result = classify_consequential_action(
            "Maybe this is outdated. Please remove it."
        )
        self.assertEqual(result.category, "action_request")
        self.assertTrue(result.requires_approval)

    def test_invalid_inputs(self):
        for value in (None, "", "   ", 123):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    classify_consequential_action(value)


if __name__ == "__main__":
    unittest.main()
