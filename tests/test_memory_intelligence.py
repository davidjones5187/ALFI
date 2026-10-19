import tempfile
import unittest
from pathlib import Path
from memory_intelligence import MemoryStore

class MemoryIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "structured_memory.json"
        self.store = MemoryStore(self.path)

    def test_classification_and_persistence(self):
        self.store.put("preference", "editor", "VS Code")
        self.assertEqual(MemoryStore(self.path).list_items()[0]["kind"], "preference")

    def test_correction_replaces_instead_of_duplicating(self):
        self.store.put("fact", "project version", "1.4")
        self.store.put("fact", "project version", "1.5")
        self.assertEqual(len(self.store.items), 1)
        self.assertEqual(self.store.items[0]["value"], "1.5")

    def test_retrieval_is_relevant_and_bounded(self):
        self.store.put("fact", "mac hardware", "Apple M3 Pro")
        self.store.put("fact", "favorite color", "blue")
        self.assertEqual(self.store.search("mac hardware", 1)[0]["key"], "mac hardware")
        self.assertEqual(len(self.store.search("mac hardware", 1)), 1)

    def test_forgetting_persists(self):
        self.store.put("instruction", "tone", "Be concise")
        self.assertTrue(self.store.forget("tone"))
        self.assertFalse(self.store.forget("tone"))
        self.assertEqual(MemoryStore(self.path).items, [])

    def test_provenance_and_timestamp(self):
        record = self.store.put("fact", "project", "ALFI", "explicit /remember")
        self.assertEqual(record["source"], "explicit /remember")
        self.assertTrue(record["updated"])

    def test_invalid_entries_rejected(self):
        with self.assertRaises(ValueError):
            self.store.put("unknown", "key", "value")
        with self.assertRaises(ValueError):
            self.store.put("fact", "", "value")

    def test_corrupt_memory_does_not_get_overwritten(self):
        self.path.write_text("invalid JSON")
        with self.assertRaises(ValueError):
            MemoryStore(self.path)

if __name__ == "__main__":
    unittest.main()
