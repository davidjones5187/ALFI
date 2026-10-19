import tempfile
import unittest
from pathlib import Path
from first_ai import ALFI

class MemoryIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ai = ALFI(memory_file=Path(self.temp.name) / "ai_memory.json", use_ollama=False)

    def test_direct_fact_response(self):
        self.ai.structured_memory.put("fact", "development computer", "MacBook Pro M3 Pro with 18 GB unified memory", "explicit /correct")
        response = self.ai.respond("What computer do I use for development?")
        self.assertIn("MacBook Pro M3 Pro with 18 GB unified memory", response)

    def test_provenance_not_verification(self):
        self.ai.structured_memory.put("fact", "development computer", "MacBook Pro", "explicit /correct")
        response = self.ai.respond("What computer do I use for development?")
        self.assertIn("not independently verified", response)

    def test_ambiguous_fact_does_not_guess(self):
        self.ai.structured_memory.put("fact", "development computer", "MacBook Pro")
        self.ai.structured_memory.put("fact", "computer", "Desktop")
        self.assertIsNone(self.ai.direct_memory_answer("What development computer do I use?"))

if __name__ == "__main__":
    unittest.main()
