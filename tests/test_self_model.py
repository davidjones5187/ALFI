import unittest

from self_model import operational_snapshot


class SelfModelTests(unittest.TestCase):

    def test_identity_and_runtime(self):
        snapshot = operational_snapshot("gemma3:4b")
        self.assertEqual(snapshot["identity"]["name"], "A.L.F.I.")
        self.assertEqual(snapshot["runtime"]["model"], "gemma3:4b")
        self.assertEqual(snapshot["runtime"]["inference"], "ollama")

    def test_autonomy_targets_are_not_active(self):
        snapshot = operational_snapshot("gemma3:4b")
        for capability in ("planning", "initiative"):
            state = snapshot["autonomy"][capability]
            self.assertFalse(state["available"])
            self.assertFalse(state["enabled"])
            self.assertTrue(state["target"])
        self.assertEqual(
            snapshot["autonomy"]["tool_execution"], "supervised"
        )

    def test_disabled_inference(self):
        snapshot = operational_snapshot("gemma3:4b", use_ollama=False)
        self.assertIsNone(snapshot["runtime"]["model"])
        self.assertEqual(snapshot["runtime"]["inference"], "disabled")

    def test_snapshot_mutation_isolation(self):
        snapshot = operational_snapshot("gemma3:4b")
        snapshot["autonomy"]["planning"]["enabled"] = True
        snapshot["capabilities"].clear()

        fresh = operational_snapshot("gemma3:4b")
        self.assertFalse(fresh["autonomy"]["planning"]["enabled"])
        self.assertIn("conversation", fresh["capabilities"])


    def test_cli_status_disabled_inference(self):
        import io
        import tempfile
        from contextlib import redirect_stdout
        from pathlib import Path
        from unittest.mock import patch

        import first_ai

        with tempfile.TemporaryDirectory() as folder:
            memory_file = Path(folder) / "memory.json"
            ai = first_ai.ALFI(
                memory_file=memory_file,
                use_ollama=False,
                ollama_model="test-model:1b",
            )
            output = io.StringIO()

            with (
                patch.object(first_ai, "ALFI", return_value=ai),
                patch("builtins.input", side_effect=["/status", "/quit"]),
                redirect_stdout(output),
            ):
                first_ai.main()

            result = output.getvalue()
            self.assertIn("Identity: A.L.F.I.", result)
            self.assertIn("Configured model: disabled", result)
            self.assertIn("Inference: disabled", result)
            self.assertIn("Planning: not implemented", result)
            self.assertIn("Initiative: not implemented", result)
            self.assertIn("Tool execution: supervised", result)

            self.assertFalse(memory_file.exists())
            self.assertFalse((Path(folder) / "conversation_history.json").exists())
            self.assertFalse((Path(folder) / "structured_memory.json").exists())

    def test_cli_status_model_override_without_network(self):
        import io
        import tempfile
        from contextlib import redirect_stdout
        from pathlib import Path
        from unittest.mock import patch

        import first_ai

        with tempfile.TemporaryDirectory() as folder:
            ai = first_ai.ALFI(
                memory_file=Path(folder) / "memory.json",
                use_ollama=True,
                ollama_model="test-model:1b",
            )
            output = io.StringIO()

            with (
                patch.object(first_ai, "ALFI", return_value=ai),
                patch("builtins.input", side_effect=["/status", "/quit"]),
                patch("first_ai.urllib.request.urlopen") as network,
                redirect_stdout(output),
            ):
                first_ai.main()

            result = output.getvalue()
            self.assertIn("Configured model: test-model:1b", result)
            self.assertIn("Inference: ollama", result)
            self.assertIn("Planning: not implemented", result)
            self.assertIn("Initiative: not implemented", result)
            network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
