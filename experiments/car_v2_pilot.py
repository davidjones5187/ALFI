"""Opt-in CAR v2 research adapter. Never imported by the default ALFI runtime.

The caller must authenticate confirmations and verify evidence. This module does
not perform either operation; confirmation is deliberately unavailable here.
"""
import json
import os
import sqlite3
from pathlib import Path


class CARPilot:
    def __init__(self, database_path, scope="alfi-car-pilot"):
        path = Path(database_path)
        if path.name in {"ai_memory.json", "structured_memory.json", "conversation_history.json"}:
            raise ValueError("Pilot must use a separate SQLite database")
        if path.suffix not in {".sqlite", ".sqlite3", ".db"}:
            raise ValueError("Pilot database must be a SQLite file")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.scope = scope
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.execute("""CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY, scope TEXT NOT NULL, context TEXT NOT NULL,
            goal TEXT NOT NULL, action TEXT NOT NULL, result TEXT NOT NULL,
            evidence TEXT NOT NULL, correction TEXT, lesson TEXT,
            status TEXT NOT NULL DEFAULT 'unverified')""")
        self.db.commit()

    def close(self):
        self.db.close()

    def propose(self, *, context, goal, action, result, evidence, correction=None, lesson=None):
        values = (context, goal, action, result)
        if not all(isinstance(v, str) and v.strip() for v in values):
            raise ValueError("CAR context, goal, action and result required")
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(v, str) and v.strip() for v in evidence
        ):
            raise ValueError("Evidence references required")
        if lesson is not None and (not isinstance(lesson, str) or not lesson.strip()):
            raise ValueError("Invalid lesson")
        if correction is not None and (not isinstance(correction, str) or not correction.strip()):
            raise ValueError("Invalid correction")
        if any(len(v) > 2000 for v in values) or len(json.dumps(evidence)) > 4000:
            raise ValueError("Pilot record exceeds limit")
        with self.db:
            cursor = self.db.execute(
                "INSERT INTO experiences (scope,context,goal,action,result,evidence,correction,lesson,status) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (self.scope, *values, json.dumps(evidence), correction, lesson,
                 "unverified" if lesson else "not_applicable"))
            return cursor.lastrowid

    def get(self, experience_id):
        row = self.db.execute(
            "SELECT * FROM experiences WHERE id=? AND scope=?", (experience_id, self.scope)
        ).fetchone()
        if row is None:
            raise ValueError("Experience not found")
        result = dict(row)
        result["evidence"] = json.loads(result["evidence"])
        return result

    def candidates(self):
        """Research-only pending proposals. Never injected into model prompts."""
        return [self.get(row["id"]) for row in self.db.execute(
            "SELECT id FROM experiences WHERE scope=? AND status='unverified' ORDER BY id",
            (self.scope,))]

    def retrieved_lessons(self, query):
        """Fail-closed: pilot has no authenticated confirmation bridge."""
        return []

    def confirm(self, *args, **kwargs):
        raise PermissionError("CAR pilot cannot authenticate confirmations; no promotion allowed")
