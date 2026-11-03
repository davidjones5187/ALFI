import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from alfi_principles import (
    FOUNDATIONAL_PRINCIPLE,
    GOVERNING_GUIDANCE,
    PRINCIPLE_VERSION,
)
from first_ai import ALFI


class FakeResponse:
    def read(self):
        return json.dumps({
            "message": {"content": "I can propose a plan."}
        }).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FoundationalPrincipleTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.ai = ALFI(
            memory_file=Path(temp.name) / "ai_memory.json",
            use_ollama=True,
        )

    def capture_messages(self, question):
        captured = []

        def fake_urlopen(request, timeout=90):
            payload = json.loads(request.data.decode("utf-8"))
            captured.extend(payload["messages"])
            return FakeResponse()

        with patch(
            "first_ai.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            self.ai.generate(question)

        return captured

    def test_principle_is_versioned(self):
        self.assertEqual(PRINCIPLE_VERSION, "1.0")
        self.assertIn(
            "free to reason and propose",
            FOUNDATIONAL_PRINCIPLE,
        )

    def test_principle_in_model_instructions(self):
        messages = self.capture_messages(
            "What possibilities should we explore?"
        )
        system_text = "\n".join(
            m["content"] for m in messages
            if m["role"] == "system"
        )
        self.assertIn(FOUNDATIONAL_PRINCIPLE, system_text)
        self.assertIn(GOVERNING_GUIDANCE, system_text)

    def test_proposals_do_not_grant_execution_authority(self):
        self.assertIn(
            "does not grant permission to execute",
            GOVERNING_GUIDANCE,
        )
        self.assertIn(
            "required human approval",
            GOVERNING_GUIDANCE,
        )

    def test_action_request_preserves_approval_boundary(self):
        messages = self.capture_messages(
            "Transfer $500 from my bank account."
        )
        system_text = "\n".join(
            m["content"] for m in messages
            if m["role"] == "system"
        )
        self.assertIn(
            "human approval is required before execution",
            system_text,
        )
        self.assertIn(
            "Do not execute or claim to have executed",
            system_text,
        )


if __name__ == "__main__":
    unittest.main()
