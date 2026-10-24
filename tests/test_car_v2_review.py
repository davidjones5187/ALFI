import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from experiments.car_v2_review import ReviewedCARPilot


class CARReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "review.sqlite3"
        self.ai = ReviewedCARPilot(self.path)
        self.addCleanup(self.ai.close)
        self.auth = patch.dict(os.environ, {"ALFI_CAR_REVIEWER_SHA256":
                              hashlib.sha256(b"local-test-secret").hexdigest()})
        self.auth.start()
        self.addCleanup(self.auth.stop)

    def proposal(self, key="memory", lesson="Use the corrected value"):
        return self.ai.propose(topic_key=key, context="Correction received",
                               goal="Accurate recall", action="Old response",
                               result="Corrected", evidence=["case-1"],
                               correction="New value", lesson=lesson)

    def test_approval_and_exact_retrieval(self):
        eid = self.proposal()
        self.assertEqual(self.ai.retrieved_lessons("memory"), [])
        self.ai.confirm(eid, reviewer_token="local-test-secret")
        self.assertEqual(self.ai.retrieved_lessons("memory")[0]["id"], eid)
        self.assertEqual(self.ai.retrieved_lessons("other"), [])

    def test_wrong_or_missing_credential_denied(self):
        eid = self.proposal()
        with self.assertRaises(PermissionError):
            self.ai.confirm(eid, reviewer_token="wrong")
        with patch.dict(os.environ, {"ALFI_CAR_REVIEWER_SHA256": ""}):
            with self.assertRaises(PermissionError):
                self.ai.confirm(eid, reviewer_token="local-test-secret")
        self.assertEqual(self.ai.get(eid)["status"], "unverified")

    def test_explicit_supersession(self):
        old = self.proposal(lesson="Old lesson")
        self.ai.confirm(old, reviewer_token="local-test-secret")
        new = self.proposal(lesson="Corrected lesson")
        with self.assertRaises(ValueError):
            self.ai.confirm(new, reviewer_token="local-test-secret")
        self.ai.confirm(new, reviewer_token="local-test-secret", supersedes_id=old)
        self.assertEqual(self.ai.get(old)["status"], "superseded")
        self.assertEqual([x["id"] for x in self.ai.retrieved_lessons("memory")], [new])

    def test_restart_retains_approved_only(self):
        eid = self.proposal()
        self.ai.confirm(eid, reviewer_token="local-test-secret")
        second = ReviewedCARPilot(self.path)
        try:
            self.assertEqual(second.retrieved_lessons("memory")[0]["id"], eid)
        finally:
            second.close()

    def test_scope_isolation(self):
        eid = self.proposal()
        self.ai.confirm(eid, reviewer_token="local-test-secret")
        other = ReviewedCARPilot(self.path, scope="other")
        try:
            self.assertEqual(other.retrieved_lessons("memory"), [])
        finally:
            other.close()

    def test_invalid_topic_key_rejected(self):
        with self.assertRaises(ValueError):
            self.proposal(key="../memory")
        self.assertEqual(self.ai.candidates(), [])


if __name__ == "__main__":
    unittest.main()
