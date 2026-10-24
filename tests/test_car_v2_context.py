import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from experiments.car_v2_context import build_car_context
from experiments.car_v2_review import ReviewedCARPilot


class CARContextGateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = ReviewedCARPilot(Path(tmp.name) / "context.sqlite3")
        self.addCleanup(self.db.close)
        self.secret = "test-only"
        p = patch.dict(os.environ, {"ALFI_CAR_REVIEWER_SHA256":
                       hashlib.sha256(self.secret.encode()).hexdigest()})
        p.start()
        self.addCleanup(p.stop)

    def add(self, topic, lesson, approve=True, supersedes_id=None):
        eid = self.db.propose(topic_key=topic, context="Case", goal="Correct response",
                              action="Answered", result="Reviewed", evidence=["case:1"],
                              lesson=lesson)
        if approve:
            self.db.confirm(eid, reviewer_token=self.secret, supersedes_id=supersedes_id)
        return eid

    def test_disabled_is_empty(self):
        self.add("project", "Use accepted milestone")
        self.assertEqual(build_car_context(self.db, "project"), "")

    def test_approved_only_and_topic_isolation(self):
        self.add("project", "Use accepted milestone")
        self.add("project", "Unreviewed draft", approve=False)
        self.add("weather", "Rain tomorrow")
        output = build_car_context(self.db, "project", enabled=True)
        self.assertIn("Use accepted milestone", output)
        self.assertNotIn("Unreviewed draft", output)
        self.assertNotIn("Rain tomorrow", output)

    def test_superseded_excluded(self):
        old = self.add("project", "Old value")
        self.add("project", "Corrected value", supersedes_id=old)
        output = build_car_context(self.db, "project", enabled=True)
        self.assertIn("Corrected value", output)
        self.assertNotIn("Old value", output)

    def test_bounded_output(self):
        self.add("project", "A" * 1800)
        self.assertEqual(build_car_context(self.db, "project", enabled=True, max_chars=200), "")

    def test_invalid_key_is_empty(self):
        self.add("project", "Valid")
        self.assertEqual(build_car_context(self.db, "../project", enabled=True), "")

    def test_restart_and_scope_isolation(self):
        self.add("project", "Persisted guidance")
        second = ReviewedCARPilot(self.db.path, scope="other")
        self.addCleanup(second.close)
        self.assertEqual(build_car_context(second, "project", enabled=True), "")
        third = ReviewedCARPilot(self.db.path)
        self.addCleanup(third.close)
        self.assertIn("Persisted guidance",
                      build_car_context(third, "project", enabled=True))

    def test_reviewer_guidance_not_claimed_as_fact(self):
        self.add("project", "Use reviewed decision")
        result = build_car_context(self.db, "project", enabled=True)
        self.assertIn("not independently verified facts", result)


if __name__ == "__main__":
    unittest.main()
