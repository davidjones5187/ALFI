"""A.L.F.I. L-1: local, read-only-to-sources knowledge library.

Documents are registered only by an explicit caller action. Source files are
never modified. The SQLite index stores passages and provenance.
"""
from __future__ import annotations

import hashlib
import sqlite3
from contextlib import closing
from pathlib import Path

MAX_BYTES = 32768
MAX_CHARS = 8000
CHUNK_CHARS = 900


class Library:
    def __init__(self, database: str | Path):
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, path TEXT NOT NULL UNIQUE, sha256 TEXT NOT NULL)")
            db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS passages USING fts5(document_id UNINDEXED, passage, tokenize='unicode61')")

    def _connect(self):
        return sqlite3.connect(self.database)

    def register(self, filename: str | Path, *, authorized: bool = False) -> int:
        if not authorized:
            raise PermissionError("Explicit document authorization is required")
        path = Path(filename).expanduser().resolve(strict=True)
        if path.suffix.lower() != '.txt' or not path.is_file():
            raise ValueError("Only regular .txt files are supported")
        if path.stat().st_size > MAX_BYTES:
            raise ValueError("File exceeds the input-size limit")
        raw = path.read_bytes()
        text = raw.decode('utf-8')
        if not text.strip() or len(text) > MAX_CHARS:
            raise ValueError("File is empty or exceeds 8,000 characters")
        chunks = [text[i:i + CHUNK_CHARS] for i in range(0, len(text), CHUNK_CHARS)]
        digest = hashlib.sha256(raw).hexdigest()
        with closing(self._connect()) as db, db:
            row = db.execute('SELECT id FROM documents WHERE path = ?', (str(path),)).fetchone()
            if row:
                document_id = row[0]
                db.execute('DELETE FROM passages WHERE document_id = ?', (document_id,))
                db.execute('UPDATE documents SET sha256 = ? WHERE id = ?', (digest, document_id))
            else:
                document_id = db.execute('INSERT INTO documents(path, sha256) VALUES (?, ?)', (str(path), digest)).lastrowid
            db.executemany('INSERT INTO passages(document_id, passage) VALUES (?, ?)', ((document_id, c) for c in chunks))
        return document_id

    def documents(self):
        with closing(self._connect()) as db, db:
            return [{'id': row[0], 'path': row[1], 'sha256': row[2]} for row in db.execute('SELECT id, path, sha256 FROM documents ORDER BY id')]

    def search(self, question: str, limit: int = 3):
        # Tokenized, parameterized FTS query; no raw user FTS operators.
        import re
        terms = re.findall(r'\w+', question, flags=re.UNICODE)
        if not terms:
            return []
        query = ' OR '.join('"' + t.replace('"', '') + '"' for t in terms[:16])
        with closing(self._connect()) as db, db:
            rows = db.execute('''SELECT d.path, p.passage, bm25(passages) AS rank
                FROM passages AS p JOIN documents AS d ON d.id = p.document_id
                WHERE passages MATCH ? ORDER BY rank LIMIT ?''', (query, max(1, min(int(limit), 10)))).fetchall()
        return [{'source': r[0], 'passage': r[1], 'rank': r[2]} for r in rows]
