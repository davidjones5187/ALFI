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


if __name__ == "__main__":
    unittest.main()
