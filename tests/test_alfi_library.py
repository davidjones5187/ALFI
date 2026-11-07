import tempfile
import unittest
from pathlib import Path
from alfi_library import Library


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.library = Library(self.root / 'index.sqlite')
        self.doc = self.root / 'example.txt'
        self.doc.write_text('The copper lantern is stored in the east archive.', encoding='utf-8')

    def test_requires_explicit_authorization(self):
        with self.assertRaises(PermissionError):
            self.library.register(self.doc)
        self.assertEqual(self.library.documents(), [])

    def test_registration_and_source_attribution(self):
        self.library.register(self.doc, authorized=True)
        hits = self.library.search('Where is the copper lantern?')
        self.assertTrue(hits)
        self.assertEqual(hits[0]['source'], str(self.doc.resolve()))
        self.assertIn('east archive', hits[0]['passage'])

    def test_no_evidence_for_unknown_topic(self):
        self.library.register(self.doc, authorized=True)
        self.assertEqual(self.library.search('zebrafish'), [])

    def test_reindex_replaces_old_passages(self):
        self.library.register(self.doc, authorized=True)
        self.doc.write_text('The violet compass is in the north vault.', encoding='utf-8')
        self.library.register(self.doc, authorized=True)
        self.assertEqual(self.library.search('copper'), [])
        self.assertTrue(self.library.search('violet'))

    def test_rejects_non_txt(self):
        other = self.root / 'bad.md'
        other.write_text('content')
        with self.assertRaises(ValueError):
            self.library.register(other, authorized=True)


if __name__ == '__main__':
    unittest.main()
