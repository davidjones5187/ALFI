"""A.L.F.I. 1.5 structured memory: explicit lessons and bounded retrieval."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

KINDS = {"fact", "preference", "instruction"}
WORDS = set("a an the is are what who how why of to about tell me my you your and it".split())

def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower())) - WORDS

class MemoryStore:
    def __init__(self, path):
        self.path = Path(path)
        self.items = self._load()

    def _load(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("Expected a list")
            for item in data:
                if not isinstance(item, dict) or not all(isinstance(item.get(k), str) for k in ("key", "kind", "value", "source", "updated")) or item["kind"] not in KINDS:
                    raise ValueError("Invalid record")
            return data
        except (OSError, ValueError) as exc:
            raise ValueError(f"Cannot read structured memory: {exc}") from exc

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_name(self.path.name + ".tmp")
        temp.write_text(json.dumps(self.items, indent=2), encoding="utf-8")
        temp.replace(self.path)

    def put(self, kind, key, value, source="explicit /remember"):
        if kind not in KINDS:
            raise ValueError("Kind must be fact, preference, or instruction")
        key, value = key.strip().lower(), value.strip()
        if not key or not value:
            raise ValueError("Key and value required")
        if len(key) > 120 or len(value) > 2000:
            raise ValueError("Memory entry too long")
        record = {"kind": kind, "key": key, "value": value, "source": source,
                  "updated": datetime.now(timezone.utc).isoformat()}
        previous = list(self.items)
        self.items = [i for i in self.items if i["key"] != key] + [record]
        try:
            self._save()
        except OSError:
            self.items = previous
            raise
        return record

    def forget(self, key):
        key = key.strip().lower()
        previous = list(self.items)
        self.items = [i for i in self.items if i["key"] != key]
        if len(self.items) == len(previous):
            return False
        try:
            self._save()
        except OSError:
            self.items = previous
            raise
        return True

    def search(self, query, limit=3):
        q = tokens(query)
        if not q:
            return []
        ranked = []
        for item in self.items:
            terms = tokens(item["key"] + " " + item["value"])
            score = len(q & terms) / max(1, len(q | terms))
            if score:
                ranked.append((score, item))
        ranked.sort(key=lambda pair: (-pair[0], pair[1]["key"]))
        return [item for _, item in ranked[:max(0, min(limit, 5))]]

    def list_items(self):
        return sorted(self.items, key=lambda item: item["key"])
