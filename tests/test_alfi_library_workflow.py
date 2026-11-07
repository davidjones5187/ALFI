import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from alfi_library_workflow import guided_library_qa


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'library.sqlite3'
        self.doc = Path(self.temp.name) / 'sample.txt'
        self.doc.write_text('The project milestone is L-2.\n', encoding='utf-8')
        self.ai = SimpleNamespace(use_ollama=False, ollama_model='test', ollama_url='http://localhost')

    def run_session(self, responses, allowed=True):
        prompts = iter(responses)
        output = []
        guided_library_qa(self.ai, database=self.db, input_fn=lambda _: next(prompts),
                          output_fn=output.append, policy_allows=lambda authorized: allowed and authorized)
        return '\n'.join(output)

    def test_denial_does_not_create_index(self):
        result = self.run_session(['add', str(self.doc), 'n', 'done'])
        self.assertIn('canceled', result)
        self.assertFalse(self.db.exists())

    def test_policy_blocks_registration(self):
        result = self.run_session(['add', str(self.doc), 'y', 'done'], allowed=False)
        self.assertIn('blocked', result)
        self.assertFalse(self.db.exists())

    def test_authorized_registration_and_listing(self):
        result = self.run_session(['add', str(self.doc), 'y', 'list', 'done'])
        self.assertIn('Registered document', result)
        self.assertIn(str(self.doc), result)

    def test_search_without_model_displays_attribution(self):
        result = self.run_session(['add', str(self.doc), 'y', 'ask', 'milestone', 'done'])
        self.assertIn('Candidate passages', result)
        self.assertIn(str(self.doc), result)
        self.assertIn('Model unavailable', result)

    def test_no_evidence_does_not_call_model(self):
        result = self.run_session(['add', str(self.doc), 'y', 'ask', 'quasar', 'done'])
        self.assertIn('No supporting passages', result)

    def test_existing_index_can_be_listed_without_source_read(self):
        self.run_session(['add', str(self.doc), 'y', 'done'])
        self.doc.unlink()
        result = self.run_session(['list', 'done'])
        self.assertIn(str(self.doc), result)


if __name__ == '__main__':
    unittest.main()
