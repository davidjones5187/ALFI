"""Mocked integration checks for supervised uncertainty guidance."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from first_ai import ALFI


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, *args):
        return b'{"message": {"content": "Acknowledged."}}'


class TestUncertaintyIntegration(unittest.TestCase):
    def model_messages(self, message):
        captured = []

        def fake_open(request, timeout):
            captured.append(json.loads(request.data.decode("utf-8")))
            return FakeResponse()

        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "ai_memory.json")
            with patch("first_ai.urllib.request.urlopen", side_effect=fake_open):
                ai.generate(message)

        self.assertEqual(len(captured), 1)
        return captured[0]["messages"]

    def test_explicit_uncertainty_adds_guidance(self):
        messages = self.model_messages("I think the schedule is correct.")
        system = [
            item["content"] for item in messages
            if item["role"] == "system"
        ]
        self.assertIn(
            "Acknowledge the stated uncertainty without claiming independent verification.",
            system,
        )

    def test_definite_statement_does_not_add_guidance(self):
        messages = self.model_messages("The schedule is correct.")
        system = [
            item["content"] for item in messages
            if item["role"] == "system"
        ]
        self.assertNotIn(
            "Acknowledge the stated uncertainty without claiming independent verification.",
            system,
        )

    def test_existing_policy_and_user_message_preserved(self):
        messages = self.model_messages("Maybe the schedule changed.")
        self.assertEqual(messages[-1], {
            "role": "user",
            "content": "Maybe the schedule changed.",
        })
        self.assertTrue(any(
            item["role"] == "system"
            and "Acknowledge the stated uncertainty" in item["content"]
            for item in messages
        ))


if __name__ == "__main__":
    unittest.main()
