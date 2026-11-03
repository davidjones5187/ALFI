import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from first_ai import ALFI


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class MemoryRetrievalParaphraseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.ai = ALFI(
            memory_file=Path(self.temp.name) / "ai_memory.json",
            use_ollama=True,
        )

        self.ai.structured_memory.put(
            "preference",
            "synthetic response format",
            "Concise bullet points",
        )

    def capture_prompt(self, question):
        captured = []

        def fake_urlopen(request, timeout=90):
            payload = json.loads(request.data.decode("utf-8"))
            captured.extend(payload["messages"])

            class Response(FakeResponse):
                def read(self):
                    return json.dumps({
                        "message": {
                            "content": "Synthetic response."
                        }
                    }).encode("utf-8")

            return Response()

        with patch(
            "first_ai.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            self.ai.generate(question)

        return "\\n".join(
            message["content"]
            for message in captured
            if message["role"] == "system"
        )

    def test_rephrased_response_format_retrieved(self):
        prompt = self.capture_prompt(
            "How should you format your replies?"
        )
        self.assertIn("synthetic response format", prompt)
        self.assertIn("Concise bullet points", prompt)

    def test_unrelated_question_excludes_preference(self):
        prompt = self.capture_prompt(
            "What causes thunderstorms?"
        )
        self.assertNotIn("synthetic response format", prompt)
        self.assertNotIn("Concise bullet points", prompt)


if __name__ == "__main__":
    unittest.main()
