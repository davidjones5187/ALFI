import tempfile
import unittest
from pathlib import Path
from first_ai import ALFI

class TestALFI(unittest.TestCase):
    def test_greeting(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            self.assertEqual(ai.classify("hello")[0], "greeting")
            self.assertEqual(ai.respond("hello"), "Hello! I'm A.L.F.I.")

    def test_unknown_words(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            self.assertIsNone(ai.classify("quasar nebula")[0])

    def test_teaching_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            with self.assertRaises(ValueError):
                ai.teach("new_topic", "", "Answer")
            self.assertNotIn("new_topic", ai.data)

    def test_exact_learned_example(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("project_identity", "what is project inception?", "Phase One.")
            self.assertEqual(ai.respond("What is project inception?"), "Phase One.")

    def test_paraphrase_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("project_identity", "what is project inception?", "First phase.")
            self.assertEqual(ai.respond("Tell me about project inception"), "First phase.")

    def test_followup_uses_topic(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("project_identity", "what is project inception?", "First phase.")
            ai.respond("what is project inception?")
            self.assertIn("First phase.", ai.respond("tell me more"))

    def test_reteach_replaces_answer(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("creator", "who created you", "Original")
            ai.teach("creator", "who created you", "Updated")
            self.assertEqual(ai.respond("who created you"), "Updated")

    def test_learning_persists(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            ai = ALFI(path)
            ai.teach("movies", "favorite movie", "Let's talk movies.")
            self.assertEqual(ALFI(path).data["movies"]["responses"], ["Let's talk movies."])

if __name__ == "__main__":
    unittest.main()
