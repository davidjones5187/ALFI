import json
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from first_ai import ALFI


class ConversationalPrecisionTests(unittest.TestCase):
    def capture_prompt(self, question):
        captured = []

        def fake_urlopen(request, *args, **kwargs):
            payload = json.loads(
                request.data.decode("utf-8")
            )
            captured.append(payload)
            raise urllib.error.URLError(
                "Intentional test interception"
            )

        with tempfile.TemporaryDirectory() as directory:
            ai = ALFI(
                memory_file=Path(directory) / "ai_memory.json"
            )
            with patch(
                "urllib.request.urlopen",
                side_effect=fake_urlopen,
            ):
                ai.respond(question)

        self.assertTrue(
            captured,
            "No Ollama request was captured.",
        )
        return captured[0]["messages"]

    def system_text(self, question):
        messages = self.capture_prompt(question)
        return " ".join(
            item["content"]
            for item in messages
            if item["role"] == "system"
        )

    def test_unrelated_question_omits_date(self):
        text = self.system_text(
            "What color is the Orion crystal?"
        )
        self.assertNotIn(
            "Current local date (from the host computer):",
            text,
        )

    def test_explicit_date_question_includes_date(self):
        text = self.system_text(
            "What is today's date?"
        )
        self.assertIn(
            "Current local date (from the host computer):",
            text,
        )

    def test_current_year_question_includes_date(self):
        text = self.system_text(
            "What is the current year?"
        )
        self.assertIn(
            "Current local date (from the host computer):",
            text,
        )

    def test_missing_information_omits_date(self):
        text = self.system_text(
            "What is the unknown serial number?"
        )
        self.assertNotIn(
            "Current local date (from the host computer):",
            text,
        )

    def test_reasoning_question_omits_date(self):
        text = self.system_text(
            "Would solar power work in a dark cave?"
        )
        self.assertNotIn(
            "Current local date (from the host computer):",
            text,
        )


if __name__ == "__main__":
    unittest.main()
