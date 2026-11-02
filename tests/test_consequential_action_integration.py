"""Mocked integration tests for supervised action classification."""

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


class TestConsequentialActionIntegration(unittest.TestCase):
    def model_messages(self, message):
        captured = []

        def fake_open(request, timeout):
            captured.append(json.loads(request.data.decode("utf-8")))
            return FakeResponse()

        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "ai_memory.json")
            with patch(
                "first_ai.urllib.request.urlopen",
                side_effect=fake_open,
            ):
                ai.generate(message)

        self.assertEqual(len(captured), 1)
        return captured[0]["messages"]

    def system_messages(self, message):
        return [
            item["content"]
            for item in self.model_messages(message)
            if item["role"] == "system"
        ]

    def test_explicit_request_requires_approval_guidance(self):
        system = self.system_messages("Delete the obsolete file.")
        self.assertTrue(any(
            "human approval is required" in content
            for content in system
        ))
        self.assertTrue(any(
            "Do not execute" in content
            for content in system
        ))

    def test_second_sentence_request(self):
        system = self.system_messages(
            "I think this file is obsolete. Delete it."
        )
        self.assertTrue(any(
            "human approval is required" in content
            for content in system
        ))
        self.assertTrue(any(
            "verifying the uncertain assumption" in content
            for content in system
        ))

    def test_discussion_does_not_authorize(self):
        system = self.system_messages("Should I delete the file?")
        self.assertTrue(any(
            "without treating the question" in content
            for content in system
        ))
        self.assertFalse(any(
            "human approval is required" in content
            for content in system
        ))

    def test_ordinary_message_preserved(self):
        messages = self.model_messages("Hello!")
        self.assertEqual(messages[-1], {
            "role": "user",
            "content": "Hello!",
        })
        self.assertFalse(any(
            "recognized consequential-action request" in item["content"]
            for item in messages
            if item["role"] == "system"
        ))

    def test_unknown_message_not_authorized(self):
        system = self.system_messages("Transfer the money.")
        self.assertFalse(any(
            "human approval is required" in content
            for content in system
        ))


if __name__ == "__main__":
    unittest.main()
