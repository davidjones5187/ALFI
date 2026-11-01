"""Tests for explicitly supplied A.L.F.I. task context."""

import unittest
from dataclasses import FrozenInstanceError

from verified_context import create_verified_context


class VerifiedContextTests(unittest.TestCase):

    def test_valid_fact(self):
        context = create_verified_context([
            {"statement": "Tests use unittest", "source": "User"}
        ])
        self.assertEqual(context.facts[0].statement, "Tests use unittest")
        self.assertEqual(context.facts[0].source, "User")

    def test_multiple_facts(self):
        context = create_verified_context([
            {"statement": "Tests use unittest", "source": "User"},
            {"statement": "Ollama is local", "source": "User"},
        ])
        self.assertEqual(len(context.facts), 2)

    def test_whitespace_normalization(self):
        context = create_verified_context([
            {"statement": "  Tests use unittest  ", "source": " User "}
        ])
        self.assertEqual(context.facts[0].statement, "Tests use unittest")
        self.assertEqual(context.facts[0].source, "User")

    def test_immutable_context(self):
        context = create_verified_context([
            {"statement": "Tests use unittest", "source": "User"}
        ])
        with self.assertRaises(FrozenInstanceError):
            context.facts = ()

    def test_immutable_fact(self):
        context = create_verified_context([
            {"statement": "Tests use unittest", "source": "User"}
        ])
        with self.assertRaises(FrozenInstanceError):
            context.facts[0].statement = "Changed"

    def test_empty_facts_rejected(self):
        with self.assertRaises(ValueError):
            create_verified_context([])

    def test_invalid_container_rejected(self):
        with self.assertRaises(ValueError):
            create_verified_context("Tests use unittest")

    def test_missing_source_rejected(self):
        with self.assertRaises(ValueError):
            create_verified_context([
                {"statement": "Tests use unittest"}
            ])

    def test_empty_source_rejected(self):
        with self.assertRaises(ValueError):
            create_verified_context([
                {"statement": "Tests use unittest", "source": " "}
            ])

    def test_empty_statement_rejected(self):
        with self.assertRaises(ValueError):
            create_verified_context([
                {"statement": " ", "source": "User"}
            ])

    def test_extra_fields_rejected(self):
        with self.assertRaises(ValueError):
            create_verified_context([
                {
                    "statement": "Tests use unittest",
                    "source": "User",
                    "approved": True,
                }
            ])

    def test_nondictionary_fact_rejected(self):
        with self.assertRaises(ValueError):
            create_verified_context(["Tests use unittest"])


if __name__ == "__main__":
    unittest.main()
