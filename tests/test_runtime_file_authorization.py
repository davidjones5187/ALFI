import ast
import builtins
import contextlib
import io
import json
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "first_ai.py"
TREE = ast.parse(SOURCE.read_text(encoding="utf-8"))

NAMES = {
    "inspect_text_file",
    "file_access_policy_allows",
    "guided_inspection",
    "guided_document_qa",
    "guided_summarization",
}

SELECTED = [
    node for node in TREE.body
    if isinstance(node, ast.FunctionDef) and node.name in NAMES
]

assert len(SELECTED) == len(NAMES)


class Decision:
    def __init__(self, decision):
        self.decision = decision


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, *args):
        return b'{"message":{"content":"Test summary."}}'


class FileAuthorizationTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.fixture = Path(self.temp.name) / "sample.txt"
        self.fixture.write_text(
            "A.L.F.I. authorization test.\n",
            encoding="utf-8"
        )

        self.namespace = {
            "Path": Path,
            "json": json,
            "urllib": urllib,
            "REQUIRES_AUTHORIZATION": "REQUIRES_AUTHORIZATION",
        }

        exec(
            compile(
                ast.Module(body=SELECTED, type_ignores=[]),
                "<file-authorization-tests>",
                "exec"
            ),
            self.namespace
        )

        self.ai = SimpleNamespace(
            ollama_model="test-model",
            ollama_url="http://127.0.0.1:1",
        )

    def set_policy(self, decision):
        self.namespace["assess_autonomy"] = (
            lambda activity: Decision(decision)
        )

    def run_workflow(self, name, decision, approved=True):
        self.set_policy(decision)

        responses = iter([
            str(self.fixture),
            "y" if approved else "n",
            "/done",
        ])

        output = io.StringIO()
        requests = []

        def fake_urlopen(request, timeout=None):
            requests.append(request)
            return FakeResponse()

        with (
            patch.object(
                builtins,
                "input",
                side_effect=lambda prompt="": next(responses)
            ),
            patch.object(
                urllib.request,
                "urlopen",
                side_effect=fake_urlopen
            ),
            contextlib.redirect_stdout(output),
        ):
            if name == "guided_inspection":
                self.namespace[name]()
            else:
                self.namespace[name](self.ai)

        return output.getvalue(), requests

    def test_helper_requires_confirmation(self):
        self.set_policy("REQUIRES_AUTHORIZATION")
        self.assertFalse(
            self.namespace["file_access_policy_allows"]()
        )
        self.assertTrue(
            self.namespace["file_access_policy_allows"](
                authorized=True
            )
        )

    def test_helper_rejects_prohibited_policy(self):
        self.set_policy("PROHIBITED")
        self.assertFalse(
            self.namespace["file_access_policy_allows"](
                authorized=True
            )
        )

    def test_helper_rejects_independent_policy(self):
        self.set_policy("INDEPENDENT")
        self.assertFalse(
            self.namespace["file_access_policy_allows"](
                authorized=True
            )
        )

    def test_user_denial_cancels_all_workflows(self):
        for name in (
            "guided_inspection",
            "guided_document_qa",
            "guided_summarization",
        ):
            with self.subTest(workflow=name):
                output, requests = self.run_workflow(
                    name, "REQUIRES_AUTHORIZATION", approved=False
                )
                self.assertIn("canceled", output.lower())
                self.assertEqual(requests, [])

    def test_prohibited_policy_blocks_all_workflows(self):
        for name in (
            "guided_inspection",
            "guided_document_qa",
            "guided_summarization",
        ):
            with self.subTest(workflow=name):
                output, requests = self.run_workflow(
                    name, "PROHIBITED"
                )
                self.assertIn(
                    "blocked by autonomy policy", output
                )
                self.assertEqual(requests, [])

    def test_authorized_inspection(self):
        output, _ = self.run_workflow(
            "guided_inspection", "REQUIRES_AUTHORIZATION"
        )
        self.assertIn("Inspection complete", output)

    def test_authorized_document_qa(self):
        output, _ = self.run_workflow(
            "guided_document_qa", "REQUIRES_AUTHORIZATION"
        )
        self.assertIn("Document loaded", output)

    def test_authorized_summarization(self):
        output, requests = self.run_workflow(
            "guided_summarization", "REQUIRES_AUTHORIZATION"
        )
        self.assertIn("Test summary.", output)
        self.assertEqual(len(requests), 1)


if __name__ == "__main__":
    unittest.main()
