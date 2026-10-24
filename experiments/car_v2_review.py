"""Operator-gated CAR review layer. Opt-in only; never used by ALFI runtime."""
import hashlib
import hmac
import os
import re
from experiments.car_v2_pilot import CARPilot


class ReviewedCARPilot(CARPilot):
    def __init__(self, database_path, scope="alfi-car-pilot"):
        super().__init__(database_path, scope)
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(experiences)")}
        for name, sql_type in (("topic_key", "TEXT"), ("supersedes_id", "INTEGER")):
            if name not in columns:
                self.db.execute(f"ALTER TABLE experiences ADD COLUMN {name} {sql_type}")
        self.db.commit()

    def propose(self, *, topic_key, **kwargs):
        if not isinstance(topic_key, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", topic_key):
            raise ValueError("Explicit lowercase topic key required")
        with self.db:
            eid = super().propose(**kwargs)
            self.db.execute("UPDATE experiences SET topic_key=? WHERE id=? AND scope=?",
                            (topic_key, eid, self.scope))
        return eid

    def confirm(self, experience_id, *, reviewer_token, supersedes_id=None):
        expected = os.environ.get("ALFI_CAR_REVIEWER_SHA256", "")
        if not re.fullmatch(r"[a-f0-9]{64}", expected):
            raise PermissionError("Operator credential not configured")
        if not isinstance(reviewer_token, str) or not hmac.compare_digest(
            hashlib.sha256(reviewer_token.encode()).hexdigest(), expected
        ):
            raise PermissionError("Operator authorization failed")
        with self.db:
            row = self.db.execute("SELECT * FROM experiences WHERE id=? AND scope=?",
                                  (experience_id, self.scope)).fetchone()
            if row is None or row["status"] != "unverified" or not row["lesson"] or not row["topic_key"]:
                raise ValueError("Only keyed unverified lessons may be approved")
            prior = self.db.execute(
                "SELECT id FROM experiences WHERE scope=? AND topic_key=? AND status='approved'",
                (self.scope, row["topic_key"])).fetchall()
            if prior:
                if len(prior) != 1 or prior[0]["id"] != supersedes_id:
                    raise ValueError("Explicit approved predecessor required")
                self.db.execute("UPDATE experiences SET status='superseded' "
                                "WHERE id=? AND scope=? AND status='approved'",
                                (supersedes_id, self.scope))
            elif supersedes_id is not None:
                raise ValueError("No predecessor to supersede")
            self.db.execute(
                "UPDATE experiences SET status='approved', supersedes_id=? "
                "WHERE id=? AND scope=? AND status='unverified'",
                (supersedes_id, experience_id, self.scope))
            return self.get(experience_id)

    def retrieved_lessons(self, query):
        """Only approved exact-key lessons; no semantic/fuzzy retrieval."""
        if not isinstance(query, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", query):
            return []
        rows = self.db.execute(
            "SELECT id,lesson,evidence FROM experiences "
            "WHERE scope=? AND topic_key=? AND status='approved' ORDER BY id DESC LIMIT 3",
            (self.scope, query)).fetchall()
        import json
        return [dict(id=row["id"], lesson=row["lesson"],
                     evidence=json.loads(row["evidence"]), status="approved") for row in rows]
