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

    def test_learning_persists(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            ai = ALFI(path)
            ai.teach("movies", "favorite movie", "Let's talk movies.")
            self.assertEqual(ALFI(path).data["movies"]["responses"], ["Let's talk movies."])

if __name__ == "__main__":
    unittest.main()
